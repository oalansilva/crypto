import { ArrowRight, Bot } from 'lucide-react'
import { Badge } from '@/components/ui/Badge'
import { Card, CardContent } from '@/components/ui/Card'
import type { AIDashboardSignal } from './AIDashboard'

function actionVariant(action: string) {
  switch (action.toUpperCase()) {
    case 'BUY':
      return 'success' as const
    case 'SELL':
      return 'danger' as const
    case 'HOLD':
      return 'warning' as const
    default:
      return 'secondary' as const
  }
}

export function SignalsList({ signals }: { signals: AIDashboardSignal[] }) {
  return (
    <Card className="page-card border-white/8 bg-[linear-gradient(180deg,rgba(16,28,42,0.98),rgba(12,22,34,0.94))]">
      <CardContent className="p-6">
        <div className="flex items-center justify-between gap-3">
          <div>
            <div className="text-xs font-semibold uppercase tracking-[0.16em] text-[var(--text-muted)]">Sinais recentes</div>
            <h2 className="mt-2 text-xl font-semibold text-[var(--text-primary)]">Decisões priorizadas</h2>
          </div>
          <div className="flex h-11 w-11 items-center justify-center rounded-2xl border border-white/10 bg-white/[0.04]">
            <Bot className="h-5 w-5 text-sky-200" />
          </div>
        </div>

        <div className="mt-5 space-y-3">
          {signals.map((signal) => (
            <div key={signal.id} className="page-card-muted flex flex-col gap-3 px-4 py-4 sm:flex-row sm:items-center sm:justify-between">
              <div className="space-y-1.5">
                <div className="flex flex-wrap items-center gap-2">
                  <div className="text-base font-semibold text-[var(--text-primary)]">{signal.asset}</div>
                  <Badge variant={actionVariant(signal.action)}>{signal.action}</Badge>
                  <Badge variant="outline">{signal.confidence}%</Badge>
                </div>
                <p className="text-sm text-[var(--text-secondary)]">{signal.reason}</p>
              </div>

              <div className="flex items-center gap-2 text-xs uppercase tracking-[0.16em] text-[var(--text-muted)]">
                <span>Confiança</span>
                <ArrowRight className="h-3.5 w-3.5" />
                <span className="font-semibold text-[var(--text-primary)]">{signal.confidence}%</span>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}
