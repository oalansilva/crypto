import type { SignalStats } from '@/types/signals'

interface SignalStatsProps {
  stats: SignalStats | null
  isLoading: boolean
}

export function SignalStats({ stats, isLoading }: SignalStatsProps) {
  if (isLoading) {
    return (
      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        {[...Array(4)].map((_, i) => (
          <div key={i} className="rounded-2xl border border-white/8 bg-white/[0.03] p-5 animate-pulse">
            <div className="h-3 w-20 rounded-full bg-white/8" />
            <div className="mt-3 h-8 w-16 rounded-full bg-white/8" />
            <div className="mt-2 h-3 w-24 rounded-full bg-white/8" />
          </div>
        ))}
      </div>
    )
  }

  if (!stats || stats.total_signals === 0) {
    return null
  }

  const statCards = [
    {
      label: 'Total de Sinais',
      value: stats.total_signals.toLocaleString('pt-BR'),
      sub: 'últimos 30 dias',
      accent: true,
    },
    {
      label: 'Win Rate',
      value: `${stats.win_rate.toFixed(1)}%`,
      sub: 'sinais disparados com lucro',
      accent: false,
      positive: stats.win_rate > 50,
    },
    {
      label: 'Confiança Média',
      value: `${stats.avg_confidence.toFixed(1)}%`,
      sub: 'média ponderada',
      accent: false,
    },
    {
      label: 'Taxa de Expirados',
      value: `${stats.expired_rate.toFixed(1)}%`,
      sub: 'sinais não disparados',
      accent: false,
      danger: true,
    },
  ]

  return (
    <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
      {statCards.map((card) => (
        <div
          key={card.label}
          className={[
            'rounded-2xl border p-5 transition-all duration-200',
            card.accent
              ? 'border-emerald-400/30 hover:border-emerald-400/50 hover:shadow-[0_0_20px_rgba(16,185,129,0.2)]'
              : card.danger
                ? 'border-red-400/30 hover:border-red-400/50 hover:shadow-[0_0_20px_rgba(239,68,68,0.15)]'
                : 'border-white/8 hover:border-white/15',
          ].join(' ')}
        >
          <div className="text-[11px] font-semibold uppercase tracking-[0.16em] text-[var(--text-muted)]">
            {card.label}
          </div>
          <div
            className={[
              'mt-2 text-2xl font-bold',
              card.positive !== undefined
                ? card.positive
                  ? 'text-emerald-300'
                  : 'text-red-300'
                : 'text-[var(--text-primary)]',
            ].join(' ')}
          >
            {card.value}
          </div>
          <div className="mt-1 text-xs text-[var(--text-tertiary)]">{card.sub}</div>
        </div>
      ))}
    </div>
  )
}
