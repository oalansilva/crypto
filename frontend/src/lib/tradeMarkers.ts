import type { StrategyChartMarker } from '../components/charts/StrategyChartSurface'

export interface TradeMarkerTrade {
    entry_time?: string | number | null
    entry_price?: number | null
    exit_time?: string | number | null
    exit_price?: number | null
    profit?: number | null
}

export interface BuildTradeMarkersOptions {
    direction?: string | null
    timeframe?: string | null
}

const TIMEFRAME_MS: Record<string, number> = {
    '1m': 60_000,
    '5m': 5 * 60_000,
    '15m': 15 * 60_000,
    '30m': 30 * 60_000,
    '1h': 60 * 60_000,
    '4h': 4 * 60 * 60_000,
    '1d': 24 * 60 * 60_000,
}

function parseTime(value?: string | number | null): number | null {
    if (value === null || value === undefined || value === '') return null
    if (typeof value === 'number') {
        const milliseconds = value > 10_000_000_000 ? value : value * 1000
        return Number.isFinite(milliseconds) ? milliseconds : null
    }
    const parsed = Date.parse(String(value))
    return Number.isFinite(parsed) ? parsed : null
}

function displayedCandleKey(value?: string | number | null, timeframe?: string | null): string {
    const parsed = parseTime(value)
    if (parsed === null) return ''
    const normalizedTimeframe = String(timeframe || '').trim().toLowerCase()
    const interval = TIMEFRAME_MS[normalizedTimeframe]
    if (!interval) return String(Math.floor(parsed / 1000))
    return String(Math.floor(parsed / interval))
}

function formatProfit(profit?: number | null): string {
    const value = Number(profit)
    return Number.isFinite(value) ? ` (${(value * 100).toFixed(2)}%)` : ''
}

function isSameDisplayedCandle(
    entryTime?: string | number | null,
    exitTime?: string | number | null,
    timeframe?: string | null,
): boolean {
    const entryKey = displayedCandleKey(entryTime, timeframe)
    const exitKey = displayedCandleKey(exitTime, timeframe)
    return entryKey !== '' && entryKey === exitKey
}

export function buildTradeMarkers(
    trades: TradeMarkerTrade[] | undefined | null,
    options: BuildTradeMarkersOptions = {},
): StrategyChartMarker[] {
    const isShort = String(options.direction || 'long').toLowerCase() === 'short'
    const timeframe = options.timeframe

    return (trades || []).flatMap((trade) => {
        const entryTime = trade.entry_time
        const exitTime = trade.exit_time
        if (!entryTime) return []

        const entryLabel = isShort ? 'VENDA' : 'COMPRA'
        const exitLabel = isShort ? 'COMPRA' : 'VENDA'
        const entryMarker: StrategyChartMarker = {
            time: entryTime,
            position: isShort ? 'aboveBar' : 'belowBar',
            color: isShort ? '#f97316' : '#10b981',
            shape: isShort ? 'arrowDown' : 'arrowUp',
            text: entryLabel,
        }

        if (!exitTime) {
            return [entryMarker]
        }

        if (isSameDisplayedCandle(entryTime, exitTime, timeframe)) {
            return [{
                time: entryTime,
                position: 'aboveBar',
                color: '#fcd535',
                shape: 'circle',
                text: `${entryLabel}/${exitLabel}${formatProfit(trade.profit)}`,
            }]
        }

        return [
            entryMarker,
            {
                time: exitTime,
                position: isShort ? 'belowBar' : 'aboveBar',
                color: isShort ? '#10b981' : '#ef4444',
                shape: isShort ? 'arrowUp' : 'arrowDown',
                text: `${exitLabel}${formatProfit(trade.profit)}`,
            },
        ]
    })
}
