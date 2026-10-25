/**
 * Lógica pura do seletor de ativos (card #1117): tipos do catálogo, contagem da
 * seleção, o que roda e o que fica fora, e os textos que o protótipo aprovado
 * mostra antes e depois do clique. Sem DOM e sem rede, para ser testada com
 * `tsx --test`.
 */

export type AssetClass = 'crypto' | 'stock' | 'etf'
export type AssetState =
  | 'tradable'
  | 'suspended'
  | 'off_market'
  | 'no_trading'
  | 'no_rules'
  | 'removed'
export type ClassFilter = 'all' | AssetClass

/** Lacuna de uma série: primeiro e último candle esperado que não veio (UTC). */
export interface HistoryGap {
  start: string
  end: string
  count: number
  /** 15m montado do 5m: a falta é a mesma do 5m e não soma no resumo da linha. */
  inherited_from?: '5m' | null
  /** Fim do bloco de 15m (só nas lacunas herdadas). */
  block_end?: string
}

export interface HistoryTimeframe {
  timeframe: string
  from: string | null
  to: string | null
  candles?: number
  /** `null`: lacunas ainda desconhecidas (série fora da autoridade nova). */
  gap_count: number | null
  gaps: HistoryGap[]
  updated_at: string | null
  origin: 'native' | 'derived'
  derived_from?: string | null
  state?: 'idle' | 'collecting' | 'failed'
  insufficient?: boolean
  incomplete?: boolean
  pages_done?: number
  requested_since?: string | null
  starts_at?: string | null
  error?: string | null
  error_at?: string | null
}

export type HistoryStatus = 'on_demand' | 'collecting' | 'covered' | 'partial' | 'failed' | 'frozen' | 'none'

/** Cobertura do histórico de um ativo (card #1118): vem de `market_series_coverage`. */
export interface AssetHistory {
  status: HistoryStatus
  from: string | null
  to: string | null
  updated_at?: string | null
  gap_count?: number | null
  timeframes?: HistoryTimeframe[]
  note?: string | null
  calendar_timezone?: string | null
  collecting?: { timeframe: string; page: number; requested_at: string | null } | null
  error?: { timeframe: string; code: string | null; message: string | null; at: string | null } | null
  partial?: {
    timeframe: string
    requested_since: string | null
    starts_at: string | null
    insufficient: boolean
  } | null
}

export interface CatalogAsset {
  asset_id: string
  asset_class: AssetClass
  symbol: string
  name: string
  state: AssetState
  state_label: string
  state_reason: string | null
  info_note?: string | null
  removed_at?: string | null
  selectable: boolean
  analysis_available: boolean
  history: AssetHistory
}

export interface ClassFreshness {
  status: 'ok' | 'stale' | 'unavailable'
  updated_at: string | null
  last_attempt_at: string | null
  reason: string | null
  code: string | null
  refreshing: boolean
}

export type FreshnessMap = Record<AssetClass, ClassFreshness>

export interface ClassCount {
  total: number | null
  eligible: number | null
}

export type CountsMap = Record<'all' | AssetClass, ClassCount>

export const CLASS_LABEL: Record<AssetClass, string> = {
  crypto: 'Cripto',
  stock: 'Ação',
  etf: 'ETF',
}

export const CLASS_FILTER_LABEL: Record<ClassFilter, string> = {
  all: 'Todas',
  crypto: 'Cripto',
  stock: 'Ações',
  etf: 'ETFs',
}

export const PAGE_SIZE = 6
/** Card #1120 (decisão 13): só a Descoberta segue recusando ação/ETF; o lote do Combo e da Otimização aceita. */
export const EQUITY_REASON =
  'ação e ETF por enquanto rodam no Combo e na Otimização (1 ativo ou lote); a Descoberta vem depois'
export const MISSING_REASON = 'ativo fora do catálogo da Binance'
export const TOP10_SYMBOLS = [
  'BTC/USDT',
  'ETH/USDT',
  'BNB/USDT',
  'SOL/USDT',
  'XRP/USDT',
  'ADA/USDT',
  'DOGE/USDT',
  'AVAX/USDT',
  'MATIC/USDT',
  'LINK/USDT',
]

export function fmtInt(value: number): string {
  return value.toLocaleString('pt-BR')
}

export function isMarked(asset: Pick<CatalogAsset, 'state'>): boolean {
  return asset.state !== 'tradable'
}

export function symbolIsCrypto(symbol: string): boolean {
  return symbol.includes('/')
}

export function normalizeSymbol(symbol: string): string {
  return String(symbol || '').trim().toUpperCase()
}

/** Sem repetição e na ordem em que chegaram. */
export function mergeSymbols(current: string[], added: string[]): string[] {
  const seen = new Set(current.map(normalizeSymbol))
  const next = [...current]
  for (const raw of added) {
    const symbol = normalizeSymbol(raw)
    if (!symbol || seen.has(symbol)) continue
    seen.add(symbol)
    next.push(symbol)
  }
  return next
}

// --- Datas ------------------------------------------------------------------------

const MONTHS = ['jan.', 'fev.', 'mar.', 'abr.', 'mai.', 'jun.', 'jul.', 'ago.', 'set.', 'out.', 'nov.', 'dez.']

function dateParts(iso: string, timeZone: string) {
  const date = new Date(iso)
  if (Number.isNaN(date.getTime())) return null
  const parts = new Intl.DateTimeFormat('en-GB', {
    timeZone,
    day: '2-digit',
    month: 'numeric',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    hour12: false,
  }).formatToParts(date)
  const get = (type: string) => parts.find((p) => p.type === type)?.value ?? ''
  return {
    day: get('day'),
    month: Number(get('month')),
    year: get('year'),
    hour: get('hour') === '24' ? '00' : get('hour'),
    minute: get('minute'),
  }
}

/** `20 out. 2026` (dia do catálogo, no fuso informado). */
export function formatDate(iso: string | null | undefined, timeZone = 'America/Sao_Paulo'): string {
  if (!iso) return ''
  const p = dateParts(iso, timeZone)
  return p ? `${p.day} ${MONTHS[p.month - 1]} ${p.year}` : ''
}

/** `2 jan. 2015` (sem zero à esquerda no dia, como no protótipo do lote). */
export function formatDatePlain(iso: string | null | undefined, timeZone = 'America/Sao_Paulo'): string {
  return formatDate(iso, timeZone).replace(/^0/, '')
}

/** `20 out. 2026, 06:00`. */
export function formatDateTime(iso: string | null | undefined, timeZone = 'America/Sao_Paulo'): string {
  if (!iso) return ''
  const p = dateParts(iso, timeZone)
  return p ? `${p.day} ${MONTHS[p.month - 1]} ${p.year}, ${p.hour}:${p.minute}` : ''
}

// --- Fatos de cada linha ------------------------------------------------------------

