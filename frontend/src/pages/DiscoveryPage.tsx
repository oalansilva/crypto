import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Check, ChevronLeft, ChevronRight, Copy, Edit3, History, Pause, Play, RefreshCw,
  Shield, Square, Star, Trash2, X,
} from 'lucide-react'
import { authFetch } from '../lib/authFetch'
import { API_BASE_URL } from '../lib/apiBase'
import { SelectionWorkbench } from '../components/SelectionWorkbench'
import type { WorkingAxis, SelectionSnapshot, CatalogItem } from '../components/SelectionWorkbench'
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
  period_type?: string | null
  start_date?: string | null
  end_date?: string | null
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
  insufficient_sample?: number
  processed: number
  terminal_reason: string | null
  terminal_code: string | null
  draft_key?: string | null
  snapshot: PreflightResult | null
  updated_at?: string | null
  wake_up_state?: string | null
  dispatch_status?: string | null
}

type HistoryRun = {
  sweep_id: string
  state: SweepState
  total: number
  processed: number
  succeeded: number
  failed: number
  skipped: number
  insufficient_sample?: number
  snapshot_hash: string | null
  created_at: string | null
}

type OosVerdict = {
  status?: string | null
  reasons?: string[] | null
}

type LeaderboardRow = {
  rank: number | null
  result_id: string
  template_id: string
  display_name?: string | null
  description?: string | null
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
  oos_verdict?: OosVerdict | null
  metrics?: { oos_verdict?: OosVerdict | null } | null
}

type Metric = 'calmar_ratio' | 'delta_cagr_vs_bh'

const TERMINAL = new Set<SweepState>(['cancelled', 'failed', 'partial_failure', 'completed'])
const NON_TERMINAL = new Set<SweepState>(['pending', 'running', 'paused', 'cancelling'])
const PAGE_SIZE = 12
const DRAFT_KEY_STORAGE = 'discovery-draft-idempotency-key'
const idempotencyKey = (prefix: string, value: string) => `${prefix}-${value}`.slice(0, 64)
const newDraftKey = () =>
  globalThis.crypto?.randomUUID?.() ?? `draft-${Date.now()}-${Math.random()}`.slice(0, 36)
const readStoredDraftKey = () => {
  try {
    return window.sessionStorage.getItem(DRAFT_KEY_STORAGE)
  } catch {
    return null
  }
}
const persistDraftKey = (key: string) => {
  try {
    window.sessionStorage.setItem(DRAFT_KEY_STORAGE, key)
  } catch {
    /* ignore quota / private mode */
  }
}
const STATE_LABEL: Record<SweepState, string> = {
  pending: 'pendente', running: 'em execução', paused: 'pausada', cancelling: 'cancelando',
  cancelled: 'cancelada', failed: 'falhou', partial_failure: 'falha parcial', completed: 'concluída',
}

const CALMAR_ABS_CEILING = 1000

function fmtNum(v: number | null | undefined, digits = 2): string {
  if (v === null || v === undefined || Number.isNaN(v) || !Number.isFinite(v)) return 'N/A'
  return v.toLocaleString('pt-BR', { minimumFractionDigits: digits, maximumFractionDigits: digits })
}
function fmtCalmar(v: number | null | undefined): string {
  if (v === null || v === undefined || Number.isNaN(v) || !Number.isFinite(v)) return 'N/A'
  if (Math.abs(v) > CALMAR_ABS_CEILING) return 'N/A'
  return v.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}
