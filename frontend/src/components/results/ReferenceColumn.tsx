import { useCallback, useEffect, useRef, useState } from 'react'
import { API_BASE_URL } from '@/lib/apiBase'
import { authFetch } from '@/lib/authFetch'
import {
    COLUMN_HINT,
    CURRENCY_NOTE_TITLE,
    PRICE_RETURN_TEXT,
    cellView,
    classLabel,
    columnChoiceHints,
    columnHeader,
    stamp,
    stripSummary,
    type CandidateWindow,
    type CellSummary,
    type ColumnCounts,
} from '@/lib/benchmarkComparison'
import { ICON_INFO, ICON_SWITCH, ICON_WARN, ReferencePicker } from './ReferencePicker'
import './BenchmarkComparison.css'

export interface RefColumnInfo {
    id: string
    reference: { symbol: string; asset_class?: string | null; currency?: string | null; name?: string | null; return_kind?: string; version_label?: string | null }
    reference_version?: string | null
    status: 'collecting' | 'computing' | 'done' | 'failed'
    done: number
    total: number
    error?: string | null
    active: boolean
    created_at?: string | null
    completed_at?: string | null
    counts?: ColumnCounts
}

export interface RefColumnState {
    column: RefColumnInfo | null
    pending: RefColumnInfo | null
}

const RUNNING = new Set(['collecting', 'computing'])
const POLL_MS = 2000

export function isColumnRunning(state: RefColumnState | null | undefined): boolean {
    return Boolean(
        (state?.column && RUNNING.has(state.column.status)) || (state?.pending && RUNNING.has(state.pending.status)),
    )
}

/** Cabeçalho "Contra <ativo>" com a dica que diz que a coluna não ordena (P2 da crítica). */
export function ReferenceColumnHeader({ symbol }: { symbol: string }) {
    return (
        <th scope="col" className="b23-xth" data-testid="extra-col-header">
            <span>{columnHeader(symbol)}</span>
            <span className="th-hint">{COLUMN_HINT}</span>
        </th>
    )
}

export function ReferenceColumnCell({
    cell,
    symbol,
    computing,
    resultId,
}: {
    cell: CellSummary | null | undefined
    symbol: string
    computing: boolean
    resultId: string
}) {
    const view = cellView(cell, symbol, computing)
    return (
        <td className="b23-xcell" data-label={columnHeader(symbol)} data-testid={`extra-cell-${resultId}`} data-b23-xstate={view.kind === 'off' ? view.code : view.kind}>
            <div className={`b23-xc${view.kind === 'off' ? ' b23-xc-off' : ''}`}>
                {view.kind === 'busy' ? <span className="b23-xc-busy">{view.text}</span> : null}
                {view.kind === 'no_sample' ? <span className="b23-xc-dim">{view.text}</span> : null}
                {view.kind === 'off' ? (
                    <>
                        <strong>{view.title}</strong>
                        <span>{view.reason}</span>
                    </>
                ) : null}
                {view.kind === 'valid' ? (
                    <>
                        <b data-tone={view.tone}>{view.delta}</b>
                        <span>{view.refLine}</span>
                        <span className="b23-xc-dim">
                            <span className="sr-only-b23">Período comum </span>
                            {view.period}
                        </span>
                        {view.fx ? (
                            <span className="b23-xc-warn">
                                {ICON_WARN}
                                <span>USDT tratado como USD</span>
                            </span>
                        ) : null}
                    </>
                ) : null}
            </div>
        </td>
    )
}

export interface ReferenceColumnStripProps {
    sweepId: string
    state: RefColumnState | null
    /** Recarrega a página do leaderboard (sem mudar ordem, filtros ou página). */
    onReload: () => void
}

/**
 * Faixa "Coluna extra" do Decidir (card #1123, decisão 10; layout de `discovery.html`): padrão "Nenhuma";
 * com referência, ativo, classe, moeda, tipo de retorno, resumo contado sobre a varredura, aviso de moeda,
 * linha de gravação, progresso (`role=status`) e falha (`role=alert`, fora do status) com "Tentar de novo".
 * A coluna não muda a ordem, o rank global nem a elegibilidade.
 */