/** Estado vazio de uma classe: o texto diz quando a coleta começa (sem botão nem outro gatilho). */
export const ON_DEMAND_TEXT: Record<AssetClass, string> = {
  crypto: 'Histórico sob demanda · coletado quando uma análise pedir',
  stock: 'Histórico sob demanda · a coleta começa quando as análises aceitarem ações',
  etf: 'Histórico sob demanda · a coleta começa quando as análises aceitarem ETFs',
}

/** Combo e Otimização (card #1120, decisão 6): a coleta acontece ao rodar o backtest ou o lote, em toda classe. */
export const ON_DEMAND_TEXT_BACKTEST: Partial<Record<AssetClass, string>> = {
  crypto: 'Histórico sob demanda · coletado ao rodar o backtest ou o lote',
  stock: 'Histórico sob demanda · coletado ao rodar o backtest ou o lote',
  etf: 'Histórico sob demanda · coletado ao rodar o backtest ou o lote',
}

export function onDemandHistory(): AssetHistory {
  return { status: 'on_demand', from: null, to: null, timeframes: [], gap_count: 0 }
}

const TIMEFRAME_MINUTES: Record<string, number> = { '1m': 1, '5m': 5, '15m': 15, '1h': 60, '4h': 240, '1d': 1440 }
const timeframeOrder = (tf: string) => TIMEFRAME_MINUTES[tf] ?? 9999

/** `22 out., 18:07` no fuso do navegador (ano só quando não é o corrente). */
export function formatShortDateTime(
  iso: string | null | undefined,
  timeZone = browserTimeZone(),
  now: Date = new Date(),
): string {
  if (!iso) return ''
  const p = dateParts(iso, timeZone)
  if (!p) return ''
  const sameYear = String(now.getFullYear()) === p.year
  return `${p.day} ${MONTHS[p.month - 1]}${sameYear ? '' : ` ${p.year}`}, ${p.hour}:${p.minute}`
}

export function browserTimeZone(): string {
  try {
    return Intl.DateTimeFormat().resolvedOptions().timeZone || 'UTC'
  } catch {
    return 'UTC'
  }
}

/** Nome do fuso no rótulo da coluna de atualização ("Brasília" para o horário de São Paulo). */
export function zoneLabel(timeZone = browserTimeZone()): string {
  if (timeZone === 'America/Sao_Paulo') return 'Brasília'
  if (timeZone === 'UTC' || timeZone === 'Etc/UTC') return 'UTC'
  return timeZone.split('/').pop()?.replace(/_/g, ' ') ?? timeZone
}

const listAnd = (names: string[]) =>
  names.length > 1 ? `${names.slice(0, -1).join(', ')} e ${names[names.length - 1]}` : (names[0] ?? '')

function withData(history: AssetHistory): HistoryTimeframe[] {
  return (history.timeframes ?? []).filter((t) => t.from)
}

/** Fuso em que o dia de início de cada série vale: Nova York para ação/ETF, UTC para cripto. */
function sessionZone(history: AssetHistory): string {
  return history.calendar_timezone || 'UTC'
}

/**
 * "desde" diz de qual timeframe é: início comum ("Histórico desde 17 ago. 2017 · 4 timeframes") ou um
 * início por grupo ("1d desde 11 nov. 2014 · 5m e 15m desde 19 mai. 2026"). Nunca um "desde" único
 * quando o intraday começa depois do diário.
 */
export function sinceText(history: AssetHistory): string {
  const frames = withData(history)
  const zone = sessionZone(history)
  const groups: { start: string; names: string[] }[] = []
  for (const frame of frames) {
    const start = formatDate(frame.from, zone)
    const group = groups.find((g) => g.start === start)
    if (group) group.names.push(frame.timeframe)
    else groups.push({ start, names: [frame.timeframe] })
  }
  groups.sort((x, y) => {
    const fx = frames.find((f) => formatDate(f.from, zone) === x.start)?.from ?? ''
    const fy = frames.find((f) => formatDate(f.from, zone) === y.start)?.from ?? ''
    return fx.localeCompare(fy)
  })
  if (groups.length === 1) {
    const n = frames.length
    return `Histórico desde ${groups[0].start} · ${n} ${n === 1 ? 'timeframe' : 'timeframes'}`
  }
  return groups
    .map((g) => `${listAnd([...g.names].sort((a, b) => timeframeOrder(a) - timeframeOrder(b)))} desde ${g.start}`)
    .join(' · ')
}

export function gapsCountText(count: number): string {
  return count === 0 ? 'sem lacunas' : count === 1 ? '1 lacuna' : `${count} lacunas`
}

export type HistoryTone = 'plain' | 'gap' | 'busy' | 'fail'

export interface HistorySummary {
  text: string
  tone: HistoryTone
}

/** Fato de histórico da linha do seletor (tarefa 6.2). "Histórico não coletado" não existe mais. */
export function historySummary(
  asset: CatalogAsset,
  now: Date = new Date(),
  onDemandTexts?: Partial<Record<AssetClass, string>>,
): HistorySummary {
  const history = asset.history
  const frames = withData(history)
  const zone = sessionZone(history)
  switch (history.status) {
    case 'collecting': {
      const info = history.collecting
      const at = info?.requested_at ? formatShortDateTime(info.requested_at, undefined, now).split(', ')[1] : ''
      return {
        text: `Coletando histórico · ${info?.timeframe ?? '—'}, página ${info?.page ?? 1}${at ? ` · pedido às ${at}` : ''}`,
        tone: 'busy',
      }
    }
    case 'failed': {
      const err = history.error
      const when = err?.at ? formatShortDateTime(err.at, undefined, now) : ''
      const collected = frames.length
        ? ` · já coletado: ${frames
            .filter((t) => t.origin === 'native')
            .map((t) => `${t.timeframe} desde ${formatDate(t.from, zone)}`)
            .join(', ')}`
        : ' · nada coletado ainda'
      return {
        text: `Coleta falhou${when ? ` ${when}` : ''} · ${err?.message ?? 'falha na coleta'}${collected}`,
        tone: 'fail',
      }
    }
    case 'partial': {
      const info = history.partial
      const updated = history.updated_at ? ` · atualizado ${formatShortDateTime(history.updated_at, undefined, now)}` : ''
      if (info?.insufficient) {
        return {
          text: `Parcial: pedido desde ${formatDate(info.requested_since, zone)}; a Binance tem desde ${formatDate(info.starts_at, zone)}${updated}`,
          tone: 'gap',
        }
      }
      return {
        text: `Parcial: coletado desde ${formatDate(info?.starts_at ?? history.from, zone)}; a coleta continua no próximo pedido${updated}`,
        tone: 'gap',
      }
    }
    case 'frozen': {
      const why = asset.state_label ? ` · sem atualização: ativo ${asset.state_label.toLowerCase()}` : ''
      return {
        text: `Histórico ${formatDate(history.from, zone)} – ${formatDate(history.to, zone)}${why}`,
        tone: 'plain',
      }
    }
    case 'covered': {
      const gaps = history.gap_count
      const parts = [sinceText(history)]
      if (gaps !== null && gaps !== undefined) parts.push(gapsCountText(gaps))
      if (history.updated_at) parts.push(`atualizado ${formatShortDateTime(history.updated_at, undefined, now)}`)
      return { text: parts.join(' · '), tone: gaps ? 'gap' : 'plain' }
    }
    case 'none':
      return { text: 'Sem histórico local', tone: 'plain' }
    default:
      return { text: onDemandTexts?.[asset.asset_class] ?? ON_DEMAND_TEXT[asset.asset_class], tone: 'plain' }
  }
}

