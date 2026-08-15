import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { authFetch } from '../lib/authFetch'
import { API_BASE_URL } from '../lib/apiBase'

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
  | 'pending'
  | 'running'
  | 'paused'
  | 'cancelling'
  | 'cancelled'
  | 'failed'
  | 'partial_failure'
  | 'completed'

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

type LeaderboardRow = {
  rank: number
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
}

const TERMINAL = new Set<SweepState>(['cancelled', 'failed', 'partial_failure', 'completed'])

function fmt(v: number | null | undefined, digits = 2): string {
  if (v === null || v === undefined || Number.isNaN(v) || !Number.isFinite(v)) return 'N/A'
  return v.toFixed(digits)
}

export function DiscoveryPage() {
  const navigate = useNavigate()
  const [templates, setTemplates] = useState<string[]>([])
  const [templateInput, setTemplateInput] = useState('')
  const [symbolInput, setSymbolInput] = useState('')
  const [timeframes, setTimeframes] = useState<string[]>(['1d'])
  const [directions, setDirections] = useState<string[]>(['long'])
  const [startDate, setStartDate] = useState('2024-01-01')
  const [endDate, setEndDate] = useState('')
  const [periodType, setPeriodType] = useState('all')
  const [preflight, setPreflight] = useState<PreflightResult | null>(null)
  const [preflightError, setPreflightError] = useState<string | null>(null)
  const [preflightLoading, setPreflightLoading] = useState(false)
  const [sweep, setSweep] = useState<Sweep | null>(null)
  const [rows, setRows] = useState<LeaderboardRow[]>([])
  const [metric, setMetric] = useState<'calmar_ratio' | 'delta_cagr_vs_bh'>('calmar_ratio')
  const [history, setHistory] = useState<{ sweep_id: string; state: string; total: number }[]>([])
  const [busy, setBusy] = useState(false)
  const [toast, setToast] = useState<string | null>(null)
  const pollRef = useRef<number | null>(null)

  const axes = useMemo(
    () => ({
      templates: templateInput
        .split(',')
        .map((s) => s.trim())
        .filter(Boolean),
      symbols: symbolInput
        .split(',')
        .map((s) => s.trim().toUpperCase())
        .filter(Boolean),
    }),
    [templateInput, symbolInput],
  )

  const loadHistory = useCallback(async () => {
    try {
      const res = await authFetch(`${API_BASE_URL}/combos/discovery/sweeps/history`)
      if (res.ok) {
        const data = await res.json()
        setHistory(data.sweeps || [])
      }
    } catch {
      /* silencioso: histórico é auxiliar */
    }
  }, [])

  useEffect(() => {
    void loadHistory()
  }, [loadHistory])

  const runPreflight = useCallback(async () => {
    setPreflightLoading(true)
    setPreflightError(null)
    try {
      const res = await authFetch(`${API_BASE_URL}/combos/discovery/sweeps/preflight`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          templates: axes.templates,
          symbols: axes.symbols,
          timeframes,
          directions,
          start_date: startDate || null,
          end_date: endDate || null,
          period_type: periodType,
        }),
      })
      const data = await res.json()
      if (!res.ok) {
        setPreflightError(data.detail ? JSON.stringify(data.detail) : 'Falha no preflight')
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
  }, [axes.templates, axes.symbols, timeframes, directions, startDate, endDate, periodType])

  const startSweep = useCallback(async () => {
    if (!preflight) return
    setBusy(true)
    try {
      // Chave idempotente estável por intenção lógica (snapshot): retry de
      // rede/duplo clique devolve o mesmo sweep, sem duplicar trabalho.
      const key = `sweep-${preflight.snapshot_hash}`
      const res = await authFetch(`${API_BASE_URL}/combos/discovery/sweeps`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          templates: axes.templates,
          symbols: axes.symbols,
          timeframes,
          directions,
          start_date: startDate || null,
          end_date: endDate || null,
          period_type: periodType,
          snapshot_token: preflight.snapshot_token,
          snapshot_hash: preflight.snapshot_hash,
          idempotency_key: key,
        }),
      })
      const data = await res.json()
      if (!res.ok) {
        setToast(data.detail ? JSON.stringify(data.detail) : 'Falha ao iniciar varredura')
        return
      }
      setSweep(data)
      setToast('Varredura iniciada.')
      void loadHistory()
    } finally {
      setBusy(false)
    }
  }, [preflight, axes, timeframes, directions, startDate, endDate, periodType, loadHistory])

  const refreshSweep = useCallback(async () => {
    if (!sweep) return
    try {
      const res = await authFetch(`${API_BASE_URL}/combos/discovery/sweeps/${sweep.sweep_id}`)
      if (!res.ok) return
      const data = await res.json()
      setSweep(data)
      if (data.state === 'completed' || data.state === 'partial_failure' || data.state === 'failed' || data.state === 'cancelled') {
        const lb = await authFetch(
          `${API_BASE_URL}/combos/discovery/sweeps/${sweep.sweep_id}/leaderboard?metric=${metric}`,
        )
        if (lb.ok) {
          const lbData = await lb.json()
          setRows(lbData.results || [])
        }
      }
    } catch {
      /* poll continua */
    }
  }, [sweep, metric])

  useEffect(() => {
    if (!sweep || TERMINAL.has(sweep.state)) {
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
  }, [sweep, refreshSweep])

  const command = useCallback(
    async (cmd: 'pause' | 'resume' | 'cancel') => {
      if (!sweep) return
      const res = await authFetch(`${API_BASE_URL}/combos/discovery/sweeps/${sweep.sweep_id}/${cmd}`, {
        method: 'POST',
      })
      if (!res.ok) {
        const data = await res.json().catch(() => null)
        setToast(data?.detail ? JSON.stringify(data.detail) : `Falha em ${cmd}`)
        return
      }
      void refreshSweep()
    },
    [sweep, refreshSweep],
  )

  const promote = useCallback(
    async (resultId: string) => {
      setBusy(true)
      try {
        const res = await authFetch(`${API_BASE_URL}/combos/discovery/results/${resultId}/promote`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            tier: 3,
            idempotency_key: `promote-${resultId}`,
          }),
        })
        const data = await res.json().catch(() => null)
        if (!res.ok) {
          setToast(data?.detail ? JSON.stringify(data.detail) : 'Falha na promoção')
          return
        }
        setToast(`Promovido: favorito ${data.favorite_id} (tier 3).`)
        void refreshSweep()
      } finally {
        setBusy(false)
      }
    },
    [refreshSweep],
  )

  const selectHistory = useCallback(
    async (sweepId: string) => {
      setBusy(true)
      try {
        const res = await authFetch(`${API_BASE_URL}/combos/discovery/sweeps/${sweepId}`)
        if (!res.ok) return
        const data = await res.json()
        setSweep(data)
        const lb = await authFetch(
          `${API_BASE_URL}/combos/discovery/sweeps/${sweepId}/leaderboard?metric=${metric}`,
        )
        if (lb.ok) {
          const lbData = await lb.json()
          setRows(lbData.results || [])
        }
      } finally {
        setBusy(false)
      }
    },
    [metric],
  )

  const canStart = preflight !== null && Object.keys(preflight.errors || {}).length === 0
  const running = sweep !== null && !TERMINAL.has(sweep.state)

  return (
    <div className="min-h-screen bg-[#0b0e11] text-gray-100">
      <header className="h-20 flex items-center justify-between px-6 border-b border-[#2b3139] bg-[#181a20]">
        <div>
          <div className="text-white font-bold text-lg">Descoberta sistemática</div>
          <div className="text-xs text-[#929aa5]">Varredura template × símbolo × timeframe com leaderboard</div>
        </div>
        <button
          onClick={() => navigate('/combo/configure')}
          className="px-3 py-2 text-sm rounded bg-[#2b3139] hover:bg-[#363c45]"
        >
          Voltar ao Combo
        </button>
      </header>

      <main className="p-6 space-y-6">
        {toast ? (
          <div className="px-4 py-3 text-sm text-[#929aa5] border border-[#2b3139] rounded bg-[#181a20]" role="status">
            {toast}
            <button className="ml-3 text-[#fcd535]" onClick={() => setToast(null)}>×</button>
          </div>
        ) : null}

        <section className="p-4 rounded-lg border border-[#2b3139] bg-[#181a20] space-y-4">
          <h2 className="font-semibold">1 · Definir escopo da varredura</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <label className="block text-sm">
              <span className="text-[#929aa5]">Templates (separados por vírgula)</span>
              <input
                value={templateInput}
                onChange={(e) => setTemplateInput(e.target.value)}
                placeholder="multi_ma_crossover, bb_breakout"
                className="mt-1 w-full px-3 py-2 rounded bg-[#0b0e11] border border-[#2b3139]"
              />
            </label>
            <label className="block text-sm">
              <span className="text-[#929aa5]">Símbolos (separados por vírgula)</span>
              <input
                value={symbolInput}
                onChange={(e) => setSymbolInput(e.target.value)}
                placeholder="BTCUSDT, ETHUSDT, SOLUSDT"
                className="mt-1 w-full px-3 py-2 rounded bg-[#0b0e11] border border-[#2b3139]"
              />
            </label>
            <div className="flex gap-6 text-sm">
              <span className="text-[#929aa5]">Timeframes</span>
              {['4h', '1d'].map((tf) => (
                <label key={tf} className="flex items-center gap-1">
                  <input
                    type="checkbox"
                    checked={timeframes.includes(tf)}
                    onChange={() =>
                      setTimeframes((prev) =>
                        prev.includes(tf) ? prev.filter((x) => x !== tf) : [...prev, tf],
                      )
                    }
                  />
                  {tf}
                </label>
              ))}
            </div>
            <div className="flex gap-6 text-sm">
              <span className="text-[#929aa5]">Direção</span>
              {['long', 'short'].map((d) => (
                <label key={d} className="flex items-center gap-1">
                  <input
                    type="checkbox"
                    checked={directions.includes(d)}
                    onChange={() =>
                      setDirections((prev) =>
                        prev.includes(d) ? prev.filter((x) => x !== d) : [...prev, d],
                      )
                    }
                  />
                  {d}
                </label>
              ))}
            </div>
            <label className="block text-sm">
              <span className="text-[#929aa5]">Início</span>
              <input
                type="date"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
                className="mt-1 w-full px-3 py-2 rounded bg-[#0b0e11] border border-[#2b3139]"
              />
            </label>
            <label className="block text-sm">
              <span className="text-[#929aa5]">Fim (vazio = hoje)</span>
              <input
                type="date"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
                className="mt-1 w-full px-3 py-2 rounded bg-[#0b0e11] border border-[#2b3139]"
              />
            </label>
          </div>
          <div className="flex gap-3">
            <button
              onClick={() => void runPreflight()}
              disabled={preflightLoading || busy}
              className="px-4 py-2 rounded bg-[#2b3139] hover:bg-[#363c45] disabled:opacity-40"
            >
              {preflightLoading ? 'Calculando…' : 'Preflight (calcular total)'}
            </button>
            <button
              onClick={() => void startSweep()}
              disabled={!canStart || busy}
              className="px-4 py-2 rounded bg-[#fcd535] text-[#0b0e11] font-semibold disabled:opacity-40 disabled:bg-[#3a3a1f]"
            >
              Iniciar varredura
            </button>
          </div>
          {preflightError ? (
            <div className="text-sm text-[#ff8294]">{preflightError}</div>
          ) : null}
          {preflight ? (
            <div className="text-sm text-[#929aa5] space-y-1">
              <div>
                Total bruto: <span className="text-white">{preflight.raw_total}</span> · Válido:{' '}
                <span className="text-white">{preflight.valid_total}</span> · Excluído:{' '}
                <span className="text-white">{preflight.excluded_count}</span> · Limite:{' '}
                <span className="text-white">{preflight.limits.max_total}</span>
              </div>
              {Object.keys(preflight.exclusions || {}).length > 0 ? (
                <details>
                  <summary className="cursor-pointer">Exclusões ({Object.keys(preflight.exclusions).length})</summary>
                  <ul className="mt-1 list-disc list-inside">
                    {Object.entries(preflight.exclusions).map(([key, ex]) => (
                      <li key={key}>
                        {key}: {ex.reasons.join(', ')}
                      </li>
                    ))}
                  </ul>
                </details>
              ) : null}
              {Object.keys(preflight.errors || {}).length > 0 ? (
                <div className="text-[#ff8294]">
                  Erros: {JSON.stringify(preflight.errors)}
                </div>
              ) : null}
            </div>
          ) : null}
        </section>

        {sweep ? (
          <section className="p-4 rounded-lg border border-[#2b3139] bg-[#181a20] space-y-4">
            <h2 className="font-semibold">2 · Varredura ativa / selecionada</h2>
            <div className="flex flex-wrap items-center gap-4 text-sm">
              <span>
                Estado:{' '}
                <span className="px-2 py-0.5 rounded bg-[#3b82f6]/20 text-[#3b82f6]">{sweep.state}</span>
              </span>
              <span>
                Processado: <span className="text-white">{sweep.processed}</span>/{sweep.total} (ok{' '}
                {sweep.succeeded} · falha {sweep.failed} · skip {sweep.skipped})
              </span>
              {sweep.terminal_reason ? (
                <span className="text-[#929aa5]">terminal_reason: {sweep.terminal_reason}</span>
              ) : null}
              {running ? (
                <div className="flex gap-2">
                  <button onClick={() => void command('pause')} className="px-3 py-1 rounded bg-[#2b3139] hover:bg-[#363c45]">
                    Pausar
                  </button>
                  <button onClick={() => void command('resume')} className="px-3 py-1 rounded bg-[#2b3139] hover:bg-[#363c45]">
                    Retomar
                  </button>
                  <button onClick={() => void command('cancel')} className="px-3 py-1 rounded bg-[#f6465d]/20 text-[#ff8294] hover:bg-[#f6465d]/30">
                    Cancelar
                  </button>
                </div>
              ) : null}
            </div>
            <div className="flex items-center gap-4 text-sm">
              <label className="flex items-center gap-2">
                Métrica de ranking
                <select
                  value={metric}
                  onChange={(e) => setMetric(e.target.value as 'calmar_ratio' | 'delta_cagr_vs_bh')}
                  className="px-2 py-1 rounded bg-[#0b0e11] border border-[#2b3139]"
                >
                  <option value="calmar_ratio">Calmar</option>
                  <option value="delta_cagr_vs_bh">Δ vs Buy &amp; Hold</option>
                </select>
              </label>
              {history.length > 0 ? (
                <label className="flex items-center gap-2">
                  Histórico
                  <select
                    value={sweep.sweep_id}
                    onChange={(e) => void selectHistory(e.target.value)}
                    className="px-2 py-1 rounded bg-[#0b0e11] border border-[#2b3139]"
                  >
                    {history.map((h) => (
                      <option key={h.sweep_id} value={h.sweep_id}>
                        {h.sweep_id.slice(0, 8)} · {h.state} · {h.total}
                      </option>
                    ))}
                  </select>
                </label>
              ) : null}
            </div>
            {rows.length > 0 ? (
              <div className="overflow-x-auto" aria-label="Leaderboard de descoberta">
                <table className="w-full text-sm">
                  <thead className="text-[#929aa5]">
                    <tr>
                      <th className="text-left px-2 py-2">#</th>
                      <th className="text-left px-2 py-2">Estratégia</th>
                      <th className="text-left px-2 py-2">Mercado</th>
                      <th className="text-left px-2 py-2">TF</th>
                      <th className="text-left px-2 py-2">Dir</th>
                      <th className="text-right px-2 py-2">Calmar</th>
                      <th className="text-right px-2 py-2">
                        <abbr title="Buy and Hold">B&amp;H</abbr>
                      </th>
                      <th className="text-right px-2 py-2">
                        <abbr title="Delta versus Buy and Hold">Δ B&amp;H</abbr>
                      </th>
                      <th className="text-right px-2 py-2">
                        <abbr title="Maximum Drawdown">Max DD</abbr>
                      </th>
                      <th className="text-right px-2 py-2">Sharpe</th>
                      <th className="text-right px-2 py-2">
                        <abbr title="Profit Factor">PF</abbr>
                      </th>
                      <th className="text-right px-2 py-2">Trades</th>
                      <th className="text-left px-2 py-2">Status</th>
                      <th className="text-right px-2 py-2">Ação</th>
                    </tr>
                  </thead>
                  <tbody>
                    {rows.map((row) => (
                      <tr key={row.result_id} className="border-t border-[#2b3139]">
                        <td className="px-2 py-2">{row.rank}</td>
                        <td className="px-2 py-2 text-[#929aa5]">{row.template_id}</td>
                        <td className="px-2 py-2">{row.symbol}</td>
                        <td className="px-2 py-2">{row.timeframe}</td>
                        <td className={`px-2 py-2 ${row.direction === 'long' ? 'text-[#0ecb81]' : 'text-[#ff8294]'}`}>
                          {row.direction}
                        </td>
                        <td className="px-2 py-2 text-right">{fmt(row.calmar_ratio)}</td>
                        <td className="px-2 py-2 text-right">{fmt(row.benchmark_cagr)}</td>
                        <td className="px-2 py-2 text-right">{fmt(row.delta_cagr_vs_bh)}</td>
                        <td className="px-2 py-2 text-right">{fmt(row.max_drawdown)}</td>
                        <td className="px-2 py-2 text-right">{fmt(row.sharpe_ratio)}</td>
                        <td className="px-2 py-2 text-right">{fmt(row.profit_factor)}</td>
                        <td className="px-2 py-2 text-right">{row.trades_count ?? 'N/A'}</td>
                        <td className="px-2 py-2">
                          {row.eligibility === 'low_sample' ? (
                            <span className="px-2 py-0.5 rounded bg-[#e5c07b]/20 text-[#e5c07b] text-xs">Baixa amostra</span>
                          ) : row.dedup_state === 'duplicate_favorite' ? (
                            <span className="px-2 py-0.5 rounded bg-[#3b82f6]/20 text-[#3b82f6] text-xs">Duplicado</span>
                          ) : row.dedup_state === 'already_promoted' ? (
                            <span className="px-2 py-0.5 rounded bg-[#0ecb81]/20 text-[#0ecb81] text-xs">Favorito tier 3</span>
                          ) : (
                            <span className="px-2 py-0.5 rounded bg-[#2b3139] text-[#929aa5] text-xs">Único</span>
                          )}
                        </td>
                        <td className="px-2 py-2 text-right">
                          <button
                            onClick={() => void promote(row.result_id)}
                            disabled={
                              busy ||
                              row.eligibility !== 'eligible' ||
                              row.dedup_state !== 'unique'
                            }
                            className="px-3 py-1 rounded bg-[#fcd535] text-[#0b0e11] text-xs font-semibold disabled:opacity-40 disabled:bg-[#3a3a1f]"
                          >
                            Promover (tier 3)
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
                <p className="mt-3 text-xs text-[#707a8a]">
                  O ranking histórico é apoio à decisão e não garante retorno futuro.
                </p>
              </div>
            ) : null}
          </section>
        ) : null}
      </main>
    </div>
  )
}