export function ReferenceColumnStrip({ sweepId, state, onReload }: ReferenceColumnStripProps) {
    const triggerRef = useRef<HTMLButtonElement | null>(null)
    const [open, setOpen] = useState(false)
    const [candidates, setCandidates] = useState<CandidateWindow[]>([])
    const [announce, setAnnounce] = useState('')
    const [requestError, setRequestError] = useState<string | null>(null)
    const [sending, setSending] = useState<string | null>(null)
    const lastSeen = useRef<string>('')
    const column = state?.column ?? null
    const pending = state?.pending ?? null

    const loadCandidates = useCallback(async () => {
        try {
            const res = await authFetch(`${API_BASE_URL}/combos/discovery/sweeps/${sweepId}/reference-column`)
            if (!res.ok) return
            const data = await res.json()
            setCandidates(Array.isArray(data?.candidates) ? data.candidates : [])
        } catch {
            /* o aviso antes da escolha some; a escolha segue */
        }
    }, [sweepId])

    // Progresso: consulta a cada 2 s enquanto coleta ou calcula; cada mudança recarrega a página.
    const running = isColumnRunning(state)
    useEffect(() => {
        if (!running) return undefined
        let stopped = false
        const timer = window.setInterval(async () => {
            try {
                const res = await authFetch(`${API_BASE_URL}/combos/discovery/sweeps/${sweepId}/reference-column`)
                if (!res.ok || stopped) return
                const data = await res.json()
                const key = JSON.stringify([
                    data?.column?.id, data?.column?.status, data?.column?.counts?.computed,
                    data?.pending?.id, data?.pending?.status,
                ])
                if (key !== lastSeen.current) {
                    lastSeen.current = key
                    onReload()
                }
            } catch {
                /* tenta de novo no próximo ciclo */
            }
        }, POLL_MS)
        return () => {
            stopped = true
            window.clearInterval(timer)
        }
    }, [running, sweepId, onReload])

    // Anúncio quando a coluna termina (uma vez por coluna).
    const doneKey = column && column.status === 'done' ? column.id : ''
    const prevDone = useRef(doneKey)
    useEffect(() => {
        if (doneKey && prevDone.current !== doneKey) {
            setAnnounce(`Coluna ${columnHeader(column?.reference.symbol)} gravada nesta varredura. A ordem do ranking não mudou.`)
        }
        prevDone.current = doneKey
    }, [doneKey, column?.reference.symbol])

    const choose = async (symbol: string | null) => {
        setOpen(false)
        setRequestError(null)
        setAnnounce('')
        setSending(symbol ?? '')
        try {
            const res = await authFetch(`${API_BASE_URL}/combos/discovery/sweeps/${sweepId}/reference-column`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ reference_symbol: symbol }),
            })
            const data = await res.json().catch(() => ({}))
            if (!res.ok) {
                const detail = data?.detail
                setRequestError(
                    (detail && typeof detail === 'object' && detail.message) ||
                        (typeof detail === 'string' ? detail : 'Não foi possível gravar a escolha da coluna extra.'),
                )
                return
            }
            if (!symbol) setAnnounce('Coluna extra removida. O ranking segue igual.')
            else if (data?.reactivated) setAnnounce(`Coluna ${columnHeader(symbol)} já gravada nesta varredura: reativada sem recalcular.`)
            onReload()
        } catch {
            setRequestError('Não foi possível gravar a escolha da coluna extra: falha de conexão.')
        } finally {
            setSending(null)
        }
    }

    const retry = async () => {
        setRequestError(null)
        try {
            const res = await authFetch(`${API_BASE_URL}/combos/discovery/sweeps/${sweepId}/reference-column/retry`, { method: 'POST' })
            if (!res.ok) setRequestError('Não foi possível tentar de novo agora.')
            onReload()
        } catch {
            setRequestError('Não foi possível tentar de novo: falha de conexão.')
        }
    }

    const shown = column
    const ref = shown?.reference
    const done = shown?.status === 'done'
    const priceOnly = ref && (ref.asset_class === 'stock' || ref.asset_class === 'etf')
    // Falha na coleta (a escolha nova não virou coluna) ou no cálculo da coluna ativa.
    const failed = pending?.status === 'failed' ? pending : shown?.status === 'failed' ? shown : null
    const busyText = (() => {
        if (sending !== null) return sending ? `Gravando a escolha de ${sending}…` : 'Removendo a coluna extra…'
        if (pending?.status === 'collecting') return `Coletando histórico de ${pending.reference.symbol} na Binance…`
        if (pending?.status === 'computing') return `Calculando contra ${pending.reference.symbol}…`
        if (shown?.status === 'computing') return `Calculando contra ${shown.reference.symbol}: ${shown.done} de ${shown.total} candidatos…`
        if (shown?.status === 'collecting') return `Coletando histórico de ${shown.reference.symbol} na Binance…`
        return ''
    })()
    const previousText = shown ? `a coluna continua contra ${shown.reference.symbol}.` : 'o ranking continua sem coluna extra.'

    return (
        <div className="b23-xref" data-testid="discovery-extra-ref" data-b23-xstate={busyText ? 'busy' : shown ? 'done' : 'none'}>
            <div className="b23-xref-main">
                <p className="b23-xref-head">
                    <span className="b23-k">Coluna extra</span>
                    <strong data-testid="extra-ref-name">{ref ? ref.symbol : 'Nenhuma'}</strong>
                    {ref ? (
                        <span className="b23-ref-meta">
                            {classLabel(ref.asset_class) ? <span className="b23-chip">{classLabel(ref.asset_class)}</span> : null}
                            {ref.currency ? <span>{ref.currency}</span> : null}
                            <span aria-hidden="true">·</span>
                            <span>buy-and-hold</span>
                            {priceOnly ? <span data-testid="extra-ref-price">{PRICE_RETURN_TEXT}</span> : null}
                        </span>
                    ) : null}
                </p>
                <p className="b23-xref-text">
                    {ref
                        ? `Diferença de CAGR de cada candidato contra ${ref.symbol} no período comum. A coluna não muda a ordem, o rank global nem a elegibilidade.`
                        : 'Compare cada candidato com outra referência, como SPY, numa coluna a mais. A ordem e o rank global não mudam. Escolher uma referência guarda as amostras desta varredura enquanto a coluna existir.'}
                </p>
                {done && shown?.counts ? (
                    <p className="b23-xref-sum" data-testid="extra-ref-summary">{stripSummary(shown.counts, shown.reference.symbol)}</p>
                ) : null}
                {done && shown?.counts?.currency_note ? (
                    <p className="b23-xref-fx" data-testid="extra-ref-fx">
                        {ICON_WARN}
                        <span>
                            <strong>{CURRENCY_NOTE_TITLE}</strong> Nos candidatos marcados, a comparação é só em percentual.
                        </span>
                    </p>
                ) : null}
                {done && shown ? (
                    <p className="b23-rec" data-testid="extra-ref-recorded">
                        {ICON_INFO}
                        <span>
                            Gravada nesta varredura para você em {stamp(shown.completed_at || shown.created_at)}. Amostra da referência:{' '}
                            {shown.reference.symbol}
                            {shown.reference_version ? ` versão ${shown.reference_version}` : ''}. Abrir, recarregar ou exportar de novo não recalcula.
                        </span>
                    </p>
                ) : null}
            </div>
            <button
                ref={triggerRef}
                type="button"
                className="b23-switch"
                aria-haspopup="dialog"
                data-testid="discovery-ref-switch"
                disabled={sending !== null}
                onClick={() => {
                    void loadCandidates()
                    setOpen(true)
                }}
            >
                {ICON_SWITCH}
                <span>{shown ? 'Trocar referência' : 'Comparar com outra referência'}</span>
            </button>
            <div className="b23-live" role="status" aria-live="polite" data-testid="extra-ref-live">
                {busyText ? (
                    <>
                        <span className="b23-spin" aria-hidden="true" />
                        <span>{busyText}</span>
                    </>
                ) : announce ? (
                    <span>{announce}</span>
                ) : null}
            </div>
            {failed || requestError ? (
                <div className="b23-fail" role="alert" data-testid="extra-ref-failure">
                    <p>
                        {failed && failed === shown
                            ? `${failed.error || 'O cálculo da coluna parou.'} As células já gravadas continuam; as que faltam aparecem como "Calculando…".`
                            : failed
                                ? `${failed.error || `Não foi possível coletar o histórico de ${failed.reference.symbol} na Binance.`} Nada foi gravado: ${previousText}`
                                : requestError}
                    </p>
                    {failed ? (
                        <button type="button" className="b23-btn" onClick={() => void retry()} data-testid="extra-ref-retry">
                            Tentar de novo
                        </button>
                    ) : null}
                </div>
            ) : null}
            {open ? (
                <ReferencePicker
                    title="Escolher referência da coluna extra"
                    description="Buy-and-hold de um ativo do catálogo, numa coluna extra do ranking. A coluna é calculada uma vez para todos os candidatos desta varredura e gravada na varredura para você. Não muda a ordem, o rank global nem a elegibilidade. Ativo sem histórico guardado é coletado na Binance ao escolher."
                    own={{
                        symbol: 'Próprio ativo',
                        name: 'Sem coluna extra: o ranking já compara cada candidato com o próprio ativo',
                        hist: 'Buy-and-hold do ativo de cada candidato',
                    }}
                    currentId={ref ? ref.symbol : 'own'}
                    hintsFor={(asset) => columnChoiceHints(asset, candidates)}
                    onUse={(symbol) => void choose(symbol)}
                    onClose={() => setOpen(false)}
                    returnFocus={triggerRef}
                />
            ) : null}
        </div>
    )
}