export function historyText(asset: CatalogAsset, now: Date = new Date()): string {
  return historySummary(asset, now).text
}

// --- Detalhe da cobertura por timeframe -----------------------------------------------

export interface CoverageRow {
  timeframe: string
  derived: boolean
  period: string
  gaps: string
  gapsTone: 'ok' | 'warn' | 'busy'
  updated: string
  origin: string
}

const NY_LABEL = 'horário de Nova York'

function hm(iso: string, timeZone: string): string {
  const p = dateParts(iso, timeZone)
  return p ? `${p.hour}:${p.minute}` : ''
}

/** Uma lacuna com data, hora e fuso na própria célula (design, decisão 16). */
export function gapLabel(gap: HistoryGap, timeframe: string, history: AssetHistory): string {
  const equity = !!history.calendar_timezone
  const zone = equity ? history.calendar_timezone! : browserTimeZone()
  const zoneText = equity ? NY_LABEL : 'horário local'
  const day = formatDate(gap.start, zone)
  if (timeframe === '1d') {
    const last = formatDate(gap.end, zone)
    return last === day ? `${day} (1 pregão sem candle)` : `${day} a ${last} (${gap.count} pregões sem candle)`
  }
  const from = hm(gap.start, zone)
  const to = hm(gap.inherited_from && gap.block_end ? gap.block_end : gap.end, zone)
  const range = from === to ? from : `${from}–${to}`
  return `${day}, ${range}, ${zoneText}`
}

function gapsCell(frame: HistoryTimeframe, history: AssetHistory): { text: string; tone: CoverageRow['gapsTone'] } {
  if (frame.state === 'collecting') return { text: 'em coleta', tone: 'busy' }
  const zone = sessionZone(history)
  if (frame.state === 'failed' || frame.incomplete) {
    return {
      text: `incompleto: faltam os candles antes de ${formatDate(frame.from, zone)}; a coleta continua do ponto em que parou no próximo pedido`,
      tone: 'warn',
    }
  }
  if (frame.insufficient) {
    return {
      text: `insuficiente para o último pedido (desde ${formatDate(frame.requested_since, zone)}): a Binance não tem candles antes de ${formatDate(frame.starts_at ?? frame.from, zone)}`,
      tone: 'warn',
    }
  }
  if (frame.origin === 'derived') {
    if (!frame.gaps.length) return { text: 'sem lacunas', tone: 'ok' }
    const shown = frame.gaps.slice(0, 3).map((g) => gapLabel(g, frame.timeframe, history))
    return {
      text: `herdada do ${frame.derived_from ?? '5m'}: ${shown.join('; ')} (bloco incompleto; não soma no resumo)`,
      tone: 'warn',
    }
  }
  const count = frame.gap_count
  if (count === null || count === undefined) return { text: 'lacunas ainda não calculadas', tone: 'ok' }
  if (count === 0) return { text: 'sem lacunas', tone: 'ok' }
  const shown = frame.gaps.slice(-3).map((g) => `${gapLabel(g, frame.timeframe, history)} (${g.count} ${g.count === 1 ? 'candle' : 'candles'} que a Binance não tem)`)
  const more = count > shown.length ? `; e mais ${count - shown.length}` : ''
  return { text: `${gapsCountText(count)}: ${shown.join('; ')}${more}`, tone: 'warn' }
}

export function coverageRows(history: AssetHistory, now: Date = new Date()): CoverageRow[] {
  const zone = sessionZone(history)
  return (history.timeframes ?? []).map((frame) => {
    const cell = gapsCell(frame, history)
    const derived = frame.origin === 'derived'
    const period =
      frame.state === 'collecting'
        ? `até agora: ${formatDate(frame.from, zone)} – ${formatDate(frame.to, zone)}`
        : `${formatDate(frame.from, zone)} – ${formatDate(frame.to, zone)}`
    return {
      timeframe: frame.timeframe,
      derived,
      period,
      gaps: cell.text,
      gapsTone: cell.tone,
      updated: frame.updated_at ? formatShortDateTime(frame.updated_at, undefined, now) : '—',
      origin: derived ? `montado do ${frame.derived_from ?? '5m'}` : 'nativo',
    }
  })
}

/** Linha de fonte, sessão e ajuste do detalhe da cobertura. */
export function coverageNote(history: AssetHistory): string {
  return `${history.note ?? ''}. Mercado fechado não conta como lacuna.`.replace(/^\. /, '')
}

/** O detalhe só existe quando há o que mostrar por timeframe. */
export function hasCoverageDetail(history: AssetHistory): boolean {
  return (history.timeframes ?? []).length > 0
}

/** Complemento exibido sob a linha de um ativo marcado. */
export function markedReasonText(asset: CatalogAsset, inSelection: boolean): string {
  const reason = (asset.state_reason || `${asset.state_label}.`).trim()
  return (
    `${reason} Não pode ser escolhido para análise nova; aparece para explicar resultados e favoritos antigos.` +
    (inSelection ? ' Está na seleção salva e fica de fora ao rodar.' : '')
  )
}

// --- Seleção ---------------------------------------------------------------------------

/** O que a seleção faz ao rodar: `runs` roda; os demais ficam de fora com motivo. */
export type EntryKind = 'runs' | 'class' | 'marked' | 'missing'

export interface SelectionEntry {
  symbol: string
  asset: CatalogAsset | null
  kind: EntryKind
}

/**
 * Classifica uma seleção concreta (símbolos) com o que o catálogo já conhece.
 * Símbolo desconhecido de uma classe sem lista válida segue como `runs`: a falha
 * da Binance não bloqueia por conta própria (o servidor decide).
 */
