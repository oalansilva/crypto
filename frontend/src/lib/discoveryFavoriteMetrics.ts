const DISCOVERY_ORIGIN_TYPES = new Set(['discovery_sweep', 'discovery'])

type Metrics = Record<string, any> | null | undefined

export function isDiscoveryOrigin(metrics?: Metrics): boolean {
    return DISCOVERY_ORIGIN_TYPES.has(String(metrics?.origin_type || ''))
}

export function getDiscoverySnapshot(metrics?: Metrics): Record<string, any> | null {
    const snapshot = metrics?.metrics_snapshot
    return snapshot && typeof snapshot === 'object' ? snapshot : null
}

function numeric(value: unknown): number | null {
    if (value === null || value === undefined || value === '') return null
    const numberValue = Number(value)
    return Number.isFinite(numberValue) ? numberValue : null
}

function firstPresent(source: Record<string, any>, ...keys: string[]): unknown {
    for (const key of keys) {
        if (source[key] !== undefined && source[key] !== null) return source[key]
    }
    return undefined
}

export function gridMetricsFromSnapshot(
    snapshot?: Record<string, any> | null,
    extras?: Record<string, any> | null,
): Record<string, any> {
    const source = { ...(extras || {}), ...(snapshot || {}) }
    const grid: Record<string, any> = {}

    const sharpe = numeric(firstPresent(source, 'sharpe_ratio', 'sharpe'))
    if (sharpe !== null) grid.sharpe_ratio = sharpe

    const winRate = numeric(firstPresent(source, 'win_rate'))
    if (winRate !== null) grid.win_rate = winRate

    let maxDrawdown = numeric(firstPresent(source, 'max_drawdown'))
    if (maxDrawdown === null) {
        const maxDrawdownPct = numeric(firstPresent(source, 'max_drawdown_pct'))
        if (maxDrawdownPct !== null) {
            maxDrawdown = Math.abs(maxDrawdownPct) > 1 ? maxDrawdownPct / 100 : maxDrawdownPct
        }
    }
    if (maxDrawdown !== null) grid.max_drawdown = maxDrawdown

    const totalReturn = numeric(firstPresent(source, 'total_return'))
    const totalReturnPct = numeric(firstPresent(source, 'total_return_pct'))
    if (totalReturnPct !== null) {
        grid.total_return_pct = totalReturnPct
        grid.total_return = totalReturn !== null ? totalReturn : totalReturnPct / 100
    } else if (totalReturn !== null) {
        grid.total_return = totalReturn
        grid.total_return_pct = totalReturn * 100
    }

    const tradesValue = firstPresent(source, 'total_trades', 'trades_count', 'num_trades')
    const trades = Array.isArray(tradesValue) ? null : numeric(tradesValue)
    if (trades !== null) grid.total_trades = trades

    const profitFactor = numeric(firstPresent(source, 'profit_factor'))
    if (profitFactor !== null) grid.profit_factor = profitFactor

    return grid
}

export function favoriteGridMetrics(metrics?: Metrics): Record<string, any> {
    if (!metrics || typeof metrics !== 'object') return {}
    if (!isDiscoveryOrigin(metrics)) return metrics
    const snapshot = getDiscoverySnapshot(metrics)
    if (!snapshot) return metrics
    return { ...metrics, ...gridMetricsFromSnapshot(snapshot) }
}

export function formatPtBrDate(value?: string | null): string {
    if (!value) return ''
    const iso = String(value).trim()
    const match = iso.match(/^(\d{4})-(\d{2})-(\d{2})/)
    if (match) {
        const [, year, month, day] = match
        return `${day}/${month}/${year}`
    }
    const date = new Date(iso)
    if (Number.isNaN(date.getTime())) return ''
    const day = String(date.getUTCDate()).padStart(2, '0')
    const month = String(date.getUTCMonth() + 1).padStart(2, '0')
    return `${day}/${month}/${date.getUTCFullYear()}`
}

export function discoveryTrainWindowLabel(
    startDate?: string | null,
    endDate?: string | null,
    metrics?: Metrics,
): string {
    const snapshot = getDiscoverySnapshot(metrics)
    const start = startDate
        || metrics?.start_date
        || snapshot?.start_date
        || snapshot?.start_at
        || null
    const end = endDate
        || metrics?.end_date
        || snapshot?.end_date
        || snapshot?.end_at
        || null
    const startLabel = formatPtBrDate(start)
    const endLabel = formatPtBrDate(end)
    const range = startLabel && endLabel
        ? `${startLabel} → ${endLabel}`
        : startLabel || endLabel
    return range
        ? `Resumo · janela de treino da Descoberta · ${range}`
        : 'Resumo · janela de treino da Descoberta'
}

export function currentCandlesTradesLabel(count: number): string {
    return `Lista de operações · velas atuais · ${count} negócios — não é a janela da Descoberta`
}
