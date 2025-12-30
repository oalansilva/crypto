import { CandlestickChart } from '../CandlestickChart'
import { TradesTable } from '../TradesTable'
import { ArrowLeft } from 'lucide-react'

interface StrategyDetailProps {
    data: any
    candles: any[]
    onBack: () => void
}

export function StrategyDetail({ data, candles, onBack }: StrategyDetailProps) {
    const { strategyName, result } = data
    const color = '#2196F3' // Could map colors dynamically?

    return (
        <div className="animate-fade-in space-y-6">
            <button
                onClick={onBack}
                className="flex items-center gap-2 text-gray-400 hover:text-white transition-colors mb-4 group"
            >
                <div className="p-2 rounded-full bg-white/5 group-hover:bg-white/10 transition-colors">
                    <ArrowLeft className="w-5 h-5" />
                </div>
                <span className="font-semibold">Back to Comparison</span>
            </button>

            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-3xl font-bold text-white flex items-center gap-3">
                        <div className="w-3 h-8 rounded-full bg-[var(--accent-primary)]" />
                        {strategyName}
                    </h2>
                    <div className="flex gap-4 mt-2 text-sm text-[var(--text-secondary)]">
                        <span>Win Rate: <span className="text-white font-mono">{(result.metrics.win_rate * 100).toFixed(1)}%</span></span>
                        <span>PF: <span className="text-white font-mono">{result.metrics.profit_factor.toFixed(2)}</span></span>
                        <span>Sharpe: <span className="text-white font-mono">{result.metrics.sharpe.toFixed(2)}</span></span>
                    </div>
                </div>
                <div className="text-right">
                    <p className="text-gray-400 text-sm">Net Profit</p>
                    <p className={`text-3xl font-bold font-mono ${result.metrics.total_return_pct >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                        {result.metrics.total_return_pct >= 0 ? '+' : ''}{(result.metrics.total_return_pct * 100).toFixed(2)}%
                    </p>
                </div>
            </div>

            {/* Charts Section */}
            <div className="glass p-6 rounded-2xl border border-white/10">
                <h3 className="text-lg font-bold text-white mb-4">Price Action & Signals</h3>
                <div className="h-[500px]">
                    <CandlestickChart
                        candles={candles}
                        markers={result.markers}
                        indicators={result.indicators}
                        strategyName={strategyName}
                        color={color}
                    />
                </div>
            </div>

            {/* Trades Table */}
            <TradesTable
                trades={result.trades}
                strategyName={strategyName}
                color={color}
            />
        </div>
    )
}
