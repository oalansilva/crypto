import { useEffect, useMemo, useRef, useState } from 'react'
import { ArrowLeft, BarChart3, Database, Download, FlaskConical, Play } from 'lucide-react'
import { useNavigate } from 'react-router-dom'

import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { Card, CardContent } from '@/components/ui/Card'
import { useToast } from '@/components/ui/use-toast'
import { apiUrl } from '@/lib/apiBase'
import './OnchainSignalsPage.css'
import './OnchainBacktestPage.css'

const HISTORY_LIMIT = 100
const CHAIN_OPTIONS = [
  { value: 'ALL', label: 'Todas as chains' },
  { value: 'ethereum', label: 'Ethereum' },
  { value: 'solana', label: 'Solana' },
  { value: 'arbitrum', label: 'Arbitrum' },
  { value: 'base', label: 'Base' },
  { value: 'matic', label: 'Matic' },
] as const

type OnchainHistoryItem = {
  id: string
  token: string
  chain: string
  signal_type: 'BUY' | 'SELL' | 'HOLD'
  confidence: number
  status: string
  created_at: string
  price_at_signal: number | null
  price_after_1h: number | null
  price_after_4h: number | null
  price_after_24h: number | null
}

type OnchainHistoryResponse = {
  signals: OnchainHistoryItem[]
  total: number
  limit: number
  offset: number
}

type OnchainPerformanceResponse = {
  total_signals: number
  win_rate: number
  avg_confidence: number
  expired_rate: number
  by_signal_type: Record<string, { count: number; avg_confidence: number }>
}

type BacktestFormState = {
  chain: (typeof CHAIN_OPTIONS)[number]['value']
  token: string
  startDate: string
  endDate: string
  confidenceThreshold: number
}

type EvaluatedSignal = OnchainHistoryItem & {
  outcome: 'WIN' | 'LOSS' | 'SKIPPED'
  simulatedReturnLabel: string
}

type BacktestResult = {
  totalPeriodSignals: number
  totalSignalsEvaluated: number
  winCount: number
  lossCount: number
  winRate: number
  avgWinningConfidence: number
  avgLosingConfidence: number
  rows: EvaluatedSignal[]
}

function average(values: number[]) {
  if (values.length === 0) return 0
  return values.reduce((sum, value) => sum + value, 0) / values.length
}

function formatDateInput(value: string) {
  if (!value) return ''
  return value.slice(0, 10)
}

function formatDateLabel(value: string) {
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return 'Data invalida'
  return new Intl.DateTimeFormat('pt-BR', {
    dateStyle: 'medium',
    timeStyle: 'short',
  }).format(date)
}

function formatPercent(value: number) {
  return `${value.toFixed(1)}%`
}

function normalizeToken(token: string) {
  return token.trim().toUpperCase()
}

async function fetchJson<T>(path: string) {
  const response = await fetch(apiUrl(path).toString(), {
    headers: { Accept: 'application/json' },
  })

  if (!response.ok) {
    throw new Error(`Falha ao carregar ${path} (${response.status})`)
  }

  return (await response.json()) as T
}

