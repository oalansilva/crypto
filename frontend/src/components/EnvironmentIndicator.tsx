import { getRuntimeEnvironment } from '@/lib/environment'

interface EnvironmentIndicatorProps {
  compact?: boolean
  className?: string
}

export function EnvironmentIndicator({ compact = false, className = '' }: EnvironmentIndicatorProps) {
  const environment = getRuntimeEnvironment()
  const isDevelopment = environment.kind === 'development'

  const toneClasses = isDevelopment
    ? 'border-[rgba(252,213,53,0.46)] bg-[rgba(252,213,53,0.12)] text-[var(--accent-primary)]'
    : 'border-[rgba(14,203,129,0.34)] bg-[rgba(14,203,129,0.1)] text-[var(--accent-success)]'
  const dotClasses = isDevelopment ? 'bg-[var(--accent-primary)]' : 'bg-[var(--accent-success)]'

  return (
    <div
      data-testid="environment-indicator"
      data-environment={environment.kind}
      title={environment.caption}
      aria-label={environment.caption}
      className={[
        'inline-flex h-9 shrink-0 items-center gap-2 rounded-lg border px-3 text-[11px] font-semibold uppercase tracking-[0.14em] shadow-[var(--shadow-sm)]',
        toneClasses,
        compact ? 'min-w-[72px] justify-center px-2' : 'min-w-[132px]',
        className,
      ].join(' ')}
    >
      <span className={['h-2 w-2 shrink-0 rounded-full', dotClasses].join(' ')} aria-hidden="true" />
      {!compact && <span className="text-[var(--text-muted)]">Ambiente</span>}
      <span>{environment.label}</span>
    </div>
  )
}
