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

export function SignalsList({
  signals,
  sectionErrors,
}: {
  signals: AIDashboardSignal[]
  sectionErrors?: Record<string, string>
}) {
  const formatPrice = (value: number | null | undefined) => {
    if (value == null || Number.isNaN(value)) return '—'
    return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 2 }).format(value)
  }

  const signalTestId = (asset: string) => `ai-signal-card-${asset.replace(/[^a-z0-9]+/gi, '-').toLowerCase()}`
  const sourceStatusLabel = (status?: string) => {
    switch ((status || '').toLowerCase()) {
      case 'supporting':
        return 'Confirma'
      case 'conflicting':
        return 'Conflita'
      default:
        return 'Neutro'
    }
  }

  const safeSignals = Array.isArray(signals) ? signals : []

  return (
    <Card className="page-card border-white/8 bg-[linear-gradient(180deg,rgba(16,28,42,0.98),rgba(12,22,34,0.94))]">
      <CardContent className="p-6">
        <div className="flex items-center justify-between gap-3">
          <div>
            <div className="text-xs font-semibold uppercase tracking-[0.16em] text-[var(--text-muted)]">Sinais unificados</div>
            <h2 className="mt-2 text-xl font-semibold text-[var(--text-primary)]">Uma decisão consolidada por ativo</h2>
          </div>
          <div className="flex h-11 w-11 items-center justify-center rounded-2xl border border-white/10 bg-white/[0.04]">
            <Bot className="h-5 w-5 text-sky-200" />
          </div>
        </div>

        <div className="mt-5 space-y-3">
          {safeSignals.length === 0 ? (
            <div className="page-card-muted px-4 py-4 text-sm text-[var(--text-secondary)]">
              {sectionErrors?.signals || 'Nenhum sinal unificado disponível agora.'}
              {sectionErrors?.onchain || sectionErrors?.stats ? (
                <div className="mt-3 space-y-1 text-xs text-[var(--text-muted)]">
                  {sectionErrors?.onchain ? <div>On-chain: {sectionErrors.onchain}</div> : null}
                  {sectionErrors?.stats ? <div>Histórico AI: {sectionErrors.stats}</div> : null}
                </div>
              ) : null}
            </div>
          ) : null}
          {safeSignals.map((signal) => {
            const sourceCount = Number.isFinite(signal.total_sources) ? signal.total_sources : 0
            const strength = Number.isFinite(signal.strength) ? signal.strength : 0
            const sources = Array.isArray(signal.sources) ? signal.sources : []

            return (
            <details key={signal.id} className="page-card-muted group px-4 py-4" data-testid={signalTestId(signal.asset)}>
              <summary className="flex cursor-pointer list-none flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                <div className="space-y-2">
                  <div className="flex flex-wrap items-center gap-2">
                    <div className="text-base font-semibold text-[var(--text-primary)]">{signal.asset}</div>
                    <Badge variant={actionVariant(signal.action)}>{signal.action}</Badge>
                    <Badge variant="outline">{signal.direction || 'Neutro'}</Badge>
                    <Badge variant="outline">{signal.confidence}%</Badge>
                  </div>
                  <p className="text-sm text-[var(--text-secondary)]">{signal.reason}</p>
                </div>

                <div className="grid gap-2 text-xs uppercase tracking-[0.16em] text-[var(--text-muted)] sm:text-right">
                  <div className="flex items-center gap-2 sm:justify-end">
                    <span>Força</span>
                    <ArrowRight className="h-3.5 w-3.5" />
                    <span className="font-semibold text-[var(--text-primary)]">{strength}/{sourceCount}</span>
                  </div>
                  <div className="flex items-center gap-2 sm:justify-end">
                    <span>Preço</span>
                    <ArrowRight className="h-3.5 w-3.5" />
                    <span className="font-semibold text-[var(--text-primary)]">{formatPrice(signal.price)}</span>
                  </div>
                </div>
              </summary>

              <div className="mt-4 space-y-3 border-t border-white/8 pt-4">
                <div className="text-[11px] font-semibold uppercase tracking-[0.16em] text-[var(--text-muted)]">Fontes do sinal</div>
                <div className="flex gap-1.5">
                  {Array.from({ length: Math.max(sourceCount, 3) }).map((_, index) => (
                    <div
                      key={`${signal.id}-strength-${index}`}
                      className={[
                        'h-2 flex-1 rounded-full',
                        index < strength ? 'bg-emerald-400' : 'bg-white/8',
                      ].join(' ')}
                    />
                  ))}
                </div>

                <div className="grid gap-2">
                  {sources.map((source) => (
                    <div key={`${signal.id}-${source.source}`} className="rounded-2xl border border-white/8 bg-black/10 px-3 py-3" data-testid={`${signalTestId(signal.asset)}-source-${source.source.replace(/[^a-z0-9]+/gi, '-').toLowerCase()}`}>
                      <div className="flex flex-wrap items-center gap-2">
                        <div className="text-sm font-semibold text-[var(--text-primary)]">{source.source}</div>
                        <Badge variant={actionVariant(source.action)}>{source.action}</Badge>
                        <Badge variant="outline">{source.confidence}%</Badge>
                        <Badge variant="outline">{source.direction || 'Neutro'}</Badge>
                        <Badge variant="outline">{sourceStatusLabel(source.status)}</Badge>
                        {source.price != null ? <Badge variant="outline">{formatPrice(source.price)}</Badge> : null}
                      </div>
                      {source.reason ? <p className="mt-2 text-sm text-[var(--text-secondary)]">{source.reason}</p> : null}
                    </div>
                  ))}
                </div>
              </div>
            </details>
            )
          })}
        </div>
      </CardContent>
    </Card>
  )
}
