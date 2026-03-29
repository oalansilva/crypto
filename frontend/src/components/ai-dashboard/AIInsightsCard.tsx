import { Brain, Sparkles, TrendingDown, TrendingUp, TriangleAlert } from 'lucide-react'
import { Badge } from '@/components/ui/Badge'
import { Card, CardContent } from '@/components/ui/Card'
import type { AIDashboardInsight } from './AIDashboard'

function toneStyles(tone: string) {
  switch (tone) {
    case 'bullish':
      return {
        badge: 'success' as const,
        icon: TrendingUp,
        iconClass: 'text-emerald-300',
        glow: 'from-emerald-500/14 via-emerald-500/8 to-sky-500/10',
      }
    case 'danger':
    case 'bearish':
      return {
        badge: 'danger' as const,
        icon: TrendingDown,
        iconClass: 'text-red-300',
        glow: 'from-red-500/14 via-red-500/8 to-orange-500/10',
      }
    case 'warning':
      return {
        badge: 'warning' as const,
        icon: TriangleAlert,
        iconClass: 'text-amber-300',
        glow: 'from-amber-500/14 via-amber-500/8 to-orange-500/10',
      }
    default:
      return {
        badge: 'secondary' as const,
        icon: Sparkles,
        iconClass: 'text-sky-200',
        glow: 'from-sky-500/14 via-sky-500/8 to-violet-500/10',
      }
  }
}

export function AIInsightsCard({ insight }: { insight: AIDashboardInsight }) {
  const styles = toneStyles(insight.tone)
  const Icon = styles.icon

  return (
    <Card className={`page-card border-white/8 bg-gradient-to-br ${styles.glow}`}>
      <CardContent className="p-5">
        <div className="flex items-start justify-between gap-4">
          <div className="flex min-w-0 items-start gap-3">
            <div className="flex h-11 w-11 items-center justify-center rounded-2xl border border-white/10 bg-white/[0.04] shadow-[0_14px_28px_rgba(2,8,14,0.22)]">
              <Icon className={`h-5 w-5 ${styles.iconClass}`} />
            </div>
            <div className="min-w-0">
              <div className="flex flex-wrap items-center gap-2">
                <h3 className="text-base font-semibold text-[var(--text-primary)]">{insight.title}</h3>
                {insight.asset ? <Badge variant="outline">{insight.asset}</Badge> : null}
              </div>
              <p className="mt-2 text-sm leading-6 text-[var(--text-secondary)]">{insight.description}</p>
            </div>
          </div>

          <Badge variant={styles.badge}>{insight.badge || 'AI'}</Badge>
        </div>

        <div className="mt-4 flex items-center gap-2 text-xs uppercase tracking-[0.14em] text-[var(--text-muted)]">
          <Brain className="h-3.5 w-3.5" />
          <span>Insight sintetizado por IA</span>
        </div>
      </CardContent>
    </Card>
  )
}
