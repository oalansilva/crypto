import { type FormEvent, useCallback, useEffect, useMemo, useState } from 'react'
import { Activity, CalendarClock, Gauge, Play, RefreshCw, Timer, Trash2 } from 'lucide-react'
import { Card, CardContent } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { useToast } from '@/components/ui/use-toast'
import { API_BASE_URL } from '@/lib/apiBase'
import { authFetch } from '@/lib/authFetch'

type BackfillJob = {
  job_id: string
  symbol: string
  timeframes: string[]
  status: string
  processed: number
  written: number
  duplicates: number
  attempts: number
  estimated_total: number | null
  percent: number
  eta_seconds: number | null
  requested_window: Record<string, unknown>
  provider: string | null
  requested_source: string | null
  page_size: number
  max_requests_per_minute: number
  last_error: string | null
  created_at: string | null
  updated_at: string | null
  finished_at: string | null
  current_timeframe: string | null
  current_lookback_to: string | null
  timeframe_states: Record<
    string,
    {
      status?: string
      processed?: number
      written?: number
      duplicates?: number
      estimated_total?: number
      retries?: number
      errors?: number
    }
  > | null
  events: Array<Record<string, unknown>>
}

type BackfillListResponse = {
  items: BackfillJob[]
  total: number
  page: number
  page_size: number
}

type StartBackfillPayload = {
  symbol: string
  timeframes: string[]
  data_source?: string
  history_window_years: number
  page_size: number
  max_requests_per_minute: number
}

const PAGE_SIZE = 20
const MIN_PAGE_SIZE = 100
const MAX_PAGE_SIZE = 5000
const MIN_RPM = 10
const MAX_RPM = 6000

function readErrorMessage(response: Response, fallback: string) {
  const payload = response.json().catch(() => null) as Promise<{
    detail?: string | string[]
  } | null>

  return payload.then((value) => {
    if (Array.isArray(value?.detail)) {
      return value.detail.join(', ')
    }
    if (typeof value?.detail === 'string' && value.detail.trim()) {
      return value.detail
    }
    return fallback
  })
}

function formatDate(value: string | null) {
  if (!value) return '—'
  const parsed = new Date(value)
  if (Number.isNaN(parsed.getTime())) return value
  return parsed.toLocaleString('pt-BR')
}

function formatEtaSeconds(value: number | null) {
  if (value === null || !Number.isFinite(value) || value <= 0) return '—'
  const total = Math.round(value)
  const hours = Math.floor(total / 3600)
  const minutes = Math.floor((total % 3600) / 60)
  const seconds = total % 60
  if (hours > 0) return `${hours}h ${minutes}m ${seconds}s`
  if (minutes > 0) return `${minutes}m ${seconds}s`
  return `${seconds}s`
}

function parseTimeframesInput(value: string) {
  const seen = new Set<string>()
  return value
    .split(',')
    .map((part) => part.trim().toLowerCase())
    .filter(Boolean)
    .filter((part) => {
      if (seen.has(part)) return false
      seen.add(part)
      return true
    })
}

function isIntegerInRange(value: number, min: number, max: number) {
  return Number.isFinite(value) && Number.isInteger(value) && value >= min && value <= max
}

function statusChipClass(status: string) {
  switch (status) {
    case 'completed':
      return 'border-emerald-500/30 bg-emerald-500/10 text-emerald-200'
    case 'running':
    case 'retrying':
      return 'border-sky-500/30 bg-sky-500/10 text-sky-200'
    case 'failed':
      return 'border-rose-500/30 bg-rose-500/10 text-rose-200'
    case 'cancelled':
      return 'border-orange-500/30 bg-orange-500/10 text-orange-200'
    case 'partial_complete':
      return 'border-amber-500/30 bg-amber-500/10 text-amber-200'
    default:
      return 'border-zinc-500/30 bg-zinc-500/10 text-zinc-200'
  }
}

