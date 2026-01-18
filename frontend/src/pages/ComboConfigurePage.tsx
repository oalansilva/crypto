import { useState, useEffect } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { Play, Settings, TrendingUp, Calendar, DollarSign } from 'lucide-react'

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

    // Backtest parameters
    const [symbol, setSymbol] = useState('BTC/USDT')
    const [timeframe, setTimeframe] = useState('1h')
    const [startDate, setStartDate] = useState('2024-01-01')
    const [endDate, setEndDate] = useState('2024-12-31')
    const [parameters, setParameters] = useState<Record<string, any>>({})

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

            // Initialize parameters with defaults
            const defaultParams: Record<string, any> = {}
            data.indicators.forEach((ind: any) => {
                Object.entries(ind.params).forEach(([key, value]) => {
                    const paramKey = ind.alias ? `${ind.alias}_${key}` : `${ind.type}_${key}`
                    defaultParams[paramKey] = value
                })
            })
            setParameters(defaultParams)
        } catch (error) {
            console.error('Failed to fetch metadata:', error)
        } finally {
            setLoading(false)
        }
    }

    const handleRunBacktest = async () => {
        setRunning(true)
        try {
            const response = await fetch('http://localhost:8000/api/combos/backtest', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    template_name: templateName,
                    symbol,
                    timeframe,
                    start_date: startDate,
                    end_date: endDate,
                    parameters
                })
            })

            if (response.ok) {
                const result = await response.json()
                // Navigate to results page with data
                navigate('/combo/results', { state: { result } })
            } else {
                alert('Backtest failed. Check console for details.')
            }
        } catch (error) {
            console.error('Backtest error:', error)
            alert('Failed to run backtest')
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

                    {/* Backtest Configuration */}
                    <div className="glass-strong rounded-2xl p-6 border border-white/10">
                        <h2 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
                            <TrendingUp className="w-5 h-5" />
                            Backtest Configuration
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

                            {/* Start Date */}
                            <div>
                                <label className="block text-sm font-semibold text-gray-300 mb-2">
                                    <Calendar className="w-4 h-4 inline mr-1" />
                                    Start Date
                                </label>
                                <input
                                    type="date"
                                    value={startDate}
                                    onChange={(e) => setStartDate(e.target.value)}
                                    className="w-full glass px-4 py-3 rounded-lg border border-white/10 text-white focus:border-blue-500 focus:outline-none"
                                />
                            </div>

                            {/* End Date */}
                            <div>
                                <label className="block text-sm font-semibold text-gray-300 mb-2">
                                    <Calendar className="w-4 h-4 inline mr-1" />
                                    End Date
                                </label>
                                <input
                                    type="date"
                                    value={endDate}
                                    onChange={(e) => setEndDate(e.target.value)}
                                    className="w-full glass px-4 py-3 rounded-lg border border-white/10 text-white focus:border-blue-500 focus:outline-none"
                                />
                            </div>
                        </div>
                    </div>

                    {/* Run Button */}
                    <div className="flex justify-center">
                        <button
                            onClick={handleRunBacktest}
                            disabled={running}
                            className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-500 hover:to-purple-500 disabled:from-gray-600 disabled:to-gray-700 text-white font-bold py-4 px-8 rounded-xl transition-all duration-300 flex items-center gap-3 shadow-lg shadow-blue-500/50 hover:scale-105 disabled:scale-100 disabled:cursor-not-allowed"
                        >
                            {running ? (
                                <>
                                    <Settings className="w-5 h-5 animate-spin" />
                                    Running Backtest...
                                </>
                            ) : (
                                <>
                                    <Play className="w-5 h-5" />
                                    Run Backtest
                                </>
                            )}
                        </button>
                    </div>
                </div>
            </main>
        </div>
    )
}