function computeBacktest(historySignals: OnchainHistoryItem[], filters: BacktestFormState): BacktestResult {
  const normalizedToken = normalizeToken(filters.token)
  const startAt = filters.startDate ? new Date(`${filters.startDate}T00:00:00Z`).getTime() : Number.NEGATIVE_INFINITY
  const endAt = filters.endDate ? new Date(`${filters.endDate}T23:59:59Z`).getTime() : Number.POSITIVE_INFINITY

  const filteredPeriodSignals = historySignals.filter((item) => {
    const itemTimestamp = new Date(item.created_at).getTime()
    if (Number.isNaN(itemTimestamp)) return false
    if (filters.chain !== 'ALL' && item.chain !== filters.chain) return false
    if (normalizedToken && item.token.toUpperCase() !== normalizedToken) return false
    if (item.confidence < filters.confidenceThreshold) return false
    return itemTimestamp >= startAt && itemTimestamp <= endAt
  })

  const rows = filteredPeriodSignals.map<EvaluatedSignal>((item) => {
    if (item.signal_type !== 'BUY') {
      return {
        ...item,
        outcome: 'SKIPPED',
        simulatedReturnLabel: 'N/A',
      }
    }

    const outcome = item.confidence > 70 ? 'WIN' : 'LOSS'

    return {
      ...item,
      outcome,
      simulatedReturnLabel: outcome === 'WIN' ? '+1 simulado' : '-1 simulado',
    }
  })

  const evaluatedRows = rows.filter((item) => item.outcome !== 'SKIPPED')
  const winningRows = evaluatedRows.filter((item) => item.outcome === 'WIN')
  const losingRows = evaluatedRows.filter((item) => item.outcome === 'LOSS')

  return {
    totalPeriodSignals: filteredPeriodSignals.length,
    totalSignalsEvaluated: evaluatedRows.length,
    winCount: winningRows.length,
    lossCount: losingRows.length,
    winRate: evaluatedRows.length > 0 ? (winningRows.length / evaluatedRows.length) * 100 : 0,
    avgWinningConfidence: average(winningRows.map((item) => item.confidence)),
    avgLosingConfidence: average(losingRows.map((item) => item.confidence)),
    rows,
  }
}

