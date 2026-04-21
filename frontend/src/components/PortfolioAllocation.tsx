import { useMemo } from 'react'
import { useQuery } from '@tanstack/react-query'
import { AlertCircle, RefreshCcw, Wallet } from 'lucide-react'
import { Cell, Pie, PieChart, ResponsiveContainer } from 'recharts'

import { apiUrl } from '@/lib/apiBase'
import { cn } from '@/lib/utils'

type PortfolioKPI = {
  total_usd: number
  btc_value: number
  eth_value: number
  usdt_value: number
  other_usd: number
}

type AllocationKey = 'BTC' | 'ETH' | 'USDT' | 'OTHER'

type AllocationEntry = {
  key: AllocationKey
  label: string
  value: number
  pct: number
  color: string
}

const ALLOCATION_META: Array<{
  key: AllocationKey
  label: string
  color: string
  valueKey: keyof Pick<PortfolioKPI, 'btc_value' | 'eth_value' | 'usdt_value' | 'other_usd'>
}> = [
  { key: 'BTC', label: 'Bitcoin', color: '#F7931A', valueKey: 'btc_value' },
  { key: 'ETH', label: 'Ethereum', color: '#627EEA', valueKey: 'eth_value' },
  { key: 'USDT', label: 'Tether', color: '#26A17B', valueKey: 'usdt_value' },
  { key: 'OTHER', label: 'Other', color: '#484F58', valueKey: 'other_usd' },
]

async function fetchPortfolioKpi(): Promise<PortfolioKPI> {
  const token = localStorage.getItem('auth_access_token')
  const headers: Record<string, string> = {}
  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }
  const response = await fetch(apiUrl('/portfolio/kpi').toString(), { headers })
  const payload = await response.json().catch(() => null)

  if (!response.ok) {
    const detail =
      payload && typeof payload === 'object' && 'detail' in payload && typeof payload.detail === 'string'
        ? payload.detail
        : 'Failed to load portfolio allocation.'

    throw new Error(detail)
  }

  return payload as PortfolioKPI
}

function formatCurrency(value: number | null | undefined) {
  if (value == null || !Number.isFinite(value)) return '$0.00'

  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    maximumFractionDigits: value >= 1000 ? 2 : 4,
  }).format(value)
}

function formatPercent(value: number) {
  return `${value.toFixed(1)}%`
}

function buildAllocationEntries(data?: PortfolioKPI | null) {
  if (!data) return [] satisfies AllocationEntry[]

  const positiveValues = ALLOCATION_META.map((item) => Math.max(0, Number(data[item.valueKey] ?? 0)))
  const positiveSum = positiveValues.reduce((sum, value) => sum + value, 0)
  const safeTotal = Math.max(Number(data.total_usd ?? 0), positiveSum)

  if (!Number.isFinite(safeTotal) || safeTotal <= 0) return [] satisfies AllocationEntry[]

  return ALLOCATION_META.map((item) => {
    const rawValue = Number(data[item.valueKey] ?? 0)
    const value = rawValue > 0 ? rawValue : 0

    return {
      key: item.key,
      label: item.label,
      value,
      pct: safeTotal > 0 ? (value / safeTotal) * 100 : 0,
      color: item.color,
    }
  }).filter((item) => item.value > 0)
}

function LoadingState() {
  return (
    <div className="grid gap-5 lg:grid-cols-[minmax(0,1fr)_280px] lg:items-center">
      <div className="rounded-[28px] border border-white/10 bg-white/[0.03] p-4 sm:p-5">
        <div className="mx-auto aspect-square w-full max-w-[320px] animate-pulse rounded-full border-[18px] border-white/10 bg-white/[0.02]" />
      </div>

      <div className="space-y-3">
        {Array.from({ length: 4 }).map((_, index) => (
          <div key={index} className="animate-pulse rounded-2xl border border-white/10 bg-white/[0.03] p-4">
            <div className="flex items-center gap-3">
              <div className="h-3.5 w-3.5 rounded-full bg-white/10" />
              <div className="h-4 w-24 rounded bg-white/10" />
            </div>
            <div className="mt-3 h-6 w-32 rounded bg-white/10" />
            <div className="mt-2 h-3 w-20 rounded bg-white/5" />
          </div>
        ))}
      </div>
    </div>
  )
}

