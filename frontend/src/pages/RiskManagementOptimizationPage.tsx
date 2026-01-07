import React, { useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { Play, Shield, Award, List, X, ArrowUp, ArrowDown } from 'lucide-react';

const SYMBOLS = ['BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'SOL/USDT', 'ADA/USDT'];
const TIMEFRAMES = ['5m', '15m', '30m', '1h', '2h', '4h', '1d'];
const STOP_GAIN_OPTIONS = [
    { value: null, label: 'None' },
    { value: 0.01, label: '1%' },
    { value: 0.02, label: '2%' },
    { value: 0.03, label: '3%' },
    { value: 0.04, label: '4%' },
    { value: 0.05, label: '5%' },
    { value: 0.075, label: '7.5%' },
    { value: 0.10, label: '10%' }
];

interface IndicatorMetadata {
    name: string;
    category: string;
}

interface Trade {
    entry_time: string;
    exit_time: string;
    entry_price: number;
    exit_price: number;
    pnl: number;
    pnl_pct: number;
    direction: string;
    size: number;
    type: string; // 'Limit', 'Market', etc. (if available)
    initial_capital?: number; // Added
    final_capital?: number; // Added
    entry_reason?: string;
    exit_reason?: string;
}

interface RiskResult {
    stop_loss: number;
    stop_gain: number | null;
    total_return: number;
    sharpe_ratio: number;
    max_drawdown: number;
    win_rate: number;
    total_trades: number;
    trades?: Trade[]; // Added trades
}

const TradesModal: React.FC<{ result: RiskResult; onClose: () => void }> = ({ result, onClose }) => {
    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4" style={{ backgroundColor: 'rgba(0,0,0,0.8)' }}>
            <div className="bg-[#151922] border border-[#2A2F3A] rounded-xl w-full max-w-5xl max-h-[80vh] flex flex-col shadow-2xl">
                <div className="flex items-center justify-between p-6 border-b border-[#2A2F3A]">
                    <div>
                        <h2 className="text-xl font-bold text-white mb-1">Trade History</h2>
                        <div className="text-sm text-gray-400 font-mono">
                            SL: {(result.stop_loss * 100).toFixed(1)}% |
                            TP: {result.stop_gain ? `${(result.stop_gain * 100).toFixed(1)}%` : 'None'} |
                            Total Trades: {result.total_trades}
                        </div>
                    </div>
                    <button onClick={onClose} className="p-2 hover:bg-[#2A2F3A] rounded-full transition-colors">
                        <X className="w-6 h-6 text-gray-400" />
                    </button>
                </div>

                <div className="flex-1 overflow-auto p-6">
                    <table className="w-full text-sm text-left">
                        <thead className="text-xs text-gray-400 uppercase bg-[#0B0E14] sticky top-0">
                            <tr>
                                <th className="px-4 py-3 rounded-tl-lg">Entry Time</th>
                                <th className="px-4 py-3 text-right">Init. Bal.</th>
                                <th className="px-4 py-3 text-right">Final Bal.</th>
                                <th className="px-4 py-3">Type</th>
                                <th className="px-4 py-3 text-right">Entry Price</th>
                                <th className="px-4 py-3 text-right">Exit Price</th>
                                <th className="px-4 py-3 text-right">PnL</th>
                                <th className="px-4 py-3 text-right rounded-tr-lg">Return %</th>
                            </tr>
                        </thead>
                        <tbody>
                            {[...(result.trades || [])].sort((a, b) => new Date(b.entry_time).getTime() - new Date(a.entry_time).getTime()).map((trade, idx) => {
                                const isWin = trade.pnl > 0;
                                return (
                                    <tr key={idx} className="border-b border-[#2A2F3A] hover:bg-[#1A202C]">
                                        <td className="px-4 py-3 text-gray-300 font-mono">
                                            {new Date(trade.entry_time).toLocaleString()}
                                            <div className="text-xs text-gray-500 mt-1">
                                                Exited: {trade.exit_time ? new Date(trade.exit_time).toLocaleString() : 'Open'}
                                            </div>
                                        </td>
                                        <td className="px-4 py-3 text-right text-gray-300 font-mono">
                                            ${trade.initial_capital?.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) || '-'}
                                        </td>
                                        <td className="px-4 py-3 text-right text-gray-300 font-mono">
                                            ${trade.final_capital?.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) || '-'}
                                        </td>
                                        <td className="px-4 py-3">
                                            <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded text-xs font-medium ${trade.direction === 'Long' ? 'bg-green-900/30 text-green-400' : 'bg-red-900/30 text-red-400'}`}>
                                                {trade.direction === 'Long' ? <ArrowUp className="w-3 h-3" /> : <ArrowDown className="w-3 h-3" />}
                                                {trade.direction}
                                            </span>
                                        </td>
                                        <td className="px-4 py-3 text-right font-mono text-gray-300">
                                            ${trade.entry_price?.toFixed(2)}
                                        </td>
                                        <td className="px-4 py-3 text-right font-mono text-gray-300">
                                            ${trade.exit_price?.toFixed(2)}
                                        </td>
                                        <td className="px-4 py-3 text-right font-mono font-bold" style={{ color: isWin ? '#10B981' : '#EF4444' }}>
                                            {trade.pnl > 0 ? '+' : ''}{trade.pnl?.toFixed(2)}
                                        </td>
                                        <td className="px-4 py-3 text-right font-mono" style={{ color: isWin ? '#10B981' : '#EF4444' }}>
                                            {trade.pnl_pct ? (trade.pnl_pct * 100).toFixed(2) + '%' : '-'}
                                        </td>
                                    </tr>
                                );
                            })}
                            {(!result.trades || result.trades.length === 0) && (
                                <tr>
                                    <td colSpan={8} className="px-4 py-8 text-center text-gray-500">
                                        No trades recorded for this configuration.
                                    </td>
                                </tr>
                            )}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
};

export const RiskManagementOptimizationPage: React.FC = () => {
    const [searchParams] = useSearchParams();

    // Get URL parameters
    const urlTimeframe = searchParams.get('timeframe');
    const urlSymbol = searchParams.get('symbol');
    const urlStrategy = searchParams.get('strategy');

    const [symbol, setSymbol] = useState(urlSymbol || 'BTC/USDT');
    const [selectedIndicator, setSelectedIndicator] = useState<string>(urlStrategy || '');
    const [selectedTimeframe, setSelectedTimeframe] = useState<string>(urlTimeframe || '1h');

    // Dynamic Strategy Parameters
    const [strategyParams, setStrategyParams] = useState<Record<string, string | number>>(() => {
        const params: Record<string, string | number> = {};
        searchParams.forEach((value, key) => {
            if (!['symbol', 'strategy', 'timeframe', 'stop_loss', 'stop_gain'].includes(key)) {
                // Try to parse as number if possible
                const numVal = parseFloat(value);
                params[key] = !isNaN(numVal) ? numVal : value;
            }
        });
        return params;
    });

    // Stop-Loss configuration
    const [stopLossMin, setStopLossMin] = useState(0.005); // 0.5%
    const [stopLossMax, setStopLossMax] = useState(0.13);  // 13%
    const [stopLossStep, setStopLossStep] = useState(0.002); // 0.2%

    // Stop-Gain configuration
    const [selectedStopGains, setSelectedStopGains] = useState<(number | null)[]>([null]);

    const [isOptimizing, setIsOptimizing] = useState(false);
    const [results, setResults] = useState<RiskResult[]>([]);
    const [bestConfig, setBestConfig] = useState<RiskResult | null>(null);
    const [selectedTradeResult, setSelectedTradeResult] = useState<RiskResult | null>(null);

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

    const toggleStopGain = (value: number | null) => {
        if (selectedStopGains.includes(value)) {
            setSelectedStopGains(selectedStopGains.filter(v => v !== value));
        } else {
            setSelectedStopGains([...selectedStopGains, value]);
        }
    };

    const handleStartOptimization = async () => {
        if (!selectedIndicator) return;

        setIsOptimizing(true);
        setResults([]);
        setBestConfig(null);

        try {
            // Construct payload separately to avoid complex nesting issues
            const payload = {
                symbol: symbol,
                strategy: selectedIndicator,
                timeframe: selectedTimeframe,
                custom_ranges: {
                    stop_loss: {
                        min: stopLossMin,
                        max: stopLossMax,
                        step: stopLossStep
                    },
                    stop_gain: selectedStopGains // Pass list directly, backend now supports it
                },
                strategy_params: strategyParams // Pass as explicit dictionary
            };

            const response = await fetch('http://127.0.0.1:8000/api/optimize/parameters', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payload)
            });

            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`Optimization failed: ${errorText}`);
            }

            const data = await response.json();

            // Map API response to RiskResult format
            const mappedResults: RiskResult[] = data.results.map((res: any) => ({
                stop_loss: res.params.stop_loss || res.params.stop_pct || 0,
                stop_gain: res.params.stop_gain !== undefined ? res.params.stop_gain : (res.params.take_profit || res.params.take_pct || null),
                total_return: (res.metrics.total_return_pct || 0) * 100, // Backend returns decimal (0.6028), multiply by 100 for percentage (60.28)
                sharpe_ratio: res.metrics.sharpe_ratio || 0,
                max_drawdown: res.metrics.max_drawdown || 0,
                win_rate: res.metrics.win_rate || 0,
                total_trades: res.metrics.total_trades || 0,
                trades: res.trades || []
            }));

            // Sort by total return (or sharpe)
            mappedResults.sort((a, b) => b.total_return - a.total_return);

            setResults(mappedResults);

            // Use backend best combination logic if available, or just take top sorted
            if (mappedResults.length > 0) {
                setBestConfig(mappedResults[0]);
            }

        } catch (error) {
            console.error("Optimization failed:", error);
            alert("Failed to run risk optimization. Check backend logs.");
        } finally {
            setIsOptimizing(false);
        }
    };

    return (
        <div className="min-h-screen font-sans p-6" style={{ backgroundColor: '#0B0E14', color: '#E2E8F0' }}>
            {selectedTradeResult && (
                <TradesModal result={selectedTradeResult} onClose={() => setSelectedTradeResult(null)} />
            )}

            <div className="max-w-6xl mx-auto">

                {/* Header */}
                <div className="mb-8">
                    <h1 className="text-3xl font-bold mb-2 flex items-center gap-3" style={{ color: '#14b8a6' }}>
                        <Shield className="w-8 h-8" />
                        Risk Management Optimization
                    </h1>
                    <p className="text-gray-400">
                        Fine-tune your stop-loss and take-profit levels
                    </p>
                </div>

                {/* Configuration Form */}
                <div className="rounded-xl p-6 mb-6" style={{ backgroundColor: '#151922', border: '1px solid #2A2F3A' }}>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
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
                            <label className="block text-white font-medium mb-2">Strategy</label>
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

                        {/* Timeframe */}
                        <div>
                            <label className="block text-white font-medium mb-2">Timeframe</label>
                            <select
                                value={selectedTimeframe}
                                onChange={(e) => setSelectedTimeframe(e.target.value)}
                                className="w-full px-4 py-3 rounded-md border focus:outline-none focus:ring-1"
                                style={{
                                    backgroundColor: '#0B0E14',
                                    borderColor: '#14b8a6',
                                    color: '#E2E8F0'
                                }}
                            >
                                {TIMEFRAMES.map(tf => (
                                    <option key={tf} value={tf}>{tf}</option>
                                ))}
                            </select>
                        </div>
                    </div>

                    {/* Dynamic Strategy Parameters */}
                    {Object.keys(strategyParams).length > 0 && (
                        <div className="rounded-lg p-6 mb-6" style={{ backgroundColor: '#0B0E14', border: '1px solid #2A2F3A' }}>
                            <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                                <List className="w-5 h-5" style={{ color: '#14b8a6' }} />
                                Strategy Parameters
                            </h3>
                            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                                {Object.entries(strategyParams).map(([key, value]) => (
                                    <div key={key}>
                                        <label className="block text-sm text-gray-400 mb-1 capitalize">{key.replace(/_/g, ' ')}</label>
                                        <input
                                            type="text"
                                            value={value}
                                            onChange={(e) => {
                                                const val = e.target.value;
                                                setStrategyParams(prev => ({
                                                    ...prev,
                                                    [key]: val
                                                }));
                                            }}
                                            onBlur={(e) => {
                                                const val = e.target.value;
                                                // Try to convert to number on blur if it looks like one
                                                const numVal = parseFloat(val);
                                                if (!isNaN(numVal) && val.trim() !== '') {
                                                    setStrategyParams(prev => ({
                                                        ...prev,
                                                        [key]: numVal
                                                    }));
                                                }
                                            }}
                                            className="w-full px-3 py-2 rounded-md border"
                                            style={{
                                                backgroundColor: '#151922',
                                                borderColor: '#2D3748',
                                                color: '#E2E8F0'
                                            }}
                                        />
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}

                    {/* Risk Configuration */}
                    <div className="rounded-lg p-6 mb-6" style={{ backgroundColor: '#0B0E14', border: '1px solid #2A2F3A' }}>
                        <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                            <Shield className="w-5 h-5" style={{ color: '#14b8a6' }} />
                            Risk Management Configuration
                        </h3>

                        {/* Stop-Loss Range */}
                        <div className="mb-6">
                            <label className="block text-white font-medium mb-3">Stop-Loss Range</label>
                            <div className="grid grid-cols-3 gap-4">
                                <div>
                                    <label className="block text-sm text-gray-400 mb-1">Min (%)</label>
                                    <input
                                        type="text"
                                        defaultValue={stopLossMin * 100}
                                        onBlur={(e) => {
                                            const val = e.target.value.replace(',', '.');
                                            const parsed = parseFloat(val);
                                            if (!isNaN(parsed)) setStopLossMin(parsed / 100);
                                        }}
                                        className="w-full px-3 py-2 rounded-md border"
                                        style={{
                                            backgroundColor: '#151922',
                                            borderColor: '#2D3748',
                                            color: '#E2E8F0'
                                        }}
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm text-gray-400 mb-1">Max (%)</label>
                                    <input
                                        type="text"
                                        defaultValue={stopLossMax * 100}
                                        onBlur={(e) => {
                                            const val = e.target.value.replace(',', '.');
                                            const parsed = parseFloat(val);
                                            if (!isNaN(parsed)) setStopLossMax(parsed / 100);
                                        }}
                                        className="w-full px-3 py-2 rounded-md border"
                                        style={{
                                            backgroundColor: '#151922',
                                            borderColor: '#2D3748',
                                            color: '#E2E8F0'
                                        }}
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm text-gray-400 mb-1">Step (%)</label>
                                    <input
                                        type="text"
                                        defaultValue={stopLossStep * 100}
                                        onBlur={(e) => {
                                            const val = e.target.value.replace(',', '.');
                                            const parsed = parseFloat(val);
                                            if (!isNaN(parsed)) setStopLossStep(parsed / 100);
                                        }}
                                        className="w-full px-3 py-2 rounded-md border"
                                        style={{
                                            backgroundColor: '#151922',
                                            borderColor: '#2D3748',
                                            color: '#E2E8F0'
                                        }}
                                    />
                                </div>
                            </div>
                            <p className="text-xs text-gray-400 mt-2">💡 Most traders use 1-2%. Range 0.5%-13% covers conservative to aggressive.</p>
                        </div>

                        {/* Stop-Gain Options */}
                        <div>
                            <label className="block text-white font-medium mb-3">Stop-Gain / Take Profit Options</label>
                            <div className="flex flex-wrap gap-3">
                                {STOP_GAIN_OPTIONS.map(option => (
                                    <button
                                        key={option.label}
                                        onClick={() => toggleStopGain(option.value)}
                                        className="px-4 py-2 rounded-md font-medium transition-all"
                                        style={{
                                            backgroundColor: selectedStopGains.includes(option.value) ? '#14b8a6' : '#151922',
                                            color: selectedStopGains.includes(option.value) ? '#0B0E14' : '#E2E8F0',
                                            border: `1px solid ${selectedStopGains.includes(option.value) ? '#14b8a6' : '#2D3748'}`
                                        }}
                                    >
                                        {option.label}
                                    </button>
                                ))}
                            </div>
                        </div>
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
                        {isOptimizing ? 'Optimizing...' : 'Start Risk Optimization'}
                    </button>
                </div>

                {/* Results */}
                {results.length > 0 && (
                    <div className="rounded-xl p-6" style={{ backgroundColor: '#151922', border: '1px solid #2A2F3A' }}>
                        <h2 className="text-xl font-bold mb-4 text-white">Results</h2>

                        {/* Best Configuration Card */}
                        {bestConfig && (
                            <div className="rounded-lg p-6 mb-6" style={{ backgroundColor: '#14b8a6/10', border: '1px solid #14b8a6' }}>
                                <div className="flex items-center justify-between">
                                    <div>
                                        <div className="text-sm text-gray-400 mb-1">Best Configuration</div>
                                        <div className="text-2xl font-bold font-mono" style={{ color: '#14b8a6' }}>
                                            SL {(bestConfig.stop_loss * 100).toFixed(1)}% / TP {bestConfig.stop_gain ? `${(bestConfig.stop_gain * 100).toFixed(1)}%` : 'None'}
                                        </div>
                                        <div className="text-sm text-gray-300 mt-1">
                                            Return: {bestConfig.total_return >= 0 ? '+' : ''}{bestConfig.total_return.toFixed(2)}% |
                                            Sharpe: {bestConfig.sharpe_ratio.toFixed(2)}
                                        </div>
                                    </div>
                                    <Award className="w-12 h-12" style={{ color: '#14b8a6' }} />
                                </div>
                            </div>
                        )}

                        <div className="overflow-x-auto">
                            <table className="w-full text-sm">
                                <thead className="border-b" style={{ borderColor: '#2A2F3A' }}>
                                    <tr>
                                        <th className="text-left py-3 px-4 font-semibold text-gray-400">Stop-Loss</th>
                                        <th className="text-left py-3 px-4 font-semibold text-gray-400">Stop-Gain</th>
                                        <th className="text-right py-3 px-4 font-semibold text-gray-400">Total Return</th>
                                        <th className="text-right py-3 px-4 font-semibold text-gray-400">Sharpe Ratio</th>
                                        <th className="text-right py-3 px-4 font-semibold text-gray-400">Win Rate</th>
                                        <th className="text-right py-3 px-4 font-semibold text-gray-400">Trades</th>
                                        <th className="text-center py-3 px-4 font-semibold text-gray-400">Explore</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {results.map((result, idx) => {
                                        const isBest = idx === 0;
                                        return (
                                            <tr
                                                key={idx}
                                                className="border-b transition-colors"
                                                style={{
                                                    borderColor: '#2A2F3A',
                                                    backgroundColor: isBest ? '#14b8a6/10' : 'transparent'
                                                }}
                                            >
                                                <td className="py-3 px-4 font-mono" style={{ color: isBest ? '#14b8a6' : '#E2E8F0' }}>
                                                    {(result.stop_loss * 100).toFixed(1)}%
                                                </td>
                                                <td className="py-3 px-4 font-mono" style={{ color: isBest ? '#14b8a6' : '#E2E8F0' }}>
                                                    {result.stop_gain ? `${(result.stop_gain * 100).toFixed(1)}%` : 'None'}
                                                </td>
                                                <td className="py-3 px-4 text-right font-mono" style={{ color: result.total_return >= 0 ? '#10B981' : '#EF4444' }}>
                                                    {result.total_return >= 0 ? '+' : ''}{result.total_return.toFixed(2)}%
                                                </td>
                                                <td className="py-3 px-4 text-right font-mono text-gray-300">
                                                    {result.sharpe_ratio.toFixed(2)}
                                                </td>
                                                <td className="py-3 px-4 text-right font-mono text-gray-300">
                                                    {(result.win_rate).toFixed(1)}%
                                                </td>
                                                <td className="py-3 px-4 text-right font-mono text-gray-300">
                                                    {result.total_trades}
                                                </td>
                                                <td className="py-3 px-4 text-center">
                                                    <button
                                                        onClick={() => setSelectedTradeResult(result)}
                                                        className="p-1.5 hover:bg-[#2A2F3A] rounded transition-colors text-gray-400 hover:text-white"
                                                        title="View Trades"
                                                    >
                                                        <List className="w-5 h-5" />
                                                    </button>
                                                </td>
                                            </tr>
                                        );
                                    })}
                                </tbody>
                            </table>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};