export function resolveSelection(
  symbols: string[],
  known: ReadonlyMap<string, CatalogAsset>,
  freshness: FreshnessMap | null,
  lookedUp?: ReadonlySet<string>,
): SelectionEntry[] {
  return symbols.map((raw) => {
    const symbol = normalizeSymbol(raw)
    const asset = known.get(symbol) ?? null
    if (asset) {
      if (isMarked(asset)) return { symbol, asset, kind: 'marked' as const }
      if (asset.asset_class !== 'crypto') return { symbol, asset, kind: 'class' as const }
      return { symbol, asset, kind: 'runs' as const }
    }
    const cls: AssetClass = symbolIsCrypto(symbol) ? 'crypto' : 'stock'
    // Sem consulta feita ou sem lista válida da classe, o símbolo segue neutro.
    const notAsked = lookedUp ? !lookedUp.has(symbol) : false
    const unverified = notAsked || !freshness || freshness[cls].status === 'unavailable'
    if (unverified) {
      return { symbol, asset: null, kind: symbolIsCrypto(symbol) ? ('runs' as const) : ('class' as const) }
    }
    return { symbol, asset: null, kind: 'missing' as const }
  })
}

export interface SelectionCounts {
  crypto: number
  stock: number
  etf: number
  equities: number
  marked: number
  missing: number
  out: number
  total: number
}

export function selectionCounts(entries: SelectionEntry[]): SelectionCounts {
  const counts: SelectionCounts = {
    crypto: 0,
    stock: 0,
    etf: 0,
    equities: 0,
    marked: 0,
    missing: 0,
    out: 0,
    total: 0,
  }
  for (const entry of entries) {
    if (entry.kind === 'marked') counts.marked += 1
    else if (entry.kind === 'missing') counts.missing += 1
    else if (entry.kind === 'runs') counts.crypto += 1
    else if (entry.asset?.asset_class === 'etf') counts.etf += 1
    else counts.stock += 1
  }
  counts.equities = counts.stock + counts.etf
  counts.out = counts.equities + counts.marked + counts.missing
  counts.total = counts.crypto + counts.out
  return counts
}

/** Marcados primeiro: nunca ficam escondidos no "+N". */
export function sortedForChips(entries: SelectionEntry[]): SelectionEntry[] {
  const rank = (e: SelectionEntry) => (e.kind === 'marked' ? 0 : e.kind === 'missing' ? 1 : 2)
  return entries
    .map((entry, index) => ({ entry, index }))
    .sort((a, b) => rank(a.entry) - rank(b.entry) || a.index - b.index)
    .map((item) => item.entry)
}

export function runnableSymbols(entries: SelectionEntry[]): string[] {
  return entries.filter((e) => e.kind === 'runs').map((e) => e.symbol)
}

export function outEntries(entries: SelectionEntry[]): SelectionEntry[] {
  return sortedForChips(entries).filter((e) => e.kind !== 'runs')
}

export function classLabelOf(entry: SelectionEntry): string {
  if (entry.asset) return CLASS_LABEL[entry.asset.asset_class]
  return symbolIsCrypto(entry.symbol) ? CLASS_LABEL.crypto : 'Ação ou ETF'
}

export function entryStateLabel(entry: SelectionEntry): string | null {
  if (entry.kind === 'marked' && entry.asset) return entry.asset.state_label
  if (entry.kind === 'missing') return 'Fora do catálogo'
  return null
}

export function outLabel(entry: SelectionEntry): string {
  const state = entryStateLabel(entry)
  return `${entry.symbol} (${classLabelOf(entry)}${state ? `, ${state}` : ''})`
}

export function outReason(entry: SelectionEntry): string {
  if (entry.kind === 'marked' && entry.asset) {
    const reason = (entry.asset.state_reason || entry.asset.state_label).replace(/\.$/, '')
    return `${reason}; não entra em análise nova`
  }
  if (entry.kind === 'missing') return MISSING_REASON
  return EQUITY_REASON
}

export function outNames(entries: SelectionEntry[], max = 3): string {
  const out = outEntries(entries)
  const shown = out.slice(0, max).map(outLabel)
  const rest = out.length - shown.length
  return shown.join(', ') + (rest > 0 ? ` e mais ${fmtInt(rest)}` : '')
}

export function outWhy(counts: SelectionCounts): string {
  const hasMarked = counts.marked > 0 || counts.missing > 0
  if (counts.equities && hasMarked) {
    return `${EQUITY_REASON}, e ativos marcados pela Binance não entram em análise nova`
  }
  if (hasMarked) {
    return 'ativo marcado pela Binance (suspenso, fora de mercado, sem negociação, sem regras ou removido) não entra em análise nova'
  }
  return EQUITY_REASON
}

export function selectionCountText(counts: SelectionCounts): string {
  const parts: string[] = []
  if (counts.crypto) parts.push(`${fmtInt(counts.crypto)} cripto`)
  if (counts.stock) parts.push(`${fmtInt(counts.stock)} ${counts.stock === 1 ? 'ação' : 'ações'}`)
  if (counts.etf) parts.push(`${fmtInt(counts.etf)} ${counts.etf === 1 ? 'ETF' : 'ETFs'}`)
  const marked = counts.marked + counts.missing
  if (marked) parts.push(`${fmtInt(marked)} ${marked === 1 ? 'marcado fica de fora' : 'marcados ficam de fora'}`)
  return (
    `${fmtInt(counts.total)} ${counts.total === 1 ? 'selecionado' : 'selecionados'}` +
    (parts.length ? ` · ${parts.join(' · ')}` : '')
  )
}

export function markedNoteText(entries: SelectionEntry[]): { title: string; body: string } | null {
  const marked = entries.filter((e) => e.kind === 'marked' || e.kind === 'missing')
  if (!marked.length) return null
  const names = sortedForChips(marked).slice(0, 3).map(outLabel).join(', ')
  const one = marked.length === 1
  return {
    title: one ? 'Ativo marcado na seleção salva' : 'Ativos marcados na seleção salva',
    body:
      `${names}: a Binance pausou ou retirou ${one ? 'esse ativo' : 'esses ativos'}. ` +
      `${one ? 'Ele aparece' : 'Eles aparecem'} para explicar resultados e favoritos antigos, mas ` +
      `${one ? 'fica' : 'ficam'} de fora de qualquer análise nova. Remova com ×.`,
  }
}

// --- Confirmação do "Todos do filtro" ---------------------------------------------------

const NOUN: Record<ClassFilter, [string, string]> = {
  all: ['ativo negociável', 'ativos negociáveis'],
  crypto: ['par cripto negociável', 'pares cripto negociáveis'],
  stock: ['ação negociável', 'ações negociáveis'],
  etf: ['ETF negociável', 'ETFs negociáveis'],
}

export interface ConfirmCopy {
  prefix: string
  count: string
  middle: string
  marked: string | null
  markedText: string
  suffix: string
}

