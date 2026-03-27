import { cn } from '@/lib/utils'

type ConfidenceGaugeProps = {
  value: number
  threshold?: number
}

function resolveTone(value: number) {
  if (value >= 70) return 'bg-emerald-400 shadow-[0_0_20px_rgba(16,185,129,0.35)]'
  if (value >= 50) return 'bg-amber-400 shadow-[0_0_20px_rgba(245,158,11,0.28)]'
  return 'bg-red-400 shadow-[0_0_20px_rgba(239,68,68,0.25)]'
}

export function ConfidenceGauge({ value, threshold = 70 }: ConfidenceGaugeProps) {
  const normalized = Math.max(0, Math.min(100, Math.round(value)))

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between text-[11px] font-semibold uppercase tracking-[0.16em] text-[var(--text-muted)]">
        <span>Confidence</span>
        <span>{normalized}%</span>
      </div>
      <div className="relative h-3 overflow-hidden rounded-full bg-white/8">
        <div
          className={cn('h-full rounded-full transition-[width] duration-500 ease-out', resolveTone(normalized))}
          style={{ width: `${normalized}%` }}
        />
        <div
          className="absolute inset-y-0 w-px bg-white/70"
          style={{ left: `${threshold}%` }}
          aria-hidden="true"
        />
      </div>
      <div className="flex items-center justify-between text-[11px] text-[var(--text-muted)]">
        <span>0%</span>
        <span>Limiar {threshold}%</span>
        <span>100%</span>
      </div>
    </div>
  )
}
