import { useMemo, useState } from 'react'
import { AlertTriangle, ArrowDownRight, ArrowUpRight, CircleGauge, RefreshCw, ShieldAlert, WalletCards } from 'lucide-react'
import { useQuery } from '@tanstack/react-query'

import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { Card, CardContent } from '@/components/ui/Card'
import { apiUrl } from '@/lib/apiBase'
import { authFetch } from '@/lib/authFetch'

type SupplyWindow = '24h' | '7d' | '30d'

type SupplyBand = {
  id: string
  label: string
  min_btc: number | null
  max_btc: number | null
  latest: number | null
  previous: number | null
  change_abs: number | null
  change_pct: number | null
  share_pct: number | null
}

type SupplyCohort = {
  latest?: number | null
  previous?: number | null
  change_abs?: number | null
  change_pct?: number | null
  share_pct?: number | null
}

type WhaleMovement = {
  threshold_btc: number | null
  change_abs: number | null
  direction: string | null
  alert: boolean
}

type SupplyAlert = {
  type: string
  threshold_btc?: number | null
  change_abs?: number | null
  direction?: string | null
}

type SupplyDistributionResponse = {
  asset: string
  basis: string
  window: SupplyWindow
  interval: string
  since: number | string | null
  until: number | string | null
  cached: boolean
  bands: SupplyBand[]
  cohorts: Record<string, SupplyCohort | null>
  whale_movement: WhaleMovement | null
  alerts: SupplyAlert[]
  sources: Record<string, unknown>
}

const WINDOWS: SupplyWindow[] = ['24h', '7d', '30d']

const COHORT_LABELS: Record<string, string> = {
  shrimps: 'Shrimps',
  whales: 'Whales',
  hodlers: 'Hodlers',
}

function formatBtc(value: number | null | undefined) {
  if (value === null || value === undefined || !Number.isFinite(value)) return '—'
  return new Intl.NumberFormat('pt-BR', {
    maximumFractionDigits: Math.abs(value) >= 100 ? 0 : 4,
  }).format(value)
}

function formatPct(value: number | null | undefined) {
  if (value === null || value === undefined || !Number.isFinite(value)) return '—'
  const sign = value > 0 ? '+' : ''
  return `${sign}${value.toFixed(2)}%`
}

function formatDate(value: number | string | null | undefined) {
  if (value === null || value === undefined || value === '') return '—'
  const parsed = typeof value === 'number' ? new Date(value * 1000) : new Date(value)
  if (Number.isNaN(parsed.getTime())) return value
  return new Intl.DateTimeFormat('pt-BR', { dateStyle: 'short', timeStyle: 'short' }).format(parsed)
}

function changeTone(value: number | null | undefined) {
  if (value === null || value === undefined || !Number.isFinite(value) || value === 0) {
    return 'text-[var(--text-tertiary)]'
  }
  return value > 0 ? 'text-emerald-300' : 'text-rose-300'
}

function directionLabel(direction: string | null | undefined) {
  if (!direction) return 'Sem movimento'
  if (direction === 'accumulation' || direction === 'increase') return 'Acumulação'
  if (direction === 'distribution' || direction === 'decrease') return 'Distribuição'
  return direction
}

function sourceCount(sources: Record<string, unknown> | undefined) {
  if (!sources) return 0
  return Object.keys(sources).length
}

async function fetchSupplyDistribution(window: SupplyWindow) {
  const url = apiUrl('/onchain/glassnode/BTC/supply-distribution')
  url.searchParams.set('basis', 'entity')
  url.searchParams.set('window', window)

  const response = await authFetch(url.toString())
  if (!response.ok) {
    throw new Error(`Falha ao carregar distribuição (${response.status})`)
  }
  return (await response.json()) as SupplyDistributionResponse
}