export function confirmCopy(
  filter: ClassFilter,
  query: string,
  eligible: number,
  markedCount: number,
  newCount: number | null,
): ConfirmCopy {
  const noun = NOUN[filter][eligible === 1 ? 0 : 1]
  const q = query.trim()
  const scope = q
    ? ` que correspondem a “${q}”${filter === 'all' ? ' (todas as classes)' : ''}`
    : filter === 'all'
      ? ' de todas as classes'
      : ''
  const alreadyIn = newCount !== null && newCount < eligible
  return {
    prefix: 'Incluir ',
    count: alreadyIn ? `${fmtInt(eligible)} (${fmtInt(newCount as number)} ${newCount === 1 ? 'novo' : 'novos'})` : fmtInt(eligible),
    middle: ` ${noun}${scope} na seleção?`,
    marked: markedCount > 0 ? fmtInt(markedCount) : null,
    markedText:
      markedCount > 0
        ? ` ${markedCount === 1 ? 'ativo marcado fica' : 'ativos marcados ficam'} de fora: suspensos, fora de mercado, sem negociação, sem regras ou removidos não podem ser escolhidos para análise nova.`
        : '',
    suffix: ' O que já está selecionado continua.',
  }
}

// --- Frescor e falha por classe ----------------------------------------------------------

export interface CatalogBanner {
  kind: 'stale' | 'down'
  group: 'crypto' | 'equity'
  title: string
  body: string
  retry: boolean
}

function groupFreshness(freshness: FreshnessMap, group: 'crypto' | 'equity'): ClassFreshness {
  return group === 'crypto' ? freshness.crypto : freshness.stock
}

export function catalogBanners(freshness: FreshnessMap | null): CatalogBanner[] {
  if (!freshness) return []
  const banners: CatalogBanner[] = []
  for (const group of ['crypto', 'equity'] as const) {
    const info = groupFreshness(freshness, group)
    const name = group === 'crypto' ? 'Cripto' : 'Ações e ETFs'
    if (info.status === 'stale') {
      banners.push({
        kind: 'stale',
        group,
        title: group === 'crypto' ? 'Cripto desatualizado' : 'Ações e ETFs desatualizados',
        body:
          `A Binance não respondeu na atualização de ${formatDateTime(info.last_attempt_at)}. ` +
          `Mostrando a lista válida de ${formatDateTime(info.updated_at)}; pesquisa e escolha continuam.`,
        retry: false,
      })
    } else if (info.status === 'unavailable') {
      const other = group === 'crypto' ? 'Ações e ETFs continuam disponíveis' : 'Cripto continua disponível'
      banners.push({
        kind: 'down',
        group,
        title: group === 'crypto' ? 'Cripto indisponível' : 'Ações e ETFs indisponíveis',
        body: info.refreshing
          ? `Buscando a lista de ${name.toLowerCase()} na Binance. A seleção atual foi mantida.`
          : `A Binance não respondeu e ainda não há lista salva de ${name.toLowerCase()}. ${other}; a seleção atual foi mantida.`,
        retry: !info.refreshing,
      })
    }
  }
  // Um alerta vermelho só por vez: com cripto e ações fora, o de cripto manda.
  const down = banners.filter((b) => b.kind === 'down')
  if (down.length > 1) return [down[0], ...banners.filter((b) => b.kind !== 'down')]
  return banners
}

export function freshnessLine(freshness: FreshnessMap | null): string {
  if (!freshness) return 'Catálogo Binance · carregando…'
  const crypto = freshness.crypto
  const equity = freshness.stock
  const cText = (f: ClassFreshness) => (f.updated_at ? formatDateTime(f.updated_at) : '')
  if (crypto.status === 'unavailable' && equity.status === 'unavailable') return 'Catálogo Binance sem lista salva'
  if (crypto.status === 'unavailable') return `Cripto sem lista · Ações e ETFs atualizados ${cText(equity)}`
  if (equity.status === 'unavailable') return `Cripto atualizado ${cText(crypto)} · Ações e ETFs sem lista`
  if (crypto.status === 'stale' || equity.status === 'stale') {
    return `Cripto atualizado ${cText(crypto)} · Ações e ETFs de ${cText(equity)}`
  }
  return `Catálogo Binance · atualizado ${cText(crypto)}`
}

export function emptySearchMessage(
  query: string,
  filter: ClassFilter,
  freshness: FreshnessMap | null,
): string {
  const q = query.trim()
  const cryptoDown = freshness?.crypto.status === 'unavailable'
  const equityDown = freshness?.stock.status === 'unavailable'
  if (filter === 'crypto' && cryptoDown) {
    return 'Lista de cripto indisponível por falha da Binance. Use “Tentar de novo” no aviso acima; a seleção atual foi mantida.'
  }
  if (cryptoDown && (filter === 'all' || filter === 'crypto')) {
    return `Nenhuma ação ou ETF para “${q}”. Cripto está indisponível agora por falha da Binance, então pares cripto não aparecem na pesquisa até a lista voltar. A seleção atual foi mantida.`
  }
  if (equityDown && (filter === 'all' || filter === 'stock' || filter === 'etf')) {
    return `Nenhum par cripto para “${q}”. Ações e ETFs estão indisponíveis agora por falha da Binance, então não aparecem na pesquisa até a lista voltar. A seleção atual foi mantida.`
  }
  const where =
    filter === 'all' ? 'todas as classes' : filter === 'crypto' ? 'Cripto' : filter === 'stock' ? 'Ações' : 'ETFs'
  return `Nenhum ativo para “${q}” em ${where}. Confira o símbolo ou troque a classe. A seleção atual foi mantida.`
}

// --- Aviso antes e depois de rodar (Combo e Otimização) -----------------------------------

export type RunMode = 'none' | 'blocked' | 'single' | 'batch'
export type RunPage = 'combo' | 'optimize'
/** Por que um ativo fica fora: marcado/fora do catálogo, tempo que ação/ETF não roda, 5m que não cobre a janela. */
export type OutKind = 'marked' | 'missing' | 'timeframe' | 'coverage'

export interface PlannedAsset {
  entry: SelectionEntry
  runs: boolean
  outKind: OutKind | null
  /** Motivo curto, sem ponto final ("ação e ETF não rodam em 5m; …"). */
  reason: string | null
}

export interface RunPlan {
  mode: RunMode
  page: RunPage
  timeframe: string
  assets: PlannedAsset[]
  /** Os que rodam. */
  runnable: string[]
  /** Todos os selecionados: o lote manda todos; o servidor decide e devolve "Fora" com o motivo. */
  selected: string[]
  out: PlannedAsset[]
  counts: SelectionCounts
  /** 1 ação ou ETF sozinha e que roda (backtest de 1 ativo, sem lote). */
  equityRun: SelectionEntry | null
  /** 1 ação ou ETF sozinha, rode ou não. */
  singleEquity: SelectionEntry | null
  hasEquity: boolean
  hasCrypto: boolean
}

/** Tempos que ação e ETF não rodam (card #1119, decisão 5). A Otimização também recusa 30m. */
export function equityBadTimeframes(page: RunPage): string[] {
  return page === 'optimize' ? ['1m', '5m', '30m'] : ['1m', '5m']
}

export const EQUITY_TIMEFRAME_HINT = 'Escolha 15m, 1h, 4h ou 1d.'
export const OPTIMIZE_FIXED_WINDOW_LABEL = '1 a 31 jan. 2024'
export const OPTIMIZE_FIXED_WINDOW = { start: '2024-01-01', end: '2024-01-31' }
const NY = 'America/New_York'

