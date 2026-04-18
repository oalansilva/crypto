import { useEffect, useMemo, useRef, useState } from 'react'
import { Activity, FlaskConical, RefreshCcw } from 'lucide-react'
import { useNavigate } from 'react-router-dom'

import { OnchainSignalCard, OnchainSignalCardSkeleton, type OnchainSignal } from '@/components/signals/OnchainSignalCard'
import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { Card, CardContent } from '@/components/ui/Card'
import { useToast } from '@/components/ui/use-toast'
import { apiUrl } from '@/lib/apiBase'
import './OnchainSignalsPage.css'

const HISTORY_LIMIT = 18
const MAX_LIVE_CARDS = 60
const CHAIN_OPTIONS = [
  { value: 'ALL', label: 'Todas as chains' },
  { value: 'ethereum', label: 'Ethereum' },
  { value: 'solana', label: 'Solana' },
  { value: 'arbitrum', label: 'Arbitrum' },
  { value: 'base', label: 'Base' },
  { value: 'matic', label: 'Matic' },
] as const

type OnchainHistoryItem = {
  token: string
  chain: string
  signal_type: 'BUY' | 'SELL' | 'HOLD'
  confidence: number
  breakdown: Partial<OnchainSignal['breakdown']>
  tvl: number | null
  active_addresses: number | null
  exchange_flow: number | null
  github_commits: number | null
  github_stars: number | null
  github_prs: number | null
  github_issues: number | null
  created_at: string
}

type OnchainHistoryResponse = {
  signals: OnchainHistoryItem[]
  total: number
  limit: number
  offset: number
}

type OnchainApiResponse = {
  signal: 'BUY' | 'SELL' | 'HOLD'
  confidence: number
  breakdown: Partial<OnchainSignal['breakdown']>
  metrics?: {
    token?: string
    chain?: string
    tvl?: number | string | null
    active_addresses?: number | string | null
    exchange_flow?: number | string | null
    github_commits?: number | string | null
    github_stars?: number | string | null
    github_prs?: number | string | null
    github_issues?: number | string | null
  }
  token?: string
  chain?: string
  tvl?: number | string | null
  active_addresses?: number | string | null
  exchange_flow?: number | string | null
  github_commits?: number | string | null
  github_stars?: number | string | null
  github_prs?: number | string | null
  github_issues?: number | string | null
  timestamp: string
}

type OnchainSnapshotResponse = {
  signals: OnchainApiResponse[]
  limit: number
  total: number
}

function pairKey(pair: { token: string; chain: string }) {
  return `${pair.token.toUpperCase()}::${pair.chain.toLowerCase()}`
}

function uniqueValues(values: string[]) {
  return Array.from(new Set(values.filter(Boolean)))
}

function toNumber(value: unknown): number | null {
  if (value === null || value === undefined || value === '') return null
  if (typeof value === 'number') {
    return Number.isFinite(value) ? value : null
  }
  if (typeof value === 'string') {
    const normalized = value.replace(/,/g, '').trim()
    if (!normalized) return null
    const parsed = Number(normalized)
    return Number.isFinite(parsed) ? parsed : null
  }
  return null
}

function normalizeBreakdown(breakdown: Partial<OnchainSignal['breakdown']>): OnchainSignal['breakdown'] {
  return {
    tvl: toNumber(breakdown.tvl) ?? 0,
    active_addresses: toNumber(breakdown.active_addresses) ?? 0,
    exchange_flow: toNumber(breakdown.exchange_flow) ?? 0,
    github_commits: toNumber(breakdown.github_commits) ?? 0,
    github_stars: toNumber(breakdown.github_stars) ?? 0,
    github_issues: toNumber(breakdown.github_issues) ?? 0,
  }
}

function mapHistorySignal(item: OnchainHistoryItem): OnchainSignal {
  return {
    token: item.token,
    chain: item.chain,
    signal: item.signal_type,
    confidence: item.confidence,
    breakdown: normalizeBreakdown(item.breakdown),
    metrics: {
      tvl: toNumber(item.tvl),
      active_addresses: toNumber(item.active_addresses),
      exchange_flow: toNumber(item.exchange_flow),
      github_commits: toNumber(item.github_commits),
      github_stars: toNumber(item.github_stars),
      github_prs: toNumber(item.github_prs),
      github_issues: toNumber(item.github_issues),
    },
    timestamp: item.created_at,
  }
}

