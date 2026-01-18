import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import {
    Settings, Play, TrendingUp, Activity,
    ArrowLeft, Search, CheckCircle, BarChart3,
    Sliders
} from 'lucide-react'

// Mock Data (Replace with API fetch)
const TIMEFRAMES = ["1m", "5m", "15m", "30m", "1h", "4h", "1d"]

export function ComboOptimizePage() {
    const navigate = useNavigate()

    // State
    const [templates, setTemplates] = useState<any[]>([])
    const [selectedTemplate, setSelectedTemplate] = useState<string>('')
    const [symbol, setSymbol] = useState('BTC/USDT')
    const [timeframe, setTimeframe] = useState('1h')
    const [isOptimizing, setIsOptimizing] = useState(false)
    const [params, setParams] = useState<any[]>([])
    const [results, setResults] = useState<any>(null)

    // Fetch templates on load
    useEffect(() => {
        fetch('http://localhost:8000/api/combos/templates')
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

        fetch(`http://localhost:8000/api/combos/templates/${selectedTemplate}/metadata`)
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
            const res = await fetch('http://localhost:8000/api/combos/optimize', {
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
        <div className="min-h-screen relative overflow-hidden text-gray-100">
            {/* Background */}
            <div className="fixed inset-0 -z-10 bg-[#0f172a]">
                <div className="absolute top-0 right-0 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl"></div>
                <div className="absolute bottom-0 left-0 w-96 h-96 bg-blue-500/10 rounded-full blur-3xl"></div>
            </div>

            {/* Header */}
            <header className="glass-strong border-b border-white/10 sticky top-0 z-50">
                <div className="container mx-auto px-6 py-4 flex items-center justify-between">
                    <div className="flex items-center gap-4">
                        <button onClick={() => navigate('/combo/configure')} className="p-2 hover:bg-white/5 rounded-lg transition-colors">
                            <ArrowLeft className="w-5 h-5 text-gray-400" />
                        </button>
                        <div className="flex items-center gap-3">
                            <div className="bg-gradient-to-br from-purple-500 to-pink-600 p-2 rounded-lg">
                                <Sliders className="w-5 h-5 text-white" />
                            </div>
                            <h1 className="text-xl font-bold">Strategy Optimizer</h1>
                        </div>
                    </div>
                </div>
            </header>

            <main className="container mx-auto px-6 py-8">
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">

                    {/* CONFIGURATION PANEL */}
                    <div className="lg:col-span-1 space-y-6">
                        <div className="glass-strong rounded-2xl p-6 border border-white/10">
                            <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
                                <Settings className="w-4 h-4 text-purple-400" /> Configuration
                            </h2>

                            <div className="space-y-4">
                                {/* Template Selection */}
                                <div>
                                    <label className="block text-sm text-gray-400 mb-1">Strategy Template</label>
                                    <select
                                        value={selectedTemplate}
                                        onChange={(e) => setSelectedTemplate(e.target.value)}
                                        className="w-full bg-black/40 border border-white/10 rounded-xl px-4 py-3 outline-none focus:border-purple-500 transition-colors"
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
                                        <label className="block text-sm text-gray-400 mb-1">Symbol</label>
                                        <input
                                            type="text"
                                            value={symbol}
                                            onChange={(e) => setSymbol(e.target.value)}
                                            className="w-full bg-black/40 border border-white/10 rounded-xl px-4 py-3 outline-none focus:border-purple-500"
                                        />
                                    </div>
                                    <div>
                                        <label className="block text-sm text-gray-400 mb-1">Timeframe</label>
                                        <select
                                            value={timeframe}
                                            onChange={(e) => setTimeframe(e.target.value)}
                                            className="w-full bg-black/40 border border-white/10 rounded-xl px-4 py-3 outline-none focus:border-purple-500"
                                        >
                                            {TIMEFRAMES.map(tf => <option key={tf} value={tf}>{tf}</option>)}
                                        </select>
                                    </div>
                                </div>

                                {/* Parameters Ranges */}
                                {params.length > 0 && (
                                    <div className="space-y-4 pt-4 border-t border-white/10">
                                        <h3 className="text-sm font-semibold text-gray-300">Parameter Ranges</h3>
                                        <div className="space-y-4 max-h-[400px] overflow-y-auto pr-2 custom-scrollbar">
                                            {params.map((param, idx) => (
                                                <div key={idx} className="bg-white/5 rounded-lg p-3">
                                                    <div className="flex justify-between mb-2">
                                                        <span className="text-sm font-medium text-purple-300">{param.name}</span>
                                                    </div>
                                                    <div className="grid grid-cols-3 gap-2">
                                                        <div>
                                                            <label className="text-xs text-gray-500">Min</label>
                                                            <input
                                                                type="number"
                                                                value={param.min}
                                                                onChange={(e) => {
                                                                    const newParams = [...params]
                                                                    newParams[idx].min = parseFloat(e.target.value)
                                                                    setParams(newParams)
                                                                }}
                                                                className="w-full bg-black/20 border border-white/10 rounded-lg px-2 py-1 text-sm"
                                                            />
                                                        </div>
                                                        <div>
                                                            <label className="text-xs text-gray-500">Max</label>
                                                            <input
                                                                type="number"
                                                                value={param.max}
                                                                onChange={(e) => {
                                                                    const newParams = [...params]
                                                                    newParams[idx].max = parseFloat(e.target.value)
                                                                    setParams(newParams)
                                                                }}
                                                                className="w-full bg-black/20 border border-white/10 rounded-lg px-2 py-1 text-sm"
                                                            />
                                                        </div>
                                                        <div>
                                                            <label className="text-xs text-gray-500">Step</label>
                                                            <input
                                                                type="number"
                                                                value={param.step}
                                                                onChange={(e) => {
                                                                    const newParams = [...params]
                                                                    newParams[idx].step = parseFloat(e.target.value)
                                                                    setParams(newParams)
                                                                }}
                                                                className="w-full bg-black/20 border border-white/10 rounded-lg px-2 py-1 text-sm"
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
                                    className="w-full bg-gradient-to-r from-purple-500 to-pink-600 hover:from-purple-400 hover:to-pink-500 text-white font-bold py-4 rounded-xl shadow-lg shadow-purple-500/25 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 mt-4"
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
                            <div className="h-full min-h-[400px] glass-strong rounded-2xl border border-white/10 flex flex-col items-center justify-center text-center p-8">
                                <div className="bg-white/5 p-4 rounded-full mb-4">
                                    <Search className="w-12 h-12 text-gray-600" />
                                </div>
                                <h3 className="text-xl font-semibold text-gray-300 mb-2">Ready to Optimize</h3>
                                <p className="text-gray-500 max-w-md">
                                    Select a strategy template and configure parameter ranges to find the best performing combination.
                                </p>
                            </div>
                        ) : (
                            <div className="space-y-6 animate-fade-in">

                                {/* Best Result Card */}
                                <div className="glass-strong rounded-2xl p-6 border border-emerald-500/20 bg-emerald-500/5">
                                    <div className="flex items-center gap-3 mb-6">
                                        <div className="bg-emerald-500 p-2 rounded-lg">
                                            <CheckCircle className="w-6 h-6 text-white" />
                                        </div>
                                        <div>
                                            <h2 className="text-2xl font-bold text-white">Optimization Complete</h2>
                                            <p className="text-emerald-400">Found optimal parameters</p>
                                        </div>
                                    </div>

                                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                                        <div className="bg-black/20 p-4 rounded-xl">
                                            <p className="text-xs text-gray-400 mb-1">Total Return</p>
                                            <p className="text-2xl font-bold text-emerald-400">
                                                {(results.best_metrics.total_return * 100).toFixed(2)}%
                                            </p>
                                        </div>
                                        <div className="bg-black/20 p-4 rounded-xl">
                                            <p className="text-xs text-gray-400 mb-1">Win Rate</p>
                                            <p className="text-2xl font-bold text-blue-400">
                                                {(results.best_metrics.win_rate * 100).toFixed(1)}%
                                            </p>
                                        </div>
                                        <div className="bg-black/20 p-4 rounded-xl">
                                            <p className="text-xs text-gray-400 mb-1">Sharpe Ratio</p>
                                            <p className="text-2xl font-bold text-purple-400">
                                                {results.best_metrics.sharpe_ratio.toFixed(2)}
                                            </p>
                                        </div>
                                        <div className="bg-black/20 p-4 rounded-xl">
                                            <p className="text-xs text-gray-400 mb-1">Trades</p>
                                            <p className="text-2xl font-bold text-white">
                                                {results.best_metrics.total_trades}
                                            </p>
                                        </div>
                                    </div>

                                    <div>
                                        <h3 className="text-sm font-semibold text-gray-400 mb-3">Optimal Parameters</h3>
                                        <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                                            {Object.entries(results.best_parameters).map(([key, val]) => (
                                                <div key={key} className="flex justify-between items-center bg-black/20 px-4 py-3 rounded-lg border border-white/5">
                                                    <span className="text-gray-400 text-sm">{key}</span>
                                                    <span className="font-mono font-bold text-white">{String(val)}</span>
                                                </div>
                                            ))}
                                        </div>
                                    </div>
                                </div>

                                {/* Stages Log (Simplificado) */}
                                <div className="glass-strong rounded-2xl p-6 border border-white/10">
                                    <h3 className="text-lg font-semibold mb-4">Optimization Stages</h3>
                                    <div className="space-y-2">
                                        {results.stages.map((stage: any, i: number) => (
                                            <div key={i} className="flex items-center gap-4 p-3 hover:bg-white/5 rounded-lg transition-colors">
                                                <div className="w-8 h-8 rounded-full bg-blue-500/20 flex items-center justify-center text-blue-400 font-bold text-sm">
                                                    {stage.stage_num}
                                                </div>
                                                <div>
                                                    <p className="font-medium text-white">{stage.stage_name}</p>
                                                    <p className="text-xs text-gray-400">Tested {stage.values.length} variations</p>
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
