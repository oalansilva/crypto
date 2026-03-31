import { useMemo } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { Activity, ArrowRight, FileText, Kanban, Layers, Settings } from 'lucide-react'
import { apiUrl } from '@/lib/apiBase'
import PortfolioAllocation from '@/components/PortfolioAllocation'
import { useAuth } from '@/stores/authStore'

type HealthState = {
  status?: string
  service?: string
}

type FavoriteStrategy = {
  id: number
  name: string
  symbol: string
  timeframe: string
  strategy_name: string
  metrics?: Record<string, unknown> | null
  created_at: string
}

type BalancesSnapshot = {
  balances?: Array<Record<string, unknown>>
  total_usd?: number | null
  as_of?: string | null
}

type CoordinationChangeItem = {
  id: string
  title?: string | null
  description?: string | null
  card_number?: number | null
  path: string
  status: Record<string, string>
  archived: boolean
  column: string
  position?: number
  item_type?: 'change' | 'bug'
}

type CoordinationChangeListResponse = {
  items: CoordinationChangeItem[]
}

type ChangeDetailResponse = {
  id: string
  project_id: string
  change_id: string
  title: string
  description: string
  status: string
  card_number?: number | null
  created_at: string
  updated_at: string
}

type FocusChange = CoordinationChangeItem & {
  created_at?: string | null
  updated_at?: string | null
}

type LabRunSummary = {
  run_id: string
  status: string
  step?: string | null
  created_at_ms: number
  updated_at_ms: number
  viewer_url: string
}

type LabRunsResponse = {
  runs: LabRunSummary[]
}

type PortfolioKPI = {
  pnl_today_pct: number | null
  pnl_today_vs_btc_pct: number | null
  drawdown_30d_pct: number
  drawdown_peak_date: string | null
  btc_change_24h_pct: number | null
  total_usd: number
  btc_value: number
  usdt_value: number
  eth_value: number
  other_usd: number
  _history_insufficient: boolean
}

type MarketPrice = {
  symbol: string
  price: number
  change_24h_pct: number
}

type MarketPricesResponse = {
  prices: MarketPrice[]
  fetched_at: string | null
}



function cx(...xs: Array<string | false | null | undefined>) {
  return xs.filter(Boolean).join(' ')
}

async function fetchJson<T>(path: string): Promise<T> {
  const token = localStorage.getItem('auth_access_token')
  const headers: Record<string, string> = {}
  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }
  const res = await fetch(apiUrl(path).toString(), { headers })
  const payload = await res.json().catch(() => null)
  if (!res.ok) {
    const detail = payload && typeof payload === 'object' ? (payload as { detail?: string }).detail : undefined
    throw new Error(detail || `Falha ao carregar ${path}`)
  }
  return payload as T
}

function formatDt(value: string | Date) {
  const dt = value instanceof Date ? value : new Date(value)
  if (Number.isNaN(dt.getTime())) return '—'
  return dt.toLocaleString('pt-BR', {
    day: '2-digit',
    month: 'short',
    hour: '2-digit',
    minute: '2-digit',
  })
}

function formatPercent(value: number | null | undefined) {
  if (value == null || !Number.isFinite(value)) return null
  return `${value >= 0 ? '+' : ''}${value.toFixed(1)}%`
}

function formatCurrency(value: number | null | undefined) {
  if (value == null || !Number.isFinite(value)) return '—'
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    maximumFractionDigits: value >= 1000 ? 2 : 4,
  }).format(value)
}

function formatFreshness(value: string | null | undefined) {
  if (!value) return null
  const dt = new Date(value)
  if (Number.isNaN(dt.getTime())) return null
  const diffMs = Date.now() - dt.getTime()
  if (diffMs <= 60_000) return 'agora'
  const diffMinutes = Math.round(diffMs / 60_000)
  if (diffMinutes < 60) return `há ${diffMinutes} min`
  const diffHours = Math.round(diffMinutes / 60)
  if (diffHours < 24) return `há ${diffHours} h`
  const diffDays = Math.round(diffHours / 24)
  return `há ${diffDays} d`
}

