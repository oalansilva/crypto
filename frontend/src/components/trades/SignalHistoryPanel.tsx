import type { ReactNode } from 'react'
import type { OpportunitySignalHistoryItem } from '@/components/monitor/types'
import {
  formatSignalPrice,
  formatSignalReason,
  formatSignalTimestamp,
  getSignalHistoryLabel,
  getSignalHistoryMarkerStyle,
  sortSignalHistoryNewestFirst,
  type MonitorSyncStatus,
} from '@/lib/signalHistory'

interface SignalHistoryPanelProps {
  history?: OpportunitySignalHistoryItem[] | null
  direction?: string | null
  syncStatus?: MonitorSyncStatus | null
  limit?: number
  testId?: string
  className?: string
}

export function SignalHistoryPanel({
  history,
  direction,
  syncStatus = null,
  limit = 5,
  testId = 'signal-history-panel',
  className = '',
}: SignalHistoryPanelProps) {
  const sorted = sortSignalHistoryNewestFirst(history).slice(0, limit)
  const unavailable = syncStatus === 'timeout' || syncStatus === 'missing' || syncStatus === 'error'
  const empty = !unavailable && sorted.length === 0

  let body: ReactNode
  if (unavailable) {
    body = (
      <p className="text-sm text-[#929aa5]" data-testid={`${testId}-unavailable`}>
        Histórico de sinais do Monitor indisponível no momento. Tente abrir novamente.
      </p>
    )
  } else if (empty) {
    body = (
      <p className="text-sm text-[#929aa5]" data-testid={`${testId}-empty`}>
        Nenhum histórico confirmado de compra/venda para esta estratégia.
      </p>
    )
  } else {
    body = (
      <div className="space-y-2" data-testid={testId}>
        {sorted.map((item, index) => {
          const marker = getSignalHistoryMarkerStyle(item, direction)
          return (
            <div
              key={`${item.timestamp}-${item.type}-${index}`}
              className="flex items-start justify-between gap-3 rounded-md border border-[#2b3139] bg-[#1e2329] px-3 py-2"
              data-testid={`${testId}-item-${index}`}
            >
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <span className="h-2.5 w-2.5 rounded-full" style={{ backgroundColor: marker.color }} />
                  <span className="font-mono text-sm text-[#eaecef]">{getSignalHistoryLabel(item, direction)}</span>
                  <span className="text-xs text-[#929aa5]">{formatSignalReason(item.reason, direction)}</span>
                </div>
                <p className="text-xs text-[#929aa5]">{formatSignalTimestamp(item.timestamp)}</p>
              </div>
              <span className="font-mono text-sm text-[#eaecef]">{formatSignalPrice(item.price)}</span>
            </div>
          )
        })}
      </div>
    )
  }

  return (
    <section className={className} data-testid={`${testId}-section`}>
      <div className="flex items-center justify-between gap-3">
        <p className="text-[10px] font-semibold uppercase tracking-normal text-[#929aa5]">
          Histórico de sinais
        </p>
        <span className="text-[11px] text-[#929aa5]">Últimos do Monitor</span>
      </div>
      <div className="mt-2 rounded-lg border border-[#2b3139] bg-[#0b0e11] p-3">
        {body}
      </div>
    </section>
  )
}