/** Quando a cobertura do 5m (catálogo) mostra que ele não cobre a janela fixa da Otimização. */
export function fiveMinuteGap(entry: SelectionEntry | null, windowStart: string): { startsAt: string } | null {
  const frame = entry?.asset?.history.timeframes?.find((t) => t.timeframe === '5m' && t.origin === 'native' && t.from)
  if (!frame?.from) return null
  if (new Date(frame.from).getTime() <= new Date(`${windowStart}T23:59:59Z`).getTime()) return null
  return { startsAt: formatDate(frame.from, NY) }
}

/** Onde o 5m de ação/ETF começa na Binance, pelas séries já guardadas na seleção (a mais antiga). */
function equityFiveMinuteHorizon(entries: SelectionEntry[]): string | null {
  const starts = entries
    .map((e) => e.asset?.history.timeframes?.find((t) => t.timeframe === '5m' && t.origin === 'native' && t.from)?.from)
    .filter((from): from is string => !!from)
    .sort()
  return starts[0] ?? null
}

function equityCoverageGap(
  entry: SelectionEntry,
  horizon: string | null,
): { startsAt: string } | null {
  const own = fiveMinuteGap(entry, OPTIMIZE_FIXED_WINDOW.start)
  if (own) return own
  if (entry.asset?.history.timeframes?.some((t) => t.timeframe === '5m' && t.origin === 'native' && t.from)) {
    return null // o 5m dele cobre a janela
  }
  if (horizon && new Date(horizon).getTime() > new Date(`${OPTIMIZE_FIXED_WINDOW.start}T23:59:59Z`).getTime()) {
    return { startsAt: formatDate(horizon, NY) }
  }
  return null
}

function timeframeAdvice(page: RunPage): string {
  return page === 'optimize'
    ? 'para incluí-los, use 1d aqui ou o Combo, que tem período'
    : 'para incluí-los, use 15m, 1h, 4h ou 1d'
}

function planAsset(
  entry: SelectionEntry,
  timeframe: string,
  page: RunPage,
  horizon: string | null,
): PlannedAsset {
  if (entry.kind === 'marked') return { entry, runs: false, outKind: 'marked', reason: outReason(entry) }
  if (entry.kind === 'missing') return { entry, runs: false, outKind: 'missing', reason: MISSING_REASON }
  if (entry.kind === 'runs') return { entry, runs: true, outKind: null, reason: null }
  // ação ou ETF
  if (equityBadTimeframes(page).includes(timeframe)) {
    return {
      entry,
      runs: false,
      outKind: 'timeframe',
      reason: `ação e ETF não rodam em ${timeframe}; ${timeframeAdvice(page)}`,
    }
  }
  if (page === 'optimize' && ['15m', '1h', '4h'].includes(timeframe)) {
    const gap = equityCoverageGap(entry, horizon)
    if (gap) {
      return {
        entry,
        runs: false,
        outKind: 'coverage',
        reason:
          `o 5m de ${entry.symbol} começa em ${gap.startsAt} e não cobre ${OPTIMIZE_FIXED_WINDOW_LABEL}, ` +
          'o período fixo desta tela; use 1d aqui ou o Combo, que tem período',
      }
    }
  }
  return { entry, runs: true, outKind: null, reason: null }
}

/**
 * Plano do lote por classe e tempo (card #1120, decisões 2 e 6). Seleção com mais de 1 ativo é sempre
 * lote: cripto roda; ação e ETF rodam em 15m, 1h, 4h e 1d (na Otimização, só se o 5m cobre o período
 * fixo); o que não serve fica fora com o motivo, antes de começar. 1 ativo segue o caminho do #1119.
 */
export function planRun(
  entries: SelectionEntry[],
  options: { timeframe?: string; page?: RunPage } = {},
): RunPlan {
  const timeframe = (options.timeframe ?? '1d').toLowerCase()
  const page = options.page ?? 'combo'
  const horizon = equityFiveMinuteHorizon(entries)
  const assets = entries.map((entry) => planAsset(entry, timeframe, page, horizon))
  const runs = assets.filter((a) => a.runs)
  const out = assets.filter((a) => !a.runs)
  const equities = entries.filter((e) => e.kind === 'class')
  let mode: RunMode
  if (entries.length === 0) mode = 'none'
  else if (runs.length === 0) mode = 'blocked'
  else if (entries.length === 1) mode = 'single'
  else mode = 'batch'
  const singleEquity = entries.length === 1 && equities.length === 1 ? equities[0] : null
  return {
    mode,
    page,
    timeframe,
    assets,
    runnable: runs.map((a) => a.entry.symbol),
    selected: entries.map((e) => e.symbol),
    out,
    counts: selectionCounts(entries),
    equityRun: mode === 'single' && singleEquity ? singleEquity : null,
    singleEquity,
    hasEquity: equities.length > 0,
    hasCrypto: entries.some((e) => e.kind === 'runs' || (e.kind !== 'class' && symbolIsCrypto(e.symbol))),
  }
}

/** "1 ação (NVDA)" ou "1 ETF (SPY)". */
export function equityRunLabel(entry: SelectionEntry): string {
  return `1 ${entry.asset?.asset_class === 'etf' ? 'ETF' : 'ação'} (${entry.symbol})`
}

/** Tempos "(só cripto)": com ação ou ETF na seleção, os que ação/ETF não rodam. */
export function cryptoOnlyTimeframes(plan: RunPlan): string[] {
  return plan.hasEquity ? equityBadTimeframes(plan.page) : []
}

/** Só ação/ETF na seleção (sem cripto): esses tempos ficam indisponíveis; com cripto, seguem escolhíveis. */
export function timeframeDisabled(plan: RunPlan, timeframe: string): boolean {
  return plan.hasEquity && !plan.hasCrypto && equityBadTimeframes(plan.page).includes(timeframe)
}

/** Campo Market Data do Combo: fonte por ativo na seleção mista (decisão 6). */
export function marketDataText(plan: RunPlan): string {
  if (plan.hasEquity && plan.hasCrypto) return 'Por ativo: CCXT (cripto) · Binance Ações (ação e ETF)'
  if (plan.hasEquity) return 'Binance Ações · pregão regular de Nova York · ajustado por split'
  return 'CCXT (crypto exchange data)'
}

