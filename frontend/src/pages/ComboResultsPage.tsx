import { useLocation, useNavigate } from 'react-router-dom'
import { useState, useMemo } from 'react'
import { Activity, BarChart3, ArrowLeft } from 'lucide-react'
import { MonitorAlignedCandlestickChart } from '../components/MonitorAlignedCandlestickChart'
import { SaveFavoriteModal } from '../components/SaveFavoriteModal'
import { StrategyTradesTable } from '../components/charts/StrategyTradesTable'
import { API_BASE_URL } from '../lib/apiBase'
import { authFetch } from '@/lib/authFetch'
import { formatStrategyParameterLabel, formatStrategyParameterValue } from '@/lib/strategyParameters'

interface BacktestResult {
    template_name: string
    symbol: string
    timeframe: string
    execution_mode?: string
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
    candles: Array<{
        timestamp_utc: string
        open: number
        high: number
        low: number
        close: number
        volume: number
    }>
}

export function ComboResultsPage() {
    const location = useLocation()
    const navigate = useNavigate()
    const result = location.state?.result as BacktestResult
    const returnTo = location.state?.returnTo as string | undefined
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

            const result = await response.json()
            console.log('✅ Favorito salvo com sucesso:', result)
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
                
                const isShortExport = ((result as any).direction ?? result.parameters?.direction ?? 'long').toString().toLowerCase() === 'short';
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
                    <p className="text-red-400">No results found</p>
                    <button onClick={() => navigate('/combo/select')} className="mt-4 text-blue-400">
                        ← Back to templates
                    </button>
                </div>
            </div>
        )
    }

    const direction = ((result as any).direction ?? result.parameters?.direction ?? 'long').toString().toLowerCase()
    const isShort = direction === 'short'
    const isProtectedResult = Boolean(result.is_strategy_protected)

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

    // Prepare Chart Data (entry/exit invertidos para short: entrada = venda, saída = compra)
    const markers = result.trades.flatMap(curr => {
        const list = []
        if (isShort) {
            list.push({
                time: curr.entry_time,
                position: 'aboveBar',
                color: '#f97316',
                shape: 'arrowDown',
                text: 'SHORT'
            })
            if (curr.exit_time) {
                list.push({
                    time: curr.exit_time,
                    position: 'belowBar',
                    color: '#10b981',
                    shape: 'arrowUp',
                    text: `COVER (${(curr.profit! * 100).toFixed(2)}%)`
                })
            }
        } else {
            list.push({
                time: curr.entry_time,
                position: 'belowBar',
                color: '#10b981',
                shape: 'arrowUp',
                text: 'BUY'
            })
            if (curr.exit_time) {
                list.push({
                    time: curr.exit_time,
                    position: 'aboveBar',
                    color: '#ef4444',
                    shape: 'arrowDown',
                    text: `SELL (${(curr.profit! * 100).toFixed(2)}%)`
                })
            }
        }
        return list
    })

    return (
        <div className="app-page combo-page relative overflow-hidden">
            {/* Main Content */}
            <main className="container mx-auto px-6 py-12">
                <div className="max-w-7xl mx-auto space-y-8">
                    <div className="flex items-center justify-between gap-3">
                        <button
                            type="button"
                            onClick={handleBack}
                            className="inline-flex items-center gap-2 rounded-md border border-[#2b3139] bg-[#1e2329] px-4 py-2 text-sm font-semibold text-[#eaecef] transition-colors hover:bg-[#2b3139]"
                        >
                            <ArrowLeft className="h-4 w-4" />
                            {returnTo === '/favorites' ? 'Voltar aos favoritos' : 'Voltar'}
                        </button>
                    </div>

                    {/* Configuration Info */}
                    <div className="glass-strong rounded-[28px] p-6 border border-zinc-200">
                        <div className="flex items-center gap-3 mb-6">
                            <div className="bg-emerald-500/20 p-2.5 rounded-lg border border-emerald-600/30">
                                <Activity className="w-6 h-6 text-emerald-400" />
                            </div>
                            <div>
                                <h2 className="text-xl font-bold text-zinc-900 leading-none">Winning Configuration</h2>
                                <p className="text-sm text-emerald-400 mt-1 font-medium">Os parâmetros campeões escolhidos pelo algoritmo</p>
                            </div>
                        </div>

                        {isProtectedResult ? (
                            <div className="rounded-lg border border-[#2b3139] bg-[#1e2329] px-4 py-3 text-sm text-[#eaecef]">
                                Parâmetros técnicos protegidos para este perfil.
                            </div>
                        ) : (
                            <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4" data-testid="combo-result-parameters">
                                {Object.entries(result.parameters).map(([key, value]) => {
                                    // Skip internal keys if any
                                    if (key.startsWith('_')) return null;

                                    const formattedValue = formatStrategyParameterValue(key, value);

                                    return (
                                        <div key={key} className="bg-zinc-50 rounded-[16px] p-4 border border-zinc-100 hover:border-zinc-200 transition-colors group">
                                            <p className="text-xs text-zinc-400 uppercase tracking-wider font-bold mb-2 group-hover:text-blue-400 transition-colors">
                                                {formatStrategyParameterLabel(key)}
                                            </p>
                                            <div className="flex items-baseline gap-1">
                                                <span className="text-xl font-bold text-zinc-900 font-mono">
                                                    {formattedValue}
                                                </span>
                                            </div>
                                        </div>
                                    )
                                })}
                            </div>
                        )}
                    </div>

                    {/* CHART VISUALIZATION */}
                    {(result.candles && result.candles.length > 0) ? (
                        <MonitorAlignedCandlestickChart
                            candles={result.candles}
                            markers={markers as any}
                            strategyName={result.template_name}
                            symbol={result.symbol}
                            timeframe={result.timeframe}
                        />
                    ) : (
                        <div className="glass-strong rounded-[28px] p-8 text-center border border-zinc-200 mb-8">
                            <BarChart3 className="w-12 h-12 mx-auto text-zinc-500 mb-4 opacity-50" />
                            <p className="text-zinc-400">Chart data not available for this run.</p>
                        </div>
                    )}

                    <StrategyTradesTable
                        trades={result.trades}
                        candles={result.candles}
                        direction={direction}
                        metrics={metrics}
                        onExport={handleExportTrades}
                        testId="result-trades"
                    />

                </div>
            </main>

            {/* Save Favorite Modal */}
            <SaveFavoriteModal
                isOpen={isModalOpen}
                onClose={() => setIsModalOpen(false)}
                backtestResult={{
                    template_name: result.template_name,
                    symbol: result.symbol,
                    timeframe: result.timeframe,
                    parameters: { ...(result.parameters || (result as any).best_parameters || {}), direction: isShort ? 'short' : 'long' },
                    metrics: metrics,
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
        </div>
    )
}
