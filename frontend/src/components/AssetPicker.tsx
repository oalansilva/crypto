import { useEffect, useId, useMemo, useRef, useState, type KeyboardEvent, type ReactNode } from 'react'
import {
  fetchCatalogPage,
  refreshCatalog,
  resolveCatalogFilter,
  type CatalogPage,
  type ResolvedFilter,
} from '../lib/assetCatalogApi'
import {
  CLASS_FILTER_LABEL,
  CLASS_LABEL,
  PAGE_SIZE,
  catalogBanners,
  classLabelOf,
  confirmCopy,
  coverageNote,
  coverageRows,
  emptySearchMessage,
  entryStateLabel,
  fmtInt,
  freshnessLine,
  hasCoverageDetail,
  historySummary,
  isMarked,
  markedNoteText,
  markedReasonText,
  mergeSymbols,
  normalizeSymbol,
  onDemandHistory,
  selectionCountText,
  selectionCounts,
  sortedForChips,
  zoneLabel,
  type CatalogAsset,
  type ClassFilter,
} from '../lib/assetSelection'
import { rememberAssets, useSelectionView } from '../lib/assetStore'
import './AssetPicker.css'

const FILTERS: ClassFilter[] = ['all', 'crypto', 'stock', 'etf']
const MAX_CHIPS = 8

export interface AssetPickerProps {
  /** Seleção concreta (símbolos): `BTC/USDT`, `NVDA`, `SPY`. */
  value: string[]
  onChange: (next: string[]) => void
  ariaLabel: string
  /** Título visível (Descoberta). Nas telas com rótulo próprio, fica fora do seletor. */
  title?: string
  disabled?: boolean
  /** Combo: `Limpar (1 ativo)` volta para BTC/USDT. Padrão: seleção vazia. */
  clearTo?: string[]
  clearLabel?: string
  extraActions?: ReactNode
  classNote: string
  variant?: 'default' | 'narrow'
  /** Aviso fixo acima da pesquisa (ex.: `?symbol=` fora do catálogo). */
  notice?: { title: string; body: string } | null
}

interface ConfirmState {
  eligible: number
  marked: number
  filter: ClassFilter
  q: string
  newCount: number | null
}

