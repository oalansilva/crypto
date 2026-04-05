import { useEffect, useMemo, useRef, useState } from 'react'
import { Activity, FlaskConical, RefreshCcw } from 'lucide-react'
import { useNavigate } from 'react-router-dom'

import { OnchainSignalCard, OnchainSignalCardSkeleton, type OnchainSignal } from '@/components/signals/OnchainSignalCard'
import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { Card, CardContent } from '@/components/ui/Card'
import { useToast } from '@/components/ui/use-toast'
import './OnchainSignalsPage.css'

const API_BASE_URL = 'http://127.0.0.1:8003'
const HISTORY_LIMIT = 18
const MAX_LIVE_CARDS = 6
const CHAIN_OPTIONS = [
  { value: 'ALL', label: 'Todas as chains' },
  { value: 'ethereum', label: 'Ethereum' },
  { value: 'solana', label: 'Solana' },
  { value: 'arbitrum', label: 'Arbitrum' },
  { value: 'base', label: 'Base' },
  { value: 'matic', label: 'Matic' },
] as const
const DEFAULT_PAIRS = [
  { token: 'ETH', chain: 'ethereum' },
  { token: 'SOL', chain: 'solana' },
  { token: 'ARB', chain: 'arbitrum' },
  { token: 'BASE', chain: 'base' },
  { token: 'MATIC', chain: 'matic' },
]

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
  metrics: {
    token: string
    chain: string
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

type Pair = {
  token: string
  chain: string
}

function pairKey(pair: Pair) {
  return `${pair.token.toUpperCase()}::${pair.chain.toLowerCase()}`
}

function uniqueValues(values: string[]) {
  return Array.from(new Set(values.filter(Boolean)))
}

function normalizeBreakdown(breakdown: Partial<OnchainSignal['breakdown']>): OnchainSignal['breakdown'] {
  return {
    tvl: breakdown.tvl ?? 0,
    active_addresses: breakdown.active_addresses ?? 0,
    exchange_flow: breakdown.exchange_flow ?? 0,
    github_commits: breakdown.github_commits ?? 0,
    github_stars: breakdown.github_stars ?? 0,
    github_issues: breakdown.github_issues ?? 0,
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
      tvl: item.tvl,
      active_addresses: item.active_addresses,
      exchange_flow: item.exchange_flow,
      github_commits: item.github_commits,
      github_stars: item.github_stars,
      github_prs: item.github_prs,
      github_issues: item.github_issues,
    },
    timestamp: item.created_at,
  }
}

function mapLiveSignal(payload: OnchainApiResponse): OnchainSignal {
  return {
    token: payload.metrics.token,
    chain: payload.metrics.chain,
    signal: payload.signal,
    confidence: payload.confidence,
    breakdown: normalizeBreakdown(payload.breakdown),
    metrics: {
      tvl: payload.metrics.tvl,
      active_addresses: payload.metrics.active_addresses,
      exchange_flow: payload.metrics.exchange_flow,
      github_commits: payload.metrics.github_commits,
      github_stars: payload.metrics.github_stars,
      github_prs: payload.metrics.github_prs,
      github_issues: payload.metrics.github_issues,
    },
    timestamp: payload.timestamp,
  }
}

function resolvePairs(token: string, chain: string, historySignals: OnchainSignal[]): Pair[] {
  if (token !== 'ALL' && chain !== 'ALL') {
    return [{ token, chain }]
  }

  if (token !== 'ALL') {
    const chains = chain === 'ALL' ? CHAIN_OPTIONS.slice(1).map((item) => item.value) : [chain]
    return chains.map((chainValue) => ({ token, chain: chainValue }))
  }

  if (chain !== 'ALL') {
    const tokens = uniqueValues([
      ...historySignals.map((item) => item.token),
      ...DEFAULT_PAIRS.filter((item) => item.chain === chain).map((item) => item.token),
    ]).slice(0, MAX_LIVE_CARDS)
    return tokens.map((tokenValue) => ({ token: tokenValue, chain }))
  }

  const historyPairs = Array.from(
    new Map(historySignals.map((item) => [pairKey({ token: item.token, chain: item.chain }), { token: item.token, chain: item.chain }])).values(),
  )

  return (historyPairs.length > 0 ? historyPairs : DEFAULT_PAIRS).slice(0, MAX_LIVE_CARDS)
}

async function fetchJson<T>(path: string, params: Record<string, string | number | undefined>) {
  const url = new URL(path, API_BASE_URL)

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
      ...DEFAULT_PAIRS.map((item) => item.token),
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

        const historyResponse = await fetchJson<OnchainHistoryResponse>('/api/signals/onchain/history', {
          limit: HISTORY_LIMIT,
          offset: 0,
          token: tokenFilter !== 'ALL' ? tokenFilter : undefined,
          chain: chainFilter !== 'ALL' ? chainFilter : undefined,
        })

        if (cancelled || requestId !== requestIdRef.current) return

        const mappedHistory = historyResponse.signals.map(mapHistorySignal)
        const pairs = resolvePairs(tokenFilter, chainFilter, mappedHistory)

        const liveResults = await Promise.all(
          pairs.map(async (pair) => {
            try {
              const payload = await fetchJson<OnchainApiResponse>('/api/signals/onchain', pair)
              return mapLiveSignal(payload)
            } catch (error) {
              return null
            }
          }),
        )

        if (cancelled || requestId !== requestIdRef.current) return

        setHistorySignals(mappedHistory)
        setLiveSignals(liveResults.filter((item): item is OnchainSignal => item !== null))
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
        if (cancelled || requestId !== requestIdRef.current) return
        setIsLoading(false)
        setIsRefreshing(false)
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
            Leitura rapida de BUY, SELL e HOLD por chain, com confidence, drivers do score e historico recente para comparacao.
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
            <p className="onchain-section__copy">Cards consultados em tempo real no endpoint onchain por combinacao de token e chain.</p>
          </header>

          {isLoading ? (
            <div className="onchain-grid">
              {Array.from({ length: 6 }).map((_, index) => (
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
