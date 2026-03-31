import { useEffect, useMemo, useState } from 'react'
import { RefreshCcw } from 'lucide-react'
import { useQuery } from '@tanstack/react-query'

import { DisclaimerBanner } from '@/components/signals/DisclaimerBanner'
import { FilterBar } from '@/components/signals/FilterBar'
import { RiskProfileSelector } from '@/components/signals/RiskProfileSelector'
import { SignalCard, SignalCardSkeleton } from '@/components/signals/SignalCard'
import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { Card, CardContent } from '@/components/ui/Card'
import { apiUrl } from '@/lib/apiBase'
import { authFetch } from '@/lib/authFetch'
import { useToast } from '@/components/ui/use-toast'
import type { RiskProfile, SignalFilterType, SignalListResponse } from '@/types/signals'

const STORAGE_KEY = 'signals.riskProfile'
const DEFAULT_ASSETS = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT']
const INITIAL_LIMIT = 6

function defaultConfidenceForRiskProfile(profile: RiskProfile): number {
  switch (profile) {
    case 'conservative':
      return 75
    case 'aggressive':
      return 60
    case 'moderate':
    default:
      return 70
  }
}

function useDebouncedValue<T>(value: T, delay = 300) {
  const [debounced, setDebounced] = useState(value)

  useEffect(() => {
    const timer = window.setTimeout(() => setDebounced(value), delay)
    return () => window.clearTimeout(timer)
  }, [delay, value])

  return debounced
}

function readStoredRiskProfile(): RiskProfile {
  const raw = window.localStorage.getItem(STORAGE_KEY)
  if (raw === 'conservative' || raw === 'moderate' || raw === 'aggressive') {
    return raw
  }
  return 'moderate'
}

