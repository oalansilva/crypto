import { useState, useEffect } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import {
    Settings, Play, TrendingUp, Activity,
    ArrowLeft, Search, CheckCircle, BarChart3,
    Sliders
} from 'lucide-react'
import { API_BASE_URL } from '../lib/apiBase'

// Mock Data (Replace with API fetch)
const TIMEFRAMES = ["1m", "5m", "15m", "30m", "1h", "4h", "1d"]

export function ComboOptimizePage() {
    const navigate = useNavigate()
    const [searchParams] = useSearchParams()

    // State
    const [templates, setTemplates] = useState<any[]>([])
    const [selectedTemplate, setSelectedTemplate] = useState<string>(searchParams.get('template') || '')
    const [symbol, setSymbol] = useState(searchParams.get('symbol') || 'BTC/USDT')
    const [timeframe, setTimeframe] = useState(searchParams.get('timeframe') || '1h')
    const [isOptimizing, setIsOptimizing] = useState(false)
    const [params, setParams] = useState<any[]>([])
    const [results, setResults] = useState<any>(null)

    // Fetch templates on load
    useEffect(() => {
        fetch(`${API_BASE_URL}/combos/templates`)
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

        fetch(`${API_BASE_URL}/combos/templates/${selectedTemplate}/metadata`)
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

    const handleRunOptimization = async () => {
        setIsOptimizing(true)
        setResults(null)

        // Build custom ranges
        const custom_ranges: Record<string, any> = {}
        params.forEach(p => {
            custom_ranges[p.name] = {
                min: p.min,
                max: p.max,
                step: p.step
            }
        })

        try {
            const res = await fetch(`${API_BASE_URL}/combos/optimize`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    template_name: selectedTemplate,
                    symbol,
                    timeframe,
                    start_date: "2024-01-01", // TODO: Date picker
                    end_date: "2024-01-31",
                    custom_ranges
                })
            })

            const data = await res.json()
            setResults(data)

        } catch (err) {
            console.error(err)
            alert("Optimization failed")
        } finally {
            setIsOptimizing(false)
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

                                {/* Symbol & Timeframe */}
                                <div className="grid grid-cols-2 gap-4">
                                    <div>
                                        <label className="block text-sm text-zinc-400 mb-1">Symbol</label>
                                        <input
                                            type="text"
                                            value={symbol}
                                            onChange={(e) => setSymbol(e.target.value)}
                                            className="w-full bg-white0 border border-zinc-200 rounded-xl px-4 py-3 outline-none focus:border-purple-500"
                                        />
                                    </div>
                                    <div>
                                        <label className="block text-sm text-zinc-400 mb-1">Timeframe</label>
                                        <select
                                            value={timeframe}
                                            onChange={(e) => setTimeframe(e.target.value)}
                                            className="w-full bg-white0 border border-zinc-200 rounded-xl px-4 py-3 outline-none focus:border-purple-500"
                                        >
                                            {TIMEFRAMES.map(tf => <option key={tf} value={tf}>{tf}</option>)}
                                        </select>
                                    </div>
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
                                    disabled={isOptimizing || !selectedTemplate}
                                    className="w-full bg-gradient-to-r from-purple-500 to-pink-600 hover:from-purple-400 hover:to-pink-500 text-zinc-900 font-bold py-4 rounded-xl shadow-lg shadow-purple-500/25 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 mt-4"
                                >
                                    {isOptimizing ? (
                                        <>
                                            <Activity className="w-5 h-5 animate-spin" /> Optimizing...
                                        </>
                                    ) : (
                                        <>
                                            <Play className="w-5 h-5 fill-current" /> Run Optimization
                                        </>
                                    )}
                                </button>

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
