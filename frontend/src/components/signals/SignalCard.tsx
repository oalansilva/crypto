import { ArrowDownRight, ArrowUpRight, Pause, ShieldAlert } from 'lucide-react'

import { Badge } from '@/components/ui/Badge'
import { Card, CardContent } from '@/components/ui/Card'
import { cn } from '@/lib/utils'
import type { Signal } from '@/types/signals'
import { ConfidenceGauge } from './ConfidenceGauge'

type SignalCardProps = {
  signal: Signal
}

function badgeVariant(type: Signal['type']) {
  if (type === 'BUY') return 'success'
  if (type === 'SELL') return 'danger'
  return 'outline'
}

function toneClasses(type: Signal['type']) {
  if (type === 'BUY') return 'hover:border-emerald-400/40 hover:shadow-[0_14px_40px_rgba(16,185,129,0.16)]'
  if (type === 'SELL') return 'hover:border-red-400/40 hover:shadow-[0_14px_40px_rgba(239,68,68,0.14)]'
  return 'hover:border-zinc-500/40 hover:shadow-[0_14px_40px_rgba(148,163,184,0.12)]'
}

function signalIcon(type: Signal['type']) {
  if (type === 'BUY') return <ArrowUpRight className="h-4 w-4" />
  if (type === 'SELL') return <ArrowDownRight className="h-4 w-4" />
  return <Pause className="h-4 w-4" />
}

function formatPrice(value: number) {
  return new Intl.NumberFormat('en-US', { maximumFractionDigits: 2 }).format(value)
}

function formatDate(value: string) {
  return new Intl.DateTimeFormat('pt-BR', {
    dateStyle: 'short',
    timeStyle: 'short',
  }).format(new Date(value))
}

export function SignalCard({ signal }: SignalCardProps) {
  return (
    <Card className={cn('border-white/8 bg-[rgba(9,18,28,0.92)] transition-all duration-200', toneClasses(signal.type))}>
      <CardContent className="p-5">
        <div className="flex items-start justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <Badge variant={badgeVariant(signal.type)} className={signal.type === 'HOLD' ? 'border-white/15 bg-white/6 text-zinc-200' : ''}>
                <span className="mr-1 inline-flex">{signalIcon(signal.type)}</span>
                {signal.type}
              </Badge>
              <span className="text-sm font-semibold text-[var(--text-primary)]">{signal.asset}</span>
            </div>
            <p className="mt-3 text-xs uppercase tracking-[0.18em] text-[var(--text-muted)]">Perfil {signal.risk_profile}</p>
          </div>
          <div className="text-right text-xs text-[var(--text-tertiary)]">
            <div>{formatDate(signal.created_at)}</div>
          </div>
        </div>

        <div className="mt-5">
          <ConfidenceGauge value={signal.confidence} />
        </div>

        <div className="mt-5 grid grid-cols-2 gap-3 text-sm">
          <div className="rounded-2xl border border-white/8 bg-white/[0.03] p-3">
            <div className="text-[11px] uppercase tracking-[0.16em] text-[var(--text-muted)]">Target</div>
            <div className="mt-1 font-semibold text-emerald-300">{formatPrice(signal.target_price)}</div>
          </div>
          <div className="rounded-2xl border border-white/8 bg-white/[0.03] p-3">
            <div className="text-[11px] uppercase tracking-[0.16em] text-[var(--text-muted)]">Stop loss</div>
            <div className="mt-1 font-semibold text-red-300">{formatPrice(signal.stop_loss)}</div>
          </div>
        </div>

        <div className="mt-5 grid grid-cols-1 gap-3 text-sm text-[var(--text-secondary)] sm:grid-cols-3">
          <div className="rounded-2xl border border-white/8 bg-white/[0.03] p-3">
            <div className="text-[11px] uppercase tracking-[0.16em] text-[var(--text-muted)]">RSI</div>
            <div className="mt-1 font-semibold">{signal.indicators.RSI.toFixed(1)}</div>
          </div>
          <div className="rounded-2xl border border-white/8 bg-white/[0.03] p-3">
            <div className="text-[11px] uppercase tracking-[0.16em] text-[var(--text-muted)]">MACD</div>
            <div className="mt-1 font-semibold capitalize">{signal.indicators.MACD}</div>
          </div>
          <div className="rounded-2xl border border-white/8 bg-white/[0.03] p-3">
            <div className="flex items-center gap-1 text-[11px] uppercase tracking-[0.16em] text-[var(--text-muted)]">
              <ShieldAlert className="h-3.5 w-3.5" />
              Bollinger
            </div>
            <div className="mt-1 font-semibold text-[13px]">
              {formatPrice(signal.indicators.BollingerBands.lower)} - {formatPrice(signal.indicators.BollingerBands.upper)}
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

export function SignalCardSkeleton() {
  return (
    <Card className="border-white/8 bg-[rgba(9,18,28,0.82)]">
      <CardContent className="space-y-4 p-5 animate-pulse">
        <div className="flex items-center justify-between gap-4">
          <div className="h-6 w-28 rounded-full bg-white/8" />
          <div className="h-4 w-24 rounded-full bg-white/8" />
        </div>
        <div className="h-3 rounded-full bg-white/8" />
        <div className="grid grid-cols-2 gap-3">
          <div className="h-18 rounded-2xl bg-white/8" />
          <div className="h-18 rounded-2xl bg-white/8" />
        </div>
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-3">
          <div className="h-16 rounded-2xl bg-white/8" />
          <div className="h-16 rounded-2xl bg-white/8" />
          <div className="h-16 rounded-2xl bg-white/8" />
        </div>
      </CardContent>
    </Card>
  )
}
