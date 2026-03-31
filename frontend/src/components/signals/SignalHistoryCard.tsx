import { useEffect } from 'react'
import { X } from 'lucide-react'
import type { SignalHistoryItem } from '@/types/signals'

interface SignalHistoryCardProps {
  signal: SignalHistoryItem | null
  onClose: () => void
}

function formatPrice(value: number | null | undefined): string {
  if (value == null) return '—'
  const absValue = Math.abs(value)
  let maximumFractionDigits = 2

  if (absValue < 1000) maximumFractionDigits = 4
  if (absValue < 1) maximumFractionDigits = 6
  if (absValue < 0.01) maximumFractionDigits = 8

  return new Intl.NumberFormat('en-US', {
    minimumFractionDigits: 0,
    maximumFractionDigits,
  }).format(value)
}

function formatDate(value: string | null | undefined): string {
  if (!value) return '—'
  return new Intl.DateTimeFormat('pt-BR', {
    dateStyle: 'short',
    timeStyle: 'short',
  }).format(new Date(value))
}

function formatDateFull(value: string | null | undefined): string {
  if (!value) return '—'
  return new Intl.DateTimeFormat('pt-BR', {
    dateStyle: 'medium',
    timeStyle: 'short',
  }).format(new Date(value))
}

function getDisplayStatus(status: string): 'open' | 'closed' {
  return status === 'ativo' ? 'open' : 'closed'
}

