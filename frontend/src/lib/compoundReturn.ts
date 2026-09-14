export type CompoundReturnSource = {
    total_return?: number | null
    total_return_pct?: number | null
}

function numeric(value: unknown): number | null {
    if (value === null || value === undefined || value === '') return null
    const numberValue = Number(value)
    return Number.isFinite(numberValue) ? numberValue : null
}

/**
 * Compound return in percentage points.
 * `total_return_pct` is already points (98591.56 = +98,591.56%).
 * `total_return` is always a decimal ratio (0.35 = +35%; 985.91 = +98,591%) — never treat |ratio| > 1 as "already %".
 */
export function compoundReturnPoints(source?: CompoundReturnSource | null): number | null {
    if (!source || typeof source !== 'object') return null
    const points = numeric(source.total_return_pct)
    if (points !== null) return points
    const ratio = numeric(source.total_return)
    if (ratio === null) return null
    return ratio * 100
}

export function formatCompoundReturn(
    source?: CompoundReturnSource | null,
    options?: { decimals?: number; empty?: string },
): { text: string; positive: boolean; points: number | null } {
    const decimals = options?.decimals ?? 2
    const empty = options?.empty ?? 'Indisponível'
    const points = compoundReturnPoints(source)
    if (points === null) return { text: empty, positive: true, points: null }
    return {
        text: `${points >= 0 ? '+' : ''}${points.toFixed(decimals)}%`,
        positive: points >= 0,
        points,
    }
}

/** Win rate / max drawdown stay as ratios < 1. |value| > 1 means the payload is already a percent. */
export function formatBoundedRatioPercent(
    value: number | null | undefined,
    decimals = 2,
    empty = 'Indisponível',
): string {
    if (value === undefined || value === null || Number.isNaN(Number(value))) return empty
    const numberValue = Number(value)
    const percentage = Math.abs(numberValue) > 1 ? numberValue : numberValue * 100
    const formatted = percentage.toFixed(decimals).replace(/(\.\d*?)0+$/, '$1').replace(/\.$/, '')
    return `${formatted}%`
}
