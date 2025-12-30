// src/components/CustomBacktestForm.tsx
import { useState } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { backtestApi, type BacktestRunCreate } from '../lib/api'
import { StrategyBuilder } from './StrategyBuilder'
import {
    PlayCircle,
    Activity,
    Settings,
    TrendingUp,
    X,
    Target,
    Layers,
    DollarSign,
    Percent,
    Plus,
    FlaskConical,
    Calendar,
    BarChart3
} from 'lucide-react'

interface CustomBacktestFormProps {
    onClose: () => void
    onSuccess: () => void
}

const AVAILABLE_STRATEGIES = [
    {
        id: 'sma_cross',
        name: 'SMA Cross',
        description: 'Classic trend following with two moving averages',
        icon: TrendingUp,
        params: { fast: 20, slow: 50 },
        color: 'blue'
    },
    {
        id: 'rsi_reversal',
        name: 'RSI Reversal',
        description: 'Mean reversion strategy based on overbought/oversold levels',
        icon: Activity,
        params: { rsi_period: 14, oversold: 30, overbought: 70 },
        color: 'purple'
    },
    {
        id: 'bb_meanrev',
        name: 'Bollinger Bands',
        description: 'Trade reversals from upper/lower volatility bands',
        icon: Layers,
        params: { bb_period: 20, bb_std: 2.0, exit_mode: 'mid' },
        color: 'amber'
    },
]