export default function OnchainBacktestPage() {
  const navigate = useNavigate()
  const { toast } = useToast()
  const initializedFiltersRef = useRef(false)
  const [historySignals, setHistorySignals] = useState<OnchainHistoryItem[]>([])
  const [performanceStats, setPerformanceStats] = useState<OnchainPerformanceResponse | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [isRunning, setIsRunning] = useState(false)
  const [errorMessage, setErrorMessage] = useState<string | null>(null)
  const [form, setForm] = useState<BacktestFormState>({
    chain: 'ALL',
    token: '',
    startDate: '',
    endDate: '',
    confidenceThreshold: 40,
  })
  const [appliedFilters, setAppliedFilters] = useState<BacktestFormState | null>(null)

  useEffect(() => {
    let cancelled = false

    async function loadData() {
      setIsLoading(true)

      try {
        setErrorMessage(null)

        const [historyResponse, performanceResponse] = await Promise.all([
          fetchJson<OnchainHistoryResponse>(`/api/signals/onchain/history?limit=${HISTORY_LIMIT}`),
          fetchJson<OnchainPerformanceResponse>('/api/signals/onchain/performance'),
        ])

        if (cancelled) return

        setHistorySignals(historyResponse.signals)
        setPerformanceStats(performanceResponse)

        if (!initializedFiltersRef.current && historyResponse.signals.length > 0) {
          const timestamps = historyResponse.signals
            .map((item) => item.created_at)
            .filter(Boolean)
            .sort((left, right) => new Date(left).getTime() - new Date(right).getTime())

          setForm((current) => ({
            ...current,
            startDate: formatDateInput(timestamps[0] ?? ''),
            endDate: formatDateInput(timestamps[timestamps.length - 1] ?? ''),
          }))
          initializedFiltersRef.current = true
        }
      } catch (error) {
        if (cancelled) return

        const message = error instanceof Error ? error.message : 'Falha ao carregar dados do backtest onchain'
        setErrorMessage(message)
        toast({
          variant: 'destructive',
          title: 'Erro ao carregar dashboard',
          description: message,
        })
      } finally {
        if (!cancelled) {
          setIsLoading(false)
        }
      }
    }

    void loadData()

    return () => {
      cancelled = true
    }
  }, [toast])

  const tokenSuggestions = useMemo(
    () => Array.from(new Set(historySignals.map((item) => item.token.toUpperCase()).filter(Boolean))).sort(),
    [historySignals],
  )

  const results = useMemo(() => {
    if (!appliedFilters) return null
    return computeBacktest(historySignals, appliedFilters)
  }, [appliedFilters, historySignals])

  const winBarWidth = results && results.totalSignalsEvaluated > 0 ? (results.winCount / results.totalSignalsEvaluated) * 100 : 0
  const lossBarWidth = results && results.totalSignalsEvaluated > 0 ? (results.lossCount / results.totalSignalsEvaluated) * 100 : 0

  function updateForm<K extends keyof BacktestFormState>(key: K, value: BacktestFormState[K]) {
    setForm((current) => ({ ...current, [key]: value }))
  }

  function handleRunBacktest() {
    if (form.startDate && form.endDate && form.startDate > form.endDate) {
      toast({
        variant: 'destructive',
        title: 'Periodo invalido',
        description: 'A data inicial precisa ser anterior ou igual a data final.',
      })
      return
    }

    setIsRunning(true)
    setAppliedFilters({ ...form, token: normalizeToken(form.token) })
    window.requestAnimationFrame(() => setIsRunning(false))
  }

  function handleExportCsv() {
    if (!results || results.rows.length === 0) return

    const lines = [
      ['token', 'chain', 'signal_type', 'confidence', 'created_at', 'outcome', 'simulated_return'],
      ...results.rows.map((row) => [
        row.token,
        row.chain,
        row.signal_type,
        String(row.confidence),
        row.created_at,
        row.outcome,
        row.simulatedReturnLabel,
      ]),
    ]

    const csv = lines
      .map((line) => line.map((cell) => `"${String(cell).replaceAll('"', '""')}"`).join(','))
      .join('\n')

    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = 'onchain-backtest-results.csv'
    link.click()
    URL.revokeObjectURL(url)
  }

  return (
    <div className="app-page onchain-backtest-page">
      <header className="onchain-page__header">
        <div className="onchain-page__headline">
          <span className="onchain-page__eyebrow">Onchain Signals</span>
          <h1 className="onchain-page__title">Backtesting Dashboard</h1>
          <p className="onchain-page__copy">
            Simulacao client-side usando o historico onchain. Regra simplificada: apenas sinais BUY entram no backtest e BUY com confidence acima de 70 sao tratados como win.
          </p>
        </div>

        <div className="onchain-page__actions">
          <Button variant="ghost" onClick={() => navigate('/signals/onchain')} icon={<ArrowLeft size={16} />}>
            Voltar aos sinais
          </Button>
          {performanceStats ? (
            <div className="onchain-page__status">
              <Database size={15} />
              <span>{performanceStats.total_signals} sinais na base</span>
            </div>
          ) : null}
          <div className="onchain-page__status">
            <BarChart3 size={15} />
            <span>{results ? `${results.totalSignalsEvaluated} BUYs avaliados` : 'Configure e rode o backtest'}</span>
          </div>
        </div>
      </header>

      <Card className="page-card-muted">
        <CardContent className="onchain-backtest-filters">
          <div className="onchain-filters__header">
            <div>
              <h2 className="onchain-filters__title">Parametros do backtest</h2>
              <p className="onchain-filters__copy">Filtre o historico localmente e rode a simulacao sem depender de um endpoint dedicado.</p>
            </div>
            <Badge variant="outline">History limit: {HISTORY_LIMIT}</Badge>
          </div>

          <div className="onchain-backtest-grid">
            <label className="onchain-field">
              <span className="onchain-field__label">Chain</span>
              <select className="input onchain-field__select" value={form.chain} onChange={(event) => updateForm('chain', event.target.value as BacktestFormState['chain'])}>
                {CHAIN_OPTIONS.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </label>

            <label className="onchain-field">
              <span className="onchain-field__label">Token</span>
              <input
                className="input"
                list="onchain-backtest-token-suggestions"
                placeholder="ETH, SOL, ARB..."
                value={form.token}
                onChange={(event) => updateForm('token', event.target.value.toUpperCase())}
              />
              <datalist id="onchain-backtest-token-suggestions">
                {tokenSuggestions.map((token) => (
                  <option key={token} value={token} />
                ))}
              </datalist>
            </label>

            <label className="onchain-field">
              <span className="onchain-field__label">Data inicial</span>
              <input className="input" type="date" value={form.startDate} onChange={(event) => updateForm('startDate', event.target.value)} />
            </label>

            <label className="onchain-field">
              <span className="onchain-field__label">Data final</span>
              <input className="input" type="date" value={form.endDate} onChange={(event) => updateForm('endDate', event.target.value)} />
            </label>

            <label className="onchain-field onchain-backtest-grid__threshold">
              <span className="onchain-field__label">Confidence minima</span>
              <div className="onchain-field__range-wrap">
                <input
                  className="onchain-field__range"
                  type="range"
                  min={0}
                  max={100}
                  value={form.confidenceThreshold}
                  onChange={(event) => updateForm('confidenceThreshold', Number(event.target.value))}
                />
                <div className="onchain-field__range-meta">
                  <span>Threshold minimo para incluir sinais no periodo.</span>
                  <span className="onchain-field__range-value">{form.confidenceThreshold}%</span>
                </div>
              </div>
            </label>
          </div>

          <div className="onchain-backtest-filters__actions">
            <Button variant="secondary" onClick={handleRunBacktest} loading={isRunning || isLoading} icon={<Play size={16} />}>
              Run Backtest
            </Button>
            <Button variant="ghost" onClick={handleExportCsv} disabled={!results || results.rows.length === 0} icon={<Download size={16} />}>
              Exportar CSV
            </Button>
          </div>
        </CardContent>
      </Card>

      {errorMessage && !isLoading ? (
        <Card className="onchain-state onchain-state--error">
          <CardContent>
            <div className="onchain-state__title">Nao foi possivel carregar a base do backtest</div>
            <p className="onchain-state__copy">{errorMessage}</p>
          </CardContent>
        </Card>
      ) : null}

      <div className="onchain-backtest-layout">
        <section className="onchain-section">
          <header className="onchain-section__header">
            <h2 className="onchain-section__title">Resumo da simulacao</h2>
            <p className="onchain-section__copy">
              Resultado calculado no frontend sobre o intervalo filtrado. SELL e HOLD aparecem na tabela, mas nao contam como trades avaliados.
            </p>
          </header>

          <div className="onchain-backtest-summary">
            <Card className="onchain-card onchain-backtest-stat">
              <CardContent className="onchain-backtest-stat__content">
                <span className="onchain-backtest-stat__label">Sinais no periodo</span>
                <strong className="onchain-backtest-stat__value">{results?.totalPeriodSignals ?? 0}</strong>
              </CardContent>
            </Card>

            <Card className="onchain-card onchain-backtest-stat">
              <CardContent className="onchain-backtest-stat__content">
                <span className="onchain-backtest-stat__label">Total avaliado</span>
                <strong className="onchain-backtest-stat__value">{results?.totalSignalsEvaluated ?? 0}</strong>
              </CardContent>
            </Card>

            <Card className="onchain-card onchain-backtest-stat">
              <CardContent className="onchain-backtest-stat__content">
                <span className="onchain-backtest-stat__label">Win rate</span>
                <strong className="onchain-backtest-stat__value">{results ? formatPercent(results.winRate) : '0.0%'}</strong>
              </CardContent>
            </Card>

            <Card className="onchain-card onchain-backtest-stat">
              <CardContent className="onchain-backtest-stat__content">
                <span className="onchain-backtest-stat__label">Confidence media</span>
                <strong className="onchain-backtest-stat__value">
                  {results ? `${formatPercent(results.avgWinningConfidence)} / ${formatPercent(results.avgLosingConfidence)}` : '0.0% / 0.0%'}
                </strong>
                <span className="onchain-backtest-stat__hint">wins / losses</span>
              </CardContent>
            </Card>
          </div>
        </section>

        <section className="onchain-backtest-panels">
          <Card className="onchain-card onchain-backtest-chart">
            <CardContent className="onchain-backtest-chart__content">
              <div className="onchain-backtest-chart__header">
                <div>
                  <h3 className="onchain-section__title">Win vs loss</h3>
                  <p className="onchain-section__copy">Barra CSS-only com base nos BUYs avaliados.</p>
                </div>
                <FlaskConical size={18} className="onchain-backtest-chart__icon" />
              </div>

              <div className="onchain-backtest-chart__bar" aria-hidden="true">
                <div className="onchain-backtest-chart__segment onchain-backtest-chart__segment--win" style={{ width: `${winBarWidth}%` }} />
                <div className="onchain-backtest-chart__segment onchain-backtest-chart__segment--loss" style={{ width: `${lossBarWidth}%` }} />
              </div>

              <div className="onchain-backtest-chart__legend">
                <div className="onchain-backtest-chart__legend-item">
                  <span className="onchain-backtest-chart__dot onchain-backtest-chart__dot--win" />
                  <span>Wins: {results?.winCount ?? 0}</span>
                </div>
                <div className="onchain-backtest-chart__legend-item">
                  <span className="onchain-backtest-chart__dot onchain-backtest-chart__dot--loss" />
                  <span>Losses: {results?.lossCount ?? 0}</span>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="onchain-card onchain-backtest-chart">
            <CardContent className="onchain-backtest-chart__content">
              <div className="onchain-backtest-chart__header">
                <div>
                  <h3 className="onchain-section__title">Contexto da API</h3>
                  <p className="onchain-section__copy">Metricas agregadas do endpoint `/api/signals/onchain/performance`.</p>
                </div>
                <Database size={18} className="onchain-backtest-chart__icon" />
              </div>

              <div className="onchain-backtest-context">
                <div className="onchain-backtest-context__item">
                  <span>Win rate global</span>
                  <strong>{performanceStats ? formatPercent(performanceStats.win_rate) : '0.0%'}</strong>
                </div>
                <div className="onchain-backtest-context__item">
                  <span>Confidence media global</span>
                  <strong>{performanceStats ? formatPercent(performanceStats.avg_confidence) : '0.0%'}</strong>
                </div>
                <div className="onchain-backtest-context__item">
                  <span>Expired rate</span>
                  <strong>{performanceStats ? formatPercent(performanceStats.expired_rate) : '0.0%'}</strong>
                </div>
              </div>
            </CardContent>
          </Card>
        </section>

        <section className="onchain-section">
          <header className="onchain-section__header">
            <h2 className="onchain-section__title">Historico avaliado</h2>
            <p className="onchain-section__copy">Lista detalhada dos sinais encontrados no periodo filtrado e seu outcome simulado.</p>
          </header>

          {!results ? (
            <Card className="onchain-state">
              <CardContent>
                <div className="onchain-state__title">Nenhum backtest executado ainda</div>
                <p className="onchain-state__copy">Preencha os filtros e clique em "Run Backtest" para gerar os resultados.</p>
              </CardContent>
            </Card>
          ) : results.rows.length === 0 ? (
            <Card className="onchain-state">
              <CardContent>
                <div className="onchain-state__title">Sem sinais para o periodo selecionado</div>
                <p className="onchain-state__copy">Ajuste chain, token, datas ou threshold para ampliar a amostra.</p>
              </CardContent>
            </Card>
          ) : (
            <Card className="onchain-card">
              <CardContent className="onchain-backtest-table__wrap">
                <table className="onchain-backtest-table">
                  <thead>
                    <tr>
                      <th>Token</th>
                      <th>Chain</th>
                      <th>Sinal</th>
                      <th>Confidence</th>
                      <th>Data</th>
                      <th>Outcome</th>
                      <th>Simulacao</th>
                    </tr>
                  </thead>
                  <tbody>
                    {results.rows.map((row) => (
                      <tr key={row.id}>
                        <td>{row.token}</td>
                        <td className="onchain-backtest-table__cell--caps">{row.chain}</td>
                        <td>{row.signal_type}</td>
                        <td>{formatPercent(row.confidence)}</td>
                        <td>{formatDateLabel(row.created_at)}</td>
                        <td>
                          <span className={`onchain-backtest-outcome onchain-backtest-outcome--${row.outcome.toLowerCase()}`}>{row.outcome}</span>
                        </td>
                        <td>{row.simulatedReturnLabel}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </CardContent>
            </Card>
          )}
        </section>
      </div>
    </div>
  )
}
