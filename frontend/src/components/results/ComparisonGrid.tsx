import { TrendingUp, TrendingDown, ArrowRight, Trophy } from 'lucide-react'

interface ComparisonGridProps {
    results: any[]
    onSelectStrategy: (strategyKey: string) => void
}

export function ComparisonGrid({ results, onSelectStrategy }: ComparisonGridProps) {
    // Sort by Net Profit (descending)
    const sortedResults = [...results].sort((a, b) => {
        const netA = (a.metrics.final_equity || 0) - 10000 // assuming 10k base, strictly we should use return
        const netB = (b.metrics.final_equity || 0) - 10000
        return netB - netA
    })

    const bestStrategy = sortedResults[0]

    return (
        <div className="glass rounded-2xl p-6 border border-white/10">
            <div className="flex items-center justify-between mb-6">
                <div>
                    <h2 className="text-2xl font-bold text-white mb-2">Strategy Comparison</h2>
                    <p className="text-gray-400">Ranked by Net Profit</p>
                </div>
            </div>

            <div className="overflow-x-auto">
                <table className="w-full">
                    <thead>
                        <tr className="border-b border-white/10">
                            <th className="px-6 py-4 text-left text-xs font-semibold text-gray-400 uppercase">Rank</th>
                            <th className="px-6 py-4 text-left text-xs font-semibold text-gray-400 uppercase">Strategy</th>
                            <th className="px-6 py-4 text-right text-xs font-semibold text-gray-400 uppercase">Net Profit</th>
                            <th className="px-6 py-4 text-right text-xs font-semibold text-gray-400 uppercase">Win Rate</th>
                            <th className="px-6 py-4 text-right text-xs font-semibold text-gray-400 uppercase">Max DD</th>
                            <th className="px-6 py-4 text-right text-xs font-semibold text-gray-400 uppercase">P. Factor</th>
                            <th className="px-6 py-4 text-right text-xs font-semibold text-gray-400 uppercase">Trades</th>
                            <th className="px-6 py-4 text-right text-xs font-semibold text-gray-400 uppercase">Action</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-white/5">
                        {sortedResults.map((res, index) => {
                            const isBest = index === 0
                            const profit = (res.metrics.total_return_pct || 0) * 100
                            const winRate = (res.metrics.win_rate || 0) * 100
                            const dd = (res.metrics.max_drawdown_pct || 0) * 100
                            const pf = res.metrics.profit_factor || 0

                            return (
                                <tr
                                    key={index}
                                    className={`hover:bg-white/5 transition-colors cursor-pointer group ${isBest ? 'bg-[var(--accent-primary)]/5' : ''}`}
                                    onClick={() => onSelectStrategy(res.strategyName)}
                                >
                                    <td className="px-6 py-4">
                                        <div className="flex items-center gap-2">
                                            <span className={`w-6 h-6 flex items-center justify-center rounded-full text-xs font-bold ${isBest ? 'bg-yellow-500/20 text-yellow-500' : 'bg-white/10 text-gray-400'
                                                }`}>
                                                {index + 1}
                                            </span>
                                            {isBest && <Trophy className="w-4 h-4 text-yellow-500" />}
                                        </div>
                                    </td>
                                    <td className="px-6 py-4">
                                        <span className={`font-semibold ${isBest ? 'text-yellow-400' : 'text-white'}`}>
                                            {res.strategyName.replace(/\(.*\)/, '')}
                                        </span>
                                        <span className="text-gray-500 text-xs ml-2">
                                            {res.metrics.timeframe}
                                        </span>
                                    </td>
                                    <td className="px-6 py-4 text-right">
                                        <div className={`font-mono font-semibold ${profit >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                                            {profit >= 0 ? '+' : ''}{profit.toFixed(2)}%
                                        </div>
                                    </td>
                                    <td className="px-6 py-4 text-right text-gray-300 font-mono">
                                        {winRate.toFixed(1)}%
                                    </td>
                                    <td className="px-6 py-4 text-right text-rose-400 font-mono">
                                        {dd.toFixed(2)}%
                                    </td>
                                    <td className="px-6 py-4 text-right text-gray-300 font-mono">
                                        {pf.toFixed(2)}
                                    </td>
                                    <td className="px-6 py-4 text-right text-gray-300 font-mono">
                                        {res.metrics.num_trades}
                                    </td>
                                    <td className="px-6 py-4 text-right">
                                        <button className="text-[var(--accent-primary)] opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-end gap-1 ml-auto">
                                            Details <ArrowRight className="w-4 h-4" />
                                        </button>
                                    </td>
                                </tr>
                            )
                        })}
                    </tbody>
                </table>
            </div>
        </div>
    )
}
