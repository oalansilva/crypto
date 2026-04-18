import { useLocation, useNavigate } from 'react-router-dom'
import { useState, useMemo } from 'react'
import { TrendingUp, TrendingDown, Activity, DollarSign, Target, BarChart3, Star, Download } from 'lucide-react'
import { CandlestickChart } from '../components/CandlestickChart'
import { SaveFavoriteModal } from '../components/SaveFavoriteModal'
import { API_BASE_URL } from '../lib/apiBase'
import { authFetch } from '@/lib/authFetch'

interface BacktestResult {
    template_name: string
    symbol: string
    timeframe: string
    execution_mode?: string
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
    const [isModalOpen, setIsModalOpen] = useState(false)
    const [saveSuccess, setSaveSuccess] = useState(false)

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

            setSaveSuccess(true)
            setTimeout(() => setSaveSuccess(false), 3000)
        } catch (err) {
            console.error('❌ Erro ao salvar favorito:', err)
            throw err
        }
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

    const trades = result?.trades ?? []

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

    // Prepare Indicators
    const indicators = Object.entries(result.indicator_data).map(([name, values], index) => {
        // Filter out None values and create data points
        const data = values.map((val, i) => {
            if (val === null || val === undefined) return null
            // Check if we have a matching candle timestamp
            if (!result.candles || !result.candles[i]) return null

            return {
                time: result.candles[i].timestamp_utc,
                value: val
            }
        }).filter(d => d !== null) as { time: string; value: number }[]

        const colors = ['#fbbf24', '#3b82f6', '#8b5cf6', '#ec4899', '#f97316']

        return {
            name: name,
            data: data,
            color: colors[index % colors.length]
        }
    })

    return (
        <div className="app-page combo-page relative overflow-hidden">
            {/* Main Content */}
            <main className="container mx-auto px-6 py-12">
                <div className="max-w-7xl mx-auto space-y-8">

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

                        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
                            {Object.entries(result.parameters).map(([key, value]) => {
                                // Skip internal keys if any
                                if (key.startsWith('_')) return null;

                                const isPercentage = key.includes('stop_loss') || key.includes('take_profit') || key.includes('pct');
                                const formattedValue = isPercentage && typeof value === 'number'
                                    ? `${(value * 100).toFixed(2)}%`
                                    : value;

                                return (
                                    <div key={key} className="bg-zinc-50 rounded-[16px] p-4 border border-zinc-100 hover:border-zinc-200 transition-colors group">
                                        <p className="text-xs text-zinc-400 uppercase tracking-wider font-bold mb-2 group-hover:text-blue-400 transition-colors">
                                            {key.replace(/_/g, ' ')}
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
                    </div>

                    {/* CHART VISUALIZATION */}
                    {(result.candles && result.candles.length > 0) ? (
                        <CandlestickChart
                            candles={result.candles}
                            markers={markers as any}
                            indicators={indicators}
                            strategyName={result.template_name}
                            color="#3b82f6"
                        />
                    ) : (
                        <div className="glass-strong rounded-[28px] p-8 text-center border border-zinc-200 mb-8">
                            <BarChart3 className="w-12 h-12 mx-auto text-zinc-500 mb-4 opacity-50" />
                            <p className="text-zinc-400">Chart data not available for this run.</p>
                        </div>
                    )}

                    {/* Metrics Cards */}
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                        {/* Total Trades */}
                        <div className="glass-strong rounded-[24px] p-6 border border-zinc-200">
                            <div className="flex items-center justify-between mb-3">
                                <div className="bg-blue-500/20 p-2 rounded-lg">
                                    <Activity className="w-5 h-5 text-blue-400" />
                                </div>
                                <span className="text-2xl font-bold text-zinc-900">{metrics.total_trades}</span>
                            </div>
                            <p className="text-sm text-zinc-400">Total Trades</p>
                        </div>

                        {/* Win Rate */}
                        <div className="glass-strong rounded-[24px] p-6 border border-zinc-200">
                            <div className="flex items-center justify-between mb-3">
                                <div className="bg-green-500/20 p-2 rounded-lg">
                                    <Target className="w-5 h-5 text-green-400" />
                                </div>
                                <span className="text-2xl font-bold text-zinc-900">{(metrics.win_rate * 100).toFixed(1)}%</span>
                            </div>
                            <p className="text-sm text-zinc-400">Win Rate</p>
                        </div>

                        {/* Total Return */}
                        <div className="glass-strong rounded-[24px] p-6 border border-zinc-200">
                            <div className="flex items-center justify-between mb-3">
                                <div className={`p-2 rounded-lg ${metrics.total_return >= 0 ? 'bg-emerald-500/20' : 'bg-rose-500/20'}`}>
                                    {metrics.total_return >= 0 ? (
                                        <TrendingUp className="w-5 h-5 text-emerald-400" />
                                    ) : (
                                        <TrendingDown className="w-5 h-5 text-rose-400" />
                                    )}
                                </div>
                                <span className={`text-2xl font-bold ${metrics.total_return >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                                    {(metrics.total_return * 100).toFixed(2)}%
                                </span>
                            </div>
                            <p className="text-sm text-zinc-400">Total Return</p>
                        </div>

                        {/* Avg Profit */}
                        <div className="glass-strong rounded-[24px] p-6 border border-zinc-200">
                            <div className="flex items-center justify-between mb-3">
                                <div className="bg-purple-500/20 p-2 rounded-lg">
                                    <DollarSign className="w-5 h-5 text-purple-400" />
                                </div>
                                <span className="text-2xl font-bold text-zinc-900">{(metrics.avg_profit * 100).toFixed(2)}%</span>
                            </div>
                            <p className="text-sm text-zinc-400">Avg Profit</p>
                        </div>
                    </div>

                    {/* Trades Table - TradingView Style */}
                    <div className="bg-zinc-900 rounded-[24px] overflow-hidden border border-zinc-200 shadow-sm">
                        <div className="p-4 border-b border-zinc-200 flex items-center justify-between bg-zinc-50">
                            <div className="flex items-center gap-4">
                                <button className="px-3 py-1.5 text-sm font-medium text-zinc-700 bg-zinc-900 border border-zinc-300 rounded-[12px] hover:bg-zinc-50">
                                    Metrics
                                </button>
                                <button className="px-3 py-1.5 text-sm font-medium text-white bg-zinc-900 border border-zinc-300 rounded-[12px] border-b-2 border-b-blue-600">
                                    List of trades
                                </button>
                            </div>
                            <div className="flex items-center gap-2">
                                <button className="p-2 text-zinc-600 hover:bg-zinc-100 rounded-[12px]">
                                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                                    </svg>
                                </button>
                                <button className="p-2 text-zinc-600 hover:bg-zinc-100 rounded-[12px]">
                                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                                    </svg>
                                </button>
                                <button className="p-2 text-zinc-600 hover:bg-zinc-100 rounded-[12px]">
                                    <Download className="w-4 h-4" />
                                </button>
                                <button
                                    onClick={handleExportTrades}
                                    className="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-zinc-900 rounded-[12px] text-sm font-medium transition-colors"
                                >
                                    Exportar para Excel
                                </button>
                            </div>
                        </div>
                        <div className="overflow-x-auto bg-zinc-900">
                            <table className="w-full text-sm">
                                <thead className="bg-zinc-50 border-b border-zinc-200">
                                    <tr>
                                        <th className="px-4 py-3 text-left text-xs font-semibold text-zinc-600 uppercase tracking-wider">
                                            Trade # <span className="text-zinc-400">↓</span>
                                        </th>
                                        <th className="px-4 py-3 text-left text-xs font-semibold text-zinc-600 uppercase tracking-wider">Type</th>
                                        <th className="px-4 py-3 text-left text-xs font-semibold text-zinc-600 uppercase tracking-wider">Date and time</th>
                                        <th className="px-4 py-3 text-left text-xs font-semibold text-zinc-600 uppercase tracking-wider">Signal</th>
                                        <th className="px-4 py-3 text-left text-xs font-semibold text-zinc-600 uppercase tracking-wider">Price</th>
                                        <th className="px-4 py-3 text-left text-xs font-semibold text-zinc-600 uppercase tracking-wider">Position size</th>
                                        <th className="px-4 py-3 text-left text-xs font-semibold text-zinc-600 uppercase tracking-wider">Net P&L</th>
                                        <th className="px-4 py-3 text-left text-xs font-semibold text-zinc-600 uppercase tracking-wider">Favorable excursion</th>
                                        <th className="px-4 py-3 text-left text-xs font-semibold text-zinc-600 uppercase tracking-wider">Adverse excursion</th>
                                        <th className="px-4 py-3 text-left text-xs font-semibold text-zinc-600 uppercase tracking-wider">Cumulative P&L</th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-slate-100">
                                    {(() => {
                                        // Preparar trades com cálculos
                                        const initialCapital = 100;
                                        
                                        // Primeiro, ordenar trades cronologicamente (mais antigos primeiro) para calcular cumulative
                                        const sortedTrades = [...result.trades]
                                            .filter(t => t.exit_time && t.exit_price)
                                            .sort((a, b) => new Date(a.entry_time).getTime() - new Date(b.entry_time).getTime());
                                        
                                        // Calcular cumulative P&L do mais antigo para o mais recente
                                        let runningEquity = initialCapital;
                                        const tradesWithCumulative = sortedTrades.map((trade, idx) => {
                                            // Determinar Signal Type (short: Vender/Cobrir; long: Comprar/Close)
                                            let signalType = (trade as any).signal_type || '';
                                            if (!signalType) {
                                                const exitReason = (trade as any).exit_reason || '';
                                                if (exitReason && exitReason.toLowerCase().includes('stop')) {
                                                    signalType = 'Stop';
                                                } else if (exitReason) {
                                                    signalType = isShort ? 'Cobrir' : 'Close entry(s) order...';
                                                } else {
                                                    signalType = (trade as any).entry_signal_type || (isShort ? 'Vender' : 'Comprar');
                                                }
                                            }
                                            
                                            // Calcular Position size baseado no equity atual (antes do trade)
                                            // Position size = quanto do ativo podemos comprar com o equity atual
                                            const positionSize = runningEquity / trade.entry_price;
                                            const positionValueUSD = runningEquity; // Valor em USD investido
                                            
                                            // Calcular Net P&L
                                            const profitPct = trade.profit || 0;
                                            const netPnlUSD = runningEquity * profitPct;
                                            const netPnlPct = profitPct * 100;
                                            
                                            // Calcular Favorable/Adverse excursion usando candles
                                            let favorableExcursionUSD = 0;
                                            let favorableExcursionPct = 0;
                                            let adverseExcursionUSD = 0;
                                            let adverseExcursionPct = 0;
                                            
                                            if (result.candles && trade.entry_time && trade.exit_time) {
                                                const entryDate = new Date(trade.entry_time);
                                                const exitDate = new Date(trade.exit_time);
                                                
                                                const relevantCandles = result.candles.filter(c => {
                                                    const candleDate = new Date(c.timestamp_utc);
                                                    return candleDate >= entryDate && candleDate <= exitDate;
                                                });
                                                
                                                if (relevantCandles.length > 0) {
                                                    // Favorable: máximo high durante o trade
                                                    const maxHigh = Math.max(...relevantCandles.map(c => c.high));
                                                    favorableExcursionUSD = (maxHigh - trade.entry_price) * positionSize;
                                                    favorableExcursionPct = ((maxHigh - trade.entry_price) / trade.entry_price) * 100;
                                                    
                                                    // Adverse: mínimo low durante o trade
                                                    const minLow = Math.min(...relevantCandles.map(c => c.low));
                                                    adverseExcursionUSD = (trade.entry_price - minLow) * positionSize;
                                                    adverseExcursionPct = ((trade.entry_price - minLow) / trade.entry_price) * 100;
                                                }
                                            }
                                            
                                            // Atualizar equity para próximo trade (compounding)
                                            runningEquity *= (1 + profitPct);
                                            
                                            return {
                                                ...trade,
                                                tradeNum: sortedTrades.length - idx, // Número do trade (mais recente = maior número)
                                                signalType,
                                                positionSize,
                                                positionValueUSD,
                                                netPnlUSD,
                                                netPnlPct,
                                                favorableExcursionUSD,
                                                favorableExcursionPct,
                                                adverseExcursionUSD,
                                                adverseExcursionPct,
                                                cumulativeEquity: runningEquity,
                                                cumulativePnlUSD: runningEquity - initialCapital,
                                                cumulativePnlPct: ((runningEquity / initialCapital) - 1) * 100
                                            };
                                        });
                                        
                                        // Reverter para mostrar mais recentes primeiro (estilo TradingView)
                                        return tradesWithCumulative.reverse().flatMap((trade) => {
                                            // Formatar data no estilo TradingView: "Mês DD, YYYY"
                                            const formatDate = (dateStr: string) => {
                                                const date = new Date(dateStr);
                                                const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
                                                return `${months[date.getUTCMonth()]} ${date.getUTCDate()}, ${date.getUTCFullYear()}`;
                                            };
                                            
                                            // Formatar preço com vírgulas e USDT
                                            const formatPrice = (price: number) => {
                                                return `${price.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} USDT`;
                                            };
                                            
                                            // Formatar USD e %
                                            const formatPnl = (usd: number, pct: number, isPositive: boolean) => {
                                                const color = isPositive ? 'text-green-600' : 'text-red-600';
                                                return (
                                                    <div>
                                                        <span className={color}>{isPositive ? '+' : ''}{usd.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} USD</span>
                                                        <span className={`ml-2 ${color}`}>, {isPositive ? '+' : ''}{pct.toFixed(2)}%</span>
                                                    </div>
                                                );
                                            };
                                            
                                            return [
                                                // Linha de Entry
                                                <tr key={`${trade.tradeNum}-entry`} className="hover:bg-zinc-50">
                                                    <td rowSpan={2} className="px-4 py-3 text-center border-r border-zinc-200">
                                                        <div className="font-medium text-white">{trade.tradeNum}</div>
                                                        <div className={`text-xs ${isShort ? 'text-orange-600' : 'text-zinc-500'}`}>{isShort ? 'Short' : 'Long'}</div>
                                                    </td>
                                                    <td className="px-4 py-2 text-zinc-700">Entry</td>
                                                    <td className="px-4 py-2 text-zinc-700">{formatDate(trade.entry_time)}</td>
                                                    <td className="px-4 py-2 text-zinc-700">{isShort ? 'Vender' : 'Comprar'}</td>
                                                    <td className="px-4 py-2 text-white font-medium">{formatPrice(trade.entry_price)}</td>
                                                    <td className="px-4 py-2 text-zinc-700">
                                                        <div>{trade.positionSize.toFixed(2)}</div>
                                                        <div className="text-xs text-zinc-500">{(trade.positionValueUSD / 1000).toFixed(2)} K USD</div>
                                                    </td>
                                                    <td colSpan={4} className="px-4 py-2"></td>
                                                </tr>,
                                                // Linha de Exit
                                                <tr key={`${trade.tradeNum}-exit`} className="hover:bg-zinc-50 border-b border-zinc-200">
                                                    <td className="px-4 py-2 text-zinc-700">Exit</td>
                                                    <td className="px-4 py-2 text-zinc-700">{formatDate(trade.exit_time!)}</td>
                                                    <td className="px-4 py-2 text-zinc-700">{trade.signalType}</td>
                                                    <td className="px-4 py-2 text-white font-medium">{formatPrice(trade.exit_price!)}</td>
                                                    <td className="px-4 py-2"></td>
                                                    <td className="px-4 py-2">
                                                        {formatPnl(trade.netPnlUSD, trade.netPnlPct, trade.netPnlUSD >= 0)}
                                                    </td>
                                                    <td className="px-4 py-2 text-zinc-700">
                                                        <div>{trade.favorableExcursionUSD.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} USD</div>
                                                        <div className="text-xs text-zinc-500">, {trade.favorableExcursionPct.toFixed(2)}%</div>
                                                    </td>
                                                    <td className="px-4 py-2 text-red-600">
                                                        <div>-{trade.adverseExcursionUSD.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} USD</div>
                                                        <div className="text-xs">, -{trade.adverseExcursionPct.toFixed(2)}%</div>
                                                    </td>
                                                    <td className="px-4 py-2 text-zinc-700">
                                                        <div>{trade.cumulativePnlUSD.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} USD</div>
                                                        <div className="text-xs text-zinc-500">, {trade.cumulativePnlPct.toFixed(2)}%</div>
                                                    </td>
                                                </tr>
                                            ];
                                        });
                                    })()}
                                </tbody>
                            </table>
                        </div>
                    </div>



                    {/* Indicator Info */}
                    <div className="glass-strong rounded-[28px] p-6 border border-zinc-200">
                        <h2 className="text-xl font-bold text-zinc-900 mb-4 opacity-80">Indicators Used</h2>
                        <div className="flex flex-wrap gap-2">
                            {Object.keys(result.indicator_data).map((indicator) => (
                                <span key={indicator} className="px-3 py-1 bg-blue-500/10 text-blue-400 rounded-lg text-sm border border-blue-500/20 opacity-70 hover:opacity-100 transition-opacity">
                                    {indicator}
                                </span>
                            ))}
                        </div>
                    </div>
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
