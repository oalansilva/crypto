import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { TrendingUp, Award, ArrowRight, ChevronDown, Trophy, Target } from 'lucide-react';
import SaveFavoriteButton from '../SaveFavoriteButton';

interface ParameterCombination {
    params: Record<string, any>;
    metrics: {
        total_pnl: number;
        sharpe_ratio: number;
        win_rate: number;
        total_trades: number;
        [key: string]: any;
    };
    trades?: any[];
}

interface ParameterOptimizationResultsProps {
    results: ParameterCombination[];
    bestCombination: Record<string, any>;
    symbol: string;
    strategy: string;
    timeframe: string;
}

const ParameterOptimizationResults: React.FC<ParameterOptimizationResultsProps> = ({
    results,
    bestCombination,
    symbol,
    strategy,
    timeframe
}) => {
    const navigate = useNavigate();
    const [expandedIndex, setExpandedIndex] = useState<number | null>(null);

    // Pagination state
    const [currentPage, setCurrentPage] = useState(1);
    const [pageSize, setPageSize] = useState(25);

    // Sort results by total_pnl descending
    const sortedResults = [...results].sort((a, b) =>
        b.metrics.total_pnl - a.metrics.total_pnl
    );

    // Pagination logic
    const totalResults = sortedResults.length;
    const totalPages = Math.ceil(totalResults / pageSize);
    const startIndex = (currentPage - 1) * pageSize;
    const endIndex = startIndex + pageSize;
    const displayedResults = sortedResults.slice(startIndex, endIndex);
    const bestResult = sortedResults[0];

    // Reset to page 1 if current page exceeds total pages
    if (currentPage > totalPages && totalPages > 0) {
        setCurrentPage(1);
    }

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
        let returnPct = 0;

        // Priority 1: Use Total Return Pct from Backend (it's a decimal, so * 100)
        // Check for total_return_pct or total_pnl_pct (alias)
        if ('total_return_pct' in result.metrics || 'total_pnl_pct' in result.metrics) {
            const rawVal = result.metrics.total_return_pct ?? result.metrics.total_pnl_pct;
            returnPct = extractNumber(rawVal) * 100;
        }
        // Priority 2: Recalculate from trades if metric missing
        else if (result.trades && result.trades.length > 0) {
            const firstTrade = result.trades[0];
            const lastTrade = result.trades[result.trades.length - 1];

            if (firstTrade?.initial_capital && lastTrade?.final_capital) {
                const initialCapital = firstTrade.initial_capital;
                const finalCapital = lastTrade.final_capital;
                returnPct = ((finalCapital - initialCapital) / initialCapital) * 100;
            }
        }
        // Priority 3: Fallback to total_pnl (likely absolute value, might look weird as %)
        else {
            returnPct = extractNumber(result.metrics.total_pnl);
        }

        return {
            ...result.metrics,
            pnl: returnPct,
            sharpe: extractNumber(result.metrics.sharpe_ratio),
            winRate: extractNumber(result.metrics.win_rate),
            trades: extractNumber(result.metrics.total_trades),
            total_return: returnPct,
            total_return_pct: returnPct,
            max_drawdown: extractNumber(result.metrics.max_drawdown),
            profit_factor: extractNumber(result.metrics.profit_factor),
            expectancy: extractNumber(result.metrics.expectancy),
            sortino: extractNumber(result.metrics.sortino_ratio),
            max_loss: extractNumber(result.metrics.max_loss),
            avg_atr: extractNumber(result.metrics.avg_atr),
            win_rate_bull: extractNumber(result.metrics.win_rate_bull),
            win_rate_bear: extractNumber(result.metrics.win_rate_bear),
            avg_adx: extractNumber(result.metrics.avg_adx)
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
                                                    {new Date(trade.entry_time).toLocaleString()}
                                                </td>
                                                <td className="px-4 py-3 whitespace-nowrap text-xs">
                                                    {new Date(trade.exit_time).toLocaleString()}
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

                    {/* Save Favorite Button */}
                    <div className="mt-4 flex justify-center">
                        <SaveFavoriteButton
                            config={{
                                symbol,
                                timeframe,
                                strategy_name: strategy,
                                parameters: bestCombination
                            }}
                            metrics={{
                                ...bestMetrics,
                                sortino: bestMetrics.sortino,
                                max_loss: bestMetrics.max_loss,
                                avg_atr: bestMetrics.avg_atr,
                                win_rate_bull: bestMetrics.win_rate_bull,
                                win_rate_bear: bestMetrics.win_rate_bear,
                                avg_adx: bestMetrics.avg_adx
                            }}
                            className="bg-purple-600/20 text-purple-300 hover:bg-purple-600/40 w-full justify-center"
                        />
                    </div>
                </div>

                {/* All Results */}
                {/* All Results Table */}
                <div className="bg-gray-800/50 backdrop-blur-sm rounded-2xl border border-gray-700 overflow-hidden">
                    <div className="p-6 border-b border-gray-700">
                        <div className="flex items-center justify-between flex-wrap gap-4">
                            <h2 className="text-xl font-bold text-white">All Results</h2>

                            {/* Pagination Controls - Top */}
                            <div className="flex items-center gap-4 text-sm">
                                {/* Results Counter */}
                                <span className="text-gray-400">
                                    Showing {startIndex + 1}-{Math.min(endIndex, totalResults)} of {totalResults}
                                </span>

                                {/* Page Size Selector */}
                                <select
                                    value={pageSize}
                                    onChange={(e) => {
                                        setPageSize(Number(e.target.value));
                                        setCurrentPage(1);
                                    }}
                                    className="px-3 py-1.5 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-teal-500"
                                >
                                    <option value={10}>10 per page</option>
                                    <option value={25}>25 per page</option>
                                    <option value={50}>50 per page</option>
                                    <option value={100}>100 per page</option>
                                    <option value={totalResults}>Show All</option>
                                </select>

                                {/* Page Navigation */}
                                {totalPages > 1 && (
                                    <div className="flex items-center gap-2">
                                        <button
                                            onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
                                            disabled={currentPage === 1}
                                            className="px-3 py-1.5 bg-gray-700 border border-gray-600 rounded-lg text-white disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-600 transition-colors"
                                        >
                                            Previous
                                        </button>
                                        <span className="text-gray-400">
                                            Page {currentPage} of {totalPages}
                                        </span>
                                        <button
                                            onClick={() => setCurrentPage(Math.min(totalPages, currentPage + 1))}
                                            disabled={currentPage === totalPages}
                                            className="px-3 py-1.5 bg-gray-700 border border-gray-600 rounded-lg text-white disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-600 transition-colors"
                                        >
                                            Next
                                        </button>
                                    </div>
                                )}
                            </div>
                        </div>
                    </div>

                    <div className="overflow-x-auto">
                        <table className="w-full text-left border-collapse">
                            <thead>
                                <tr className="bg-gray-900/50 text-gray-400 text-sm uppercase tracking-wider">
                                    <th className="p-4 font-medium border-b border-gray-700">Rank</th>
                                    <th className="p-4 font-medium border-b border-gray-700 w-1/3">Parameters</th>
                                    <th className="p-4 font-medium border-b border-gray-700 text-right">Return</th>
                                    <th className="p-4 font-medium border-b border-gray-700 text-right">Sharpe</th>
                                    <th className="p-4 font-medium border-b border-gray-700 text-right">Win Rate</th>
                                    <th className="p-4 font-medium border-b border-gray-700 text-right">Trades</th>
                                    <th className="p-4 font-medium border-b border-gray-700 text-center">Actions</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-gray-700/50 text-sm">
                                {displayedResults.map((result, idx) => {
                                    const metrics = getMetrics(result);
                                    const globalRank = startIndex + idx + 1; // Use global rank, not page-local
                                    const isPositive = metrics.pnl >= 0;
                                    const isExpanded = expandedIndex === idx;

                                    return (
                                        <React.Fragment key={idx}>
                                            <tr className={`hover:bg-gray-700/30 transition-colors ${globalRank === 1 ? 'bg-teal-500/10' : ''}`}>
                                                <td className="p-4">
                                                    <span className={`font-mono font-bold ${globalRank === 1 ? 'text-teal-400 flex items-center gap-1' : 'text-gray-500'}`}>
                                                        {globalRank === 1 && <Trophy className="w-3 h-3" />}
                                                        #{globalRank}
                                                    </span>
                                                </td>
                                                <td className="p-4 font-mono text-gray-300">
                                                    {formatParams(result.params)}
                                                </td>
                                                <td className={`p-4 text-right font-bold ${isPositive ? 'text-green-400' : 'text-red-400'}`}>
                                                    {isPositive ? '+' : ''}{metrics.pnl.toFixed(2)}%
                                                </td>
                                                <td className="p-4 text-right text-gray-300">
                                                    {metrics.sharpe.toFixed(2)}
                                                </td>
                                                <td className="p-4 text-right text-gray-300">
                                                    {formatWinRate(metrics.winRate)}
                                                </td>
                                                <td className="p-4 text-right text-gray-300">
                                                    {metrics.trades}
                                                </td>
                                                <td className="p-4 text-center">
                                                    {metrics.trades > 0 && (
                                                        <button
                                                            onClick={() => setExpandedIndex(isExpanded ? null : idx)}
                                                            className="p-2 hover:bg-teal-500/10 rounded-lg text-teal-400 transition-colors"
                                                            title={isExpanded ? "Hide Trades" : "Show Trades"}
                                                        >
                                                            <ChevronDown className={`w-4 h-4 transform transition-transform ${isExpanded ? 'rotate-180' : ''}`} />
                                                        </button>
                                                    )}

                                                    <SaveFavoriteButton
                                                        variant="icon"
                                                        config={{
                                                            symbol,
                                                            timeframe,
                                                            strategy_name: strategy,
                                                            parameters: result.params
                                                        }}
                                                        metrics={{
                                                            total_return_pct: metrics.pnl,
                                                            sharpe_ratio: metrics.sharpe,
                                                            win_rate: metrics.winRate,
                                                            total_trades: metrics.trades,
                                                            max_drawdown: metrics.max_drawdown,
                                                            profit_factor: metrics.profit_factor,
                                                            expectancy: metrics.expectancy,
                                                            sortino: metrics.sortino,
                                                            max_loss: metrics.max_loss,
                                                            avg_atr: metrics.avg_atr,
                                                            win_rate_bull: metrics.win_rate_bull,
                                                            win_rate_bear: metrics.win_rate_bear,
                                                            avg_adx: metrics.avg_adx
                                                        }}
                                                    />
                                                </td>
                                            </tr>
                                            {isExpanded && (
                                                <tr className="bg-gray-900/30">
                                                    <td colSpan={7} className="p-4 border-b border-gray-700/50 inset-shadow">
                                                        <div className="bg-gray-900 rounded-lg border border-gray-700 overflow-hidden">
                                                            {result.trades && result.trades.length > 0 ? (
                                                                <div className="overflow-x-auto max-h-96">
                                                                    <table className="w-full text-xs text-left text-gray-300">
                                                                        <thead className="bg-gray-800 text-gray-400 uppercase tracking-tight sticky top-0">
                                                                            <tr>
                                                                                <th className="px-4 py-2">Entry</th>
                                                                                <th className="px-4 py-2">Exit</th>
                                                                                <th className="px-4 py-2">Side</th>
                                                                                <th className="px-4 py-2 text-right">Price In</th>
                                                                                <th className="px-4 py-2 text-right">Price Out</th>
                                                                                <th className="px-4 py-2 text-right">P&L</th>
                                                                                <th className="px-4 py-2 text-right">P&L %</th>
                                                                            </tr>
                                                                        </thead>
                                                                        <tbody className="divide-y divide-gray-700">
                                                                            {result.trades.map((trade: any, tIdx: number) => (
                                                                                <tr key={tIdx} className="hover:bg-gray-800/50">
                                                                                    <td className="px-4 py-2 whitespace-nowrap text-gray-400">
                                                                                        {new Date(trade.entry_time).toLocaleString()}
                                                                                    </td>
                                                                                    <td className="px-4 py-2 whitespace-nowrap text-gray-400">
                                                                                        {new Date(trade.exit_time).toLocaleString()}
                                                                                    </td>
                                                                                    <td className="px-4 py-2">
                                                                                        <span className={`px-1.5 py-0.5 rounded text-[10px] uppercase font-bold ${trade.side === 'long' ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'}`}>
                                                                                            {trade.side}
                                                                                        </span>
                                                                                    </td>
                                                                                    <td className="px-4 py-2 text-right font-mono text-gray-400">
                                                                                        {trade.entry_price?.toFixed(2)}
                                                                                    </td>
                                                                                    <td className="px-4 py-2 text-right font-mono text-gray-400">
                                                                                        {trade.exit_price?.toFixed(2)}
                                                                                    </td>
                                                                                    <td className={`px-4 py-2 text-right font-bold ${trade.pnl >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                                                                                        {trade.pnl?.toFixed(2)}
                                                                                    </td>
                                                                                    <td className={`px-4 py-2 text-right font-bold ${trade.pnl_pct >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                                                                                        {(trade.pnl_pct * 100)?.toFixed(2)}%
                                                                                    </td>
                                                                                </tr>
                                                                            ))}
                                                                        </tbody>
                                                                    </table>
                                                                </div>
                                                            ) : (
                                                                <div className="p-8 text-center text-gray-500 italic">
                                                                    No trade details available for this result.
                                                                </div>
                                                            )}
                                                        </div>
                                                    </td>
                                                </tr>
                                            )}
                                        </React.Fragment>
                                    );
                                })}
                            </tbody>
                        </table>
                    </div>

                    {/* Pagination Controls - Bottom */}
                    {totalPages > 1 && (
                        <div className="p-4 border-t border-gray-700 flex items-center justify-center gap-2">
                            <button
                                onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
                                disabled={currentPage === 1}
                                className="px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-600 transition-colors"
                            >
                                Previous
                            </button>
                            <span className="text-gray-400 px-4">
                                Page {currentPage} of {totalPages}
                            </span>
                            <button
                                onClick={() => setCurrentPage(Math.min(totalPages, currentPage + 1))}
                                disabled={currentPage === totalPages}
                                className="px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-600 transition-colors"
                            >
                                Next
                            </button>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default ParameterOptimizationResults;