function getReturnPct(metrics: Record<string, unknown> | null | undefined) {
  if (!metrics) return null
  const totalReturnPct = metrics.total_return_pct
  if (typeof totalReturnPct === 'number' && Number.isFinite(totalReturnPct)) return totalReturnPct
  const totalReturn = metrics.total_return
  if (typeof totalReturn === 'number' && Number.isFinite(totalReturn)) return totalReturn * 100
  return null
}

function getBestFavorite(favorites: FavoriteStrategy[]) {
  if (!favorites.length) return null

  return favorites
    .slice()
    .sort((left, right) => {
      const leftRoi = getReturnPct(left.metrics)
      const rightRoi = getReturnPct(right.metrics)
      const leftHasRoi = leftRoi != null
      const rightHasRoi = rightRoi != null

      if (leftHasRoi && rightHasRoi && leftRoi !== rightRoi) {
        return (rightRoi || 0) - (leftRoi || 0)
      }
      if (leftHasRoi !== rightHasRoi) {
        return leftHasRoi ? -1 : 1
      }

      const leftTs = new Date(left.created_at).getTime()
      const rightTs = new Date(right.created_at).getTime()
      return rightTs - leftTs
    })[0]
}

function toneForColumn(column: string) {
  const normalized = String(column || '').toLowerCase()
  if (normalized.includes('qa')) return 'ok'
  if (normalized.includes('dev') || normalized.includes('design') || normalized.includes('po')) return 'warn'
  return 'idle'
}

function toneForRunStatus(status: string) {
  const normalized = String(status || '').toLowerCase()
  if (['done', 'completed', 'success'].includes(normalized)) return 'ok'
  if (['running', 'queued', 'pending', 'created'].includes(normalized)) return 'warn'
  return 'idle'
}

function formatRunStep(step: string | null | undefined) {
  const value = String(step || '').trim()
  if (!value) return 'Etapa não informada'
  return value.replaceAll('_', ' ')
}

function SnapshotBadge({ children }: { children: string }) {
  return (
    <span className="rounded-full border border-white/10 bg-white/[0.04] px-2.5 py-1 text-[10px] font-semibold uppercase tracking-[0.14em] text-[var(--text-secondary)]">
      {children}
    </span>
  )
}

function SectionTag({ label, tone = 'idle' }: { label: string; tone?: 'ok' | 'warn' | 'idle' }) {
  return (
    <span
      className={cx(
        'inline-flex items-center rounded-full px-3 py-1 text-[10px] font-semibold tracking-[0.12em]',
        tone === 'ok' && 'bg-emerald-400/12 text-emerald-300',
        tone === 'warn' && 'bg-amber-400/12 text-amber-300',
        tone === 'idle' && 'bg-white/10 text-[var(--text-secondary)]',
      )}
    >
      {label}
    </span>
  )
}

function KpiSkeleton() {
  return (
    <div className="mt-3 space-y-2 animate-pulse">
      <div className="h-7 w-28 rounded-lg bg-white/10" />
      <div className="h-4 w-40 rounded bg-white/5" />
    </div>
  )
}

function SectionSkeletonRows({ rows = 3 }: { rows?: number }) {
  return (
    <div className="mt-5 space-y-3 animate-pulse">
      {Array.from({ length: rows }).map((_, index) => (
        <div key={index} className="h-20 rounded-2xl border border-white/8 bg-white/[0.03]" />
      ))}
    </div>
  )
}

function KpiCard({
  title,
  label,
  children,
  testId,
}: {
  title: string
  label?: string
  children: React.ReactNode
  testId?: string
}) {
  return (
    <div className="page-card p-5" data-testid={testId}>
      <div className="flex items-start justify-between gap-3">
        <div className="text-[11px] uppercase tracking-[0.14em] text-[var(--text-muted)]">{title}</div>
        {label ? <SnapshotBadge>{label}</SnapshotBadge> : null}
      </div>
      {children}
    </div>
  )
}