const SYMBOLS = ['BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'SOL/USDT', 'ADA/USDT']
const TIMEFRAMES = ['5m', '15m', '30m', '1h', '2h', '4h', '1d', '3d', '1w']

export function CustomBacktestForm({ onClose, onSuccess }: CustomBacktestFormProps) {
    const queryClient = useQueryClient()
    const [mode, setMode] = useState<'run' | 'compare'>('run')
    const [symbol, setSymbol] = useState('BTC/USDT')
    const [timeframe, setTimeframe] = useState('1d')
    const [selectedStrategies, setSelectedStrategies] = useState<string[]>(['sma_cross'])

    // Custom Strategies State
    const [customStrategies, setCustomStrategies] = useState<any[]>([])
    const [isBuilderOpen, setIsBuilderOpen] = useState(false)

    // Params
    const [cash, setCash] = useState(10000)
    const [fee, setFee] = useState(0.001)
    const [slippage, setSlippage] = useState(0.0005)
    const [stopPct, setStopPct] = useState<number | null>(null)
    const [takePct, setTakePct] = useState<number | null>(null)

    // Legacy Strategy params (kept for presets)
    const [smaFast, setSmaFast] = useState(20)
    const [smaSlow, setSmaSlow] = useState(50)
    const [rsiPeriod, setRsiPeriod] = useState(14)
    const [rsiOversold, setRsiOversold] = useState(30)
    const [rsiOverbought, setRsiOverbought] = useState(70)
    const [bbPeriod, setBbPeriod] = useState(20)
    const [bbStd, setBbStd] = useState(2.0)
    const [bbExitMode, setBbExitMode] = useState('mid')

    // Date range
    const [sinceDate, setSinceDate] = useState(() => {
        const date = new Date()
        date.setFullYear(date.getFullYear() - 1)
        return date.toISOString().split('T')[0]
    })
    const [untilDate, setUntilDate] = useState(() => {
        return new Date().toISOString().split('T')[0]
    })

    const runMutation = useMutation({
        mutationFn: async (config: BacktestRunCreate) => {
            const endpoint = config.mode === 'compare'
                ? backtestApi.createCompare
                : backtestApi.createRun
            const response = await endpoint(config)
            return response.data
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['runs'] })
            onSuccess()
            onClose()
        },
    })

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault()

        // Prepare strategy configuration list
        const strategiesPayload = selectedStrategies.map(id => {
            const custom = customStrategies.find(c => c.id === id)
            if (custom) {
                return custom.config
            }
            return id
        })

        // Build legacy params for presets
        const params: Record<string, any> = {}
        if (selectedStrategies.includes('sma_cross')) {
            params.sma_cross = { fast: smaFast, slow: smaSlow }
        }
        if (selectedStrategies.includes('rsi_reversal')) {
            params.rsi_reversal = { rsi_period: rsiPeriod, oversold: rsiOversold, overbought: rsiOverbought }
        }
        if (selectedStrategies.includes('bb_meanrev')) {
            params.bb_meanrev = { bb_period: bbPeriod, bb_std: bbStd, exit_mode: bbExitMode }
        }

        const config: BacktestRunCreate = {
            mode,
            exchange: 'binance',
            symbol,
            timeframe,
            since: `${sinceDate} 00:00:00`,
            until: untilDate ? `${untilDate} 23:59:59` : null,
            strategies: strategiesPayload,
            params: Object.keys(params).length > 0 ? params : null,
            cash,
            fee,
            slippage,
            stop_pct: stopPct,
            take_pct: takePct,
            fill_mode: 'close',
        }

        runMutation.mutate(config)
    }

    const toggleStrategy = (strategyId: string) => {
        if (mode === 'run') {
            setSelectedStrategies([strategyId])
        } else {
            if (selectedStrategies.includes(strategyId)) {
                if (selectedStrategies.length > 1) {
                    setSelectedStrategies(selectedStrategies.filter(s => s !== strategyId))
                }
            } else {
                if (selectedStrategies.length < 3) {
                    setSelectedStrategies([...selectedStrategies, strategyId])
                }
            }
        }
    }

    const handleSaveCustomStrategy = (config: any) => {
        const id = `custom_${Date.now()}`
        const newStrategy = {
            id,
            name: config.name,
            description: 'Custom Strategy',
            icon: FlaskConical,
            config: config
        }
        setCustomStrategies([...customStrategies, newStrategy])
        toggleStrategy(id)
        setIsBuilderOpen(false)
    }

    if (isBuilderOpen) {
        return (
            <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm">
                <div className="w-full max-w-6xl h-[90vh] bg-[#0a0f1c] border border-white/5 rounded-3xl shadow-2xl flex flex-col overflow-hidden relative">
                    <StrategyBuilder
                        onSave={handleSaveCustomStrategy}
                        onCancel={() => setIsBuilderOpen(false)}
                    />
                </div>
            </div>
        )
    }

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm">
            <div className="w-full max-w-5xl max-h-[90vh] bg-[#0a0f1c] border border-white/5 rounded-3xl shadow-2xl flex flex-col overflow-hidden">

                {/* Header */}
                <div className="flex items-center justify-between p-6 border-b border-white/5 bg-white/[0.02]">
                    <div className="flex items-center gap-4">
                        <div className="bg-gradient-to-br from-blue-600 to-purple-600 p-3 rounded-2xl shadow-lg shadow-blue-500/20">
                            <Settings className="w-6 h-6 text-white" />
                        </div>
                        <div>
                            <h2 className="text-2xl font-bold text-white">New Backtest</h2>
                            <p className="text-gray-400 text-sm">Configure and run your simulation</p>
                        </div>
                    </div>
                    <button
                        onClick={onClose}
                        className="p-2.5 hover:bg-white/5 rounded-xl transition-all text-gray-400 hover:text-white"
                    >
                        <X className="w-6 h-6" />
                    </button>
                </div>

                {/* Content */}
                <div className="flex-1 overflow-y-auto p-8 space-y-8 custom-scrollbar">

                    {/* Market Selection */}
                    <section className="space-y-4">
                        <h3 className="text-sm font-bold text-gray-400 uppercase tracking-wider flex items-center gap-2">
                            <BarChart3 className="w-4 h-4" />
                            Market Configuration
                        </h3>
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                            <div>
                                <label className="block text-xs text-gray-500 mb-2 uppercase font-semibold">Symbol</label>
                                <select
                                    value={symbol}
                                    onChange={(e) => setSymbol(e.target.value)}
                                    className="w-full bg-white/[0.03] border border-white/10 rounded-xl px-4 h-12 text-white appearance-none focus:border-blue-500/50 transition-all outline-none cursor-pointer"
                                >
                                    {SYMBOLS.map(s => (
                                        <option key={s} value={s} className="bg-slate-900">{s}</option>
                                    ))}
                                </select>
                            </div>
                            <div>
                                <label className="block text-xs text-gray-500 mb-2 uppercase font-semibold">Timeframe</label>
                                <select
                                    value={timeframe}
                                    onChange={(e) => setTimeframe(e.target.value)}
                                    className="w-full bg-white/[0.03] border border-white/10 rounded-xl px-4 h-12 text-white appearance-none focus:border-blue-500/50 transition-all outline-none cursor-pointer"
                                >
                                    {TIMEFRAMES.map(tf => (
                                        <option key={tf} value={tf} className="bg-slate-900">{tf}</option>
                                    ))}
                                </select>
                            </div>
                            <div>
                                <label className="block text-xs text-gray-500 mb-2 uppercase font-semibold">Mode</label>
                                <div className="flex bg-slate-900/80 p-1.5 rounded-xl border border-white/5 h-12">
                                    <button
                                        type="button"
                                        onClick={() => {
                                            setMode('run')
                                            if (selectedStrategies.length > 1) setSelectedStrategies([selectedStrategies[0]])
                                        }}
                                        className={`flex-1 text-xs font-semibold rounded-lg transition-all ${mode === 'run'
                                            ? 'bg-blue-600 text-white shadow-lg'
                                            : 'text-gray-400 hover:text-white'}`}
                                    >
                                        Single
                                    </button>
                                    <button
                                        type="button"
                                        onClick={() => setMode('compare')}
                                        className={`flex-1 text-xs font-semibold rounded-lg transition-all ${mode === 'compare'
                                            ? 'bg-purple-600 text-white shadow-lg'
                                            : 'text-gray-400 hover:text-white'}`}
                                    >
                                        Compare
                                    </button>
                                </div>
                            </div>
                        </div>
                    </section>

                    {/* Date Range */}
                    <section className="space-y-4">
                        <h3 className="text-sm font-bold text-gray-400 uppercase tracking-wider flex items-center gap-2">
                            <Calendar className="w-4 h-4" />
                            Time Period
                        </h3>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div>
                                <label className="block text-xs text-gray-500 mb-2 uppercase font-semibold">Start Date</label>
                                <input
                                    type="date"
                                    value={sinceDate}
                                    onChange={(e) => setSinceDate(e.target.value)}
                                    className="w-full bg-white/[0.03] border border-white/10 rounded-xl px-4 h-12 text-white focus:border-blue-500/50 transition-all outline-none"
                                />
                            </div>
                            <div>
                                <label className="block text-xs text-gray-500 mb-2 uppercase font-semibold">End Date</label>
                                <input
                                    type="date"
                                    value={untilDate}
                                    onChange={(e) => setUntilDate(e.target.value)}
                                    className="w-full bg-white/[0.03] border border-white/10 rounded-xl px-4 h-12 text-white focus:border-blue-500/50 transition-all outline-none"
                                />
                            </div>
                        </div>
                    </section>

                    {/* Strategy Selection */}
                    <section className="space-y-4">
                        <h3 className="text-sm font-bold text-gray-400 uppercase tracking-wider flex items-center gap-2">
                            <Target className="w-4 h-4" />
                            Select Strategy {mode === 'compare' && <span className="text-purple-400">(2-3)</span>}
                        </h3>
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                            {AVAILABLE_STRATEGIES.map((strategy) => {
                                const isSelected = selectedStrategies.includes(strategy.id)
                                const isDisabled = mode === 'compare' && selectedStrategies.length >= 3 && !isSelected
                                const Icon = strategy.icon

                                return (
                                    <button
                                        key={strategy.id}
                                        type="button"
                                        onClick={() => toggleStrategy(strategy.id)}
                                        disabled={isDisabled}
                                        className={`relative p-5 rounded-2xl border text-left transition-all ${isSelected
                                            ? 'bg-blue-500/10 border-blue-500 shadow-lg shadow-blue-500/10'
                                            : 'bg-white/[0.02] border-white/5 hover:border-white/20 hover:bg-white/[0.04]'
                                            } ${isDisabled ? 'opacity-30 cursor-not-allowed' : ''}`}
                                    >
                                        <div className={`w-10 h-10 rounded-xl flex items-center justify-center mb-3 ${isSelected
                                            ? 'bg-blue-500 text-white'
                                            : 'bg-white/5 text-gray-400'}`}>
                                            <Icon className="w-5 h-5" />
                                        </div>
                                        <h4 className={`font-bold text-sm mb-1 ${isSelected ? 'text-white' : 'text-gray-300'}`}>
                                            {strategy.name}
                                        </h4>
                                        <p className="text-xs text-gray-500 leading-relaxed">
                                            {strategy.description}
                                        </p>
                                        {isSelected && (
                                            <div className="absolute top-4 right-4 w-2 h-2 rounded-full bg-blue-400 shadow-[0_0_10px_2px_rgba(96,165,250,0.5)]" />
                                        )}
                                    </button>
                                )
                            })}

                            {customStrategies.map((strategy) => {
                                const isSelected = selectedStrategies.includes(strategy.id)
                                const isDisabled = mode === 'compare' && selectedStrategies.length >= 3 && !isSelected
                                const Icon = strategy.icon

                                return (
                                    <button
                                        key={strategy.id}
                                        type="button"
                                        onClick={() => toggleStrategy(strategy.id)}
                                        disabled={isDisabled}
                                        className={`relative p-5 rounded-2xl border text-left transition-all ${isSelected
                                            ? 'bg-green-500/10 border-green-500 shadow-lg shadow-green-500/10'
                                            : 'bg-white/[0.02] border-white/5 hover:border-white/20 hover:bg-white/[0.04]'
                                            } ${isDisabled ? 'opacity-30 cursor-not-allowed' : ''}`}
                                    >
                                        <div className={`w-10 h-10 rounded-xl flex items-center justify-center mb-3 ${isSelected
                                            ? 'bg-green-500 text-white'
                                            : 'bg-white/5 text-gray-400'}`}>
                                            <Icon className="w-5 h-5" />
                                        </div>
                                        <h4 className={`font-bold text-sm mb-1 ${isSelected ? 'text-white' : 'text-gray-300'}`}>
                                            {strategy.name}
                                        </h4>
                                        <p className="text-xs text-gray-500">
                                            {strategy.description}
                                        </p>
                                        {isSelected && (
                                            <div className="absolute top-4 right-4 w-2 h-2 rounded-full bg-green-400 shadow-[0_0_10px_2px_rgba(74,222,128,0.5)]" />
                                        )}
                                    </button>
                                )
                            })}

                            <button
                                type="button"
                                onClick={() => setIsBuilderOpen(true)}
                                className="p-5 rounded-2xl border border-dashed border-white/20 text-left transition-all hover:border-blue-500 hover:bg-blue-500/5 flex flex-col items-center justify-center text-gray-500 hover:text-blue-400 min-h-[160px]"
                            >
                                <div className="w-12 h-12 rounded-full bg-white/5 flex items-center justify-center mb-3">
                                    <Plus className="w-6 h-6" />
                                </div>
                                <span className="font-semibold text-sm">Add Custom</span>
                            </button>
                        </div>
                    </section>

                    {/* Risk Management */}
                    <section className="space-y-4">
                        <h3 className="text-sm font-bold text-gray-400 uppercase tracking-wider flex items-center gap-2">
                            <DollarSign className="w-4 h-4" />
                            Risk & Money Management
                        </h3>
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                            <div>
                                <label className="block text-xs text-gray-500 mb-2 uppercase font-semibold">Initial Cash</label>
                                <input
                                    type="number"
                                    value={cash}
                                    onChange={(e) => setCash(Number(e.target.value))}
                                    className="w-full bg-white/[0.03] border border-white/10 rounded-xl px-4 h-12 text-white focus:border-blue-500/50 transition-all outline-none"
                                    step="100"
                                />
                            </div>
                            <div>
                                <label className="block text-xs text-gray-500 mb-2 uppercase font-semibold">Trading Fee %</label>
                                <input
                                    type="number"
                                    value={fee * 100}
                                    onChange={(e) => setFee(Number(e.target.value) / 100)}
                                    className="w-full bg-white/[0.03] border border-white/10 rounded-xl px-4 h-12 text-white focus:border-blue-500/50 transition-all outline-none"
                                    step="0.01"
                                />
                            </div>
                            <div>
                                <label className="block text-xs text-gray-500 mb-2 uppercase font-semibold">Stop Loss %</label>
                                <input
                                    type="number"
                                    value={stopPct ? stopPct * 100 : ''}
                                    onChange={(e) => setStopPct(e.target.value ? Number(e.target.value) / 100 : null)}
                                    placeholder="Optional"
                                    className="w-full bg-white/[0.03] border border-white/10 rounded-xl px-4 h-12 text-white placeholder-gray-600 focus:border-red-500/50 transition-all outline-none"
                                    step="0.5"
                                />
                            </div>
                            <div>
                                <label className="block text-xs text-gray-500 mb-2 uppercase font-semibold">Take Profit %</label>
                                <input
                                    type="number"
                                    value={takePct ? takePct * 100 : ''}
                                    onChange={(e) => setTakePct(e.target.value ? Number(e.target.value) / 100 : null)}
                                    placeholder="Optional"
                                    className="w-full bg-white/[0.03] border border-white/10 rounded-xl px-4 h-12 text-white placeholder-gray-600 focus:border-green-500/50 transition-all outline-none"
                                    step="0.5"
                                />
                            </div>
                        </div>
                    </section>

                    {/* Preset Parameters (only if preset strategies selected) */}
                    {selectedStrategies.filter(id => !id.startsWith('custom_')).length > 0 && (
                        <section className="space-y-4">
                            <h3 className="text-sm font-bold text-gray-400 uppercase tracking-wider">Preset Parameters</h3>
                            <div className="space-y-6">
                                {selectedStrategies.includes('sma_cross') && (
                                    <div className="bg-white/[0.02] border border-white/5 rounded-2xl p-6">
                                        <h4 className="text-sm font-bold text-blue-400 mb-4 uppercase tracking-wider">SMA Cross</h4>
                                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                            <div>
                                                <label className="block text-xs text-gray-500 mb-2 uppercase font-semibold">Fast Period</label>
                                                <input
                                                    type="number"
                                                    value={smaFast}
                                                    onChange={(e) => setSmaFast(Number(e.target.value))}
                                                    className="w-full bg-black/20 border border-white/10 rounded-xl px-4 h-10 text-white focus:border-blue-500/50 transition-all outline-none"
                                                />
                                            </div>
                                            <div>
                                                <label className="block text-xs text-gray-500 mb-2 uppercase font-semibold">Slow Period</label>
                                                <input
                                                    type="number"
                                                    value={smaSlow}
                                                    onChange={(e) => setSmaSlow(Number(e.target.value))}
                                                    className="w-full bg-black/20 border border-white/10 rounded-xl px-4 h-10 text-white focus:border-blue-500/50 transition-all outline-none"
                                                />
                                            </div>
                                        </div>
                                    </div>
                                )}

                                {selectedStrategies.includes('rsi_reversal') && (
                                    <div className="bg-white/[0.02] border border-white/5 rounded-2xl p-6">
                                        <h4 className="text-sm font-bold text-purple-400 mb-4 uppercase tracking-wider">RSI Reversal</h4>
                                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                                            <div>
                                                <label className="block text-xs text-gray-500 mb-2 uppercase font-semibold">Period</label>
                                                <input
                                                    type="number"
                                                    value={rsiPeriod}
                                                    onChange={(e) => setRsiPeriod(Number(e.target.value))}
                                                    className="w-full bg-black/20 border border-white/10 rounded-xl px-4 h-10 text-white focus:border-purple-500/50 transition-all outline-none"
                                                />
                                            </div>
                                            <div>
                                                <label className="block text-xs text-gray-500 mb-2 uppercase font-semibold">Oversold</label>
                                                <input
                                                    type="number"
                                                    value={rsiOversold}
                                                    onChange={(e) => setRsiOversold(Number(e.target.value))}
                                                    className="w-full bg-black/20 border border-white/10 rounded-xl px-4 h-10 text-white focus:border-purple-500/50 transition-all outline-none"
                                                />
                                            </div>
                                            <div>
                                                <label className="block text-xs text-gray-500 mb-2 uppercase font-semibold">Overbought</label>
                                                <input
                                                    type="number"
                                                    value={rsiOverbought}
                                                    onChange={(e) => setRsiOverbought(Number(e.target.value))}
                                                    className="w-full bg-black/20 border border-white/10 rounded-xl px-4 h-10 text-white focus:border-purple-500/50 transition-all outline-none"
                                                />
                                            </div>
                                        </div>
                                    </div>
                                )}

                                {selectedStrategies.includes('bb_meanrev') && (
                                    <div className="bg-white/[0.02] border border-white/5 rounded-2xl p-6">
                                        <h4 className="text-sm font-bold text-amber-400 mb-4 uppercase tracking-wider">Bollinger Bands</h4>
                                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                                            <div>
                                                <label className="block text-xs text-gray-500 mb-2 uppercase font-semibold">Period</label>
                                                <input
                                                    type="number"
                                                    value={bbPeriod}
                                                    onChange={(e) => setBbPeriod(Number(e.target.value))}
                                                    className="w-full bg-black/20 border border-white/10 rounded-xl px-4 h-10 text-white focus:border-amber-500/50 transition-all outline-none"
                                                />
                                            </div>
                                            <div>
                                                <label className="block text-xs text-gray-500 mb-2 uppercase font-semibold">Std Dev</label>
                                                <input
                                                    type="number"
                                                    value={bbStd}
                                                    onChange={(e) => setBbStd(Number(e.target.value))}
                                                    step="0.1"
                                                    className="w-full bg-black/20 border border-white/10 rounded-xl px-4 h-10 text-white focus:border-amber-500/50 transition-all outline-none"
                                                />
                                            </div>
                                            <div>
                                                <label className="block text-xs text-gray-500 mb-2 uppercase font-semibold">Exit Mode</label>
                                                <select
                                                    value={bbExitMode}
                                                    onChange={(e) => setBbExitMode(e.target.value)}
                                                    className="w-full bg-black/20 border border-white/10 rounded-xl px-4 h-10 text-white focus:border-amber-500/50 transition-all outline-none cursor-pointer"
                                                >
                                                    <option value="mid" className="bg-slate-900">Middle Band</option>
                                                    <option value="upper" className="bg-slate-900">Upper Band</option>
                                                </select>
                                            </div>
                                        </div>
                                    </div>
                                )}
                            </div>
                        </section>
                    )}
                </div>

                {/* Footer */}
                <div className="p-6 border-t border-white/5 bg-white/[0.02] flex justify-end gap-4">
                    <button
                        type="button"
                        onClick={onClose}
                        className="px-6 py-3 rounded-xl text-sm font-semibold text-gray-400 hover:text-white hover:bg-white/5 transition-all"
                    >
                        Cancel
                    </button>
                    <button
                        onClick={handleSubmit}
                        disabled={runMutation.isPending || selectedStrategies.length === 0}
                        className="bg-gradient-to-r from-blue-600 via-purple-600 to-blue-600 bg-[length:200%_auto] hover:bg-right disabled:opacity-50 disabled:cursor-not-allowed text-white font-bold text-sm px-8 py-3 rounded-xl shadow-xl shadow-blue-900/20 transition-all flex items-center gap-3"
                    >
                        {runMutation.isPending ? (
                            <>
                                <Activity className="w-5 h-5 animate-spin" />
                                Processing...
                            </>
                        ) : (
                            <>
                                <PlayCircle className="w-5 h-5" />
                                Run Backtest
                            </>
                        )}
                    </button>
                </div>
            </div>
        </div>
    )
}
