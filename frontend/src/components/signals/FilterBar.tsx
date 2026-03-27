import { SlidersHorizontal } from 'lucide-react'

import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import type { SignalFilterType } from '@/types/signals'

type FilterBarProps = {
  signalType: SignalFilterType
  asset: string
  confidenceMin: number
  assets: string[]
  onTypeChange: (value: SignalFilterType) => void
  onAssetChange: (value: string) => void
  onConfidenceChange: (value: number) => void
  onClear: () => void
}

export function FilterBar({
  signalType,
  asset,
  confidenceMin,
  assets,
  onTypeChange,
  onAssetChange,
  onConfidenceChange,
  onClear,
}: FilterBarProps) {
  return (
    <div className="page-card-muted p-4">
      <div className="flex items-center justify-between gap-3">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[var(--text-muted)]">Filtros</p>
          <p className="text-sm text-[var(--text-secondary)]">Tipo, ativo e confidence mínima.</p>
        </div>
        <Button variant="ghost" size="sm" onClick={onClear} className="whitespace-nowrap">
          Limpar filtros
        </Button>
      </div>

      <div className="mt-4 grid grid-cols-1 gap-4 lg:grid-cols-[1fr_1fr_minmax(220px,1.4fr)]">
        <label className="block">
          <span className="mb-2 block text-xs font-semibold uppercase tracking-[0.16em] text-[var(--text-muted)]">Tipo</span>
          <div className="relative">
            <select
              value={signalType}
              onChange={(event) => onTypeChange(event.target.value as SignalFilterType)}
              className="input pr-10"
            >
              <option value="ALL">Todos</option>
              <option value="BUY">BUY</option>
              <option value="SELL">SELL</option>
              <option value="HOLD">HOLD</option>
            </select>
            <SlidersHorizontal className="pointer-events-none absolute right-4 top-1/2 h-4 w-4 -translate-y-1/2 text-[var(--text-muted)]" />
          </div>
        </label>

        <label className="block">
          <span className="mb-2 block text-xs font-semibold uppercase tracking-[0.16em] text-[var(--text-muted)]">Ativo</span>
          <select value={asset} onChange={(event) => onAssetChange(event.target.value)} className="input">
            <option value="ALL">Todos</option>
            {assets.map((item) => (
              <option key={item} value={item}>
                {item}
              </option>
            ))}
          </select>
        </label>

        <div className="grid grid-cols-[1fr_110px] gap-3">
          <label className="block">
            <span className="mb-2 block text-xs font-semibold uppercase tracking-[0.16em] text-[var(--text-muted)]">Confidence mínima</span>
            <input
              type="range"
              min={0}
              max={100}
              value={confidenceMin}
              onChange={(event) => onConfidenceChange(Number(event.target.value))}
              className="mt-3 w-full accent-emerald-400"
            />
            <div className="mt-2 text-xs text-[var(--text-tertiary)]">Threshold atual: {confidenceMin}%</div>
          </label>
          <Input
            type="number"
            min={0}
            max={100}
            value={confidenceMin}
            onChange={(event) => onConfidenceChange(Number(event.target.value))}
            label="Valor"
          />
        </div>
      </div>
    </div>
  )
}
