import { useLocation, useNavigate } from 'react-router-dom'
import { TrendingUp, TrendingDown, Activity, DollarSign, Target, BarChart3 } from 'lucide-react'
import { CandlestickChart } from '../components/CandlestickChart'

interface BacktestResult {
    template_name: string
    symbol: string
    timeframe: string
    parameters: Record<string, any>
    metrics: {
        total_trades: number
        win_rate: number
        total_return: number
        avg_profit: number
    }
    trades: Array<{
        entry_time: string
        entry_price: number
        exit_time?: string
        exit_price?: number
        profit?: number
        type?: string
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

    if (!result) {
        return (
            <div className="min-h-screen flex items-center justify-center">
                <div className="text-center">
                    <p className="text-red-400">No results found</p>
                    <button onClick={() => navigate('/combo/select')} className="mt-4 text-blue-400">
                        ← Back to templates
                    </button>
                </div>
            </div>
        )
    }

    // Handle both backtest and optimization results
    // Optimization results have best_metrics, backtest results have metrics
    const metrics = result.metrics || (result as any).best_metrics || {
        total_trades: 0,
        win_rate: 0,
        total_return: 0,
        avg_profit: 0
    }

    // Prepare Chart Data
    const markers = result.trades.flatMap(curr => {
        const list = []
        // Entry Marker
        list.push({
            time: curr.entry_time,
            position: 'belowBar',
            color: '#10b981',
            shape: 'arrowUp',
            text: 'BUY'
        })
        // Exit Marker
        if (curr.exit_time) {
            list.push({
                time: curr.exit_time,
                position: 'aboveBar',
                color: '#ef4444',
                shape: 'arrowDown',
                text: `SELL (${(curr.profit! * 100).toFixed(2)}%)`
            })
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
                                    <BarChart3 className="w-7 h-7 text-white" />
                                </div>
                            </div>
                            <div>
                                <h1 className="text-3xl font-bold gradient-text">Backtest Results</h1>
                                <p className="text-sm text-gray-400 mt-0.5">{result.template_name} - {result.symbol} {result.timeframe}</p>
                            </div>
                        </div>
                        <button
                            onClick={() => navigate('/combo/select')}
                            className="text-gray-400 hover:text-white transition-colors"
                        >
                            ← New Backtest
                        </button>
                    </div>
                </div>
            </header>

            {/* Main Content */}
            <main className="container mx-auto px-6 py-12">
                <div className="max-w-7xl mx-auto space-y-8">

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
                        <div className="glass-strong rounded-2xl p-8 text-center border border-white/10 mb-8">
                            <BarChart3 className="w-12 h-12 mx-auto text-gray-500 mb-4 opacity-50" />
                            <p className="text-gray-400">Chart data not available for this run.</p>
                        </div>
                    )}

                    {/* Metrics Cards */}
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                        {/* Total Trades */}
                        <div className="glass-strong rounded-xl p-6 border border-white/10">
                            <div className="flex items-center justify-between mb-3">
                                <div className="bg-blue-500/20 p-2 rounded-lg">
                                    <Activity className="w-5 h-5 text-blue-400" />
                                </div>
                                <span className="text-2xl font-bold text-white">{metrics.total_trades}</span>
                            </div>
                            <p className="text-sm text-gray-400">Total Trades</p>
                        </div>

                        {/* Win Rate */}
                        <div className="glass-strong rounded-xl p-6 border border-white/10">
                            <div className="flex items-center justify-between mb-3">
                                <div className="bg-green-500/20 p-2 rounded-lg">
                                    <Target className="w-5 h-5 text-green-400" />
                                </div>
                                <span className="text-2xl font-bold text-white">{(metrics.win_rate * 100).toFixed(1)}%</span>
                            </div>
                            <p className="text-sm text-gray-400">Win Rate</p>
                        </div>

                        {/* Total Return */}
                        <div className="glass-strong rounded-xl p-6 border border-white/10">
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
                            <p className="text-sm text-gray-400">Total Return</p>
                        </div>

                        {/* Avg Profit */}
                        <div className="glass-strong rounded-xl p-6 border border-white/10">
                            <div className="flex items-center justify-between mb-3">
                                <div className="bg-purple-500/20 p-2 rounded-lg">
                                    <DollarSign className="w-5 h-5 text-purple-400" />
                                </div>
                                <span className="text-2xl font-bold text-white">{(metrics.avg_profit * 100).toFixed(2)}%</span>
                            </div>
                            <p className="text-sm text-gray-400">Avg Profit</p>
                        </div>
                    </div>

                    {/* Trades Table */}
                    <div className="glass-strong rounded-2xl overflow-hidden border border-white/10">
                        <div className="p-6 border-b border-white/10">
                            <h2 className="text-xl font-bold text-white">Trade History</h2>
                        </div>
                        <div className="overflow-x-auto">
                            <table className="w-full">
                                <thead>
                                    <tr className="border-b border-white/10">
                                        <th className="px-6 py-4 text-left text-xs font-semibold text-gray-400 uppercase">Entry Time</th>
                                        <th className="px-6 py-4 text-left text-xs font-semibold text-gray-400 uppercase">Entry Price</th>
                                        <th className="px-6 py-4 text-left text-xs font-semibold text-gray-400 uppercase">Exit Time</th>
                                        <th className="px-6 py-4 text-left text-xs font-semibold text-gray-400 uppercase">Exit Price</th>
                                        <th className="px-6 py-4 text-left text-xs font-semibold text-gray-400 uppercase">Profit</th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-white/5">
                                    {result.trades.map((trade, i) => (
                                        <tr key={i} className="hover:bg-white/5 transition-colors">
                                            <td className="px-6 py-4 text-sm text-gray-300">{new Date(trade.entry_time).toLocaleString()}</td>
                                            <td className="px-6 py-4 text-sm text-white font-mono">${trade.entry_price.toFixed(2)}</td>
                                            <td className="px-6 py-4 text-sm text-gray-300">
                                                {trade.exit_time ? new Date(trade.exit_time).toLocaleString() : '-'}
                                            </td>
                                            <td className="px-6 py-4 text-sm text-white font-mono">
                                                {trade.exit_price ? `$${trade.exit_price.toFixed(2)}` : '-'}
                                            </td>
                                            <td className="px-6 py-4 text-sm">
                                                {trade.profit !== undefined ? (
                                                    <span className={`font-bold ${trade.profit >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                                                        {trade.profit >= 0 ? '+' : ''}{(trade.profit * 100).toFixed(2)}%
                                                    </span>
                                                ) : (
                                                    <span className="text-gray-500">Open</span>
                                                )}
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </div>

                    {/* Indicator Info */}
                    <div className="glass-strong rounded-2xl p-6 border border-white/10">
                        <h2 className="text-xl font-bold text-white mb-4">Indicators Used</h2>
                        <div className="flex flex-wrap gap-2">
                            {Object.keys(result.indicator_data).map((indicator) => (
                                <span key={indicator} className="px-3 py-1 bg-blue-500/20 text-blue-400 rounded-lg text-sm border border-blue-500/30">
                                    {indicator}
                                </span>
                            ))}
                        </div>
                    </div>
                </div>
            </main>
        </div>
    )
}