export default function AdminBackfillPage() {
  const { toast } = useToast()

  const [jobs, setJobs] = useState<BackfillJob[]>([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [loading, setLoading] = useState(false)
  const [symbolFilter, setSymbolFilter] = useState('')
  const [statusFilter, setStatusFilter] = useState('')
  const [appliedSymbolFilter, setAppliedSymbolFilter] = useState('')
  const [appliedStatusFilter, setAppliedStatusFilter] = useState('')

  const [symbol, setSymbol] = useState('')
  const [timeframes, setTimeframes] = useState('1d')
  const [dataSource, setDataSource] = useState('')
  const [historyWindowYears, setHistoryWindowYears] = useState(2)
  const [batchSize, setBatchSize] = useState(1000)
  const [maxRpm, setMaxRpm] = useState(60)
  const [creating, setCreating] = useState(false)
  const [runningScheduler, setRunningScheduler] = useState(false)
  const [inFlight, setInFlight] = useState('')

  const totalPages = useMemo(() => Math.max(1, Math.ceil(total / PAGE_SIZE)), [total])

  const loadJobs = useCallback(async () => {
    setLoading(true)
    try {
      const params = new URLSearchParams()
      if (appliedStatusFilter) params.set('status', appliedStatusFilter)
      if (appliedSymbolFilter) params.set('symbol', appliedSymbolFilter)
      params.set('page', String(page))
      params.set('pageSize', String(PAGE_SIZE))

      const response = await authFetch(`${API_BASE_URL}/admin/backfill/jobs?${params.toString()}`)
      if (!response.ok) {
        throw new Error(await readErrorMessage(response, `Falha ao carregar jobs (${response.status})`))
      }
      const payload = (await response.json()) as BackfillListResponse
      setJobs(payload.items)
      setTotal(payload.total)
    } catch (error: unknown) {
      setJobs([])
      setTotal(0)
      if (error instanceof Error) {
        toast({ variant: 'destructive', title: 'Falha ao carregar backfill', description: error.message })
      }
    } finally {
      setLoading(false)
    }
  }, [appliedStatusFilter, appliedSymbolFilter, page, toast])

  useEffect(() => {
    loadJobs()
  }, [loadJobs])

  useEffect(() => {
    const interval = setInterval(loadJobs, 5000)
    return () => clearInterval(interval)
  }, [loadJobs])

  const handleApplyFilters = () => {
    setPage(1)
    setAppliedSymbolFilter(symbolFilter.trim().toUpperCase())
    setAppliedStatusFilter(statusFilter)
  }

  const handleClearFilters = () => {
    setSymbolFilter('')
    setStatusFilter('')
    setAppliedSymbolFilter('')
    setAppliedStatusFilter('')
    setPage(1)
  }

  const withActionState = async (
    actionKey: string,
    actionLabel: string,
    fn: () => Promise<void>,
  ) => {
    setInFlight(actionKey)
    try {
      await fn()
    } catch (error: unknown) {
      if (error instanceof Error) {
        toast({
          variant: 'destructive',
          title: `Falha ao ${actionLabel}`,
          description: error.message,
        })
      }
    } finally {
      setInFlight('')
    }
  }

  const handleCreate = async (event: FormEvent) => {
    event.preventDefault()
    const normalizedSymbol = symbol.trim().toUpperCase()
    if (!normalizedSymbol) {
      toast({ variant: 'destructive', title: 'Campo inválido', description: 'Informe o símbolo a ser processado.' })
      return
    }

    const parsedTimeframes = parseTimeframesInput(timeframes)
    if (parsedTimeframes.length === 0) {
      toast({
        variant: 'destructive',
        title: 'Campo inválido',
        description: 'Informe pelo menos 1 timeframe.',
      })
      return
    }

    if (!isIntegerInRange(batchSize, MIN_PAGE_SIZE, MAX_PAGE_SIZE)) {
      toast({
        variant: 'destructive',
        title: 'Campo inválido',
        description: `Page size deve estar entre ${MIN_PAGE_SIZE} e ${MAX_PAGE_SIZE}.`,
      })
      return
    }

    if (!isIntegerInRange(maxRpm, MIN_RPM, MAX_RPM)) {
      toast({
        variant: 'destructive',
        title: 'Campo inválido',
        description: `RPM deve estar entre ${MIN_RPM} e ${MAX_RPM}.`,
      })
      return
    }

    if (!isIntegerInRange(historyWindowYears, 1, 10)) {
      toast({
        variant: 'destructive',
        title: 'Campo inválido',
        description: 'Anos de histórico devem estar entre 1 e 10.',
      })
      return
    }

    setCreating(true)
    try {
      const payload: StartBackfillPayload = {
        symbol: normalizedSymbol,
        timeframes: parsedTimeframes,
        history_window_years: historyWindowYears,
        page_size: batchSize,
        max_requests_per_minute: maxRpm,
      }
      if (dataSource.trim()) {
        payload.data_source = dataSource.trim()
      }

      const response = await authFetch(`${API_BASE_URL}/admin/backfill/jobs`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      })
      if (!response.ok) {
        throw new Error(await readErrorMessage(response, `Falha ao iniciar backfill (${response.status})`))
      }
      toast({ title: 'Job iniciado', description: `Backfill para ${normalizedSymbol} foi enfileirado.` })
      await loadJobs()
      setSymbol('')
      setTimeframes('1d')
      setDataSource('')
      setHistoryWindowYears(2)
      setBatchSize(1000)
      setMaxRpm(60)
    } catch (error: unknown) {
      if (error instanceof Error) {
        toast({ variant: 'destructive', title: 'Erro ao iniciar backfill', description: error.message })
      }
    } finally {
      setCreating(false)
    }
  }

  const handleCancel = async (jobId: string) => {
    await withActionState(`cancel:${jobId}`, 'cancelar job', async () => {
      const response = await authFetch(`${API_BASE_URL}/admin/backfill/jobs/${jobId}/cancel`, { method: 'POST' })
      if (!response.ok) {
        throw new Error(await readErrorMessage(response, `Falha ao cancelar job (${response.status})`))
      }
      toast({ title: 'Cancelamento solicitado', description: `Job ${jobId} cancelado.` })
      await loadJobs()
    })
  }

  const handleRetry = async (jobId: string) => {
    await withActionState(`retry:${jobId}`, 'reiniciar job', async () => {
      const response = await authFetch(`${API_BASE_URL}/admin/backfill/jobs/${jobId}/retry`, { method: 'POST' })
      if (!response.ok) {
        throw new Error(await readErrorMessage(response, `Falha ao reenviar job (${response.status})`))
      }
      toast({ title: 'Retry solicitado', description: `Job ${jobId} reiniciado.` })
      await loadJobs()
    })
  }

  const handleRunScheduler = async () => {
    setRunningScheduler(true)
    try {
      const response = await authFetch(`${API_BASE_URL}/admin/backfill/scheduler/run-now`, { method: 'POST' })
      if (!response.ok) {
        throw new Error(await readErrorMessage(response, `Falha ao executar scheduler (${response.status})`))
      }
      const payload = (await response.json()) as { started: number }
      toast({
        title: 'Scheduler executado',
        description: `Jobs disparados agora: ${payload.started}.`,
      })
      await loadJobs()
    } catch (error: unknown) {
      if (error instanceof Error) {
        toast({ variant: 'destructive', title: 'Falha no scheduler', description: error.message })
      }
    } finally {
      setRunningScheduler(false)
    }
  }

  return (
    <div className="app-page space-y-6 pb-20">
      <section className="page-card p-6 sm:p-7 lg:p-8">
        <div className="flex flex-wrap items-start gap-4">
          <div className="flex h-14 w-14 items-center justify-center rounded-3xl border border-cyan-300/20 bg-[linear-gradient(135deg,rgba(56,189,248,0.18),rgba(16,185,129,0.12))]">
            <Activity className="h-6 w-6 text-cyan-200" />
          </div>
          <div>
            <div className="eyebrow">
              <span>Admin</span>
            </div>
            <h1 className="section-title mt-2">Backfill histórico de OHLCV</h1>
            <p className="section-copy mt-2">
              Inicie jobs de histórico, acompanhe progresso e gerencie cancelamentos/retries.
            </p>
          </div>
        </div>
      </section>

      <Card className="page-card border-white/8 bg-[linear-gradient(180deg,rgba(16,28,42,0.98),rgba(12,22,34,0.94))]">
        <CardContent className="p-6">
          <form onSubmit={handleCreate} className="space-y-4">
            <div className="flex flex-col gap-2">
              <h2 className="text-xl font-semibold text-[var(--text-primary)]">Novo job</h2>
              <p className="text-sm text-[var(--text-secondary)]">
                O job roda de forma assíncrona e registra progresso por timeframe.
              </p>
            </div>

            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              <div className="space-y-1.5">
                <label className="text-xs font-semibold uppercase tracking-[0.16em] text-[var(--text-muted)]">
                  Símbolo
                </label>
                <input
                  value={symbol}
                  onChange={(event) => setSymbol(event.target.value)}
                  placeholder="BTC/USDT"
                  className="w-full rounded-xl border border-[var(--border-default)] bg-[var(--bg-input)] px-4 py-3 text-sm text-[var(--text-primary)] transition focus:border-[var(--accent-primary)] focus:outline-none focus:ring-1 focus:ring-[var(--accent-primary)]"
                />
              </div>
              <div className="space-y-1.5">
                <label className="text-xs font-semibold uppercase tracking-[0.16em] text-[var(--text-muted)]">Timeframes</label>
                <input
                  value={timeframes}
                  onChange={(event) => setTimeframes(event.target.value)}
                  placeholder="1m,5m,1h,1d"
                  className="w-full rounded-xl border border-[var(--border-default)] bg-[var(--bg-input)] px-4 py-3 text-sm text-[var(--text-primary)] transition focus:border-[var(--accent-primary)] focus:outline-none focus:ring-1 focus:ring-[var(--accent-primary)]"
                />
              </div>
              <div className="space-y-1.5">
                <label className="text-xs font-semibold uppercase tracking-[0.16em] text-[var(--text-muted)]">
                  Fonte (opcional)
                </label>
                <input
                  value={dataSource}
                  onChange={(event) => setDataSource(event.target.value)}
                  placeholder="ccxt, stooq, yahoo"
                  className="w-full rounded-xl border border-[var(--border-default)] bg-[var(--bg-input)] px-4 py-3 text-sm text-[var(--text-primary)] transition focus:border-[var(--accent-primary)] focus:outline-none focus:ring-1 focus:ring-[var(--accent-primary)]"
                />
              </div>
              <div className="space-y-1.5">
                <label className="text-xs font-semibold uppercase tracking-[0.16em] text-[var(--text-muted)]">
                  Histórico (anos)
                </label>
                <input
                  type="number"
                  min={1}
                  max={10}
                  value={historyWindowYears}
                  onChange={(event) => setHistoryWindowYears(Number(event.target.value))}
                  className="w-full rounded-xl border border-[var(--border-default)] bg-[var(--bg-input)] px-4 py-3 text-sm text-[var(--text-primary)] transition focus:border-[var(--accent-primary)] focus:outline-none focus:ring-1 focus:ring-[var(--accent-primary)]"
                />
              </div>
              <div className="space-y-1.5">
                <label className="text-xs font-semibold uppercase tracking-[0.16em] text-[var(--text-muted)]">
                  Page size
                </label>
                <input
                  type="number"
                  min={MIN_PAGE_SIZE}
                  max={MAX_PAGE_SIZE}
                  value={batchSize}
                  onChange={(event) => setBatchSize(Number(event.target.value))}
                  className="w-full rounded-xl border border-[var(--border-default)] bg-[var(--bg-input)] px-4 py-3 text-sm text-[var(--text-primary)] transition focus:border-[var(--accent-primary)] focus:outline-none focus:ring-1 focus:ring-[var(--accent-primary)]"
                />
              </div>
              <div className="space-y-1.5">
                <label className="text-xs font-semibold uppercase tracking-[0.16em] text-[var(--text-muted)]">
                  RPM máx.
                </label>
                <input
                  type="number"
                  min={MIN_RPM}
                  max={MAX_RPM}
                  value={maxRpm}
                  onChange={(event) => setMaxRpm(Number(event.target.value))}
                  className="w-full rounded-xl border border-[var(--border-default)] bg-[var(--bg-input)] px-4 py-3 text-sm text-[var(--text-primary)] transition focus:border-[var(--accent-primary)] focus:outline-none focus:ring-1 focus:ring-[var(--accent-primary)]"
                />
              </div>
            </div>

            <div className="flex flex-wrap items-center gap-3">
              <Button type="submit" icon={<Play className="h-4 w-4" />} loading={creating}>
                Iniciar backfill
              </Button>
              <Button
                type="button"
                variant="secondary"
                icon={<RefreshCw className="h-4 w-4" />}
                loading={runningScheduler}
                onClick={handleRunScheduler}
              >
                Rodar scheduler agora
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>

      <Card className="page-card border-white/8 bg-[linear-gradient(180deg,rgba(16,28,42,0.98),rgba(12,22,34,0.94))]">
        <CardContent className="p-6">
          <div className="flex flex-col gap-4 md:flex-row md:items-end">
            <div className="space-y-1.5">
              <label className="text-xs font-semibold uppercase tracking-[0.16em] text-[var(--text-muted)]">Símbolo</label>
              <input
                value={symbolFilter}
                onChange={(event) => setSymbolFilter(event.target.value)}
                placeholder="Filtro por símbolo"
                className="w-full min-w-[220px] rounded-xl border border-[var(--border-default)] bg-[var(--bg-input)] px-4 py-2 text-sm text-[var(--text-primary)] transition focus:border-[var(--accent-primary)] focus:outline-none focus:ring-1 focus:ring-[var(--accent-primary)]"
              />
            </div>
            <div className="space-y-1.5">
              <label className="text-xs font-semibold uppercase tracking-[0.16em] text-[var(--text-muted)]">Status</label>
              <select
                value={statusFilter}
                onChange={(event) => setStatusFilter(event.target.value)}
                className="w-full min-w-[200px] rounded-xl border border-[var(--border-default)] bg-[var(--bg-input)] px-4 py-2 text-sm text-[var(--text-primary)]"
              >
                <option value="">Todos</option>
                <option value="pending">Pendente</option>
                <option value="running">Executando</option>
                <option value="retrying">Retry</option>
                <option value="completed">Concluído</option>
                <option value="partial_complete">Parcial</option>
                <option value="failed">Falhou</option>
                <option value="cancelled">Cancelado</option>
              </select>
            </div>
            <div className="flex gap-2">
              <Button variant="secondary" size="sm" onClick={handleApplyFilters}>
                Aplicar
              </Button>
              <Button variant="ghost" size="sm" onClick={handleClearFilters}>
                Limpar
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card className="page-card border-white/8 bg-[linear-gradient(180deg,rgba(16,28,42,0.98),rgba(12,22,34,0.94))]">
        <CardContent className="p-0">
          <div className="overflow-x-auto">
            <table className="w-full min-w-[950px] text-sm">
              <thead>
                <tr className="border-b border-white/10 bg-white/[0.02] text-left text-[var(--text-muted)]">
                  <th className="p-3 font-semibold">Símbolo</th>
                  <th className="p-3 font-semibold">Status</th>
                  <th className="p-3 font-semibold">Timeframes</th>
                  <th className="p-3 font-semibold">Progresso</th>
                  <th className="p-3 font-semibold">RPM / Batch</th>
                  <th className="p-3 font-semibold">Atualização</th>
                  <th className="p-3 font-semibold">Último erro</th>
                  <th className="p-3 font-semibold">Ações</th>
                </tr>
              </thead>
              <tbody>
                {!loading && jobs.length === 0 ? (
                  <tr>
                    <td className="p-4" colSpan={8}>Nenhum job encontrado.</td>
                  </tr>
                ) : (
                  jobs.map((job) => {
                    const percent = Number.isFinite(job.percent) ? job.percent : 0
                    const canCancel = ['pending', 'running', 'retrying'].includes(job.status)
                    const canRetry = ['failed', 'partial_complete', 'cancelled'].includes(job.status)
                    const timeframeText =
                      Object.entries(job.timeframe_states || {})
                        .map(([timeframe, state]) => `${timeframe}: ${state.status ?? '—'}`)
                        .join(' · ') || '—'
                    const isLoadingAction = (action: string) => inFlight === action
                    return (
                      <tr key={job.job_id} className="border-b border-white/6 align-top">
                        <td className="p-3">
                          <div className="font-medium text-[var(--text-primary)]">{job.symbol}</div>
                          <div className="text-xs text-[var(--text-muted)]">{job.job_id}</div>
                        </td>
                        <td className="p-3">
                          <span className={`inline-block rounded-full border px-2 py-1 text-[11px] font-semibold ${statusChipClass(job.status)}`}>
                            {job.status}
                          </span>
                        </td>
                        <td className="p-3">
                          <div className="text-xs text-[var(--text-secondary)]">{timeframeText}</div>
                          <div className="mt-2 flex flex-wrap gap-1.5">
                            {job.timeframes.map((timeframe) => (
                              <span key={timeframe} className="rounded-full border border-white/10 px-2 py-0.5 text-xs text-[var(--text-secondary)]">
                                {timeframe}
                              </span>
                            ))}
                          </div>
                        </td>
                        <td className="p-3">
                          <div className="space-y-2">
                            <div className="text-xs text-[var(--text-secondary)]">
                              {job.current_timeframe ? `Atual: ${job.current_timeframe}` : 'Aguardando'}
                            </div>
                            <div className="text-xs text-[var(--text-secondary)]">
                              {job.written}/{job.estimated_total ?? '—'} candles
                            </div>
                            <div className="h-2 w-full overflow-hidden rounded-full bg-white/10">
                              <div
                                className="h-full bg-[linear-gradient(90deg,rgba(56,189,248,0.9),rgba(16,185,129,0.9))]"
                                style={{ width: `${Math.min(100, Math.max(0, percent))}%` }}
                              />
                            </div>
                            <div className="text-xs text-[var(--text-muted)]">
                              {percent.toFixed(1)}% · ETA {formatEtaSeconds(job.eta_seconds)}
                            </div>
                          </div>
                        </td>
                        <td className="p-3">
                          <div className="text-xs text-[var(--text-secondary)]">
                            <span className="inline-flex items-center gap-1">
                              <Gauge className="h-3.5 w-3.5" />
                              {job.max_requests_per_minute} rpm
                            </span>
                          </div>
                          <div className="text-xs text-[var(--text-secondary)]">
                            <span className="inline-flex items-center gap-1">
                              <Timer className="h-3.5 w-3.5" />
                              {job.page_size} / lote
                            </span>
                          </div>
                        </td>
                        <td className="p-3">
                          <div className="space-y-1 text-xs text-[var(--text-secondary)]">
                            <div className="inline-flex items-center gap-1">
                              <CalendarClock className="h-3.5 w-3.5" />
                              <span>Atualizado: {formatDate(job.updated_at)}</span>
                            </div>
                            <div>Criado: {formatDate(job.created_at)}</div>
                            <div>Encerrado: {formatDate(job.finished_at)}</div>
                          </div>
                        </td>
                        <td className="max-w-[240px] p-3 text-xs text-[var(--text-secondary)]">
                          <div className="truncate" title={job.last_error || undefined}>
                            {job.last_error || '—'}
                          </div>
                          <div className="mt-1 text-[11px] text-[var(--text-muted)]">
                            Fonte: {job.provider || job.requested_source || 'auto'}
                          </div>
                        </td>
                        <td className="p-3">
                          <div className="flex flex-wrap gap-2">
                            <Button
                              size="sm"
                              variant="secondary"
                              icon={<Trash2 className="h-4 w-4" />}
                              loading={isLoadingAction(`cancel:${job.job_id}`)}
                              disabled={!canCancel}
                              onClick={() => handleCancel(job.job_id)}
                            >
                              Cancelar
                            </Button>
                            <Button
                              size="sm"
                              icon={<RefreshCw className="h-4 w-4" />}
                              loading={isLoadingAction(`retry:${job.job_id}`)}
                              disabled={!canRetry}
                              onClick={() => handleRetry(job.job_id)}
                            >
                              Retry
                            </Button>
                          </div>
                          {job.current_lookback_to ? (
                            <div className="mt-2 text-[11px] text-[var(--text-muted)]">Lookback: {formatDate(job.current_lookback_to)}</div>
                          ) : null}
                        </td>
                      </tr>
                    )
                  })
                )}
              </tbody>
            </table>
          </div>

          <div className="flex flex-wrap items-center justify-between border-t border-white/10 px-3 py-3 text-sm">
            <div className="text-[var(--text-secondary)]">
              Total: {total} jobs · Página {page} de {totalPages}
            </div>
            <div className="flex gap-2">
              <Button size="sm" disabled={loading || page <= 1} onClick={() => setPage((value) => Math.max(1, value - 1))}>
                <span>Anterior</span>
              </Button>
              <Button size="sm" disabled={loading || page >= totalPages} onClick={() => setPage((value) => Math.min(totalPages, value + 1))}>
                <span>Próxima</span>
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card className="page-card border-white/8 bg-[linear-gradient(180deg,rgba(16,28,42,0.98),rgba(12,22,34,0.94))]">
        <CardContent className="space-y-2 p-6">
          <h2 className="text-lg font-semibold text-[var(--text-primary)]">Observações úteis</h2>
          <ul className="list-inside list-disc space-y-1 text-sm text-[var(--text-secondary)]">
            <li>Status <strong>running</strong> e <strong>retrying</strong> representam processamento ativo.</li>
            <li><strong>partial_complete</strong> indica que o provedor retornou menos candles do esperado antes do fim da janela.</li>
            <li>Em caso de falha, o botão <strong>Retry</strong> tenta reexecutar o job a partir dos checkpoints salvos.</li>
          </ul>
        </CardContent>
      </Card>
    </div>
  )
}