export const CLASS_NOTE: Record<RunPage, string> = {
  combo:
    'Cripto, ação e ETF rodam juntos no lote: cada ativo usa a sua fonte, sessão, ajuste e moeda, e o melhor resultado de cada um vira favorito. ' +
    'Ação e ETF não rodam em 1m e 5m: nesses tempos ficam fora com o motivo. 1 ação ou ETF sozinha abre o resultado, sem salvar.',
  optimize:
    'Cripto, ação e ETF rodam juntos no lote, no período fixo desta tela: cada ativo usa a sua fonte, sessão, ajuste e moeda, e o melhor resultado de cada um vira favorito. ' +
    'Ação e ETF não rodam em 1m, 5m e 30m, nem em 15m, 1h e 4h quando o 5m deles não cobre o período fixo: ficam fora com o motivo; use 1d aqui ou o Combo, que tem período. ' +
    '1 ação ou ETF sozinha mostra o resultado ao lado.',
}

export interface EquityRunBlock {
  /** Texto do "antes de rodar" (âmbar). */
  copy: string
  /** Aviso `role=status` ao rodar/escolher o tempo. */
  notice: RunNotice
}

/**
 * Ação/ETF sozinha num tempo que não roda: o valor fica como está (sem troca silenciosa) e a tela
 * avisa antes de rodar. `null` quando o tempo serve.
 */
export function equityTimeframeBlock(
  plan: RunPlan,
  timeframe: string,
  page: RunPage,
): EquityRunBlock | null {
  const entry = plan.singleEquity
  if (!entry) return null
  const planned = plan.assets[0]
  if (!planned || planned.runs) return null
  const tf = timeframe.toLowerCase()
  const cls = entry.asset ? CLASS_LABEL[entry.asset.asset_class] : 'Ação'
  if (planned.outKind === 'timeframe') {
    return {
      copy: `Nada será executado: ${entry.symbol} (${cls}) não roda em ${tf}. ${EQUITY_TIMEFRAME_HINT}`,
      notice: {
        tone: 'warn',
        title: EQUITY_TIMEFRAME_HINT.replace(/\.$/, ''),
        body:
          page === 'optimize'
            ? 'Ação e ETF não rodam em 1m, 5m nem 30m. Nada foi executado; a seleção foi mantida.'
            : 'Ação e ETF não rodam em 1m nem 5m. Nada foi executado; a seleção foi mantida.',
      },
    }
  }
  if (planned.outKind === 'coverage') {
    const startsAt = /começa em (.+?) e não cobre/.exec(planned.reason ?? '')?.[1] ?? ''
    // 1 ação/ETF sozinha (#1119): o motivo, ponto final e o conselho em frase própria
    const why = (planned.reason ?? '').replace(/; use 1d aqui ou o Combo, que tem período$/, '')
    return {
      copy: `Nada será executado: ${why}. Use 1d aqui ou o Combo, que tem período.`,
      notice: {
        tone: 'warn',
        title: `${entry.symbol} não roda em ${tf} nesta tela`,
        body: `O 5m de ${entry.symbol} começa em ${startsAt} e não cobre ${OPTIMIZE_FIXED_WINDOW_LABEL}, o período fixo da Otimização. Nada foi executado. Use 1d aqui ou o Combo, que tem período.`,
      },
    }
  }
  return null
}

function listNames(assets: PlannedAsset[], max = 3): string {
  const shown = assets.slice(0, max).map((a) => outLabel(a.entry))
  const rest = assets.length - shown.length
  return shown.join(', ') + (rest > 0 ? ` e mais ${fmtInt(rest)}` : '')
}

/** Motivo do grupo que fica fora: os distintos, na ordem timeframe, cobertura, marcado/fora do catálogo. */
function groupWhy(out: PlannedAsset[], page: RunPage, timeframe: string): string {
  const parts: string[] = []
  if (out.some((a) => a.outKind === 'timeframe')) {
    parts.push(`ação e ETF não rodam em ${timeframe}; ${timeframeAdvice(page)}`)
  }
  const coverage = out.filter((a) => a.outKind === 'coverage')
  if (coverage.length) {
    const dates = new Set(coverage.map((a) => /começa em (.+?) e não cobre/.exec(a.reason ?? '')?.[1] ?? ''))
    parts.push(
      dates.size === 1
        ? `o 5m deles começa em ${[...dates][0]} e não cobre ${OPTIMIZE_FIXED_WINDOW_LABEL}, o período fixo desta tela; use 1d aqui ou o Combo, que tem período`
        : coverage.map((a) => a.reason).join('; '),
    )
  }
  if (out.some((a) => a.outKind === 'marked' || a.outKind === 'missing')) {
    parts.push(
      'ativo marcado pela Binance (suspenso, fora de mercado, sem negociação, sem regras ou removido) não entra em análise nova',
    )
  }
  return parts.join('; ')
}

export interface RunCopy {
  text: string
  blocked: boolean
  /** Partes do lote para o componente pôr o trecho de fora em âmbar. */
  parts?: { lead: string; runs: string; out: string | null }
}

function breakdownOf(plan: RunPlan): string {
  const counts = { crypto: 0, stock: 0, etf: 0 }
  for (const a of plan.assets) {
    if (!a.runs) continue
    if (a.entry.kind === 'runs') counts.crypto += 1
    else if (a.entry.asset?.asset_class === 'etf') counts.etf += 1
    else counts.stock += 1
  }
  const parts: string[] = []
  if (counts.crypto) parts.push(`${fmtInt(counts.crypto)} cripto`)
  if (counts.stock) parts.push(`${fmtInt(counts.stock)} ${counts.stock === 1 ? 'ação' : 'ações'}`)
  if (counts.etf) parts.push(`${fmtInt(counts.etf)} ${counts.etf === 1 ? 'ETF' : 'ETFs'}`)
  return parts.join(', ')
}

/** Cópia que a tela mostra antes do clique (decisão 6). */
export function runCopy(plan: RunPlan, page: RunPage = plan.page, options: { timeframe?: string } = {}): RunCopy {
  const timeframe = (options.timeframe ?? plan.timeframe).toLowerCase()
  if (plan.mode === 'none') {
    return { text: 'Nenhum ativo selecionado: escolha ao menos 1 par cripto em USDT.', blocked: false }
  }
  if (plan.mode === 'blocked') {
    const block = equityTimeframeBlock(plan, timeframe, page)
    if (block) return { text: block.copy, blocked: true }
    return {
      text: `Nada será executado: ${listNames(plan.out)} — ${groupWhy(plan.out, page, timeframe)}.`,
      blocked: true,
    }
  }
  if (plan.mode === 'single') {
    if (plan.equityRun) {
      const label = equityRunLabel(plan.equityRun)
      return {
        text:
          page === 'combo'
            ? `${label}: otimiza e abre o resultado, sem salvar em favoritos: ações e ETFs ainda não podem ser favoritados.`
            : `${label}: otimiza em ${timeframe}, de ${OPTIMIZE_FIXED_WINDOW_LABEL}, e mostra o resultado ao lado.`,
        blocked: false,
      }
    }
    return {
      text:
        page === 'combo'
          ? '1 ativo selecionado: otimiza, salva em favoritos e abre a página de favoritos.'
          : '1 ativo: otimiza e mostra o resultado ao lado.',
      blocked: false,
    }
  }
  const total = plan.selected.length
  const running = plan.runnable.length
  if (plan.out.length === 0) {
    const text =
      `Lote de ${fmtInt(total)} ativos (${breakdownOf(plan)}): otimiza cada um com esta configuração` +
      `${page === 'optimize' ? ', no período fixo desta tela,' : ''} e grava o melhor de cada em favoritos ` +
      '(nota "gerado em lote"). Antes de começar, você confirma o lote.'
    return { text, blocked: false }
  }
  const lead = `Lote de ${fmtInt(total)} ativos: roda ${fmtInt(running)}`
  const runs = `(${namesOf(plan.assets.filter((a) => a.runs))}).`
  const outText = `Fora antes de começar: ${listNames(plan.out)} — ${groupWhy(plan.out, page, timeframe)}.`
  return { text: `${lead} ${runs} ${outText}`, blocked: false, parts: { lead, runs, out: outText } }
}

