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

export type MarkerSignalType = 'entry' | 'exit'

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

export function sameDisplayedCandle(
    left?: string | number | null,
    right?: string | number | null,
    timeframe?: string | null,
): boolean {
    const leftKey = displayedCandleKey(left, timeframe)
    const rightKey = displayedCandleKey(right, timeframe)
    return leftKey !== '' && leftKey === rightKey
}

function formatProfit(profit?: number | null): string {
    const value = Number(profit)
    return Number.isFinite(value) ? ` (${(value * 100).toFixed(2)}%)` : ''
}

function markerAction(marker: StrategyChartMarker): 'COMPRA' | 'VENDA' | null {
    const text = marker.text.toUpperCase()
    if (text.includes('COMPRA')) return 'COMPRA'
    if (text.includes('VENDA')) return 'VENDA'
    return null
}

export function getMarkerSignalType(marker: StrategyChartMarker): MarkerSignalType | null {
    if (marker.signalType === 'entry' || marker.signalType === 'exit') return marker.signalType
    const action = markerAction(marker)
    if (action === 'COMPRA') return 'entry'
    if (action === 'VENDA') return 'exit'
    return null
}

export function getLatestMarkerSignalType(markers: StrategyChartMarker[]): MarkerSignalType | null {
    const latest = [...markers]
        .map((marker, index) => ({ marker, index, type: getMarkerSignalType(marker), timestamp: parseTime(marker.time) }))
        .filter((entry): entry is {
            marker: StrategyChartMarker
            index: number
            type: MarkerSignalType
            timestamp: number
        } => entry.type !== null && entry.timestamp !== null)
        .sort((left, right) => {
            const timeDelta = left.timestamp - right.timestamp
            return timeDelta === 0 ? left.index - right.index : timeDelta
        })
        .at(-1)

    return latest?.type ?? null
}

function markerProfitText(marker: StrategyChartMarker): string {
    return marker.text.match(/\([+-]?\d+(?:\.\d+)?%\)/)?.[0] || ''
}

function markerForAction(group: StrategyChartMarker[], action: 'COMPRA' | 'VENDA'): StrategyChartMarker {
    const selected = group.find((marker) => markerAction(marker) === action) ?? group[0]
    return {
        ...selected,
        text: `${action}${markerProfitText(selected) ? ` ${markerProfitText(selected)}` : ''}`,
    }
}

export function collapseSameCandleOppositeMarkers(
    markers: StrategyChartMarker[],
    timeframe?: string | null,
): StrategyChartMarker[] {
    const groups = new Map<string, { marker: StrategyChartMarker; index: number }[]>()
    const passthrough: { marker: StrategyChartMarker; index: number }[] = []

    markers.forEach((marker, index) => {
        const key = displayedCandleKey(marker.time, timeframe)
        if (!key) {
            passthrough.push({ marker, index })
            return
        }
        groups.set(key, [...(groups.get(key) || []), { marker, index }])
    })

    let lastAction: 'COMPRA' | 'VENDA' | null = null

    return [...passthrough.map((entry) => [entry]), ...Array.from(groups.values())]
        .sort((left, right) => left[0].index - right[0].index)
        .flatMap((entries) => {
            const group = entries.map((entry) => entry.marker)
            const actions = group
                .map(markerAction)
                .filter((action): action is 'COMPRA' | 'VENDA' => action !== null)
            const uniqueActions = actions.filter((action, index) => actions.indexOf(action) === index)

            if (uniqueActions.length < 2) {
                if (uniqueActions[0]) lastAction = uniqueActions[0]
                return group
            }

            const targetAction = lastAction === 'COMPRA'
                ? 'VENDA'
                : lastAction === 'VENDA'
                    ? 'COMPRA'
                    : actions[actions.length - 1]

            lastAction = targetAction
            return [markerForAction(group, targetAction)]
        })
}

export function buildTradeMarkers(
    trades: TradeMarkerTrade[] | undefined | null,
    options: BuildTradeMarkersOptions = {},
): StrategyChartMarker[] {
    const isShort = String(options.direction || 'long').toLowerCase() === 'short'
    const timeframe = options.timeframe

    const markers: StrategyChartMarker[] = (trades || []).flatMap((trade): StrategyChartMarker[] => {
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
            signalType: 'entry',
        }

        if (!exitTime) {
            return [entryMarker]
        }

        return [
            entryMarker,
            {
                time: exitTime,
                position: isShort ? 'belowBar' : 'aboveBar',
                color: isShort ? '#10b981' : '#ef4444',
                shape: isShort ? 'arrowUp' : 'arrowDown',
                text: `${exitLabel}${formatProfit(trade.profit)}`,
                signalType: 'exit',
            },
        ]
    })

    return collapseSameCandleOppositeMarkers(markers, timeframe)
}
