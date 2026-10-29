import { useState, useEffect, useMemo, useRef } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { Settings, TrendingUp, Calendar, DollarSign, Sliders, HelpCircle } from 'lucide-react'
import { API_BASE_URL, apiUrl } from '../lib/apiBase'
import { BackendLogViewer } from '../components/BackendLogViewer'
import { AssetPicker } from '../components/AssetPicker'
import {
    BatchConfirm,
    BatchConfirmError,
    BatchConfirmLoading,
    BatchPanel,
    BatchPausedBlock,
    type BatchPanelHandle,
} from '../components/batch/BatchLote'
import { useBatchJob } from '../hooks/useBatchJob'
import { authFetch } from '@/lib/authFetch'
import {
    CLASS_NOTE,
    ON_DEMAND_TEXT_BACKTEST,
    TOP10_SYMBOLS,
    blockedNotice,
    collectingCopy,
    cryptoOnlyTimeframes,
    equityTimeframeBlock,
    historyUnavailableNotice,
    marketDataText,
    planRun,
    refusalMessage,
    runCopy,
    timeframeDisabled,
    type RunNotice,
} from '../lib/assetSelection'
import '../components/results/DataExecution.css'
import { tradableCrypto, useSelectionView } from '../lib/assetStore'
import {
    comboPeriodHint,
    customPeriodImpediments,
    isPeriodKey,
    PERIOD_OPTIONS,
    resolvePeriodDates,
    type PeriodKey,
} from '../lib/sweepPeriod'

interface TemplateMetadata {
    name: string
    display_name?: string
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
    const [walkForwardEnabled, setWalkForwardEnabled] = useState(false)
    const [walkForwardTrainRatio, setWalkForwardTrainRatio] = useState(0.7)
    const [direction, setDirection] = useState<'long' | 'short'>('long')
    const [logs, setLogs] = useState<string[]>([])
    const [logViewerOpen, setLogViewerOpen] = useState(false)

    const [period, setPeriod] = useState<PeriodKey>('all')
    const [customStartDate, setCustomStartDate] = useState('')
    const [customEndDate, setCustomEndDate] = useState('')

    // Ativos: o seletor do catálogo (cripto, ações e ETFs). Padrão BTC/USDT, como no incumbente.
    const defaultSymbol = 'BTC/USDT'
    const [selectedSymbols, setSelectedSymbols] = useState<string[]>([defaultSymbol])
    const [runNotice, setRunNotice] = useState<RunNotice | null>(null)

    // Lote multiclasse (card #1120): plano, progresso por ativo, Pausar, Retomar e Encerrar (compartilhados com a Otimização)
    const batch = useBatchJob()
    const runButton = useRef<HTMLButtonElement>(null)
    const panelRef = useRef<BatchPanelHandle>(null)

    // O que roda e o que fica fora, por classe e tempo (ação, ETF e ativo marcado pela Binance).
    const { entries: selectionEntries, loading: selectionLoading } = useSelectionView(selectedSymbols)
    const plan = useMemo(
        () => planRun(selectionEntries, { timeframe, page: 'combo' }),
        [selectionEntries, timeframe],
    )
    // Ação/ETF sozinha (card #1119): roda o backtest de 1 ativo. 1m e 5m ficam indisponíveis e, se o
    // tempo já era 5m (seleção mista antes), a tela avisa antes de rodar sem trocar o valor.
    const equityRun = plan.equityRun
    const tfBlock = equityTimeframeBlock(plan, timeframe, 'combo')
    const copy = runCopy(plan, 'combo')
    const [collecting, setCollecting] = useState<string | null>(null)
    const cryptoOnlyTfs = cryptoOnlyTimeframes(plan)
    const batchRunning = batch.active && batch.job?.status !== 'paused'

    useEffect(() => {
        if (templateName) {
            fetchMetadata()
            // Template short_ema200_pullback é só para short: forçar Direction = Short
            if (templateName === 'short_ema200_pullback') {
                setDirection('short')
            }
        }
    }, [templateName])

