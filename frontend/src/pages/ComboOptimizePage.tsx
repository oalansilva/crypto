import { useState, useEffect, useMemo } from 'react'
import { useSearchParams } from 'react-router-dom'
import {
    Settings, Play, Activity,
    Search, CheckCircle,
} from 'lucide-react'
import { API_BASE_URL } from '../lib/apiBase'
import { authFetch } from '../lib/authFetch'
import { AssetPicker } from '../components/AssetPicker'
import { DataExecutionBlock } from '../components/results/DataExecutionBlock'
import { BatchProgressPanel } from '../components/BatchProgressPanel'
import { useBatchJob } from '../hooks/useBatchJob'
import { lookupCatalogAssets } from '../lib/assetCatalogApi'
import {
    ON_DEMAND_TEXT_BACKTEST,
    OPTIMIZE_FIXED_WINDOW,
    OPTIMIZE_FIXED_WINDOW_LABEL,
    blockedNotice,
    collectingCopy,
    equityBadTimeframes,
    equityTimeframeBlock,
    historyUnavailableNotice,
    normalizeSymbol,
    partialNotice,
    planRun,
    refusalMessage,
    runCopy,
    urlSymbolNotice,
    type RunNotice,
} from '../lib/assetSelection'
import { rememberAssets, useSelectionView } from '../lib/assetStore'

// Mock Data (Replace with API fetch)
const TIMEFRAMES = ["1m", "5m", "15m", "30m", "1h", "4h", "1d"]

const DEFAULT_SYMBOL = 'BTC/USDT'