function gridEasyMetrics(row: LeaderboardRow, calmarBlocked: boolean) {
  const sharpe = calmarBlocked ? 'N/A' : fmtNum(row.sharpe_ratio)
  const win = calmarBlocked ? 'N/A' : fmtPct(row.win_rate)
  const cagr = calmarBlocked ? 'N/A' : fmtPct(row.cagr)
  return {
    blocked: calmarBlocked,
    sharpe,
    win,
    cagr,
    sharpeNa: sharpe === 'N/A',
    winNa: win === 'N/A',
    cagrNa: cagr === 'N/A',
  }
}
function walkForwardStatus(row: LeaderboardRow): 'GO' | 'NO-GO' | null {
  const nested = row.metrics && typeof row.metrics === 'object' ? row.metrics.oos_verdict : null
  const raw = String(row.oos_verdict?.status ?? nested?.status ?? '').trim().toUpperCase()
  if (raw === 'GO' || raw === 'NO-GO') return raw
  return null
}
function WalkForwardSeal({ status }: { status: 'GO' | 'NO-GO' | null }) {
  if (status !== 'GO' && status !== 'NO-GO') return null
  return (
    <span
      className={`verdict ${status === 'GO' ? 'verdict-go' : 'verdict-nogo'}`}
      data-testid={status === 'GO' ? 'seal-go' : 'seal-nogo'}
    >
      {status}
    </span>
  )
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
function makeEmptyAxis(): WorkingAxis {
  return { mode: 'manual', selected: new Set(), excluded: new Set(), query: '', category: 'all', page: 1, catalogState: 'ready' }
}
function makeEmptySelection(): SelectionSnapshot {
  return { templates: makeEmptyAxis(), symbols: makeEmptyAxis() }
}

const TEMPLATE_CATEGORIES: Record<string, string> = {
  multi: 'Tendência', bollinger: 'Volatilidade', ema: 'Reversão', dual: 'Momentum',
  adx: 'Tendência', supertrend: 'Tendência', ichimoku: 'Tendência', donchian: 'Tendência',
  macd: 'Momentum', rsi: 'Reversão', stochastic: 'Reversão', cci: 'Momentum',
  williams: 'Reversão', atr: 'Volatilidade', keltner: 'Volatilidade', volume: 'Volume',
  obv: 'Volume', mfi: 'Volume', vwap: 'Volume', sma: 'Tendência', roc: 'Momentum',
  momentum: 'Momentum', volatility: 'Volatilidade', pivot: 'Reversão', support: 'Reversão',
  breakout: 'Tendência',
}

const TOP_CODES = new Set(['BTC', 'ETH', 'SOL', 'BNB', 'XRP', 'ADA', 'DOGE', 'AVAX', 'TRX', 'DOT'])

function catalogFromTemplates(list: { name: string; display_name?: string; description: string }[]): CatalogItem[] {
  return list.map((t) => {
    const prefix = (t.name.split('_')[0] ?? 'outros').toLowerCase()
    const cat = TEMPLATE_CATEGORIES[prefix] ?? 'Outros'
    return { id: t.name, label: t.display_name || t.name, category: cat, meta: t.description || '' }
  })
}

function catalogFromSymbols(list: string[]): CatalogItem[] {
  return list.map((code) => {
    const base = code.split('/')[0] ?? code
    const cat = TOP_CODES.has(base) ? 'Alta liquidez' : 'Demais pares'
    return { id: code, label: code, category: cat, meta: 'Spot · cotação USDT' }
  })
}

function errorDetail(data: unknown, fallback: string): string {
  // O detalhe de erro da API chega embrulhado ({ detail: {...} }); a tela
  // exibe só instrução de operação (card #837, aceite 7) — nunca JSON técnico.
  if (data && typeof data === 'object') {
    const d = (data as Record<string, unknown>).detail
    if (typeof d === 'string') return d
    if (d && typeof d === 'object') {
      const nested = (d as Record<string, unknown>).detail
      if (typeof nested === 'string') return nested
    }
  }
  return fallback
}

// Cópias operacionais do início de varredura (card #837), alinhadas ao
// protótipo aprovado: o que fazer, sem JSON nem jargão.
const START_FAILURE_FALLBACK =
  'Não foi possível iniciar a varredura. Confira a seleção e tente de novo — nada foi criado.'
const LIVE_BLOCK_COPY =
  'Há outra varredura em curso — conclua ou cancele antes de iniciar esta.'

function sameStringSet(a: string[], b: string[] | undefined): boolean {
  if (!b) return a.length === 0
  if (a.length !== b.length) return false
  const setB = new Set(b)
  return a.every((x) => setB.has(x))
}

export function DiscoveryPage() {
  const navigate = useNavigate()

  // Catálogos
  const [symbols, setSymbols] = useState<string[]>([])
  // Seleção
  const [selectedTemplates, setSelectedTemplates] = useState<string[]>([])
  const [selectedSymbols, setSelectedSymbols] = useState<string[]>([])
  const [timeframes, setTimeframes] = useState<string[]>(['4h', '1d'])
  const [directions, setDirections] = useState<string[]>(['long'])
  const [period, setPeriod] = useState<'6m' | '2y' | 'all'>('all')
  const [draftMetric, setDraftMetric] = useState<Metric>('calmar_ratio')
  const [metric, setMetric] = useState<Metric>('calmar_ratio')
  // Workbench
  const [workbenchOpen, setWorkbenchOpen] = useState(false)
  const [workbenchTrigger, setWorkbenchTrigger] = useState<'templates' | 'symbols'>('templates')
  const workbenchTriggerRef = useRef<HTMLButtonElement | null>(null)
  const [templatesCatalog, setTemplatesCatalog] = useState<CatalogItem[]>([])
  const [symbolsCatalog, setSymbolsCatalog] = useState<CatalogItem[]>([])
  const [committedSelection, setCommittedSelection] = useState<SelectionSnapshot>(() => makeEmptySelection())
  // Preflight
  const [preflight, setPreflight] = useState<PreflightResult | null>(null)
  const [preflightLoading, setPreflightLoading] = useState(false)
  const [preflightError, setPreflightError] = useState<string | null>(null)
  const [snapshotStale, setSnapshotStale] = useState(false)
  const [draftFrozen, setDraftFrozen] = useState(false)
  const [draftKey, setDraftKey] = useState(() => readStoredDraftKey() || newDraftKey())
  const [startError, setStartError] = useState<string | null>(null)
  const [recoveryStatus, setRecoveryStatus] = useState<'loading' | 'ready' | 'error'>('loading')
  const [reconnected, setReconnected] = useState(false)
  // Sweep ativo e run histórico exibido permanecem separados, como no protótipo.
  const [activeSweep, setActiveSweep] = useState<Sweep | null>(null)
  const [viewSweep, setViewSweep] = useState<Sweep | null>(null)
  const [history, setHistory] = useState<HistoryRun[]>([])
  const [busy, setBusy] = useState(false)
  // Leaderboard
  const [rows, setRows] = useState<LeaderboardRow[]>([])
  // Card 852: parciais do Acompanhar vivem separadas do leaderboard do
  // Decidir (top-5 travadas do sweep em curso, sem paginação).
  const [partials, setPartials] = useState<LeaderboardRow[]>([])
  const [totalMatched, setTotalMatched] = useState(0)
  const [totalAvailable, setTotalAvailable] = useState(0)
  const [lbLoading, setLbLoading] = useState(false)
  const [lbError, setLbError] = useState(false)
  const [sessionExpired, setSessionExpired] = useState(false)
  const [page, setPage] = useState(1)
  const [fSymbol, setFSymbol] = useState('all')
  const [fTimeframe, setFTimeframe] = useState('all')
  const [fDirection, setFDirection] = useState('all')
  // Modal / toast / estados críticos
  const [promoteTarget, setPromoteTarget] = useState<LeaderboardRow | null>(null)
  const [promoteConflict, setPromoteConflict] = useState<string | null>(null)
  const [promotedFocusId, setPromotedFocusId] = useState<string | null>(null)
  const [promoting, setPromoting] = useState(false)
  const [discardTarget, setDiscardTarget] = useState<LeaderboardRow | null>(null)
  const [discarding, setDiscarding] = useState(false)
  const [toast, setToast] = useState<{ title: string; copy: string } | null>(null)
  const [permissionDenied, setPermissionDenied] = useState(false)
  const [cancelConfirmOpen, setCancelConfirmOpen] = useState(false)
  const [historyOpen, setHistoryOpen] = useState(false)
  // Card 852 — 1 modo visível por vez: Montar (rascunho editável + preflight),
  // Acompanhando (progresso da live + parciais travadas), Decidir (leaderboard
  // do sweep escolhido). Eventos movem o modo; tabs permitem revisitar.
  const [mode, setMode] = useState<'montar' | 'acomp' | 'decidir'>('montar')
  const [expandedRows, setExpandedRows] = useState<Set<string>>(new Set())
  const [inlineQuery, setInlineQuery] = useState({ templates: '', symbols: '' })

  const pollRef = useRef<number | null>(null)
  const preflightTimer = useRef<number | null>(null)
  const toastTimer = useRef<number | null>(null)
  const focusStartedSweepRef = useRef(false)
  const skipCatalogDefaultsRef = useRef(false)
  const viewOriginRef = useRef<'auto' | 'user'>('auto')
  const pollRevRef = useRef(0)
  const pollInFlightRef = useRef(false)
  const activeSweepRef = useRef<Sweep | null>(null)
  const lbReqRef = useRef(0)
  const appliedUpdatedAtRef = useRef<Record<string, string>>({})
  const modalRef = useRef<HTMLDivElement | null>(null)
  const discardModalRef = useRef<HTMLDivElement | null>(null)
  const promotionTriggerRef = useRef<HTMLButtonElement | null>(null)
  const discardTriggerRef = useRef<HTMLButtonElement | null>(null)
  const progressHeadingRef = useRef<HTMLSpanElement | null>(null)
  const leaderboardTitleRef = useRef<HTMLHeadingElement | null>(null)
  const previousActiveStateRef = useRef<SweepState | null>(null)

  useEffect(() => {
    persistDraftKey(draftKey)
  }, [draftKey])

  // ---- catalog helpers ----

  function applySelectionFromWorkbench(state: SelectionSnapshot) {
    const t = [...(state.templates.mode === 'all'
      ? templatesCatalog.filter((i) => !state.templates.excluded.has(i.id))
      : [...state.templates.selected].map((id) => templatesCatalog.find((i) => i.id === id)).filter(Boolean))
    ] as CatalogItem[]
    const s = [...(state.symbols.mode === 'all'
      ? symbolsCatalog.filter((i) => !state.symbols.excluded.has(i.id))
      : [...state.symbols.selected].map((id) => symbolsCatalog.find((i) => i.id === id)).filter(Boolean))
    ] as CatalogItem[]
    setSelectedTemplates(t.map((i) => i.id))
    setSelectedSymbols(s.map((i) => i.id))
    setCommittedSelection(state)
  }

  // summary helpers
  function selectionSummary(axis: 'templates' | 'symbols') {
    const a = committedSelection[axis]
    const total = axis === 'templates' ? templatesCatalog.length : symbolsCatalog.length
    if (a.mode === 'all') {
      const excluded = [...a.excluded].map((id) => (axis === 'templates' ? templatesCatalog : symbolsCatalog).find((i) => i.id === id)?.label ?? id)
      return {
        count: `${Math.max(0, total - a.excluded.size)} de ${total} selecionados`,
        detail: excluded.length ? `Catálogo inteiro · ${excluded.length} exceções` : 'Catálogo inteiro · nenhuma exceção',
        chips: excluded.slice(0, 3),
        extra: excluded.length > 3 ? `+${excluded.length - 3}` : '',
      }
    }
    const ids = [...a.selected]
    const chips = ids.slice(0, 3).map((id) => (axis === 'templates' ? templatesCatalog : symbolsCatalog).find((i) => i.id === id)?.label ?? id)
    return {
      count: `${a.selected.size} de ${total} selecionados`,
      detail: 'Seleção manual',
      chips,
      extra: ids.length > 3 ? `+${ids.length - 3}` : '',
    }
  }

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
        ].map((t: { name?: string; display_name?: string; description?: string }) => ({
          name: String(t.name ?? ''),
          display_name: String(t.display_name ?? ''),
          description: String(t.description ?? ''),
        }))
        const catT = catalogFromTemplates(flat)
        setTemplatesCatalog(catT)
        if (!skipCatalogDefaultsRef.current) {
          setSelectedTemplates(flat.slice(0, 3).map((t) => t.name))
          setCommittedSelection((prev) => ({
            ...prev,
            templates: { ...prev.templates, selected: new Set(flat.slice(0, 3).map((t) => t.name)) },
          }))
        }
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
        const catS = catalogFromSymbols(list)
        setSymbolsCatalog(catS)
        if (!skipCatalogDefaultsRef.current) {
          setSelectedSymbols(list.slice(0, 4))
          setCommittedSelection((prev) => ({ ...prev, symbols: { ...prev.symbols, selected: new Set(list.slice(0, 4)) } }))
        }
      } catch {
        /* catálogo auxiliar */
      }
    })()
  }, [])

  // ---------- Histórico ----------
  const hydrateFromSweep = useCallback((sweep: Sweep) => {
    const snapshot = sweep.snapshot
    const axes = snapshot?.axes
    if (!axes) return false
    skipCatalogDefaultsRef.current = true
    setSelectedTemplates(axes.templates || [])
    setSelectedSymbols(axes.symbols || [])
    setTimeframes(axes.timeframes?.length ? axes.timeframes : ['4h', '1d'])
    setDirections(axes.directions?.length ? axes.directions : ['long'])
    const periodType = snapshot.period_type
    if (periodType === '6m' || periodType === '2y' || periodType === 'all') {
      setPeriod(periodType)
    }
    setPreflight(snapshot)
    setDraftFrozen(true)
    if (sweep.draft_key) setDraftKey(sweep.draft_key)
    setCommittedSelection({
      templates: { ...makeEmptyAxis(), selected: new Set(axes.templates || []) },
      symbols: { ...makeEmptyAxis(), selected: new Set(axes.symbols || []) },
    })
    return true
  }, [])

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

  // ---------- Preflight (auto, com debounce) ----------
  const runPreflight = useCallback(async () => {
    if (recoveryStatus !== 'ready' || draftFrozen) return
    setStartError(null)
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
  }, [draftFrozen, recoveryStatus, selectedTemplates, selectedSymbols, timeframes, directions, period])

  useEffect(() => {
    if (recoveryStatus !== 'ready' || draftFrozen) return
    if (preflightTimer.current !== null) window.clearTimeout(preflightTimer.current)
    preflightTimer.current = window.setTimeout(() => void runPreflight(), 450)
    return () => {
      if (preflightTimer.current !== null) window.clearTimeout(preflightTimer.current)
    }
  }, [selectedTemplates, selectedSymbols, timeframes, directions, period, draftFrozen, runPreflight])

  const axisCount = [
    ...(committedSelection.templates.mode === 'all'
      ? templatesCatalog.filter((i) => !committedSelection.templates.excluded.has(i.id))
      : [...committedSelection.templates.selected].filter((id) => templatesCatalog.some((i) => i.id === id))),
  ].length * [
    ...(committedSelection.symbols.mode === 'all'
      ? symbolsCatalog.filter((i) => !committedSelection.symbols.excluded.has(i.id))
      : [...committedSelection.symbols.selected].filter((id) => symbolsCatalog.some((i) => i.id === id))),
  ].length * timeframes.length * directions.length
  const overLimit = Boolean(preflight?.errors?.total)
  // Com varredura em curso, Iniciar de outra seleção fica bloqueado com aviso
  // para cancelar antes (card #837, aceite 4); a repetição da mesma seleção
  // continua valendo como retry idempotente que mostra a existente.
  const liveSweep = activeSweep && NON_TERMINAL.has(activeSweep.state) ? activeSweep : null
  const liveAxes = liveSweep?.snapshot?.axes ?? null
  // A janela do snapshot também ancora o bloqueio: período igual com datas
  // divergentes (ex.: catálogo/janela re-resolvida) é outra seleção.
  const liveStartDate = liveSweep?.snapshot?.start_date ?? null
  const liveEndDate = liveSweep?.snapshot?.end_date ?? null
  const draftStartDate = preflight?.start_date ?? null
  const draftEndDate = preflight?.end_date ?? null
  // A igualdade de escopo ancora o bloqueio: mesmo período com datas
  // divergentes (ex.: catálogo/janela re-resolvida) é outra seleção.
  const sameScopeAsLive = Boolean(
    liveSweep &&
      liveAxes &&
      sameStringSet(selectedTemplates, liveAxes.templates) &&
      sameStringSet(
        selectedSymbols.map((s) => s.toUpperCase()),
        (liveAxes.symbols ?? []).map((s) => s.toUpperCase()),
      ) &&
      sameStringSet(timeframes, liveAxes.timeframes) &&
      sameStringSet(directions, liveAxes.directions) &&
      (liveSweep.snapshot?.period_type ?? null) === period &&
      !(preflight != null && (draftStartDate !== liveStartDate || draftEndDate !== liveEndDate)),
  )
  const blockedOtherSelection = Boolean(liveSweep && liveAxes && !sameScopeAsLive)
  const canStart =
    recoveryStatus === 'ready' &&
    !draftFrozen &&
    !blockedOtherSelection &&
    preflight !== null &&
    Object.keys(preflight.errors || {}).length === 0 &&
    !snapshotStale
  // Card 852: mesmo escopo com live em curso nomeia a igualdade (ver
  // progresso) em vez do bloqueio genérico; só aparece com início fechado
  // para não contradizer o retry idempotente permitido.
  const sameScopeBlocked = Boolean(liveSweep && sameScopeAsLive && !canStart)
  // Card 852: preflight humano — impedimentos acionáveis em linguagem de
  // operação (nunca JSON técnico no caminho feliz).
  const impediments: string[] = []
  if (selectedTemplates.length === 0) impediments.push('Escolha ao menos 1 template.')
  if (selectedSymbols.length === 0) impediments.push('Escolha ao menos 1 símbolo.')
  if (timeframes.length === 0) impediments.push('Escolha 1 timeframe (4h ou 1d).')
  if (directions.length === 0) impediments.push('Escolha a direção Long.')
  if (overLimit) {
    impediments.push(
      `Reduza o escopo: ${axisCount} combinações passam do limite de ${preflight?.limits.max_total ?? '—'}.`,
    )
  }
  const preflightWindow =
    preflight?.start_date || preflight?.end_date
      ? ` [${fmtDate(preflight?.start_date ?? null)}, ${fmtDate(preflight?.end_date ?? null)})`
      : ''
  const ctaTotal = preflight?.valid_total ?? (draftFrozen && activeSweep ? activeSweep.total : axisCount)
  const goToProgress = useCallback(() => {
    setMode('acomp')
    window.setTimeout(() => progressHeadingRef.current?.focus(), 0)
  }, [])

  const toggleList = (list: string[], setList: (v: string[]) => void, value: string) =>
    setList(list.includes(value) ? list.filter((x) => x !== value) : [...list, value])

  // Card 852: seleção inline (busca + marcar/desmarcar, sem modal). Espelha
  // o eixo no snapshot aplicado para que o contador inline reflita na hora.
  const isInlineSelected = (axis: 'templates' | 'symbols', id: string): boolean => {
    const a = committedSelection[axis]
    return a.mode === 'all' ? !a.excluded.has(id) : a.selected.has(id)
  }
  const toggleInline = (axis: 'templates' | 'symbols', id: string) => {
    const catalog = axis === 'templates' ? templatesCatalog : symbolsCatalog
    const ids = catalog.map((i) => i.id)
    const prevAxis = committedSelection[axis]
    const selected = isInlineSelected(axis, id)
    const nextAxis = {
      ...prevAxis,
      selected: new Set(prevAxis.selected),
      excluded: new Set(prevAxis.excluded),
      catalogState: prevAxis.catalogState,
    }
    let nextSelected: string[]
    if (prevAxis.mode === 'all') {
      if (selected) nextAxis.excluded.add(id)
      else nextAxis.excluded.delete(id)
      nextSelected = ids.filter((x) => !nextAxis.excluded.has(x))
    } else {
      if (selected) nextAxis.selected.delete(id)
      else nextAxis.selected.add(id)
      nextSelected = [...nextAxis.selected]
    }
    if (axis === 'templates') setSelectedTemplates(nextSelected)
    else setSelectedSymbols(nextSelected)
    setCommittedSelection((prev) => ({ ...prev, [axis]: nextAxis }))
  }

  // ---------- Sweep ----------
  const rotateDraftKey = useCallback(() => {
    // A chave do rascunho aposenta com a run morta (card #837): o próximo
    // Iniciar sempre começa uma varredura nova, mesmo com seleção igual.
    const next = newDraftKey()
    setDraftKey(next)
    persistDraftKey(next)
  }, [])

  // Card 852: top-5 travadas do sweep em curso para o modo Acompanhar.
  // Separadas de `rows` para não corromper o leaderboard do Decidir.
  // Definido antes de startSweep/restoreSession para satisfazer dependências.
  const loadPartials = useCallback(async (sweepId: string, m: Metric) => {
    try {
      const params = new URLSearchParams({
        metric: m,
        offset: '0',
        limit: '5',
        exclude_eligibility: 'insufficient_sample',
      })
      const res = await authFetch(
        `${API_BASE_URL}/combos/discovery/sweeps/${sweepId}/leaderboard?${params.toString()}`,
      )
      if (!res.ok) return
      const data = await res.json()
      setPartials(
        (data.results || []).filter((row: LeaderboardRow) => row.eligibility !== 'insufficient_sample'),
      )
    } catch {
      /* parciais são auxiliares; o progresso segue */
    }
  }, [])

  const startSweep = useCallback(async () => {
    if (!preflight) return
    setBusy(true)
    setSnapshotStale(false)
    setStartError(null)
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
          idempotency_key: draftKey,
        }),
      })
      const data = await res.json()
      if (!res.ok) {
        if (res.status === 403) {
          setPermissionDenied(true)
          return
        }
        const detail = errorDetail(data, START_FAILURE_FALLBACK)
        // Roteamento do 409 pelo código de máquina `error`; `detail` segue
        // só como texto de exibição (card #837, P1 code-reviewer).
        const startErrorCode =
          data && typeof data === 'object' && typeof (data as Record<string, unknown>).error === 'string'
            ? String((data as Record<string, unknown>).error).toLowerCase()
            : ''
        if (res.status === 409 && startErrorCode.includes('stale')) {
          setSnapshotStale(true)
        } else if (res.status === 409 && (startErrorCode.includes('live sweep') || startErrorCode.includes('idempotency'))) {
          showToast('Há uma varredura em execução', `${detail} Nada foi criado.`)
          return
        } else {
          setStartError(detail)
        }
        showToast('Não foi possível iniciar', detail)
        return
      }
      // Pós-terminal, o servidor deriva a chave efetiva da varredura nova; o
      // rascunho adota para que a repetição vire retry idempotente.
      const effectiveKey =
        data && typeof data === 'object'
          ? (data as Record<string, unknown>).idempotency_key
          : null
      if (typeof effectiveKey === 'string' && effectiveKey.length >= 8) {
        setDraftKey(effectiveKey)
        persistDraftKey(effectiveKey)
      }
      const isRetry =
        data && typeof data === 'object'
          ? (data as Record<string, unknown>).idempotent_retry === true
          : false
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
      focusStartedSweepRef.current = true
      pollRevRef.current += 1
      // A live recém-criada é a fonte da verdade (card #837): o rascunho adota
      // a seleção efetiva do servidor para que draft==live e a nota de bloqueio
      // não persista sobre o próprio rascunho congelado.
      if (fullSweep.snapshot?.axes) hydrateFromSweep(fullSweep)
      activeSweepRef.current = fullSweep
      setActiveSweep(fullSweep)
      if (!viewSweep) setViewSweep(fullSweep)
      setMetric(draftMetric)
      setDraftFrozen(true)
      setPage(1)
      // Card 852: iniciar colapsa o rascunho e trava no sweep em curso —
      // o modo vira Acompanhando e as parciais (top-5) vêm do leaderboard.
      setMode('acomp')
      setExpandedRows(new Set())
      void loadPartials(fullSweep.sweep_id, draftMetric)
      if (!viewSweep) {
        setRows([])
        setTotalMatched(0)
        setTotalAvailable(0)
      }
      showToast(
        isRetry ? 'Varredura já em andamento' : 'Varredura iniciada',
        isRetry
          ? 'Mostrando a existente — nenhuma duplicata foi criada.'
          : 'Nova varredura da seleção da tela; o progresso aparece acima.',
      )
      void loadHistory()
    } finally {
      setBusy(false)
    }
  }, [preflight, selectedTemplates, selectedSymbols, timeframes, directions, period, draftMetric, draftKey, hydrateFromSweep, loadHistory, loadPartials, showToast, viewSweep])

  useEffect(() => {
    if (!activeSweep || !focusStartedSweepRef.current) return
    focusStartedSweepRef.current = false
    const frame = window.requestAnimationFrame(() => {
      const heading = progressHeadingRef.current
      if (!heading) return
      heading.focus({ preventScroll: true })
      heading.scrollIntoView({ behavior: 'smooth', block: 'center' })
    })
    return () => window.cancelAnimationFrame(frame)
  }, [activeSweep])

  const loadLeaderboard = useCallback(
    async (sweepId: string, m: Metric, symbol: string, timeframe: string, direction: string, pg: number, silent = false) => {
      const req = ++lbReqRef.current
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
        if (req !== lbReqRef.current) return
        if (!res.ok) {
          if (res.status === 401) {
            setSessionExpired(true)
            return
          }
          if (res.status === 403) {
            setPermissionDenied(true)
            return
          }
          setLbError(true)
          return
        }
        const data = await res.json()
        if (req !== lbReqRef.current) return
        setRows(data.results || [])
        setTotalMatched(data.total || 0)
        setTotalAvailable(data.unfiltered_total ?? data.total ?? 0)
      } catch {
        if (req !== lbReqRef.current) return
        setLbError(true)
      } finally {
        if (req === lbReqRef.current) setLbLoading(false)
      }
    },
    [],
  )

  const restoreSession = useCallback(async (opts?: { focus?: boolean }) => {    setRecoveryStatus('loading')
    try {
      const [activeRes] = await Promise.all([
        authFetch(`${API_BASE_URL}/combos/discovery/sweeps/active`),
        loadHistory(),
      ])
      if (!activeRes.ok) {
        if (activeRes.status === 401) setSessionExpired(true)
        if (activeRes.status === 403) setPermissionDenied(true)
        setRecoveryStatus('error')
        return
      }
      const data = await activeRes.json()
      const sweeps: Sweep[] = Array.isArray(data?.sweeps) ? data.sweeps : []
      const newest = sweeps[0]
      if (!newest) {
        pollRevRef.current += 1
        activeSweepRef.current = null
        setActiveSweep(null)
        setReconnected(false)
        setRecoveryStatus('ready')
        return
      }
      if (TERMINAL.has(newest.state)) {
        pollRevRef.current += 1
        activeSweepRef.current = null
        setActiveSweep(null)
        setViewSweep(newest)
        viewOriginRef.current = 'auto'
        rotateDraftKey()
        setRecoveryStatus('ready')
        setPage(1)
        setFSymbol('all')
        setFTimeframe('all')
        setFDirection('all')
        await loadLeaderboard(newest.sweep_id, 'calmar_ratio', 'all', 'all', 'all', 1)
        return
      }
      const ok = hydrateFromSweep(newest)
      if (!ok) {
        setRecoveryStatus('error')
        return
      }
      pollRevRef.current += 1
      activeSweepRef.current = newest
      setActiveSweep(newest)
      if (newest.updated_at) appliedUpdatedAtRef.current[newest.sweep_id] = newest.updated_at
      if (viewOriginRef.current === 'auto') {
        setViewSweep(newest)
        setMetric('calmar_ratio')
        setPage(1)
        setFSymbol('all')
        setFTimeframe('all')
        setFDirection('all')
        await loadLeaderboard(newest.sweep_id, 'calmar_ratio', 'all', 'all', 'all', 1)
      }
      // Card 852: recuperação com live em curso abre no modo Acompanhar.
      setMode('acomp')
      void loadPartials(newest.sweep_id, 'calmar_ratio')
      setReconnected(true)
      setRecoveryStatus('ready')
      if (opts?.focus) {
        window.setTimeout(() => progressHeadingRef.current?.focus(), 0)
      }
    } catch {
      setRecoveryStatus('error')
    }
  }, [hydrateFromSweep, loadHistory, loadLeaderboard, loadPartials, rotateDraftKey])

  useEffect(() => {
    void restoreSession()
  }, [restoreSession])

  const refreshSweep = useCallback(async () => {
    const live = activeSweepRef.current
    if (!live || TERMINAL.has(live.state)) return
    const sweepId = live.sweep_id
    const rev = ++pollRevRef.current
    pollInFlightRef.current = true
    try {
      const res = await authFetch(`${API_BASE_URL}/combos/discovery/sweeps/${sweepId}`)
      if (rev !== pollRevRef.current) return
      if (activeSweepRef.current?.sweep_id !== sweepId) return
      if (!res.ok) {
        if (res.status === 401) {
          setSessionExpired(true)
          if (pollRef.current !== null) {
            window.clearInterval(pollRef.current)
            pollRef.current = null
          }
          return
        }
        if (res.status === 403) setPermissionDenied(true)
        return
      }
      const data: Sweep = await res.json()
      if (rev !== pollRevRef.current) return
      if (activeSweepRef.current?.sweep_id !== sweepId) return
      const prevApplied = appliedUpdatedAtRef.current[sweepId]
      if (prevApplied && data.updated_at && data.updated_at < prevApplied) return
      if (data.updated_at) appliedUpdatedAtRef.current[sweepId] = data.updated_at
      if (TERMINAL.has(data.state)) {
        activeSweepRef.current = data
        setActiveSweep(data)
        setViewSweep(data)
        setDraftFrozen(false)
        rotateDraftKey()
        setFSymbol('all')
        setFTimeframe('all')
        setFDirection('all')
        setPage(1)
        await loadLeaderboard(data.sweep_id, metric, 'all', 'all', 'all', 1, true)
        void loadHistory()
        return
      }
      activeSweepRef.current = data
      setActiveSweep(data)
    } catch {
      /* poll continua */
    } finally {
      if (rev === pollRevRef.current) pollInFlightRef.current = false
    }
  }, [metric, loadLeaderboard, loadHistory, rotateDraftKey])

  useEffect(() => {
    if (!activeSweep || TERMINAL.has(activeSweep.state) || sessionExpired) {
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
  }, [activeSweep, refreshSweep, sessionExpired])

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
    async (sweepId: string, origin: 'user' | 'auto' = 'user') => {
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
        viewOriginRef.current = origin
        setViewSweep(data)
        // Card 852: escolha do usuário abre o Decidir; o auto-carregamento
        // inicial não arranca o operador do Montar (sem sweep ativo) — só
        // vai ao Acompanhar se o sweep auto-carregado estiver em curso.
        if (origin === 'user') setMode('decidir')
        else if (NON_TERMINAL.has(data.state)) setMode('acomp')
        if (NON_TERMINAL.has(data.state)) {
          pollRevRef.current += 1
          activeSweepRef.current = data
          setActiveSweep(data)
        }
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
    const nextKey = newDraftKey()
    setDraftKey(nextKey)
    persistDraftKey(nextKey)
    setDraftFrozen(false)
    setCancelConfirmOpen(false)
    // Card 852: novo rascunho volta ao modo Montar (live preservada).
    setMode('montar')
    showToast('Novo rascunho', 'Sweep ativo preservado no histórico; configurador liberado.')
  }, [showToast])

  useEffect(() => {
    if (recoveryStatus !== 'ready') return
    if (!viewSweep && history.length > 0) {
      void selectHistory(history[0].sweep_id, 'auto')
    }
  }, [history, viewSweep, selectHistory, recoveryStatus])

  // Filtros / paginação do leaderboard
  const applyFilters = useCallback(
    (m: Metric, symbol: string, timeframe: string, direction: string, pg: number) => {
      if (!viewSweep) return
      setExpandedRows(new Set())
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

  const closeDiscard = useCallback((returnFocus = true) => {
    setDiscardTarget(null)
    if (returnFocus) {
      window.setTimeout(() => discardTriggerRef.current?.focus(), 0)
    }
  }, [])

  const discard = useCallback(async () => {
    if (!discardTarget) return
    setDiscarding(true)
    try {
      const res = await authFetch(
        `${API_BASE_URL}/combos/discovery/results/${discardTarget.result_id}/discard`,
        { method: 'POST' },
      )
      const data = await res.json().catch(() => null)
      if (!res.ok) {
        if (res.status === 403) {
          setPermissionDenied(true)
          return
        }
        showToast('Falha na exclusão', errorDetail(data, 'Não foi possível excluir o resultado.'))
        return
      }
      closeDiscard(false)
      showToast(
        'Resultado excluído.',
        `O candidato saiu do ranking da varredura #${viewSweep?.sweep_id ?? '—'}.`,
      )
      setPage(1)
      applyFilters(metric, fSymbol, fTimeframe, fDirection, 1)
    } finally {
      setDiscarding(false)
    }
  }, [discardTarget, showToast, closeDiscard, viewSweep, applyFilters, metric, fSymbol, fTimeframe, fDirection])

  useEffect(() => {
    if (!discardTarget) return
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        e.preventDefault()
        closeDiscard(true)
        return
      }
      if (e.key === 'Tab' && discardModalRef.current) {
        const focusables = discardModalRef.current.querySelectorAll<HTMLElement>('button:not(:disabled), [href]')
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
    const t = window.setTimeout(
      () => discardModalRef.current?.querySelector<HTMLElement>('[data-testid="confirm-discard"]')?.focus(),
      30,
    )
    return () => {
      document.removeEventListener('keydown', onKey, true)
      window.clearTimeout(t)
    }
  }, [discardTarget, closeDiscard])

  useEffect(() => {
    const previous = previousActiveStateRef.current
    if (activeSweep && previous && !TERMINAL.has(previous) && TERMINAL.has(activeSweep.state)) {
      // Card 852: o terminal leva ao modo Decidir; o foco vai ao título do
      // leaderboard (o progresso sai de cena com o modo Acompanhar).
      setMode('decidir')
      window.setTimeout(() => leaderboardTitleRef.current?.focus(), 0)
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

  // Card 852: bloco inline por eixo (busca + marcar/desmarcar, sem modal).
  const renderInlineAxis = (axis: 'templates' | 'symbols') => {
    const catalog = axis === 'templates' ? templatesCatalog : symbolsCatalog
    const query = inlineQuery[axis].toLowerCase()
    const filtered = query
      ? catalog.filter(
          (item) => item.label.toLowerCase().includes(query) || item.id.toLowerCase().includes(query),
        )
      : catalog
    const shown = filtered.slice(0, 30)
    const searchLabel = axis === 'templates' ? 'Buscar templates' : 'Buscar símbolos'
    return (
      <div className="mt-3">
        <input
          type="search"
          value={inlineQuery[axis]}
          disabled={draftFrozen}
          onChange={(e) => setInlineQuery((prev) => ({ ...prev, [axis]: e.target.value }))}
          placeholder={searchLabel}
          aria-label={searchLabel}
          data-testid={axis === 'templates' ? 'inline-templates-search' : 'inline-symbols-search'}
          className="w-full rounded-md border border-[var(--border-default)] bg-[var(--bg-input)] px-3 py-2 text-sm text-[var(--text-primary)]"
        />
        {catalog.length === 0 ? (
          <p className="mt-2 text-xs text-[var(--text-tertiary)]">Carregando catálogo…</p>
        ) : (
          <div
            role="group"
            aria-label={`${axis === 'templates' ? 'Templates' : 'Símbolos'} (seleção inline)`}
            className="mt-2 flex max-h-[190px] flex-col gap-1.5 overflow-auto"
          >
            {shown.map((item) => (
              <label
                key={item.id}
                className="flex min-h-[44px] cursor-pointer items-center gap-2.5 rounded-md border border-[var(--border-default)] bg-[var(--bg-primary)] px-3 py-2 text-[13px] text-[var(--text-secondary)]"
              >
                <input
                  type="checkbox"
                  checked={isInlineSelected(axis, item.id)}
                  disabled={draftFrozen}
                  onChange={() => toggleInline(axis, item.id)}
                  className="h-[18px] w-[18px] shrink-0 accent-[#fcd535]"
                />
                <span className="min-w-0 truncate">{item.label}</span>
              </label>
            ))}
          </div>
        )}
        {filtered.length > shown.length ? (
          <p className="mt-1.5 text-[11px] text-[var(--text-tertiary)]">
            Mostrando {shown.length} de {filtered.length} — refine a busca.
          </p>
        ) : null}
      </div>
    )
  }

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

        {/* Card 852 — 1 modo visível por vez */}
        <div
          role="tablist"
          aria-label="Modos da Descoberta"
          data-testid="discovery-modes"
          onKeyDown={(e) => {
            if (e.key !== 'ArrowRight' && e.key !== 'ArrowLeft') return
            e.preventDefault()
            const order: Array<'montar' | 'acomp' | 'decidir'> = ['montar', 'acomp', 'decidir']
            const enabled = order.filter((m) =>
              m === 'montar' ? true : m === 'acomp' ? liveSweep != null : viewSweep != null,
            )
            const current = enabled.indexOf(mode)
            const next = enabled[(current + (e.key === 'ArrowRight' ? 1 : -1) + enabled.length) % enabled.length]
            if (next) {
              setMode(next)
              window.setTimeout(
                () => document.querySelector<HTMLElement>(`[data-mode-tab="${next}"]`)?.focus(),
                0,
              )
            }
          }}
          className="mb-5 grid grid-cols-3 overflow-hidden rounded-lg border border-[var(--border-default)] bg-[var(--bg-elevated)]"
        >
          {(
            [
              { id: 'montar', label: 'Montar', enabled: true },
              {
                id: 'acomp',
                label: `Acompanhando #${liveSweep ? liveSweep.sweep_id.slice(0, 8) : '—'}`,
                enabled: liveSweep != null,
              },
              { id: 'decidir', label: 'Decidir', enabled: viewSweep != null },
            ] as const
          ).map((tab) => (
            <button
              key={tab.id}
              type="button"
              role="tab"
              id={`tab-${tab.id}`}
              aria-selected={mode === tab.id}
              aria-controls={`panel-${tab.id}`}
              tabIndex={mode === tab.id ? 0 : -1}
              disabled={!tab.enabled}
              data-mode-tab={tab.id}
              onClick={() => setMode(tab.id)}
              className={`min-h-[48px] border-0 px-2 py-3 text-[13px] font-semibold leading-tight ${
                mode === tab.id
                  ? 'bg-[rgba(252,213,53,0.12)] text-[var(--accent-primary)] shadow-[inset_0_-2px_0_var(--accent-primary)]'
                  : 'bg-[var(--bg-elevated)] text-[var(--text-tertiary)]'
              } disabled:cursor-not-allowed disabled:opacity-40`}
            >
              {tab.label}
            </button>
          ))}
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

        {recoveryStatus === 'loading' || recoveryStatus === 'error' || (reconnected && activeSweep && !TERMINAL.has(activeSweep.state)) ? (
          <div
            className={`recovery-banner mb-4 ${recoveryStatus === 'error' ? 'error' : ''}`}
            role="status"
            aria-live="polite"
            data-testid="recovery-banner"
          >
            <RefreshCw className="mt-0.5 h-4 w-4 shrink-0" />
            <div>
              <strong>
                {recoveryStatus === 'loading'
                  ? 'Verificando varredura ativa…'
                  : recoveryStatus === 'error'
                    ? 'Não foi possível verificar a varredura ativa'
                    : activeSweep && TERMINAL.has(activeSweep.state)
                      ? 'Sweep reconciliado nesta sessão'
                      : 'Varredura ativa recuperada do servidor'}
              </strong>
              <span>
                {recoveryStatus === 'loading'
                  ? 'O servidor está confirmando o estado antes de liberar um novo rascunho.'
                  : recoveryStatus === 'error'
                    ? 'O sweep continua protegido no servidor. Tente novamente antes de iniciar outra run.'
                    : 'F5 não inicia outra run. O snapshot segue congelado enquanto o sweep continua.'}
              </span>
            </div>
            {recoveryStatus === 'error' ? (
              <button
                type="button"
                className="ml-auto inline-flex min-h-[44px] shrink-0 items-center justify-center rounded-md border border-[var(--border-default)] bg-[var(--bg-elevated)] px-3 text-sm font-semibold"
                data-testid="recovery-retry"
                onClick={() => void restoreSession({ focus: true })}
              >
                Tentar novamente
              </button>
            ) : null}
          </div>
        ) : null}

        {/* Sessão expirada — fora do switch de modos (card 852: vale em
            Montar/Acompanhar/Decidir; o poll pode expirar fora do Decidir) */}
        {sessionExpired ? (
          <div className="mb-4 rounded-lg border border-[rgba(245,158,11,0.4)] bg-[rgba(245,158,11,0.07)] p-3.5" data-testid="session-expired">
            <p className="text-sm font-semibold text-[var(--text-secondary)]">Sessão expirada</p>
            <p className="mt-1 text-xs text-[var(--text-tertiary)]">
              Seu acesso expirou enquanto a página estava aberta. O sweep continua no servidor; recarregue para retomar.
            </p>
            <button
              type="button"
              onClick={() => window.location.reload()}
              className="mt-2.5 inline-flex min-h-[44px] items-center gap-1.5 rounded-md border border-[var(--border-default)] bg-[var(--bg-secondary)] px-3.5 text-xs font-semibold text-[var(--text-secondary)]"
            >
              <RefreshCw className="h-3.5 w-3.5" />
              Recarregar página
            </button>
          </div>
        ) : null}

        {/* Progress card — modo Acompanhar (1 visível por vez) */}
        {activeSweep && mode === 'acomp' ? (
          <section
            role="tabpanel"
            id="panel-acomp"
            aria-labelledby="tab-acomp"
            data-testid="mode-acomp"
          >
          <section
            className="mb-4 rounded-xl border border-[var(--border-default)] bg-[var(--bg-elevated)]"
            aria-labelledby="progress-heading"
            data-testid="sweep-progress"
          >
            <div className="flex items-start justify-between gap-4 border-b border-[var(--border-default)] px-5 py-4">
              <div>
                <h2 className="text-lg font-semibold">
                  Sweep ativo · <span className="font-mono">#{activeSweep.sweep_id}</span>
                </h2>
                <p className="mt-1 text-xs text-[var(--text-tertiary)]">
                  Reconectado ao servidor · snapshot <span className="font-mono">{snapshotLabel(activeSnapshotHash, activeSweep.total)}</span>
                  {' · '}separado do histórico exibido
                </p>
              </div>
              <span
                className={`inline-flex min-h-[28px] items-center rounded border px-2 py-1 text-[11px] font-bold ${
                  activeSweep.state === 'paused'
                    ? 'border-[rgba(245,158,11,0.42)] text-[#fbbf24]'
                    : TERMINAL.has(activeSweep.state)
                      ? 'border-[var(--border-default)] text-[var(--text-tertiary)]'
                      : 'border-[rgba(59,130,246,0.42)] text-[#93c5fd]'
                }`}
                data-testid="active-state-chip"
              >
                {activeSweep.state === 'running' ? 'EM CURSO' : activeSweep.state.toUpperCase()}
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
                    {activeSweep.processed} processadas = {activeSweep.succeeded} sucesso + {activeSweep.failed} falha + {activeSweep.skipped} ignoradas + {activeSweep.insufficient_sample ?? 0} amostra insuficiente
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
                        ? 'border-[rgba(252,213,53,0.45)] bg-[rgba(252,213,53,0.08)] text-[var(--accent-primary)]'
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

          {/* Rascunho colapsado + parciais travadas (fora do switch: sem paginação, sem re-perguntar) */}
          <div
            className="mb-4 rounded-lg border border-[var(--border-default)] bg-[var(--bg-secondary)] p-3.5 text-xs text-[var(--text-tertiary)]"
            data-testid="draft-collapsed"
          >
            Rascunho congelado:{' '}
            {(() => {
              const axes = activeSweep.snapshot?.axes
              const t = axes ? axes.templates.length : selectedTemplates.length
              const s = axes ? axes.symbols.length : selectedSymbols.length
              const tf = axes && axes.timeframes.length ? axes.timeframes.join(' + ') : timeframes.join(' + ')
              return `${t} templates · ${s} símbolos · ${tf || '—'} · Long · ${periodLabel}`
            })()}{' '}
            —{' '}
            <button
              type="button"
              onClick={newDraft}
              className="font-semibold text-[var(--accent-primary)] underline"
            >
              novo rascunho
            </button>
          </div>

          <section
            className="mb-4 overflow-hidden rounded-xl border border-[var(--border-default)] bg-[var(--bg-elevated)]"
            aria-label="Parciais travadas do sweep em curso"
          >
            <div className="border-b border-[var(--border-default)] p-5">
              <h2 className="text-lg font-semibold">Parciais · top-5 travadas</h2>
              <p className="mt-1 text-xs text-[var(--text-tertiary)]">
                Ranking travado na varredura <span className="font-mono">#{activeSweep.sweep_id}</span> — parciais abaixo, sem re-perguntar o rascunho. Todo GO acima de todo NO-GO.
              </p>
            </div>
            {partials.length > 0 ? (
              <div className="overflow-x-auto" tabIndex={0} role="region" aria-label="Tabela rolável de parciais">
                <table className="discovery-table" data-testid="partials-table">
                  <thead>
                    <tr>
                      <th scope="col">Rank</th>
                      <th scope="col">Candidato</th>
                      <th scope="col" aria-label="Calmar (CAGR anual do calendário ÷ Max DD)">
                        <span>Calmar</span>
                        <span className="th-hint">CAGR ÷ Max DD</span>
                      </th>
                      <th scope="col" aria-label="Maximum Drawdown">Max DD</th>
                      <th scope="col" aria-label="negócios / cobertura">
                        <span>Trades/cobertura</span>
                        <span className="th-hint">negócios · velas</span>
                      </th>
                      <th scope="col" aria-label="Sharpe">
                        <span>Sharpe</span>
                      </th>
                      <th scope="col" aria-label="Win rate (taxa de acerto)">
                        <span>Win%</span>
                        <span className="th-hint">acerto</span>
                      </th>
                      <th scope="col" aria-label="Retorno (CAGR) anualizado da varredura">
                        <span>CAGR</span>
                        <span className="th-hint">anualizado</span>
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    {partials.slice(0, 5).map((row) => {
                      const verdict = walkForwardStatus(row)
                      const calmarText = fmtCalmar(row.calmar_ratio)
                      const easy = gridEasyMetrics(row, calmarText === 'N/A')
                      return (
                      <tr
                        key={row.result_id}
                        className="result-row"
                        data-verdict={verdict ?? undefined}
                        data-testid={
                          row.result_id === 'RS-B109ED2C80'
                            ? 'partial-nogo'
                            : row.rank === 1
                              ? 'partial-go-1'
                              : calmarText === 'N/A'
                                ? 'partial-na'
                                : undefined
                        }
                      >
                        <td className="rank-cell" data-label="Rank">
                          <span className="rank-cell-value">{row.rank ?? '—'}</span>
                        </td>
                        <td className="candidate-cell" data-label="Candidato">
                          <strong className="candidate-name">{row.display_name || row.template_id}</strong>
                          <span className="candidate-meta">{row.symbol} · {row.timeframe} · {row.direction === 'long' ? 'Long' : 'Short'}</span>
                          <WalkForwardSeal status={verdict} />
                        </td>
                        <td className={`number ${calmarText === 'N/A' ? 'na' : ''}`} data-label="Calmar">{calmarText}</td>
                        <td className="number negative" data-label="Maximum Drawdown">{fmtDrawdown(row.max_drawdown)}</td>
                        <td className="number" data-label="negócios / cobertura">{row.trades_count ?? 'N/A'} · {fmtPct(row.coverage)}</td>
                        <td
                          className={`number ${easy.sharpeNa ? 'na' : ''}`}
                          data-label="Sharpe"
                          data-testid={
                            row.rank === 1
                              ? 'partial-sharpe-1'
                              : easy.sharpeNa
                                ? `partial-sharpe-na-${row.result_id}`
                                : undefined
                          }
                        >
                          {easy.sharpe}
                        </td>
                        <td className={`number ${easy.winNa ? 'na' : ''}`} data-label="Win rate">{easy.win}</td>
                        <td
                          className={`number ${easy.cagrNa ? 'na' : row.cagr != null && row.cagr > 0 ? 'positive' : ''}`}
                          data-label="Retorno (CAGR)"
                        >
                          {easy.cagr}
                        </td>
                      </tr>
                      )
                    })}
                  </tbody>
                </table>
              </div>
            ) : (
              <p className="p-5 text-sm text-[var(--text-tertiary)]" data-testid="partials-empty">
                Parciais ainda carregando — o progresso acima já acompanha a varredura.
              </p>
            )}
          </section>
          </section>
        ) : null}

        {/* Config layout — modo Montar (1 visível por vez) */}
        {mode === 'montar' ? (
        <section role="tabpanel" id="panel-montar" aria-labelledby="tab-montar" data-testid="mode-montar" className="grid grid-cols-1 items-start gap-4 lg:grid-cols-[minmax(0,1fr)_330px]" aria-label="Novo rascunho de varredura">
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
              {/* Templates — summary card */}
              <section className="min-w-0 rounded-lg border border-[var(--border-default)] bg-[#181a20] p-4">
                <div className="flex items-start justify-between gap-3">
                  <div className="min-w-0">
                    <h3 className="text-sm font-semibold text-[var(--text-secondary)]">Templates</h3>
                    <p className="mt-0.5 text-xs text-[var(--text-muted)]" data-testid="template-count">{selectionSummary('templates').count}</p>
                    <p className="mt-0.5 text-[11px] text-[#bfdbfe]" data-testid="template-axis-status">{selectionSummary('templates').detail}</p>
                  </div>
                  <button
                    type="button"
                    onClick={(e) => { workbenchTriggerRef.current = e.currentTarget; setWorkbenchTrigger('templates'); setWorkbenchOpen(true) }}
                    disabled={draftFrozen}
                    className="inline-flex min-h-[44px] items-center gap-1.5 rounded-md border border-[var(--border-default)] bg-[var(--bg-secondary)] px-3 text-xs font-semibold text-[var(--text-secondary)] hover:bg-[var(--bg-input)] disabled:opacity-40"
                    data-testid="edit-templates"
                    aria-haspopup="dialog"
                    aria-controls="selection-workbench"
                  >
                    <Edit3 className="h-3.5 w-3.5" />
                    Edição avançada
                  </button>
                </div>
                <div className="mt-2.5 flex min-h-[32px] gap-1.5 overflow-hidden">
                  {selectionSummary('templates').chips.map((label, idx) => (
                    <span key={`tpl-${label}-${idx}`} className="inline-flex min-h-[28px] max-w-[160px] items-center rounded border border-[var(--border-default)] bg-[var(--bg-primary)] px-2 py-1 text-[11px] text-[var(--text-secondary)] overflow-hidden text-ellipsis whitespace-nowrap">{label}</span>
                  ))}
                  {selectionSummary('templates').extra ? <span className="inline-flex min-h-[28px] items-center rounded border border-dashed border-[var(--border-default)] px-2 py-1 text-[11px] text-[var(--text-tertiary)]">{selectionSummary('templates').extra}</span> : null}
                </div>
                {renderInlineAxis('templates')}
              </section>

              {/* Symbols — summary card */}
              <section className="min-w-0 rounded-lg border border-[var(--border-default)] bg-[#181a20] p-4">
                <div className="flex items-start justify-between gap-3">
                  <div className="min-w-0">
                    <h3 className="text-sm font-semibold text-[var(--text-secondary)]">Símbolos</h3>
                    <p className="mt-0.5 text-xs text-[var(--text-muted)]" data-testid="symbol-count">{selectionSummary('symbols').count}</p>
                    <p className="mt-0.5 text-[11px] text-[#bfdbfe]" data-testid="symbol-axis-status">{selectionSummary('symbols').detail}</p>
                  </div>
                  <button
                    type="button"
                    onClick={(e) => { workbenchTriggerRef.current = e.currentTarget; setWorkbenchTrigger('symbols'); setWorkbenchOpen(true) }}
                    disabled={draftFrozen}
                    className="inline-flex min-h-[44px] items-center gap-1.5 rounded-md border border-[var(--border-default)] bg-[var(--bg-secondary)] px-3 text-xs font-semibold text-[var(--text-secondary)] hover:bg-[var(--bg-input)] disabled:opacity-40"
                    data-testid="edit-symbols"
                    aria-haspopup="dialog"
                    aria-controls="selection-workbench"
                  >
                    <Edit3 className="h-3.5 w-3.5" />
                    Edição avançada
                  </button>
                </div>
                <div className="mt-2.5 flex min-h-[32px] gap-1.5 overflow-hidden">
                  {selectionSummary('symbols').chips.map((label, idx) => (
                    <span key={`sym-${label}-${idx}`} className="inline-flex min-h-[28px] max-w-[160px] items-center rounded border border-[var(--border-default)] bg-[var(--bg-primary)] px-2 py-1 text-[11px] text-[var(--text-secondary)] overflow-hidden text-ellipsis whitespace-nowrap">{label}</span>
                  ))}
                  {selectionSummary('symbols').extra ? <span className="inline-flex min-h-[28px] items-center rounded border border-dashed border-[var(--border-default)] px-2 py-1 text-[11px] text-[var(--text-tertiary)]">{selectionSummary('symbols').extra}</span> : null}
                </div>
                {renderInlineAxis('symbols')}
              </section>

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

              {/* Direção — card 852: short fora do caminho feliz até haver dados */}
              <fieldset disabled={draftFrozen} className="min-w-0 border-0 p-0">
                <legend className="mb-2 block text-[13px] font-semibold text-[var(--text-secondary)]">Direção</legend>
                <div className="grid grid-cols-2 gap-2">
                  <label className="relative">
                    <input
                      type="checkbox"
                      className="absolute h-0 w-0 opacity-0"
                      checked={directions.includes('long')}
                      onChange={() => toggleList(directions, setDirections, 'long')}
                    />
                    <span
                      className={`flex min-h-[44px] items-center justify-center rounded-md border px-3 py-2 text-sm font-semibold ${
                        directions.includes('long')
                          ? 'border-[rgba(252,213,53,0.5)] bg-[rgba(252,213,53,0.1)] text-[var(--accent-primary)]'
                          : 'border-[var(--border-default)] bg-[var(--bg-secondary)] text-[var(--text-tertiary)]'
                      }`}
                    >
                      Long
                    </span>
                  </label>
                </div>
                <p className="mt-2 min-h-[18px] text-[11px] text-[var(--text-tertiary)]">
                  Direção: apenas Long nesta etapa. Short volta quando houver dados.
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
                  <option value="all">Todo o histórico</option>
                  <option value="2y">Últimos 2 anos</option>
                  <option value="6m">Últimos 6 meses</option>
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

          {/* Preflight humano (card 852): 3 linhas + impedimentos; técnico em details */}
          <aside className="rounded-xl border border-[var(--border-default)] bg-[var(--bg-elevated)] lg:sticky lg:top-24" aria-label="Preflight da varredura">
            <div className="flex items-start justify-between gap-4 border-b border-[var(--border-default)] px-5 py-4">
              <div>
                <h2 className="text-lg font-semibold">Preflight</h2>
                <p className="mt-1 text-xs text-[var(--text-tertiary)]" data-testid="preflight-state">
                  {preflightLoading
                    ? 'Calculando…'
                    : draftFrozen
                      ? 'Rascunho congelado'
                      : snapshotStale
                        ? 'Snapshot expirado'
                        : impediments.length > 0
                          ? 'Bloqueado — veja o que falta'
                          : preflight
                            ? 'Pronto para iniciar'
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
                <p className="mt-2 text-[13px] text-[var(--text-secondary)]" aria-live="polite" data-testid="preflight-3line">
                  {preflight ? (
                    <>
                      <b>{preflight.valid_total} combinações</b> · {fmtEstimate(preflight.valid_total)} estimado · {periodLabel}
                      {preflightWindow}
                    </>
                  ) : preflightLoading ? (
                    <>Calculando combinações…</>
                  ) : (
                    <>
                      <b>{axisCount} combinações</b> · — · {periodLabel}
                    </>
                  )}
                </p>
                {impediments.length > 0 && !preflightLoading ? (
                  <div
                    className="mt-3 rounded-md border border-[rgba(245,158,11,0.35)] bg-[rgba(245,158,11,0.06)] p-2.5 text-[11px] text-[#fbbf24]"
                    data-testid="preflight-impediments"
                  >
                    <strong className="block">Falta fazer:</strong>
                    <ul className="mt-1 list-disc pl-5 text-[var(--text-secondary)]">
                      {impediments.map((item) => (
                        <li key={item}>{item}</li>
                      ))}
                    </ul>
                  </div>
                ) : null}
                <details className="mt-3 text-[11px] text-[var(--text-muted)]">
                  <summary className="cursor-pointer rounded py-2">Detalhe técnico (fora do caminho feliz)</summary>
                  <div className="mt-1 font-mono" data-testid="planned-formula">
                    {overLimit
                      ? `${axisCount} combinações brutas`
                      : preflight
                        ? `${selectedTemplates.length} × ${selectedSymbols.length} × ${timeframes.length} × ${directions.length}${preflight.excluded_count ? ` − ${preflight.excluded_count} incompatíveis` : ''}`
                        : '—'}
                  </div>
                  {preflight && !overLimit ? (
                    <div className="mt-1" data-testid="preflight-breakdown">
                      <b className="text-[var(--text-secondary)]">{preflight.raw_total} brutas</b> · {preflight.excluded_count} excluídas ·{' '}
                      {preflight.valid_total} válidas · limite {preflight.limits.max_total}
                      <br />
                      snapshot{' '}
                      <span className="font-mono">
                        {snapshotLabel(preflight.snapshot_hash, preflight.valid_total)}
                      </span>
                    </div>
                  ) : null}
                  <div className="mt-1 flex justify-between gap-3">
                    <span>Chave do rascunho</span>
                    <b
                      className="max-w-[22ch] break-all text-right font-mono text-[var(--text-secondary)]"
                      data-testid="draft-key"
                      aria-live="polite"
                    >
                      {draftKey}
                    </b>
                  </div>
                </details>
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
                <Play className="h-4 w-4" />
                Iniciar varredura — {ctaTotal}, {fmtEstimate(ctaTotal)}
              </button>

              {blockedOtherSelection ? (
                <p
                  className="mt-3 rounded-md border border-[rgba(245,158,11,0.35)] bg-[rgba(245,158,11,0.06)] p-2.5 text-[11px] text-[#fbbf24]"
                  role="alert"
                  data-testid="live-block-note"
                >
                  {LIVE_BLOCK_COPY}{' '}
                  <button
                    type="button"
                    onClick={goToProgress}
                    data-testid="live-block-progress"
                    className="font-bold text-[var(--accent-primary)] underline"
                  >
                    ver progresso
                  </button>
                </p>
              ) : sameScopeBlocked ? (
                <p
                  className="mt-3 rounded-md border border-[rgba(245,158,11,0.35)] bg-[rgba(245,158,11,0.06)] p-2.5 text-[11px] text-[#fbbf24]"
                  role="alert"
                  data-testid="live-block-note"
                >
                  Existe varredura igual em curso —{' '}
                  <button
                    type="button"
                    onClick={goToProgress}
                    data-testid="live-block-progress"
                    className="font-bold text-[var(--accent-primary)] underline"
                  >
                    ver progresso
                  </button>
                  . Nada foi criado.
                </p>
              ) : null}

              {startError && !snapshotStale ? (
                <p
                  className="mt-3 rounded-md border border-[rgba(246,70,93,0.4)] bg-[rgba(246,70,93,0.06)] p-2.5 text-[11px] text-[var(--text-secondary)]"
                  role="alert"
                  data-testid="start-error"
                >
                  {startError}
                </p>
              ) : null}

              {overLimit ? (
                <p className="mt-3 text-xs text-[var(--text-muted)]" data-testid="over-limit-note">
                  {preflight?.errors?.total} Reduza templates, símbolos, timeframes ou direções; o preflight e a ação de início usam o mesmo total.
                </p>
              ) : (
                <p className="mt-3 flex gap-2 text-xs text-[var(--text-muted)]">
                  <Shield className="h-4 w-4 shrink-0 text-[var(--accent-cyan)]" />
                  <span>O rascunho congela após o início; nada é criado sem o preflight válido.</span>
                </p>
              )}
            </div>
          </aside>
        </section>
        ) : null}

        {/* Workbench */}
        <SelectionWorkbench
          open={workbenchOpen}
          initialAxis={workbenchTrigger}
          templates={templatesCatalog}
          symbols={symbolsCatalog}
          committed={committedSelection}
          multiplier={timeframes.length * directions.length}
          onApply={applySelectionFromWorkbench}
          onClose={() => {
            setWorkbenchOpen(false)
            setTimeout(() => workbenchTriggerRef.current?.focus(), 0)
          }}
        />

        {/* Leaderboard — modo Decidir (1 visível por vez) */}
        {viewSweep && mode === 'decidir' ? (
          <section
            role="tabpanel"
            id="panel-decidir"
            aria-labelledby="tab-decidir"
            data-testid="mode-decidir"
            className="mt-5 overflow-hidden rounded-xl border border-[var(--border-default)] bg-[var(--bg-elevated)]"
            aria-busy={lbLoading}
          >
            <div className="border-b border-[var(--border-default)] p-5">
              <div className="flex flex-col gap-2 md:flex-row md:items-start md:justify-between">
                <div>
                  <h2 id="leaderboard-title" ref={leaderboardTitleRef} tabIndex={-1} className="text-xl font-semibold">
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

              <div className="mt-4 grid grid-cols-2 items-end gap-2.5 md:grid-cols-[repeat(3,minmax(140px,1fr))_auto]">
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

            <div className="overflow-x-auto" tabIndex={0} role="region" aria-label="Tabela rolável de candidatos">
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
              <table className="discovery-table decidable" aria-describedby="leaderboard-note" data-testid="decidir-table">
                <caption className="sr-only">
                  Candidatos da varredura selecionada; ranks globais não renumeram sob filtro. Calmar é CAGR anual do calendário dividido pelo Max DD, não retorno. Trades/cobertura são negócios fechados e cobertura de velas, não taxa de acerto.
                </caption>
                <thead>
                  <tr>
                    <th scope="col">Rank global</th>
                    <th scope="col">Candidato</th>
                    <th scope="col" aria-label="Calmar (CAGR anual do calendário ÷ Max DD)">
                      <span>Calmar</span>
                      <span className="th-hint">CAGR ÷ Max DD</span>
                    </th>
                    <th scope="col" aria-label="Maximum Drawdown">Max DD</th>
                    <th scope="col" aria-label="negócios / cobertura">
                      <span>Trades/cobertura</span>
                      <span className="th-hint">negócios · velas</span>
                    </th>
                    <th scope="col" aria-label="Sharpe">
                      <span>Sharpe</span>
                    </th>
                    <th scope="col" aria-label="Win rate (taxa de acerto)">
                      <span>Win%</span>
                      <span className="th-hint">acerto</span>
                    </th>
                    <th scope="col" aria-label="Retorno (CAGR) anualizado da varredura">
                      <span>CAGR</span>
                      <span className="th-hint">anualizado</span>
                    </th>
                    <th scope="col" className="action">Ação</th>
                  </tr>
                </thead>
                <tbody>
                  {rows.map((row) => {
                    const insufficient = row.eligibility === 'insufficient_sample'
                    const lowSample = row.eligibility === 'low_sample'
                    const duplicate = row.dedup_state === 'duplicate_favorite'
                    const promoted = row.dedup_state === 'already_promoted'
                    const promoteDisabled = busy || promoting || lowSample || duplicate || promoted
                    const expanded = expandedRows.has(row.result_id)
                    const verdict = walkForwardStatus(row)
                    const calmarText = insufficient ? 'N/A' : fmtCalmar(row.calmar_ratio)
                    const easy = gridEasyMetrics(row, insufficient || calmarText === 'N/A')
                    return (
                      <tr
                        key={row.result_id}
                        className="result-row"
                        data-eligibility={row.eligibility}
                        data-verdict={verdict ?? undefined}
                        data-testid={insufficient ? 'row-insufficient' : row.result_id === 'RS-B109ED2C80' ? 'row-nogo' : undefined}
                      >
                        <td className="rank-cell" data-label="Rank global">
                          <span className="rank-cell-value">{row.rank ?? '—'}</span>
                        </td>
                        <td className="candidate-cell" data-label="Candidato">
                          <div className="candidate-cell-min" data-testid="discovery-strategy-identity">
                            <strong className="candidate-name" data-testid="discovery-strategy-title">
                              {row.display_name || row.template_id}
                            </strong>
                            {row.description ? (
                              <span className="candidate-description" data-testid="discovery-strategy-description">
                                {row.description}
                              </span>
                            ) : null}
                            <span className="candidate-meta">
                              {row.result_id} · cobertura {insufficient ? 'N/A' : fmtPct(row.coverage)}
                              {fmtParams(row.parameters) ? ` · ${fmtParams(row.parameters)}` : ''}
                              {row.direction === 'short' ? ' · benchmark B&H long-only' : ''}
                            </span>
                            <WalkForwardSeal status={verdict} />
                            {insufficient ? (
                              <span className="sample-badge" data-testid="seal-insufficient">Amostra insuficiente</span>
                            ) : null}
                            {lowSample ? <span className="sample-badge">Baixa amostra</span> : null}
                            {duplicate ? (
                              <span className="dedup-note" title={`Promoção bloqueada: equivalente ao favorito ativo ${row.dedup_reference ?? ''}`}>
                                <Copy className="h-3 w-3" />
                                Equivale ao favorito ativo {row.dedup_reference ?? '—'}
                              </span>
                            ) : null}
                            <button
                              type="button"
                              onClick={() =>
                                setExpandedRows((prev) => {
                                  const next = new Set(prev)
                                  if (next.has(row.result_id)) next.delete(row.result_id)
                                  else next.add(row.result_id)
                                  return next
                                })
                              }
                              aria-expanded={expanded}
                              data-testid={`expand-${row.result_id}`}
                              className="mt-1 inline-flex min-h-[44px] items-center px-1 text-xs font-semibold text-[var(--accent-primary)]"
                            >
                              {expanded ? '− detalhes' : '+ detalhes'}
                            </button>
                            {expanded ? (
                              <span className="candidate-meta" data-testid={`details-${row.result_id}`}>
                                B&amp;H {fmtPct(row.benchmark_cagr)} · Δ {fmtPp(row.delta_cagr_vs_bh)} · PF {fmtNum(row.profit_factor)} ·
                                mercado {row.symbol} · {row.timeframe} · {row.direction === 'long' ? 'Long' : 'Short'}
                                {row.start_at || row.end_at ? ` · janela [${fmtDate(row.start_at)}, ${fmtDate(row.end_at)})` : ''}
                              </span>
                            ) : null}
                          </div>
                        </td>
                        <td className={`number ${calmarText === 'N/A' ? 'na' : ''} ${calmarText !== 'N/A' && row.calmar_ratio != null && row.calmar_ratio < 0 ? 'negative' : ''}`} data-label="Calmar">
                          {calmarText}
                        </td>
                        <td className={`number ${insufficient ? 'na' : 'negative'}`} data-label="Maximum Drawdown">{insufficient ? 'N/A' : fmtDrawdown(row.max_drawdown)}</td>
                        <td className={`number ${insufficient ? 'na' : ''}`} data-label="negócios / cobertura">{insufficient ? 'N/A' : `${row.trades_count ?? 'N/A'} · ${fmtPct(row.coverage)}`}</td>
                        <td
                          className={`number ${easy.sharpeNa ? 'na' : ''}`}
                          data-label="Sharpe"
                          data-testid={
                            insufficient
                              ? `decidir-sharpe-na-${row.result_id}`
                              : row.rank === 1
                                ? 'decidir-sharpe-1'
                                : easy.sharpeNa
                                  ? `decidir-sharpe-na-${row.result_id}`
                                  : undefined
                          }
                        >
                          {easy.sharpe}
                        </td>
                        <td
                          className={`number ${easy.winNa ? 'na' : ''}`}
                          data-label="Win rate"
                          data-testid={insufficient || easy.winNa ? `decidir-win-na-${row.result_id}` : undefined}
                        >
                          {easy.win}
                        </td>
                        <td
                          className={`number ${easy.cagrNa ? 'na' : row.cagr != null && row.cagr > 0 ? 'positive' : ''}`}
                          data-label="Retorno (CAGR)"
                          data-testid={
                            insufficient
                              ? `decidir-cagr-na-${row.result_id}`
                              : row.rank === 1
                                ? 'decidir-cagr-1'
                                : easy.cagrNa
                                  ? `decidir-cagr-na-${row.result_id}`
                                  : undefined
                          }
                        >
                          {easy.cagr}
                        </td>
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
                            <div className="action-stack">
                              {insufficient ? null : (
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
                              <button
                                type="button"
                                disabled={busy || discarding}
                                onClick={(event) => {
                                  discardTriggerRef.current = event.currentTarget
                                  setDiscardTarget(row)
                                }}
                                aria-haspopup="dialog"
                                aria-controls="discard-modal"
                                aria-expanded={discardTarget?.result_id === row.result_id}
                                aria-label={`Excluir resultado ${row.result_id} ${row.display_name || row.template_id}`}
                                data-testid={`discard-${row.result_id}`}
                                className="discard-action inline-flex min-h-[44px] items-center justify-center gap-1.5 rounded-md border px-3.5 text-xs font-bold border-[rgba(246,70,93,0.45)] bg-transparent text-[var(--trading-down-text)] hover:bg-[rgba(246,70,93,0.08)] disabled:cursor-not-allowed disabled:opacity-40"
                              >
                                <Trash2 className="h-3.5 w-3.5" />
                                Excluir
                              </button>
                            </div>
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
            <p className="border-t border-[var(--border-default)] px-5 py-3 text-[11px] text-[var(--text-muted)]" data-testid="column-copy">
              Calmar não é retorno: é CAGR do calendário da janela dividido pelo Max DD.{' '}
              <span className="font-mono">30 · 100%</span> = 30 negócios fechados e 100% de cobertura de velas — não é taxa de acerto.{' '}
              CAGR na grelha é o retorno anualizado da varredura, o mesmo «Retorno (CAGR)» do promover.
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
              <div className="rounded-lg border border-[var(--border-default)] bg-[var(--bg-secondary)] p-3.5" data-testid="modal-strategy-identity">
                <strong className="block" data-testid="modal-strategy-title">
                  {promoteTarget.display_name || promoteTarget.template_id}
                </strong>
                {promoteTarget.description ? (
                  <span className="mt-1 block text-sm text-[var(--text-secondary)]" data-testid="modal-strategy-description">
                    {promoteTarget.description}
                  </span>
                ) : null}
                <span className="mt-2 block text-xs text-[var(--text-tertiary)]" data-testid="modal-candidate">
                  {promoteTarget.result_id} · {promoteTarget.template_id}
                </span>
                <span className="text-xs text-[var(--text-tertiary)]" data-testid="modal-market">
                  {promoteTarget.symbol} · {promoteTarget.timeframe} · {promoteTarget.direction === 'long' ? 'Long' : 'Short'}
                </span>
              </div>
              <div className="my-4 grid grid-cols-2 gap-2.5" data-testid="modal-risk-grid">
                <div className="rounded-md border border-[var(--border-default)] bg-[var(--bg-secondary)] p-2.5">
                  <small className="block text-[var(--text-muted)]">Retorno (CAGR)</small>
                  <b className="text-[15px] tabular-nums" data-testid="modal-risk-cagr">{fmtPct(promoteTarget.cagr)}</b>
                </div>
                <div className="rounded-md border border-[var(--border-default)] bg-[var(--bg-secondary)] p-2.5">
                  <small className="block text-[var(--text-muted)]">Queda máxima</small>
                  <b className="text-[15px] tabular-nums text-[#ff8294]" data-testid="modal-risk-dd">{fmtDrawdown(promoteTarget.max_drawdown)}</b>
                </div>
                <div className="rounded-md border border-[var(--border-default)] bg-[var(--bg-secondary)] p-2.5">
                  <small className="block text-[var(--text-muted)]">Trades</small>
                  <b className="text-[15px] tabular-nums" data-testid="modal-risk-trades">{promoteTarget.trades_count ?? '—'}</b>
                </div>
                <div className="rounded-md border border-[var(--border-default)] bg-[var(--bg-secondary)] p-2.5">
                  <small className="block text-[var(--text-muted)]">Cobertura · janela</small>
                  <b className="text-[15px] tabular-nums" data-testid="modal-risk-cov">{fmtPct(promoteTarget.coverage)} · {fmtDate(promoteTarget.start_at)} – {fmtDate(promoteTarget.end_at)}</b>
                </div>
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
                <span className="mt-1 block text-[11px] text-[var(--text-tertiary)]">Onde ver depois: Favoritos → Tier 3. Reversível: retire o favorito; o histórico da varredura fica.</span>
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

      {discardTarget ? (
        <div
          className="fixed inset-0 z-[80] flex items-center justify-center bg-black/70 p-5"
          onClick={(e) => {
            if (e.target === e.currentTarget) closeDiscard(true)
          }}
        >
          <div
            ref={discardModalRef}
            id="discard-modal"
            role="dialog"
            aria-modal="true"
            aria-labelledby="discard-title"
            aria-describedby="discard-description"
            className="w-full max-w-[480px] rounded-xl border border-[var(--border-default)] bg-[var(--bg-elevated)] shadow-2xl"
          >
            <div className="flex items-start justify-between gap-4 border-b border-[var(--border-default)] p-5">
              <div>
                <h2 id="discard-title" className="text-xl font-semibold">Excluir resultado</h2>
                <p id="discard-description" className="mt-1 text-xs text-[var(--text-tertiary)]">
                  Remove só este resultado do ranking desta varredura. Não cancela a varredura e não apaga favoritos.
                </p>
              </div>
              <button
                type="button"
                onClick={() => closeDiscard(true)}
                aria-label="Fechar"
                className="grid h-11 w-11 min-h-[44px] place-items-center rounded-md border border-[var(--border-default)] bg-[var(--bg-secondary)] text-[var(--text-secondary)]"
              >
                <X className="h-4 w-4" />
              </button>
            </div>
            <div className="p-5">
              <div className="rounded-lg border border-[var(--border-default)] bg-[var(--bg-secondary)] p-3.5">
                <strong className="block">{discardTarget.display_name || discardTarget.template_id}</strong>
                <span className="mt-2 block text-xs text-[var(--text-tertiary)]">{discardTarget.result_id}</span>
              </div>
              <div className="my-4 grid grid-cols-2 gap-2.5">
                <div className="rounded-md border border-[var(--border-default)] bg-[var(--bg-secondary)] p-2.5">
                  <small className="block text-[var(--text-muted)]">Varredura</small>
                  <b className="font-mono text-xs">#{viewSweep?.sweep_id ?? '—'}</b>
                </div>
                <div className="rounded-md border border-[var(--border-default)] bg-[var(--bg-secondary)] p-2.5">
                  <small className="block text-[var(--text-muted)]">Resultado</small>
                  <b className="font-mono text-xs" data-testid="discard-modal-result">{discardTarget.result_id}</b>
                </div>
              </div>
            </div>
            <div className="flex justify-end gap-2.5 p-5 pt-0">
              <button
                type="button"
                onClick={() => closeDiscard(true)}
                className="inline-flex min-h-[44px] items-center rounded-md border border-[var(--border-default)] bg-[var(--bg-elevated)] px-4 py-2 text-sm font-semibold text-[var(--text-secondary)]"
              >
                Voltar
              </button>
              <button
                type="button"
                onClick={() => void discard()}
                disabled={discarding}
                data-testid="confirm-discard"
                className="inline-flex min-h-[44px] items-center gap-2 rounded-md border border-[rgba(246,70,93,0.55)] bg-[rgba(246,70,93,0.12)] px-4 py-2 text-sm font-bold text-[var(--trading-down-text)] disabled:opacity-50"
              >
                <Trash2 className="h-4 w-4" />
                Confirmar exclusão
              </button>
            </div>
          </div>
        </div>
      ) : null}
    </div>
  )
}
