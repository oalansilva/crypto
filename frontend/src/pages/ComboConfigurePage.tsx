import { useState, useEffect, useRef } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { Settings, TrendingUp, Calendar, DollarSign, Sliders, HelpCircle, ExternalLink, ChevronRight, ChevronLeft, ChevronsRight, ChevronsLeft, Search, Pause, Square } from 'lucide-react'

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
    const [timeframe, setTimeframe] = useState('1d')
    const [deepBacktest, setDeepBacktest] = useState(true)
    const [direction, setDirection] = useState<'long' | 'short'>('long')
    const [logs, setLogs] = useState<string[]>([])

    // Período: últimos 6 meses / 2 anos / todo o histórico
    type PeriodKey = '6m' | '2y' | 'all'
    const [period, setPeriod] = useState<PeriodKey>('all')

    // Escopo: Todos (seleciona todos, desabilita caixa) ou Seleciona (usuário escolhe).
    type BatchScope = 'all' | 'selected'
    const [batchScope, setBatchScope] = useState<BatchScope>('selected')
    const [selectedSymbols, setSelectedSymbols] = useState<string[]>(['BTC/USDT'])
    const [leftHighlighted, setLeftHighlighted] = useState<string[]>([])
    const [rightHighlighted, setRightHighlighted] = useState<string[]>([])
    const [leftFilter, setLeftFilter] = useState('')

    // Batch backtest
    const [batchRunning, setBatchRunning] = useState(false)
    const [batchJobId, setBatchJobId] = useState<string | null>(null)
    const [batchPauseCancelRequested, setBatchPauseCancelRequested] = useState(false)
    const [batchProgress, setBatchProgress] = useState<{
        status: string
        processed: number
        total: number
        succeeded: number
        failed: number
        skipped?: number
        errors: Array<{ symbol: string; error: string }>
        started_at: string | null
        elapsed_sec: number
        estimated_remaining_sec: number | null
        current_symbol?: string | null
    } | null>(null)
    const [batchTotal, setBatchTotal] = useState(0)
    const pollRef = useRef<ReturnType<typeof setInterval> | null>(null)
    const batchStartTimeRef = useRef<number | null>(null)
    const [clientElapsedSec, setClientElapsedSec] = useState(0)

    // Fetch available symbols from Binance
    const { data: symbolsData } = useQuery({
        queryKey: ['binance-symbols'],
        queryFn: async () => {
            const response = await fetch('http://localhost:8000/api/exchanges/binance/symbols');
            if (!response.ok) {
                throw new Error('Failed to fetch symbols');
            }
            const data = await response.json();
            return data.symbols as string[];
        },
        staleTime: 1000 * 60 * 60 * 24, // Cache for 24 hours
    });

    useEffect(() => {
        if (templateName) {
            fetchMetadata()
        }
    }, [templateName])

    useEffect(() => {
        if (batchScope === 'all' && (symbolsData ?? []).length > 0) {
            setSelectedSymbols([...(symbolsData ?? [])])
        }
    }, [batchScope, symbolsData])

    const fetchMetadata = async () => {
        try {
            const response = await fetch(`http://localhost:8000/api/combos/meta/${templateName}`)
            const data = await response.json()
            setMetadata(data)

            // Extract params for optimization from optimization_schema (if available) or indicators
            const optParams: any[] = []

            // Check if template has optimization_schema in database
            // Check if template has optimization_schema in database
            if (data.optimization_schema && Object.keys(data.optimization_schema).length > 0) {
                // Use optimization schema from database
                // Handle both Flat (legacy) and Nested (new) schema structures
                let schemaSource = data.optimization_schema;
                if (data.optimization_schema.parameters) {
                    schemaSource = data.optimization_schema.parameters;
                }

                Object.entries(schemaSource).forEach(([paramName, config]: [string, any]) => {
                    // Skip non-parameter keys if any (like correlated_groups if mixed in flat schema)
                    if (paramName === 'correlated_groups' || paramName === 'parameters') return;

                    // Determine group from parameter name (e.g., "sma_short" -> "short")
                    const parts = paramName.split('_')
                    const group = parts.length > 1 ? parts[parts.length - 1] : paramName

                    // Ensure config has min/max (it might be a raw value in some weird legacy cases, but assuming dict)
                    // If config is null/undefined or not an object, skip
                    if (!config || typeof config !== 'object') return;

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

    const getBatchSymbols = (): string[] => {
        if (batchScope === 'all') return symbolsData ?? []
        return selectedSymbols
    }

    /** Últimos 6 meses, últimos 2 anos ou todo o histórico. */
    function getPeriodDates(): { start_date: string | null; end_date: string | null } {
        if (period === 'all') return { start_date: null, end_date: null }
        const end = new Date()
        const start = new Date()
        if (period === '6m') {
            start.setMonth(start.getMonth() - 6)
        } else {
            start.setFullYear(start.getFullYear() - 2)
        }
        return {
            start_date: start.toISOString().slice(0, 10),
            end_date: end.toISOString().slice(0, 10)
        }
    }

    function formatElapsed(sec: number): string {
        const m = Math.floor(sec / 60)
        const s = Math.floor(sec % 60)
        return `${m}m ${s}s`
    }

    const handlePauseBatch = async () => {
        if (!batchJobId || batchPauseCancelRequested) return
        setBatchPauseCancelRequested(true)
        try {
            const res = await fetch(`http://localhost:8000/api/combos/backtest/batch/${batchJobId}/pause`, { method: 'POST' })
            if (!res.ok) setBatchPauseCancelRequested(false)
        } catch {
            setBatchPauseCancelRequested(false)
        }
    }

    const handleCancelBatch = async () => {
        if (!batchJobId || batchPauseCancelRequested) return
        setBatchPauseCancelRequested(true)
        try {
            const res = await fetch(`http://localhost:8000/api/combos/backtest/batch/${batchJobId}/cancel`, { method: 'POST' })
            if (!res.ok) setBatchPauseCancelRequested(false)
        } catch {
            setBatchPauseCancelRequested(false)
        }
    }

    const handleRun = async () => {
        const symbolsToRun = getBatchSymbols()
        if (batchScope === 'selected' && symbolsToRun.length === 0) {
            alert('Selecione ao menos um símbolo na lista acima.')
            return
        }
        if (symbolsToRun.length === 0) {
            alert('Nenhum símbolo disponível.')
            return
        }

        const custom_ranges: Record<string, { min: number; max: number; step: number }> = {}
        params.forEach(p => {
            custom_ranges[p.name] = { min: p.min, max: p.max, step: p.step ?? 1 }
        })
        const { start_date, end_date } = getPeriodDates()

        if (symbolsToRun.length === 1) {
            setRunning(true)
            try {
                const existsUrl = new URL('http://localhost:8000/api/favorites/exists')
                existsUrl.searchParams.set('strategy_name', templateName)
                existsUrl.searchParams.set('symbol', symbolsToRun[0])
                existsUrl.searchParams.set('timeframe', timeframe)
                existsUrl.searchParams.set('period_type', period)
                existsUrl.searchParams.set('direction', direction)
                const existsRes = await fetch(existsUrl.toString())
                if (existsRes.ok) {
                    const { exists } = await existsRes.json()
                    if (exists) {
                        alert('Estratégia já existe nos favoritos (mesmo template, ativo, timeframe, período e direção). Redirecionando.')
                        navigate('/favorites')
                        return
                    }
                }
                const res = await fetch('http://localhost:8000/api/combos/optimize', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        template_name: templateName,
                        symbol: symbolsToRun[0],
                        timeframe,
                        start_date,
                        end_date,
                        deep_backtest: deepBacktest,
                        direction,
                        custom_ranges
                    })
                })
                if (!res.ok) {
                    alert('Falha na otimização')
                    return
                }
                const result = await res.json()
                const name = `${result.template_name} - ${result.symbol} ${result.timeframe} (${new Date().toLocaleTimeString()})`
                const baseParams = result.best_parameters ?? result.parameters ?? {}
                const parameters = { ...baseParams, direction }
                const favRes = await fetch('http://localhost:8000/api/favorites/', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        name,
                        symbol: result.symbol,
                        timeframe: result.timeframe,
                        strategy_name: result.template_name,
                        parameters,
                        metrics: result.best_metrics ?? {},
                        start_date: start_date ?? null,
                        end_date: end_date ?? null,
                        period_type: period
                    })
                })
                if (!favRes.ok) {
                    const err = await favRes.json().catch(() => ({}))
                    throw new Error(err.detail ?? 'Falha ao salvar nos favoritos')
                }
                navigate('/favorites')
            } catch (e) {
                console.error('Optimization error:', e)
                alert(e instanceof Error ? e.message : 'Falha na otimização')
            } finally {
                setRunning(false)
            }
            return
        }

        setBatchRunning(true)
        setBatchJobId(null)
        setBatchProgress(null)
        setBatchTotal(symbolsToRun.length)
        setBatchPauseCancelRequested(false)
        setClientElapsedSec(0)
        batchStartTimeRef.current = Date.now()
        try {
            const res = await fetch('http://localhost:8000/api/combos/backtest/batch', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    template_name: templateName,
                    symbols: symbolsToRun,
                    timeframe,
                    start_date,
                    end_date,
                    period_type: period,
                    deep_backtest: deepBacktest,
                    direction,
                    custom_ranges
                })
            })
            if (!res.ok) {
                const err = await res.json().catch(() => ({}))
                throw new Error(err.detail ?? 'Falha ao iniciar batch')
            }
            const data = await res.json()
            setBatchJobId(data.job_id)
        } catch (e) {
            console.error('Batch start error:', e)
            alert(e instanceof Error ? e.message : 'Falha ao iniciar batch')
            setBatchRunning(false)
        }
    }

    useEffect(() => {
        if (!batchJobId) return
        const poll = async () => {
            try {
                const res = await fetch(`http://localhost:8000/api/combos/backtest/batch/${batchJobId}`)
                if (!res.ok) return
                const data = await res.json()
                setBatchProgress(data)
                if (['completed', 'failed', 'paused', 'cancelled'].includes(data.status)) {
                    if (pollRef.current) {
                        clearInterval(pollRef.current)
                        pollRef.current = null
                    }
                    setBatchRunning(false)
                    setBatchJobId(null)
                    setBatchPauseCancelRequested(false)
                    batchStartTimeRef.current = null
                }
            } catch {
                /* ignore */
            }
        }
        poll()
        pollRef.current = setInterval(poll, 2000)
        return () => {
            if (pollRef.current) clearInterval(pollRef.current)
        }
    }, [batchJobId])

    useEffect(() => {
        if (!batchRunning) return
        const t = setInterval(() => {
            const start = batchStartTimeRef.current
            if (start != null) setClientElapsedSec(Math.floor((Date.now() - start) / 1000))
        }, 1000)
        return () => clearInterval(t)
    }, [batchRunning])

    const selectTopSymbols = () => {
        const list = symbolsData ?? []
        const top = list.filter(s => /^(BTC|ETH|BNB|SOL|XRP|ADA|DOGE|AVAX|MATIC|LINK)\/USDT$/i.test(s))
        setSelectedSymbols(prev => {
            const next = new Set(prev)
            top.forEach(x => next.add(x))
            return [...next]
        })
        setLeftHighlighted([])
        setRightHighlighted([])
    }

    const availableSymbols = (symbolsData ?? []).filter(s => !selectedSymbols.includes(s))
    const leftFilterLower = leftFilter.trim().toLowerCase()
    const availableFiltered = leftFilterLower
        ? availableSymbols.filter(s => s.toLowerCase().includes(leftFilterLower))
        : availableSymbols
    const toggleLeft = (s: string) => {
        setLeftHighlighted(prev => prev.includes(s) ? prev.filter(x => x !== s) : [...prev, s])
    }
    const toggleRight = (s: string) => {
        setRightHighlighted(prev => prev.includes(s) ? prev.filter(x => x !== s) : [...prev, s])
    }
    const addSelected = () => {
        if (leftHighlighted.length === 0) return
        setSelectedSymbols(prev => [...prev, ...leftHighlighted])
        setLeftHighlighted([])
    }
    const removeSelected = () => {
        if (rightHighlighted.length === 0) return
        setSelectedSymbols(prev => {
            const next = prev.filter(s => !rightHighlighted.includes(s))
            return next.length ? next : ['BTC/USDT']
        })
        setRightHighlighted([])
    }
    const addAll = () => {
        if (availableFiltered.length === 0) return
        setSelectedSymbols(prev => [...prev, ...availableFiltered])
        setLeftHighlighted([])
    }
    const clearToBtc = () => {
        setSelectedSymbols(['BTC/USDT'])
        setLeftHighlighted([])
        setRightHighlighted([])
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
                            <div className="md:col-span-2">
                                <label className="block text-sm font-semibold text-gray-300 mb-2">Escopo</label>
                                <div className="flex flex-wrap gap-4 mb-4">
                                    <label className="flex items-center gap-2 cursor-pointer">
                                        <input
                                            type="radio"
                                            name="scope"
                                            checked={batchScope === 'all'}
                                            onChange={() => {
                                                setBatchScope('all')
                                                setSelectedSymbols([...(symbolsData ?? [])])
                                                setLeftHighlighted([])
                                                setRightHighlighted([])
                                                setLeftFilter('')
                                            }}
                                            className="rounded-full border-white/20"
                                        />
                                        <span className="text-sm text-white">Todos</span>
                                    </label>
                                    <label className="flex items-center gap-2 cursor-pointer">
                                        <input
                                            type="radio"
                                            name="scope"
                                            checked={batchScope === 'selected'}
                                            onChange={() => {
                                                setBatchScope('selected')
                                                setSelectedSymbols(prev => (prev.length ? prev : ['BTC/USDT']))
                                                setLeftHighlighted([])
                                                setRightHighlighted([])
                                                setLeftFilter('')
                                            }}
                                            className="rounded-full border-white/20"
                                        />
                                        <span className="text-sm text-white">Seleciona</span>
                                    </label>
                                </div>
                                <label className="block text-sm font-semibold text-gray-300 mb-2">
                                    <DollarSign className="w-4 h-4 inline mr-1" />
                                    Ativos
                                </label>
                                <p className="text-xs text-gray-400 mb-2">
                                    {batchScope === 'all'
                                        ? 'Todos selecionados. Otimizar 1: usa o primeiro; N: batch em todos.'
                                        : <>1 ativo: otimiza o <strong>primeiro</strong>. N ativos: <strong>batch</strong> nos selecionados.</>}
                                </p>
                                {batchScope === 'all' ? (
                                    <div className="py-6 rounded-lg bg-white/5 border border-white/10 text-center text-gray-400 text-sm">
                                        Modo Todos — todos os pares USDT serão usados. Altere para &quot;Seleciona&quot; para escolher ativos.
                                    </div>
                                ) : (
                                    <>
                                        <div className="flex gap-2 mb-2">
                                            <button
                                                type="button"
                                                onClick={selectTopSymbols}
                                                className="text-xs px-3 py-1.5 bg-purple-500/20 text-purple-300 rounded-lg hover:bg-purple-500/30 transition-colors"
                                            >
                                                Top 10
                                            </button>
                                            <button
                                                type="button"
                                                onClick={clearToBtc}
                                                className="text-xs px-3 py-1.5 bg-white/10 text-gray-300 rounded-lg hover:bg-white/20 transition-colors"
                                            >
                                                Limpar (só BTC)
                                            </button>
                                        </div>
                                        <div className="grid grid-cols-[1fr_auto_1fr] gap-3 items-stretch">
                                            <div className="flex flex-col min-h-0">
                                                <div className="text-xs text-gray-400 mb-1 font-medium">Selecione</div>
                                                <div className="relative mb-1.5">
                                                    <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
                                                    <input
                                                        type="text"
                                                        value={leftFilter}
                                                        onChange={(e) => setLeftFilter(e.target.value)}
                                                        placeholder="Filtrar ativo…"
                                                        className="w-full pl-8 pr-3 py-1.5 rounded-sm border border-white/10 bg-black/40 text-sm text-white placeholder-gray-500 focus:border-blue-500 focus:outline-none"
                                                    />
                                                </div>
                                                <div className="flex-1 min-h-[160px] max-h-48 overflow-y-auto rounded-sm border border-white/10 bg-black/40 p-1 space-y-0.5">
                                                    {availableFiltered.map(s => (
                                                        <div
                                                            key={s}
                                                            onClick={() => toggleLeft(s)}
                                                            onDoubleClick={() => { setSelectedSymbols(prev => [...prev, s]); setLeftHighlighted(prev => prev.filter(x => x !== s)) }}
                                                            className={`px-3 py-1.5 rounded-sm text-sm cursor-pointer truncate ${leftHighlighted.includes(s) ? 'bg-blue-500/30 text-white' : 'text-gray-300 hover:bg-white/10'}`}
                                                        >
                                                            {s}
                                                        </div>
                                                    ))}
                                                    {availableFiltered.length === 0 && (
                                                        <div className="text-gray-500 text-sm italic py-4 text-center">
                                                            {availableSymbols.length === 0 ? 'Nenhum disponível' : 'Nenhum resultado para o filtro'}
                                                        </div>
                                                    )}
                                                </div>
                                            </div>
                                            <div className="flex flex-col justify-center gap-1 py-6">
                                                <button
                                                    type="button"
                                                    onClick={addSelected}
                                                    disabled={leftHighlighted.length === 0}
                                                    className="p-1.5 rounded bg-white/10 text-gray-300 hover:bg-blue-500/30 hover:text-white disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
                                                    title="Adicionar selecionados"
                                                >
                                                    <ChevronRight className="w-4 h-4" />
                                                </button>
                                                <button
                                                    type="button"
                                                    onClick={removeSelected}
                                                    disabled={rightHighlighted.length === 0}
                                                    className="p-1.5 rounded bg-white/10 text-gray-300 hover:bg-blue-500/30 hover:text-white disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
                                                    title="Remover selecionados"
                                                >
                                                    <ChevronLeft className="w-4 h-4" />
                                                </button>
                                                <button
                                                    type="button"
                                                    onClick={addAll}
                                                    disabled={availableFiltered.length === 0}
                                                    className="p-1.5 rounded bg-white/10 text-gray-300 hover:bg-blue-500/30 hover:text-white disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
                                                    title={leftFilter.trim() ? 'Adicionar todos (filtrados)' : 'Adicionar todos'}
                                                >
                                                    <ChevronsRight className="w-4 h-4" />
                                                </button>
                                                <button
                                                    type="button"
                                                    onClick={clearToBtc}
                                                    className="p-1.5 rounded bg-white/10 text-gray-300 hover:bg-blue-500/30 hover:text-white transition-colors"
                                                    title="Limpar (só BTC)"
                                                >
                                                    <ChevronsLeft className="w-4 h-4" />
                                                </button>
                                            </div>
                                            <div className="flex flex-col min-h-0">
                                                <div className="text-xs text-gray-400 mb-1 font-medium">Selecionados</div>
                                                <div className="flex-1 min-h-[160px] max-h-48 overflow-y-auto rounded-sm border border-white/10 bg-black/40 p-1 space-y-0.5">
                                                    {selectedSymbols.map(s => (
                                                        <div
                                                            key={s}
                                                            onClick={() => toggleRight(s)}
                                                            onDoubleClick={() => setSelectedSymbols(prev => (prev.filter(x => x !== s).length ? prev.filter(x => x !== s) : ['BTC/USDT']))}
                                                            className={`px-3 py-1.5 rounded-sm text-sm cursor-pointer truncate ${rightHighlighted.includes(s) ? 'bg-blue-500/30 text-white' : 'text-gray-300 hover:bg-white/10'}`}
                                                        >
                                                            {s}
                                                        </div>
                                                    ))}
                                                </div>
                                            </div>
                                        </div>
                                        <p className="text-xs text-gray-500 mt-1">
                                            Clique para marcar; duplo clique para mover. Use os botões entre as listas para adicionar/remover.
                                        </p>
                                    </>
                                )}
                            </div>

                            <div>
                                <label className="block text-sm font-semibold text-gray-300 mb-2">
                                    Timeframe
                                </label>
                                <select
                                    value={timeframe}
                                    onChange={(e) => setTimeframe(e.target.value)}
                                    className="w-full glass px-4 py-3 rounded-lg border border-white/10 text-white focus:border-blue-500 focus:outline-none"
                                >
                                    <option value="1m" className="bg-gray-900 text-white">1 minute</option>
                                    <option value="5m" className="bg-gray-900 text-white">5 minutes</option>
                                    <option value="15m" className="bg-gray-900 text-white">15 minutes</option>
                                    <option value="1h" className="bg-gray-900 text-white">1 hour</option>
                                    <option value="4h" className="bg-gray-900 text-white">4 hours</option>
                                    <option value="1d" className="bg-gray-900 text-white">1 day</option>
                                </select>
                            </div>
                            <div>
                                <label className="block text-sm font-semibold text-gray-300 mb-2">
                                    Período
                                </label>
                                <select
                                    value={period}
                                    onChange={(e) => setPeriod(e.target.value as PeriodKey)}
                                    className="w-full glass px-4 py-3 rounded-lg border border-white/10 text-white focus:border-blue-500 focus:outline-none"
                                >
                                    <option value="6m" className="bg-gray-900 text-white">Últimos 6 meses</option>
                                    <option value="2y" className="bg-gray-900 text-white">Últimos 2 anos</option>
                                    <option value="all" className="bg-gray-900 text-white">Todo o período</option>
                                </select>
                            </div>
                        </div>

                        {/* Direction: Long / Short */}
                        <div className="mt-6">
                            <label className="block text-sm font-medium text-gray-300 mb-2">Direction</label>
                            <select
                                value={direction}
                                onChange={(e) => setDirection(e.target.value as 'long' | 'short')}
                                className="w-full glass px-4 py-3 rounded-lg border border-white/10 text-white focus:border-blue-500 focus:outline-none bg-white/5"
                            >
                                <option value="long" className="bg-gray-900 text-white">Long</option>
                                <option value="short" className="bg-gray-900 text-white">Short</option>
                            </select>
                            <p className="text-xs text-gray-400 mt-1">Long = buy on entry signal, sell on exit. Short = sell on entry, buy on exit (same template logic).</p>
                        </div>

                        {/* Deep Backtest Toggle */}
                        <div className="mt-6">
                            <label className="flex items-center gap-3 cursor-pointer group">
                                <input
                                    type="checkbox"
                                    checked={deepBacktest}
                                    onChange={(e) => setDeepBacktest(e.target.checked)}
                                    className="w-5 h-5 rounded border-2 border-white/20 bg-white/5 checked:bg-blue-500 checked:border-blue-500 cursor-pointer transition-all"
                                />
                                <div className="flex-1">
                                    <span className="text-sm font-semibold text-white group-hover:text-blue-400 transition-colors">
                                        Deep Backtest (15m Precision)
                                    </span>
                                    <p className="text-xs text-gray-400 mt-1">
                                        Simulates execution using 15-minute candles for realistic stop/target validation
                                    </p>
                                </div>
                            </label>
                        </div>

                        {/* Warning for tight stops without Deep Backtest */}
                        {!deepBacktest && metadata && metadata.stop_loss < 0.02 && (
                            <div className="mt-4 p-3 bg-yellow-500/10 border border-yellow-500/30 rounded-lg">
                                <p className="text-sm text-yellow-300 flex items-center gap-2">
                                    ⚠️ Tight stops may produce unrealistic results without Deep Backtesting
                                </p>
                            </div>
                        )}

                        <div className="mt-4 p-3 bg-blue-500/10 border border-blue-500/30 rounded-lg">
                            <p className="text-sm text-blue-300 flex items-center gap-2">
                                <Calendar className="w-4 h-4" />
                                {period === 'all'
                                    ? 'Será usado todo o histórico disponível para os símbolos escolhidos.'
                                    : period === '6m'
                                        ? 'Serão usados os últimos 6 meses de dados.'
                                        : 'Serão usados os últimos 2 anos de dados.'}
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
                                            <span className="text-sm font-medium text-purple-300 capitalize">
                                                {param.name.replace(/_/g, ' ')}
                                            </span>
                                        </div>
                                        <div className="grid grid-cols-2 gap-3">
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
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}

                    {/* Executar: 1 ou N ativos, mesmo botão */}
                    <div className="glass-strong rounded-2xl p-6 border border-white/10">
                        <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
                            <Sliders className="w-5 h-5" />
                            Otimizar
                            <span className="text-xs font-normal text-gray-400 flex items-center gap-1" title='1 ativo: otimiza, salva em favoritos e redireciona. N ativos: batch, salva cada um em favoritos (nota "gerado em lote", tier 3).'>
                                <HelpCircle className="w-4 h-4" />
                                ajuda
                            </span>
                        </h2>
                        <p className="text-sm text-gray-400 mb-4">
                            {getBatchSymbols().length === 1
                                ? '1 ativo selecionado: otimiza, salva em favoritos e abre a página de favoritos.'
                                : batchScope === 'all'
                                    ? 'Todos os pares: batch (pode demorar). Cada resultado é salvo em favoritos.'
                                    : `${selectedSymbols.length} ativos: batch. Cada resultado é salvo em favoritos.`}
                        </p>

                        <div className="flex flex-wrap items-center gap-4">
                            <button
                                onClick={handleRun}
                                disabled={batchRunning || running}
                                className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-500 hover:to-pink-500 disabled:from-gray-600 disabled:to-gray-700 text-white font-bold py-4 px-10 rounded-xl transition-all flex items-center justify-center gap-2 shadow-lg shadow-purple-500/50 hover:scale-105 disabled:scale-100 disabled:cursor-not-allowed"
                            >
                                {batchRunning || running ? (
                                    <>
                                        <Settings className="w-5 h-5 animate-spin" />
                                        Otimizando…
                                    </>
                                ) : (
                                    <>
                                        <Sliders className="w-5 h-5" />
                                        Otimizar
                                    </>
                                )}
                            </button>
                        </div>

                        {batchRunning && (
                            <div className="mt-4 p-4 bg-blue-500/10 border border-blue-500/30 rounded-lg">
                                <div className="flex items-center gap-2 text-blue-300 font-medium mb-2">
                                    <Settings className="w-4 h-4 animate-spin" />
                                    {(batchProgress?.processed ?? 0)} de {batchProgress?.total ?? batchTotal} ativos
                                </div>
                                {batchProgress?.current_symbol && (
                                    <p className="text-sm text-cyan-300/90 mb-2">
                                        Ativo atual: <span className="font-medium">{batchProgress.current_symbol}</span>
                                    </p>
                                )}
                                <div className="text-sm text-gray-300 space-y-1">
                                    <p>Tempo decorrido: {formatElapsed(clientElapsedSec)}</p>
                                    {(() => {
                                        const p = batchProgress?.processed ?? 0
                                        const t = batchProgress?.total ?? batchTotal
                                        const eta = batchProgress?.estimated_remaining_sec
                                        if (p > 0 && p < t && eta != null) return <p>Tempo restante: ~{formatElapsed(Math.ceil(eta))}</p>
                                        if (p > 0 && p < t) return <p>Tempo restante: calculando…</p>
                                        return null
                                    })()}
                                </div>
                                <div className="flex gap-2 mt-3">
                                    <button
                                        type="button"
                                        onClick={handlePauseBatch}
                                        disabled={batchPauseCancelRequested}
                                        className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-amber-500/20 text-amber-300 border border-amber-500/40 hover:bg-amber-500/30 disabled:opacity-50 disabled:cursor-not-allowed text-sm font-medium transition-colors"
                                    >
                                        <Pause className="w-4 h-4" />
                                        Pausar
                                    </button>
                                    <button
                                        type="button"
                                        onClick={handleCancelBatch}
                                        disabled={batchPauseCancelRequested}
                                        className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-red-500/20 text-red-300 border border-red-500/40 hover:bg-red-500/30 disabled:opacity-50 disabled:cursor-not-allowed text-sm font-medium transition-colors"
                                    >
                                        <Square className="w-4 h-4" />
                                        Encerrar
                                    </button>
                                </div>
                            </div>
                        )}

                        {!batchRunning && batchProgress && ['completed', 'failed', 'paused', 'cancelled'].includes(batchProgress.status) && (
                            <div className="mt-4 p-4 bg-white/5 border border-white/10 rounded-lg space-y-2">
                                <p className="text-sm font-medium text-white">
                                    {batchProgress.status === 'cancelled' && 'Encerrado pelo usuário. '}
                                    {batchProgress.status === 'paused' && 'Pausado pelo usuário. '}
                                    {batchProgress.succeeded} sucesso, {batchProgress.failed} falha
                                    {(batchProgress.skipped ?? 0) > 0 && `, ${batchProgress.skipped} ignorado(s) (já em favoritos ou não suportados)`}.
                                </p>
                                {batchProgress.errors.length > 0 && (
                                    <details className="text-xs text-gray-400">
                                        <summary>Erros por ativo</summary>
                                        <ul className="mt-1 list-disc list-inside">
                                            {batchProgress.errors.map((e, i) => (
                                                <li key={i}>{e.symbol}: {e.error}</li>
                                            ))}
                                        </ul>
                                    </details>
                                )}
                                <button
                                    onClick={() => navigate('/favorites')}
                                    className="inline-flex items-center gap-1 text-sm text-cyan-400 hover:text-cyan-300"
                                >
                                    <ExternalLink className="w-4 h-4" />
                                    Abrir Strategy Favorites
                                </button>
                            </div>
                        )}
                    </div>
                </div>
            </main>
        </div>
    )
}