function EmptyState() {
  return (
    <div className="flex min-h-[320px] flex-col items-center justify-center rounded-[28px] border border-dashed border-white/12 bg-white/[0.02] px-6 py-10 text-center">
      <div className="flex h-14 w-14 items-center justify-center rounded-full border border-white/10 bg-white/[0.04] text-[var(--text-secondary)]">
        <Wallet className="h-6 w-6" />
      </div>
      <h3 className="mt-4 text-lg font-semibold text-[var(--text-primary)]">No portfolio allocation yet</h3>
      <p className="mt-2 max-w-md text-sm text-[var(--text-tertiary)]">
        We could not find any positive BTC, ETH, USDT, or other balances to visualize.
      </p>
    </div>
  )
}

function ErrorState({ message, onRetry, retrying }: { message: string; onRetry: () => void; retrying: boolean }) {
  return (
    <div className="flex min-h-[320px] flex-col items-center justify-center rounded-[28px] border border-rose-400/20 bg-rose-500/[0.06] px-6 py-10 text-center">
      <div className="flex h-14 w-14 items-center justify-center rounded-full border border-rose-400/20 bg-rose-500/10 text-rose-300">
        <AlertCircle className="h-6 w-6" />
      </div>
      <h3 className="mt-4 text-lg font-semibold text-[var(--text-primary)]">Unable to load allocation</h3>
      <p className="mt-2 max-w-md text-sm text-rose-200/90">{message}</p>
      <button
        type="button"
        onClick={onRetry}
        disabled={retrying}
        className="mt-5 inline-flex items-center gap-2 rounded-full border border-white/12 bg-white/[0.05] px-4 py-2 text-sm font-medium text-[var(--text-primary)] hover:border-white/20 hover:bg-white/[0.08] disabled:cursor-not-allowed disabled:opacity-70"
      >
        <RefreshCcw className={cn('h-4 w-4', retrying && 'animate-spin')} />
        {retrying ? 'Retrying...' : 'Try again'}
      </button>
    </div>
  )
}