export default function HomePage() {
  const navigate = useNavigate()
  const { user } = useAuth()

  const healthQuery = useQuery<HealthState>({
    queryKey: ['home', 'health'],
    queryFn: () => fetchJson<HealthState>('/health'),
    refetchOnWindowFocus: false,
  })

  const favoritesQuery = useQuery<FavoriteStrategy[]>({
    queryKey: ['home', 'favorites', user?.id ?? 'anonymous'],
    queryFn: () => fetchJson<FavoriteStrategy[]>('/favorites/'),
    refetchOnWindowFocus: false,
  })

  const balancesQuery = useQuery<BalancesSnapshot>({
    queryKey: ['home', 'balances', user?.id ?? 'anonymous'],
    queryFn: () => fetchJson<BalancesSnapshot>('/external/binance/spot/balances'),
    refetchOnWindowFocus: false,
  })

  const portfolioKpiQuery = useQuery<PortfolioKPI>({
    queryKey: ['home', 'portfolio-kpi', user?.id ?? 'anonymous'],
    queryFn: () => fetchJson<PortfolioKPI>('/portfolio/kpi'),
    refetchOnWindowFocus: false,
  })

  const focusQuery = useQuery<FocusChange[]>({
    queryKey: ['home', 'focus'],
    queryFn: async () => {
      const response = await fetchJson<CoordinationChangeListResponse>('/workflow/kanban/changes?project_slug=crypto')
      const activeChanges = (response.items || [])
        .filter((item) => item.item_type !== 'bug')
        .filter((item) => !item.archived)
        .filter((item) => !['Archived', 'Canceled'].includes(item.column))
        .slice(-3)
        .reverse()

      const detailed = await Promise.all(
        activeChanges.map(async (item) => {
          try {
            const detail = await fetchJson<ChangeDetailResponse>(
              `/workflow/projects/crypto/changes/${encodeURIComponent(item.id)}`,
            )
            return {
              ...item,
              created_at: detail.created_at,
              updated_at: detail.updated_at,
            }
          } catch {
            return {
              ...item,
              created_at: null,
              updated_at: null,
            }
          }
        }),
      )

      return detailed
    },
    refetchOnWindowFocus: false,
  })

  const runsQuery = useQuery<LabRunsResponse>({
    queryKey: ['home', 'lab-runs', user?.id ?? 'anonymous'],
    queryFn: () => fetchJson<LabRunsResponse>('/lab/runs?limit=5'),
    refetchOnWindowFocus: false,
  })

  const marketQuery = useQuery<MarketPricesResponse>({
    queryKey: ['home', 'market-prices'],
    queryFn: () => fetchJson<MarketPricesResponse>('/market/prices'),
    refetchOnWindowFocus: false,
    refetchInterval: 30_000,
  })

  const nowLabel = useMemo(() => formatDt(new Date()), [])
  const bestFavorite = useMemo(() => getBestFavorite(favoritesQuery.data || []), [favoritesQuery.data])
  const bestFavoriteRoi = getReturnPct(bestFavorite?.metrics)
  const balancesFreshness = formatFreshness(balancesQuery.data?.as_of)
  const activeChanges = focusQuery.data || []
  const recentRuns = runsQuery.data?.runs || []
  const marketPrices = marketQuery.data?.prices || []
  const marketFreshness = formatFreshness(marketQuery.data?.fetched_at || undefined)
  const healthStatus = healthQuery.data?.status === 'ok' ? 'ok' : healthQuery.isLoading ? 'loading' : 'error'

  return (
    <main className="page-stack">
      <div className="page-stack">
        <section className="grid grid-cols-1 gap-6 lg:grid-cols-[1.45fr_0.95fr]">
          <div className="page-card p-6 sm:p-8 lg:p-10">
            <span className="eyebrow mb-5">Cockpit diário</span>
            <h1 className="section-title">Seu snapshot diário de crypto</h1>
            <p className="section-copy mt-4 text-sm sm:text-base">
              Como estou indo, o que precisa atenção e qual o próximo passo mais rápido.
            </p>

            <div className="mt-8 grid grid-cols-1 gap-3 md:grid-cols-3">
              <button
                type="button"
                onClick={() => navigate('/combo/select')}
                className="rounded-2xl border border-white/10 bg-white/[0.03] p-4 text-left shadow-[inset_0_1px_0_rgba(255,255,255,0.03)] hover:-translate-y-0.5 hover:border-emerald-300/20 hover:bg-white/[0.06]"
              >
                <div className="flex items-center justify-between">
                  <div>
                    <div className="text-sm font-semibold text-[var(--text-primary)]">Rodar um backtest</div>
                    <div className="mt-1 text-xs text-[var(--text-tertiary)]">Escolha estratégia · timeframe</div>
                  </div>
                  <ArrowRight className="h-4 w-4 text-[var(--text-tertiary)]" />
                </div>
              </button>

              <button
                type="button"
                onClick={() => navigate('/lab')}
                className="rounded-2xl border border-white/10 bg-white/[0.03] p-4 text-left shadow-[inset_0_1px_0_rgba(255,255,255,0.03)] hover:-translate-y-0.5 hover:border-sky-300/20 hover:bg-white/[0.06]"
              >
                <div className="flex items-center justify-between">
                  <div>
                    <div className="text-sm font-semibold text-[var(--text-primary)]">Atualizar dados</div>
                    <div className="mt-1 text-xs text-[var(--text-tertiary)]">Explorar candles · Lab</div>
                  </div>
                  <ArrowRight className="h-4 w-4 text-[var(--text-tertiary)]" />
                </div>
              </button>

              <button
                type="button"
                onClick={() => navigate('/monitor')}
                className="rounded-2xl border border-white/10 bg-white/[0.03] p-4 text-left shadow-[inset_0_1px_0_rgba(255,255,255,0.03)] hover:-translate-y-0.5 hover:border-amber-300/20 hover:bg-white/[0.06]"
              >
                <div className="flex items-center justify-between">
                  <div>
                    <div className="text-sm font-semibold text-[var(--text-primary)]">Abrir monitor</div>
                    <div className="mt-1 text-xs text-[var(--text-tertiary)]">Sinais · posições</div>
                  </div>
                  <ArrowRight className="h-4 w-4 text-[var(--text-tertiary)]" />
                </div>
              </button>
            </div>
          </div>

          <aside className="page-card p-6 sm:p-7">
            <div className="flex items-center justify-between gap-3">
              <h2 className="text-xs font-semibold uppercase tracking-[0.18em] text-[var(--text-muted)]">Saúde do sistema</h2>
              <span
                className={cx(
                  'rounded-full px-3 py-1 text-[10px] font-semibold tracking-[0.12em]',
                  healthStatus === 'ok' && 'bg-emerald-400/12 text-emerald-300',
                  healthStatus === 'loading' && 'bg-white/[0.06] text-[var(--text-secondary)]',
                  healthStatus === 'error' && 'bg-red-400/12 text-red-300',
                )}
              >
                {healthStatus === 'loading' ? 'CHECK' : healthStatus.toUpperCase()}
              </span>
            </div>

            <dl className="mt-5 space-y-3 text-sm">
              <div className="flex justify-between gap-4 rounded-2xl bg-white/[0.03] px-4 py-3">
                <dt className="text-[var(--text-tertiary)]">Último check</dt>
                <dd className="text-[var(--text-secondary)]">{nowLabel}</dd>
              </div>
              <div className="flex justify-between gap-4 rounded-2xl bg-white/[0.03] px-4 py-3">
                <dt className="text-[var(--text-tertiary)]">API</dt>
                <dd className="text-[var(--text-secondary)]">{healthQuery.data?.service || '—'}</dd>
              </div>
              <div className="flex justify-between gap-4 rounded-2xl bg-white/[0.03] px-4 py-3">
                <dt className="text-[var(--text-tertiary)]">Carteira</dt>
                <dd className="text-[var(--text-secondary)]">External balances</dd>
              </div>
            </dl>

            <div className="mt-5 flex flex-wrap gap-2">
              <button
                type="button"
                onClick={() => navigate('/openspec')}
                className="rounded-full border border-white/10 px-3.5 py-2 text-xs font-medium text-[var(--text-secondary)] hover:border-sky-300/18 hover:bg-white/[0.05] hover:text-white"
              >
                <FileText className="mr-1.5 inline-block h-3.5 w-3.5" />
                OpenSpec
              </button>
              <button
                type="button"
                onClick={() => navigate('/lab')}
                className="rounded-full border border-white/10 px-3.5 py-2 text-xs font-medium text-[var(--text-secondary)] hover:border-emerald-300/18 hover:bg-white/[0.05] hover:text-white"
              >
                <Settings className="mr-1.5 inline-block h-3.5 w-3.5" />
                Lab
              </button>
            </div>
          </aside>
        </section>

        <section className="grid grid-cols-1 gap-3 sm:grid-cols-2 xl:grid-cols-4">
          <KpiCard title="Portfolio PnL (hoje)" testId="home-kpi-pnl">
            {portfolioKpiQuery.isLoading ? (
              <KpiSkeleton />
            ) : portfolioKpiQuery.error ? (
              <>
                <div className="mt-3 text-xl font-semibold text-[var(--text-primary)]">não disponível</div>
                <div className="mt-1 text-[12px] text-rose-300">Não foi possível carregar `/api/portfolio/kpi`.</div>
              </>
            ) : (
              <>
                <div className={`mt-3 text-2xl font-semibold ${(portfolioKpiQuery.data?.pnl_today_pct ?? 0) >= 0 ? 'text-emerald-300' : 'text-rose-300'}`}>
                  {portfolioKpiQuery.data?.pnl_today_pct != null ? `${portfolioKpiQuery.data.pnl_today_pct >= 0 ? '+' : ''}${portfolioKpiQuery.data.pnl_today_pct.toFixed(2)}%` : 'N/A'}
                </div>
                <div className="mt-1 text-[12px] text-[var(--text-tertiary)]">
                  {portfolioKpiQuery.data?.pnl_today_vs_btc_pct != null
                    ? `vs. BTC: ${portfolioKpiQuery.data.pnl_today_vs_btc_pct >= 0 ? '+' : ''}${portfolioKpiQuery.data.pnl_today_vs_btc_pct.toFixed(2)}%`
                    : 'vs. BTC: N/A'}
                </div>
              </>
            )}
          </KpiCard>

          <KpiCard title="Drawdown (30d)" testId="home-kpi-drawdown">
            {portfolioKpiQuery.isLoading ? (
              <KpiSkeleton />
            ) : portfolioKpiQuery.error ? (
              <>
                <div className="mt-3 text-xl font-semibold text-[var(--text-primary)]">não disponível</div>
                <div className="mt-1 text-[12px] text-rose-300">Não foi possível carregar `/api/portfolio/kpi`.</div>
              </>
            ) : (
              <>
                <div className={`mt-3 text-2xl font-semibold ${(portfolioKpiQuery.data?.drawdown_30d_pct ?? 0) >= 0 ? 'text-emerald-300' : 'text-rose-300'}`}>
                  {portfolioKpiQuery.data?.drawdown_30d_pct != null ? `${portfolioKpiQuery.data.drawdown_30d_pct.toFixed(2)}%` : 'N/A'}
                </div>
                <div className="mt-1 text-[12px] text-[var(--text-tertiary)]">
                  {portfolioKpiQuery.data?.drawdown_peak_date ? `Pico: ${new Date(portfolioKpiQuery.data.drawdown_peak_date).toLocaleDateString('pt-BR', { day: 'numeric', month: 'short' })}` : 'Pico: N/A'}
                </div>
              </>
            )}
          </KpiCard>

          <KpiCard title="Melhor estratégia (7d)" testId="home-kpi-best-strategy">
            {favoritesQuery.isLoading ? (
              <KpiSkeleton />
            ) : favoritesQuery.error ? (
              <>
                <div className="mt-3 text-xl font-semibold text-[var(--text-primary)]">não disponível</div>
                <div className="mt-1 text-[12px] text-rose-300">Não foi possível carregar `/api/favorites`.</div>
              </>
            ) : !bestFavorite ? (
              <>
                <div className="mt-3 text-xl font-semibold text-[var(--text-primary)]">Nenhuma estratégia favoritada</div>
                <div className="mt-1 text-[12px] text-[var(--text-tertiary)]">Salve uma estratégia para acompanhar aqui.</div>
              </>
            ) : (
              <>
                <div className="mt-3 text-2xl font-semibold text-[var(--text-primary)]">
                  {bestFavorite.strategy_name || bestFavorite.name}
                </div>
                <div className="mt-1 text-[12px] text-[var(--text-tertiary)]">
                  {bestFavorite.symbol} · {bestFavorite.timeframe}
                  {bestFavoriteRoi != null ? ` · ROI ${formatPercent(bestFavoriteRoi)}` : ' · ROI não disponível'}
                </div>
              </>
            )}
          </KpiCard>

          <KpiCard title="Data freshness" testId="home-kpi-freshness">
            {balancesQuery.isLoading ? (
              <KpiSkeleton />
            ) : balancesQuery.error ? (
              <>
                <div className="mt-3 text-xl font-semibold text-[var(--text-primary)]">não disponível</div>
                <div className="mt-1 text-[12px] text-rose-300">Não foi possível carregar `/api/external/binance/spot/balances`.</div>
              </>
            ) : !balancesQuery.data?.as_of ? (
              <>
                <div className="mt-3 text-xl font-semibold text-[var(--text-primary)]">Sem snapshot disponível</div>
                <div className="mt-1 text-[12px] text-[var(--text-tertiary)]">O endpoint respondeu sem timestamp utilizável.</div>
              </>
            ) : (
              <>
                <div className="mt-3 text-2xl font-semibold text-[var(--text-primary)]">{balancesFreshness || 'Snapshot recente'}</div>
                <div className="mt-1 text-[12px] text-[var(--text-tertiary)]">Snapshot em {formatDt(balancesQuery.data.as_of)}</div>
              </>
            )}
          </KpiCard>
        </section>

        <PortfolioAllocation />

        <section className="grid grid-cols-1 gap-6 lg:grid-cols-[1.45fr_0.95fr]">
          <div className="flex flex-col gap-4">
            <div className="page-card p-6" data-testid="home-focus-section">
              <div className="flex items-center justify-between gap-3">
                <div className="flex items-center gap-3">
                  <h2 className="text-xs font-semibold uppercase tracking-[0.18em] text-[var(--text-muted)]">Mudanças ativas</h2>
                  <SnapshotBadge>kanban real</SnapshotBadge>
                </div>
                <Link to="/kanban" className="text-[11px] font-semibold text-emerald-300 hover:text-emerald-200">
                  Ver tudo
                </Link>
              </div>

              {focusQuery.isLoading ? <SectionSkeletonRows /> : null}
              {focusQuery.error ? (
                <div className="mt-5 rounded-2xl border border-rose-400/20 bg-rose-400/5 px-4 py-4 text-sm text-rose-200">
                  não disponível · Falha ao carregar mudanças ativas.
                </div>
              ) : null}
              {!focusQuery.isLoading && !focusQuery.error && activeChanges.length === 0 ? (
                <div className="mt-5 rounded-2xl border border-white/8 bg-white/[0.03] p-4 text-sm text-[var(--text-tertiary)]">
                  Nenhuma mudança ativa no momento
                </div>
              ) : null}

              {!focusQuery.isLoading && !focusQuery.error && activeChanges.length > 0 ? (
                <ul className="mt-5 space-y-3">
                  {activeChanges.map((item) => {
                    const tone = toneForColumn(item.column)
                    const statusLabel = item.column || item.status?.status || 'Ativa'
                    const dateLabel = item.updated_at ? formatDt(item.updated_at) : 'Data indisponível'

                    return (
                      <li
                        key={item.id}
                        className="flex items-center gap-3 rounded-2xl border border-white/8 bg-white/[0.03] p-4 hover:bg-white/[0.05]"
                      >
                        <SectionTag label={statusLabel} tone={tone} />
                        <div className="min-w-0 flex-1">
                          <div className="truncate text-sm text-[var(--text-primary)]">{item.title || item.id}</div>
                          <div className="mt-0.5 text-[11px] text-[var(--text-tertiary)]">
                            {item.card_number ? `Card #${item.card_number}` : item.id} · {dateLabel}
                          </div>
                        </div>
                        <button
                          type="button"
                          onClick={() => navigate('/kanban')}
                          className="rounded-full border border-white/10 px-3 py-1.5 text-[11px] font-semibold text-[var(--text-secondary)] hover:bg-white/[0.06] hover:text-white"
                        >
                          Abrir
                        </button>
                      </li>
                    )
                  })}
                </ul>
              ) : null}
            </div>

            <div className="page-card p-6" data-testid="home-runs-section">
              <div className="flex items-center justify-between gap-3">
                <div className="flex items-center gap-3">
                  <h2 className="text-xs font-semibold uppercase tracking-[0.18em] text-[var(--text-muted)]">Runs recentes</h2>
                  <SnapshotBadge>lab real</SnapshotBadge>
                </div>
                <Link to="/lab" className="text-[11px] font-semibold text-sky-300 hover:text-sky-200">
                  Abrir Lab
                </Link>
              </div>

              {runsQuery.isLoading ? <SectionSkeletonRows rows={4} /> : null}
              {runsQuery.error ? (
                <div className="mt-5 rounded-2xl border border-rose-400/20 bg-rose-400/5 px-4 py-4 text-sm text-rose-200">
                  não disponível · Falha ao carregar `/api/lab/runs`.
                </div>
              ) : null}
              {!runsQuery.isLoading && !runsQuery.error && recentRuns.length === 0 ? (
                <div className="mt-5 rounded-2xl border border-white/8 bg-white/[0.03] p-4 text-sm text-[var(--text-tertiary)]">
                  Nenhuma run recente encontrada.
                </div>
              ) : null}

              {!runsQuery.isLoading && !runsQuery.error && recentRuns.length > 0 ? (
                <ul className="mt-5 space-y-3">
                  {recentRuns.map((run) => (
                    <li
                      key={run.run_id}
                      className="flex items-center gap-3 rounded-2xl border border-white/8 bg-white/[0.03] p-4 hover:bg-white/[0.05]"
                    >
                      <SectionTag label={run.status || 'unknown'} tone={toneForRunStatus(run.status)} />
                      <div className="min-w-0 flex-1">
                        <div className="truncate text-sm text-[var(--text-primary)]">{run.run_id}</div>
                        <div className="mt-0.5 text-[11px] text-[var(--text-tertiary)]">
                          {formatRunStep(run.step)} · {formatDt(new Date(run.created_at_ms || run.updated_at_ms || 0))}
                        </div>
                      </div>
                      <a
                        href={run.viewer_url}
                        className="rounded-full border border-white/10 px-3 py-1.5 text-[11px] font-semibold text-[var(--text-secondary)] hover:bg-white/[0.06] hover:text-white"
                      >
                        Ver trace
                      </a>
                    </li>
                  ))}
                </ul>
              ) : null}
            </div>


          </div>

          <aside className="flex flex-col gap-4">
            <div className="page-card p-6" data-testid="home-market-section">
              <div className="flex items-center justify-between gap-3">
                <div className="flex items-center gap-3">
                  <h2 className="text-xs font-semibold uppercase tracking-[0.18em] text-[var(--text-muted)]">Market watch</h2>
                  <SnapshotBadge>binance 24h</SnapshotBadge>
                </div>
                <Link to="/monitor" className="text-[11px] font-semibold text-amber-300 hover:text-amber-200">
                  Abrir monitor
                </Link>
              </div>

              {marketQuery.isLoading ? <SectionSkeletonRows rows={3} /> : null}
              {marketQuery.error ? (
                <div className="mt-5 rounded-2xl border border-rose-400/20 bg-rose-400/5 px-4 py-4 text-sm text-rose-200">
                  não disponível · Falha ao carregar `/api/market/prices`.
                </div>
              ) : null}
              {!marketQuery.isLoading && !marketQuery.error && marketPrices.length === 0 ? (
                <div className="mt-5 rounded-2xl border border-white/8 bg-white/[0.03] p-4 text-sm text-[var(--text-tertiary)]">
                  Nenhum preço disponível agora.
                </div>
              ) : null}

              {!marketQuery.isLoading && !marketQuery.error && marketPrices.length > 0 ? (
                <div className="mt-5 space-y-3">
                  {marketPrices.map((item) => {
                    const changeLabel = formatPercent(item.change_24h_pct)
                    return (
                      <div key={item.symbol} className="rounded-2xl border border-white/8 bg-white/[0.03] p-4">
                        <div className="flex items-center justify-between gap-3">
                          <div>
                            <div className="text-sm font-semibold text-[var(--text-primary)]">{item.symbol}</div>
                            <div className="mt-1 text-[11px] text-[var(--text-tertiary)]">{formatCurrency(item.price)}</div>
                          </div>
                          <div
                            className={cx(
                              'text-sm font-semibold',
                              item.change_24h_pct >= 0 ? 'text-emerald-300' : 'text-rose-300',
                            )}
                          >
                            {changeLabel || '—'}
                          </div>
                        </div>
                      </div>
                    )
                  })}

                  <div className="text-[11px] text-[var(--text-tertiary)]">
                    {marketQuery.data?.fetched_at
                      ? `Atualizado ${marketFreshness || formatDt(marketQuery.data.fetched_at)}`
                      : 'Sem timestamp de atualização.'}
                  </div>
                </div>
              ) : null}
            </div>

            <div className="page-card p-6">
              <h2 className="text-xs font-semibold uppercase tracking-[0.18em] text-[var(--text-muted)]">Atalhos</h2>
              <div className="mt-4 flex flex-wrap gap-2">
                {[
                  { to: '/combo/select', label: 'Combo', icon: Layers },
                  { to: '/kanban', label: 'Kanban', icon: Kanban },
                  { to: '/external/balances', label: 'Carteira', icon: Activity },
                ].map(({ to, label, icon: Icon }) => (
                  <Link
                    key={to}
                    to={to}
                    className="inline-flex items-center gap-1.5 rounded-full border border-white/10 px-3 py-2 text-xs font-medium text-[var(--text-secondary)] hover:border-white/20 hover:bg-white/[0.05] hover:text-white"
                  >
                    <Icon className="h-3.5 w-3.5" />
                    {label}
                  </Link>
                ))}
              </div>
            </div>

            <div className="page-card p-6">
              <h2 className="text-xs font-semibold uppercase tracking-[0.18em] text-[var(--text-muted)]">Notas</h2>
              <p className="mt-3 text-[12px] leading-6 text-[var(--text-tertiary)]">
                Home usa dados reais para saúde, favoritos, carteira, Kanban, runs recentes e market watch. Só os KPIs marcados continuam ilustrativos.
              </p>
            </div>
          </aside>
        </section>
      </div>
    </main>
  )
}
