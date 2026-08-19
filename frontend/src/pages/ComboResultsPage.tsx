import { useLocation, useNavigate } from 'react-router-dom'
import { useState, useMemo } from 'react'
import { BarChart3, ArrowLeft, Star } from 'lucide-react'
import { MonitorAlignedCandlestickChart } from '../components/MonitorAlignedCandlestickChart'
import { SaveFavoriteModal } from '../components/SaveFavoriteModal'
import { StrategyTradesTable } from '../components/charts/StrategyTradesTable'
import { StrategyTransparencyPanel } from '../components/trades/StrategyTransparencyPanel'
import { StrategyRuleOverview } from '../components/trades/StrategyRuleOverview'
import { API_BASE_URL } from '../lib/apiBase'
import { authFetch } from '@/lib/authFetch'
import { buildTradeMarkers } from '@/lib/tradeMarkers'
import { buildSignalHistoryMarkers, type MonitorSyncStatus } from '@/lib/signalHistory'
import { normalizeStrategyTransparency, type StrategyTransparency } from '@/lib/strategyTransparency'
import type { OpportunitySignalHistoryItem } from '@/components/monitor/types'
import { OosMetricsTable, OosVerdictBadge } from '@/components/results/OosComparison'

interface BacktestResult {
    template_name: string
    display_name?: string | null
    symbol: string
    timeframe: string
    start_date?: string | null
    end_date?: string | null
    period_type?: string | null
    execution_mode?: string
    strategy_description?: string | null
    is_strategy_protected?: boolean
    parameters: Record<string, any>
    metrics: {
        total_trades: number
        win_rate: number
        total_return: number
        avg_profit: number
        sharpe_ratio?: number
        max_drawdown?: number
    }
    promotion_metrics?: Record<string, any> | null
    trades: Array<{
        entry_time: string
        entry_price: number
        exit_time?: string
        exit_price?: number
        profit?: number
        type?: string
        pnl?: number
        initial_capital?: number
        final_capital?: number
    }>
    indicator_data: Record<string, number[]>
    strategy_transparency?: StrategyTransparency | Record<string, unknown> | null
    signal_history?: OpportunitySignalHistoryItem[] | null
    monitor_sync_status?: MonitorSyncStatus | null
    candles: Array<{
        timestamp_utc: string
        open: number
        high: number
        low: number
        close: number
        volume: number
    }>
    /** Walk-forward (card #470): métricas e veredito do holdout quando split usado */
    oos_metrics?: Record<string, any> | null
    oos_proof?: string | null
    oos_verdict?: {
        status?: string
        reasons?: string[]
        warnings?: string[]
        holdout_trades?: number
        execution_mode?: string
        split_train_ratio?: number
    } | null
}