export function SignalHistoryCard({ signal, onClose }: SignalHistoryCardProps) {
  // Close on ESC
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose()
    }
    window.addEventListener('keydown', handler)
    return () => window.removeEventListener('keydown', handler)
  }, [onClose])

  if (!signal) return null
  const displayStatus = getDisplayStatus(signal.status)

  const pnlValue = signal.pnl
  const pnlPercent =
    signal.entry_price && signal.exit_price && signal.type === 'BUY'
      ? (((signal.exit_price - signal.entry_price) / signal.entry_price) * 100).toFixed(2)
      : signal.type === 'SELL' && signal.entry_price && signal.exit_price
        ? (((signal.entry_price - signal.exit_price) / signal.entry_price) * 100).toFixed(2)
        : null

  const isPnlPositive = pnlValue !== null && pnlValue > 0
  const isPnlNegative = pnlValue !== null && pnlValue < 0

  return (
    <>
      {/* Overlay */}
      <div
        className="fixed inset-0 z-[99] bg-[rgba(7,17,26,0.7)] backdrop-blur-sm"
        onClick={onClose}
      />

      {/* Drawer */}
      <aside className="fixed inset-y-0 right-0 z-[100] w-[min(100vw,480px)] border-l border-white/8 bg-[#101c2a] shadow-2xl">
        {/* Header */}
        <div className="sticky top-0 z-10 flex items-center justify-between border-b border-white/8 bg-[#101c2a] px-5 py-4">
          <div>
            <h3 className="font-bold text-[var(--text-primary)]">
              {signal.asset} — {signal.type}
            </h3>
            <p className="mt-0.5 text-xs text-[var(--text-muted)]">
              {formatDateFull(signal.created_at)}
            </p>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="inline-flex h-9 w-9 items-center justify-center rounded-xl border border-white/10 bg-white/[0.04] text-[var(--text-secondary)] hover:border-white/20 hover:bg-white/[0.08] hover:text-white transition-all"
          >
            <X className="h-4 w-4" />
          </button>
        </div>

        {/* Body */}
        <div className="overflow-y-auto p-5" style={{ maxHeight: 'calc(100vh - 73px)' }}>
          {/* Status */}
          <div className="mb-6">
            <div className="mb-2 text-[11px] font-semibold uppercase tracking-[0.16em] text-[var(--text-muted)]">
              Status
            </div>
            <span
              className={[
                'inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-[10px] font-semibold uppercase tracking-wide',
                displayStatus === 'open'
                  ? 'bg-sky-500/12 text-sky-300 border border-sky-400/25'
                  : 'bg-emerald-500/12 text-emerald-300 border border-emerald-400/25',
              ].join(' ')}
            >
              <span className="h-1.5 w-1.5 rounded-full bg-current" />
              {displayStatus === 'open' ? 'Aberto' : 'Fechado'}
            </span>
          </div>

          {/* Key Metrics */}
          <div className="mb-6">
            <div className="mb-3 text-[11px] font-semibold uppercase tracking-[0.16em] text-[var(--text-muted)]">
              Métricas
            </div>
            <div className="grid grid-cols-2 gap-3">
              {[
                { label: 'Confiança', value: `${signal.confidence}%`, valueClass: 'text-emerald-300' },
                { label: 'Target', value: formatPrice(signal.target_price), valueClass: 'text-emerald-300' },
                { label: 'Stop Loss', value: formatPrice(signal.stop_loss), valueClass: 'text-red-300' },
                { label: 'Preço no Trigger', value: formatPrice(signal.trigger_price), valueClass: '' },
              ].map((item) => (
                <div
                  key={item.label}
                  className="rounded-xl border border-white/8 bg-white/[0.02] p-3"
                >
                  <div className="text-[10px] uppercase tracking-[0.14em] text-[var(--text-muted)]">
                    {item.label}
                  </div>
                  <div className={['mt-1 text-sm font-semibold', item.valueClass || 'text-[var(--text-primary)]'].join(' ')}>
                    {item.value}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* PnL Section */}
          <div className="mb-6">
            <div className="mb-3 text-[11px] font-semibold uppercase tracking-[0.16em] text-[var(--text-muted)]">
              PnL
            </div>
            <div className="grid grid-cols-2 gap-3">
              {[
                {
                  label: 'Valor',
                  value: pnlValue !== null ? `${pnlValue >= 0 ? '+' : ''}${pnlValue.toFixed(6)}` : '—',
                  valueClass: isPnlPositive ? 'text-emerald-300' : isPnlNegative ? 'text-red-300' : 'text-[var(--text-muted)]',
                },
                {
                  label: '%',
                  value: pnlPercent !== null ? `${parseFloat(pnlPercent) >= 0 ? '+' : ''}${pnlPercent}%` : '—',
                  valueClass: parseFloat(pnlPercent || '0') >= 0 ? 'text-emerald-300' : 'text-red-300',
                },
                {
                  label: 'Preço Saída',
                  value: formatPrice(signal.exit_price),
                  valueClass: '',
                },
                {
                  label: 'Entrada',
                  value: formatPrice(signal.entry_price),
                  valueClass: '',
                },
                {
                  label: 'Quantidade',
                  value: signal.quantity != null ? signal.quantity.toString() : '—',
                  valueClass: '',
                },
              ].map((item) => (
                <div
                  key={item.label}
                  className="rounded-xl border border-white/8 bg-white/[0.02] p-3"
                >
                  <div className="text-[10px] uppercase tracking-[0.14em] text-[var(--text-muted)]">
                    {item.label}
                  </div>
                  <div className={['mt-1 text-sm font-semibold', item.valueClass || 'text-[var(--text-primary)]'].join(' ')}>
                    {item.value}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Indicators Snapshot */}
          {signal.indicators && (
            <div className="mb-6">
              <div className="mb-3 text-[11px] font-semibold uppercase tracking-[0.16em] text-[var(--text-muted)]">
                Indicadores (snapshot)
              </div>
              <div className="grid grid-cols-3 gap-2">
                {[
                  { label: 'RSI', value: signal.indicators.RSI?.toFixed(1) || '—' },
                  { label: 'MACD', value: signal.indicators.MACD || '—' },
                  {
                    label: 'BB Lower',
                    value: signal.indicators.BollingerBands?.lower
                      ? formatPrice(signal.indicators.BollingerBands.lower)
                      : '—',
                  },
                  {
                    label: 'BB Upper',
                    value: signal.indicators.BollingerBands?.upper
                      ? formatPrice(signal.indicators.BollingerBands.upper)
                      : '—',
                  },
                  {
                    label: 'BB Middle',
                    value: signal.indicators.BollingerBands?.middle
                      ? formatPrice(signal.indicators.BollingerBands.middle)
                      : '—',
                  },
                  {
                    label: 'Perfil',
                    value: signal.risk_profile,
                  },
                ].map((chip) => (
                  <div
                    key={chip.label}
                    className="rounded-xl border border-white/8 bg-white/[0.02] p-2.5 text-center"
                  >
                    <div className="text-[10px] uppercase tracking-[0.12em] text-[var(--text-muted)]">
                      {chip.label}
                    </div>
                    <div className="mt-1 text-[13px] font-semibold text-[var(--text-primary)]">
                      {chip.value}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Timeline */}
          <div>
            <div className="mb-3 text-[11px] font-semibold uppercase tracking-[0.16em] text-[var(--text-muted)]">
              Timeline
            </div>
            <div className="relative pl-5">
              {/* Vertical line */}
              <div className="absolute left-[7px] top-1 bottom-1 w-px bg-white/12" />

              {/* Signal created */}
              <div className="relative pb-4">
                <div className="absolute -left-[18px] top-[5px] h-2.5 w-2.5 rounded-full border-2 border-[var(--accent-primary)] bg-[#101c2a]" />
                <div className="text-[11px] text-[var(--text-muted)]">
                  {formatDateFull(signal.created_at)}
                </div>
                <div className="mt-0.5 text-sm font-medium text-[var(--text-primary)]">
                  Sinal criado com confiança {signal.confidence}%
                </div>
              </div>

              {/* Trigger (if applicable) */}
              {displayStatus === 'closed' && signal.trigger_price && (
                <div className="relative pb-4">
                  <div className="absolute -left-[18px] top-[5px] h-2.5 w-2.5 rounded-full border-2 border-emerald-400 bg-[#101c2a]" />
                  <div className="text-[11px] text-[var(--text-muted)]">
                    {signal.updated_at ? formatDateFull(signal.updated_at) : '—'}
                  </div>
                  <div className="mt-0.5 text-sm font-medium text-emerald-300">
                    Sinal passou para fechado
                  </div>
                  {signal.trigger_price && (
                    <div className="mt-0.5 text-xs text-[var(--text-tertiary)]">
                      Preço no trigger: {formatPrice(signal.trigger_price)}
                    </div>
                  )}
                </div>
              )}

              {/* Closed positions */}
              {signal.exit_price && (
                <div className="relative">
                  <div className="absolute -left-[18px] top-[5px] h-2.5 w-2.5 rounded-full border-2 border-sky-400 bg-[#101c2a]" />
                  <div className="text-[11px] text-[var(--text-muted)]">
                    {signal.updated_at ? formatDateFull(signal.updated_at) : '—'}
                  </div>
                  <div className="mt-0.5 text-sm font-medium text-[var(--text-primary)]">
                    Posição fechada
                  </div>
                  {signal.exit_price && (
                    <div className="mt-0.5 text-xs text-[var(--text-tertiary)]">
                      Preço saída: {formatPrice(signal.exit_price)}
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      </aside>
    </>
  )
}
