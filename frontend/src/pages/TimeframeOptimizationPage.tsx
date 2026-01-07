import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { Play, TrendingUp, Award, ChevronDown, ChevronRight } from 'lucide-react';

const SYMBOLS = ['BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'SOL/USDT', 'ADA/USDT'];
const TIMEFRAMES = ['5m', '15m', '30m', '1h', '2h', '4h', '1d'];

interface IndicatorMetadata {
    name: string;
    category: string;
}

interface TimeframeResult {
    timeframe: string;
    total_return: number;
    sharpe_ratio: number;
    max_drawdown: number;
    win_rate: number;
    total_trades: number;
    trades?: any[];  // Trade details for display
}

export const TimeframeOptimizationPage: React.FC = () => {
    const navigate = useNavigate();

    const [symbol, setSymbol] = useState('BTC/USDT');
    const [selectedIndicator, setSelectedIndicator] = useState<string>('');
    const [isOptimizing, setIsOptimizing] = useState(false);
    const [results, setResults] = useState<TimeframeResult[]>([]);
    const [bestTimeframe, setBestTimeframe] = useState<string | null>(null);
    const [selectedTimeframe, setSelectedTimeframe] = useState<string | null>(null);
    const [expandedTimeframe, setExpandedTimeframe] = useState<string | null>(null);
    const [fee, setFee] = useState(0.00075); // Default 0.075% (enabled)
    const [slippage, setSlippage] = useState(0); // Default 0% (disabled) for TradingView alignment

    // Fetch indicators
    const { data: indicators, isLoading: loadingIndicators } = useQuery({
        queryKey: ['indicators-metadata'],
        queryFn: async () => {
            const response = await fetch('http://127.0.0.1:8000/api/strategies/metadata');
            if (!response.ok) {
                return [
                    { name: 'rsi', category: 'Momentum' },
                    { name: 'macd', category: 'Trend' }
                ];
            }
            const data = await response.json();
            const flattened: IndicatorMetadata[] = [];
            Object.entries(data).forEach(([category, indicators]: [string, any]) => {
                if (Array.isArray(indicators)) {
                    indicators.forEach((indicator: any) => {
                        flattened.push({
                            name: indicator.id || indicator.name,
                            category
                        });
                    });
                }
            });
            return flattened.sort((a, b) => a.name.localeCompare(b.name));
        }
    });

    const handleStartOptimization = async () => {
        if (!selectedIndicator) return;

        setIsOptimizing(true);
        setResults([]);
        setBestTimeframe(null);
        setSelectedTimeframe(null);

        try {
            // Get indicator schema for default parameters
            const schemaResponse = await fetch(`http://127.0.0.1:8000/api/indicator/${selectedIndicator}/schema`);
            const schema = await schemaResponse.json();

            const defaultParams: any = {};
            if (schema.parameters) {
                Object.entries(schema.parameters).forEach(([key, param]: [string, any]) => {
                    defaultParams[key] = param.default;
                });
            }

            // Start timeframe optimization
            const response = await fetch('http://127.0.0.1:8000/api/optimize/sequential/timeframe', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    symbol,
                    strategy: selectedIndicator,
                    fee,
                    slippage,
                    timeframes: TIMEFRAMES,
                    parameters: defaultParams
                })
            });

            const data = await response.json();

            console.log('Optimization response:', data);

            // Process results directly from HTTP response
            if (data.all_results && Array.isArray(data.all_results)) {
                // Map backend response to frontend format
                const mappedResults = data.all_results.map((result: any) => ({
                    timeframe: result.timeframe,
                    total_return: result.metrics?.total_return_pct || 0,
                    sharpe_ratio: result.metrics?.sharpe_ratio || 0,
                    max_drawdown: result.metrics?.max_drawdown || 0,
                    win_rate: result.metrics?.win_rate || 0,
                    total_trades: result.metrics?.total_trades || 0,
                    trades: result.trades || []
                }));

                setResults(mappedResults);
                setBestTimeframe(data.best_timeframe);
                setSelectedTimeframe(data.best_timeframe);
            }

            setIsOptimizing(false);

        } catch (error) {
            console.error('Optimization error:', error);
            setIsOptimizing(false);
        }
    };

    const handleOptimizeParameters = () => {
        if (!selectedTimeframe) return;
        navigate(`/optimize/parameters?timeframe=${selectedTimeframe}&symbol=${symbol}&strategy=${selectedIndicator}`);
    };

    return (
        <div className="min-h-screen font-sans p-6" style={{ backgroundColor: '#0B0E14', color: '#E2E8F0' }}>
            <div className="max-w-5xl mx-auto">

                {/* Header */}
                <div className="mb-8">
                    <h1 className="text-3xl font-bold mb-2" style={{ color: '#14b8a6' }}>
                        Timeframe Optimization
                    </h1>
                    <p className="text-gray-400">
                        Find the best timeframe for your strategy
                    </p>
                </div>

                {/* Input Form */}
                <div className="rounded-xl p-6 mb-6" style={{ backgroundColor: '#151922', border: '1px solid #2A2F3A' }}>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                        {/* Trading Pair */}
                        <div>
                            <label className="block text-white font-medium mb-2">Trading Pair</label>
                            <select
                                value={symbol}
                                onChange={(e) => setSymbol(e.target.value)}
                                className="w-full px-4 py-3 rounded-md border focus:outline-none focus:ring-1"
                                style={{
                                    backgroundColor: '#0B0E14',
                                    borderColor: '#14b8a6',
                                    color: '#E2E8F0'
                                }}
                            >
                                {SYMBOLS.map(s => (
                                    <option key={s} value={s}>{s}</option>
                                ))}
                            </select>
                        </div>

                        {/* Strategy */}
                        <div>
                            <label className="block text-white font-medium mb-2">Strategy / Indicator</label>
                            <select
                                value={selectedIndicator}
                                onChange={(e) => setSelectedIndicator(e.target.value)}
                                className="w-full px-4 py-3 rounded-md border focus:outline-none focus:ring-1"
                                style={{
                                    backgroundColor: '#0B0E14',
                                    borderColor: '#2D3748',
                                    color: '#E2E8F0'
                                }}
                                disabled={loadingIndicators}
                            >
                                <option value="">Select an indicator</option>
                                {indicators?.map(ind => (
                                    <option key={ind.name} value={ind.name}>
                                        {ind.name.toUpperCase()}
                                    </option>
                                ))}
                            </select>
                        </div>
                    </div>

                    {/* Advanced Options */}
                    <div className="mb-6 p-4 rounded-lg" style={{ backgroundColor: '#0B0E14', border: '1px solid #2A2F3A' }}>
                        <h3 className="text-white font-medium mb-3">Advanced Options</h3>
                        <div className="flex gap-6">
                            <label className="flex items-center gap-2 text-gray-300 cursor-pointer">
                                <input
                                    type="checkbox"
                                    checked={fee > 0}
                                    onChange={(e) => setFee(e.target.checked ? 0.00075 : 0)}
                                    className="w-4 h-4 rounded border-gray-600 text-teal-500 focus:ring-teal-500"
                                />
                                <span>Enable Trading Fees (0.075% - Binance)</span>
                            </label>
                            <label className="flex items-center gap-2 text-gray-300 cursor-pointer">
                                <input
                                    type="checkbox"
                                    checked={slippage > 0}
                                    onChange={(e) => setSlippage(e.target.checked ? 0.0005 : 0)}
                                    className="w-4 h-4 rounded border-gray-600 text-teal-500 focus:ring-teal-500"
                                />
                                <span>Enable Slippage (0.05%)</span>
                            </label>
                        </div>
                        <p className="text-xs text-gray-500 mt-2">
                            💡 Disable both for TradingView alignment (default)
                        </p>
                    </div>

                    {/* Start Button */}
                    <button
                        onClick={handleStartOptimization}
                        disabled={!selectedIndicator || isOptimizing}
                        className="flex items-center gap-3 px-6 py-3 rounded-md font-bold transition-all"
                        style={{
                            backgroundColor: selectedIndicator && !isOptimizing ? '#14b8a6' : '#1A202C',
                            color: selectedIndicator && !isOptimizing ? '#0B0E14' : '#4A5568',
                            cursor: selectedIndicator && !isOptimizing ? 'pointer' : 'not-allowed'
                        }}
                    >
                        <Play className="w-5 h-5" fill={selectedIndicator && !isOptimizing ? 'currentColor' : 'none'} />
                        {isOptimizing ? 'Optimizing...' : 'Start Timeframe Optimization'}
                    </button>
                </div>

                {/* Results */}
                {results.length > 0 && (
                    <div className="rounded-xl p-6" style={{ backgroundColor: '#151922', border: '1px solid #2A2F3A' }}>
                        <h2 className="text-xl font-bold mb-4 text-white">Results</h2>
                        <p className="text-sm text-gray-400 mb-4">Click on a row to select that timeframe.</p>

                        <div className="overflow-x-auto mb-6">
                            <table className="w-full text-sm">
                                <thead className="border-b" style={{ borderColor: '#2A2F3A' }}>
                                    <tr>
                                        <th className="text-left py-3 px-4 font-semibold text-gray-400">Timeframe</th>
                                        <th className="text-right py-3 px-4 font-semibold text-gray-400">Total Return</th>
                                        <th className="text-right py-3 px-4 font-semibold text-gray-400">Sharpe Ratio</th>
                                        <th className="text-right py-3 px-4 font-semibold text-gray-400">Win Rate</th>
                                        <th className="text-right py-3 px-4 font-semibold text-gray-400">Trades</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {results.map((result) => {
                                        const isBest = result.timeframe === bestTimeframe;
                                        const isSelected = result.timeframe === selectedTimeframe;
                                        const isExpanded = result.timeframe === expandedTimeframe;

                                        return (
                                            <React.Fragment key={result.timeframe}>
                                                <tr
                                                    onClick={() => setSelectedTimeframe(result.timeframe)}
                                                    className="border-b transition-colors cursor-pointer hover:bg-[#1A202C]"
                                                    style={{
                                                        borderColor: '#2A2F3A',
                                                        backgroundColor: isSelected ? '#14b8a6/20' : (isBest ? '#14b8a6/5' : 'transparent'),
                                                        borderLeft: isSelected ? '4px solid #14b8a6' : '4px solid transparent'
                                                    }}
                                                >
                                                    <td className="py-3 px-4 font-mono font-bold flex items-center gap-2" style={{ color: isSelected ? '#14b8a6' : '#E2E8F0' }}>
                                                        <button
                                                            onClick={(e) => {
                                                                e.stopPropagation();
                                                                setExpandedTimeframe(isExpanded ? null : result.timeframe);
                                                            }}
                                                            className="p-1 hover:bg-gray-700 rounded"
                                                        >
                                                            {isExpanded ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
                                                        </button>
                                                        {isBest && <Award className="inline w-4 h-4 mr-2" style={{ color: '#14b8a6' }} />}
                                                        {result.timeframe} {isSelected && !isBest && <span className="text-xs text-gray-500 ml-2">(Selected)</span>}
                                                    </td>
                                                    <td className="py-3 px-4 text-right font-mono" style={{ color: result.total_return >= 0 ? '#10B981' : '#EF4444' }}>
                                                        {result.total_return >= 0 ? '+' : ''}{(result.total_return * 100).toFixed(2)}%
                                                    </td>
                                                    <td className="py-3 px-4 text-right font-mono text-gray-300">
                                                        {result.sharpe_ratio.toFixed(2)}
                                                    </td>
                                                    <td className="py-3 px-4 text-right font-mono text-gray-300">
                                                        {(result.win_rate * 100).toFixed(1)}%
                                                    </td>
                                                    <td className="py-3 px-4 text-right font-mono text-gray-300">
                                                        {result.total_trades}
                                                    </td>
                                                </tr>
                                                {isExpanded && (
                                                    <tr>
                                                        <td colSpan={5} className="p-4 bg-[#0e1116] border-b border-[#2A2F3A]">
                                                            <div className="text-sm font-bold mb-2 text-gray-400">Trades List ({result.trades?.length || 0})</div>
                                                            <div className="max-h-60 overflow-y-auto">
                                                                <table className="w-full text-xs">
                                                                    <thead className="bg-[#1A202C] text-gray-400">
                                                                        <tr>
                                                                            <th className="p-2 text-left">Entry Time</th>
                                                                            <th className="p-2 text-left">Type</th>
                                                                            <th className="p-2 text-right">Entry Price</th>
                                                                            <th className="p-2 text-right">Exit Price</th>
                                                                            <th className="p-2 text-right">PnL</th>
                                                                            <th className="p-2 text-left">Reason</th>
                                                                            <th className="p-2 text-right">Exit Time</th>
                                                                        </tr>
                                                                    </thead>
                                                                    <tbody>
                                                                        {result.trades?.sort((a: any, b: any) => new Date(b.entry_time).getTime() - new Date(a.entry_time).getTime()).map((trade: any, idx: number) => (
                                                                            <tr key={idx} className="border-b border-[#2A2F3A] hover:bg-[#1A202C]/50">
                                                                                <td className="p-2 font-mono text-gray-300">{trade.entry_time?.substring(0, 16).replace('T', ' ')}</td>
                                                                                <td className={`p-2 font-bold ${trade.side === 'buy' || trade.side === 'long' ? 'text-green-500' : 'text-red-500'}`}>
                                                                                    {(trade.side || 'LONG').toUpperCase()}
                                                                                </td>
                                                                                <td className="p-2 text-right font-mono text-gray-300">{trade.entry_price?.toFixed(2)}</td>
                                                                                <td className="p-2 text-right font-mono text-gray-300">{trade.exit_price?.toFixed(2)}</td>
                                                                                <td className={`p-2 text-right font-mono font-bold ${(trade.pnl || trade.profit) >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                                                                                    {trade.pnl_pct ?
                                                                                        `${(trade.pnl_pct * 100).toFixed(2)}%` :
                                                                                        `$${(trade.pnl || trade.profit)?.toFixed(2)}`
                                                                                    }
                                                                                </td>
                                                                                <td className="p-2 font-mono text-gray-400">
                                                                                    <span className={`px-2 py-1 rounded text-xs ${trade.reason === 'Signal' ? 'bg-blue-900/30 text-blue-400' :
                                                                                        trade.reason === 'SL' ? 'bg-red-900/30 text-red-400' :
                                                                                            trade.reason === 'TP' ? 'bg-green-900/30 text-green-400' :
                                                                                                'bg-gray-900/30 text-gray-400'
                                                                                        }`}>
                                                                                        {trade.reason || 'N/A'}
                                                                                    </span>
                                                                                </td>
                                                                                <td className="p-2 text-right font-mono text-gray-300">{trade.exit_time?.substring(0, 16).replace('T', ' ')}</td>
                                                                            </tr>
                                                                        ))}
                                                                        {(!result.trades || result.trades.length === 0) && (
                                                                            <tr>
                                                                                <td colSpan={7} className="p-4 text-center text-gray-500">No trades recorded for this period.</td>
                                                                            </tr>
                                                                        )}
                                                                    </tbody>
                                                                </table>
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

                        {/* Best Timeframe Card */}
                        {bestTimeframe && (
                            <div className="rounded-lg p-6 mb-4" style={{ backgroundColor: '#14b8a6/10', border: '1px solid #14b8a6' }}>
                                <div className="flex items-center justify-between">
                                    <div>
                                        <div className="text-sm text-gray-400 mb-1">Best Timeframe Identified</div>
                                        <div className="text-3xl font-bold font-mono" style={{ color: '#14b8a6' }}>
                                            {bestTimeframe}
                                        </div>
                                    </div>
                                    <TrendingUp className="w-12 h-12" style={{ color: '#14b8a6' }} />
                                </div>
                            </div>
                        )}

                        {/* Navigate to Parameters */}
                        <button
                            onClick={handleOptimizeParameters}
                            disabled={!selectedTimeframe}
                            className="w-full py-3 rounded-md font-bold transition-all"
                            style={{
                                backgroundColor: selectedTimeframe ? '#14b8a6' : '#2D3748',
                                color: selectedTimeframe ? '#0B0E14' : '#718096',
                                cursor: selectedTimeframe ? 'pointer' : 'not-allowed'
                            }}
                        >
                            → Optimize Parameters with {selectedTimeframe || '...'}
                        </button>
                    </div>
                )}
            </div>
        </div>
    );
};
