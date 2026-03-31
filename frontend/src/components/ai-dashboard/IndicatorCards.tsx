import { Activity, CandlestickChart, Waves } from 'lucide-react'
import { Badge } from '@/components/ui/Badge'
import { Card, CardContent } from '@/components/ui/Card'
import type { AIDashboardIndicator } from './AIDashboard'

function indicatorIcon(id: string) {
  switch (id) {
    case 'rsi':
      return Activity
    case 'macd':
      return CandlestickChart
    default:
      return Waves
  }
}

function toneVariant(tone: string) {
  switch (tone) {
    case 'bullish':
      return 'success' as const
    case 'danger':
    case 'bearish':
      return 'danger' as const
    case 'warning':
      return 'warning' as const
    case 'neutral':
      return 'secondary' as const
    default:
      return 'outline' as const
  }
}

export function IndicatorCards({ indicators }: { indicators: AIDashboardIndicator[] }) {
  if (indicators.length === 0) {
    return (
      <Card className="page-card border-white/8 bg-[linear-gradient(180deg,rgba(16,28,42,0.98),rgba(12,22,34,0.94))]">
        <CardContent className="p-6">
          <div className="text-xs font-semibold uppercase tracking-[0.16em] text-[var(--text-muted)]">Indicadores</div>
          <h2 className="mt-2 text-xl font-semibold text-[var(--text-primary)]">Sem leitura técnica ainda</h2>
          <p className="mt-3 text-sm text-[var(--text-secondary)]">
            A dashboard só exibe cards quando esta conta já possui sinais com indicadores salvos no histórico.
          </p>
        </CardContent>
      </Card>
    )
  }

  return (
    <div className="grid gap-6 lg:grid-cols-3">
      {indicators.map((indicator) => {
        const Icon = indicatorIcon(indicator.id)

        return (
          <Card key={indicator.id} className="page-card border-white/8 bg-[linear-gradient(180deg,rgba(16,28,42,0.98),rgba(12,22,34,0.94))]">
            <CardContent className="p-5">
              <div className="flex items-start justify-between gap-3">
                <div>
                  <div className="text-xs font-semibold uppercase tracking-[0.16em] text-[var(--text-muted)]">Indicador</div>
                  <h3 className="mt-2 text-lg font-semibold text-[var(--text-primary)]">{indicator.title}</h3>
                  <p className="mt-1 text-sm text-[var(--text-secondary)]">{indicator.subtitle}</p>
                </div>
                <div className="flex h-11 w-11 items-center justify-center rounded-2xl border border-white/10 bg-white/[0.04]">
                  <Icon className="h-5 w-5 text-sky-200" />
                </div>
              </div>

              <div className="mt-5 space-y-3">
                {indicator.readings.map((reading) => (
                  <div key={`${indicator.id}-${reading.asset}`} className="page-card-muted flex items-center justify-between gap-3 px-4 py-3">
                    <div>
                      <div className="text-sm font-semibold text-[var(--text-primary)]">{reading.asset}</div>
                      <div className="mt-1 text-xs uppercase tracking-[0.14em] text-[var(--text-muted)]">{reading.value}</div>
                    </div>
                    <Badge variant={toneVariant(reading.tone)}>{reading.status}</Badge>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )
      })}
    </div>
  )
}