export function ComboResultsPage() {
    const location = useLocation()
    const navigate = useNavigate()
    const result = location.state?.result as BacktestResult
    const returnTo = location.state?.returnTo as string | undefined
    const isOptimization = location.state?.isOptimization === true
    const [isModalOpen, setIsModalOpen] = useState(false)

    const handleSaveFavorite = async (data: any) => {
        console.log('📤 handleSaveFavorite chamado com:', data)

        try {
            const response = await authFetch(`${API_BASE_URL}/favorites`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            })

            console.log('📡 Response status:', response.status)

            if (!response.ok) {
                const error = await response.json()
                console.error('❌ Erro da API:', error)
                throw new Error(error.detail || 'Erro ao salvar favorito')
            }

            const savedFavorite = await response.json()
            console.log('✅ Favorito salvo com sucesso:', savedFavorite)
            navigate('/favorites')
        } catch (err) {
            console.error('❌ Erro ao salvar favorito:', err)
            throw err
        }
    }

    const handleBack = () => {
        if (returnTo) {
            navigate(returnTo)
            return
        }
        if (window.history.length > 1) {
            navigate(-1)
            return
        }
        navigate('/combo/select')
    }

    const handleExportTrades = async () => {
        try {
            // Filter only closed trades (with exit_time) for export
            // This ensures consistency with metrics calculation
            const closedTrades = result.trades.filter(t => t.exit_time && t.exit_price);
            
            console.log(`📊 Exportando trades: ${closedTrades.length} fechados de ${result.trades.length} total`);
            
            // Prepare trades data with all necessary fields
            const tradesData = closedTrades.map(trade => {
                // Calculate P&L in USD if not present
                let pnl = trade.pnl;
                if (pnl === undefined && trade.profit !== undefined) {
                    // If we have profit percentage, we need initial capital to calculate P&L
                    // For now, we'll use a default or calculate from entry price
                    const initialCapital = 100; // Default starting capital
                    pnl = initialCapital * trade.profit;
                }
                
                const isShortExport = ((result as any).direction ?? result.parameters?.direction ?? strategyTransparency?.direction ?? 'long').toString().toLowerCase() === 'short';
                // Determinar Signal Type (prioridade: signal_type > exit_reason > entry_signal_type)
                let signalType = (trade as any).signal_type || '';
                if (!signalType) {
                    const exitReason = (trade as any).exit_reason || '';
                    if (exitReason && exitReason.toLowerCase().includes('stop')) {
                        signalType = 'Stop';
                    } else if (exitReason) {
                        signalType = isShortExport ? 'Cobrir' : 'Close entry(s) order...';
                    } else {
                        signalType = (trade as any).entry_signal_type || (isShortExport ? 'Vender' : 'Comprar');
                    }
                }
                
                return {
                    entry_time: trade.entry_time,
                    entry_price: trade.entry_price,
                    exit_time: trade.exit_time || '',
                    exit_price: trade.exit_price || 0,
                    type: (trade as any).type || (isShortExport ? 'short' : 'long'),
                    signal_type: signalType,  // Incluir signal_type para exportação
                    profit: trade.profit || 0,
                    pnl: pnl || 0,
                    initial_capital: trade.initial_capital || 100,
                    final_capital: trade.final_capital || (100 + (pnl || 0))
                };
            });

            const response = await fetch(`${API_BASE_URL}/combos/export-trades`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    trades: tradesData,
                    symbol: result.symbol,
                    template_name: result.template_name,
                    timeframe: result.timeframe
                })
            });

            if (!response.ok) {
                throw new Error('Erro ao exportar trades');
            }

            // Get the blob and create download link
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            
            // Extract filename from Content-Disposition header or use default
            const contentDisposition = response.headers.get('Content-Disposition');
            let filename = `${result.template_name}_${result.symbol.replace('/', '_')}_${result.timeframe}_trades.xlsx`;
            if (contentDisposition) {
                const filenameMatch = contentDisposition.match(/filename="?(.+)"?/);
                if (filenameMatch) {
                    filename = filenameMatch[1];
                }
            }
            
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
        } catch (err) {
            console.error('❌ Erro ao exportar trades:', err);
            alert('Erro ao exportar trades para Excel. Tente novamente.');
        }
    }

    const trades = useMemo(() => result?.trades ?? [], [result?.trades])
    const strategyTransparency = useMemo(
        () => normalizeStrategyTransparency(result?.strategy_transparency),
        [result?.strategy_transparency],
    )

    // Métricas derivadas dos MESMOS trades exibidos na tabela (fechados, ordenados)
    // Garante que Win Rate e Total Return batam com a List of trades / Cumulative P&L
    const closedTrades = useMemo(() => {
        return [...trades]
            .filter((t: any) => t.exit_time && t.exit_price)
            .sort((a: any, b: any) => new Date(a.entry_time).getTime() - new Date(b.entry_time).getTime())
    }, [trades])

    const derivedMetrics = useMemo(() => {
        if (closedTrades.length === 0) return null
        const initialCapital = 100
        let equity = initialCapital
        let wins = 0
        for (const t of closedTrades) {
            const p = (t as any).profit ?? 0
            if (p > 0) wins++
            equity *= 1 + p
        }
        const totalReturnPct = (equity / initialCapital - 1) * 100
        return {
            total_trades: closedTrades.length,
            win_rate: wins / closedTrades.length,
            total_return: totalReturnPct / 100,
            avg_profit: totalReturnPct / 100 / closedTrades.length
        }
    }, [closedTrades])

    if (!result) {
        return (
            <div className="app-page combo-page flex min-h-[50vh] items-center justify-center">
                <div className="text-center">
                    <p className="text-red-400">Nenhum resultado encontrado.</p>
                    <button onClick={() => navigate('/combo/select')} className="mt-4 text-blue-400">
                        ← Voltar aos modelos
                    </button>
                </div>
            </div>
        )
    }

    const direction = ((result as any).direction ?? result.parameters?.direction ?? strategyTransparency?.direction ?? 'long').toString().toLowerCase()
    const isShort = direction === 'short'
    // Usar métricas derivadas quando há trades; senão fallback para backend
    const baseMetrics = result.metrics || (result as any).best_metrics || {
        total_trades: 0,
        win_rate: 0,
        total_return: 0,
        avg_profit: 0
    }
    const metrics = derivedMetrics
        ? { ...baseMetrics, ...derivedMetrics }
        : baseMetrics

    const signalHistory = Array.isArray(result.signal_history) ? result.signal_history : []
    const markers = signalHistory.length > 0
        ? buildSignalHistoryMarkers(signalHistory, direction, undefined)
        : buildTradeMarkers(result.trades, { direction, timeframe: result.timeframe })

    const strategyName = result?.display_name
        || strategyTransparency?.display_name
        || result?.template_name
        || ''
    const strategyDescription = String(result?.strategy_description || strategyTransparency?.description || '').trim()
    const directionLabel = isShort ? 'Short / venda' : 'Long / compra'

    const formatMetricPercentage = (value: number | undefined, decimals = 1) => {
        if (value === undefined || value === null || Number.isNaN(value)) return 'Indisponível'
        const percentage = Math.abs(value) > 1 ? value : value * 100
        return `${percentage.toFixed(decimals)}%`
    }
    const summaryMetrics = [
        {
            label: 'Retorno total',
            value: formatMetricPercentage(metrics.total_return, 2),
            tone: Number(metrics.total_return) >= 0 ? 'text-[#0ecb81]' : 'text-[#f6465d]',
        },
        { label: 'Taxa de acerto', value: formatMetricPercentage(metrics.win_rate), tone: 'text-[#eaecef]' },
        { label: 'Drawdown máximo', value: formatMetricPercentage(metrics.max_drawdown), tone: 'text-[#eaecef]' },
        { label: 'Operações', value: String(metrics.total_trades ?? 0), tone: 'text-[#eaecef]' },
    ]

    return (
        <div className="app-page combo-page relative overflow-hidden">
            <main className="container mx-auto px-4 py-8 sm:px-6 sm:py-12">
                <div className="mx-auto max-w-7xl space-y-6 sm:space-y-8">
                    <div className="flex items-center justify-between gap-3">
                        <button
                            type="button"
                            onClick={handleBack}
                            className="inline-flex min-h-11 items-center gap-2 rounded-md border border-[#2b3139] bg-[#1e2329] px-4 py-2 text-sm font-semibold text-[#eaecef] transition-colors hover:bg-[#2b3139] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#3b82f6]"
                        >
                            <ArrowLeft className="h-4 w-4" />
                            {returnTo === '/favorites' ? 'Voltar aos favoritos' : 'Voltar'}
                        </button>
                        {isOptimization ? (
                            <button
                                type="button"
                                onClick={() => setIsModalOpen(true)}
                                className="inline-flex min-h-11 items-center gap-2 rounded-md bg-[#fcd535] px-4 py-2 text-sm font-semibold text-[#0b0e11] transition-colors hover:bg-[#fcd535]/90 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#3b82f6]"
                                data-testid="save-favorite-button"
                            >
                                <Star className="h-4 w-4" />
                                Salvar nos Favoritos
                            </button>
                        ) : null}
                    </div>

                    <section
                        className="min-w-0 overflow-hidden rounded-2xl border border-[#2b3139] bg-[#181a20] text-[#eaecef]"
                        aria-label="Análise da estratégia"
                        data-testid="combo-result-summary"
                    >
                        <div className="grid min-w-0 gap-6 p-5 sm:p-6 lg:grid-cols-[minmax(0,1.4fr)_minmax(360px,1fr)] lg:items-end">
                            <div className="min-w-0">
                                <div className="flex flex-wrap items-center gap-2 text-xs font-semibold">
                                    <span className="rounded-md border border-[#2b3139] bg-[#0b0e11] px-2.5 py-1.5">{result.symbol}</span>
                                    <span className="rounded-md border border-[#2b3139] bg-[#0b0e11] px-2.5 py-1.5 uppercase">{result.timeframe}</span>
                                    <span className="rounded-md border border-[#fcd535]/50 bg-[#fcd535]/10 px-2.5 py-1.5 text-[#fcd535]">{directionLabel}</span>
                                </div>
                                <div data-testid="combo-read-mode">
                                    <h1
                                        className="mt-4 break-words text-2xl font-bold leading-tight sm:text-3xl [overflow-wrap:anywhere]"
                                        data-testid="combo-result-title"
                                    >
                                        {strategyName}
                                    </h1>
                                    {strategyDescription ? (
                                        <p
                                            className="mt-3 max-w-3xl whitespace-normal break-words text-sm leading-6 text-[#b7bdc6] [overflow-wrap:anywhere]"
                                            data-testid="combo-result-description"
                                        >
                                            {strategyDescription}
                                        </p>
                                    ) : null}
                                </div>
                            </div>
                            <dl className="grid min-w-0 grid-cols-2 gap-x-4 gap-y-5 border-t border-[#2b3139] pt-5 sm:grid-cols-4 lg:grid-cols-2 lg:border-l lg:border-t-0 lg:pl-6 lg:pt-0" aria-label="Resumo de desempenho e risco">
                                {summaryMetrics.map((metric) => (
                                    <div key={metric.label} className="min-w-0">
                                        <dt className="text-xs text-[#929aa5]">{metric.label}</dt>
                                        <dd className={`mt-1 break-words font-mono text-xl font-semibold tabular-nums ${metric.tone}`}>{metric.value}</dd>
                                    </div>
                                ))}
                            </dl>
                        </div>
                    </section>

                    {(result.oos_verdict || result.oos_metrics) ? (
                        <section
                            className="min-w-0 overflow-hidden rounded-2xl border border-[#2b3139] bg-[#181a20] text-[#eaecef]"
                            aria-label="Comparativo treino vs holdout (walk-forward)"
                            data-testid="combo-result-oos-comparison"
                        >
                            <div className="flex flex-wrap items-center justify-between gap-3 border-b border-[#2b3139] px-5 py-4 sm:px-6">
                                <div>
                                    <h2 className="text-lg font-semibold">Treino vs Holdout</h2>
                                    <p className="mt-1 text-xs text-[#929aa5]">
                                        Validação walk-forward (card #470): parâmetros otimizados no treino, veredito no período de validação.
                                    </p>
                                </div>
                                <OosVerdictBadge verdict={result.oos_verdict} />
                            </div>
                            <OosMetricsTable
                                trainMetrics={metrics}
                                oosMetrics={result.oos_metrics}
                                verdict={result.oos_verdict}
                            />
                        </section>
                    ) : null}

                    <StrategyRuleOverview
                        id="combo-result-strategy-rules"
                        strategyTransparency={strategyTransparency}
                        direction={direction}
                        includeRisk
                    />

                    {/* CHART VISUALIZATION */}
                    {(result.candles && result.candles.length > 0) ? (
                        <MonitorAlignedCandlestickChart
                            candles={result.candles}
                            markers={markers as any}
                            strategyName={strategyTransparency?.display_name || result.template_name}
                            symbol={result.symbol}
                            timeframe={result.timeframe}
                            strategyTransparency={strategyTransparency}
                        />
                    ) : (
                        <div className="glass-strong rounded-[28px] p-8 text-center border border-zinc-200 mb-8">
                            <BarChart3 className="w-12 h-12 mx-auto text-zinc-500 mb-4 opacity-50" />
                            <p className="text-zinc-400">Dados do gráfico indisponíveis para esta execução.</p>
                        </div>
                    )}

                    <StrategyTransparencyPanel
                        id="combo-result-strategy-transparency"
                        strategyTransparency={strategyTransparency}
                        direction={direction}
                        timeframe={result.timeframe}
                        fallbackName={result.template_name}
                        showIdentity={false}
                        showRules={false}
                        defaultDetailsOpen={false}
                        detailsLabel="Detalhes técnicos"
                        fallbackParameters={result.parameters}
                    />

                    <StrategyTradesTable
                        trades={result.trades}
                        candles={result.candles}
                        direction={direction}
                        metrics={metrics}
                        onExport={handleExportTrades}
                        testId="result-trades"
                        showMetrics={false}
                    />

                    <p className="rounded-lg border border-[#2b3139] bg-[#181a20] px-4 py-3 text-xs leading-5 text-[#929aa5]">
                        Conteúdo educacional baseado em dados históricos. Resultados passados não garantem retornos futuros.
                    </p>

                </div>
            </main>

            {isOptimization ? (
                <SaveFavoriteModal
                    isOpen={isModalOpen}
                    onClose={() => setIsModalOpen(false)}
                    backtestResult={{
                        template_name: result.template_name,
                        symbol: result.symbol,
                        timeframe: result.timeframe,
                        start_date: result.start_date ?? null,
                        end_date: result.end_date ?? null,
                        period_type: result.period_type ?? null,
                        parameters: { ...(result.parameters || (result as any).best_parameters || {}), direction: isShort ? 'short' : 'long' },
                        metrics: metrics,
                        promotion_metrics: result.promotion_metrics ?? null,
                        oos_verdict: result.oos_verdict ?? null,
                        oos_metrics: result.oos_metrics ?? null,
                        oos_proof: result.oos_proof ?? null,
                        trades: (() => {
                            // Sort trades by entry time to ensure correct chronological order for balance calculation
                            const sortedTrades = [...result.trades].sort((a, b) =>
                                new Date(a.entry_time).getTime() - new Date(b.entry_time).getTime()
                            );

                            let currentBalance = 100; // Requirement: Start with $100

                            return sortedTrades.map(t => {
                                const initial_capital = currentBalance;
                                // profit is percentage (e.g., 0.05 for 5%)
                                const profitPct = t.profit || 0;
                                const profitAmount = initial_capital * profitPct;
                                const final_capital = initial_capital + profitAmount;

                                // Update balance for next trade
                                currentBalance = final_capital;

                                return {
                                    ...t,
                                    pnl_pct: profitPct,
                                    initial_capital: initial_capital,
                                    final_capital: final_capital,
                                    pnl: profitAmount, // PnL in dollars
                                    direction: isShort ? 'Short' : 'Long'
                                };
                            });
                        })()
                    }}
                    onSave={handleSaveFavorite}
                />
            ) : null}
        </div>
    )
}
