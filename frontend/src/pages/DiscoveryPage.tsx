import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Check, ChevronLeft, ChevronRight, Copy, History, Pause, Play, RefreshCw,
  Shield, Square, Star, X,
} from 'lucide-react'
import { authFetch } from '../lib/authFetch'
import { API_BASE_URL } from '../lib/apiBase'
import './DiscoveryPage.css'

type PreflightResult = {
  axes: { templates: string[]; symbols: string[]; timeframes: string[]; directions: string[] }
  raw_total: number
  exclusions: Record<string, { reasons: string[] }>
  excluded_count: number
  valid_total: number
  limits: { max_total: number }
  errors: Record<string, string>
  expires_at: string
  snapshot_token: string
  snapshot_hash: string
}

type SweepState =
  | 'pending' | 'running' | 'paused' | 'cancelling'
  | 'cancelled' | 'failed' | 'partial_failure' | 'completed'

type Sweep = {
  sweep_id: string
  state: SweepState
  total: number
  succeeded: number
  failed: number
  skipped: number
  processed: number
  terminal_reason: string | null
  terminal_code: string | null
  snapshot: PreflightResult | null
}

type HistoryRun = {
  sweep_id: string
  state: SweepState
  total: number
  processed: number
  succeeded: number
  failed: number
  skipped: number
  snapshot_hash: string | null
  created_at: string | null
}

type LeaderboardRow = {
  rank: number | null
  result_id: string
  template_id: string
  symbol: string
  timeframe: string
  direction: string
  calmar_ratio: number | null
  cagr: number | null
  benchmark_cagr: number | null
  delta_cagr_vs_bh: number | null
  max_drawdown: number | null
  sharpe_ratio: number | null
  profit_factor: number | null
  win_rate: number | null
  trades_count: number | null
  coverage: number | null
  eligibility: string
  eligibility_reason: string | null
  dedup_state: string
  dedup_reference: string | null
  start_at: string | null
  end_at: string | null
  candle_source: string | null
  candle_version: string | null
  expected_candles: number | null
  observed_valid_candles: number | null
  parameters?: Record<string, unknown>
  fees_slippage: { fees?: number; slippage?: number; fee_pct?: number; slippage_pct?: number } | null
}

type Metric = 'calmar_ratio' | 'delta_cagr_vs_bh'

const TERMINAL = new Set<SweepState>(['cancelled', 'failed', 'partial_failure', 'completed'])
const PAGE_SIZE = 3
const AXIS_PAGE_SIZE = 4
const idempotencyKey = (prefix: string, value: string) => `${prefix}-${value}`.slice(0, 64)
const STATE_LABEL: Record<SweepState, string> = {
  pending: 'pendente', running: 'em execução', paused: 'pausada', cancelling: 'cancelando',
  cancelled: 'cancelada', failed: 'falhou', partial_failure: 'falha parcial', completed: 'concluída',
}

function fmtNum(v: number | null | undefined, digits = 2): string {
  if (v === null || v === undefined || Number.isNaN(v) || !Number.isFinite(v)) return 'N/A'
  return v.toLocaleString('pt-BR', { minimumFractionDigits: digits, maximumFractionDigits: digits })
}
function fmtPct(v: number | null | undefined): string {
  if (v === null || v === undefined || Number.isNaN(v) || !Number.isFinite(v)) return 'N/A'
  const percentage = Math.abs(v) <= 1 ? v * 100 : v
  return `${percentage.toLocaleString('pt-BR', { maximumFractionDigits: 1 })}%`
}
function fmtPp(v: number | null | undefined): string {
  if (v === null || v === undefined || Number.isNaN(v) || !Number.isFinite(v)) return 'N/A'
  const sign = v >= 0 ? '+' : '−'
  return `${sign}${Math.abs(v).toLocaleString('pt-BR', { maximumFractionDigits: 1 })} p.p.`
}
function fmtDrawdown(v: number | null | undefined): string {
  if (v === null || v === undefined || Number.isNaN(v) || !Number.isFinite(v)) return 'N/A'
  const percentage = Math.abs(v) <= 1 ? Math.abs(v) * 100 : Math.abs(v)
  return `−${percentage.toLocaleString('pt-BR', { maximumFractionDigits: 1 })}%`
}
function fmtParams(parameters: Record<string, unknown> | undefined): string {
  if (!parameters) return ''
  return Object.entries(parameters)
    .slice(0, 2)
    .map(([key, value]) => `${key} ${String(value)}`)
    .join(' · ')
}
function fmtEstimate(valid: number): string {
  if (!valid) return '—'
  const minutes = valid * 2
  return minutes >= 60 ? `~${Math.floor(minutes / 60)}h ${minutes % 60}min` : `~${minutes}min`
}
function fmtDate(iso: string | null): string {
  if (!iso) return '—'
  const d = new Date(iso)
  return d.toLocaleDateString('pt-BR', { day: '2-digit', month: 'short', year: 'numeric' })
}
function snapshotLabel(hash: string | null | undefined, total: number | null | undefined): string {
  if (!hash) return '—'
  return `#PF-${hash.replace(/[^a-zA-Z0-9]/g, '').slice(0, 4).toUpperCase()}-${total ?? '—'}`
}
function errorDetail(data: unknown, fallback: string): string {
  if (data && typeof data === 'object') {
    const d = (data as Record<string, unknown>).detail
    if (typeof d === 'string') return d
    if (d && typeof d === 'object') return JSON.stringify(d)
  }
  return fallback
}

