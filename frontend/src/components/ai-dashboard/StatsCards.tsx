import { Gauge, Radar, Target } from 'lucide-react'
import { Card, CardContent } from '@/components/ui/Card'
import type { AIDashboardStats } from './AIDashboard'

const statConfig = [
  {
    key: 'hit_rate',
    label: 'Hit Rate',
    icon: Target,
    suffix: '%',
  },
  {
    key: 'total_signals',
    label: 'Total',
    icon: Radar,
    suffix: ' sinais',
  },
  {
    key: 'avg_confidence',
    label: 'Confiança Média',
    icon: Gauge,
    suffix: '%',
  },
] as const

export function StatsCards({ stats }: { stats: AIDashboardStats }) {
  const values = {
    hit_rate: stats.hit_rate,
    total_signals: stats.total_signals,
    avg_confidence: stats.avg_confidence,
  }

  const descriptions = {
    hit_rate: 'Efetividade agregada dos sinais',
    total_signals: `${stats.total_signals} sinais monitorados`,
    avg_confidence: 'Nível médio de convicção',
  }

  return (
    <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
      {statConfig.map((item) => {
        const Icon = item.icon
        const value = values[item.key]

        return (
          <Card key={item.key} className="page-card border-white/8 bg-[linear-gradient(180deg,rgba(16,28,42,0.98),rgba(12,22,34,0.94))]">
            <CardContent className="p-5">
              <div className="flex items-start justify-between gap-3">
                <div>
                  <div className="text-xs font-semibold uppercase tracking-[0.16em] text-[var(--text-muted)]">{item.label}</div>
                  <div className="mt-3 text-3xl font-semibold text-[var(--text-primary)]">
                    {value}
                    {item.suffix}
                  </div>
                  <p className="mt-2 text-sm text-[var(--text-secondary)]">{descriptions[item.key]}</p>
                </div>
                <div className="flex h-11 w-11 items-center justify-center rounded-2xl border border-white/10 bg-white/[0.04]">
                  <Icon className="h-5 w-5 text-emerald-200" />
                </div>
              </div>
            </CardContent>
          </Card>
        )
      })}
    </section>
  )
}