function namesOf(assets: PlannedAsset[], max = 3): string {
  const shown = assets.slice(0, max).map((a) => a.entry.symbol)
  const rest = assets.length - shown.length
  return shown.join(', ') + (rest > 0 ? ` e mais ${fmtInt(rest)}` : '')
}

export interface RunNotice {
  tone: 'alert' | 'warn'
  title: string
  body: string
}

/** Aviso ao rodar quando nada roda (`blocked`): o que ficou fora e por quê. A seleção é mantida. */
export function blockedNotice(plan: RunPlan, page: RunPage = plan.page): RunNotice {
  const kinds = new Set(plan.out.map((a) => a.outKind))
  const onlyMarked = [...kinds].every((k) => k === 'marked' || k === 'missing')
  const onlyEquity = [...kinds].every((k) => k === 'timeframe' || k === 'coverage')
  const title = onlyMarked
    ? 'Ativo marcado pela Binance não entra em análise nova'
    : onlyEquity
      ? kinds.has('coverage') && !kinds.has('timeframe')
        ? `Ação e ETF não rodam em ${plan.timeframe} nesta tela`
        : `Ação e ETF não rodam em ${plan.timeframe}`
      : 'Nenhum ativo da seleção pode rodar agora'
  return {
    tone: 'alert',
    title,
    body: `${listNames(plan.out)}: ${groupWhy(plan.out, page, plan.timeframe)}. Nada foi executado. A seleção foi mantida.`,
  }
}

/**
 * Linha `role=status` enquanto o backtest de 1 ação/ETF coleta o histórico (card #1119, decisão 4).
 * Combo: tempo gráfico e o 5m do intrabar; Otimização: o tempo gráfico na janela fixa.
 */
export function collectingCopy(
  symbol: string,
  page: RunPage,
  timeframe: string,
  deepBacktest = true,
): string {
  const tf = timeframe.toLowerCase()
  const tail = 'antes de otimizar… Na primeira execução de um ativo isso pode levar alguns segundos.'
  if (page === 'optimize') {
    return `Coletando histórico de ${symbol} (${tf} de ${OPTIMIZE_FIXED_WINDOW_LABEL}) ${tail}`
  }
  const series = tf === '1d' ? (deepBacktest ? '1d e o 5m do intrabar' : '1d') : `${tf}, montado do 5m`
  return `Coletando histórico de ${symbol} para a janela pedida (${series}) ${tail}`
}

/** 422 `history_unavailable` (coleta sem nada guardado) vira alerta com o motivo, nunca resultado vazio. */
export function historyUnavailableNotice(detail: unknown): RunNotice | null {
  if (!detail || typeof detail !== 'object') return null
  const d = detail as Record<string, unknown>
  if (d.code !== 'history_unavailable') return null
  const symbol = typeof d.symbol === 'string' ? d.symbol : 'o ativo'
  const reason = typeof d.reason === 'string' ? d.reason : ''
  const cap = reason ? `${reason[0].toUpperCase()}${reason.slice(1)}` : ''
  const lead = !cap
    ? `Nada de ${symbol} guardado para esta janela.`
    : d.error_code
      ? `${cap} e nada de ${symbol} guardado para esta janela.`
      : `${cap}.`
  return {
    tone: 'alert',
    title: `Histórico de ${symbol} indisponível agora`,
    body: `${lead} Nada foi executado. Tente de novo em alguns minutos.`,
  }
}

/** Mensagem da API (`detail.message`) em recusa estruturada; texto simples cai no fallback. */
export function refusalMessage(detail: unknown, fallback: string): string {
  if (typeof detail === 'string' && detail.trim()) return detail
  if (detail && typeof detail === 'object') {
    const message = (detail as Record<string, unknown>).message
    if (typeof message === 'string' && message.trim()) return message
    const nested = (detail as Record<string, unknown>).detail
    if (nested) return refusalMessage(nested, fallback)
  }
  return fallback
}

export function urlSymbolNotice(symbol: string): { title: string; body: string } {
  return {
    title: `${symbol} não está no catálogo da Binance`,
    body: 'O endereço trouxe esse símbolo, mas ele não foi marcado. Escolha os ativos na lista.',
  }
}

// --- Preflight da Descoberta -------------------------------------------------------------

export interface PreflightExcludedAsset {
  symbol: string
  asset_class: AssetClass | null
  state: AssetState | null
  kind: 'class' | 'marked' | 'missing'
  reason: string
  combinations: number
}

export function outOfSweepTitle(assets: PreflightExcludedAsset[]): string {
  const combos = assets.reduce((sum, a) => sum + a.combinations, 0)
  return (
    `Fora desta varredura: ${fmtInt(assets.length)} ${assets.length === 1 ? 'ativo' : 'ativos'} ` +
    `(${fmtInt(combos)} ${combos === 1 ? 'combinação' : 'combinações'})`
  )
}

export function preflightExcludedLabel(asset: PreflightExcludedAsset): string {
  const cls = asset.asset_class ? CLASS_LABEL[asset.asset_class] : 'Ação ou ETF'
  const state = asset.kind === 'marked' && asset.state ? STATE_NAMES[asset.state] : null
  return `${asset.symbol} (${cls}${state ? `, ${state}` : ''})`
}

const STATE_NAMES: Record<AssetState, string> = {
  tradable: 'Negociável',
  suspended: 'Suspenso',
  off_market: 'Fora de mercado',
  no_trading: 'Sem negociação',
  no_rules: 'Sem regras de negociação',
  removed: 'Removido',
}

export function preflightRestLine(assets: PreflightExcludedAsset[], shown: number): string | null {
  const rest = assets.length - shown
  if (rest <= 0) return null
  const hasMarked = assets.slice(shown).some((a) => a.kind !== 'class')
  return hasMarked
    ? `e mais ${fmtInt(rest)} ativos, pelos mesmos motivos.`
    : `e mais ${fmtInt(rest)} ações e ETFs, pelo mesmo motivo.`
}
