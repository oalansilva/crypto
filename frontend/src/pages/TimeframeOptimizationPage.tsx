import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { Play, TrendingUp, Award } from 'lucide-react';

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
}

export const TimeframeOptimizationPage: React.FC = () => {
    const navigate = useNavigate();

    const [symbol, setSymbol] = useState('BTC/USDT');
    const [selectedIndicator, setSelectedIndicator] = useState<string>('');
    const [isOptimizing, setIsOptimizing] = useState(false);
    const [results, setResults] = useState<TimeframeResult[]>([]);
    const [bestTimeframe, setBestTimeframe] = useState<string | null>(null);
    const [selectedTimeframe, setSelectedTimeframe] = useState<string | null>(null);
    const [jobId, setJobId] = useState<string | null>(null);

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
                    timeframes: TIMEFRAMES,
                    parameters: defaultParams
                })
            });

            const data = await response.json();
            setJobId(data.job_id);

            // Connect to WebSocket for updates
            const ws = new WebSocket(`ws://localhost:8000/api/optimize/sequential/ws/${data.job_id}`);

            ws.onmessage = (event) => {
                const message = JSON.parse(event.data);

                if (message.type === 'completed') {
                    setResults(message.result.all_results || []);
                    setBestTimeframe(message.result.best_timeframe);
                    setSelectedTimeframe(message.result.best_timeframe);
                    setIsOptimizing(false);
                    ws.close();
                }
            };

            ws.onerror = () => {
                setIsOptimizing(false);
            };

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
                                        return (
                                            <tr
                                                key={result.timeframe}
                                                onClick={() => setSelectedTimeframe(result.timeframe)}
                                                className="border-b transition-colors cursor-pointer hover:bg-[#1A202C]"
                                                style={{
                                                    borderColor: '#2A2F3A',
                                                    backgroundColor: isSelected ? '#14b8a6/20' : (isBest ? '#14b8a6/5' : 'transparent'),
                                                    borderLeft: isSelected ? '4px solid #14b8a6' : '4px solid transparent'
                                                }}
                                            >
                                                <td className="py-3 px-4 font-mono font-bold" style={{ color: isSelected ? '#14b8a6' : '#E2E8F0' }}>
                                                    {isBest && <Award className="inline w-4 h-4 mr-2" style={{ color: '#14b8a6' }} />}
                                                    {result.timeframe} {isSelected && !isBest && <span className="text-xs text-gray-500 ml-2">(Selected)</span>}
                                                </td>
                                                <td className="py-3 px-4 text-right font-mono" style={{ color: result.total_return >= 0 ? '#10B981' : '#EF4444' }}>
                                                    {result.total_return >= 0 ? '+' : ''}{result.total_return.toFixed(2)}%
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