export default function PortfolioAllocation() {
  const query = useQuery<PortfolioKPI>({
    queryKey: ['portfolio-allocation', 'kpi'],
    queryFn: fetchPortfolioKpi,
    refetchOnWindowFocus: false,
  })

  const entries = useMemo(() => buildAllocationEntries(query.data), [query.data])
  const totalUsd = Math.max(
    Number(query.data?.total_usd ?? 0),
    entries.reduce((sum, entry) => sum + entry.value, 0),
  )
  const hasData = entries.length > 0 && totalUsd > 0

  return (
    <section className="rounded-[28px] border border-white/10 bg-[linear-gradient(180deg,rgba(255,255,255,0.06),rgba(255,255,255,0.02))] p-4 shadow-[0_18px_50px_rgba(0,0,0,0.22)] backdrop-blur sm:p-6">
      <div className="flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <span className="text-[11px] font-semibold uppercase tracking-[0.18em] text-[var(--text-muted)]">
            Portfolio allocation
          </span>
          <h2 className="mt-2 text-xl font-semibold text-[var(--text-primary)] sm:text-2xl">
            Portfolio composition by asset
          </h2>
          <p className="mt-1 text-sm text-[var(--text-tertiary)]">
            Live split from `/portfolio/kpi`, optimized for quick daily review.
          </p>
        </div>

        <div className="rounded-2xl border border-white/10 bg-white/[0.04] px-4 py-3">
          <div className="text-[10px] font-semibold uppercase tracking-[0.16em] text-[var(--text-muted)]">
            Total portfolio
          </div>
          <div className="mt-1 text-lg font-semibold text-[var(--text-primary)]">{formatCurrency(totalUsd)}</div>
        </div>
      </div>

      <div className="mt-6">
        {query.isLoading ? <LoadingState /> : null}

        {!query.isLoading && query.isError ? (
          <ErrorState
            message={query.error instanceof Error ? query.error.message : 'Unexpected error while fetching /portfolio/kpi.'}
            onRetry={() => void query.refetch()}
            retrying={query.isFetching}
          />
        ) : null}

        {!query.isLoading && !query.isError && !hasData ? <EmptyState /> : null}

        {!query.isLoading && !query.isError && hasData ? (
          <div className="grid gap-5 lg:grid-cols-[minmax(0,1fr)_280px] lg:items-center">
            <div className="rounded-[28px] border border-white/10 bg-white/[0.03] p-3 sm:p-4">
              <div className="relative mx-auto h-[320px] w-full min-w-0 max-w-[360px] sm:h-[360px]">
                <ResponsiveContainer width="100%" height="100%" minWidth={0}>
                  <PieChart>
                    <Pie
                      data={entries}
                      dataKey="value"
                      nameKey="key"
                      innerRadius="62%"
                      outerRadius="88%"
                      paddingAngle={2}
                      stroke="rgba(7, 17, 26, 0.9)"
                      strokeWidth={3}
                      isAnimationActive
                    >
                      {entries.map((entry) => (
                        <Cell key={entry.key} fill={entry.color} />
                      ))}
                    </Pie>
                  </PieChart>
                </ResponsiveContainer>

                <div className="pointer-events-none absolute inset-0 flex flex-col items-center justify-center px-8 text-center">
                  <div className="text-[10px] font-semibold uppercase tracking-[0.16em] text-[var(--text-muted)]">
                    Total USD
                  </div>
                  <div className="mt-2 text-xl font-semibold text-[var(--text-primary)] sm:text-2xl">
                    {formatCurrency(totalUsd)}
                  </div>
                  <div className="mt-1 text-xs text-[var(--text-tertiary)]">
                    {entries.length} {entries.length === 1 ? 'asset' : 'assets'} allocated
                  </div>
                </div>
              </div>
            </div>

            <div className="space-y-3">
              {entries.map((entry) => (
                <div
                  key={entry.key}
                  className="rounded-2xl border border-white/10 bg-white/[0.03] px-4 py-3.5 shadow-[inset_0_1px_0_rgba(255,255,255,0.02)]"
                >
                  <div className="flex items-center justify-between gap-3">
                    <div className="flex min-w-0 items-center gap-3">
                      <span className="h-3 w-3 shrink-0 rounded-full" style={{ backgroundColor: entry.color }} />
                      <div className="min-w-0">
                        <div className="text-sm font-semibold text-[var(--text-primary)]">{entry.key}</div>
                        <div className="truncate text-xs text-[var(--text-tertiary)]">{entry.label}</div>
                      </div>
                    </div>

                    <div className="text-right">
                      <div className="text-sm font-semibold text-[var(--text-primary)]">{formatPercent(entry.pct)}</div>
                      <div className="text-xs text-[var(--text-tertiary)]">{formatCurrency(entry.value)}</div>
                    </div>
                  </div>

                  <div className="mt-3 h-2 overflow-hidden rounded-full bg-white/[0.05]">
                    <div
                      className="h-full rounded-full"
                      style={{ width: `${Math.min(entry.pct, 100)}%`, backgroundColor: entry.color }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>
        ) : null}
      </div>

      <div className="mt-6 flex items-center justify-between gap-3 border-t border-white/10 pt-4 text-sm">
        <span className="text-[var(--text-tertiary)]">Portfolio total</span>
        <span className="font-semibold text-[var(--text-primary)]">{formatCurrency(totalUsd)}</span>
      </div>
    </section>
  )
}