export function AssetPicker({
  value,
  onChange,
  ariaLabel,
  title,
  disabled = false,
  clearTo = [],
  clearLabel = 'Limpar seleção',
  extraActions,
  classNote,
  variant = 'default',
  notice = null,
}: AssetPickerProps) {
  const headingId = useId()
  const confirmTextId = useId()
  const [q, setQ] = useState('')
  const [filter, setFilter] = useState<ClassFilter>('all')
  const [page, setPage] = useState(1)
  const [data, setData] = useState<CatalogPage | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [tick, setTick] = useState(0)
  const [confirm, setConfirm] = useState<ConfirmState | null>(null)
  const [retryBusy, setRetryBusy] = useState(false)
  const [retryError, setRetryError] = useState<string | null>(null)

  // Cobertura aberta por ativo (nunca marca nem desmarca o ativo) e botões, para devolver o foco no Esc.
  const [openCoverage, setOpenCoverage] = useState<Record<string, boolean>>({})
  const [announce, setAnnounce] = useState('')
  const coverageButtons = useRef<Record<string, HTMLButtonElement | null>>({})
  const lastAnnounced = useRef('')
  const silentRefresh = useRef(false)
  const searchRef = useRef<HTMLInputElement | null>(null)
  const allRef = useRef<HTMLButtonElement | null>(null)
  const okRef = useRef<HTMLButtonElement | null>(null)
  const resolvedRef = useRef<Promise<ResolvedFilter> | null>(null)
  const firstLoad = useRef(true)
  // Valor mais recente: o `Incluir` espera o resolve e não pode usar o `value` do clique.
  const valueRef = useRef(value)
  useEffect(() => {
    valueRef.current = value
  }, [value])

  const { entries, freshness: storeFreshness } = useSelectionView(value)
  const counts = useMemo(() => selectionCounts(entries), [entries])
  const selected = useMemo(() => new Set(value.map(normalizeSymbol)), [value])
  const freshness = data?.freshness ?? storeFreshness

  // --- Página do catálogo (pesquisa com debounce, sem perder a lista anterior) --------
  useEffect(() => {
    const controller = new AbortController()
    const delay = firstLoad.current ? 0 : 250
    const timer = window.setTimeout(async () => {
      // Atualização de fundo (coleta em andamento) não pisca a lista nem desliga o "Todos do filtro".
      const silent = silentRefresh.current
      silentRefresh.current = false
      if (!silent) setLoading(true)
      try {
        const next = await fetchCatalogPage({ q: q.trim(), filter, page, pageSize: PAGE_SIZE }, controller.signal)
        if (controller.signal.aborted) return
        firstLoad.current = false
        rememberAssets(next.items, { fresh: next.freshness })
        setData(next)
        setError(null)
        if (next.page > next.pages) setPage(next.pages)
      } catch (e) {
        if (controller.signal.aborted) return
        setError(e instanceof Error ? e.message : 'Não foi possível carregar o catálogo de ativos.')
      } finally {
        if (!controller.signal.aborted && !silent) setLoading(false)
      }
    }, delay)
    return () => {
      window.clearTimeout(timer)
      controller.abort()
    }
  }, [q, filter, page, tick])

  // Atualização da Binance em andamento: pergunta de novo em instantes.
  const refreshing = freshness
    ? [freshness.crypto, freshness.stock].some((info) => info.refreshing && info.status === 'unavailable')
    : false
  useEffect(() => {
    if (!refreshing) return
    const timer = window.setTimeout(() => setTick((n) => n + 1), 4000)
    return () => window.clearTimeout(timer)
  }, [refreshing, tick])

  // Coleta de histórico em andamento numa linha visível: acompanha o progresso sem recarregar a lista.
  const collectingVisible = data?.items.some((asset) => asset.history.status === 'collecting') ?? false
  useEffect(() => {
    if (!collectingVisible) return
    const timer = window.setTimeout(() => {
      silentRefresh.current = true
      setTick((n) => n + 1)
    }, 5000)
    return () => window.clearTimeout(timer)
  }, [collectingVisible, tick])

  // role=status anuncia só quando o progresso muda, não a cada filtro ou página (P3 aceito do Design).
  const collectingKey = (data?.items ?? [])
    .filter((asset) => asset.history.status === 'collecting')
    .map((asset) => `${asset.symbol}: ${historySummary(asset).text}`)
    .join('. ')
  useEffect(() => {
    if (collectingKey === lastAnnounced.current) return
    lastAnnounced.current = collectingKey
    setAnnounce(collectingKey)
  }, [collectingKey])

  const closeCoverage = (assetId: string) => {
    setOpenCoverage((current) => ({ ...current, [assetId]: false }))
    window.setTimeout(() => coverageButtons.current[assetId]?.focus(), 0)
  }

  const closeConfirm = (refocus: boolean) => {
    setConfirm(null)
    resolvedRef.current = null
    if (refocus) window.setTimeout(() => allRef.current?.focus(), 0)
  }

  useEffect(() => {
    if (confirm) okRef.current?.focus()
  }, [confirm])

  const resetView = (patch: { q?: string; filter?: ClassFilter }) => {
    if (patch.q !== undefined) setQ(patch.q)
    if (patch.filter !== undefined) setFilter(patch.filter)
    setPage(1)
    setConfirm(null)
    resolvedRef.current = null
  }

  const toggle = (asset: CatalogAsset) => {
    if (disabled || isMarked(asset)) return
    const symbol = normalizeSymbol(asset.symbol)
    onChange(selected.has(symbol) ? value.filter((s) => normalizeSymbol(s) !== symbol) : mergeSymbols(value, [symbol]))
  }

  const openConfirm = () => {
    if (!data || disabled || data.eligible_total === 0 || !settled) return
    const request = resolveCatalogFilter({ q: q.trim(), filter })
    resolvedRef.current = request
    setConfirm({
      eligible: data.eligible_total,
      marked: data.marked_total,
      filter,
      q: q.trim(),
      newCount: null,
    })
    void request
      .then((resolved) => {
        if (resolvedRef.current !== request) return
        setConfirm((current) =>
          current
            ? {
                ...current,
                newCount: resolved.items.filter((item) => !selected.has(normalizeSymbol(item.symbol))).length,
              }
            : current,
        )
      })
      .catch(() => undefined)
  }

  const applyConfirm = async () => {
    const request = resolvedRef.current
    if (!request) return
    try {
      const resolved = await request
      if (resolvedRef.current !== request) return
      rememberAssets(
        resolved.items.map((item) => ({
          asset_id: item.asset_id,
          asset_class: item.asset_class,
          symbol: item.symbol,
          name: item.name,
          state: 'tradable' as const,
          state_label: 'Negociável',
          state_reason: null,
          selectable: true,
          analysis_available: item.asset_class === 'crypto',
          history: onDemandHistory(),
        })),
        { overwrite: false },
      )
      onChange(mergeSymbols(valueRef.current, resolved.items.map((item) => item.symbol)))
      setConfirm(null)
      resolvedRef.current = null
      window.setTimeout(() => allRef.current?.focus(), 0)
    } catch {
      setConfirm(null)
      resolvedRef.current = null
      setError('Não foi possível listar os ativos do filtro. A seleção não mudou.')
    }
  }

  const onKeyDown = (event: KeyboardEvent<HTMLElement>) => {
    if (event.key !== 'Escape') return
    // Esc com o foco no botão "Cobertura" ou dentro da tabela fecha e devolve o foco ao botão.
    const target = event.target as HTMLElement
    const owner =
      target.closest?.<HTMLElement>('[data-cov-btn]')?.getAttribute('data-cov-btn') ??
      target.closest?.<HTMLElement>('.ap-cov')?.getAttribute('data-asset-id') ??
      null
    if (owner && openCoverage[owner]) {
      event.preventDefault()
      event.stopPropagation()
      closeCoverage(owner)
      return
    }
    if (confirm) {
      event.preventDefault()
      event.stopPropagation()
      closeConfirm(true)
    }
  }

  const retry = async (group: 'crypto' | 'equity') => {
    setRetryBusy(true)
    setRetryError(null)
    try {
      await refreshCatalog(group)
      setTick((n) => n + 1)
    } catch (e) {
      setRetryError(e instanceof Error ? e.message : 'Não foi possível atualizar agora.')
    } finally {
      setRetryBusy(false)
    }
  }

  // --- Derivados da tela ------------------------------------------------------------
  const banners = catalogBanners(freshness)
  // A página exibida já responde ao que está digitado e filtrado; senão o "Todos" mostraria contagem velha.
  const settled = data != null && !loading && data.q === q.trim() && data.class === filter
  const eligibleNow = data?.eligible_total ?? 0
  const total = data?.total ?? 0
  const start = data ? (data.page - 1) * data.page_size : 0
  const cryptoDownOnFilter = filter === 'crypto' && freshness?.crypto.status === 'unavailable'
  const chipEntries = sortedForChips(entries)
  const shownChips = chipEntries.slice(0, MAX_CHIPS)
  const extraChips = Math.max(0, chipEntries.length - MAX_CHIPS)
  const markedNote = markedNoteText(entries)
  const copy = confirm ? confirmCopy(confirm.filter, confirm.q, confirm.eligible, confirm.marked, confirm.newCount) : null

  return (
    <section
      className={`asset-picker${variant === 'narrow' ? ' narrow' : ''}`}
      aria-labelledby={title ? headingId : undefined}
      aria-label={title ? undefined : ariaLabel}
      data-testid="asset-picker"
      onKeyDown={onKeyDown}
    >
      <div className="ap-head">
        <div>
          {title ? <h3 id={headingId}>{title}</h3> : null}
          <p className="ap-count" data-testid="asset-count" aria-live="polite">
            {selectionCountText(counts)}
          </p>
          <p className="ap-fresh" data-testid="catalog-fresh">
            {freshnessLine(freshness)}
          </p>
        </div>
      </div>

      <div>
        {error ? (
          <div className="ap-alert" role="alert" data-testid="catalog-error">
            <strong>Catálogo indisponível</strong>
            <span>{error} A seleção atual foi mantida.</span>
            <span className="ap-alert-actions">
              <button type="button" className="ap-btn" onClick={() => setTick((n) => n + 1)}>
                Tentar de novo
              </button>
            </span>
          </div>
        ) : null}
        {banners.map((banner) =>
          banner.kind === 'stale' ? (
            <div key={banner.group} className="ap-warn" role="status" data-testid="catalog-stale">
              <strong>{banner.title}</strong>
              {banner.body}
            </div>
          ) : (
            <div key={banner.group} className="ap-alert" role="alert" data-testid="catalog-down">
              <strong>{banner.title}</strong>
              <span>{banner.body}</span>
              {retryError ? <span>{retryError}</span> : null}
              {banner.retry ? (
                <span className="ap-alert-actions">
                  <button
                    type="button"
                    className="ap-btn"
                    data-retry
                    disabled={retryBusy}
                    onClick={() => void retry(banner.group)}
                  >
                    {retryBusy ? 'Tentando…' : 'Tentar de novo'}
                  </button>
                </span>
              ) : null}
            </div>
          ),
        )}
        {notice ? (
          <div className="ap-warn" role="status" data-testid="asset-not-found">
            <strong>{notice.title}</strong>
            {notice.body}
          </div>
        ) : null}
      </div>

      <input
        ref={searchRef}
        className="ap-search"
        type="search"
        value={q}
        onChange={(e) => resetView({ q: e.target.value })}
        placeholder="Buscar por símbolo ou nome (ex.: BTC, NVDA, nvidia)"
        aria-label="Buscar ativos por símbolo ou nome"
        data-testid="asset-search"
        autoComplete="off"
        disabled={disabled}
      />

      <div className="ap-classes" role="group" aria-label="Filtrar por classe">
        {FILTERS.map((key) => {
          const info = data?.counts?.[key]
          const unavailable = key === 'crypto' && freshness?.crypto.status === 'unavailable'
          return (
            <button
              key={key}
              type="button"
              className={`ap-class${unavailable ? ' unavailable' : ''}`}
              aria-pressed={filter === key}
              data-cls={key}
              onClick={() => resetView({ filter: key })}
            >
              {CLASS_FILTER_LABEL[key]}{' '}
              <span className="n">{unavailable ? 'indisponível' : info?.total != null ? fmtInt(info.total) : '…'}</span>
            </button>
          )
        })}
      </div>

      <span className="sr-only" role="status" aria-live="polite" data-testid="coverage-live">
        {announce}
      </span>

      <div className="ap-list" role="group" aria-label="Resultado da busca de ativos" data-testid="asset-results">
        {!data && loading ? (
          <p className="ap-empty">Carregando catálogo…</p>
        ) : cryptoDownOnFilter ? (
          <p className="ap-empty" data-testid="asset-crypto-down">
            {emptySearchMessage(q, filter, freshness)}
          </p>
        ) : data && data.items.length === 0 ? (
          <p className="ap-empty" data-testid="asset-empty">
            {q.trim()
              ? emptySearchMessage(q, filter, freshness)
              : 'Nenhum ativo disponível agora. Use “Tentar de novo” no aviso acima; a seleção atual foi mantida.'}
          </p>
        ) : (
          data?.items.map((asset) => {
            const marked = isMarked(asset)
            const inSel = selected.has(normalizeSymbol(asset.symbol))
            const cls = CLASS_LABEL[asset.asset_class]
            const summary = historySummary(asset)
            const slug = `${headingId}-${asset.asset_id}`.replace(/[^A-Za-z0-9_-]/g, '-')
            const pickId = `pick${slug}`
            const panelId = `cov${slug}`
            const detail = hasCoverageDetail(asset.history)
            const isOpen = !!openCoverage[asset.asset_id] && detail
            const histClass =
              summary.tone === 'gap' ? ' cov-gap' : summary.tone === 'busy' ? ' cov-busy' : summary.tone === 'fail' ? ' cov-fail' : ''
            const facts = (
              <span className="ap-facts">
                <span className={`ap-fact cls-${asset.asset_class}`}>{cls}</span>
                <span className={`ap-fact ${marked ? 'st-marked' : 'st-ok'}`}>
                  {marked ? asset.state_label : 'Negociável'}
                </span>
                <span className={`ap-fact hist${histClass}`} data-testid="asset-history">
                  {summary.text}
                </span>
                {detail ? (
                  <button
                    type="button"
                    className="ap-cov-btn"
                    ref={(node) => {
                      coverageButtons.current[asset.asset_id] = node
                    }}
                    data-cov-btn={asset.asset_id}
                    aria-expanded={isOpen}
                    aria-controls={panelId}
                    onClick={() => setOpenCoverage((current) => ({ ...current, [asset.asset_id]: !current[asset.asset_id] }))}
                  >
                    Cobertura<span className="sr-only"> de {asset.symbol}</span>
                  </button>
                ) : null}
              </span>
            )
            const nameBlock = (
              <>
                <strong>{asset.symbol}</strong>
                {/* A Binance não publica o nome do cripto no exchangeInfo: a linha diz o mercado. */}
                <span>{asset.asset_class === 'crypto' ? `${asset.name} · Spot, cotação USDT` : asset.name}</span>
              </>
            )
            const panel = isOpen ? (
              <div
                className="ap-cov"
                id={panelId}
                role="region"
                aria-label={`Cobertura do histórico de ${asset.symbol}`}
                tabIndex={-1}
                data-asset-id={asset.asset_id}
                data-testid={`asset-coverage-${asset.symbol}`}
              >
                <p className="ap-cov-note">{coverageNote(asset.history)}</p>
                <ul>
                  {coverageRows(asset.history).map((row) => (
                    <li key={row.timeframe} className="ap-cov-tf" data-timeframe={row.timeframe}>
                      <span className="tf">
                        <b>{row.timeframe}</b>
                        {row.derived ? (
                          <>
                            {' '}
                            <span className="ap-cov-derived">derivado</span>
                          </>
                        ) : null}
                      </span>
                      <span className="cell">
                        <span className="lbl">Período coberto</span>
                        {row.period}
                      </span>
                      <span className={`cell${row.gapsTone === 'ok' ? '' : ` ${row.gapsTone}`}`}>
                        <span className="lbl">Lacunas</span>
                        {row.gaps}
                      </span>
                      <span className="cell">
                        <span className="lbl">Atualizado ({zoneLabel()})</span>
                        {row.updated}
                      </span>
                      <span className="cell">
                        <span className="lbl">Origem</span>
                        {row.origin}
                      </span>
                    </li>
                  ))}
                </ul>
              </div>
            ) : null
            if (marked) {
              const reason = markedReasonText(asset, false)
              return (
                <div key={asset.asset_id} className="ap-item">
                  <div className="ap-row marked" data-asset={asset.symbol}>
                    <input
                      type="checkbox"
                      disabled
                      aria-label={`${asset.symbol} — ${cls}, ${asset.state_label}: não pode ser escolhido`}
                    />
                    <span className="ap-id">{nameBlock}</span>
                    {facts}
                    <p className="ap-reason" data-testid="asset-marked-reason">
                      {reason}
                      {inSel ? <b> Está na seleção salva e fica de fora ao rodar.</b> : null}
                    </p>
                  </div>
                  {panel}
                </div>
              )
            }
            return (
              <div key={asset.asset_id} className="ap-item">
                {/* Linha selecionável: <div> com <label for> no nome. O botão "Cobertura" fica fora do <label>
                    (HTML válido) e a linha inteira continua clicável como no seletor do #1117. */}
                <div
                  className="ap-row"
                  data-asset={asset.symbol}
                  onClick={(event) => {
                    if ((event.target as HTMLElement).closest('button, input, label, a')) return
                    toggle(asset)
                  }}
                >
                  <input
                    id={pickId}
                    type="checkbox"
                    checked={inSel}
                    disabled={disabled}
                    onChange={() => toggle(asset)}
                    aria-label={`${asset.symbol} — ${cls}`}
                  />
                  <label className="ap-id" htmlFor={pickId}>
                    {nameBlock}
                  </label>
                  {facts}
                </div>
                {panel}
              </div>
            )
          })
        )}
      </div>

      {data && data.items.length > 0 && !cryptoDownOnFilter ? (
        <div className="ap-pager">
          <span aria-live="polite" data-testid="asset-range">
            {fmtInt(start + 1)}–{fmtInt(Math.min(start + data.page_size, total))} de {fmtInt(total)}
          </span>
          <div>
            <button type="button" className="ap-btn" disabled={page <= 1} onClick={() => setPage((p) => Math.max(1, p - 1))}>
              Anterior
            </button>
            <button
              type="button"
              className="ap-btn"
              disabled={page >= data.pages}
              onClick={() => setPage((p) => p + 1)}
            >
              Próxima
            </button>
          </div>
        </div>
      ) : null}

      <div className="ap-actions">
        <button
          ref={allRef}
          type="button"
          className="ap-btn"
          data-testid="asset-select-all"
          disabled={disabled || eligibleNow === 0 || !settled}
          onClick={openConfirm}
        >
          Todos do filtro ({fmtInt(eligibleNow)})
        </button>
        {extraActions}
        <button
          type="button"
          className="ap-btn"
          data-testid="asset-clear"
          disabled={disabled}
          onClick={() => {
            closeConfirm(false)
            onChange([...clearTo])
          }}
        >
          {clearLabel}
        </button>
      </div>

      {confirm && copy ? (
        <div className="ap-confirm" role="alertdialog" aria-labelledby={confirmTextId} data-testid="asset-confirm">
          <p id={confirmTextId}>
            {copy.prefix}
            <b>{copy.count}</b>
            {copy.middle}
            {copy.marked ? (
              <>
                {' '}
                <b>{copy.marked}</b>
                {copy.markedText}
              </>
            ) : null}
            {copy.suffix}
          </p>
          <div className="ap-actions" style={{ marginTop: 0 }}>
            <button ref={okRef} type="button" className="ap-btn primary" data-testid="asset-confirm-ok" onClick={() => void applyConfirm()}>
              Incluir
            </button>
            <button type="button" className="ap-btn" data-testid="asset-confirm-cancel" onClick={() => closeConfirm(true)}>
              Cancelar
            </button>
          </div>
        </div>
      ) : null}

      <div className="ap-selected">
        <h4>Selecionados</h4>
        <div className="ap-chips" data-testid="asset-chips">
          {shownChips.map((entry) => {
            const marked = entry.kind === 'marked' || entry.kind === 'missing'
            const stateLabel = entryStateLabel(entry)
            return (
              <span key={entry.symbol} className={`ap-chip${marked ? ' marked' : ''}`} data-asset={entry.symbol}>
                <span>
                  <b>{entry.symbol}</b> · {classLabelOf(entry)}
                  {marked ? (
                    <>
                      {' '}
                      · {stateLabel} · <span className="out">fica de fora</span>
                    </>
                  ) : null}
                </span>
                <button
                  type="button"
                  aria-label={`Remover ${entry.symbol} da seleção`}
                  disabled={disabled}
                  onClick={() => {
                    onChange(value.filter((s) => normalizeSymbol(s) !== entry.symbol))
                    searchRef.current?.focus()
                  }}
                >
                  ×
                </button>
              </span>
            )
          })}
          {extraChips > 0 ? <span className="ap-chip more">+{fmtInt(extraChips)} ativos</span> : null}
          {chipEntries.length === 0 ? <span className="ap-none">Nenhum ativo selecionado.</span> : null}
        </div>
        {counts.equities > 0 ? (
          <p className="ap-note" data-testid="asset-class-note">
            {classNote}
          </p>
        ) : null}
        {markedNote ? (
          <p className="ap-warn small" data-testid="asset-marked-note" role="status">
            <strong>{markedNote.title}</strong>
            {markedNote.body}
          </p>
        ) : null}
      </div>
    </section>
  )
}