export interface RankingExportProps {
    sweepId: string
    params: Record<string, string>
    disabled: boolean
    column: RefColumnInfo | null
}

/** "Exportar planilha" do Decidir: recorte filtrado inteiro, na ordem e com o rank global (44 px, status `polite`). */
export function RankingExportButton({ sweepId, params, disabled, column }: RankingExportProps) {
    const [status, setStatus] = useState('')
    const [busy, setBusy] = useState(false)
    const run = async () => {
        setBusy(true)
        setStatus('Gerando a planilha…')
        try {
            const query = new URLSearchParams(params).toString()
            const res = await authFetch(`${API_BASE_URL}/combos/discovery/sweeps/${sweepId}/leaderboard/export?${query}`)
            if (!res.ok) throw new Error(`HTTP ${res.status}`)
            const blob = await res.blob()
            const disposition = res.headers.get('Content-Disposition') || ''
            const match = disposition.match(/filename="?([^";]+)"?/)
            const filename = match ? match[1] : `descoberta_${sweepId}_ranking.xlsx`
            const rows = res.headers.get('X-Export-Rows')
            const extra = res.headers.get('X-Export-Extra')
            const url = window.URL.createObjectURL(blob)
            const link = document.createElement('a')
            link.href = url
            link.download = filename
            document.body.appendChild(link)
            link.click()
            window.URL.revokeObjectURL(url)
            document.body.removeChild(link)
            const extraText =
                extra === 'included' && column
                    ? ` · colunas (extra) contra ${column.reference.symbol}`
                    : extra === 'computing' && column
                        ? ` · sem as colunas (extra): a coluna contra ${column.reference.symbol} ainda está em cálculo`
                        : ''
            setStatus(
                `Planilha baixada: ${filename} · ${rows ?? 'todos os'} candidatos do recorte, todas as páginas, na ordem do ranking · abas Ranking e Legenda${extraText}.`,
            )
        } catch {
            setStatus('Não foi possível exportar a planilha. Tente de novo.')
        } finally {
            setBusy(false)
        }
    }
    return (
        <>
            <button
                type="button"
                className="b23-btn b23-export"
                data-testid="export-ranking"
                disabled={disabled || busy}
                onClick={() => void run()}
            >
                <svg className="b23-ic" aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M12 15V3" />
                    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                    <path d="m7 10 5 5 5-5" />
                </svg>
                <span>Exportar planilha</span>
            </button>
            <span className="b23-export-status" role="status" aria-live="polite" data-testid="export-ranking-status">
                {status}
            </span>
        </>
    )
}