export default function SignalsPage() {
  const { toast } = useToast()
  const [riskProfile, setRiskProfile] = useState<RiskProfile>(() => readStoredRiskProfile())
  const [signalType, setSignalType] = useState<SignalFilterType>('ALL')
  const [asset, setAsset] = useState<string>('ALL')
  const [confidenceMin, setConfidenceMin] = useState<number>(() => defaultConfidenceForRiskProfile(readStoredRiskProfile()))
  const [limit, setLimit] = useState(INITIAL_LIMIT)

  const debouncedFilters = useDebouncedValue({ riskProfile, signalType, asset, confidenceMin, limit })

  useEffect(() => {
    window.localStorage.setItem(STORAGE_KEY, riskProfile)
  }, [riskProfile])

  useEffect(() => {
    setConfidenceMin(defaultConfidenceForRiskProfile(riskProfile))
  }, [riskProfile])

  useEffect(() => {
    setLimit(INITIAL_LIMIT)
  }, [riskProfile, signalType, asset, confidenceMin])

  const query = useQuery({
    queryKey: ['signals', debouncedFilters],
    queryFn: async () => {
      const url = apiUrl('/signals')
      url.searchParams.set('risk_profile', debouncedFilters.riskProfile)
      url.searchParams.set('confidence_min', String(debouncedFilters.confidenceMin))
      url.searchParams.set('limit', String(debouncedFilters.limit))
      if (debouncedFilters.signalType !== 'ALL') {
        url.searchParams.set('type', debouncedFilters.signalType)
      }
      if (debouncedFilters.asset !== 'ALL') {
        url.searchParams.set('asset', debouncedFilters.asset)
      }

      const response = await authFetch(url.toString())
      if (!response.ok) {
        throw new Error(`Falha ao carregar sinais (${response.status})`)
      }

      const data = (await response.json()) as SignalListResponse
      return {
        ...data,
        disclaimer: response.headers.get('x-disclaimer') || 'Isenção de responsabilidade: este não é advice financeiro.',
      }
    },
    placeholderData: (previousData) => previousData,
    retry: 2,
    refetchInterval: 60_000,
    refetchOnWindowFocus: false,
  })

  useEffect(() => {
    if (!query.error) return
    const message = query.error instanceof Error ? query.error.message : 'Falha ao carregar sinais'
    toast({
      variant: 'destructive',
      title: 'Erro ao carregar sinais',
      description: message,
    })
  }, [query.error, toast])

  const assets = useMemo(() => {
    const fromApi = query.data?.available_assets?.length ? query.data.available_assets : DEFAULT_ASSETS
    return [...new Set(fromApi)]
  }, [query.data?.available_assets])

  const hasMore = (query.data?.total || 0) >= limit && (asset === 'ALL' || (query.data?.signals.length || 0) > 0)
  const isStale = Boolean(
    query.data?.is_stale ||
      (query.data?.cached_at && Date.now() - new Date(query.data.cached_at).getTime() > 300_000),
  )

  return (
    <div className="app-page space-y-6 pb-20">
      <header className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-[var(--text-muted)]">Card #53</p>
          <h1 className="mt-2 text-3xl font-bold text-[var(--text-primary)]">Sinais de Trading</h1>
          <p className="mt-2 max-w-3xl text-sm text-[var(--text-secondary)]">
            Recomendações acionáveis de BUY e SELL com confidence gauge, target price, stop loss e filtros por risco.
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          {query.data?.cached_at ? (
            <Badge variant="secondary">Atualizado em {new Intl.DateTimeFormat('pt-BR', { dateStyle: 'short', timeStyle: 'short' }).format(new Date(query.data.cached_at))}</Badge>
          ) : null}
          {isStale ? <Badge variant="warning">Dados desatualizados</Badge> : null}
          {query.isFetching ? <Badge variant="outline">Atualizando…</Badge> : null}
        </div>
      </header>

      <RiskProfileSelector value={riskProfile} onChange={setRiskProfile} />

      <FilterBar
        signalType={signalType}
        asset={asset}
        confidenceMin={confidenceMin}
        assets={assets}
        onTypeChange={setSignalType}
        onAssetChange={setAsset}
        onConfidenceChange={(value) => setConfidenceMin(Math.max(0, Math.min(100, Number.isFinite(value) ? value : 0)))}
        onClear={() => {
          setSignalType('ALL')
          setAsset('ALL')
          setConfidenceMin(defaultConfidenceForRiskProfile(riskProfile))
        }}
      />

      {query.isLoading ? (
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3">
          {Array.from({ length: 6 }).map((_, index) => (
            <SignalCardSkeleton key={index} />
          ))}
        </div>
      ) : query.error && !query.data ? (
        <Card className="border-red-400/25 bg-red-500/8">
          <CardContent className="flex flex-col gap-4 p-6 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <h2 className="text-lg font-semibold text-red-100">Não foi possível carregar os sinais</h2>
              <p className="text-sm text-red-100/80">Verifique a API e tente novamente.</p>
            </div>
            <Button onClick={() => void query.refetch()} icon={<RefreshCcw className="h-4 w-4" />}>
              Tentar novamente
            </Button>
          </CardContent>
        </Card>
      ) : query.data && query.data.signals.length === 0 ? (
        <Card>
          <CardContent className="p-8 text-center">
            <h2 className="text-lg font-semibold text-[var(--text-primary)]">Nenhum sinal encontrado</h2>
            <p className="mt-2 text-sm text-[var(--text-secondary)]">Ajuste os filtros ou diminua a confidence mínima.</p>
          </CardContent>
        </Card>
      ) : (
        <>
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3">
            {query.data?.signals.map((signal) => (
              <SignalCard key={signal.id} signal={signal} />
            ))}
          </div>

          <div className="flex justify-center">
            <Button variant="secondary" onClick={() => setLimit((current) => current + INITIAL_LIMIT)} disabled={!hasMore || query.isFetching}>
              Ver mais sinais
            </Button>
          </div>
        </>
      )}

      <DisclaimerBanner text={query.data?.disclaimer} />
    </div>
  )
}