export function DiscoveryPage() {
  const navigate = useNavigate()

  // Catálogos
  const [templates, setTemplates] = useState<{ name: string; description: string }[]>([])
  const [symbols, setSymbols] = useState<string[]>([])
  // Seleção
  const [selectedTemplates, setSelectedTemplates] = useState<string[]>([])
  const [selectedSymbols, setSelectedSymbols] = useState<string[]>([])
  const [timeframes, setTimeframes] = useState<string[]>(['4h', '1d'])
  const [directions, setDirections] = useState<string[]>(['long', 'short'])
  const [period, setPeriod] = useState<'6m' | '2y' | 'all'>('2y')
  const [draftMetric, setDraftMetric] = useState<Metric>('calmar_ratio')
  const [metric, setMetric] = useState<Metric>('calmar_ratio')
  // Busca dos eixos
  const [templateSearch, setTemplateSearch] = useState('')
  const [symbolSearch, setSymbolSearch] = useState('')
  const [templatePage, setTemplatePage] = useState(1)
  const [symbolPage, setSymbolPage] = useState(1)
  // Preflight
  const [preflight, setPreflight] = useState<PreflightResult | null>(null)
  const [preflightLoading, setPreflightLoading] = useState(false)
  const [preflightError, setPreflightError] = useState<string | null>(null)
  const [snapshotStale, setSnapshotStale] = useState(false)
  const [draftFrozen, setDraftFrozen] = useState(false)
  // Sweep ativo e run histórico exibido permanecem separados, como no protótipo.
  const [activeSweep, setActiveSweep] = useState<Sweep | null>(null)
  const [viewSweep, setViewSweep] = useState<Sweep | null>(null)
  const [history, setHistory] = useState<HistoryRun[]>([])
  const [busy, setBusy] = useState(false)
  // Leaderboard
  const [rows, setRows] = useState<LeaderboardRow[]>([])
  const [totalMatched, setTotalMatched] = useState(0)
  const [totalAvailable, setTotalAvailable] = useState(0)
  const [lbLoading, setLbLoading] = useState(false)
  const [lbError, setLbError] = useState(false)
  const [page, setPage] = useState(1)
  const [fSymbol, setFSymbol] = useState('all')
  const [fTimeframe, setFTimeframe] = useState('all')
  const [fDirection, setFDirection] = useState('all')
  // Modal / toast / estados críticos
  const [promoteTarget, setPromoteTarget] = useState<LeaderboardRow | null>(null)
  const [promoteConflict, setPromoteConflict] = useState<string | null>(null)
  const [promotedFocusId, setPromotedFocusId] = useState<string | null>(null)
  const [promoting, setPromoting] = useState(false)
  const [toast, setToast] = useState<{ title: string; copy: string } | null>(null)
  const [permissionDenied, setPermissionDenied] = useState(false)
  const [cancelConfirmOpen, setCancelConfirmOpen] = useState(false)
  const [historyOpen, setHistoryOpen] = useState(false)

  const pollRef = useRef<number | null>(null)
  const preflightTimer = useRef<number | null>(null)
  const toastTimer = useRef<number | null>(null)
  const modalRef = useRef<HTMLDivElement | null>(null)
  const promotionTriggerRef = useRef<HTMLButtonElement | null>(null)
  const progressHeadingRef = useRef<HTMLSpanElement | null>(null)
  const previousActiveStateRef = useRef<SweepState | null>(null)

  const visibleTemplates = useMemo(
    () => templates.filter((t) => `${t.description} ${t.name}`.toLowerCase().includes(templateSearch.toLowerCase())),
    [templates, templateSearch],
  )
  const visibleSymbols = useMemo(
    () => symbols.filter((s) => s.toLowerCase().includes(symbolSearch.toLowerCase())),
    [symbols, symbolSearch],
  )
  const templatePages = Math.max(1, Math.ceil(visibleTemplates.length / AXIS_PAGE_SIZE))
  const symbolPages = Math.max(1, Math.ceil(visibleSymbols.length / AXIS_PAGE_SIZE))
  const pagedTemplates = visibleTemplates.slice((templatePage - 1) * AXIS_PAGE_SIZE, templatePage * AXIS_PAGE_SIZE)
  const pagedSymbols = visibleSymbols.slice((symbolPage - 1) * AXIS_PAGE_SIZE, symbolPage * AXIS_PAGE_SIZE)

  useEffect(() => setTemplatePage(1), [templateSearch])
  useEffect(() => setSymbolPage(1), [symbolSearch])

  const showToast = useCallback((title: string, copy: string) => {
    setToast({ title, copy })
    if (toastTimer.current !== null) window.clearTimeout(toastTimer.current)
    toastTimer.current = window.setTimeout(() => setToast(null), 5000)
  }, [])

  // ---------- Catálogos ----------
  useEffect(() => {
    void (async () => {
      try {
        const res = await authFetch(`${API_BASE_URL}/combos/templates`)
        if (!res.ok) return
        const data = await res.json()
        const flat = [
          ...(data.prebuilt || []),
          ...(data.examples || []),
          ...(data.custom || []),
        ].map((t: { name?: string; description?: string }) => ({
          name: String(t.name ?? ''),
          description: String(t.description ?? ''),
        }))
        setTemplates(flat)
        setSelectedTemplates(flat.slice(0, 3).map((t) => t.name))
      } catch {
        /* catálogo auxiliar */
      }
    })()
  }, [])

  useEffect(() => {
    void (async () => {
      try {
        const res = await fetch(`${API_BASE_URL}/exchanges/binance/symbols`)
        if (!res.ok) return
        const data = await res.json()
        const list: string[] = data.symbols || []
        setSymbols(list)
        setSelectedSymbols(list.slice(0, 4))
      } catch {
        /* catálogo auxiliar */
      }
    })()
  }, [])

  // ---------- Histórico ----------
  const loadHistory = useCallback(async () => {
    try {
      const res = await authFetch(`${API_BASE_URL}/combos/discovery/sweeps/history`)
      if (res.ok) {
        const data = await res.json()
        setHistory(data.sweeps || [])
      }
    } catch {
      /* histórico é auxiliar */
    }
  }, [])

  useEffect(() => {
    void loadHistory()
  }, [loadHistory])

  // ---------- Preflight (auto, com debounce) ----------
  const runPreflight = useCallback(async () => {
    if (draftFrozen) return
    if (selectedTemplates.length === 0 || selectedSymbols.length === 0 || timeframes.length === 0 || directions.length === 0) {
      setPreflight(null)
      setSnapshotStale(false)
      return
    }
    setPreflightLoading(true)
    setPreflightError(null)
    setSnapshotStale(false)
    try {
      const res = await authFetch(`${API_BASE_URL}/combos/discovery/sweeps/preflight`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          templates: selectedTemplates,
          symbols: selectedSymbols,
          timeframes,
          directions,
          period_type: period,
        }),
      })
      const data = await res.json()
      if (!res.ok) {
        setPreflightError(errorDetail(data, 'Falha no preflight'))
        setPreflight(null)
        return
      }
      setPreflight(data)
    } catch (e: unknown) {
      setPreflightError(e instanceof Error ? e.message : 'Erro no preflight')
      setPreflight(null)
    } finally {
      setPreflightLoading(false)
    }
  }, [draftFrozen, selectedTemplates, selectedSymbols, timeframes, directions, period])

  useEffect(() => {
    if (draftFrozen) return
    if (preflightTimer.current !== null) window.clearTimeout(preflightTimer.current)
    preflightTimer.current = window.setTimeout(() => void runPreflight(), 450)
    return () => {
      if (preflightTimer.current !== null) window.clearTimeout(preflightTimer.current)
    }
  }, [selectedTemplates, selectedSymbols, timeframes, directions, period, draftFrozen, runPreflight])

  const axisCount = selectedTemplates.length * selectedSymbols.length * timeframes.length * directions.length
  const overLimit = Boolean(preflight?.errors?.total)
  const canStart =
    preflight !== null &&
    Object.keys(preflight.errors || {}).length === 0 &&
    !draftFrozen &&
    !snapshotStale

  const toggleList = (list: string[], setList: (v: string[]) => void, value: string) =>
    setList(list.includes(value) ? list.filter((x) => x !== value) : [...list, value])
  const toggleVisible = (visible: string[], list: string[], setList: (v: string[]) => void) => {
    const all = visible.every((v) => list.includes(v))
    const next = new Set(list)
    visible.forEach((v) => (all ? next.delete(v) : next.add(v)))
    setList([...next])
  }

  // ---------- Sweep ----------
  const startSweep = useCallback(async () => {
    if (!preflight) return
    setBusy(true)
    setSnapshotStale(false)
    try {
      const res = await authFetch(`${API_BASE_URL}/combos/discovery/sweeps`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          templates: selectedTemplates,
          symbols: selectedSymbols,
          timeframes,
          directions,
          period_type: period,
          snapshot_token: preflight.snapshot_token,
          snapshot_hash: preflight.snapshot_hash,
          idempotency_key: idempotencyKey('sweep', preflight.snapshot_hash),
        }),
      })
      const data = await res.json()
      if (!res.ok) {
        if (res.status === 403) {
          setPermissionDenied(true)
          return
        }
        const detail = errorDetail(data, 'Falha ao iniciar varredura')
        if (res.status === 409 && /mudaram|expirado|inválido/i.test(detail)) {
          setSnapshotStale(true)
        }
        showToast('Falha ao iniciar', detail)
        return
      }
      const detailRes = await authFetch(`${API_BASE_URL}/combos/discovery/sweeps/${data.sweep_id}`)
      const fullSweep: Sweep = detailRes.ok
        ? await detailRes.json()
        : {
            sweep_id: data.sweep_id,
            state: data.state,
            total: data.total ?? preflight.valid_total,
            succeeded: 0,
            failed: 0,
            skipped: 0,
            processed: 0,
            terminal_reason: null,
            terminal_code: null,
            snapshot: preflight,
          }
      setActiveSweep(fullSweep)
      if (!viewSweep) setViewSweep(fullSweep)
      setMetric(draftMetric)
      setDraftFrozen(true)
      setPage(1)
      if (!viewSweep) {
        setRows([])
        setTotalMatched(0)
        setTotalAvailable(0)
      }
      showToast('Varredura iniciada', 'Sweep criado; progresso atualiza automaticamente.')
      void loadHistory()
    } finally {
      setBusy(false)
    }
  }, [preflight, selectedTemplates, selectedSymbols, timeframes, directions, period, draftMetric, loadHistory, showToast, viewSweep])

  const loadLeaderboard = useCallback(
    async (sweepId: string, m: Metric, symbol: string, timeframe: string, direction: string, pg: number, silent = false) => {
      if (!silent) setLbLoading(true)
      setLbError(false)
      try {
        const params = new URLSearchParams({
          metric: m,
          offset: String((pg - 1) * PAGE_SIZE),
          limit: String(PAGE_SIZE),
        })
        if (symbol !== 'all') params.set('symbol', symbol)
        if (timeframe !== 'all') params.set('timeframe', timeframe)
        if (direction !== 'all') params.set('direction', direction)
        const res = await authFetch(
          `${API_BASE_URL}/combos/discovery/sweeps/${sweepId}/leaderboard?${params.toString()}`,
        )
        if (!res.ok) {
          if (res.status === 403) {
            setPermissionDenied(true)
            return
          }
          setLbError(true)
          return
        }
        const data = await res.json()
        setRows(data.results || [])
        setTotalMatched(data.total || 0)
        setTotalAvailable(data.unfiltered_total ?? data.total ?? 0)
      } catch {
        setLbError(true)
      } finally {
        setLbLoading(false)
      }
    },
    [],
  )

  const refreshSweep = useCallback(async () => {
    if (!activeSweep) return
    try {
      const res = await authFetch(`${API_BASE_URL}/combos/discovery/sweeps/${activeSweep.sweep_id}`)
      if (!res.ok) {
        if (res.status === 403) setPermissionDenied(true)
        return
      }
      const data = await res.json()
      setActiveSweep(data)
      if (TERMINAL.has(data.state)) {
        setViewSweep(data)
        setFSymbol('all')
        setFTimeframe('all')
        setFDirection('all')
        setPage(1)
        await loadLeaderboard(data.sweep_id, metric, 'all', 'all', 'all', 1, true)
        void loadHistory()
      }
    } catch {
      /* poll continua */
    }
  }, [activeSweep, metric, loadLeaderboard, loadHistory])

  useEffect(() => {
    if (!activeSweep || TERMINAL.has(activeSweep.state)) {
      if (pollRef.current !== null) {
        window.clearInterval(pollRef.current)
        pollRef.current = null
      }
      return
    }
    pollRef.current = window.setInterval(() => void refreshSweep(), 2000)
    return () => {
      if (pollRef.current !== null) {
        window.clearInterval(pollRef.current)
        pollRef.current = null
      }
    }
  }, [activeSweep, refreshSweep])

  const command = useCallback(
    async (cmd: 'pause' | 'resume' | 'cancel') => {
      if (!activeSweep) return
      setCancelConfirmOpen(false)
      const res = await authFetch(`${API_BASE_URL}/combos/discovery/sweeps/${activeSweep.sweep_id}/${cmd}`, {
        method: 'POST',
      })
      if (!res.ok) {
        if (res.status === 403) {
          setPermissionDenied(true)
          return
        }
        const data = await res.json().catch(() => null)
        showToast('Comando falhou', errorDetail(data, `Falha em ${cmd}`))
        return
      }
      void refreshSweep()
    },
    [activeSweep, refreshSweep, showToast],
  )

  const selectHistory = useCallback(
    async (sweepId: string) => {
      setBusy(true)
      setPromoteTarget(null)
      setCancelConfirmOpen(false)
      try {
        const res = await authFetch(`${API_BASE_URL}/combos/discovery/sweeps/${sweepId}`)
        if (!res.ok) {
          if (res.status === 403) setPermissionDenied(true)
          return
        }
        const data = await res.json()
        setViewSweep(data)
        setFSymbol('all')
        setFTimeframe('all')
        setFDirection('all')
        setPage(1)
        await loadLeaderboard(sweepId, metric, 'all', 'all', 'all', 1)
      } finally {
        setBusy(false)
      }
    },
    [metric, loadLeaderboard],
  )

  const newDraft = useCallback(() => {
    setDraftFrozen(false)
    setCancelConfirmOpen(false)
    showToast('Novo rascunho', 'Sweep ativo preservado no histórico; configurador liberado.')
  }, [showToast])

  useEffect(() => {
    if (!viewSweep && history.length > 0) {
      void selectHistory(history[0].sweep_id)
    }
  }, [history, viewSweep, selectHistory])

  // Filtros / paginação do leaderboard
  const applyFilters = useCallback(
    (m: Metric, symbol: string, timeframe: string, direction: string, pg: number) => {
      if (!viewSweep) return
      void loadLeaderboard(viewSweep.sweep_id, m, symbol, timeframe, direction, pg)
    },
    [viewSweep, loadLeaderboard],
  )

  const handleSortChange = (m: Metric) => {
    setMetric(m)
    setPage(1)
    applyFilters(m, fSymbol, fTimeframe, fDirection, 1)
  }
  const handleFilterChange = (key: 'symbol' | 'timeframe' | 'direction', value: string) => {
    const updaters = {
      symbol: setFSymbol,
      timeframe: setFTimeframe,
      direction: setFDirection,
    }
    updaters[key](value)
    const next = { symbol: fSymbol, timeframe: fTimeframe, direction: fDirection, ...{ [key]: value } }
    setPage(1)
    applyFilters(metric, next.symbol, next.timeframe, next.direction, 1)
  }
  const clearFilters = () => {
    setFSymbol('all')
    setFTimeframe('all')
    setFDirection('all')
    setPage(1)
    applyFilters(metric, 'all', 'all', 'all', 1)
  }
  const goPage = (pg: number) => {
    setPage(pg)
    applyFilters(metric, fSymbol, fTimeframe, fDirection, pg)
  }

  // ---------- Promoção ----------
  const closePromotion = useCallback((returnFocus = true) => {
    setPromoteConflict(null)
    setPromoteTarget(null)
    if (returnFocus) {
      window.setTimeout(() => promotionTriggerRef.current?.focus(), 0)
    }
  }, [])

  const promote = useCallback(async () => {
    if (!promoteTarget) return
    setPromoting(true)
    setPromoteConflict(null)
    try {
      const res = await authFetch(
        `${API_BASE_URL}/combos/discovery/results/${promoteTarget.result_id}/promote`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ tier: 3, idempotency_key: idempotencyKey('promote', promoteTarget.result_id) }),
        },
      )
      const data = await res.json().catch(() => null)
      if (!res.ok) {
        if (res.status === 403) {
          setPermissionDenied(true)
          return
        }
        if (res.status === 409) {
          const reference =
            (data && typeof data === 'object' && (data as Record<string, unknown>).reference) ||
            promoteTarget.dedup_reference
          setPromoteConflict(reference ? String(reference) : 'estratégia equivalente já promovida')
          return
        }
        showToast('Falha na promoção', errorDetail(data, 'Não foi possível promover.'))
        return
      }
      const fid = data && typeof data === 'object' ? (data as Record<string, unknown>).favorite_id : null
      setRows((prev) =>
        prev.map((r) =>
          r.result_id === promoteTarget.result_id
            ? { ...r, dedup_state: 'already_promoted', dedup_reference: fid ? String(fid) : r.dedup_reference }
            : r,
        ),
      )
      const promotedId = promoteTarget.result_id
      setPromotedFocusId(promotedId)
      closePromotion(false)
      showToast(
        'Candidato promovido.',
        `Favorito tier 3 criado${fid ? ` (${String(fid)})` : ''} com origem #${viewSweep?.sweep_id ?? '—'}.`,
      )
    } finally {
      setPromoting(false)
    }
  }, [promoteTarget, showToast, closePromotion, viewSweep])

  useEffect(() => {
    if (!promotedFocusId) return
    const timer = window.setTimeout(() => {
      document.querySelector<HTMLElement>(`[data-promoted-result="${promotedFocusId}"]`)?.focus()
      setPromotedFocusId(null)
    }, 0)
    return () => window.clearTimeout(timer)
  }, [promotedFocusId, rows])

  // Focus trap do modal
  useEffect(() => {
    if (!promoteTarget) return
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        e.preventDefault()
        closePromotion(true)
        return
      }
      if (e.key === 'Tab' && modalRef.current) {
        const focusables = modalRef.current.querySelectorAll<HTMLElement>('button:not(:disabled), [href]')
        const first = focusables[0]
        const last = focusables[focusables.length - 1]
        if (e.shiftKey && document.activeElement === first) {
          e.preventDefault()
          last?.focus()
        } else if (!e.shiftKey && document.activeElement === last) {
          e.preventDefault()
          first?.focus()
        }
      }
    }
    document.addEventListener('keydown', onKey, true)
    const t = window.setTimeout(() => modalRef.current?.querySelector<HTMLElement>('#confirm-promotion')?.focus(), 30)
    return () => {
      document.removeEventListener('keydown', onKey, true)
      window.clearTimeout(t)
    }
  }, [promoteTarget, closePromotion])

  useEffect(() => {
    const previous = previousActiveStateRef.current
    if (activeSweep && previous && !TERMINAL.has(previous) && TERMINAL.has(activeSweep.state)) {
      window.setTimeout(() => progressHeadingRef.current?.focus(), 0)
    }
    previousActiveStateRef.current = activeSweep?.state ?? null
  }, [activeSweep])

  // Cabeçalho do leaderboard (janela/candles/fees) derivado da primeira linha elegível
  const evidence = useMemo(() => {
    const row = rows.find((r) => r.eligibility === 'eligible') ?? rows[0]
    if (!row) return null
    const fee = row.fees_slippage?.fee_pct ?? row.fees_slippage?.fees
    const slippage = row.fees_slippage?.slippage_pct ?? row.fees_slippage?.slippage
    return {
      start: fmtDate(row.start_at),
      end: fmtDate(row.end_at),
      candles: `${row.observed_valid_candles ?? '—'}/${row.expected_candles ?? '—'} candles ${row.candle_source ?? '—'}${row.candle_version ? ` v${row.candle_version}` : ''}`,
      fees: fee != null ? `fees ${fmtPct(fee)}` : '',
      slippage: slippage != null ? `slippage ${fmtPct(slippage)}` : '',
    }
  }, [rows])

  const totalPages = Math.max(1, Math.ceil(totalMatched / PAGE_SIZE))
  const running = activeSweep !== null && !TERMINAL.has(activeSweep.state)
  const symbolOptions = useMemo(() => {
    const fromSnapshot = viewSweep?.snapshot?.axes?.symbols ?? preflight?.axes?.symbols ?? []
    const fromRows = [...new Set(rows.map((r) => r.symbol))]
    const merged = [...new Set([...fromSnapshot, ...fromRows])]
    return merged.length ? merged : symbols
  }, [preflight, viewSweep, rows, symbols])
  const activeSnapshotHash = activeSweep?.snapshot?.snapshot_hash ?? preflight?.snapshot_hash ?? null
  const periodLabel = { '6m': '6 meses', '2y': '2 anos', all: 'Todo histórico' }[period]

  return (
    <div className="min-h-screen text-[var(--text-primary)]">
      <div className="mx-auto max-w-[1480px] px-4 py-6 md:px-8 md:py-8">
        {/* Breadcrumb */}
        <nav className="mb-3 flex items-center gap-2 text-sm text-[var(--text-tertiary)]" aria-label="Localização">
          <span>Combo</span>
          <span aria-hidden="true">/</span>
          <strong className="font-semibold text-[var(--text-secondary)]">Varreduras</strong>
        </nav>

        {/* Page heading */}
        <div className="mb-5 flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
          <div>
            <h1 className="text-2xl font-semibold tracking-tight md:text-3xl">Descoberta de estratégias swing</h1>
            <p className="mt-2 max-w-[72ch] text-sm text-[var(--text-tertiary)]">
              Compare templates em 4h e 1d. Preflight, ranking e promoção usam evidência histórica;
              nenhum candidato é salvo sem revisão.
            </p>
          </div>
          <button
            type="button"
            onClick={() => setHistoryOpen((v) => !v)}
            aria-expanded={historyOpen}
            aria-controls="history-panel"
            data-testid="history-button"
            className="inline-flex min-h-[44px] items-center justify-center gap-2 rounded-md border border-[var(--border-default)] bg-[var(--bg-elevated)] px-3.5 py-2.5 text-sm font-semibold text-[var(--text-secondary)] hover:bg-[#262b33]"
          >
            <History className="h-4 w-4" />
            Histórico de varreduras
          </button>
        </div>

        {/* History panel */}
        {historyOpen ? (
          <section
            id="history-panel"
            aria-labelledby="history-label"
            className="mb-5 flex flex-col gap-3 rounded-lg border border-[var(--border-default)] bg-[var(--bg-secondary)] p-4 md:flex-row md:items-end"
          >
            <label className="flex-1">
              <span id="history-label" className="mb-2 block text-sm font-semibold text-[var(--text-secondary)]">
                Run exibido no leaderboard
              </span>
              <select
                value={viewSweep?.sweep_id ?? ''}
                onChange={(e) => {
                  if (e.target.value) void selectHistory(e.target.value)
                }}
                data-testid="run-selector"
                disabled={busy}
                className="w-full rounded-md border border-[var(--border-default)] bg-[var(--bg-input)] px-3 py-2 text-sm text-[var(--text-primary)]"
              >
                {history.map((h) => (
                  <option key={h.sweep_id} value={h.sweep_id}>
                    #{h.sweep_id} · {STATE_LABEL[h.state]} · {h.total} combinações
                  </option>
                ))}
              </select>
            </label>
            {(() => {
              const current = history.find((h) => h.sweep_id === viewSweep?.sweep_id)
              if (!current) return null
              return (
                <p className="text-xs text-[var(--text-tertiary)] md:pb-1">
                  Snapshot {snapshotLabel(current.snapshot_hash, current.total)} · {current.total} válidas
                  {' · '}{current.succeeded} sucesso · {current.failed} falhas · {STATE_LABEL[current.state]}.
                  {' '}Separado do sweep ativo.
                </p>
              )
            })()}
          </section>
        ) : null}

        {/* Toast */}
        {toast ? (
          <div
            role="status"
            className="fixed bottom-6 right-6 z-[70] flex max-w-[min(420px,calc(100vw-32px))] items-start gap-2.5 rounded-lg border border-[rgba(252,213,53,0.35)] bg-[var(--bg-elevated)] px-3.5 py-3 text-sm text-[var(--text-secondary)] shadow-2xl"
          >
            <Check className="mt-0.5 h-4 w-4 shrink-0 text-[var(--accent-primary)]" />
            <div>
              <strong className="block">{toast.title}</strong>
              <div className="text-xs text-[var(--text-tertiary)]">{toast.copy}</div>
            </div>
          </div>
        ) : null}

        {/* Permission denied */}
        {permissionDenied ? (
          <section className="mb-5 rounded-lg border border-[rgba(246,70,93,0.4)] bg-[rgba(246,70,93,0.06)] p-4">
            <h2 className="text-base font-semibold">Permissão negada (403)</h2>
            <p className="mt-1 text-sm text-[var(--text-tertiary)]">
              Sua sessão não tem autorização administrativa para operar varreduras.
            </p>
            <button
              type="button"
              onClick={() => navigate('/combo/configure')}
              className="mt-3 inline-flex min-h-[44px] items-center justify-center gap-2 rounded-md border border-[var(--border-default)] bg-[var(--bg-elevated)] px-4 py-2 text-sm font-semibold text-[var(--text-secondary)]"
            >
              Voltar ao Combo
            </button>
          </section>
        ) : null}

        {/* Config layout */}
        <section className="grid grid-cols-1 items-start gap-4 lg:grid-cols-[minmax(0,1fr)_330px]" aria-label="Novo rascunho de varredura">
          <article className="rounded-xl border border-[var(--border-default)] bg-[var(--bg-elevated)]">
            <div className="flex items-start justify-between gap-4 border-b border-[var(--border-default)] px-5 py-4">
              <div>
                <h2 className="text-lg font-semibold">Rascunho de varredura</h2>
                <p id="draft-status" className="mt-1 text-xs text-[var(--text-tertiary)]">
                  {draftFrozen ? 'Congelado pelo snapshot ativo' : 'Editável · preflight server-side atualizado'}
                </p>
              </div>
              <span className="inline-flex min-h-[28px] items-center rounded border border-[rgba(59,130,246,0.42)] px-2 py-1 text-[11px] font-bold text-[#93c5fd]">
                {draftFrozen ? 'CONGELADO' : 'RASCUNHO'}
              </span>
            </div>

            <div className="grid grid-cols-1 gap-x-6 gap-y-5 p-5 md:grid-cols-2">
              {/* Templates */}
              <fieldset disabled={draftFrozen} className="min-w-0 border-0 p-0">
                <legend className="mb-2 block text-[13px] font-semibold text-[var(--text-secondary)]">Templates</legend>
                <p className="mb-2 text-xs text-[var(--text-muted)]" aria-live="polite" data-testid="template-count">
                  {selectedTemplates.length} de {templates.length} selecionados · {pagedTemplates.length} visíveis
                </p>
                <div className="mb-2 grid grid-cols-[1fr_auto] gap-2">
                  <input
                    type="search"
                    value={templateSearch}
                    onChange={(e) => setTemplateSearch(e.target.value)}
                    placeholder="Buscar template"
                    aria-label="Buscar template"
                    className="w-full rounded-md border border-[var(--border-default)] bg-[var(--bg-input)] px-2.5 py-2 text-sm text-[var(--text-primary)]"
                  />
                  <button
                    type="button"
                    onClick={() => toggleVisible(pagedTemplates.map((t) => t.name), selectedTemplates, setSelectedTemplates)}
                    className="min-h-[44px] rounded-md border border-[var(--border-default)] bg-[var(--bg-input)] px-2.5 text-xs font-semibold text-[var(--text-secondary)]"
                  >
                    Selecionar visíveis
                  </button>
                </div>
                <div className="grid grid-cols-1 gap-2 sm:grid-cols-2">
                  {visibleTemplates.length === 0 ? (
                    <p className="text-xs text-[var(--text-muted)]">Nenhum template encontrado.</p>
                  ) : null}
                  {pagedTemplates.map((t) => (
                    <label
                      key={t.name}
                      className={`flex min-h-[46px] items-start gap-2.5 rounded-lg border border-[var(--border-default)] bg-[var(--bg-secondary)] px-2.5 py-2.5 text-sm text-[var(--text-secondary)] ${
                        selectedTemplates.includes(t.name) ? 'border-[rgba(252,213,53,0.45)] bg-[rgba(252,213,53,0.07)]' : ''
                      }`}
                    >
                      <input
                        type="checkbox"
                        className="mt-0.5 h-[17px] w-[17px] min-h-[17px] accent-[var(--accent-primary)]"
                        checked={selectedTemplates.includes(t.name)}
                        onChange={() => toggleList(selectedTemplates, setSelectedTemplates, t.name)}
                      />
                      <span className="min-w-0">
                        <b className="block truncate text-[13px] font-semibold text-[var(--text-secondary)]">{t.description || t.name}</b>
                        <small className="block text-[11px] text-[var(--text-muted)]">{t.name}</small>
                      </span>
                    </label>
                  ))}
                </div>
                {templatePages > 1 ? (
                  <div className="mt-2 flex items-center justify-between text-xs text-[var(--text-tertiary)]">
                    <button
                      type="button"
                      disabled={templatePage <= 1}
                      onClick={() => setTemplatePage((p) => Math.max(1, p - 1))}
                      className="min-h-[44px] rounded-md border border-[var(--border-default)] bg-[var(--bg-secondary)] px-3 disabled:opacity-40"
                    >
                      Anterior
                    </button>
                    <span>Página {templatePage} de {templatePages}</span>
                    <button
                      type="button"
                      disabled={templatePage >= templatePages}
                      onClick={() => setTemplatePage((p) => Math.min(templatePages, p + 1))}
                      className="min-h-[44px] rounded-md border border-[var(--border-default)] bg-[var(--bg-secondary)] px-3 disabled:opacity-40"
                    >
                      Próxima
                    </button>
                  </div>
                ) : null}
                <p className={`mt-2 min-h-[18px] text-[11px] ${selectedTemplates.length ? 'text-[#93c5fd]' : 'text-[#fbbf24]'}`} data-testid="template-axis-status">
                  {selectedTemplates.length ? '' : 'Selecione ao menos um template.'}
                </p>
              </fieldset>

              {/* Símbolos */}
              <fieldset disabled={draftFrozen} className="min-w-0 border-0 p-0">
                <legend className="mb-2 block text-[13px] font-semibold text-[var(--text-secondary)]">Símbolos</legend>
                <p className="mb-2 text-xs text-[var(--text-muted)]" aria-live="polite" data-testid="symbol-count">
                  {selectedSymbols.length} de {symbols.length} selecionados · {pagedSymbols.length} visíveis
                </p>
                <div className="mb-2 grid grid-cols-[1fr_auto] gap-2">
                  <input
                    type="search"
                    value={symbolSearch}
                    onChange={(e) => setSymbolSearch(e.target.value)}
                    placeholder="Buscar símbolo"
                    aria-label="Buscar símbolo"
                    className="w-full rounded-md border border-[var(--border-default)] bg-[var(--bg-input)] px-2.5 py-2 text-sm text-[var(--text-primary)]"
                  />
                  <button
                    type="button"
                    onClick={() => toggleVisible(pagedSymbols, selectedSymbols, setSelectedSymbols)}
                    className="min-h-[44px] rounded-md border border-[var(--border-default)] bg-[var(--bg-input)] px-2.5 text-xs font-semibold text-[var(--text-secondary)]"
                  >
                    Selecionar visíveis
                  </button>
                </div>
                <div className="grid grid-cols-1 gap-2 sm:grid-cols-2">
                  {visibleSymbols.length === 0 ? (
                    <p className="text-xs text-[var(--text-muted)]">Nenhum símbolo encontrado.</p>
                  ) : null}
                  {pagedSymbols.map((s) => (
                    <label
                      key={s}
                      className={`flex min-h-[46px] items-start gap-2.5 rounded-lg border border-[var(--border-default)] bg-[var(--bg-secondary)] px-2.5 py-2.5 text-sm text-[var(--text-secondary)] ${
                        selectedSymbols.includes(s) ? 'border-[rgba(252,213,53,0.45)] bg-[rgba(252,213,53,0.07)]' : ''
                      }`}
                    >
                      <input
                        type="checkbox"
                        className="mt-0.5 h-[17px] w-[17px] min-h-[17px] accent-[var(--accent-primary)]"
                        checked={selectedSymbols.includes(s)}
                        onChange={() => toggleList(selectedSymbols, setSelectedSymbols, s)}
                      />
                      <span className="min-w-0">
                        <b className="block truncate text-[13px] font-semibold text-[var(--text-secondary)]">{s}</b>
                      </span>
                    </label>
                  ))}
                </div>
                {symbolPages > 1 ? (
                  <div className="mt-2 flex items-center justify-between text-xs text-[var(--text-tertiary)]">
                    <button
                      type="button"
                      disabled={symbolPage <= 1}
                      onClick={() => setSymbolPage((p) => Math.max(1, p - 1))}
                      className="min-h-[44px] rounded-md border border-[var(--border-default)] bg-[var(--bg-secondary)] px-3 disabled:opacity-40"
                    >
                      Anterior
                    </button>
                    <span>Página {symbolPage} de {symbolPages}</span>
                    <button
                      type="button"
                      disabled={symbolPage >= symbolPages}
                      onClick={() => setSymbolPage((p) => Math.min(symbolPages, p + 1))}
                      className="min-h-[44px] rounded-md border border-[var(--border-default)] bg-[var(--bg-secondary)] px-3 disabled:opacity-40"
                    >
                      Próxima
                    </button>
                  </div>
                ) : null}
                <p className={`mt-2 min-h-[18px] text-[11px] ${selectedSymbols.length ? 'text-[#93c5fd]' : 'text-[#fbbf24]'}`} data-testid="symbol-axis-status" aria-live="polite">
                  {selectedSymbols.length
                    ? Object.keys(preflight?.exclusions || {}).length
                      ? `Excluídas: ${Object.entries(preflight!.exclusions)
                          .map(([k, v]) => {
                            const [template, ...dimensions] = k.split('|')
                            const friendly = templates.find((item) => item.name === template)?.description || template
                            return `${[friendly, ...dimensions].join(' × ')} — ${v.reasons.join(', ')}`
                          })
                          .join('; ')}`
                      : ''
                    : 'Selecione ao menos um símbolo.'}
                </p>
              </fieldset>

              {/* Timeframes */}
              <fieldset disabled={draftFrozen} className="min-w-0 border-0 p-0">
                <legend className="mb-2 block text-[13px] font-semibold text-[var(--text-secondary)]">Timeframes swing</legend>
                <div className="grid grid-cols-2 gap-2">
                  {['4h', '1d'].map((tf) => (
                    <label key={tf} className="relative">
                      <input
                        type="checkbox"
                        className="absolute h-0 w-0 opacity-0"
                        checked={timeframes.includes(tf)}
                        onChange={() => toggleList(timeframes, setTimeframes, tf)}
                      />
                      <span
                        className={`flex min-h-[44px] items-center justify-center rounded-md border px-3 py-2 text-sm font-semibold ${
                          timeframes.includes(tf)
                            ? 'border-[rgba(252,213,53,0.5)] bg-[rgba(252,213,53,0.1)] text-[var(--accent-primary)]'
                            : 'border-[var(--border-default)] bg-[var(--bg-secondary)] text-[var(--text-tertiary)]'
                        }`}
                      >
                        {tf === '4h' ? '4 horas' : '1 dia'}
                      </span>
                    </label>
                  ))}
                </div>
                <p className={`mt-2 min-h-[18px] text-[11px] ${timeframes.length ? 'text-[#93c5fd]' : 'text-[#fbbf24]'}`}>
                  {timeframes.length ? '' : 'Selecione ao menos um timeframe.'}
                </p>
              </fieldset>

              {/* Direção */}
              <fieldset disabled={draftFrozen} className="min-w-0 border-0 p-0">
                <legend className="mb-2 block text-[13px] font-semibold text-[var(--text-secondary)]">Direção</legend>
                <div className="grid grid-cols-2 gap-2">
                  {(['long', 'short'] as const).map((d) => (
                    <label key={d} className="relative">
                      <input
                        type="checkbox"
                        className="absolute h-0 w-0 opacity-0"
                        checked={directions.includes(d)}
                        onChange={() => toggleList(directions, setDirections, d)}
                      />
                      <span
                        className={`flex min-h-[44px] items-center justify-center rounded-md border px-3 py-2 text-sm font-semibold ${
                          directions.includes(d)
                            ? 'border-[rgba(252,213,53,0.5)] bg-[rgba(252,213,53,0.1)] text-[var(--accent-primary)]'
                            : 'border-[var(--border-default)] bg-[var(--bg-secondary)] text-[var(--text-tertiary)]'
                        }`}
                      >
                        {d === 'long' ? 'Long' : 'Short'}
                      </span>
                    </label>
                  ))}
                </div>
                <p className={`mt-2 min-h-[18px] text-[11px] ${directions.length ? 'text-[#93c5fd]' : 'text-[#fbbf24]'}`}>
                  {directions.length ? '' : 'Selecione ao menos uma direção.'}
                </p>
              </fieldset>

              {/* Período + Ranking */}
              <label className="block">
                <span className="mb-2 block text-[13px] font-semibold text-[var(--text-secondary)]">Período histórico</span>
                <select
                  value={period}
                  disabled={draftFrozen}
                  onChange={(e) => setPeriod(e.target.value as '6m' | '2y' | 'all')}
                  className="w-full rounded-md border border-[var(--border-default)] bg-[var(--bg-input)] px-3 py-2 text-sm text-[var(--text-primary)]"
                >
                  <option value="2y">Últimos 2 anos</option>
                  <option value="6m">Últimos 6 meses</option>
                  <option value="all">Todo o histórico</option>
                </select>
              </label>
              <label className="block">
                <span className="mb-2 block text-[13px] font-semibold text-[var(--text-secondary)]">Ranking principal</span>
                <select
                  value={draftMetric}
                  disabled={draftFrozen}
                  onChange={(e) => setDraftMetric(e.target.value as Metric)}
                  className="w-full rounded-md border border-[var(--border-default)] bg-[var(--bg-input)] px-3 py-2 text-sm text-[var(--text-primary)]"
                >
                  <option value="calmar_ratio">Calmar (recomendado)</option>
                  <option value="delta_cagr_vs_bh">CAGR vs Buy &amp; Hold</option>
                </select>
              </label>
            </div>
          </article>

          {/* Preflight do servidor */}
          <aside className="rounded-xl border border-[var(--border-default)] bg-[var(--bg-elevated)] lg:sticky lg:top-24" aria-label="Preflight da varredura">
            <div className="flex items-start justify-between gap-4 border-b border-[var(--border-default)] px-5 py-4">
              <div>
                <h2 className="text-lg font-semibold">Preflight do servidor</h2>
                <p className="mt-1 text-xs text-[var(--text-tertiary)]">
                  {preflightLoading
                    ? 'Calculando…'
                    : overLimit
                      ? 'Limite excedido'
                      : snapshotStale
                        ? 'Snapshot expirado'
                        : preflight
                          ? 'Snapshot válido'
                          : 'Aguardando escopo'}
                </p>
              </div>
            </div>
            <div className="p-5">
              <div className="border-b border-[var(--border-default)] pb-4">
                <strong
                  className="block font-mono text-[34px] font-bold leading-tight text-[var(--accent-primary)]"
                  data-testid="planned-total"
                >
                  {overLimit ? (preflight?.errors?.total ?? '').match(/\d+/)?.[0] ?? '—' : preflight?.valid_total ?? '—'}
                </strong>
                <span className="text-sm text-[var(--text-tertiary)]">combinações válidas</span>
                <div className="mt-2 font-mono text-xs text-[var(--text-muted)]" data-testid="planned-formula">
                  {overLimit
                    ? `${axisCount} combinações brutas`
                    : preflight
                      ? `${selectedTemplates.length} × ${selectedSymbols.length} × ${timeframes.length} × ${directions.length}${preflight.excluded_count ? ` − ${preflight.excluded_count} incompatíveis` : ''}`
                      : '—'}
                </div>
              </div>

              {snapshotStale ? (
                <div className="mt-3 rounded-md border border-[rgba(245,158,11,0.35)] bg-[rgba(245,158,11,0.06)] p-2.5 text-[11px] text-[#fbbf24]">
                  O catálogo mudou após o preflight. Revalide o snapshot antes de iniciar.
                  <button
                    type="button"
                    onClick={() => void runPreflight()}
                    className="mt-2 inline-flex min-h-[44px] items-center gap-1.5 rounded-md border border-[rgba(245,158,11,0.42)] bg-[rgba(245,158,11,0.08)] px-3 text-xs font-semibold text-[#fbbf24]"
                  >
                    <RefreshCw className="h-3.5 w-3.5" />
                    Refazer preflight
                  </button>
                </div>
              ) : preflight ? (
                <div
                  className={`mt-3 rounded-md border p-2.5 text-[11px] ${
                    overLimit
                      ? 'border-[rgba(245,158,11,0.35)] bg-[rgba(245,158,11,0.06)] text-[#fbbf24]'
                      : 'border-[rgba(59,130,246,0.35)] bg-[rgba(59,130,246,0.07)] text-[#bfdbfe]'
                  }`}
                  role="status"
                  aria-live="polite"
                  data-testid="preflight-breakdown"
                >
                  <b className="text-[var(--text-secondary)]">{preflight.raw_total} brutas</b> · {preflight.excluded_count} excluídas ·{' '}
                  {preflight.valid_total} válidas · limite {preflight.limits.max_total}
                  <br />
                  snapshot{' '}
                  <span className="font-mono">
                    {overLimit ? 'não emitido · escopo acima do limite' : snapshotLabel(preflight.snapshot_hash, preflight.valid_total)}
                  </span>
                </div>
              ) : null}

              {preflightError ? (
                <div className="mt-3 text-xs text-[#ff8294]" data-testid="preflight-error">
                  {preflightError}
                </div>
              ) : null}

              <div className="my-3.5">
                <div className="flex justify-between gap-3 py-1.5 text-sm text-[var(--text-tertiary)]">
                  <span>Período</span>
                  <b className="font-semibold text-[var(--text-secondary)]">{periodLabel}</b>
                </div>
                <div className="flex justify-between gap-3 py-1.5 text-sm text-[var(--text-tertiary)]">
                  <span>Estimativa</span>
                  <b className="font-semibold text-[var(--text-secondary)]">{fmtEstimate(preflight?.valid_total ?? 0)}</b>
                </div>
                <div className="flex justify-between gap-3 py-1.5 text-sm text-[var(--text-tertiary)]">
                  <span>Ranking</span>
                  <b className="font-semibold text-[var(--text-secondary)]">
                    {draftMetric === 'calmar_ratio' ? 'Calmar' : 'CAGR vs B&H'}
                  </b>
                </div>
                <div className="flex justify-between gap-3 py-1.5 text-sm text-[var(--text-tertiary)]">
                  <span>Elegibilidade</span>
                  <b className="font-semibold text-[var(--text-secondary)]">≥30 trades · ≥90%</b>
                </div>
              </div>

              <button
                type="button"
                onClick={() => void startSweep()}
                disabled={!canStart || busy}
                data-testid="start-sweep"
                className={`flex min-h-[44px] w-full items-center justify-center gap-2 rounded-md border px-4 py-2.5 text-sm font-bold ${
                  !canStart || busy
                    ? 'cursor-not-allowed border-[var(--accent-primary-disabled)] bg-[var(--accent-primary-disabled)] text-[var(--text-muted)]'
                    : 'border-[var(--accent-primary)] bg-[var(--accent-primary)] text-[#181a20] hover:bg-[var(--accent-primary-hover)]'
                }`}
              >
                {draftFrozen && activeSweep ? (
                  <>
                    <Check className="h-4 w-4" />
                    Token revalidado · sweep criado
                  </>
                ) : (
                  <>
                    <Play className="h-4 w-4" />
                    Iniciar {preflight?.valid_total ?? 0} combinações
                  </>
                )}
              </button>

              {overLimit ? (
                <p className="mt-3 text-xs text-[var(--text-muted)]" data-testid="over-limit-note">
                  {preflight?.errors?.total} Reduza templates, símbolos, timeframes ou direções; o preflight e a ação de início usam o mesmo total.
                </p>
              ) : (
                <p className="mt-3 flex gap-2 text-xs text-[var(--text-muted)]">
                  <Shield className="h-4 w-4 shrink-0 text-[var(--accent-cyan)]" />
                  <span>O token será revalidado atomicamente; o rascunho congela após o start.</span>
                </p>
              )}
            </div>
          </aside>
        </section>

        {/* Progress card */}
        {activeSweep ? (
          <section
            className="mt-5 rounded-xl border border-[var(--border-default)] bg-[var(--bg-elevated)]"
            aria-labelledby="progress-heading"
            aria-live="polite"
            data-testid="sweep-progress"
          >
            <div className="flex items-start justify-between gap-4 border-b border-[var(--border-default)] px-5 py-4">
              <div>
                <h2 className="text-lg font-semibold">
                  Sweep ativo · <span className="font-mono">#{activeSweep.sweep_id}</span>
                </h2>
                <p className="mt-1 text-xs text-[var(--text-tertiary)]">
                  Snapshot <span className="font-mono">{snapshotLabel(activeSnapshotHash, activeSweep.total)}</span> · separado do histórico exibido
                </p>
              </div>
              <span className="inline-flex min-h-[28px] items-center rounded border border-[rgba(59,130,246,0.42)] px-2 py-1 text-[11px] font-bold text-[#93c5fd]" data-testid="active-state-chip">
                {activeSweep.state.toUpperCase()}
              </span>
            </div>

            <div className="grid grid-cols-1 items-center gap-5 p-5 md:grid-cols-[1fr_auto]">
              <div>
                <div className="mb-2.5 flex items-center justify-between gap-4">
                  <div className="flex items-center gap-2.5 font-semibold">
                    <span
                      className={`status-dot ${
                        activeSweep.state === 'paused' ? 'paused' : TERMINAL.has(activeSweep.state) ? 'cancelled' : ''
                      }`}
                    />
                    <span id="progress-heading" ref={progressHeadingRef} tabIndex={-1}>
                      {{
                        pending: 'Varredura pendente',
                        running: 'Varredura em execução',
                        paused: 'Varredura pausada',
                        cancelling: 'Cancelamento em andamento',
                        cancelled: 'Varredura cancelada',
                        failed: 'Varredura falhou',
                        partial_failure: 'Varredura concluída com falhas',
                        completed: 'Varredura concluída',
                      }[activeSweep.state]}
                    </span>
                  </div>
                  <strong className="font-mono" data-testid="progress-count">
                    {activeSweep.processed} de {activeSweep.total}
                  </strong>
                </div>
                <div
                  className="progress-track"
                  role="progressbar"
                  aria-label="Progresso da varredura ativa"
                  aria-valuemin={0}
                  aria-valuemax={activeSweep.total}
                  aria-valuenow={activeSweep.processed}
                >
                  <div
                    className="progress-fill"
                    style={{ width: `${activeSweep.total ? Math.round((activeSweep.processed / activeSweep.total) * 100) : 0}%` }}
                  />
                </div>
                <div className="mt-2.5 flex flex-wrap gap-x-4 gap-y-1 text-xs text-[var(--text-tertiary)]">
                  <span data-testid="counter-invariant">
                    {activeSweep.processed} processadas = {activeSweep.succeeded} sucesso + {activeSweep.failed} falha + {activeSweep.skipped} ignoradas
                  </span>
                  <span>Limites: 8 global · 1 por sweep · fila justa</span>
                  {activeSweep.terminal_reason ? <span>terminal: {activeSweep.terminal_reason}</span> : null}
                </div>

                {cancelConfirmOpen ? (
                  <div
                    className="mt-3 flex items-center justify-between gap-3.5 rounded-lg border border-[rgba(245,158,11,0.35)] bg-[rgba(245,158,11,0.06)] p-3"
                    role="alertdialog"
                    aria-modal="false"
                    aria-labelledby="cancel-title"
                  >
                    <p id="cancel-title" className="text-xs text-[var(--text-secondary)]">
                      Cancelar após as leases ativas? Resultados concluídos ficam; pendentes viram ignorados.
                    </p>
                    <div className="flex shrink-0 gap-2">
                      <button
                        type="button"
                        onClick={() => setCancelConfirmOpen(false)}
                        className="inline-flex min-h-[44px] items-center rounded-md border border-[var(--border-default)] bg-[var(--bg-secondary)] px-3 text-xs font-semibold text-[var(--text-secondary)]"
                      >
                        Continuar
                      </button>
                      <button
                        type="button"
                        onClick={() => void command('cancel')}
                        data-testid="confirm-cancel"
                        className="inline-flex min-h-[44px] items-center rounded-md border border-[var(--border-default)] bg-[var(--bg-secondary)] px-3 text-xs font-semibold text-[var(--text-secondary)]"
                      >
                        Confirmar cancelamento
                      </button>
                    </div>
                  </div>
                ) : null}
              </div>

              <div className="flex flex-wrap gap-2">
                {running ? (
                  <button
                    type="button"
                    onClick={() => void command(activeSweep.state === 'paused' ? 'resume' : 'pause')}
                    disabled={activeSweep.state === 'cancelling'}
                    data-testid="pause-sweep"
                    className={`inline-flex min-h-[44px] items-center gap-2 rounded-md border px-3.5 py-2 text-sm font-semibold ${
                      activeSweep.state === 'paused'
                        ? 'border-[rgba(14,203,129,0.4)] bg-[rgba(14,203,129,0.08)] text-[var(--accent-success)]'
                        : 'border-[rgba(245,158,11,0.42)] bg-[rgba(245,158,11,0.08)] text-[#fbbf24]'
                    } disabled:cursor-not-allowed disabled:opacity-50`}
                  >
                    {activeSweep.state === 'paused' ? <Play className="h-4 w-4" /> : <Pause className="h-4 w-4" />}
                    {activeSweep.state === 'paused' ? 'Retomar' : 'Pausar'}
                  </button>
                ) : null}
                {running ? (
                  <button
                    type="button"
                    onClick={() => setCancelConfirmOpen(true)}
                    disabled={activeSweep.state === 'cancelling'}
                    aria-expanded={cancelConfirmOpen}
                    data-testid="cancel-sweep"
                    className="inline-flex min-h-[44px] items-center gap-2 rounded-md border border-[var(--border-default)] bg-[var(--bg-secondary)] px-3.5 py-2 text-sm font-semibold text-[var(--text-secondary)] disabled:cursor-not-allowed disabled:opacity-50"
                  >
                    <Square className="h-4 w-4" />
                    Cancelar
                  </button>
                ) : null}
                <button
                  type="button"
                  onClick={newDraft}
                  data-testid="new-draft"
                  className="inline-flex min-h-[44px] items-center gap-2 rounded-md border border-[var(--border-default)] bg-[var(--bg-secondary)] px-3.5 py-2 text-sm font-semibold text-[var(--text-secondary)]"
                >
                  <RefreshCw className="h-4 w-4" />
                  Novo rascunho
                </button>
              </div>
            </div>
          </section>
        ) : null}

        {/* Leaderboard */}
        {viewSweep ? (
          <section
            className="mt-5 overflow-hidden rounded-xl border border-[var(--border-default)] bg-[var(--bg-elevated)]"
            aria-labelledby="leaderboard-title"
            aria-busy={lbLoading}
          >
            <div className="border-b border-[var(--border-default)] p-5">
              <div className="flex flex-col gap-2 md:flex-row md:items-start md:justify-between">
                <div>
                  <h2 id="leaderboard-title" className="text-xl font-semibold">
                    Leaderboard · {metric === 'calmar_ratio' ? 'Calmar' : 'CAGR vs Buy &amp; Hold'}
                  </h2>
                  <p className="mt-1 text-xs text-[var(--text-tertiary)]" data-testid="leaderboard-meta">
                    Varredura <span className="font-mono">#{viewSweep.sweep_id}</span> · {STATE_LABEL[viewSweep.state]}
                    {evidence ? (
                      <>
                        {' · '}janela UTC [{evidence.start}, {evidence.end}) · {evidence.candles}
                        {evidence.fees ? ` · ${evidence.fees}` : ''}
                        {evidence.slippage ? ` · ${evidence.slippage}` : ''}
                      </>
                    ) : null}
                  </p>
                </div>
                <span className="text-xs text-[var(--text-tertiary)]" aria-live="polite" data-testid="result-count">
                  {lbLoading ? 'Carregando…' : `${totalMatched} de ${totalAvailable} candidatos · página ${page} de ${totalPages}`}
                </span>
              </div>

              {lbError ? (
                <div className="mt-4 rounded-lg border border-[rgba(246,70,93,0.4)] bg-[rgba(246,70,93,0.06)] p-3.5">
                  <p className="text-sm font-semibold text-[var(--text-secondary)]">Falha ao carregar leaderboard</p>
                  <p className="mt-1 text-xs text-[var(--text-tertiary)]">
                    A conexão foi interrompida; o sweep continua no servidor e pode ser consultado novamente.
                  </p>
                  <button
                    type="button"
                    onClick={() => applyFilters(metric, fSymbol, fTimeframe, fDirection, page)}
                    className="mt-2.5 inline-flex min-h-[44px] items-center gap-1.5 rounded-md border border-[var(--border-default)] bg-[var(--bg-secondary)] px-3.5 text-xs font-semibold text-[var(--text-secondary)]"
                  >
                    <RefreshCw className="h-3.5 w-3.5" />
                    Tentar novamente
                  </button>
                </div>
              ) : null}

              <div className="mt-4 grid grid-cols-2 items-end gap-2.5 md:grid-cols-[repeat(4,minmax(140px,1fr))_auto]">
                <label className="block">
                  <span className="mb-1.5 block text-[11px] font-semibold uppercase tracking-wide text-[var(--text-muted)]">Ordenar por</span>
                  <select
                    value={metric}
                    onChange={(e) => handleSortChange(e.target.value as Metric)}
                    data-testid="sort-filter"
                    className="w-full rounded-md border border-[var(--border-default)] bg-[var(--bg-input)] px-3 py-2 text-sm text-[var(--text-primary)]"
                  >
                    <option value="calmar_ratio">Calmar</option>
                    <option value="delta_cagr_vs_bh">CAGR vs B&amp;H</option>
                  </select>
                </label>
                <label className="block">
                  <span className="mb-1.5 block text-[11px] font-semibold uppercase tracking-wide text-[var(--text-muted)]">Símbolo</span>
                  <select
                    value={fSymbol}
                    onChange={(e) => handleFilterChange('symbol', e.target.value)}
                    data-testid="symbol-filter"
                    className="w-full rounded-md border border-[var(--border-default)] bg-[var(--bg-input)] px-3 py-2 text-sm text-[var(--text-primary)]"
                  >
                    <option value="all">Todos</option>
                    {symbolOptions.map((s) => (
                      <option key={s} value={s}>{s}</option>
                    ))}
                  </select>
                </label>
                <label className="block">
                  <span className="mb-1.5 block text-[11px] font-semibold uppercase tracking-wide text-[var(--text-muted)]">Timeframe</span>
                  <select
                    value={fTimeframe}
                    onChange={(e) => handleFilterChange('timeframe', e.target.value)}
                    data-testid="timeframe-filter"
                    className="w-full rounded-md border border-[var(--border-default)] bg-[var(--bg-input)] px-3 py-2 text-sm text-[var(--text-primary)]"
                  >
                    <option value="all">Todos</option>
                    <option value="4h">4h</option>
                    <option value="1d">1d</option>
                  </select>
                </label>
                <label className="block">
                  <span className="mb-1.5 block text-[11px] font-semibold uppercase tracking-wide text-[var(--text-muted)]">Direção</span>
                  <select
                    value={fDirection}
                    onChange={(e) => handleFilterChange('direction', e.target.value)}
                    data-testid="direction-filter"
                    className="w-full rounded-md border border-[var(--border-default)] bg-[var(--bg-input)] px-3 py-2 text-sm text-[var(--text-primary)]"
                  >
                    <option value="all">Todas</option>
                    <option value="long">Long</option>
                    <option value="short">Short</option>
                  </select>
                </label>
                <button
                  type="button"
                  onClick={clearFilters}
                  data-testid="clear-filters"
                  className="inline-flex min-h-[44px] items-center justify-center gap-2 whitespace-nowrap rounded-md border border-[var(--border-default)] bg-[var(--bg-elevated)] px-3.5 py-2 text-sm font-semibold text-[var(--text-secondary)] md:col-span-1"
                >
                  <X className="h-4 w-4" />
                  Limpar filtros
                </button>
              </div>
            </div>

            <div className="overflow-x-auto" tabIndex={0} aria-label="Tabela rolável de candidatos">
              {rows.length === 0 && !lbLoading && !lbError ? (
                <div className="p-8 text-center" data-testid="empty-state">
                  <strong className="block text-[var(--text-secondary)]">Nenhum candidato neste recorte.</strong>
                  <p className="mt-1 text-sm text-[var(--text-tertiary)]">Limpe os filtros para voltar ao leaderboard completo.</p>
                  <button
                    type="button"
                    onClick={clearFilters}
                    className="mt-3 inline-flex min-h-[44px] items-center rounded-md border border-[var(--border-default)] bg-[var(--bg-secondary)] px-4 text-sm font-semibold text-[var(--text-secondary)]"
                  >
                    Limpar filtros
                  </button>
                </div>
              ) : null}
              <table className="discovery-table" aria-describedby="leaderboard-note">
                <caption className="sr-only">
                  Candidatos da varredura selecionada; ranks são globais e permanecem sob filtro e paginação
                </caption>
                <thead>
                  <tr>
                    <th scope="col">Rank global</th>
                    <th scope="col">Candidato</th>
                    <th scope="col">Mercado</th>
                    <th scope="col">CAGR</th>
                    <th scope="col" aria-label="Buy and Hold">B&amp;H</th>
                    <th scope="col" aria-label="Delta versus Buy and Hold">Δ B&amp;H</th>
                    <th scope="col">Calmar</th>
                    <th scope="col" aria-label="Maximum Drawdown">Max DD</th>
                    <th scope="col">Sharpe</th>
                    <th scope="col" aria-label="Profit Factor">PF</th>
                    <th scope="col">Win rate</th>
                    <th scope="col">Trades</th>
                    <th scope="col">Ação</th>
                  </tr>
                </thead>
                <tbody>
                  {rows.map((row) => {
                    const lowSample = row.eligibility !== 'eligible'
                    const duplicate = row.dedup_state === 'duplicate_favorite'
                    const promoted = row.dedup_state === 'already_promoted'
                    const promoteDisabled = busy || promoting || lowSample || duplicate || promoted
                    return (
                      <tr key={row.result_id} className="result-row">
                        <td className="rank-cell" data-label="Rank global">
                          <span className="rank-cell-value">{row.rank ?? '—'}</span>
                        </td>
                        <td className="candidate-cell" data-label="Candidato">
                          <div className="candidate-cell-min">
                            <strong className="candidate-name">{row.template_id}</strong>
                            <span className="candidate-meta">
                              {row.result_id} · cobertura {fmtPct(row.coverage)}
                              {fmtParams(row.parameters) ? ` · ${fmtParams(row.parameters)}` : ''}
                              {row.direction === 'short' ? ' · benchmark B&H long-only' : ''}
                            </span>
                            {lowSample ? <span className="sample-badge">Baixa amostra</span> : null}
                            {duplicate ? (
                              <span className="dedup-note" title={`Promoção bloqueada: equivalente ao favorito ativo ${row.dedup_reference ?? ''}`}>
                                <Copy className="h-3 w-3" />
                                Equivale ao favorito ativo {row.dedup_reference ?? '—'}
                              </span>
                            ) : null}
                          </div>
                        </td>
                        <td data-label="Mercado">
                          <span className="discovery-tag">{row.symbol} · {row.timeframe}</span>{' '}
                          <span className={`discovery-tag ${row.direction}`}>{row.direction === 'long' ? 'Long' : 'Short'}</span>
                        </td>
                        <td className={`number ${row.cagr != null && row.cagr >= 0 ? 'positive' : 'negative'}`} data-label="CAGR">
                          {fmtPct(row.cagr)}
                        </td>
                        <td className="number" data-label="Buy and Hold">{fmtPct(row.benchmark_cagr)}</td>
                        <td className={`number ${row.delta_cagr_vs_bh != null && row.delta_cagr_vs_bh >= 0 ? 'positive' : 'negative'}`} data-label="Delta versus Buy and Hold">
                          {fmtPp(row.delta_cagr_vs_bh)}
                        </td>
                        <td className={`number ${row.calmar_ratio != null && row.calmar_ratio < 0 ? 'negative' : ''}`} data-label="Calmar">
                          {fmtNum(row.calmar_ratio)}
                        </td>
                        <td className="number negative" data-label="Maximum Drawdown">{fmtDrawdown(row.max_drawdown)}</td>
                        <td className="number" data-label="Sharpe">{fmtNum(row.sharpe_ratio)}</td>
                        <td className="number" data-label="Profit Factor">{fmtNum(row.profit_factor)}</td>
                        <td className="number" data-label="Win rate">{fmtPct(row.win_rate)}</td>
                        <td className="number" data-label="Trades">{row.trades_count ?? 'N/A'}</td>
                        <td className="action-cell" data-label="Ação">
                          {promoted ? (
                            <span
                              className="promoted-state"
                              tabIndex={-1}
                              data-promoted-result={row.result_id}
                            >
                              <Check className="h-3.5 w-3.5" />
                              Favorito tier 3
                            </span>
                          ) : (
                            <button
                              type="button"
                              disabled={promoteDisabled}
                              onClick={(event) => {
                                promotionTriggerRef.current = event.currentTarget
                                setPromoteTarget(row)
                              }}
                              aria-haspopup="dialog"
                              aria-controls="promotion-modal"
                              aria-expanded={promoteTarget?.result_id === row.result_id}
                              aria-describedby={lowSample || duplicate ? `reason-${row.result_id}` : undefined}
                              data-testid={`promote-${row.result_id}`}
                              className={`promote-action inline-flex min-h-[44px] items-center justify-center gap-1.5 rounded-md border px-3.5 text-xs font-bold ${
                                promoteDisabled
                                  ? 'cursor-not-allowed border-[var(--accent-primary-disabled)] bg-[var(--accent-primary-disabled)] text-[var(--text-muted)]'
                                  : 'border-[var(--accent-primary)] bg-[var(--accent-primary)] text-[#181a20] hover:bg-[var(--accent-primary-hover)]'
                              }`}
                            >
                              {lowSample ? 'Baixa amostra' : duplicate ? 'Já existe' : 'Promover'}
                            </button>
                          )}
                          {lowSample || duplicate ? (
                            <span id={`reason-${row.result_id}`} className="sr-only">
                              {lowSample
                                ? 'Promoção bloqueada: mínimo 30 trades e 90 por cento de cobertura'
                                : `Promoção bloqueada: equivalente ao favorito ativo ${row.dedup_reference ?? ''}`}
                            </span>
                          ) : null}
                        </td>
                      </tr>
                    )
                  })}
                </tbody>
              </table>
            </div>

            {!lbLoading && !lbError && rows.length > 0 ? (
              <div className="flex items-center justify-between border-t border-[var(--border-default)] px-5 py-3">
                <button
                  type="button"
                  onClick={() => goPage(page - 1)}
                  disabled={page <= 1}
                  data-testid="prev-page"
                  className="inline-flex min-h-[44px] items-center gap-1.5 rounded-md border border-[var(--border-default)] bg-[var(--bg-secondary)] px-3.5 text-sm font-semibold text-[var(--text-secondary)] disabled:cursor-not-allowed disabled:opacity-40"
                >
                  <ChevronLeft className="h-4 w-4" />
                  Anterior
                </button>
                <span className="text-sm text-[var(--text-tertiary)]" data-testid="page-label">
                  Página {page} de {totalPages}
                </span>
                <button
                  type="button"
                  onClick={() => goPage(page + 1)}
                  disabled={page >= totalPages}
                  data-testid="next-page"
                  className="inline-flex min-h-[44px] items-center gap-1.5 rounded-md border border-[var(--border-default)] bg-[var(--bg-secondary)] px-3.5 text-sm font-semibold text-[var(--text-secondary)] disabled:cursor-not-allowed disabled:opacity-40"
                >
                  Próxima
                  <ChevronRight className="h-4 w-4" />
                </button>
              </div>
            ) : null}
            <p id="leaderboard-note" className="border-t border-[var(--border-default)] px-5 py-3 text-[11px] text-[var(--text-muted)]">
              Conteúdo educacional. Rank global usa resultados elegíveis (≥30 trades, ≥90% cobertura); filtros não renumeram posições.
              Dados históricos não garantem retornos futuros.
            </p>
          </section>
        ) : null}
      </div>

      {/* Modal de promoção */}
      {promoteTarget ? (
        <div
          className="fixed inset-0 z-[80] flex items-center justify-center bg-black/70 p-5"
          onClick={(e) => {
            if (e.target === e.currentTarget) closePromotion(true)
          }}
        >
          <div
            ref={modalRef}
            id="promotion-modal"
            role="dialog"
            aria-modal="true"
            aria-labelledby="modal-title"
            aria-describedby="modal-description"
            className="w-full max-w-[480px] rounded-xl border border-[var(--border-default)] bg-[var(--bg-elevated)] shadow-2xl"
          >
            <div className="flex items-start justify-between gap-4 border-b border-[var(--border-default)] p-5">
              <div>
                <h2 id="modal-title" className="text-xl font-semibold">Promover a favorito tier 3</h2>
                <p id="modal-description" className="mt-1 text-xs text-[var(--text-tertiary)]">
                  Destino fixo deste fluxo. Revise a origem antes de confirmar.
                </p>
              </div>
              <button
                type="button"
                onClick={() => closePromotion(true)}
                aria-label="Fechar"
                data-testid="close-modal"
                className="grid h-11 w-11 min-h-[44px] place-items-center rounded-md border border-[var(--border-default)] bg-[var(--bg-secondary)] text-[var(--text-secondary)]"
              >
                <X className="h-4 w-4" />
              </button>
            </div>
            <div className="p-5">
              <div className="rounded-lg border border-[var(--border-default)] bg-[var(--bg-secondary)] p-3.5">
                <strong className="block" data-testid="modal-candidate">{promoteTarget.template_id}</strong>
                <span className="text-xs text-[var(--text-tertiary)]" data-testid="modal-market">
                  {promoteTarget.symbol} · {promoteTarget.timeframe} · {promoteTarget.direction === 'long' ? 'Long' : 'Short'}
                </span>
              </div>
              <div className="my-4 grid grid-cols-2 gap-2.5">
                <div className="rounded-md border border-[var(--border-default)] bg-[var(--bg-secondary)] p-2.5">
                  <small className="block text-[var(--text-muted)]">Varredura de origem</small>
                  <b className="font-mono text-xs" data-testid="modal-run">#{viewSweep?.sweep_id ?? '—'}</b>
                </div>
                <div className="rounded-md border border-[var(--border-default)] bg-[var(--bg-secondary)] p-2.5">
                  <small className="block text-[var(--text-muted)]">Resultado</small>
                  <b className="font-mono text-xs" data-testid="modal-result">{promoteTarget.result_id}</b>
                </div>
              </div>
              <div className="rounded-md border border-[var(--border-default)] bg-[var(--bg-secondary)] p-2.5">
                <small className="block text-[var(--text-muted)]">Destino obrigatório</small>
                <strong className="text-[var(--accent-primary)]">Tier 3 · observação</strong>
              </div>
              {promoteConflict ? (
                <div className="mt-3.5 rounded-lg border border-[rgba(246,70,93,0.4)] bg-[rgba(246,70,93,0.06)] p-3 text-xs text-[var(--text-secondary)]" data-testid="promote-conflict">
                  <strong className="block">Conflito equivalente (409)</strong>
                  <span className="mt-1 block text-[var(--text-tertiary)]">
                    Outro administrador promoveu uma estratégia equivalente. Referência vencedora:{' '}
                    <b className="font-mono text-[var(--text-secondary)]">{promoteConflict}</b>. Nenhuma nova promoção foi criada.
                  </span>
                  <button
                    type="button"
                    onClick={() => {
                      closePromotion(true)
                      if (viewSweep) applyFilters(metric, fSymbol, fTimeframe, fDirection, page)
                    }}
                    className="mt-2.5 inline-flex min-h-[44px] items-center rounded-md border border-[var(--border-default)] bg-[var(--bg-secondary)] px-3.5 text-xs font-semibold text-[var(--text-secondary)]"
                  >
                    <RefreshCw className="mr-1.5 h-3.5 w-3.5" />
                    Recarregar deduplicação
                  </button>
                </div>
              ) : null}
              <p className="mt-3.5 flex gap-2 text-xs text-[var(--text-muted)]">
                <Shield className="h-4 w-4 shrink-0 text-[var(--accent-cyan)]" />
                <span>Elegibilidade e identidade de estratégia serão revalidadas sob lock. Evidência de outra janela não contorna duplicidade.</span>
              </p>
            </div>
            <div className="flex justify-end gap-2.5 p-5 pt-0">
              <button
                type="button"
                onClick={() => closePromotion(true)}
                className="inline-flex min-h-[44px] items-center rounded-md border border-[var(--border-default)] bg-[var(--bg-elevated)] px-4 py-2 text-sm font-semibold text-[var(--text-secondary)]"
              >
                Voltar
              </button>
              <button
                type="button"
                onClick={() => void promote()}
                disabled={promoting || promoteConflict !== null}
                id="confirm-promotion"
                data-testid="confirm-promotion"
                className="inline-flex min-h-[44px] items-center gap-2 rounded-md border border-[var(--accent-primary)] bg-[var(--accent-primary)] px-4 py-2 text-sm font-bold text-[#181a20] hover:bg-[var(--accent-primary-hover)] disabled:cursor-not-allowed disabled:opacity-50"
              >
                <Star className="h-4 w-4" />
                Promover como tier 3
              </button>
            </div>
          </div>
        </div>
      ) : null}
    </div>
  )
}
