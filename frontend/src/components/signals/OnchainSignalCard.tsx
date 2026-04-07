import { ArrowDownRight, ArrowUpRight, ChevronDown, Clock3, Pause } from 'lucide-react'

import { Badge } from '@/components/ui/Badge'
import { Card, CardContent } from '@/components/ui/Card'
import { cn } from '@/lib/utils'
import { ConfidenceGauge } from './ConfidenceGauge'

export type OnchainSignal = {
  token: string
  chain: string
  signal: 'BUY' | 'SELL' | 'HOLD'
  confidence: number
  breakdown: {
    tvl: number
    active_addresses: number
    exchange_flow: number
    github_commits: number
    github_stars: number
    github_issues: number
  }
  metrics: {
    tvl: number | null
    active_addresses: number | null
    exchange_flow: number | null
    github_commits: number | null
    github_stars: number | null
    github_prs: number | null
    github_issues: number | null
  }
  timestamp: string
}

type OnchainSignalCardProps = {
  signal: OnchainSignal
  sourceLabel?: string
}

const BREAKDOWN_LABELS: Array<{ key: keyof OnchainSignal['breakdown']; label: string }> = [
  { key: 'tvl', label: 'TVL' },
  { key: 'active_addresses', label: 'Enderecos ativos' },
  { key: 'exchange_flow', label: 'Exchange flow' },
  { key: 'github_commits', label: 'Commits GitHub' },
  { key: 'github_stars', label: 'Stars GitHub' },
  { key: 'github_issues', label: 'Issues GitHub' },
]

function signalVariant(signalType: OnchainSignal['signal']) {
  if (signalType === 'BUY') return 'success'
  if (signalType === 'SELL') return 'danger'
  return 'outline'
}

function signalToneClass(signalType: OnchainSignal['signal']) {
  if (signalType === 'BUY') return 'onchain-card--buy'
  if (signalType === 'SELL') return 'onchain-card--sell'
  return 'onchain-card--hold'
}

function signalIcon(signalType: OnchainSignal['signal']) {
  if (signalType === 'BUY') return <ArrowUpRight size={14} />
  if (signalType === 'SELL') return <ArrowDownRight size={14} />
  return <Pause size={14} />
}

function formatTimestamp(value: string) {
  return new Intl.DateTimeFormat('pt-BR', {
    dateStyle: 'short',
    timeStyle: 'short',
  }).format(new Date(value))
}

function formatCompactNumber(value: number | null) {
  if (value === null || !Number.isFinite(value)) return 'Sem dados'
  return new Intl.NumberFormat('pt-BR', {
    notation: 'compact',
    maximumFractionDigits: 1,
  }).format(value)
}

function formatFlow(value: number | null) {
  if (value === null || !Number.isFinite(value)) return 'Sem dados'
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    notation: 'compact',
    maximumFractionDigits: 1,
  }).format(value)
}

function normalizeChain(chain: string) {
  return chain.toLowerCase().trim()
}

function chainLabel(chain: string) {
  const value = normalizeChain(chain)
  if (value === 'matic') return 'Polygon'
  return value.charAt(0).toUpperCase() + value.slice(1)
}

export function OnchainSignalCard({ signal, sourceLabel }: OnchainSignalCardProps) {
  const chain = normalizeChain(signal.chain)

  return (
    <Card className={cn('onchain-card', signalToneClass(signal.signal))}>
      <CardContent className="onchain-card__content">
        <div className="onchain-card__header">
          <div className="onchain-card__identity">
            <div className="onchain-card__badges">
              <Badge variant={signalVariant(signal.signal)} className="onchain-card__signal-badge">
                <span className="onchain-card__badge-icon">{signalIcon(signal.signal)}</span>
                {signal.signal}
              </Badge>
              <Badge variant="secondary" className={`onchain-card__chain-badge onchain-card__chain-badge--${chain}`}>
                {chainLabel(signal.chain)}
              </Badge>
              {sourceLabel ? (
                <Badge variant="outline" className="onchain-card__source-badge">
                  {sourceLabel}
                </Badge>
              ) : null}
            </div>
            <h2 className="onchain-card__token">{signal.token}</h2>
          </div>

          <div className="onchain-card__timestamp">
            <Clock3 size={14} />
            <span>{formatTimestamp(signal.timestamp)}</span>
          </div>
        </div>

        <div className="onchain-card__gauge">
          <ConfidenceGauge value={signal.confidence} />
        </div>

        <div className="onchain-card__metrics">
          <div className="onchain-card__metric">
            <span className="onchain-card__metric-label">TVL</span>
            <strong className="onchain-card__metric-value">{formatFlow(signal.metrics.tvl)}</strong>
          </div>
          <div className="onchain-card__metric">
            <span className="onchain-card__metric-label">Enderecos</span>
            <strong className="onchain-card__metric-value">{formatCompactNumber(signal.metrics.active_addresses)}</strong>
          </div>
          <div className="onchain-card__metric">
            <span className="onchain-card__metric-label">Flow</span>
            <strong className="onchain-card__metric-value">{formatFlow(signal.metrics.exchange_flow)}</strong>
          </div>
          <div className="onchain-card__metric">
            <span className="onchain-card__metric-label">GitHub</span>
            <strong className="onchain-card__metric-value">{formatCompactNumber(signal.metrics.github_commits)}</strong>
          </div>
        </div>

        <details className="onchain-card__details">
          <summary className="onchain-card__summary">
            <span>Drivers do sinal</span>
            <ChevronDown size={16} className="onchain-card__summary-icon" />
          </summary>
          <div className="onchain-card__breakdown">
            {BREAKDOWN_LABELS.map(({ key, label }) => {
              const value = Math.max(0, Math.min(100, signal.breakdown[key] ?? 0))
              return (
                <div key={key} className="onchain-card__breakdown-row">
                  <div className="onchain-card__breakdown-head">
                    <span>{label}</span>
                    <strong>{value.toFixed(1)}%</strong>
                  </div>
                  <div className="onchain-card__breakdown-track" aria-hidden="true">
                    <div className="onchain-card__breakdown-fill" style={{ width: `${value}%` }} />
                  </div>
                </div>
              )
            })}
          </div>
        </details>
      </CardContent>
    </Card>
  )
}

export function OnchainSignalCardSkeleton() {
  return (
    <Card className="onchain-card onchain-card--skeleton">
      <CardContent className="onchain-card__content onchain-card__content--skeleton">
        <div className="onchain-skeleton onchain-skeleton--header" />
        <div className="onchain-skeleton onchain-skeleton--gauge" />
        <div className="onchain-card__metrics">
          <div className="onchain-skeleton onchain-skeleton--metric" />
          <div className="onchain-skeleton onchain-skeleton--metric" />
          <div className="onchain-skeleton onchain-skeleton--metric" />
          <div className="onchain-skeleton onchain-skeleton--metric" />
        </div>
        <div className="onchain-skeleton onchain-skeleton--details" />
      </CardContent>
    </Card>
  )
}
