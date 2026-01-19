import { useState, useEffect } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { Settings, TrendingUp, Calendar, DollarSign, Sliders } from 'lucide-react'

interface TemplateMetadata {
    name: string
    description: string
    indicators: Array<{
        type: string
        alias?: string
        params: Record<string, any>
    }>
    entry_logic: string
    exit_logic: string
    stop_loss: number
}

export function ComboConfigurePage() {
    const navigate = useNavigate()
    const [searchParams] = useSearchParams()
    const templateName = searchParams.get('template')

    const [metadata, setMetadata] = useState<TemplateMetadata | null>(null)
    const [loading, setLoading] = useState(true)
    const [running, setRunning] = useState(false)

    // Optimization parameters
    const [params, setParams] = useState<any[]>([])
    const [symbol, setSymbol] = useState('BTC/USDT')
    const [timeframe, setTimeframe] = useState('1d')
    const [logs, setLogs] = useState<string[]>([])

    useEffect(() => {
        if (templateName) {
            fetchMetadata()
        }
    }, [templateName])

    const fetchMetadata = async () => {
        try {
            const response = await fetch(`http://localhost:8000/api/combos/meta/${templateName}`)
            const data = await response.json()
            setMetadata(data)

            // Extract params for optimization from optimization_schema (if available) or indicators
            const optParams: any[] = []

            // Check if template has optimization_schema in database
            if (data.optimization_schema && Object.keys(data.optimization_schema).length > 0) {
                // Use optimization schema from database
                Object.entries(data.optimization_schema).forEach(([paramName, config]: [string, any]) => {
                    // Determine group from parameter name (e.g., "sma_short" -> "short")
                    const parts = paramName.split('_')
                    const group = parts.length > 1 ? parts[parts.length - 1] : paramName

                    optParams.push({
                        name: paramName,
                        group: group,
                        min: config.min,
                        max: config.max,
                        step: config.step || 1
                    })
                })
            } else {
                // Fallback: Extract from indicators metadata (old behavior)
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
                            addParam(`${alias}_${key}`, val as number, alias)
                        }
                    })
                })
            }

            setParams(optParams)
        } catch (error) {
            console.error('Failed to fetch metadata:', error)
        } finally {
            setLoading(false)
        }
    }

    const handleRunOptimization = async () => {
        setRunning(true)
        try {
            // Build custom ranges
            const custom_ranges: Record<string, any> = {}
            params.forEach(p => {
                custom_ranges[p.name] = {
                    min: p.min,
                    max: p.max,
                    step: p.step
                }
            })

            const response = await fetch('http://localhost:8000/api/combos/optimize', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    template_name: templateName,
                    symbol,
                    timeframe,
                    start_date: null, // Use all available data
                    end_date: null,
                    custom_ranges
                })
            })

            if (response.ok) {
                const result = await response.json()
                // Navigate to results page with data
                navigate('/combo/results', { state: { result, isOptimization: true } })
            } else {
                alert('Optimization failed. Check console for details.')
            }
        } catch (error) {
            console.error('Optimization error:', error)
            alert('Failed to run optimization')
        } finally {
            setRunning(false)
        }
    }

    if (loading) {
        return (
            <div className="min-h-screen flex items-center justify-center">
                <div className="text-center">
                    <Settings className="w-12 h-12 animate-spin text-blue-400 mx-auto mb-4" />
                    <p className="text-gray-400">Loading configuration...</p>
                </div>
            </div>
        )
    }

    if (!metadata) {
        return (
            <div className="min-h-screen flex items-center justify-center">
                <div className="text-center">
                    <p className="text-red-400">Template not found</p>
                    <button onClick={() => navigate('/combo/select')} className="mt-4 text-blue-400">
                        ← Back to templates
                    </button>
                </div>
            </div>
        )
    }

    return (
        <div className="min-h-screen relative overflow-hidden">
            {/* Animated background */}
            <div className="fixed inset-0 -z-10">
                <div className="absolute top-0 left-1/4 w-96 h-96 bg-blue-500/20 rounded-full blur-3xl animate-float"></div>
                <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-purple-500/20 rounded-full blur-3xl animate-float" style={{ animationDelay: '2s' }}></div>
            </div>

            {/* Header */}
            <header className="glass-strong border-b border-white/10 sticky top-0 z-50">
                <div className="container mx-auto px-6 py-6">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center gap-4">
                            <div className="relative">
                                <div className="absolute inset-0 bg-gradient-to-r from-blue-500 to-purple-500 rounded-xl blur opacity-75 animate-pulse"></div>
                                <div className="relative bg-gradient-to-br from-blue-500 to-purple-600 p-2.5 rounded-xl shadow-glow-blue">
                                    <Settings className="w-7 h-7 text-white" />
                                </div>
                            </div>
                            <div>
                                <h1 className="text-3xl font-bold gradient-text">Configure Backtest</h1>
                                <p className="text-sm text-gray-400 mt-0.5">{metadata.name}</p>
                            </div>
                        </div>
                        <button
                            onClick={() => navigate('/combo/select')}
                            className="text-gray-400 hover:text-white transition-colors"
                        >
                            ← Back to Templates
                        </button>
                    </div>
                </div>
            </header>

            {/* Main Content */}
            <main className="container mx-auto px-6 py-12">
                <div className="max-w-4xl mx-auto space-y-8">
                    {/* Template Info */}
                    <div className="glass-strong rounded-2xl p-6 border border-white/10">
                        <h2 className="text-xl font-bold text-white mb-4">Template Information</h2>
                        <div className="space-y-3">
                            <div>
                                <span className="text-gray-400 text-sm">Description:</span>
                                <p className="text-white">{metadata.description}</p>
                            </div>
                            <div>
                                <span className="text-gray-400 text-sm">Indicators:</span>
                                <div className="flex flex-wrap gap-2 mt-2">
                                    {metadata.indicators.map((ind, i) => (
                                        <span key={i} className="px-3 py-1 bg-blue-500/20 text-blue-400 rounded-lg text-sm border border-blue-500/30">
                                            {ind.alias || ind.type}
                                        </span>
                                    ))}
                                </div>
                            </div>
                            <div>
                                <span className="text-gray-400 text-sm">Entry Logic:</span>
                                <code className="block mt-1 p-3 bg-black/30 rounded-lg text-green-400 text-sm font-mono">
                                    {metadata.entry_logic}
                                </code>
                            </div>
                            <div>
                                <span className="text-gray-400 text-sm">Exit Logic:</span>
                                <code className="block mt-1 p-3 bg-black/30 rounded-lg text-red-400 text-sm font-mono">
                                    {metadata.exit_logic}
                                </code>
                            </div>
                        </div>
                    </div>

                    {/* Configuration */}
                    <div className="glass-strong rounded-2xl p-6 border border-white/10">
                        <h2 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
                            <TrendingUp className="w-5 h-5" />
                            Configuration
                        </h2>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            {/* Symbol */}
                            <div>
                                <label className="block text-sm font-semibold text-gray-300 mb-2">
                                    <DollarSign className="w-4 h-4 inline mr-1" />
                                    Symbol
                                </label>
                                <select
                                    value={symbol}
                                    onChange={(e) => setSymbol(e.target.value)}
                                    className="w-full glass px-4 py-3 rounded-lg border border-white/10 text-white focus:border-blue-500 focus:outline-none"
                                >
                                    <option value="BTC/USDT">BTC/USDT</option>
                                    <option value="ETH/USDT">ETH/USDT</option>
                                    <option value="BNB/USDT">BNB/USDT</option>
                                    <option value="SOL/USDT">SOL/USDT</option>
                                </select>
                            </div>

                            {/* Timeframe */}
                            <div>
                                <label className="block text-sm font-semibold text-gray-300 mb-2">
                                    Timeframe
                                </label>
                                <select
                                    value={timeframe}
                                    onChange={(e) => setTimeframe(e.target.value)}
                                    className="w-full glass px-4 py-3 rounded-lg border border-white/10 text-white focus:border-blue-500 focus:outline-none"
                                >
                                    <option value="1m">1 minute</option>
                                    <option value="5m">5 minutes</option>
                                    <option value="15m">15 minutes</option>
                                    <option value="1h">1 hour</option>
                                    <option value="4h">4 hours</option>
                                    <option value="1d">1 day</option>
                                </select>
                            </div>
                        </div>

                        <div className="mt-4 p-3 bg-blue-500/10 border border-blue-500/30 rounded-lg">
                            <p className="text-sm text-blue-300 flex items-center gap-2">
                                <Calendar className="w-4 h-4" />
                                Will use all available historical data for this symbol
                            </p>
                        </div>
                    </div>

                    {/* Parameter Optimization Ranges */}
                    {params.length > 0 && (
                        <div className="glass-strong rounded-2xl p-6 border border-white/10">
                            <h2 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
                                <Sliders className="w-5 h-5" />
                                Parameter Optimization Ranges
                            </h2>

                            <div className="space-y-4">
                                {params.map((param, idx) => (
                                    <div key={idx} className="bg-white/5 rounded-lg p-4">
                                        <div className="flex justify-between items-center mb-3">
                                            <span className="text-sm font-medium text-purple-300">{param.name}</span>
                                            <span className="text-xs text-gray-500 bg-black/30 px-2 py-1 rounded">
                                                {param.group}
                                            </span>
                                        </div>
                                        <div className="grid grid-cols-3 gap-3">
                                            <div>
                                                <label className="text-xs text-gray-400 block mb-1">Min</label>
                                                <input
                                                    type="number"
                                                    value={param.min}
                                                    onChange={(e) => {
                                                        const newParams = [...params]
                                                        newParams[idx].min = parseFloat(e.target.value)
                                                        setParams(newParams)
                                                    }}
                                                    className="w-full bg-black/40 border border-white/10 rounded-lg px-3 py-2 text-sm text-white focus:border-purple-500 focus:outline-none"
                                                />
                                            </div>
                                            <div>
                                                <label className="text-xs text-gray-400 block mb-1">Max</label>
                                                <input
                                                    type="number"
                                                    value={param.max}
                                                    onChange={(e) => {
                                                        const newParams = [...params]
                                                        newParams[idx].max = parseFloat(e.target.value)
                                                        setParams(newParams)
                                                    }}
                                                    className="w-full bg-black/40 border border-white/10 rounded-lg px-3 py-2 text-sm text-white focus:border-purple-500 focus:outline-none"
                                                />
                                            </div>
                                            <div>
                                                <label className="text-xs text-gray-400 block mb-1">Step</label>
                                                <input
                                                    type="number"
                                                    value={param.step}
                                                    onChange={(e) => {
                                                        const newParams = [...params]
                                                        newParams[idx].step = parseFloat(e.target.value)
                                                        setParams(newParams)
                                                    }}
                                                    className="w-full bg-black/40 border border-white/10 rounded-lg px-3 py-2 text-sm text-white focus:border-purple-500 focus:outline-none"
                                                />
                                            </div>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}

                    {/* Run Button */}
                    <div className="flex justify-center">
                        <button
                            onClick={handleRunOptimization}
                            disabled={running}
                            className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-500 hover:to-pink-500 disabled:from-gray-600 disabled:to-gray-700 text-white font-bold py-4 px-12 rounded-xl transition-all duration-300 flex items-center gap-3 shadow-lg shadow-purple-500/50 hover:scale-105 disabled:scale-100 disabled:cursor-not-allowed"
                        >
                            {running ? (
                                <>
                                    <Settings className="w-5 h-5 animate-spin" />
                                    Running Optimization...
                                </>
                            ) : (
                                <>
                                    <Sliders className="w-5 h-5" />
                                    Run Optimization
                                </>
                            )}
                        </button>
                    </div>
                </div>
            </main>
        </div>
    )
}
