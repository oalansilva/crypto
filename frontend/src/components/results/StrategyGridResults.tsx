import { Card } from '../ui'
import { TrendingUp, Award, BarChart3 } from 'lucide-react'

interface StrategyResult {
    strategy: string
    results: Array<{
        params: Record<string, any>
        metrics: {
            total_pnl: number
            total_pnl_pct: number
            win_rate: number
            total_trades: number
            max_drawdown: number
            profit_factor: number
        }
    }>
    best: {
        params: Record<string, any>
        metrics: {
            total_pnl: number
            total_pnl_pct: number
            win_rate: number
            total_trades: number
            max_drawdown: number
            profit_factor: number
        }
    }
    combinations_tested: number
}

interface StrategyGridResultsProps {
    strategies: StrategyResult[]
    overall_best: {
        strategy: string
        params: Record<string, any>
        metrics: {
            total_pnl: number
            total_pnl_pct: number
            win_rate: number
            total_trades: number
        }
    }
    onDrillDown?: (strategy: string) => void
}

function formatParamKey(key: string): string {
    return key.replace(/_/g, ' ').toUpperCase()
}

function formatParamValue(key: string, val: any): string {
    if (val === null || val === undefined) return 'N/A'
    if (typeof val === 'number') {
        if (key.toLowerCase().endsWith('pct') || key === 'stop_loss' || key === 'take_profit') {
            return `${(val * 100).toLocaleString('en-US', { maximumFractionDigits: 2 })}%`
        }
        return val.toLocaleString('en-US', { maximumFractionDigits: 2 })
    }
    return String(val)
}

