import React, { useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { Play, Shield, List, X, ArrowUp, ArrowDown } from 'lucide-react';
import { OptimizationResults } from '../components/results/OptimizationResultsNew';

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

interface IndicatorParam {
    name: string;
    type: string;
    default: any;
}

interface IndicatorMetadata {
    name: string;
    category: string;
    params?: IndicatorParam[];
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
    // Advanced fields
    profit_factor?: number;
    expectancy?: number;
    max_consecutive_losses?: number;
    avg_atr?: number;
    avg_adx?: number;
    regime_performance?: Record<string, any>;
}

const TradesModal: React.FC<{ result: RiskResult; onClose: () => void }> = ({ result, onClose }) => {
    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4" style={{ backgroundColor: 'rgba(0,0,0,0.8)' }}>
            <div className="bg-[#151922] border border-[#2A2F3A] rounded-xl w-full max-w-5xl max-h-[80vh] flex flex-col shadow-2xl">
                <div className="flex items-center justify-between p-6 border-b border-[#2A2F3A]">
                    <div>
                        <h2 className="text-xl font-bold text-white mb-1">Trade History</h2>
                        <div className="text-sm text-gray-400 font-mono">
                            SL: {result.stop_loss === 0 ? 'None' : `${(result.stop_loss * 100).toFixed(1)}%`} |
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
    const [includeZeroStopLoss, setIncludeZeroStopLoss] = useState(true);

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
                            category,
                            params: indicator.params
                        });
                    });
                }
            });
            return flattened.sort((a, b) => a.name.localeCompare(b.name));
        }
    });

    // Sync main fields from URL
    React.useEffect(() => {
        const s = searchParams.get('strategy');
        if (s && s !== selectedIndicator) setSelectedIndicator(s);

        const t = searchParams.get('timeframe');
        if (t && t !== selectedTimeframe) setSelectedTimeframe(t);

        const sym = searchParams.get('symbol');
        if (sym && sym !== symbol) setSymbol(sym);
    }, [searchParams]);

    // Effect to populate strategy parameters when indicator changes or URL params update
    React.useEffect(() => {
        if (!selectedIndicator || !indicators) return;

        // Find metadata (handle potential case differences or extra info in name)
        const meta = indicators.find(i =>
            i.name === selectedIndicator ||
            i.name.toLowerCase() === selectedIndicator.toLowerCase() ||
            i.name === selectedIndicator.split('(')[0].trim().toLowerCase()
        );

        if (meta && meta.params) {
            const defaults: Record<string, string | number> = {};
            meta.params.forEach(p => {
                // Check URL params first
                const urlParam = searchParams.get(p.name);

                if (urlParam !== null) {
                    // query params are strings, convert to number if possible/appropriate
                    // We check if it looks like a number
                    const parsed = parseFloat(urlParam);
                    if (!isNaN(parsed) && urlParam.trim() !== '') {
                        defaults[p.name] = parsed;
                    } else {
                        defaults[p.name] = urlParam;
                    }
                }
                // Fallback to default from metadata
                else if (p.default !== undefined && p.default !== null) {
                    defaults[p.name] = p.default;
                }
            });

            // Update state with combined values
            if (Object.keys(defaults).length > 0) {
                setStrategyParams(defaults);
            }
        }
    }, [selectedIndicator, indicators, searchParams]);

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
            // Sanitize strategy name (remove category/parentheses if present, e.g. "MACD (momentum)" -> "macd")
            const strategySlug = selectedIndicator.split('(')[0].trim().toLowerCase();

            // Construct payload separately to avoid complex nesting issues
            const payload = {
                symbol: symbol,
                strategy: strategySlug,
                timeframe: selectedTimeframe,
                custom_ranges: {
                    stop_loss: (() => {
                        const slValues = [];
                        if (includeZeroStopLoss) slValues.push(0);

                        // Generate range values
                        let current = stopLossMin;
                        // Use epsilon to avoid floating point issues
                        while (current <= stopLossMax + 1e-10) {
                            slValues.push(Number(current.toFixed(4)));
                            current += stopLossStep;
                        }
                        return slValues;
                    })(),
                    stop_gain: selectedStopGains // Pass list directly, backend now supports it
                },
                ...strategyParams // Include dynamic strategy parameters at top level
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
                total_return: res.metrics.total_return_pct || 0, // Corrected to use percentage
                sharpe_ratio: res.metrics.sharpe_ratio || 0,
                max_drawdown: res.metrics.max_drawdown || 0,
                win_rate: res.metrics.win_rate || 0,
                total_trades: res.metrics.total_trades || 0,
                trades: res.trades || [],
                // Advanced
                profit_factor: res.metrics.profit_factor,
                expectancy: res.metrics.expectancy,
                max_consecutive_losses: res.metrics.max_consecutive_losses,
                avg_atr: res.metrics.avg_atr,
                avg_adx: res.metrics.avg_adx,
                regime_performance: res.metrics.regime_performance
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
                    {/* Strategy Parameters - Always Visible */}
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
                                        defaultValue="0.5"
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
                                        defaultValue="13"
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
                                        defaultValue="0.2"
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
                            <div className="mt-3">
                                <label className="flex items-center gap-2 cursor-pointer">
                                    <input
                                        type="checkbox"
                                        checked={includeZeroStopLoss}
                                        onChange={(e) => setIncludeZeroStopLoss(e.target.checked)}
                                        className="w-4 h-4 rounded border-gray-600 text-teal-500 focus:ring-teal-500 bg-[#151922]"
                                    />
                                    <span className="text-sm text-gray-300">Include "No Stop Loss" (0%) test</span>
                                </label>
                            </div>
                            <p className="text-xs text-gray-400 mt-2">💡 Most traders use 1-2%. Range 0.5%-5% covers conservative to aggressive.</p>
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
                        <OptimizationResults
                            results={results.map(r => ({
                                params: {
                                    stop_loss: r.stop_loss,
                                    stop_gain: r.stop_gain
                                },
                                metrics: {
                                    total_pnl: (r.total_return / 100) * 10000, // Estimate based on 10k capital as we don't have absolute pnl here easily in RiskResult yet, or pass it if available
                                    total_pnl_pct: r.total_return / 100, // Convert % to decimal
                                    win_rate: r.win_rate,
                                    total_trades: r.total_trades,
                                    max_drawdown: r.max_drawdown,
                                    profit_factor: r.profit_factor || 0,
                                    // Advanced metrics
                                    expectancy: r.expectancy,
                                    max_consecutive_losses: r.max_consecutive_losses,
                                    avg_atr: r.avg_atr,
                                    avg_adx: r.avg_adx,
                                    regime_performance: r.regime_performance
                                }
                            }))}
                            bestResult={{
                                params: {
                                    stop_loss: bestConfig?.stop_loss,
                                    stop_gain: bestConfig?.stop_gain
                                },
                                metrics: {
                                    total_pnl: (bestConfig?.total_return || 0) / 100 * 10000,
                                    total_pnl_pct: (bestConfig?.total_return || 0) / 100,
                                    win_rate: bestConfig?.win_rate || 0,
                                    total_trades: bestConfig?.total_trades || 0,
                                    max_drawdown: bestConfig?.max_drawdown || 0,
                                    profit_factor: bestConfig?.profit_factor || 0,
                                    // Advanced
                                    expectancy: bestConfig?.expectancy,
                                    max_consecutive_losses: bestConfig?.max_consecutive_losses,
                                    avg_atr: bestConfig?.avg_atr,
                                    avg_adx: bestConfig?.avg_adx,
                                    regime_performance: bestConfig?.regime_performance
                                }
                            }}
                            timeframe={selectedTimeframe}
                        />
                    </div>
                )}
            </div>
        </div>
    );
};