    const fetchMetadata = async () => {
        try {
            const response = await authFetch(`${API_BASE_URL}/combos/meta/${templateName}`)
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

    // Aviso antes de rodar quando nada roda; devolve o aviso ou null (a seleção é mantida).
    const getRunBlock = (): RunNotice | null => {
        if (tfBlock) return tfBlock.notice
        if (plan.mode === 'none') {
            return { tone: 'warn', title: 'Escolha ao menos 1 ativo', body: 'Pesquise e marque um par cripto em USDT.' }
        }
        if (plan.mode === 'blocked') return blockedNotice(plan, 'combo')
        return null
    }

    const periodText = (): string => {
        if (period === 'custom') return `${customStartDate || '—'} a ${customEndDate || '—'}`
        return (PERIOD_OPTIONS.find((o) => o.value === period)?.label ?? 'todo o histórico').toLowerCase()
    }
    const configText = (): string =>
        `${metadata?.display_name || metadata?.name || templateName} · ${timeframe} · ${periodText()} · ` +
        `${direction === 'short' ? 'Short' : 'Long'} · ${deepBacktest ? 'Deep Backtest (15m)' : 'candle do tempo gráfico'}`

    function getPeriodDates(): { start_date: string | null; end_date: string | null } {
        return resolvePeriodDates(period, customStartDate, customEndDate)
    }

    const handleRun = async () => {
        const periodIssues = customPeriodImpediments(period, customStartDate, customEndDate)
        if (periodIssues.length) {
            alert(periodIssues[0])
            return
        }
        setRunNotice(null)
        const blocked = getRunBlock()
        if (blocked) {
            // Nada é executado nem salvo; a seleção fica como está.
            setRunNotice(blocked)
            return
        }
        const symbolsToRun = plan.runnable
        if (symbolsToRun.length === 0) {
            alert('Nenhum símbolo disponível.')
            return
        }

        const custom_ranges: Record<string, { min: number; max: number; step: number }> = {}
        params.forEach(p => {
            custom_ranges[p.name] = { min: p.min, max: p.max, step: p.step ?? 1 }
        })
        const { start_date, end_date } = getPeriodDates()
        if (plan.mode === 'single') {
            batch.dismissFinished()
            setRunning(true)
            const isEquityRun = !!equityRun
            if (isEquityRun) setCollecting(collectingCopy(symbolsToRun[0], 'combo', timeframe, deepBacktest))
            try {
                if (!isEquityRun) {
                    // Ação/ETF não vira favorito (#1122): nem checa /favorites/exists.
                    const existsUrl = apiUrl('/favorites/exists')
                    existsUrl.searchParams.set('strategy_name', templateName)
                    existsUrl.searchParams.set('symbol', symbolsToRun[0])
                    existsUrl.searchParams.set('timeframe', timeframe)
                    existsUrl.searchParams.set('period_type', period)
                    existsUrl.searchParams.set('direction', direction)
                    if (period === 'custom') {
                        if (start_date) existsUrl.searchParams.set('start_date', start_date)
                        if (end_date) existsUrl.searchParams.set('end_date', end_date)
                    }
                    const existsRes = await authFetch(existsUrl.toString())
                    if (existsRes.ok) {
                        const { exists } = await existsRes.json()
                        if (exists) {
                            alert('Estratégia já existe nos favoritos (mesmo template, ativo, timeframe, período e direção). Redirecionando.')
                            navigate('/favorites')
                            return
                        }
                    }
                }
                const res = await authFetch(`${API_BASE_URL}/combos/optimize`, {
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
                        custom_ranges,
                        split_train_ratio: walkForwardEnabled ? walkForwardTrainRatio : null,
                        period_type: period,
                        run_scope: 'single',
                    })
                })
                if (!res.ok) {
                    const err = await res.json().catch(() => ({}))
                    if (isEquityRun) {
                        // Coleta falhou sem nada guardado, tempo recusado ou ativo marcado: alerta com o motivo.
                        const unavailable = historyUnavailableNotice(err?.detail)
                        setRunNotice(
                            unavailable ?? {
                                tone: 'alert',
                                title: 'Não foi possível rodar o backtest',
                                body: refusalMessage(err?.detail, 'Falha na otimização'),
                            },
                        )
                        return
                    }
                    alert(refusalMessage(err?.detail, 'Falha na otimização'))
                    return
                }
                const result = await res.json()
                const name = `${result.template_name} - ${result.symbol} ${result.timeframe} (${new Date().toLocaleTimeString()})`
                const baseParams = result.best_parameters ?? result.parameters ?? {}
                const parameters = { ...baseParams, direction }
                const metrics = {
                    ...(result.best_metrics ?? {}),
                    trades: Array.isArray(result.trades) ? result.trades : [],
                }
                const oosVerdict = result.oos_verdict ?? null
                // Walk-forward ativo: mostra a tela de resultados com o comparativo
                // Treino vs Holdout e o veredito (GO/NO-GO) para o usuário decidir.
                if (isEquityRun || walkForwardEnabled || oosVerdict) {
                    navigate('/combo/results', {
                        state: {
                            result: {
                                template_name: result.template_name,
                                symbol: result.symbol,
                                timeframe: result.timeframe,
                                start_date: start_date ?? null,
                                end_date: end_date ?? null,
                                period_type: period,
                                execution_mode: result.execution_mode ?? 'fast_1d',
                                asset: result.asset ?? null,
                                data_provenance: result.data_provenance ?? null,
                                execution: result.execution ?? null,
                                conventions: result.conventions ?? null,
                                combination_errors: result.combination_errors ?? null,
                                parameters,
                                metrics,
                                promotion_metrics: result.promotion_metrics ?? metrics,
                                trades: Array.isArray(result.trades) ? result.trades : [],
                                candles: Array.isArray(result.candles) ? result.candles : [],
                                indicator_data:
                                    result.indicator_data && typeof result.indicator_data === 'object'
                                        ? result.indicator_data
                                        : {},
                                direction: result.direction ?? direction,
                                strategy_transparency: result.strategy_transparency ?? null,
                                oos_verdict: oosVerdict,
                                oos_metrics: result.oos_metrics ?? null,
                                oos_proof: result.oos_proof ?? null,
                            },
                            isOptimization: true,
                            returnTo: '/combo/configure',
                        },
                    })
                    return
                }
                const favRes = await authFetch(`${API_BASE_URL}/favorites/`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        name,
                        symbol: result.symbol,
                        timeframe: result.timeframe,
                        strategy_name: result.template_name,
                        parameters,
                        metrics,
                        start_date: start_date ?? null,
                        end_date: end_date ?? null,
                        period_type: period,
                        oos_verdict: oosVerdict,
                        oos_metrics: result.oos_metrics ?? null,
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
                setCollecting(null)
            }
            return
        }

        // Mais de 1 ativo é sempre lote (decisão 2): o servidor monta o plano e o Confirmar abre no fluxo.
        await batch.requestPreview({
            template_name: templateName,
            symbols: plan.selected,
            timeframe,
            start_date,
            end_date,
            period_type: period,
            deep_backtest: deepBacktest,
            direction,
            custom_ranges,
            split_train_ratio: walkForwardEnabled ? walkForwardTrainRatio : null,
            page: 'combo',
        })
    }

    const confirmBatch = async (body: Record<string, unknown>) => {
        const started = await batch.confirmAndRun(body)
        if (started) requestAnimationFrame(() => panelRef.current?.focusTitle())
    }

    const backFromConfirm = () => {
        batch.closeConfirm()
        runButton.current?.focus()
    }

    // Top 10: soma só os negociáveis da lista atual do catálogo (marcados e fora do catálogo ficam de fora).
    const selectTopSymbols = async () => {
        const tradable = await tradableCrypto(TOP10_SYMBOLS)
        if (!tradable.length) return
        setSelectedSymbols(prev => {
            const next = new Set(prev)
            tradable.forEach(x => next.add(x))
            return [...next]
        })
    }

    // Seleção vazia (último chip removido) volta ao padrão, como no incumbente.
    const changeSymbols = (next: string[]) => {
        setSelectedSymbols(next.length ? next : [defaultSymbol])
        setRunNotice(null)
    }

    if (loading) {
        return (
            <div className="app-page combo-page flex min-h-[50vh] items-center justify-center">
                <div className="text-center">
                    <Settings className="w-12 h-12 animate-spin text-blue-400 mx-auto mb-4" />
                    <p className="text-zinc-400">Loading configuration...</p>
                </div>
            </div>
        )
    }

    if (!metadata) {
        return (
            <div className="app-page combo-page flex min-h-[50vh] items-center justify-center">
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
        <div className="app-page combo-page relative overflow-hidden">
            {/* Main Content */}
            <main className="container mx-auto px-6 py-12">
                <div className="max-w-4xl mx-auto space-y-8">
                    {/* Template Info */}
                    <div className="glass-strong rounded-[28px] p-6 border border-zinc-200">
                        <h2 className="text-xl font-bold text-zinc-900 mb-4">Template Information</h2>
                        <div className="space-y-3">
                            <div>
                                <span className="text-zinc-400 text-sm">Description:</span>
                                <p className="text-zinc-900">{metadata.description}</p>
                            </div>
                            <div>
                                <span className="text-zinc-400 text-sm">Indicators:</span>
                                <div className="flex flex-wrap gap-2 mt-2">
                                    {metadata.indicators.map((ind, i) => (
                                        <span key={i} className="px-3 py-1 bg-blue-500/20 text-blue-400 rounded-lg text-sm border border-blue-500/30">
                                            {ind.alias || ind.type}
                                        </span>
                                    ))}
                                </div>
                            </div>
                            <div>
                                <span className="text-zinc-400 text-sm">Entry Logic:</span>
                                <code className="block mt-1 p-3 bg-white0 rounded-[16px] text-green-400 text-sm font-mono">
                                    {metadata.entry_logic}
                                </code>
                            </div>
                            <div>
                                <span className="text-zinc-400 text-sm">Exit Logic:</span>
                                <code className="block mt-1 p-3 bg-white0 rounded-[16px] text-red-400 text-sm font-mono">
                                    {metadata.exit_logic}
                                </code>
                            </div>
                        </div>
                    </div>

                    {/* Configuration */}
                    <div className="glass-strong rounded-[28px] p-6 border border-zinc-200">
                        <h2 className="text-xl font-bold text-zinc-900 mb-6 flex items-center gap-2">
                            <TrendingUp className="w-5 h-5" />
                            Configuration
                        </h2>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <div>
                                <label className="block text-sm font-semibold text-zinc-500 mb-2">Market Data</label>
                                <div
                                    className="glass px-4 py-3 rounded-[16px] border border-zinc-200 text-sm text-zinc-600 r19-md"
                                    data-testid="combo-market-data"
                                >
                                    {marketDataText(plan)}
                                </div>
                            </div>
                            <div className="md:col-span-2">
                                <label className="block text-sm font-semibold text-zinc-500 mb-2">
                                    <DollarSign className="w-4 h-4 inline mr-1" />
                                    Ativos
                                </label>
                                <p className="text-xs text-zinc-400 mb-2" data-testid="combo-scope-hint">
                                    1 ativo: otimiza o <strong>primeiro</strong>. N ativos: <strong>batch</strong> nos selecionados.
                                </p>
                                <AssetPicker
                                    value={selectedSymbols}
                                    onChange={changeSymbols}
                                    ariaLabel="Seletor de ativos"
                                    clearTo={[defaultSymbol]}
                                    clearLabel="Limpar (1 ativo)"
                                    onDemandTexts={ON_DEMAND_TEXT_BACKTEST}
                                    classNote={CLASS_NOTE.combo}
                                    extraActions={(
                                        <button
                                            type="button"
                                            className="ap-btn"
                                            data-testid="combo-top10"
                                            onClick={() => void selectTopSymbols()}
                                        >
                                            Top 10
                                        </button>
                                    )}
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-semibold text-zinc-500 mb-2">
                                    Timeframe
                                </label>
                                <select
                                    value={timeframe}
                                    onChange={(e) => setTimeframe(e.target.value)}
                                    className="w-full glass px-4 py-3 rounded-[16px] border border-zinc-200 text-zinc-900 focus:border-blue-500 focus:outline-none"
                                >
                                    {([['1m', '1 minute'], ['5m', '5 minutes'], ['15m', '15 minutes'], ['1h', '1 hour'], ['4h', '4 hours'], ['1d', '1 day']] as const).map(([value, label]) => (
                                        <option
                                            key={value}
                                            value={value}
                                            className="bg-zinc-900 text-zinc-900"
                                            disabled={timeframeDisabled(plan, value)}
                                        >
                                            {label}{cryptoOnlyTfs.includes(value) ? ' (só cripto)' : ''}
                                        </option>
                                    ))}
                                </select>
                                {equityRun ? (
                                    <p className="r19-hint" data-testid="combo-timeframe-hint">
                                        <b>Ação e ETF:</b> 15m, 1h, 4h ou 1d, montados no pregão regular de Nova York, sem candle que atravesse o fechamento.
                                    </p>
                                ) : null}
                            </div>
                            <div>
                                <label className="block text-sm font-semibold text-zinc-500 mb-2">
                                    Período
                                </label>
                                <select
                                    value={period}
                                    data-testid="sel-period"
                                    aria-label="Período"
                                    onChange={(e) => {
                                        const next = e.target.value
                                        if (isPeriodKey(next)) setPeriod(next)
                                    }}
                                    className="w-full glass px-4 py-3 rounded-[16px] border border-zinc-200 text-zinc-900 focus:border-blue-500 focus:outline-none"
                                >
                                    {PERIOD_OPTIONS.map((opt) => (
                                        <option key={opt.value} value={opt.value} className="bg-zinc-900 text-zinc-900">
                                            {opt.label}
                                        </option>
                                    ))}
                                </select>
                            </div>
                        </div>
                        {period === 'custom' ? (
                            <div className="mt-4 grid grid-cols-1 gap-3 sm:grid-cols-2">
                                <label className="block">
                                    <span className="block text-sm font-semibold text-zinc-500 mb-2">Data Inicial</span>
                                    <input
                                        type="date"
                                        value={customStartDate}
                                        data-testid="date-start"
                                        aria-label="Data Inicial"
                                        onChange={(e) => setCustomStartDate(e.target.value)}
                                        className="w-full min-h-[44px] glass px-4 py-3 rounded-[16px] border border-zinc-200 text-zinc-900 focus:border-blue-500 focus:outline-none"
                                    />
                                </label>
                                <label className="block">
                                    <span className="block text-sm font-semibold text-zinc-500 mb-2">Data Final</span>
                                    <input
                                        type="date"
                                        value={customEndDate}
                                        data-testid="date-end"
                                        aria-label="Data Final"
                                        onChange={(e) => setCustomEndDate(e.target.value)}
                                        className="w-full min-h-[44px] glass px-4 py-3 rounded-[16px] border border-zinc-200 text-zinc-900 focus:border-blue-500 focus:outline-none"
                                    />
                                </label>
                            </div>
                        ) : null}

                        {/* Direction: Long / Short */}
                        <div className="mt-6">
                            <label className="block text-sm font-medium text-zinc-500 mb-2">Direction</label>
                            <select
                                value={direction}
                                onChange={(e) => setDirection(e.target.value as 'long' | 'short')}
                                className="w-full glass px-4 py-3 rounded-[16px] border border-zinc-200 text-zinc-900 focus:border-blue-500 focus:outline-none bg-zinc-50"
                            >
                                <option value="long" className="bg-zinc-900 text-zinc-900">Long</option>
                                <option value="short" className="bg-zinc-900 text-zinc-900">Short</option>
                            </select>
                            <p className="text-xs text-zinc-400 mt-1">Long = buy on entry signal, sell on exit. Short = sell on entry, buy on exit (same template logic).</p>
                        </div>

                        {/* Deep Backtest Toggle */}
                        <div className="mt-6">
                            <label className="flex items-center gap-3 cursor-pointer group">
                                <input
                                    type="checkbox"
                                    checked={deepBacktest}
                                    onChange={(e) => setDeepBacktest(e.target.checked)}
                                    className="w-5 h-5 rounded border-2 border-zinc-300 bg-zinc-50 checked:bg-blue-500 checked:border-blue-500 cursor-pointer transition-all"
                                />
                                <div className="flex-1">
                                    <span className="text-sm font-semibold text-zinc-900 group-hover:text-blue-400 transition-colors">
                                        Deep Backtest (15m Precision)
                                    </span>
                                    <p className="text-xs text-zinc-400 mt-1">
                                        Simulates execution using 15-minute candles for realistic stop/target validation
                                    </p>
                                    {equityRun ? (
                                        <p className="r19-hint" data-testid="combo-deep-hint">
                                            <b>Ação e ETF:</b> usa o 15m montado do 5m. Se o intradiário não cobrir a janela, o backtest roda em precisão diária e o resultado mostra o trecho que faltou.
                                        </p>
                                    ) : null}
                                </div>
                            </label>
                        </div>

                        {/* Warning for tight stops without Deep Backtest */}
                        {!deepBacktest && metadata && metadata.stop_loss < 0.02 && (
                            <div className="mt-4 p-3 bg-yellow-500/10 border border-yellow-500/30 rounded-[16px]">
                                <p className="text-sm text-yellow-300 flex items-center gap-2">
                                    ⚠️ Tight stops may produce unrealistic results without Deep Backtesting
                                </p>
                            </div>
                        )}

                        {/* Walk-forward split toggle (card #470) */}
                        <div className="mt-6">
                            <label className="flex items-center gap-3 cursor-pointer group">
                                <input
                                    type="checkbox"
                                    checked={walkForwardEnabled}
                                    onChange={(e) => setWalkForwardEnabled(e.target.checked)}
                                    className="w-5 h-5 rounded border-2 border-zinc-300 bg-zinc-50 checked:bg-blue-500 checked:border-blue-500 cursor-pointer transition-all"
                                />
                                <div className="flex-1">
                                    <span className="text-sm font-semibold text-zinc-900 group-hover:text-blue-400 transition-colors">
                                        Validação walk-forward (split 70/30)
                                    </span>
                                    <p className="text-xs text-zinc-400 mt-1">
                                        Otimiza parâmetros só no treino (70%) e valida no holdout (30%) com veredito GO/NO-GO.
                                    </p>
                                </div>
                            </label>
                            {walkForwardEnabled && (
                                <div className="mt-3 flex items-center gap-4">
                                    <label className="flex items-center gap-2 text-xs text-zinc-400">
                                        <span>Treino</span>
                                        <input
                                            type="number"
                                            min={10}
                                            max={90}
                                            value={Math.round(walkForwardTrainRatio * 100)}
                                            onChange={(e) => {
                                                const v = Number(e.target.value)
                                                if (v >= 10 && v <= 90) setWalkForwardTrainRatio(v / 100)
                                            }}
                                            className="w-16 rounded border border-zinc-300 bg-zinc-50 px-2 py-1 text-sm text-zinc-900 focus:border-blue-500 focus:outline-none"
                                        />
                                        <span>%</span>
                                    </label>
                                    <span className="text-xs text-zinc-400">Holdout: {100 - Math.round(walkForwardTrainRatio * 100)}%</span>
                                </div>
                            )}
                        </div>

                        <div className="mt-4 p-3 bg-blue-500/10 border border-blue-500/30 rounded-[16px]">
                            <p className="text-sm text-blue-300 flex items-center gap-2">
                                <Calendar className="w-4 h-4" />
                                {comboPeriodHint(period, customStartDate, customEndDate)}
                            </p>
                        </div>
                    </div>

                    {/* Parameter Optimization Ranges */}
                    {params.length > 0 && (
                        <div className="glass-strong rounded-[28px] p-6 border border-zinc-200">
                            <h2 className="text-xl font-bold text-zinc-900 mb-6 flex items-center gap-2">
                                <Sliders className="w-5 h-5" />
                                Parameter Optimization Ranges
                            </h2>

                            <div className="space-y-4">
                                {params.map((param, idx) => (
                                    <div key={idx} className="bg-zinc-50 rounded-[16px] p-4">
                                        <div className="flex justify-between items-center mb-3">
                                            <span className="text-sm font-medium text-purple-300 capitalize">
                                                {param.name.replace(/_/g, ' ')}
                                            </span>
                                        </div>
                                        <div className="grid grid-cols-2 gap-3">
                                            <div>
                                                <label className="text-xs text-zinc-400 block mb-1">Min</label>
                                                <input
                                                    type="number"
                                                    value={param.min}
                                                    onChange={(e) => {
                                                        const newParams = [...params]
                                                        newParams[idx].min = parseFloat(e.target.value)
                                                        setParams(newParams)
                                                    }}
                                                    className="w-full bg-white0 border border-zinc-200 rounded-[14px] px-3 py-2 text-sm text-zinc-900 focus:border-purple-500 focus:outline-none"
                                                />
                                            </div>
                                            <div>
                                                <label className="text-xs text-zinc-400 block mb-1">Max</label>
                                                <input
                                                    type="number"
                                                    value={param.max}
                                                    onChange={(e) => {
                                                        const newParams = [...params]
                                                        newParams[idx].max = parseFloat(e.target.value)
                                                        setParams(newParams)
                                                    }}
                                                    className="w-full bg-white0 border border-zinc-200 rounded-[14px] px-3 py-2 text-sm text-zinc-900 focus:border-purple-500 focus:outline-none"
                                                />
                                            </div>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}

                    {/* Executar: 1 ou N ativos, mesmo botão */}
                    <div className="glass-strong rounded-[28px] p-6 border border-zinc-200">
                        <h2 className="text-xl font-bold text-zinc-900 mb-4 flex items-center gap-2">
                            <Sliders className="w-5 h-5" />
                            Otimizar
                            <span className="text-xs font-normal text-zinc-400 flex items-center gap-1" title='1 ativo: otimiza, salva em favoritos e redireciona. N ativos: batch, salva cada um em favoritos (nota "gerado em lote", sem estrela).'>
                                <HelpCircle className="w-4 h-4" />
                                ajuda
                            </span>
                        </h2>
                        <p
                            className="lote-runcopy"
                            data-testid="combo-run-copy"
                        >
                            {copy.parts ? (
                                <>
                                    <b>{copy.parts.lead}</b> {copy.parts.runs}{' '}
                                    <span className="lote-out">{copy.parts.out}</span>
                                </>
                            ) : copy.blocked ? (
                                <span className="lote-out">{copy.text}</span>
                            ) : (
                                copy.text
                            )}
                        </p>

                        <div className="flex flex-wrap items-center gap-4">
                            <button
                                ref={runButton}
                                onClick={handleRun}
                                disabled={batchRunning || running || selectionLoading || batch.starting}
                                data-testid="combo-run"
                                className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-500 hover:to-pink-500 disabled:from-gray-600 disabled:to-gray-700 text-zinc-900 font-bold py-4 px-10 rounded-[16px] transition-all flex items-center justify-center gap-2 shadow-lg shadow-purple-500/50 hover:scale-105 disabled:scale-100 disabled:cursor-not-allowed"
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

                            <button
                                type="button"
                                onClick={() => setLogViewerOpen(true)}
                                className="bg-zinc-50 hover:bg-zinc-100 text-zinc-600 px-4 py-3 rounded-[16px] border border-zinc-200 transition-colors"
                                title="Ver logs do backend (últimas linhas)"
                            >
                                Ver logs
                            </button>
                        </div>

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

                        {batch.confirm.phase === 'loading' ? <BatchConfirmLoading /> : null}
                        {batch.confirm.phase === 'ready' ? (
                            <BatchConfirm
                                preview={batch.confirm.preview}
                                config={{ text: configText() }}
                                busy={batch.starting}
                                onConfirm={() => void confirmBatch((batch.confirm as { body: Record<string, unknown> }).body)}
                                onBack={backFromConfirm}
                            />
                        ) : null}
                        {batch.confirm.phase === 'error' ? (
                            <BatchConfirmError message={batch.confirm.message} onBack={backFromConfirm} />
                        ) : null}
                        {batch.confirm.phase === 'paused' ? (
                            <BatchPausedBlock
                                job={batch.job}
                                jobId={batch.confirm.jobId}
                                onResume={() => {
                                    batch.closeConfirm()
                                    void batch.resumeById((batch.confirm as { jobId: string }).jobId)
                                }}
                                onCancel={() => {
                                    batch.closeConfirm()
                                    void batch.cancelById((batch.confirm as { jobId: string }).jobId)
                                    requestAnimationFrame(() => panelRef.current?.focusTitle())
                                }}
                                onBack={backFromConfirm}
                            />
                        ) : null}
                        {batch.job ? (
                            <BatchPanel
                                ref={panelRef}
                                job={batch.job}
                                pending={batch.pending}
                                actionError={batch.actionError}
                                onPause={() => void batch.pause()}
                                onResume={() => void batch.resume()}
                                onCancel={() => void batch.cancel()}
                                showDiscoveryLink
                            />
                        ) : null}
                    </div>
                </div>
            </main>

            <BackendLogViewer
                open={logViewerOpen}
                onClose={() => setLogViewerOpen(false)}
                name="full_execution_log"
                lines={400}
                pollMs={2000}
            />
        </div>
    )
}
