import { Badge } from '@/components/ui/Badge'
import { Card, CardContent } from '@/components/ui/Card'
import type { AIDashboardFearGreed } from './AIDashboard'

function gaugeTone(tone: string) {
  switch (tone) {
    case 'bullish':
      return {
        ring: '#34d399',
        variant: 'success' as const,
        label: 'text-emerald-300',
      }
    case 'danger':
    case 'bearish':
      return {
        ring: '#f87171',
        variant: 'danger' as const,
        label: 'text-red-300',
      }
    case 'warning':
      return {
        ring: '#fbbf24',
        variant: 'warning' as const,
        label: 'text-amber-300',
      }
    default:
      return {
        ring: '#38bdf8',
        variant: 'secondary' as const,
        label: 'text-sky-300',
      }
  }
}

export function FearGreedGauge({
  fearGreed,
  sectionErrors,
}: {
  fearGreed: AIDashboardFearGreed
  sectionErrors?: Record<string, string>
}) {
  const styles = gaugeTone(fearGreed.tone)
  const percentage = Math.max(0, Math.min(100, fearGreed.value))
  const angle = (percentage / 100) * 360
  const fallbackMessage = sectionErrors?.fear_greed

  return (
    <Card className="page-card border-white/8 bg-[radial-gradient(circle_at_top,rgba(56,189,248,0.12),transparent_45%),linear-gradient(180deg,rgba(14,24,36,0.95),rgba(10,18,29,0.92))]">
      <CardContent className="flex h-full flex-col p-6">
        <div className="flex items-center justify-between gap-3">
          <div>
            <div className="text-xs font-semibold uppercase tracking-[0.16em] text-[var(--text-muted)]">Fear &amp; Greed</div>
            <h2 className="mt-2 text-xl font-semibold text-[var(--text-primary)]">Radar de sentimento</h2>
          </div>
          <Badge variant={styles.variant}>{fearGreed.label}</Badge>
        </div>

        <div className="mx-auto mt-6 flex w-full max-w-[280px] items-center justify-center">
          <div
            className="relative flex h-56 w-56 items-center justify-center rounded-full"
            style={{
              background: `conic-gradient(${styles.ring} ${angle}deg, rgba(255,255,255,0.08) ${angle}deg 360deg)`,
            }}
          >
            <div className="absolute inset-[16px] rounded-full bg-[radial-gradient(circle_at_top,rgba(56,189,248,0.12),rgba(11,19,28,0.96)_62%)] shadow-[inset_0_1px_0_rgba(255,255,255,0.06)]" />
            <div className="relative z-10 text-center">
              <div className="text-[11px] uppercase tracking-[0.18em] text-[var(--text-muted)]">Index</div>
              <div className="mt-2 text-5xl font-semibold text-[var(--text-primary)]">{fearGreed.value}</div>
              <div className={`mt-2 text-sm font-semibold ${styles.label}`}>{fearGreed.label}</div>
            </div>
          </div>
        </div>

        <div className="mt-6 grid grid-cols-3 gap-3 text-center text-xs">
          <div className="page-card-muted px-3 py-3 text-[var(--text-secondary)]">0<br /><span className="text-[10px] uppercase tracking-[0.16em] text-[var(--text-muted)]">Pânico</span></div>
          <div className="page-card-muted px-3 py-3 text-[var(--text-secondary)]">50<br /><span className="text-[10px] uppercase tracking-[0.16em] text-[var(--text-muted)]">Neutro</span></div>
          <div className="page-card-muted px-3 py-3 text-[var(--text-secondary)]">100<br /><span className="text-[10px] uppercase tracking-[0.16em] text-[var(--text-muted)]">Euforia</span></div>
        </div>

        <p className="mt-5 text-sm leading-6 text-[var(--text-secondary)]">
          Leitura atual em <span className="font-semibold text-[var(--text-primary)]">{fearGreed.value} — {fearGreed.label}</span>, sugerindo um mercado
          {fearGreed.value < 40 ? ' defensivo e mais sensível à volatilidade.' : fearGreed.value > 60 ? ' com apetite a risco acima da média.' : ' em equilíbrio, sem dominância clara entre medo e ganância.'}
        </p>

        {fallbackMessage ? (
          <div className="page-card-muted mt-4 px-4 py-3 text-sm text-amber-200">
            Fallback ativo: {fallbackMessage}
          </div>
        ) : null}
      </CardContent>
    </Card>
  )
}
