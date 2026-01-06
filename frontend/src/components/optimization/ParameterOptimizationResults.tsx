import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { TrendingUp, TrendingDown, Award, ArrowRight, ChevronDown, Trophy, Target } from 'lucide-react';

interface ParameterCombination {
    params: Record<string, any>;
    metrics: {
        total_pnl: number;
        sharpe_ratio: number;
        win_rate: number;
        total_trades: number;
    };
    trades?: any[];
}

interface ParameterOptimizationResultsProps {
    results: ParameterCombination[];
    bestCombination: Record<string, any>;
    symbol: string;
    strategy: string;
}

const ParameterOptimizationResults: React.FC<ParameterOptimizationResultsProps> = ({
    results,
    bestCombination,
    symbol,
    strategy
}) => {
    const navigate = useNavigate();
    const [expandedIndex, setExpandedIndex] = useState<number | null>(null);

    // Sort results by total_pnl descending
    const sortedResults = [...results].sort((a, b) =>
        b.metrics.total_pnl - a.metrics.total_pnl
    );

    // Show all results (excluding the best one which is shown in hero card)
    const displayedResults = sortedResults.slice(1);
    const bestResult = sortedResults[0];

    // Helper to safely extract numeric values
    const extractNumber = (value: any): number => {
        if (typeof value === 'number') return value;
        if (typeof value === 'string') return parseFloat(value) || 0;
        if (typeof value === 'object' && value !== null) {
            // Try to extract from common metric object structures
            if ('value' in value) return extractNumber(value.value);
            if ('total_return_pct' in value) return extractNumber(value.total_return_pct);
        }
        return 0;
    };

    // Format parameter value for display
    const formatParamValue = (value: any): string => {
        // Debug: log the actual value structure
        console.log('formatParamValue called with:', value, 'type:', typeof value);

        if (value === null || value === undefined) return 'N/A';
        if (typeof value === 'number') return value.toString();
        if (typeof value === 'string') return value;
        if (typeof value === 'boolean') return value ? 'Yes' : 'No';

        // For objects, try to extract meaningful value
        if (typeof value === 'object') {
            console.log('Object detected, keys:', Object.keys(value));

            // SPECIAL CASE: If this object looks like a full backtest result
            // (has metrics, trades, etc.), it means the backend returned the wrong structure
            // In this case, we can't extract a parameter value, so return 'N/A'
            if ('metrics' in value && 'trades' in value) {
                console.error('⚠️ Backend returned full backtest result as parameter value - this is a backend bug');
                return 'N/A';
            }

            // Common patterns in backend responses
            if ('value' in value) return formatParamValue(value.value);
            if ('min' in value && 'max' in value) return `${value.min}-${value.max}`;

            // If it's an array, join values
            if (Array.isArray(value)) return value.join(', ');

            // If object has a single key, use its value
            const keys = Object.keys(value);
            if (keys.length === 1) return formatParamValue(value[keys[0]]);

            // Last resort: try to find any numeric or string value
            for (const key of keys) {
                const val = value[key];
                if (typeof val === 'number' || typeof val === 'string') {
                    console.log(`Found value in key '${key}':`, val);
                    return String(val);
                }
            }
        }

        // Absolute fallback
        console.warn('Could not format value, using String():', value);
        return String(value);
    };

    // Format parameters as readable string
    const formatParams = (params: Record<string, any>): string => {
        console.log('formatParams called with:', params);
        console.log('formatParams JSON:', JSON.stringify(params, null, 2));

        return Object.entries(params)
            .map(([key, value]) => {
                const formatted = formatParamValue(value);
                return `${key}=${formatted}`;
            })
            .join(', ');
    };

    // Extract metrics safely
    const getMetrics = (result: ParameterCombination) => {
        // Calculate return percentage from trades if available
        let returnPct = extractNumber(result.metrics.total_pnl);

        if (result.trades && result.trades.length > 0) {
            const firstTrade = result.trades[0];
            const lastTrade = result.trades[result.trades.length - 1];

            if (firstTrade?.initial_capital && lastTrade?.final_capital) {
                const initialCapital = firstTrade.initial_capital;
                const finalCapital = lastTrade.final_capital;
                returnPct = ((finalCapital - initialCapital) / initialCapital) * 100;
            }
        }

        return {
            pnl: returnPct,
            sharpe: extractNumber(result.metrics.sharpe_ratio),
            winRate: extractNumber(result.metrics.win_rate),
            trades: extractNumber(result.metrics.total_trades)
        };
    };

    // Fix Win Rate display
    const formatWinRate = (winRate: number): string => {
        const correctedRate = winRate > 1 ? winRate / 100 : winRate;
        return `${(correctedRate * 100).toFixed(1)}%`;
    };

    const handleContinue = () => {
        const params = new URLSearchParams({
            symbol,
            strategy,
            ...bestCombination
        });
        navigate(`/optimize/risk?${params.toString()}`);
    };

    const bestMetrics = getMetrics(bestResult);

    return (
        <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 p-8">
            <div className="max-w-5xl mx-auto space-y-6">

                {/* Header */}
                <div className="text-center">
                    <div className="inline-flex items-center gap-2 px-4 py-2 bg-teal-500/10 border border-teal-500/30 rounded-full mb-4">
                        <Trophy className="w-5 h-5 text-teal-400" />
                        <span className="text-teal-400 font-semibold">Optimization Complete</span>
                    </div>
                    <h1 className="text-4xl font-bold text-white mb-2">
                        {strategy.toUpperCase()} on {symbol}
                    </h1>
                    <p className="text-gray-400 text-lg">
                        Tested {results.length} combinations • Found optimal parameters
                    </p>
                </div>

                {/* Best Result - Hero Card */}
                <div className="bg-gradient-to-br from-teal-900/40 via-emerald-900/30 to-teal-900/40 backdrop-blur-sm rounded-2xl border-2 border-teal-500/50 p-8 shadow-2xl">
                    <div className="flex items-start justify-between mb-6">
                        <div className="flex items-center gap-3">
                            <div className="w-12 h-12 bg-gradient-to-br from-yellow-400 to-yellow-600 rounded-full flex items-center justify-center shadow-lg">
                                <Award className="w-7 h-7 text-gray-900" />
                            </div>
                            <div>
                                <h2 className="text-2xl font-bold text-white">Best Result</h2>
                                <p className="text-teal-300 text-sm">Highest performing combination</p>
                            </div>
                        </div>
                        <div className="text-5xl">🏆</div>
                    </div>

                    {/* Parameters */}
                    <div className="bg-gray-900/50 rounded-xl p-4 mb-6">
                        <div className="text-xs text-gray-400 uppercase tracking-wider mb-2">Parameters</div>
                        <div className="text-xl font-mono font-bold text-teal-400">
                            {formatParams(bestCombination)}
                        </div>
                    </div>

                    {/* Metrics Grid */}
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                        <div className="bg-gray-900/50 rounded-xl p-4">
                            <div className="flex items-center gap-2 mb-2">
                                <TrendingUp className="w-4 h-4 text-green-400" />
                                <span className="text-xs text-gray-400 uppercase">Return</span>
                            </div>
                            <div className={`text-2xl font-bold ${bestMetrics.pnl >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                                {bestMetrics.pnl >= 0 ? '+' : ''}{bestMetrics.pnl.toFixed(2)}%
                            </div>
                        </div>

                        <div className="bg-gray-900/50 rounded-xl p-4">
                            <div className="flex items-center gap-2 mb-2">
                                <Target className="w-4 h-4 text-blue-400" />
                                <span className="text-xs text-gray-400 uppercase">Sharpe</span>
                            </div>
                            <div className="text-2xl font-bold text-white">
                                {bestMetrics.sharpe.toFixed(2)}
                            </div>
                        </div>

                        <div className="bg-gray-900/50 rounded-xl p-4">
                            <div className="flex items-center gap-2 mb-2">
                                <span className="text-lg">✓</span>
                                <span className="text-xs text-gray-400 uppercase">Win Rate</span>
                            </div>
                            <div className="text-2xl font-bold text-white">
                                {formatWinRate(bestMetrics.winRate)}
                            </div>
                        </div>

                        <div className="bg-gray-900/50 rounded-xl p-4">
                            <div className="flex items-center gap-2 mb-2">
                                <span className="text-lg">🔄</span>
                                <span className="text-xs text-gray-400 uppercase">Trades</span>
                            </div>
                            <div className="text-2xl font-bold text-white">
                                {bestMetrics.trades}
                            </div>
                        </div>
                    </div>

                    {/* View Trades Button */}
                    {bestMetrics.trades > 0 && (
                        <button
                            onClick={() => {
                                console.log("Toggling expanded for best result, current:", expandedIndex);
                                setExpandedIndex(expandedIndex === -1 ? null : -1);
                            }}
                            className="w-full flex items-center justify-center gap-2 mb-4 px-4 py-3 text-sm text-teal-400 hover:text-teal-300 bg-teal-500/10 hover:bg-teal-500/20 border border-teal-500/30 rounded-lg transition-all"
                        >
                            {expandedIndex === -1 ? 'Hide Trades' : 'View Trades'}
                            <ChevronDown className={`w-4 h-4 transform transition-transform ${expandedIndex === -1 ? 'rotate-180' : ''}`} />
                        </button>
                    )}

                    {/* Best Result Trades Table */}
                    {expandedIndex === -1 && (
                        <div className="mt-4 mb-4 overflow-x-auto bg-gray-900/50 rounded-lg p-4">
                            {bestResult.trades && bestResult.trades.length > 0 ? (
                                <table className="w-full text-sm text-left text-gray-300">
                                    <thead className="text-xs uppercase bg-gray-800/50">
                                        <tr>
                                            <th className="px-4 py-3">Entry</th>
                                            <th className="px-4 py-3">Exit</th>
                                            <th className="px-4 py-3">Side</th>
                                            <th className="px-4 py-3 text-right">Entry Price</th>
                                            <th className="px-4 py-3 text-right">Exit Price</th>
                                            <th className="px-4 py-3 text-right">Initial Capital</th>
                                            <th className="px-4 py-3 text-right">Final Capital</th>
                                            <th className="px-4 py-3 text-right">P&L</th>
                                            <th className="px-4 py-3 text-right">P&L %</th>
                                        </tr>
                                    </thead>
                                    <tbody className="divide-y divide-gray-700/50">
                                        {bestResult.trades.map((trade: any, tradeIdx: number) => (
                                            <tr key={tradeIdx} className="hover:bg-gray-800/30">
                                                <td className="px-4 py-3 whitespace-nowrap text-xs">
                                                    {new Date(trade.entry_time).toLocaleDateString()}
                                                </td>
                                                <td className="px-4 py-3 whitespace-nowrap text-xs">
                                                    {new Date(trade.exit_time).toLocaleDateString()}
                                                </td>
                                                <td className="px-4 py-3">
                                                    <span className={`px-2 py-1 rounded text-xs font-semibold ${trade.side === 'long' ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'}`}>
                                                        {trade.side?.toUpperCase() || 'N/A'}
                                                    </span>
                                                </td>
                                                <td className="px-4 py-3 text-right font-mono">
                                                    ${trade.entry_price?.toFixed(2) || 'N/A'}
                                                </td>
                                                <td className="px-4 py-3 text-right font-mono">
                                                    ${trade.exit_price?.toFixed(2) || 'N/A'}
                                                </td>
                                                <td className="px-4 py-3 text-right font-mono text-gray-400">
                                                    ${trade.initial_capital?.toFixed(2) || 'N/A'}
                                                </td>
                                                <td className="px-4 py-3 text-right font-mono text-gray-400">
                                                    ${trade.final_capital?.toFixed(2) || 'N/A'}
                                                </td>
                                                <td className={`px-4 py-3 text-right font-semibold ${trade.pnl >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                                                    {trade.pnl >= 0 ? '+' : ''}${trade.pnl?.toFixed(2) || 'N/A'}
                                                </td>
                                                <td className={`px-4 py-3 text-right font-semibold ${trade.pnl_pct >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                                                    {trade.pnl_pct >= 0 ? '+' : ''}{(trade.pnl_pct * 100)?.toFixed(2) || 'N/A'}%
                                                </td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            ) : (
                                <div className="text-center py-4 text-gray-400">
                                    No detailed trade data available for best result.
                                    <div className="text-xs text-gray-500 mt-1">(Trades list is empty or missing)</div>
                                </div>
                            )}
                        </div>
                    )}

                    {/* CTA Button */}
                    <button
                        onClick={handleContinue}
                        className="w-full flex items-center justify-center gap-2 px-6 py-4 bg-gradient-to-r from-teal-600 to-emerald-600 hover:from-teal-700 hover:to-emerald-700 text-white rounded-xl font-semibold text-lg transition-all transform hover:scale-[1.02] shadow-lg"
                    >
                        Continue to Risk Optimization
                        <ArrowRight className="w-5 h-5" />
                    </button>
                </div>

                {/* All Results */}
                <div className="bg-gray-800/50 backdrop-blur-sm rounded-2xl border border-gray-700 overflow-hidden">
                    <div className="p-6 border-b border-gray-700 flex items-center justify-between">
                        <h2 className="text-xl font-bold text-white">All Results</h2>
                    </div>

                    <div className="divide-y divide-gray-700/50">
                        {displayedResults.map((result, idx) => {
                            const metrics = getMetrics(result);
                            const rank = idx + 2; // +2 because best is #1 and we start from index 1
                            const isPositive = metrics.pnl >= 0;

                            return (
                                <div
                                    key={idx}
                                    className="p-6 hover:bg-gray-700/30 transition-colors"
                                >
                                    <div className="flex items-start gap-4">
                                        {/* Rank Badge */}
                                        <div className="flex-shrink-0 w-10 h-10 bg-gray-700 rounded-full flex items-center justify-center">
                                            <span className="text-gray-300 font-bold">#{rank}</span>
                                        </div>

                                        {/* Content */}
                                        <div className="flex-1 min-w-0">
                                            {/* Parameters */}
                                            <div className="font-mono text-sm text-gray-300 mb-3">
                                                {formatParams(result.params)}
                                            </div>

                                            {/* Metrics Row */}
                                            <div className="flex flex-wrap gap-4 text-sm">
                                                <div className="flex items-center gap-2">
                                                    {isPositive ? (
                                                        <TrendingUp className="w-4 h-4 text-green-400" />
                                                    ) : (
                                                        <TrendingDown className="w-4 h-4 text-red-400" />
                                                    )}
                                                    <span className="text-gray-400">Return:</span>
                                                    <span className={`font-bold ${isPositive ? 'text-green-400' : 'text-red-400'}`}>
                                                        {isPositive ? '+' : ''}{metrics.pnl.toFixed(2)}%
                                                    </span>
                                                </div>

                                                <div className="flex items-center gap-2">
                                                    <span className="text-gray-400">Sharpe:</span>
                                                    <span className="font-bold text-white">
                                                        {metrics.sharpe.toFixed(2)}
                                                    </span>
                                                </div>

                                                <div className="flex items-center gap-2">
                                                    <span className="text-gray-400">Win:</span>
                                                    <span className="font-bold text-white">
                                                        {formatWinRate(metrics.winRate)}
                                                    </span>
                                                </div>

                                                <div className="flex items-center gap-2">
                                                    <span className="text-gray-400">Trades:</span>
                                                    <span className="font-bold text-white">
                                                        {metrics.trades}
                                                    </span>
                                                </div>
                                            </div>

                                            {/* Show Trades Button */}
                                            {metrics.trades > 0 && (
                                                <button
                                                    onClick={() => setExpandedIndex(expandedIndex === idx ? null : idx)}
                                                    className="mt-4 text-sm text-teal-400 hover:text-teal-300 flex items-center gap-1 transition-colors"
                                                >
                                                    {expandedIndex === idx ? 'Hide Trades' : 'Show Trades'}
                                                    <ChevronDown className={`w-4 h-4 transition-transform ${expandedIndex === idx ? 'rotate-180' : ''}`} />
                                                </button>
                                            )}

                                            {/* Expanded Trades Table */}
                                            {expandedIndex === idx && (
                                                <div className="mt-4 overflow-x-auto bg-gray-900/50 rounded-lg p-4">
                                                    {result.trades && result.trades.length > 0 ? (
                                                        <table className="w-full text-sm text-left text-gray-300">
                                                            <thead className="text-xs uppercase bg-gray-800/50">
                                                                <tr>
                                                                    <th className="px-4 py-3">Entry</th>
                                                                    <th className="px-4 py-3">Exit</th>
                                                                    <th className="px-4 py-3">Side</th>
                                                                    <th className="px-4 py-3 text-right">Entry Price</th>
                                                                    <th className="px-4 py-3 text-right">Exit Price</th>
                                                                    <th className="px-4 py-3 text-right">Initial Capital</th>
                                                                    <th className="px-4 py-3 text-right">Final Capital</th>
                                                                    <th className="px-4 py-3 text-right">P&L</th>
                                                                    <th className="px-4 py-3 text-right">P&L %</th>
                                                                </tr>
                                                            </thead>
                                                            <tbody className="divide-y divide-gray-700/50">
                                                                {result.trades.map((trade: any, tradeIdx: number) => (
                                                                    <tr key={tradeIdx} className="hover:bg-gray-800/30">
                                                                        <td className="px-4 py-3 whitespace-nowrap text-xs">
                                                                            {new Date(trade.entry_time).toLocaleDateString()}
                                                                        </td>
                                                                        <td className="px-4 py-3 whitespace-nowrap text-xs">
                                                                            {new Date(trade.exit_time).toLocaleDateString()}
                                                                        </td>
                                                                        <td className="px-4 py-3">
                                                                            <span className={`px-2 py-1 rounded text-xs font-semibold ${trade.side === 'long' ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'}`}>
                                                                                {trade.side?.toUpperCase() || 'N/A'}
                                                                            </span>
                                                                        </td>
                                                                        <td className="px-4 py-3 text-right font-mono">
                                                                            ${trade.entry_price?.toFixed(2) || 'N/A'}
                                                                        </td>
                                                                        <td className="px-4 py-3 text-right font-mono">
                                                                            ${trade.exit_price?.toFixed(2) || 'N/A'}
                                                                        </td>
                                                                        <td className="px-4 py-3 text-right font-mono text-gray-400">
                                                                            ${trade.initial_capital?.toFixed(2) || 'N/A'}
                                                                        </td>
                                                                        <td className="px-4 py-3 text-right font-mono text-gray-400">
                                                                            ${trade.final_capital?.toFixed(2) || 'N/A'}
                                                                        </td>
                                                                        <td className={`px-4 py-3 text-right font-semibold ${trade.pnl >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                                                                            {trade.pnl >= 0 ? '+' : ''}${trade.pnl?.toFixed(2) || 'N/A'}
                                                                        </td>
                                                                        <td className={`px-4 py-3 text-right font-semibold ${trade.pnl_pct >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                                                                            {trade.pnl_pct >= 0 ? '+' : ''}{(trade.pnl_pct * 100)?.toFixed(2) || 'N/A'}%
                                                                        </td>
                                                                    </tr>
                                                                ))}
                                                            </tbody>
                                                        </table>
                                                    ) : (
                                                        <div className="text-center py-4 text-gray-400">
                                                            No detailed trades available.
                                                        </div>
                                                    )}
                                                </div>
                                            )}
                                        </div>
                                    </div>
                                </div>
                            );
                        })}
                    </div>

                </div>
            </div>
        </div>
    );
};

export default ParameterOptimizationResults;