function mapLiveSignal(payload: OnchainApiResponse): OnchainSignal {
  const metrics = payload.metrics ?? {}

  return {
    token: metrics.token ?? payload.token ?? '',
    chain: metrics.chain ?? payload.chain ?? '',
    signal: payload.signal,
    confidence: payload.confidence,
    breakdown: normalizeBreakdown(payload.breakdown),
    metrics: {
      tvl: toNumber(metrics.tvl ?? payload.tvl),
      active_addresses: toNumber(metrics.active_addresses ?? payload.active_addresses),
      exchange_flow: toNumber(metrics.exchange_flow ?? payload.exchange_flow),
      github_commits: toNumber(metrics.github_commits ?? payload.github_commits),
      github_stars: toNumber(metrics.github_stars ?? payload.github_stars),
      github_prs: toNumber(metrics.github_prs ?? payload.github_prs),
      github_issues: toNumber(metrics.github_issues ?? payload.github_issues),
    },
    timestamp: payload.timestamp,
  }
}

function isBreakdownEmpty(breakdown: OnchainSignal['breakdown']) {
  return Object.values(breakdown).every((value) => value === 0)
}

function mergeSignalMetrics(primary: OnchainSignal['metrics'], fallback: OnchainSignal['metrics']): OnchainSignal['metrics'] {
  return {
    tvl: primary.tvl ?? fallback.tvl,
    active_addresses: primary.active_addresses ?? fallback.active_addresses,
    exchange_flow: primary.exchange_flow ?? fallback.exchange_flow,
    github_commits: primary.github_commits ?? fallback.github_commits,
    github_stars: primary.github_stars ?? fallback.github_stars,
    github_prs: primary.github_prs ?? fallback.github_prs,
    github_issues: primary.github_issues ?? fallback.github_issues,
  }
}

function hydrateHistorySignals(history: OnchainSignal[], live: OnchainSignal[]) {
  const liveByPair = new Map(live.map((signal) => [pairKey(signal), signal]))

  return history.map((signal) => {
    const liveSignal = liveByPair.get(pairKey(signal))
    if (!liveSignal) return signal

    return {
      ...signal,
      breakdown: isBreakdownEmpty(signal.breakdown) ? liveSignal.breakdown : signal.breakdown,
      metrics: mergeSignalMetrics(signal.metrics, liveSignal.metrics),
    }
  })
}

async function fetchJson<T>(path: string, params: Record<string, string | number | undefined>) {
  const url = apiUrl(path)

  Object.entries(params).forEach(([key, value]) => {
    if (value === undefined || value === '') return
    url.searchParams.set(key, String(value))
  })

  const response = await fetch(url.toString(), {
    headers: { Accept: 'application/json' },
  })

  if (!response.ok) {
    throw new Error(`Falha ao carregar ${path} (${response.status})`)
  }

  return (await response.json()) as T
}

