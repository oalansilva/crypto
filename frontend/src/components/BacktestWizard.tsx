// src/components/BacktestWizard.tsx
import { useState } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { backtestApi, type BacktestRunCreate } from '../lib/api'
import { Button, Input, Card } from './ui'
import {
    PlayCircle,
    Activity,
    TrendingUp,
    Layers,
    Calendar,
    DollarSign,
    ChevronLeft,
    ChevronRight,
    Check,
    FlaskConical
} from 'lucide-react'
import { StrategyBuilder } from './StrategyBuilder'

interface BacktestWizardProps {
    onSuccess: () => void
}

const AVAILABLE_STRATEGIES = [
    {
        id: 'sma_cross',
        name: 'SMA Cross',
        description: 'Classic trend following with two moving averages',
        icon: TrendingUp,
    },
    {
        id: 'rsi_reversal',
        name: 'RSI Reversal',
        description: 'Mean reversion based on overbought/oversold levels',
        icon: Activity,
    },
    {
        id: 'bb_meanrev',
        name: 'Bollinger Bands',
        description: 'Trade reversals from volatility bands',
        icon: Layers,
    },
]

const SYMBOLS = ['BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'SOL/USDT', 'ADA/USDT']
const TIMEFRAMES = ['5m', '15m', '30m', '1h', '2h', '4h', '1d', '3d', '1w']

export function BacktestWizard({ onSuccess }: BacktestWizardProps) {
    const queryClient = useQueryClient()
    const [currentStep, setCurrentStep] = useState(1)
    const [isBuilderOpen, setIsBuilderOpen] = useState(false)

    // Step 1: Market Setup
    const [symbol, setSymbol] = useState('BTC/USDT')
    const [timeframe, setTimeframe] = useState('1d')
    const [sinceDate, setSinceDate] = useState(() => {
        const date = new Date()
        date.setFullYear(date.getFullYear() - 1)
        return date.toISOString().split('T')[0]
    })
    const [untilDate, setUntilDate] = useState(() => new Date().toISOString().split('T')[0])
    const [fullPeriod, setFullPeriod] = useState(false)

    // Step 2: Strategy Selection
    const [selectedStrategies, setSelectedStrategies] = useState<string[]>(['sma_cross'])
    const [customStrategies, setCustomStrategies] = useState<any[]>([])

    // Step 3: Risk & Parameters
    const [cash, setCash] = useState(10000)
    const [fee, setFee] = useState(0.1)
    const [stopPct, setStopPct] = useState<number | null>(null)
    const [takePct, setTakePct] = useState<number | null>(null)

    const runMutation = useMutation({
        mutationFn: async (config: BacktestRunCreate) => {
            const endpoint = backtestApi.createRun
            const response = await endpoint(config)
            return response.data
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['runs'] })
            onSuccess()
        },
    })

    const handleSubmit = () => {
        const strategiesPayload = selectedStrategies.map(id => {
            const custom = customStrategies.find(c => c.id === id)
            if (custom) return custom.config
            return id
        })

        const config: BacktestRunCreate = {
            mode: 'run',
            exchange: 'binance',
            symbol,
            timeframe,
            full_period: fullPeriod,
            since: fullPeriod ? null : `${sinceDate} 00:00:00`,
            until: fullPeriod ? null : (untilDate ? `${untilDate} 23:59:59` : null),
            strategies: strategiesPayload,
            params: null,
            cash,
            fee: fee / 100,
            slippage: 0.0005,
            stop_pct: stopPct ? stopPct / 100 : null,
            take_pct: takePct ? takePct / 100 : null,
            fill_mode: 'close',
        }

        runMutation.mutate(config)
    }

    const toggleStrategy = (strategyId: string) => {
        if (selectedStrategies.includes(strategyId)) {
            if (selectedStrategies.length > 1) {
                setSelectedStrategies(selectedStrategies.filter(s => s !== strategyId))
            }
        } else {
            setSelectedStrategies([...selectedStrategies, strategyId])
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

    const steps = [
        { number: 1, title: 'Market', icon: Calendar },
        { number: 2, title: 'Strategy', icon: TrendingUp },
        { number: 3, title: 'Risk', icon: DollarSign },
    ]

    if (isBuilderOpen) {
        return (
            <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm">
                <div className="w-full max-w-6xl h-[90vh] bg-[var(--bg-primary)] border border-[var(--border-subtle)] rounded-3xl shadow-2xl flex flex-col overflow-hidden">
                    <StrategyBuilder
                        onSave={handleSaveCustomStrategy}
                        onCancel={() => setIsBuilderOpen(false)}
                    />
                </div>
            </div>
        )
    }

    return (
        <div className="w-full max-w-4xl mx-auto">
            {/* Progress Steps */}
            <div className="mb-12">
                <div className="flex items-center justify-between relative">
                    {/* Progress Line */}
                    <div className="absolute top-6 left-0 right-0 h-0.5 bg-[var(--border-default)]">
                        <div
                            className="h-full bg-gradient-to-r from-[var(--accent-primary)] to-[var(--accent-secondary)] transition-all duration-500"
                            style={{ width: `${((currentStep - 1) / (steps.length - 1)) * 100}%` }}
                        />
                    </div>

                    {/* Step Indicators */}
                    {steps.map((step) => {
                        const isActive = currentStep === step.number
                        const isCompleted = currentStep > step.number
                        const Icon = step.icon

                        return (
                            <div key={step.number} className="flex flex-col items-center relative z-10">
                                <div
                                    className={`w-12 h-12 rounded-full flex items-center justify-center mb-2 transition-all duration-300 ${isCompleted
                                        ? 'bg-gradient-to-br from-[var(--accent-primary)] to-[var(--accent-secondary)] shadow-[var(--shadow-glow-blue)]'
                                        : isActive
                                            ? 'bg-gradient-to-br from-[var(--accent-primary)] to-[var(--accent-secondary)] shadow-[var(--shadow-glow-blue)] scale-110'
                                            : 'bg-[var(--bg-elevated)] border-2 border-[var(--border-default)]'
                                        }`}
                                >
                                    {isCompleted ? (
                                        <Check className="w-5 h-5 text-white" />
                                    ) : (
                                        <Icon className={`w-5 h-5 ${isActive ? 'text-white' : 'text-[var(--text-tertiary)]'}`} />
                                    )}
                                </div>
                                <span className={`text-xs font-semibold uppercase tracking-wide ${isActive ? 'text-white' : 'text-[var(--text-tertiary)]'
                                    }`}>
                                    {step.title}
                                </span>
                            </div>
                        )
                    })}
                </div>
            </div>

            {/* Step Content */}
            <Card className="p-8 mb-8 animate-slide-up">
                {/* Step 1: Market Setup */}
                {currentStep === 1 && (
                    <div className="space-y-6">
                        <div>
                            <h3 className="text-2xl font-bold text-white mb-2">Market Configuration</h3>
                            <p className="text-[var(--text-secondary)]">Select the asset and timeframe for your backtest</p>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <div>
                                <label className="block text-xs text-[var(--text-secondary)] mb-2 uppercase font-semibold">Symbol</label>
                                <select
                                    value={symbol}
                                    onChange={(e) => setSymbol(e.target.value)}
                                    className="input cursor-pointer"
                                >
                                    {SYMBOLS.map(s => (
                                        <option key={s} value={s} className="bg-[var(--bg-elevated)]">{s}</option>
                                    ))}
                                </select>
                            </div>

                            <div>
                                <label className="block text-xs text-[var(--text-secondary)] mb-2 uppercase font-semibold">Timeframe</label>
                                <select
                                    value={timeframe}
                                    onChange={(e) => setTimeframe(e.target.value)}
                                    className="input cursor-pointer"
                                >
                                    {TIMEFRAMES.map(tf => (
                                        <option key={tf} value={tf} className="bg-[var(--bg-elevated)]">{tf}</option>
                                    ))}
                                </select>
                            </div>
                        </div>

                        <div className="flex items-center space-x-2 my-4">
                            <input
                                type="checkbox"
                                id="fullPeriod"
                                checked={fullPeriod}
                                onChange={(e) => setFullPeriod(e.target.checked)}
                                className="w-4 h-4 rounded border-[var(--border-default)] bg-[var(--bg-elevated)] text-[var(--accent-primary)] focus:ring-[var(--accent-primary)] focus:ring-offset-0"
                            />
                            <label htmlFor="fullPeriod" className="text-sm font-medium text-white cursor-pointer select-none">
                                Todo o período (Full History)
                            </label>
                        </div>

                        <div className={`grid grid-cols-1 md:grid-cols-2 gap-6 ${fullPeriod ? 'opacity-50 pointer-events-none' : ''}`}>
                            <Input
                                type="date"
                                label="Start Date"
                                value={sinceDate}
                                onChange={(e) => setSinceDate(e.target.value)}
                            />
                            <Input
                                type="date"
                                label="End Date"
                                value={untilDate}
                                onChange={(e) => setUntilDate(e.target.value)}
                            />
                        </div>
                    </div>
                )}

                {/* Step 2: Strategy Selection */}
                {currentStep === 2 && (
                    <div className="space-y-6">
                        <div>
                            <h3 className="text-2xl font-bold text-white mb-2">Select Strategy</h3>
                            <p className="text-[var(--text-secondary)]">Choose one or more strategies to test</p>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            {AVAILABLE_STRATEGIES.map((strategy) => {
                                const isSelected = selectedStrategies.includes(strategy.id)
                                const Icon = strategy.icon

                                return (
                                    <button
                                        key={strategy.id}
                                        type="button"
                                        onClick={() => toggleStrategy(strategy.id)}
                                        className={`p-6 rounded-xl border text-left transition-all ${isSelected
                                            ? 'bg-[var(--accent-primary)]/10 border-[var(--accent-primary)] shadow-[var(--shadow-glow-blue)]'
                                            : 'bg-[var(--bg-elevated)] border-[var(--border-subtle)] hover:border-[var(--border-default)]'
                                            }`}
                                    >
                                        <div className={`w-12 h-12 rounded-xl flex items-center justify-center mb-4 ${isSelected
                                            ? 'bg-[var(--accent-primary)] text-white'
                                            : 'bg-white/5 text-[var(--text-tertiary)]'}`}>
                                            <Icon className="w-6 h-6" />
                                        </div>
                                        <h4 className={`font-bold mb-2 ${isSelected ? 'text-white' : 'text-[var(--text-secondary)]'}`}>
                                            {strategy.name}
                                        </h4>
                                        <p className="text-sm text-[var(--text-tertiary)]">
                                            {strategy.description}
                                        </p>
                                    </button>
                                )
                            })}

                            {customStrategies.map((strategy) => {
                                const isSelected = selectedStrategies.includes(strategy.id)
                                const Icon = strategy.icon

                                return (
                                    <button
                                        key={strategy.id}
                                        type="button"
                                        onClick={() => toggleStrategy(strategy.id)}
                                        className={`p-6 rounded-xl border text-left transition-all ${isSelected
                                            ? 'bg-green-500/10 border-green-500 shadow-glow-green'
                                            : 'bg-[var(--bg-elevated)] border-[var(--border-subtle)] hover:border-[var(--border-default)]'
                                            }`}
                                    >
                                        <div className={`w-12 h-12 rounded-xl flex items-center justify-center mb-4 ${isSelected
                                            ? 'bg-green-500 text-white'
                                            : 'bg-white/5 text-[var(--text-tertiary)]'}`}>
                                            <Icon className="w-6 h-6" />
                                        </div>
                                        <h4 className={`font-bold mb-2 ${isSelected ? 'text-white' : 'text-[var(--text-secondary)]'}`}>
                                            {strategy.name}
                                        </h4>
                                        <p className="text-sm text-[var(--text-tertiary)]">
                                            {strategy.description}
                                        </p>
                                    </button>
                                )
                            })}

                            <button
                                type="button"
                                onClick={() => setIsBuilderOpen(true)}
                                className="p-6 rounded-xl border border-dashed border-[var(--border-default)] hover:border-[var(--accent-primary)] hover:bg-[var(--accent-primary)]/5 transition-all flex flex-col items-center justify-center text-[var(--text-tertiary)] hover:text-[var(--accent-primary)] min-h-[180px]"
                            >
                                <div className="w-12 h-12 rounded-full bg-white/5 flex items-center justify-center mb-4">
                                    <FlaskConical className="w-6 h-6" />
                                </div>
                                <span className="font-semibold">Create Custom</span>
                            </button>
                        </div>
                    </div>
                )}

                {/* Step 3: Risk & Parameters */}
                {currentStep === 3 && (
                    <div className="space-y-6">
                        <div>
                            <h3 className="text-2xl font-bold text-white mb-2">Risk Management</h3>
                            <p className="text-[var(--text-secondary)]">Configure your risk parameters</p>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <Input
                                type="number"
                                label="Initial Cash ($)"
                                value={cash}
                                onChange={(e) => setCash(Number(e.target.value))}
                                step="100"
                            />
                            <Input
                                type="number"
                                label="Trading Fee (%)"
                                value={fee}
                                onChange={(e) => setFee(Number(e.target.value))}
                                step="0.01"
                            />
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <Input
                                type="number"
                                label="Stop Loss (%) - Optional"
                                value={stopPct || ''}
                                onChange={(e) => setStopPct(e.target.value ? Number(e.target.value) : null)}
                                placeholder="e.g. 2"
                                step="0.5"
                            />
                            <Input
                                type="number"
                                label="Take Profit (%) - Optional"
                                value={takePct || ''}
                                onChange={(e) => setTakePct(e.target.value ? Number(e.target.value) : null)}
                                placeholder="e.g. 5"
                                step="0.5"
                            />
                        </div>

                        {/* Summary */}
                        <div className="mt-8 p-6 bg-[var(--bg-elevated)] rounded-xl border border-[var(--border-subtle)]">
                            <h4 className="text-sm font-bold text-[var(--text-secondary)] uppercase tracking-wide mb-4">Summary</h4>
                            <div className="space-y-2 text-sm">
                                <div className="flex justify-between">
                                    <span className="text-[var(--text-tertiary)]">Market:</span>
                                    <span className="text-white font-semibold">{symbol} - {timeframe}</span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-[var(--text-tertiary)]">Period:</span>
                                    <span className="text-white">{sinceDate} to {untilDate}</span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-[var(--text-tertiary)]">Strategies:</span>
                                    <span className="text-white font-semibold">{selectedStrategies.length} selected</span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-[var(--text-tertiary)]">Initial Capital:</span>
                                    <span className="text-white">${cash.toLocaleString()}</span>
                                </div>
                            </div>
                        </div>
                    </div>
                )}
            </Card>

            {/* Navigation */}
            <div className="flex justify-between items-center">
                <Button
                    variant="ghost"
                    onClick={() => setCurrentStep(Math.max(1, currentStep - 1))}
                    disabled={currentStep === 1}
                    icon={<ChevronLeft className="w-4 h-4" />}
                >
                    Back
                </Button>

                {currentStep < 3 ? (
                    <Button
                        variant="primary"
                        size="lg"
                        onClick={() => setCurrentStep(currentStep + 1)}
                        icon={<ChevronRight className="w-4 h-4" />}
                    >
                        Next Step
                    </Button>
                ) : (
                    <Button
                        variant="primary"
                        size="lg"
                        onClick={handleSubmit}
                        loading={runMutation.isPending}
                        icon={<PlayCircle className="w-5 h-5" />}
                    >
                        Run Backtest
                    </Button>
                )}
            </div>
        </div>
    )
}
