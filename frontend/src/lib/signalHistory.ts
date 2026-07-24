import type { OpportunitySignalHistoryItem } from '../components/monitor/types'
import type { StrategyChartMarker } from '../components/charts/StrategyChartSurface'
import { toStrategyChartTimestamp } from '../components/charts/StrategyChartSurface'

export type MonitorSyncStatus = 'ok' | 'timeout' | 'missing' | 'empty' | 'error'

export function normalizeDirection(value?: string | null): 'long' | 'short' {
  return String(value || 'long').trim().toLowerCase() === 'short' ? 'short' : 'long'
}

export function actionLabelsForDirection(direction?: string | null) {
  const isShort = normalizeDirection(direction) === 'short'
  return {
    entry: isShort ? 'Venda' : 'Compra',
    exit: isShort ? 'Compra' : 'Venda',
    entrySignal: isShort ? 'Vender' : 'Comprar',
    exitRule: isShort ? 'Regra de compra/cobertura' : 'Regra de venda',
  }
}

export function formatSignalReason(value?: string | null, direction?: string | null) {
  const normalized = String(value || '').trim().toLowerCase()
  const labels = actionLabelsForDirection(direction)
  if (!normalized) return '-'
  if (normalized === 'entry') return labels.entry
  if (normalized === 'exit') return labels.exit
  if (normalized === 'exit_logic') return labels.exitRule
  if (normalized === 'stop_loss') return 'Stop loss'
  return normalized.replace(/_/g, ' ')
}

export function getSignalHistoryLabel(item: OpportunitySignalHistoryItem, direction?: string | null) {
  const labels = actionLabelsForDirection(direction)
  return item.type === 'entry' ? labels.entry : labels.exit
}

export function getSignalHistoryMarkerStyle(item: OpportunitySignalHistoryItem, direction?: string | null) {
  const isEntry = item.type === 'entry'
  const isShort = normalizeDirection(direction) === 'short'
  const isStop = !isEntry && String(item.reason || '').trim().toLowerCase() === 'stop_loss'
  const isBuyVisual = (isEntry && !isShort) || (!isEntry && isShort)
  return {
    position: (isBuyVisual ? 'belowBar' : 'aboveBar') as 'belowBar' | 'aboveBar',
    shape: (isBuyVisual ? 'arrowUp' : 'arrowDown') as 'arrowUp' | 'arrowDown',
    color: isStop ? '#f85149' : (isBuyVisual ? '#3fb950' : '#f6465d'),
    text: getSignalHistoryLabel(item, direction),
    signalType: item.type,
  }
}

export function sortSignalHistoryNewestFirst(history: OpportunitySignalHistoryItem[] | null | undefined) {
  return [...(history || [])]
    .filter((item) => item && item.timestamp && (item.type === 'entry' || item.type === 'exit'))
    .sort((left, right) => Date.parse(String(right.timestamp)) - Date.parse(String(left.timestamp)))
}

export function buildSignalHistoryMarkers(
  history: OpportunitySignalHistoryItem[] | null | undefined,
  direction?: string | null,
  candleTimes?: Set<string>,
): StrategyChartMarker[] {
  return sortSignalHistoryNewestFirst(history)
    .slice()
    .reverse()
    .flatMap((item) => {
      const time = toStrategyChartTimestamp(item.timestamp)
      if (time == null) return []
      if (candleTimes && candleTimes.size > 0) {
        const key = new Date(Date.parse(String(item.timestamp))).toISOString()
        const matches = [...candleTimes].some((candleTime) => {
          const candleMs = Date.parse(candleTime)
          const itemMs = Date.parse(String(item.timestamp))
          return Number.isFinite(candleMs) && Number.isFinite(itemMs) && Math.abs(candleMs - itemMs) < 60_000
        })
        // Prefer showing marker when candle set unknown; filter only when we have times and none match by day bucket
        if (!matches) {
          const itemDay = String(item.timestamp).slice(0, 10)
          const dayMatch = [...candleTimes].some((candleTime) => candleTime.slice(0, 10) === itemDay)
          if (!dayMatch) return []
        }
      }
      const style = getSignalHistoryMarkerStyle(item, direction)
      return [{
        time,
        position: style.position,
        shape: style.shape,
        color: style.color,
        text: style.text,
        signalType: style.signalType,
      }]
    })
}

export function formatSignalTimestamp(value?: string | null) {
  if (!value) return '-'
  return new Intl.DateTimeFormat('en-US', {
    month: 'short',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    timeZone: 'UTC',
  }).format(new Date(value))
}

export function formatSignalPrice(value?: number | null) {
  if (value === null || value === undefined || Number.isNaN(value)) return '-'
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 2,
    maximumFractionDigits: 8,
  }).format(value)
}