export function ComboOptimizePage() {
    const [searchParams] = useSearchParams()
    const urlSymbol = normalizeSymbol(searchParams.get('symbol') || '')

    // State
    const [templates, setTemplates] = useState<any[]>([])
    const [selectedTemplate, setSelectedTemplate] = useState<string>(searchParams.get('template') || '')
    // Ativos: o seletor do catálogo (sem texto livre). `?symbol=` só marca se existir no catálogo.
    const [selectedSymbols, setSelectedSymbols] = useState<string[]>(urlSymbol ? [] : [DEFAULT_SYMBOL])
    const [symbolNotice, setSymbolNotice] = useState<{ title: string; body: string } | null>(null)
    const [runNotice, setRunNotice] = useState<RunNotice | null>(null)
    const [timeframe, setTimeframe] = useState(searchParams.get('timeframe') || '1h')
    const [isOptimizing, setIsOptimizing] = useState(false)
    const [params, setParams] = useState<any[]>([])
    const [results, setResults] = useState<any>(null)

    const {
        batchRunning, setBatchRunning,
        setBatchJobId,
        batchPauseCancelRequested, setBatchPauseCancelRequested,
        batchProgress, setBatchProgress,
        batchTotal, setBatchTotal,
        clientElapsedSec, setClientElapsedSec,
        batchStartTimeRef,
        handlePauseBatch, handleCancelBatch,
    } = useBatchJob()

    // O que roda e o que fica fora (ação, ETF e ativo marcado pela Binance).
    const { entries: selectionEntries, loading: selectionLoading } = useSelectionView(selectedSymbols)
    const plan = useMemo(() => planRun(selectionEntries), [selectionEntries])
    // Ação/ETF sozinha (card #1119): roda com `run_scope: "single"` na janela fixa da tela; 1m/5m/30m
    // ficam indisponíveis e 15m/1h/4h avisam antes de rodar quando o 5m não cobre a janela fixa.
    const equityRun = plan.equityRun
    const tfBlock = equityTimeframeBlock(plan, timeframe, 'optimize')
    const copy = tfBlock ? { text: tfBlock.copy, blocked: true } : runCopy(plan, 'optimize', { timeframe })
    const [collecting, setCollecting] = useState<string | null>(null)

    // `?symbol=`: marca só se existir no catálogo; ativo marcado entra como "fica de fora".
    useEffect(() => {
        if (!urlSymbol) return
        let cancelled = false
        void (async () => {
            try {
                const data = await lookupCatalogAssets([urlSymbol])
                if (cancelled) return
                rememberAssets(data.items, { fresh: data.freshness })
                const found = data.items.some((item) => normalizeSymbol(item.symbol) === urlSymbol)
                const listUnavailable =
                    data.freshness[urlSymbol.includes('/') ? 'crypto' : 'stock'].status === 'unavailable'
                if (found || listUnavailable) setSelectedSymbols([urlSymbol])
                else setSymbolNotice(urlSymbolNotice(urlSymbol))
            } catch {
                if (!cancelled) setSelectedSymbols([urlSymbol])
            }
        })()
        return () => {
            cancelled = true
        }
    }, [urlSymbol])

    // Fetch templates on load
    useEffect(() => {
        authFetch(`${API_BASE_URL}/combos/templates`)
            .then(res => res.json())
            .then(data => {
                const all = [
                    ...data.prebuilt.map((t: any) => ({ ...t, type: 'prebuilt' })),
                    ...data.custom.map((t: any) => ({ ...t, type: 'custom' }))
                ]
                setTemplates(all)
            })
            .catch(err => console.error(err))
    }, [])

    // Load params when template selected
    useEffect(() => {
        if (!selectedTemplate) return

        authFetch(`${API_BASE_URL}/combos/templates/${selectedTemplate}/metadata`)
            .then(res => res.json())
            .then(data => {
                // Extract params for optimization
                const optParams = []

                // Helper to extract numeric params
                const addParam = (name: string, defaultVal: number, group: string) => {
                    optParams.push({
                        name,
                        group,
                        min: Math.floor(defaultVal * 0.5) || 1,
                        max: Math.ceil(defaultVal * 1.5) || 10,
                        step: 1
                    })
                }

                // Process indicators
                data.indicators.forEach((ind: any) => {
                    const alias = ind.alias || ind.type
                    Object.entries(ind.params).forEach(([key, val]) => {
                        if (typeof val === 'number') {
                            addParam(`${alias}_${key}`, val, alias)
                        }
                    })
                })

                setParams(optParams)
            })
    }, [selectedTemplate])

    const changeSymbols = (next: string[]) => {
        setSelectedSymbols(next)
        setSymbolNotice(null)
        setRunNotice(null)
    }

    const handleRunOptimization = async () => {
        setRunNotice(null)
        if (tfBlock) {
            // Nada é iniciado; o tempo escolhido fica como está.
            setRunNotice(tfBlock.notice)
            return
        }
        if (plan.mode === 'none') {
            setRunNotice({ tone: 'warn', title: 'Escolha ao menos 1 ativo', body: 'Pesquise e marque os ativos a otimizar.' })
            return
        }
        if (plan.mode === 'blocked') {
            // Nada é iniciado; a seleção fica como está.
            setRunNotice(blockedNotice(plan, 'optimize'))
            return
        }
        const symbolsToRun = plan.runnable
        setRunNotice(partialNotice(plan))

        // Build custom ranges
        const custom_ranges: Record<string, any> = {}
        params.forEach(p => {
            custom_ranges[p.name] = {
                min: p.min,
                max: p.max,
                step: p.step
            }
        })

        if (symbolsToRun.length === 1) {
            setIsOptimizing(true)
            setResults(null)
            const isEquityRun = !!equityRun
            if (isEquityRun) setCollecting(collectingCopy(symbolsToRun[0], 'optimize', timeframe))
            try {
                const res = await authFetch(`${API_BASE_URL}/combos/optimize`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        template_name: selectedTemplate,
                        symbol: symbolsToRun[0],
                        timeframe,
                        start_date: OPTIMIZE_FIXED_WINDOW.start, // TODO: Date picker (#1120)
                        end_date: OPTIMIZE_FIXED_WINDOW.end,
                        custom_ranges,
                        run_scope: 'single',
                    })
                })

                const data = await res.json()
                if (!res.ok) {
                    const unavailable = isEquityRun ? historyUnavailableNotice(data?.detail) : null
                    setRunNotice(
                        unavailable ?? {
                            tone: 'alert',
                            title: 'Otimização recusada',
                            body: refusalMessage(data?.detail, 'Falha na otimização'),
                        },
                    )
                    return
                }
                setResults(data)

            } catch (err) {
                console.error(err)
                alert("Optimization failed")
            } finally {
                setIsOptimizing(false)
                setCollecting(null)
            }
            return
        }

        // N pares: o lote do Combo, uma otimização por ativo com a mesma configuração.
        setResults(null)
        setBatchRunning(true)
        setBatchJobId(null)
        setBatchProgress(null)
        setBatchTotal(symbolsToRun.length)
        setBatchPauseCancelRequested(false)
        setClientElapsedSec(0)
        batchStartTimeRef.current = Date.now()
        try {
            const res = await authFetch(`${API_BASE_URL}/combos/backtest/batch`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    template_name: selectedTemplate,
                    symbols: symbolsToRun,
                    timeframe,
                    start_date: OPTIMIZE_FIXED_WINDOW.start, // mesmas datas do caminho de 1 ativo
                    end_date: OPTIMIZE_FIXED_WINDOW.end,
                    custom_ranges
                })
            })
            if (!res.ok) {
                const err = await res.json().catch(() => ({}))
                throw new Error(refusalMessage(err.detail, 'Falha ao iniciar o lote'))
            }
            const data = await res.json()
            setBatchJobId(data.job_id)
        } catch (err) {
            console.error(err)
            setRunNotice({
                tone: 'alert',
                title: 'Não foi possível iniciar o lote',
                body: err instanceof Error ? err.message : 'Falha ao iniciar o lote',
            })
            setBatchRunning(false)
        }
    }

    return (
        <div className="app-page combo-page relative overflow-hidden text-zinc-700">
            <main className="container mx-auto px-6 py-8">
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">

                    {/* CONFIGURATION PANEL */}
                    <div className="lg:col-span-1 space-y-6">
                        <div className="glass-strong rounded-2xl p-6 border border-zinc-200">
                            <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
                                <Settings className="w-4 h-4 text-purple-400" /> Configuration
                            </h2>

                            <div className="space-y-4">
                                {/* Template Selection */}
                                <div>
                                    <label className="block text-sm text-zinc-400 mb-1">Strategy Template</label>
                                    <select
                                        value={selectedTemplate}
                                        onChange={(e) => setSelectedTemplate(e.target.value)}
                                        className="w-full bg-white0 border border-zinc-200 rounded-xl px-4 py-3 outline-none focus:border-purple-500 transition-colors"
                                    >
                                        <option value="">Select Strategy...</option>
                                        {templates.map(t => (
                                            <option key={t.name} value={t.name}>{t.name}</option>
                                        ))}
                                    </select>
                                </div>

                                {/* Ativos: o seletor do catálogo substitui o texto livre */}
                                <div>
                                    <span className="block text-sm text-zinc-400 mb-1">Ativos</span>
                                    <AssetPicker
                                        value={selectedSymbols}
                                        onChange={changeSymbols}
                                        ariaLabel="Seletor de ativos para otimizar"
                                        variant="narrow"
                                        notice={symbolNotice}
                                        onDemandTexts={ON_DEMAND_TEXT_BACKTEST}
                                        classNote="Ação e ETF por enquanto rodam só com 1 ativo (Combo ou Otimização) e mostram o resultado ao lado. Com mais de 1 ativo, ficam fora com aviso; o lote vem depois."
                                    />
                                </div>

                                {/* Timeframe */}
                                <div>
                                    <label className="block text-sm text-zinc-400 mb-1">Timeframe</label>
                                    <select
                                        value={timeframe}
                                        onChange={(e) => setTimeframe(e.target.value)}
                                        className="w-full bg-white0 border border-zinc-200 rounded-xl px-4 py-3 outline-none focus:border-purple-500"
                                    >
                                        {TIMEFRAMES.map(tf => {
                                            const cryptoOnly = !!equityRun && equityBadTimeframes('optimize').includes(tf)
                                            return (
                                                <option key={tf} value={tf} disabled={cryptoOnly}>
                                                    {cryptoOnly ? `${tf} (só cripto)` : tf}
                                                </option>
                                            )
                                        })}
                                    </select>
                                    <p className="r19-hint" data-testid="opt-period">
                                        <b>Período:</b> {OPTIMIZE_FIXED_WINDOW_LABEL}, fixo nesta tela.
                                    </p>
                                    {equityRun ? (
                                        <p className="r19-hint" data-testid="opt-timeframe-hint">
                                            <b>Ação e ETF:</b> 15m, 1h, 4h ou 1d no pregão regular de Nova York. 15m, 1h e 4h são montados do 5m da Binance, que pode não cobrir jan. 2024; para outro período, use o Combo.
                                        </p>
                                    ) : null}
                                </div>

                                {/* Parameters Ranges */}
                                {params.length > 0 && (
                                    <div className="space-y-4 pt-4 border-t border-zinc-200">
                                        <h3 className="text-sm font-semibold text-zinc-500">Parameter Ranges</h3>
                                        <div className="space-y-4 max-h-[400px] overflow-y-auto pr-2 custom-scrollbar">
                                            {params.map((param, idx) => (
                                                <div key={idx} className="bg-zinc-50 rounded-lg p-3">
                                                    <div className="flex justify-between mb-2">
                                                        <span className="text-sm font-medium text-purple-300">{param.name}</span>
                                                    </div>
                                                    <div className="grid grid-cols-3 gap-2">
                                                        <div>
                                                            <label className="text-xs text-zinc-500">Min</label>
                                                            <input
                                                                type="number"
                                                                value={param.min}
                                                                onChange={(e) => {
                                                                    const newParams = [...params]
                                                                    newParams[idx].min = parseFloat(e.target.value)
                                                                    setParams(newParams)
                                                                }}
                                                                className="w-full bg-white0 border border-zinc-200 rounded-lg px-2 py-1 text-sm"
                                                            />
                                                        </div>
                                                        <div>
                                                            <label className="text-xs text-zinc-500">Max</label>
                                                            <input
                                                                type="number"
                                                                value={param.max}
                                                                onChange={(e) => {
                                                                    const newParams = [...params]
                                                                    newParams[idx].max = parseFloat(e.target.value)
                                                                    setParams(newParams)
                                                                }}
                                                                className="w-full bg-white0 border border-zinc-200 rounded-lg px-2 py-1 text-sm"
                                                            />
                                                        </div>
                                                        <div>
                                                            <label className="text-xs text-zinc-500">Step</label>
                                                            <input
                                                                type="number"
                                                                value={param.step}
                                                                onChange={(e) => {
                                                                    const newParams = [...params]
                                                                    newParams[idx].step = parseFloat(e.target.value)
                                                                    setParams(newParams)
                                                                }}
                                                                className="w-full bg-white0 border border-zinc-200 rounded-lg px-2 py-1 text-sm"
                                                            />
                                                        </div>
                                                    </div>
                                                </div>
                                            ))}
                                        </div>
                                    </div>
                                )}

                                <button
                                    onClick={handleRunOptimization}
                                    disabled={isOptimizing || batchRunning || !selectedTemplate || selectionLoading}
                                    data-testid="run-optimization"
                                    className="w-full bg-gradient-to-r from-purple-500 to-pink-600 hover:from-purple-400 hover:to-pink-500 text-zinc-900 font-bold py-4 rounded-xl shadow-lg shadow-purple-500/25 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 mt-4"
                                >
                                    {isOptimizing || batchRunning ? (
                                        <>
                                            <Activity className="w-5 h-5 animate-spin" /> Optimizing...
                                        </>
                                    ) : (
                                        <>
                                            <Play className="w-5 h-5 fill-current" /> Run Optimization
                                        </>
                                    )}
                                </button>

                                <p
                                    className={`text-xs ${copy.blocked ? 'text-amber-300' : 'text-zinc-400'}`}
                                    data-testid="opt-run-copy"
                                >
                                    {copy.text}
                                </p>
                                {collecting ? (
                                    <p className="r19-collect" role="status" data-testid="run-collecting">
                                        {collecting}
                                    </p>
                                ) : null}
                                {runNotice ? (
                                    <div
                                        className={runNotice.tone === 'alert' ? 'ap-alert' : 'ap-warn'}
                                        role={runNotice.tone === 'alert' ? 'alert' : 'status'}
                                        data-testid="run-warning"
                                    >
                                        <strong>{runNotice.title}</strong>
                                        {runNotice.body}
                                    </div>
                                ) : null}
                                <BatchProgressPanel
                                    batchRunning={batchRunning}
                                    batchProgress={batchProgress}
                                    batchTotal={batchTotal}
                                    clientElapsedSec={clientElapsedSec}
                                    pauseCancelRequested={batchPauseCancelRequested}
                                    onPause={handlePauseBatch}
                                    onCancel={handleCancelBatch}
                                />

                            </div>
                        </div>
                    </div>

                    {/* RESULTS PANEL */}
                    <div className="lg:col-span-2 space-y-6">
                        {!results ? (
                            <div className="h-full min-h-[400px] glass-strong rounded-2xl border border-zinc-200 flex flex-col items-center justify-center text-center p-8">
                                <div className="bg-zinc-50 p-4 rounded-full mb-4">
                                    <Search className="w-12 h-12 text-zinc-600" />
                                </div>
                                <h3 className="text-xl font-semibold text-zinc-500 mb-2">Ready to Optimize</h3>
                                <p className="text-zinc-500 max-w-md">
                                    Select a strategy template and configure parameter ranges to find the best performing combination.
                                </p>
                            </div>
                        ) : (
                            <div className="space-y-6 animate-fade-in">

                                {/* Best Result Card */}
                                <div className="glass-strong rounded-2xl p-6 border border-emerald-600/20 bg-emerald-500/5">
                                    <div className="flex items-center gap-3 mb-6">
                                        <div className="bg-emerald-500 p-2 rounded-lg">
                                            <CheckCircle className="w-6 h-6 text-zinc-900" />
                                        </div>
                                        <div>
                                            <h2 className="text-2xl font-bold text-zinc-900">Optimization Complete</h2>
                                            <p className="text-emerald-400">Found optimal parameters</p>
                                        </div>
                                    </div>

                                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                                        <div className="bg-white0 p-4 rounded-xl">
                                            <p className="text-xs text-zinc-400 mb-1">Total Return</p>
                                            <p className="text-2xl font-bold text-emerald-400">
                                                {(results.best_metrics.total_return * 100).toFixed(2)}%
                                            </p>
                                        </div>
                                        <div className="bg-white0 p-4 rounded-xl">
                                            <p className="text-xs text-zinc-400 mb-1">Win Rate</p>
                                            <p className="text-2xl font-bold text-blue-400">
                                                {(results.best_metrics.win_rate * 100).toFixed(1)}%
                                            </p>
                                        </div>
                                        <div className="bg-white0 p-4 rounded-xl">
                                            <p className="text-xs text-zinc-400 mb-1">Sharpe Ratio</p>
                                            <p className="text-2xl font-bold text-purple-400">
                                                {results.best_metrics.sharpe_ratio.toFixed(2)}
                                            </p>
                                        </div>
                                        <div className="bg-white0 p-4 rounded-xl">
                                            <p className="text-xs text-zinc-400 mb-1">Trades</p>
                                            <p className="text-2xl font-bold text-zinc-900">
                                                {results.best_metrics.total_trades}
                                            </p>
                                        </div>
                                    </div>

                                    <div>
                                        <h3 className="text-sm font-semibold text-zinc-400 mb-3">Optimal Parameters</h3>
                                        <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                                            {Object.entries(results.best_parameters).map(([key, val]) => (
                                                <div key={key} className="flex justify-between items-center bg-white0 px-4 py-3 rounded-lg border border-zinc-100">
                                                    <span className="text-zinc-400 text-sm">{key}</span>
                                                    <span className="font-mono font-bold text-zinc-900">{String(val)}</span>
                                                </div>
                                            ))}
                                        </div>
                                    </div>
                                </div>

                                <DataExecutionBlock
                                    asset={results.asset}
                                    provenance={results.data_provenance}
                                    execution={results.execution}
                                    conventions={results.conventions}
                                    timeframe={results.timeframe ?? timeframe}
                                    trades={results.trades}
                                    page="optimize"
                                    requestedFallback={OPTIMIZE_FIXED_WINDOW}
                                    requestedNote="Período fixo desta tela"
                                />

                                {/* Stages Log (Simplificado) */}
                                <div className="glass-strong rounded-2xl p-6 border border-zinc-200">
                                    <h3 className="text-lg font-semibold mb-4">Optimization Stages</h3>
                                    <div className="space-y-2">
                                        {results.stages.map((stage: any, i: number) => (
                                            <div key={i} className="flex items-center gap-4 p-3 hover:bg-zinc-50 rounded-lg transition-colors">
                                                <div className="w-8 h-8 rounded-full bg-blue-500/20 flex items-center justify-center text-blue-400 font-bold text-sm">
                                                    {stage.stage_num}
                                                </div>
                                                <div>
                                                    <p className="font-medium text-zinc-900">{stage.stage_name}</p>
                                                    <p className="text-xs text-zinc-400">Tested {stage.values.length} variations</p>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                </div>

                            </div>
                        )}
                    </div>

                </div>
            </main>
        </div>
    )
}