export default function OnchainSignalsPage() {
  const navigate = useNavigate()
  const { toast } = useToast()
  const requestIdRef = useRef(0)
  const hasLoadedRef = useRef(false)
  const [tokenFilter, setTokenFilter] = useState('ALL')
  const [chainFilter, setChainFilter] = useState<(typeof CHAIN_OPTIONS)[number]['value']>('ALL')
  const [confidenceMin, setConfidenceMin] = useState(40)
  const [liveSignals, setLiveSignals] = useState<OnchainSignal[]>([])
  const [historySignals, setHistorySignals] = useState<OnchainSignal[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [isRefreshing, setIsRefreshing] = useState(false)
  const [errorMessage, setErrorMessage] = useState<string | null>(null)
  const [refreshToken, setRefreshToken] = useState(0)

  const tokenOptions = useMemo(() => {
    const currentSelection = tokenFilter !== 'ALL' ? [tokenFilter] : []
    return uniqueValues([
      ...historySignals.map((item) => item.token),
      ...liveSignals.map((item) => item.token),
      ...currentSelection,
    ])
  }, [historySignals, liveSignals, tokenFilter])

  const filteredLiveSignals = useMemo(
    () => liveSignals.filter((item) => item.confidence >= confidenceMin),
    [confidenceMin, liveSignals],
  )

  const filteredHistorySignals = useMemo(
    () => historySignals.filter((item) => item.confidence >= confidenceMin).slice(0, 6),
    [confidenceMin, historySignals],
  )

  useEffect(() => {
    let cancelled = false
    const requestId = ++requestIdRef.current

    async function loadSignals() {
      const initialLoad = !hasLoadedRef.current

      if (initialLoad) {
        setIsLoading(true)
      } else {
        setIsRefreshing(true)
      }

      try {
        setErrorMessage(null)

        const [historyResponse, snapshotResponse] = await Promise.all([
          fetchJson<OnchainHistoryResponse>('/api/signals/onchain/history', {
            limit: HISTORY_LIMIT,
            offset: 0,
            token: tokenFilter !== 'ALL' ? tokenFilter : undefined,
            chain: chainFilter !== 'ALL' ? chainFilter : undefined,
          }),
          fetchJson<OnchainSnapshotResponse>('/api/signals/onchain/snapshot', {
            limit: MAX_LIVE_CARDS,
            token: tokenFilter !== 'ALL' ? tokenFilter : undefined,
            chain: chainFilter !== 'ALL' ? chainFilter : undefined,
          }),
        ])

        if (cancelled || requestId !== requestIdRef.current) return

        const mappedHistory = historyResponse.signals.map(mapHistorySignal)
        const mappedLive = snapshotResponse.signals.map(mapLiveSignal)

        setHistorySignals(hydrateHistorySignals(mappedHistory, mappedLive))
        setLiveSignals(mappedLive)
        hasLoadedRef.current = true
      } catch (error) {
        if (cancelled || requestId !== requestIdRef.current) return

        const message = error instanceof Error ? error.message : 'Falha ao carregar sinais onchain'
        setErrorMessage(message)
        toast({
          variant: 'destructive',
          title: 'Erro ao carregar sinais onchain',
          description: message,
        })
      } finally {
        if (!cancelled && requestId === requestIdRef.current) {
          setIsLoading(false)
          setIsRefreshing(false)
        }
      }
    }

    void loadSignals()

    return () => {
      cancelled = true
    }
  }, [chainFilter, refreshToken, toast, tokenFilter])

  return (
    <div className="app-page onchain-page">
      <header className="onchain-page__header">
        <div className="onchain-page__headline">
          <span className="onchain-page__eyebrow">Onchain Signals</span>
          <h1 className="onchain-page__title">Sinais Onchain</h1>
          <p className="onchain-page__copy">
            Snapshot de ate 60 pares Binance Spot + USDT, priorizados por liquidez, com TVL, GitHub e atividade on-chain no score.
          </p>
        </div>

        <div className="onchain-page__actions">
          {isRefreshing ? (
            <Badge variant="outline">Atualizando...</Badge>
          ) : null}
          <Button
            variant="ghost"
            onClick={() => navigate('/signals/onchain/backtest')}
            icon={<FlaskConical size={16} />}
          >
            Backtest
          </Button>
          <div className="onchain-page__status">
            <Activity size={15} />
            <span>{filteredLiveSignals.length} sinais ativos no grid</span>
          </div>
          <Button
            variant="secondary"
            onClick={() => setRefreshToken((current) => current + 1)}
            disabled={isRefreshing}
            icon={<RefreshCcw size={16} />}
          >
            Refresh
          </Button>
        </div>
      </header>

      <Card className="page-card-muted">
        <CardContent className="onchain-filters">
          <div className="onchain-filters__header">
            <div>
              <h2 className="onchain-filters__title">Filtros</h2>
              <p className="onchain-filters__copy">Selecione a chain, token e a confidence minima para o grid e o historico.</p>
            </div>
            <Button
              variant="ghost"
              onClick={() => {
                setTokenFilter('ALL')
                setChainFilter('ALL')
                setConfidenceMin(40)
              }}
            >
              Limpar
            </Button>
          </div>

          <div className="onchain-filters__grid">
            <label className="onchain-field">
              <span className="onchain-field__label">Chain</span>
              <select
                className="input onchain-field__select"
                value={chainFilter}
                onChange={(event) => setChainFilter(event.target.value as (typeof CHAIN_OPTIONS)[number]['value'])}
              >
                {CHAIN_OPTIONS.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </label>

            <label className="onchain-field">
              <span className="onchain-field__label">Token</span>
              <select className="input onchain-field__select" value={tokenFilter} onChange={(event) => setTokenFilter(event.target.value)}>
                <option value="ALL">Todos os tokens</option>
                {tokenOptions.map((token) => (
                  <option key={token} value={token}>
                    {token}
                  </option>
                ))}
              </select>
            </label>

            <label className="onchain-field">
              <span className="onchain-field__label">Confidence minima</span>
              <div className="onchain-field__range-wrap">
                <input
                  className="onchain-field__range"
                  type="range"
                  min={0}
                  max={100}
                  value={confidenceMin}
                  onChange={(event) => setConfidenceMin(Number(event.target.value))}
                />
                <div className="onchain-field__range-meta">
                  <span>Exibir apenas sinais acima do threshold.</span>
                  <span className="onchain-field__range-value">{confidenceMin}%</span>
                </div>
              </div>
            </label>
          </div>
        </CardContent>
      </Card>

      <div className="onchain-layout">
        <section className="onchain-section">
          <header className="onchain-section__header">
            <h2 className="onchain-section__title">Snapshot atual</h2>
            <p className="onchain-section__copy">Cards ranqueados pelo endpoint snapshot on-chain com filtro de volume/liquidez do mercado spot.</p>
          </header>

          {isLoading ? (
            <div className="onchain-grid">
              {Array.from({ length: 12 }).map((_, index) => (
                <OnchainSignalCardSkeleton key={`live-skeleton-${index}`} />
              ))}
            </div>
          ) : errorMessage && liveSignals.length === 0 ? (
            <Card className="onchain-state onchain-state--error">
              <CardContent>
                <div className="onchain-state__title">Nao foi possivel carregar os sinais onchain</div>
                <p className="onchain-state__copy">{errorMessage}</p>
              </CardContent>
            </Card>
          ) : filteredLiveSignals.length === 0 ? (
            <Card className="onchain-state">
              <CardContent>
                <div className="onchain-state__title">Nenhum sinal encontrado</div>
                <p className="onchain-state__copy">Ajuste os filtros ou reduza o threshold de confidence.</p>
              </CardContent>
            </Card>
          ) : (
            <div className="onchain-grid">
              {filteredLiveSignals.map((signal) => (
                <OnchainSignalCard key={`live-${pairKey(signal)}`} signal={signal} sourceLabel="Agora" />
              ))}
            </div>
          )}
        </section>

        <section className="onchain-section">
          <header className="onchain-section__header">
            <h2 className="onchain-section__title">Sinais recentes</h2>
            <p className="onchain-section__copy">Historico recente vindo de `/api/signals/onchain/history` para contexto e comparacao.</p>
          </header>

          {isLoading ? (
            <div className="onchain-grid">
              {Array.from({ length: 3 }).map((_, index) => (
                <OnchainSignalCardSkeleton key={`history-skeleton-${index}`} />
              ))}
            </div>
          ) : filteredHistorySignals.length === 0 ? (
            <Card className="onchain-state">
              <CardContent>
                <div className="onchain-state__title">Sem historico recente para estes filtros</div>
                <p className="onchain-state__copy">Assim que novos sinais forem gravados, eles aparecerao aqui.</p>
              </CardContent>
            </Card>
          ) : (
            <div className="onchain-grid">
              {filteredHistorySignals.map((signal, index) => (
                <OnchainSignalCard key={`history-${pairKey(signal)}-${index}`} signal={signal} sourceLabel="Historico" />
              ))}
            </div>
          )}
        </section>
      </div>
    </div>
  )
}