export function StrategyGridResults({ strategies, overall_best, onDrillDown }: StrategyGridResultsProps) {
    // Sort strategies by best performance
    const sortedStrategies = [...strategies].sort((a, b) =>
        (b.best?.metrics?.total_pnl || 0) - (a.best?.metrics?.total_pnl || 0)
    )

    return (
        <div className="space-y-6 animate-fade-in">
            {/* Overall Winner Card */}
            <Card className="p-6 bg-gradient-to-br from-blue-600/10 to-purple-600/10 border-blue-500/30">
                <div className="flex items-start justify-between">
                    <div>
                        <div className="flex items-center gap-2 mb-2">
                            <Award className="w-6 h-6 text-yellow-400" />
                            <h3 className="text-xl font-bold text-white">Vencedor Geral</h3>
                        </div>
                        <p className="text-3xl font-bold text-[var(--accent-primary)] mb-2">
                            {overall_best.strategy.toUpperCase()}
                        </p>
                        <div className="flex items-baseline gap-4">
                            <div>
                                <span className="text-sm text-[var(--text-secondary)]">Retorno</span>
                                <p className="text-2xl font-bold text-white">
                                    {(overall_best.metrics.total_pnl_pct * 100).toFixed(2)}%
                                </p>
                            </div>
                            <div>
                                <span className="text-sm text-[var(--text-secondary)]">Lucro</span>
                                <p className="text-xl font-bold text-green-400">
                                    ${overall_best.metrics.total_pnl.toFixed(2)}
                                </p>
                            </div>
                            <div>
                                <span className="text-sm text-[var(--text-secondary)]">Win Rate</span>
                                <p className="text-xl font-bold text-white">
                                    {(overall_best.metrics.win_rate * 100).toFixed(1)}%
                                </p>
                            </div>
                        </div>
                    </div>
                    <TrendingUp className="w-12 h-12 text-green-400 opacity-50" />
                </div>

                {/* Best params */}
                <div className="mt-4 pt-4 border-t border-white/10">
                    <p className="text-xs text-[var(--text-tertiary)] uppercase tracking-wide mb-2">Melhores Parâmetros</p>
                    <div className="flex flex-wrap gap-2">
                        {Object.entries(overall_best.params).map(([key, val]) => (
                            <div key={key} className="bg-white/5 px-3 py-1 rounded-full">
                                <span className="text-xs text-[var(--text-tertiary)]">{formatParamKey(key)}: </span>
                                <span className="text-xs font-mono text-white">{formatParamValue(key, val)}</span>
                            </div>
                        ))}
                    </div>
                </div>
            </Card>

            {/* Strategy Comparison Grid */}
            <Card className="p-6">
                <div className="flex items-center gap-2 mb-6">
                    <BarChart3 className="w-5 h-5 text-blue-400" />
                    <h3 className="text-xl font-bold text-white">Comparação de Estratégias</h3>
                </div>

                <div className="space-y-3">
                    {sortedStrategies.map((strat, index) => {
                        const isWinner = strat.strategy === overall_best.strategy
                        const pnlPct = (strat.best?.metrics?.total_pnl_pct || 0) * 100
                        const pnl = strat.best?.metrics?.total_pnl || 0
                        const winRate = (strat.best?.metrics?.win_rate || 0) * 100

                        return (
                            <div
                                key={strat.strategy}
                                className={`p-4 rounded-lg border transition-all cursor-pointer hover:border-blue-500/50 ${isWinner
                                        ? 'bg-blue-600/10 border-blue-500/30'
                                        : 'bg-white/5 border-white/10'
                                    }`}
                                onClick={() => onDrillDown?.(strat.strategy)}
                            >
                                <div className="flex items-center justify-between">
                                    <div className="flex items-center gap-4">
                                        {/* Rank */}
                                        <div className={`w-8 h-8 rounded-full flex items-center justify-center font-bold ${index === 0 ? 'bg-yellow-500/20 text-yellow-400' :
                                                index === 1 ? 'bg-gray-400/20 text-gray-300' :
                                                    index === 2 ? 'bg-orange-500/20 text-orange-400' :
                                                        'bg-white/5 text-gray-400'
                                            }`}>
                                            {index === 0 ? '🥇' : index === 1 ? '🥈' : index === 2 ? '🥉' : `#${index + 1}`}
                                        </div>

                                        {/* Strategy Name */}
                                        <div>
                                            <p className="font-bold text-white text-lg">
                                                {strat.strategy.toUpperCase()}
                                            </p>
                                            <p className="text-xs text-[var(--text-tertiary)]">
                                                {strat.combinations_tested} combinações testadas
                                            </p>
                                        </div>
                                    </div>

                                    {/* Metrics */}
                                    <div className="flex items-center gap-6">
                                        <div className="text-right">
                                            <p className="text-xs text-[var(--text-secondary)]">Retorno</p>
                                            <p className={`text-lg font-bold ${pnlPct >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                                                {pnlPct.toFixed(2)}%
                                            </p>
                                        </div>
                                        <div className="text-right">
                                            <p className="text-xs text-[var(--text-secondary)]">Lucro</p>
                                            <p className={`text-lg font-bold ${pnl >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                                                ${pnl.toFixed(2)}
                                            </p>
                                        </div>
                                        <div className="text-right">
                                            <p className="text-xs text-[var(--text-secondary)]">Win Rate</p>
                                            <p className="text-lg font-bold text-white">
                                                {winRate.toFixed(1)}%
                                            </p>
                                        </div>
                                        <div className="text-right min-w-[60px]">
                                            <p className="text-xs text-[var(--text-secondary)]">Trades</p>
                                            <p className="text-lg font-bold text-white">
                                                {strat.best?.metrics?.total_trades || 0}
                                            </p>
                                        </div>
                                    </div>
                                </div>

                                {/* Best params preview */}
                                {strat.best?.params && Object.keys(strat.best.params).length > 0 && (
                                    <div className="mt-3 pt-3 border-t border-white/5">
                                        <div className="flex flex-wrap gap-2">
                                            {Object.entries(strat.best.params).slice(0, 4).map(([key, val]) => (
                                                <div key={key} className="bg-white/5 px-2 py-1 rounded text-xs">
                                                    <span className="text-[var(--text-tertiary)]">{formatParamKey(key)}: </span>
                                                    <span className="font-mono text-white">{formatParamValue(key, val)}</span>
                                                </div>
                                            ))}
                                            {Object.keys(strat.best.params).length > 4 && (
                                                <div className="text-xs text-[var(--text-tertiary)] px-2 py-1">
                                                    +{Object.keys(strat.best.params).length - 4} mais
                                                </div>
                                            )}
                                        </div>
                                    </div>
                                )}
                            </div>
                        )
                    })}
                </div>
            </Card>

            {/* Hint */}
            <div className="text-center text-sm text-[var(--text-tertiary)]">
                💡 Clique em uma estratégia para ver todas as combinações testadas
            </div>
        </div>
    )
}