function CohortCard({ id, cohort }: { id: string; cohort: SupplyCohort | null | undefined }) {
  const label = COHORT_LABELS[id] ?? id
  const change = cohort?.change_pct

  return (
    <Card className="page-card border-white/8 bg-[linear-gradient(180deg,rgba(16,28,42,0.98),rgba(12,22,34,0.94))]">
      <CardContent className="p-5">
        <div className="flex items-start justify-between gap-3">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[var(--text-muted)]">{label}</p>
            <p className="mt-2 text-2xl font-semibold text-[var(--text-primary)]">{formatBtc(cohort?.latest)} BTC</p>
          </div>
          <div className={`flex items-center gap-1 text-sm font-semibold ${changeTone(change)}`}>
            {(change ?? 0) >= 0 ? <ArrowUpRight className="h-4 w-4" /> : <ArrowDownRight className="h-4 w-4" />}
            <span>{formatPct(change)}</span>
          </div>
        </div>
        <div className="mt-4 grid grid-cols-2 gap-3 text-sm">
          <div className="page-card-muted px-3 py-2">
            <p className="text-[11px] font-semibold uppercase tracking-[0.16em] text-[var(--text-muted)]">Share</p>
            <p className="mt-1 font-semibold text-[var(--text-primary)]">{formatPct(cohort?.share_pct)}</p>
          </div>
          <div className="page-card-muted px-3 py-2">
            <p className="text-[11px] font-semibold uppercase tracking-[0.16em] text-[var(--text-muted)]">Delta</p>
            <p className={`mt-1 font-semibold ${changeTone(cohort?.change_abs)}`}>{formatBtc(cohort?.change_abs)} BTC</p>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

function BandRow({ band, maxShare }: { band: SupplyBand; maxShare: number }) {
  const share = typeof band.share_pct === 'number' && Number.isFinite(band.share_pct) ? band.share_pct : 0
  const width = maxShare > 0 ? Math.max(2, Math.min(100, (share / maxShare) * 100)) : 2

  return (
    <div className="page-card-muted px-4 py-3" data-testid={`supply-band-${band.id}`}>
      <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
        <div className="min-w-0">
          <div className="flex flex-wrap items-center gap-2">
            <h3 className="text-sm font-semibold text-[var(--text-primary)]">{band.label}</h3>
            <Badge variant="outline">{formatPct(band.share_pct)} share</Badge>
          </div>
          <p className="mt-1 text-xs text-[var(--text-tertiary)]">
            {formatBtc(band.min_btc)} - {band.max_btc === null ? '∞' : formatBtc(band.max_btc)} BTC
          </p>
        </div>
        <div className="grid grid-cols-2 gap-3 text-right text-sm sm:grid-cols-3">
          <div>
            <p className="text-[11px] uppercase tracking-[0.14em] text-[var(--text-muted)]">Atual</p>
            <p className="font-semibold text-[var(--text-primary)]">{formatBtc(band.latest)}</p>
          </div>
          <div>
            <p className="text-[11px] uppercase tracking-[0.14em] text-[var(--text-muted)]">Delta</p>
            <p className={`font-semibold ${changeTone(band.change_abs)}`}>{formatBtc(band.change_abs)}</p>
          </div>
          <div className="col-span-2 sm:col-span-1">
            <p className="text-[11px] uppercase tracking-[0.14em] text-[var(--text-muted)]">Var.</p>
            <p className={`font-semibold ${changeTone(band.change_pct)}`}>{formatPct(band.change_pct)}</p>
          </div>
        </div>
      </div>
      <div className="mt-3 h-2 overflow-hidden rounded-full bg-white/[0.06]">
        <div className="h-full rounded-full bg-[linear-gradient(90deg,rgba(34,197,94,0.95),rgba(56,189,248,0.9))]" style={{ width: `${width}%` }} />
      </div>
    </div>
  )
}

export default function SupplyDistributionPage() {
  const [windowValue, setWindowValue] = useState<SupplyWindow>('24h')

  const query = useQuery({
    queryKey: ['supply-distribution', windowValue],
    queryFn: () => fetchSupplyDistribution(windowValue),
    placeholderData: (previousData) => previousData,
    retry: 1,
    refetchOnWindowFocus: false,
  })

  const cohortEntries = useMemo(() => {
    const cohorts = query.data?.cohorts ?? {}
    return ['shrimps', 'whales', 'hodlers'].map((id) => [id, cohorts[id]] as const)
  }, [query.data?.cohorts])
  const maxShare = useMemo(() => {
    return Math.max(0, ...(query.data?.bands ?? []).map((band) => (typeof band.share_pct === 'number' ? band.share_pct : 0)))
  }, [query.data?.bands])

  const whaleAlert = query.data?.alerts?.find((alert) => alert.type === 'whale-alert')
  const whaleMovement = query.data?.whale_movement
  const isEmpty = query.data && query.data.bands.length === 0 && Object.keys(query.data.cohorts ?? {}).length === 0

  return (
    <div className="app-page space-y-6 pb-20">
      <header className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-[var(--text-muted)]">Glassnode / BTC</p>
          <h1 className="mt-2 text-3xl font-bold text-[var(--text-primary)]">Distribuição de supply</h1>
          <p className="mt-2 max-w-3xl text-sm text-[var(--text-secondary)]">
            Supply por bandas de entidade, cohorts agregados e alerta de movimentação whale.
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-2" role="group" aria-label="Janela de distribuição">
          {WINDOWS.map((item) => (
            <button
              key={item}
              type="button"
              onClick={() => setWindowValue(item)}
              className={[
                'inline-flex h-10 min-w-14 items-center justify-center rounded-2xl border px-4 text-sm font-semibold transition',
                windowValue === item
                  ? 'border-emerald-300/30 bg-emerald-400/14 text-emerald-100'
                  : 'border-white/10 bg-white/[0.04] text-[var(--text-secondary)] hover:bg-white/[0.08] hover:text-white',
              ].join(' ')}
            >
              {item}
            </button>
          ))}
        </div>
      </header>

      <section className="page-card p-5 sm:p-6" aria-label="Resumo">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
          <div className="flex flex-wrap items-center gap-2">
            <Badge variant="secondary">{query.data?.asset ?? 'BTC'}</Badge>
            <Badge variant="outline">Basis {query.data?.basis ?? 'entity'}</Badge>
            {query.data?.cached ? <Badge variant="warning">Cache</Badge> : <Badge variant="success">Fresh</Badge>}
            {query.isFetching ? <Badge variant="outline">Atualizando</Badge> : null}
          </div>
          <div className="flex flex-wrap gap-4 text-sm text-[var(--text-secondary)]">
            <span>Intervalo: {query.data?.interval ?? '—'}</span>
            <span>Desde: {formatDate(query.data?.since)}</span>
            <span>Até: {formatDate(query.data?.until)}</span>
            <span>Fontes: {sourceCount(query.data?.sources)}</span>
          </div>
        </div>
      </section>

      {query.isLoading ? (
        <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
          {Array.from({ length: 3 }).map((_, index) => (
            <div key={index} className="page-card h-44 animate-pulse" />
          ))}
        </div>
      ) : query.error && !query.data ? (
        <Card className="border-red-400/25 bg-red-500/8">
          <CardContent className="flex flex-col gap-4 p-6 sm:flex-row sm:items-center sm:justify-between">
            <div className="flex items-start gap-3">
              <AlertTriangle className="mt-1 h-5 w-5 shrink-0 text-red-300" />
              <div>
                <h2 className="text-lg font-semibold text-red-100">Não foi possível carregar distribuição</h2>
                <p className="text-sm text-red-100/80">Verifique a API on-chain e tente novamente.</p>
              </div>
            </div>
            <Button onClick={() => void query.refetch()} icon={<RefreshCw className="h-4 w-4" />}>
              Recarregar
            </Button>
          </CardContent>
        </Card>
      ) : isEmpty ? (
        <Card>
          <CardContent className="p-8 text-center">
            <WalletCards className="mx-auto h-8 w-8 text-[var(--text-tertiary)]" />
            <h2 className="mt-3 text-lg font-semibold text-[var(--text-primary)]">Nenhuma banda disponível</h2>
            <p className="mt-2 text-sm text-[var(--text-secondary)]">A janela selecionada ainda não retornou dados de supply.</p>
          </CardContent>
        </Card>
      ) : (
        <>
          <section className="grid grid-cols-1 gap-4 md:grid-cols-3" aria-label="Cohorts">
            {cohortEntries.map(([id, cohort]) => (
              <CohortCard key={id} id={id} cohort={cohort} />
            ))}
          </section>

          <section className="grid grid-cols-1 gap-4 xl:grid-cols-[minmax(0,1fr)_360px]">
            <Card className="page-card border-white/8 bg-[linear-gradient(180deg,rgba(16,28,42,0.98),rgba(12,22,34,0.94))]">
              <CardContent className="p-5 sm:p-6">
                <div className="mb-4 flex items-center justify-between gap-3">
                  <div>
                    <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[var(--text-muted)]">Bandas</p>
                    <h2 className="mt-1 text-xl font-semibold text-[var(--text-primary)]">Supply por faixa</h2>
                  </div>
                  <CircleGauge className="h-5 w-5 text-sky-300" />
                </div>
                <div className="space-y-3">
                  {query.data?.bands.map((band) => (
                    <BandRow key={band.id} band={band} maxShare={maxShare} />
                  ))}
                </div>
              </CardContent>
            </Card>

            <Card className="page-card border-white/8 bg-[linear-gradient(180deg,rgba(16,28,42,0.98),rgba(12,22,34,0.94))]">
              <CardContent className="p-5 sm:p-6">
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[var(--text-muted)]">Whale alert</p>
                    <h2 className="mt-1 text-xl font-semibold text-[var(--text-primary)]">
                      {whaleAlert || whaleMovement?.alert ? 'Ativo' : 'Normal'}
                    </h2>
                  </div>
                  <ShieldAlert className={['h-6 w-6', whaleAlert || whaleMovement?.alert ? 'text-amber-300' : 'text-emerald-300'].join(' ')} />
                </div>

                <div className="mt-5 space-y-3">
                  <div className="page-card-muted px-4 py-3">
                    <p className="text-[11px] font-semibold uppercase tracking-[0.16em] text-[var(--text-muted)]">Direção</p>
                    <p className="mt-1 text-lg font-semibold text-[var(--text-primary)]">{directionLabel(whaleMovement?.direction ?? whaleAlert?.direction)}</p>
                  </div>
                  <div className="page-card-muted px-4 py-3">
                    <p className="text-[11px] font-semibold uppercase tracking-[0.16em] text-[var(--text-muted)]">Threshold</p>
                    <p className="mt-1 text-lg font-semibold text-[var(--text-primary)]">
                      {formatBtc(whaleMovement?.threshold_btc ?? whaleAlert?.threshold_btc)} BTC
                    </p>
                  </div>
                  <div className="page-card-muted px-4 py-3">
                    <p className="text-[11px] font-semibold uppercase tracking-[0.16em] text-[var(--text-muted)]">Delta whale</p>
                    <p className={`mt-1 text-lg font-semibold ${changeTone(whaleMovement?.change_abs ?? whaleAlert?.change_abs)}`}>
                      {formatBtc(whaleMovement?.change_abs ?? whaleAlert?.change_abs)} BTC
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </section>
        </>
      )}
    </div>
  )
}
