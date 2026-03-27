import { Shield, ShieldAlert, ShieldCheck } from 'lucide-react'

import { cn } from '@/lib/utils'
import type { RiskProfile } from '@/types/signals'

type RiskProfileSelectorProps = {
  value: RiskProfile
  onChange: (value: RiskProfile) => void
}

const OPTIONS: Array<{ value: RiskProfile; label: string; icon: typeof Shield }> = [
  { value: 'conservative', label: 'Conservative', icon: ShieldCheck },
  { value: 'moderate', label: 'Moderate', icon: Shield },
  { value: 'aggressive', label: 'Aggressive', icon: ShieldAlert },
]

export function RiskProfileSelector({ value, onChange }: RiskProfileSelectorProps) {
  return (
    <div className="page-card-muted p-2">
      <div className="flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[var(--text-muted)]">Risk profile</p>
          <p className="text-sm text-[var(--text-secondary)]">Selecione a estratégia de exposição para os sinais.</p>
        </div>
        <div className="grid grid-cols-1 gap-2 sm:grid-cols-3">
          {OPTIONS.map(({ value: option, label, icon: Icon }) => {
            const active = value === option
            return (
              <button
                key={option}
                type="button"
                onClick={() => onChange(option)}
                className={cn(
                  'inline-flex items-center justify-center gap-2 rounded-2xl border px-4 py-3 text-sm font-semibold transition-all duration-200',
                  active
                    ? 'border-emerald-300/30 bg-emerald-400/12 text-emerald-100 shadow-[0_12px_28px_rgba(16,185,129,0.16)]'
                    : 'border-white/8 bg-white/[0.03] text-[var(--text-secondary)] hover:border-white/15 hover:text-white',
                )}
              >
                <Icon className="h-4 w-4" />
                {label}
              </button>
            )
          })}
        </div>
      </div>
    </div>
  )
}
