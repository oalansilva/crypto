// src/components/SimpleBacktestWizard.tsx
import { useState, useEffect } from 'react'
import { useMutation, useQueryClient, useQuery } from '@tanstack/react-query'
import { backtestApi, type BacktestRunCreate } from '../lib/api'
import { Button, Input, Card } from './ui'
import { RangeInput } from './RangeInput'
import {
    Activity,
    TrendingUp,
    Layers,
    Calendar,
    DollarSign,
    ChevronLeft,
    ChevronRight,
    Check,
    BarChart3,
    LineChart,
    Loader2
} from 'lucide-react'


interface SimpleBacktestWizardProps {
    onSuccess: () => void
}

interface IndicatorParam {
    name: string
    type: string
    default: any
    description?: string
}

interface IndicatorMetadata {
    name: string
    category: string
    params: IndicatorParam[]
}

const SYMBOLS = ['BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'SOL/USDT', 'ADA/USDT', 'LINK/USDT', 'XMR/USDT', 'ATOM/USDT', 'LTC/USDT', 'TRX/USDT']
const TIMEFRAMES = ['5m', '15m', '30m', '1h', '2h', '4h', '1d', '3d', '1w']

const PERIOD_PRESETS = [
    { label: 'Últimos 6 meses', months: 6 },
    { label: 'Últimos 12 meses', months: 12 },
    { label: 'Últimos 24 meses', months: 24 }
]

// Mapeamento de ícones por categoria
const CATEGORY_ICONS: Record<string, any> = {
    'overlap': TrendingUp,
    'momentum': Activity,
    'volatility': Layers,
    'volume': BarChart3,
    'trend': LineChart,
    'default': Activity
}

// Indicadores populares (IDs que devem aparecer em destaque)
const POPULAR_INDICATORS = ['sma', 'ema', 'rsi', 'macd', 'bbands', 'stoch']

// Valores padrão do mercado para indicadores comuns
const MARKET_DEFAULTS: Record<string, Record<string, any>> = {
    // Moving Averages
    'sma': { length: 20 },
    'ema': { length: 12 },
    'wma': { length: 20 },
    'vwma': { length: 20 },
    'hma': { length: 9 },

    // Momentum
    'rsi': { length: 14 },
    'macd': { fast: 12, slow: 26, signal: 9 },
    'stoch': { k: 14, d: 3, smooth_k: 3 },
    'stochf': { k: 14, d: 3 },
    'cci': { length: 20 },
    'roc': { length: 12 },
    'mom': { length: 10 },
    'willr': { length: 14 },

    // Volatility
    'bbands': { length: 20, std: 2.0 },
    'atr': { length: 14 },
    'natr': { length: 14 },
    'kc': { length: 20, scalar: 2.0 },

    // Volume
    'obv': {},
    'ad': {},
    'adosc': { fast: 3, slow: 10 },
    'cmf': { length: 20 },
    'mfi': { length: 14 },

    // Trend
    'adx': { length: 14 },
    'aroon': { length: 25 },
    'psar': { af0: 0.02, af: 0.02, max_af: 0.2 },
    'supertrend': { length: 7, multiplier: 3.0 }
}

// Parâmetros essenciais para cada indicador (ocultar os opcionais)
const ESSENTIAL_PARAMS: Record<string, string[]> = {
    'rsi': ['length'],
    'sma': ['length'],
    'ema': ['length'],
    'wma': ['length'],
    'vwma': ['length'],
    'hma': ['length'],
    'macd': ['fast', 'slow', 'signal'],
    'stoch': ['k', 'd', 'smooth_k'],
    'stochf': ['k', 'd'],
    'bbands': ['length', 'std'],
    'atr': ['length'],
    'natr': ['length'],
    'adx': ['length'],
    'cci': ['length'],
    'roc': ['length'],
    'mom': ['length'],
    'willr': ['length'],
    'mfi': ['length'],
    'cmf': ['length'],
    'obv': [],
    'ad': [],
    'adosc': ['fast', 'slow'],
    'aroon': ['length'],
    'kc': ['length', 'scalar'],
    'psar': ['af0', 'af', 'max_af'],
    'supertrend': ['length', 'multiplier']
}

export function SimpleBacktestWizard({ onSuccess }: SimpleBacktestWizardProps) {
    const queryClient = useQueryClient()
    const [currentStep, setCurrentStep] = useState(1)
    const [searchQuery, setSearchQuery] = useState('')

    // Fetch indicators from API
    const { data: indicatorsData, isLoading: loadingIndicators } = useQuery({
        queryKey: ['indicators-metadata'],
        queryFn: async () => {
            const response = await fetch('http://127.0.0.1:8000/api/strategies/metadata')
            const data = await response.json()
            // Flatten grouped data
            const flattened: IndicatorMetadata[] = []
            Object.entries(data).forEach(([category, indicators]: [string, any]) => {
                // indicators is an array, not an object
                if (Array.isArray(indicators)) {
                    indicators.forEach((indicator: any) => {
                        flattened.push({
                            name: indicator.id || indicator.name,
                            category,
                            params: indicator.params || []
                        })
                    })
                }
            })
            return flattened
        }
    })

    // Execution Mode (always optimize - system auto-detects single vs multi)
    const mode = 'optimize'

    // Step 1: Market Setup
    const [symbol, setSymbol] = useState('BTC/USDT')
    const [selectedTimeframes, setSelectedTimeframes] = useState<string[]>(['1d'])
    const [periodPreset, setPeriodPreset] = useState(24)
    const [sinceDate, setSinceDate] = useState(() => {
        const date = new Date()
        date.setMonth(date.getMonth() - 24)
        return date.toISOString().split('T')[0]
    })
    const [untilDate, setUntilDate] = useState(() => new Date().toISOString().split('T')[0])

    // Step 2: Indicator Selection
    const [selectedIndicators, setSelectedIndicators] = useState<string[]>([])
    const [activeParamTab, setActiveParamTab] = useState<string>('')
    const [strategiesParams, setStrategiesParams] = useState<Record<string, Record<string, any>>>({})

    // Step 3: Risk Management
    const [cash, setCash] = useState(10000)
    const [fee, setFee] = useState(0.1)

    // Stop/Take params can be number or Range object
    const [stopPct, setStopPct] = useState<any>(null)
    const [takePct, setTakePct] = useState<any>(null)




    const runMutation = useMutation({
        mutationFn: async (config: BacktestRunCreate) => {
            const response = await backtestApi.createRun(config)
            return response.data
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['runs'] })
            onSuccess()
        },
    })

    // Auto-convert params to range objects when switching to optimize mode
    useEffect(() => {
        if (mode === 'optimize' && selectedIndicators.length > 0) {
            setStrategiesParams(prev => {
                const updated = { ...prev }

                selectedIndicators.forEach(indName => {
                    const indicator = indicatorsData?.find(i => i.name === indName)
                    if (!indicator) return

                    const currentParams = prev[indName] || {}
                    const newParams: Record<string, any> = {}

                    indicator.params.forEach((param: IndicatorParam) => {
                        const currentVal = currentParams[param.name]

                        // Skip null/undefined params - don't include them at all
                        if (currentVal === null || currentVal === undefined || currentVal === '') {
                            return
                        }

                        // If already a range object, keep it
                        if (typeof currentVal === 'object' && currentVal !== null && 'min' in currentVal) {
                            newParams[param.name] = currentVal
                        } else {
                            // Convert scalar to range
                            newParams[param.name] = {
                                min: currentVal,
                                max: currentVal + 10,
                                step: param.type === 'float' ? 0.1 : 1
                            }
                        }
                    })

                    updated[indName] = newParams
                })

                return updated
            })
        }
    }, [mode, selectedIndicators, indicatorsData])

    const handlePeriodPresetChange = (months: number) => {
        setPeriodPreset(months)
        const date = new Date()
        date.setMonth(date.getMonth() - months)
        setSinceDate(date.toISOString().split('T')[0])
        setUntilDate(new Date().toISOString().split('T')[0])
    }

    const toggleTimeframe = (tf: string) => {
        setSelectedTimeframes(prev => {
            if (prev.includes(tf)) {
                if (prev.length === 1) return prev // Keep at least one
                return prev.filter(t => t !== tf)
            }
            return [...prev, tf]
        })
    }

    const toggleIndicator = (name: string) => {
        const indicatorMeta = indicatorsData?.find(i => i.name === name)

        setSelectedIndicators(prev => {
            const isSelected = prev.includes(name)

            if (isSelected) {
                // Should we allow empty? No, at least one strategy.
                if (prev.length === 1) return prev
                return prev.filter(n => n !== name)
            }

            // Initialize params if new selection
            if (indicatorMeta && !strategiesParams[name]) {
                const defaults: Record<string, any> = {}
                const marketDefaults = MARKET_DEFAULTS[name.toLowerCase()]

                indicatorMeta.params.forEach((p: IndicatorParam) => {
                    if (marketDefaults && marketDefaults[p.name] !== undefined) {
                        defaults[p.name] = marketDefaults[p.name]
                    } else {
                        defaults[p.name] = p.default
                    }
                })

                setStrategiesParams(curr => ({
                    ...curr,
                    [name]: defaults
                }))
            }

            // Auto-switch tab to the newly selected indicator
            if (!isSelected) {
                setActiveParamTab(name)
            }

            return [...prev, name]
        })
    }

    const handleParamChange = (indicator: string, param: string, value: any) => {
        setStrategiesParams(prev => ({
            ...prev,
            [indicator]: {
                ...prev[indicator],
                [param]: value
            }
        }))
    }
    const handleSubmit = () => {
        if (selectedIndicators.length === 0) return

        let finalStopPct = null;
        let finalTakePct = null;

        // DEBUG: Log raw values
        console.log('=== STOP/TAKE DEBUG ===');
        console.log('mode:', mode);
        console.log('stopPct (raw):', stopPct, 'type:', typeof stopPct);
        console.log('takePct (raw):', takePct, 'type:', typeof takePct);

        // Convert percentages to decimals
        if (mode === 'optimize') {
            // It's a range object { min: 1, max: 5, step: 0.5 }
            if (stopPct && typeof stopPct === 'object') {
                finalStopPct = {
                    min: (stopPct.min || 0) / 100,
                    max: (stopPct.max || 0) / 100,
                    step: (stopPct.step || 0) / 100
                }
            }
            if (takePct && typeof takePct === 'object') {
                finalTakePct = {
                    min: (takePct.min || 0) / 100,
                    max: (takePct.max || 0) / 100,
                    step: (takePct.step || 0) / 100
                }
            }
        } else {
            // Standard mode
            if (stopPct !== '' && typeof stopPct === 'number') finalStopPct = stopPct / 100
            if (takePct !== '' && typeof takePct === 'number') finalTakePct = takePct / 100
        }

        console.log('finalStopPct:', finalStopPct);
        console.log('finalTakePct:', finalTakePct);

        const config: BacktestRunCreate = {
            mode: mode,
            exchange: 'binance',
            symbol,
            // NEW: Send as array if multiple timeframes, otherwise as string
            timeframe: selectedTimeframes.length === 1
                ? selectedTimeframes[0]
                : selectedTimeframes,
            timeframes: selectedTimeframes,  // Deprecated, kept for backward compatibility
            since: `${sinceDate} 00:00:00`,
            until: (untilDate ? `${untilDate} 23:59:59` : null),
            strategies: selectedIndicators.map(name => ({
                name,
                ...(strategiesParams[name] || {})
            })),
            // Clean params: remove null/undefined values
            params: Object.fromEntries(
                Object.entries(strategiesParams).map(([key, val]) => [
                    key,
                    Object.fromEntries(
                        Object.entries(val || {}).filter(([_, v]) => v !== null && v !== undefined && v !== '')
                    )
                ])
            ),
            cash,
            fee: fee / 100,
            stop_pct: finalStopPct,
            take_pct: finalTakePct
        }

        if (mode === 'optimize') {
            backtestApi.createOptimize(config).then(() => {
                queryClient.invalidateQueries({ queryKey: ['runs'] })
                onSuccess()
            })
        } else {
            runMutation.mutate(config)
        }
    }


    // Filter indicators based on search
    const filteredIndicators = indicatorsData?.filter(ind =>
        ind.name.toLowerCase().includes(searchQuery.toLowerCase())
    ) || []

    // Separate popular and other indicators
    const popularIndicators = filteredIndicators.filter(ind => POPULAR_INDICATORS.includes(ind.name))
    const otherIndicators = filteredIndicators.filter(ind => !POPULAR_INDICATORS.includes(ind.name))

    const steps = [
        { number: 1, title: 'Mercado', icon: Calendar },
        { number: 2, title: 'Indicador', icon: TrendingUp },
        { number: 3, title: 'Risco', icon: DollarSign },
    ]

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
                                        ? 'bg-gradient-to-br from-[var(--accent-primary)] to-[var(--accent-secondary)] shadow-[var(--shadow-glow-green)]'
                                        : isActive
                                            ? 'bg-gradient-to-br from-[var(--accent-primary)] to-[var(--accent-secondary)] shadow-[var(--shadow-glow-green)] scale-110'
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
                            <h3 className="text-2xl font-bold text-white mb-2">Configuração do Mercado</h3>
                            <p className="text-[var(--text-secondary)]">Selecione o ativo e período para análise</p>
                        </div>


                        {/* Grid configuration */}

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <div>
                                <label className="block text-xs text-[var(--text-secondary)] mb-2 uppercase font-semibold">Símbolo</label>
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

                            <div className="md:col-span-1">
                                <label className="block text-xs text-[var(--text-secondary)] mb-2 uppercase font-semibold">Timeframes (Selecione Múltiplos)</label>
                                <div className="grid grid-cols-4 gap-2 pt-1">
                                    {TIMEFRAMES.map(tf => {
                                        const isSelected = selectedTimeframes.includes(tf)
                                        return (
                                            <button
                                                key={tf}
                                                type="button"
                                                onClick={() => toggleTimeframe(tf)}
                                                style={{
                                                    backgroundColor: isSelected ? '#2563eb' : 'rgba(30, 41, 59, 0.5)', // Blue-600 vs Slate-800/50
                                                    borderColor: isSelected ? '#1d4ed8' : 'rgba(71, 85, 105, 0.5)'  // Blue-700 vs Slate-600/50
                                                }}
                                                className={`
                                                    relative group flex items-center justify-center gap-2 px-3 py-2.5 rounded-xl border transition-all duration-300
                                                    ${isSelected
                                                        ? 'shadow-lg shadow-blue-500/40 ring-2 ring-blue-500/30 translate-y-[-2px]'
                                                        : 'hover:border-gray-500 hover:bg-gray-800 hover:translate-y-[-1px]'
                                                    }
                                                `}
                                            >
                                                {isSelected && (
                                                    <div className="absolute inset-0 bg-[var(--accent-primary)]/5 rounded-xl animate-pulse" />
                                                )}
                                                {/* Check icon with scale animation */}
                                                <div className={`
                                                    flex items-center justify-center w-4 h-4 rounded-full transition-all duration-300
                                                    ${isSelected ? 'bg-white text-blue-600 scale-100' : 'bg-transparent scale-0 w-0'}
                                                `}>
                                                    <Check className="w-2.5 h-2.5" strokeWidth={4} />
                                                </div>

                                                <span className={`
                                                    font-bold text-sm transition-colors duration-300
                                                    ${isSelected ? 'text-white' : 'text-[var(--text-secondary)] group-hover:text-[var(--text-primary)]'}
                                                `}>
                                                    {tf}
                                                </span>
                                            </button>
                                        )
                                    })}
                                </div>
                            </div>
                        </div>

                        <div>
                            <label className="block text-xs text-[var(--text-secondary)] mb-2 uppercase font-semibold">Período</label>
                            <div className="grid grid-cols-3 gap-3 mb-4">
                                {PERIOD_PRESETS.map(preset => (
                                    <button
                                        key={preset.months}
                                        type="button"
                                        onClick={() => handlePeriodPresetChange(preset.months)}
                                        className={`px-4 py-3 rounded-xl border text-sm font-semibold transition-all ${periodPreset === preset.months
                                            ? 'bg-[var(--accent-primary)]/10 border-[var(--accent-primary)] text-[var(--accent-primary)]'
                                            : 'bg-[var(--bg-elevated)] border-[var(--border-subtle)] text-[var(--text-secondary)] hover:border-[var(--border-default)]'
                                            }`}
                                    >
                                        {preset.label}
                                    </button>
                                ))}
                            </div>
                        </div>


                    </div>
                )}

                {/* Step 2: Indicator Selection */}
                {currentStep === 2 && (
                    <div className="space-y-6">
                        <div>
                            <h3 className="text-2xl font-bold text-white mb-2">Escolha o Indicador</h3>
                            <p className="text-[var(--text-secondary)]">Selecione um indicador para testar</p>
                        </div>

                        {/* Search */}
                        <Input
                            type="text"
                            placeholder="Buscar indicador..."
                            value={searchQuery}
                            onChange={(e) => setSearchQuery(e.target.value)}
                        />

                        {loadingIndicators ? (
                            <div className="flex items-center justify-center py-12">
                                <Loader2 className="w-8 h-8 animate-spin text-[var(--accent-primary)]" />
                            </div>
                        ) : (
                            <>
                                {/* Popular Indicators */}
                                {popularIndicators.length > 0 && (
                                    <div>
                                        <h4 className="text-sm font-bold text-[var(--text-secondary)] uppercase tracking-wide mb-3">
                                            Populares
                                        </h4>
                                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                            {popularIndicators.map((indicator) => {
                                                const isSelected = selectedIndicators.includes(indicator.name)
                                                const Icon = CATEGORY_ICONS[indicator.category] || CATEGORY_ICONS.default

                                                return (
                                                    <button
                                                        key={`${indicator.category}-${indicator.name}`}
                                                        type="button"
                                                        onClick={() => toggleIndicator(indicator.name)}
                                                        className={`p-6 rounded-xl border text-left transition-all ${isSelected
                                                            ? 'bg-[var(--accent-primary)]/10 border-[var(--accent-primary)] shadow-[var(--shadow-glow-green)]'
                                                            : 'bg-[var(--bg-elevated)] border-[var(--border-subtle)] hover:border-[var(--border-default)]'
                                                            }`}
                                                    >
                                                        <div className={`w-12 h-12 rounded-xl flex items-center justify-center mb-4 ${isSelected
                                                            ? 'bg-[var(--accent-primary)] text-white'
                                                            : 'bg-white/5 text-[var(--text-tertiary)]'}`}>
                                                            <Icon className="w-6 h-6" />
                                                        </div>
                                                        <h4 className={`font-bold mb-2 ${isSelected ? 'text-white' : 'text-[var(--text-secondary)]'}`}>
                                                            {indicator.name.toUpperCase()}
                                                        </h4>
                                                        <p className="text-sm text-[var(--text-tertiary)]">
                                                            {indicator.category}
                                                        </p>
                                                    </button>
                                                )
                                            })}
                                        </div>
                                    </div>
                                )}

                                {/* Other Indicators */}
                                {otherIndicators.length > 0 && (
                                    <div>
                                        <h4 className="text-sm font-bold text-[var(--text-secondary)] uppercase tracking-wide mb-3">
                                            Outros
                                        </h4>
                                        <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                                            {otherIndicators.map((indicator) => {
                                                const isSelected = selectedIndicators.includes(indicator.name)

                                                return (
                                                    <button
                                                        key={`${indicator.category}-${indicator.name}`}
                                                        type="button"
                                                        onClick={() => toggleIndicator(indicator.name)}
                                                        className={`px-4 py-3 rounded-lg border text-sm font-semibold transition-all ${isSelected
                                                            ? 'bg-[var(--accent-primary)]/10 border-[var(--accent-primary)] text-[var(--accent-primary)]'
                                                            : 'bg-[var(--bg-elevated)] border-[var(--border-subtle)] text-[var(--text-secondary)] hover:border-[var(--border-default)]'
                                                            }`}
                                                    >
                                                        {indicator.name.toUpperCase()}
                                                    </button>
                                                )
                                            })}
                                        </div>
                                    </div>
                                )}
                            </>
                        )}

                        {/* Params Section with Tabs */}
                        {selectedIndicators.length > 0 && (
                            <div className="mt-8 p-6 bg-[var(--bg-elevated)] rounded-xl border border-[var(--border-subtle)]">
                                <div className="flex space-x-2 mb-6 overflow-x-auto pb-2 scrollbar-hide">
                                    {selectedIndicators.map(indName => (
                                        <button
                                            key={indName}
                                            type="button"
                                            onClick={() => setActiveParamTab(indName)}
                                            className={`px-4 py-2 rounded-lg text-xs font-bold uppercase tracking-wider whitespace-nowrap transition-all ${(activeParamTab === indName || (!activeParamTab && indName === selectedIndicators[0]))
                                                ? 'bg-[var(--accent-primary)] text-white shadow-lg shadow-[var(--accent-primary)]/25'
                                                : 'bg-[var(--bg-base)] text-[var(--text-tertiary)] border border-[var(--border-subtle)] hover:border-[var(--border-default)]'
                                                }`}
                                        >
                                            {indName}
                                        </button>
                                    ))}
                                </div>

                                {(() => {
                                    // Determine active tab safely
                                    const targetIndName = (activeParamTab && selectedIndicators.includes(activeParamTab))
                                        ? activeParamTab
                                        : selectedIndicators[0];

                                    const indicator = indicatorsData?.find(i => i.name === targetIndName);
                                    if (!indicator) return null;

                                    return (
                                        <div className="animate-fade-in">
                                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                                {indicator.params
                                                    .filter((param: IndicatorParam) => {
                                                        const essentialList = ESSENTIAL_PARAMS[targetIndName.toLowerCase()]
                                                        return !essentialList || essentialList.includes(param.name)
                                                    })
                                                    .map((param: IndicatorParam) => {
                                                        const currentValue = strategiesParams[targetIndName]?.[param.name]

                                                        // Optimization Mode Render
                                                        if (mode === 'optimize') {
                                                            // Ensure value is an object or initialize it
                                                            const rangeVal = typeof currentValue === 'object' ? currentValue : {
                                                                min: currentValue || param.default,
                                                                max: (currentValue || param.default) + 10, // heuristic default
                                                                step: param.type === 'float' ? 0.1 : 1
                                                            }

                                                            return (
                                                                <RangeInput
                                                                    key={param.name}
                                                                    label={param.name}
                                                                    min={rangeVal.min}
                                                                    max={rangeVal.max}
                                                                    step={rangeVal.step}
                                                                    onMinChange={(v) => {
                                                                        const parsed = v === '' ? rangeVal.min : parseFloat(v);
                                                                        if (!isNaN(parsed)) {
                                                                            handleParamChange(targetIndName, param.name, { ...rangeVal, min: parsed })
                                                                        }
                                                                    }}
                                                                    onMaxChange={(v) => {
                                                                        const parsed = v === '' ? rangeVal.max : parseFloat(v);
                                                                        if (!isNaN(parsed)) {
                                                                            handleParamChange(targetIndName, param.name, { ...rangeVal, max: parsed })
                                                                        }
                                                                    }}
                                                                    onStepChange={(v) => {
                                                                        const parsed = v === '' ? rangeVal.step : parseFloat(v);
                                                                        if (!isNaN(parsed)) {
                                                                            handleParamChange(targetIndName, param.name, { ...rangeVal, step: parsed })
                                                                        }
                                                                    }}
                                                                />
                                                            )
                                                        }

                                                        // Standard Mode Render
                                                        return (
                                                            <Input
                                                                key={param.name}
                                                                type="number"
                                                                label={param.name}
                                                                value={currentValue ?? ''}
                                                                onChange={(e) => handleParamChange(
                                                                    targetIndName,
                                                                    param.name,
                                                                    e.target.value ? Number(e.target.value) : ''
                                                                )}
                                                                step={param.type === 'float' ? 0.1 : 1}
                                                            />
                                                        )
                                                    })}
                                            </div>
                                        </div>
                                    )
                                })()}
                            </div>
                        )}
                    </div>
                )}

                {/* Step 3: Risk Management */}
                {currentStep === 3 && (
                    <div className="space-y-6">
                        <div>
                            <h3 className="text-2xl font-bold text-white mb-2">Gestão de Risco</h3>
                            <p className="text-[var(--text-secondary)]">Configure os parâmetros de risco</p>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <Input
                                type="number"
                                label="Capital Inicial ($)"
                                value={cash}
                                onChange={(e) => setCash(Number(e.target.value))}
                                step="100"
                            />
                            <Input
                                type="number"
                                label="Taxa de Trading (%)"
                                value={fee}
                                onChange={(e) => setFee(Number(e.target.value))}
                                step="0.01"
                            />
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            {mode === 'optimize' ? (
                                <>
                                    <RangeInput
                                        label="Stop Loss (%) - Opcional"
                                        min={stopPct?.min ?? ''}
                                        max={stopPct?.max ?? ''}
                                        step={stopPct?.step ?? ''}
                                        onMinChange={(v) => {
                                            if (v === '') return; // Don't update if empty
                                            const parsed = parseFloat(v);
                                            if (!isNaN(parsed)) {
                                                setStopPct((prev: any) => ({ ...(prev || {}), min: parsed }))
                                            }
                                        }}
                                        onMaxChange={(v) => {
                                            if (v === '') return; // Don't update if empty
                                            const parsed = parseFloat(v);
                                            if (!isNaN(parsed)) {
                                                setStopPct((prev: any) => ({ ...(prev || {}), max: parsed }))
                                            }
                                        }}
                                        onStepChange={(v) => {
                                            if (v === '') return; // Don't update if empty
                                            const parsed = parseFloat(v);
                                            if (!isNaN(parsed)) {
                                                setStopPct((prev: any) => ({ ...(prev || {}), step: parsed }))
                                            }
                                        }}
                                    />
                                    <RangeInput
                                        label="Take Profit (%) - Opcional"
                                        min={takePct?.min ?? ''}
                                        max={takePct?.max ?? ''}
                                        step={takePct?.step ?? ''}
                                        onMinChange={(v) => {
                                            if (v === '') return; // Don't update if empty
                                            const parsed = parseFloat(v);
                                            if (!isNaN(parsed)) {
                                                setTakePct((prev: any) => ({ ...(prev || {}), min: parsed }))
                                            }
                                        }}
                                        onMaxChange={(v) => {
                                            if (v === '') return; // Don't update if empty
                                            const parsed = parseFloat(v);
                                            if (!isNaN(parsed)) {
                                                setTakePct((prev: any) => ({ ...(prev || {}), max: parsed }))
                                            }
                                        }}
                                        onStepChange={(v) => {
                                            if (v === '') return; // Don't update if empty
                                            const parsed = parseFloat(v);
                                            if (!isNaN(parsed)) {
                                                setTakePct((prev: any) => ({ ...(prev || {}), step: parsed }))
                                            }
                                        }}
                                    />
                                </>
                            ) : (
                                <>
                                    <Input
                                        type="number"
                                        label="Stop Loss (%) - Opcional"
                                        value={stopPct}
                                        onChange={(e) => setStopPct(e.target.value ? Number(e.target.value) : '')}
                                        placeholder="ex: 2"
                                        step="0.5"
                                    />
                                    <Input
                                        type="number"
                                        label="Take Profit (%) - Opcional"
                                        value={takePct}
                                        onChange={(e) => setTakePct(e.target.value ? Number(e.target.value) : '')}
                                        placeholder="ex: 5"
                                        step="0.5"
                                    />
                                </>
                            )}
                        </div>

                        {/* Summary */}
                        <div className="mt-8 p-6 bg-[var(--bg-elevated)] rounded-xl border border-[var(--border-subtle)]">
                            <h4 className="text-sm font-bold text-[var(--text-secondary)] uppercase tracking-wide mb-4">Resumo</h4>
                            <div className="space-y-2 text-sm">
                                <div className="flex justify-between">
                                    <span className="text-[var(--text-tertiary)]">Mercado:</span>
                                    <span className="text-white font-semibold">{symbol}</span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-[var(--text-tertiary)]">Timeframes:</span>
                                    <span className="text-white text-right max-w-[200px]">{selectedTimeframes.join(', ')}</span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-[var(--text-tertiary)]">Período:</span>
                                    <span className="text-white text-right">{sinceDate} até {untilDate}</span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-[var(--text-tertiary)]">Indicadores:</span>
                                    <span className="text-white font-semibold text-right max-w-[200px] truncate">
                                        {selectedIndicators.map(i => i.toUpperCase()).join(', ')}
                                    </span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-[var(--text-tertiary)]">Capital:</span>
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
                    Voltar
                </Button>

                {currentStep < 3 ? (
                    <Button
                        variant="primary"
                        size="lg"
                        onClick={() => setCurrentStep(currentStep + 1)}
                        icon={<ChevronRight className="w-4 h-4" />}
                    >
                        Próximo
                    </Button>
                ) : (
                    <Button
                        variant="primary"
                        size="lg"
                        onClick={handleSubmit}
                        loading={runMutation.isPending}
                        icon={<Activity className="w-5 h-5" />}
                    >
                        Executar Otimização
                    </Button>
                )}
            </div>
        </div>
    )
}
