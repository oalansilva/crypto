// file: frontend/src/pages/AutoBacktestPage.tsx
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { Play, Zap } from 'lucide-react';

export const AutoBacktestPage: React.FC = () => {
    const navigate = useNavigate();
    const [symbol, setSymbol] = useState('BTC/USDT');
    const [strategy, setStrategy] = useState('');
    const [isRunning, setIsRunning] = useState(false);

    // Fetch symbols
    const { data: symbolsData } = useQuery({
        queryKey: ['binance-symbols'],
        queryFn: async () => {
            const response = await fetch('http://localhost:8000/api/exchanges/binance/symbols');
            if (!response.ok) throw new Error('Failed to fetch symbols');
            const data = await response.json();
            return data.symbols as string[];
        },
        staleTime: 1000 * 60 * 60 * 24,
    });

    // Fetch strategies
    const { data: strategies } = useQuery({
        queryKey: ['strategies-metadata'],
        queryFn: async () => {
            const response = await fetch('http://127.0.0.1:8000/api/strategies/metadata');
            if (!response.ok) return [];
            const data = await response.json();
            const flattened: any[] = [];
            Object.entries(data).forEach(([category, items]: [string, any]) => {
                if (Array.isArray(items)) {
                    items.forEach((item: any) => {
                        flattened.push({ id: item.id || item.name, name: item.name });
                    });
                }
            });
            return flattened.sort((a, b) => a.name.localeCompare(b.name));
        }
    });

    const handleStart = async () => {
        if (!symbol || !strategy) return;

        setIsRunning(true);
        try {
            const params = new URLSearchParams({ symbol, strategy });
            const response = await fetch(`http://localhost:8000/api/backtest/auto?${params}`, {
                method: 'POST'
            });

            if (!response.ok) {
                throw new Error('Failed to start auto backtest');
            }

            const result = await response.json();
            navigate(`/backtest/auto/results/${result.run_id}`);
        } catch (error) {
            console.error('Error starting auto backtest:', error);
            alert('Failed to start auto backtest. Check console for details.');
        } finally {
            setIsRunning(false);
        }
    };

    return (
        <div className="min-h-screen font-sans p-6" style={{ backgroundColor: '#0B0E14', color: '#E2E8F0' }}>
            <div className="max-w-3xl mx-auto">
                {/* Header */}
                <div className="mb-8">
                    <div className="flex items-center gap-3 mb-2">
                        <Zap className="w-8 h-8 text-teal-500" />
                        <h1 className="text-3xl font-bold text-teal-500">Auto Backtest</h1>
                    </div>
                    <p className="text-gray-400">
                        Complete end-to-end optimization: Timeframe → Parameters → Risk → Auto-save
                    </p>
                </div>

                {/* Form Card */}
                <div className="rounded-xl p-8" style={{ backgroundColor: '#151922', border: '1px solid #2A2F3A' }}>
                    <div className="space-y-6">
                        {/* Symbol */}
                        <div>
                            <label className="block text-white font-medium mb-2">Trading Pair</label>
                            <select
                                value={symbol}
                                onChange={(e) => setSymbol(e.target.value)}
                                className="w-full px-4 py-3 rounded-md border focus:outline-none focus:ring-2 focus:ring-teal-500"
                                style={{
                                    backgroundColor: '#0B0E14',
                                    borderColor: '#2D3748',
                                    color: '#E2E8F0'
                                }}
                            >
                                {symbolsData ? (
                                    symbolsData.map(s => (
                                        <option key={s} value={s}>{s}</option>
                                    ))
                                ) : (
                                    <option value={symbol}>{symbol}</option>
                                )}
                            </select>
                        </div>

                        {/* Strategy */}
                        <div>
                            <label className="block text-white font-medium mb-2">Strategy</label>
                            <select
                                value={strategy}
                                onChange={(e) => setStrategy(e.target.value)}
                                className="w-full px-4 py-3 rounded-md border focus:outline-none focus:ring-2 focus:ring-teal-500"
                                style={{
                                    backgroundColor: '#0B0E14',
                                    borderColor: '#2D3748',
                                    color: '#E2E8F0'
                                }}
                            >
                                <option value="">Select a strategy</option>
                                {strategies?.map(s => (
                                    <option key={s.id} value={s.id}>{s.name.toUpperCase()}</option>
                                ))}
                            </select>
                        </div>

                        {/* Info */}
                        <div className="p-4 rounded-lg" style={{ backgroundColor: '#0B0E14', border: '1px solid #2A2F3A' }}>
                            <p className="text-sm text-gray-400">
                                <strong className="text-teal-500">What happens:</strong><br />
                                1. Tests all timeframes (5m, 15m, 30m, 1h, 2h, 4h, 1d)<br />
                                2. Optimizes strategy parameters<br />
                                3. Optimizes stop-loss and take-profit<br />
                                4. Auto-saves best configuration to Favorites
                            </p>
                        </div>

                        {/* Start Button */}
                        <button
                            onClick={handleStart}
                            disabled={!symbol || !strategy || isRunning}
                            className="w-full flex items-center justify-center gap-3 px-6 py-4 rounded-md font-bold text-lg transition-all"
                            style={{
                                backgroundColor: symbol && strategy && !isRunning ? '#14b8a6' : '#1A202C',
                                color: symbol && strategy && !isRunning ? '#0B0E14' : '#4A5568',
                                cursor: symbol && strategy && !isRunning ? 'pointer' : 'not-allowed'
                            }}
                        >
                            <Play className="w-6 h-6" fill={symbol && strategy && !isRunning ? 'currentColor' : 'none'} />
                            {isRunning ? 'Running Auto Backtest...' : 'Start Auto Backtest'}
                        </button>

                        {/* History Link */}
                        <div className="text-center">
                            <button
                                onClick={() => navigate('/backtest/auto/history')}
                                className="text-teal-500 hover:text-teal-400 text-sm underline"
                            >
                                View Execution History
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};
