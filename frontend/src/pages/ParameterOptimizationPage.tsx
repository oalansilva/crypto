import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { Loader2, Settings, TrendingUp, ChevronDown, ChevronUp } from 'lucide-react';
import ParameterOptimizationResults from '../components/optimization/ParameterOptimizationResults';

type Step = 'config' | 'running' | 'results';

interface IndicatorMetadata {
    id: string;
    name: string;
    category: string;
    params: Array<{
        name: string;
        type: string;
        default: any;
    }>;
}

interface ParameterRange {
    min: number;
    max: number;
    step: number;
}

interface OptimizationResults {
    results: Array<{
        params: Record<string, any>;
        metrics: {
            total_pnl: number;
            sharpe_ratio: number;
            win_rate: number;
            total_trades: number;
        };
    }>;
    best_combination: Record<string, any>;
    total_tests: number;
    execution_time_seconds: number;
}

export const ParameterOptimizationPage: React.FC = () => {
    const navigate = useNavigate();
    const [searchParams] = useSearchParams();

    // Get URL parameters
    const urlTimeframe = searchParams.get('timeframe');
    const urlSymbol = searchParams.get('symbol');
    const urlStrategy = searchParams.get('strategy');

    // State
    const [step, setStep] = useState<Step>('config');
    const [results, setResults] = useState<OptimizationResults | null>(null);
    const [config, setConfig] = useState({
        symbol: urlSymbol || 'BTC/USDT',
        strategy: urlStrategy || '',
        timeframe: urlTimeframe || '1h'
    });
    const [parameterRanges, setParameterRanges] = useState<Record<string, ParameterRange>>({});
    const [showParameters, setShowParameters] = useState(false);
    const [selectedIndicator, setSelectedIndicator] = useState<IndicatorMetadata | null>(null);
    const [fee, setFee] = useState(0.00075); // Default 0.075% (enabled)
    const [slippage, setSlippage] = useState(0); // Default 0% (disabled)

    // Fetch all indicators metadata
    const { data: indicatorsData, isLoading: loadingIndicators } = useQuery({
        queryKey: ['indicators-metadata'],
        queryFn: async () => {
            const response = await fetch('http://localhost:8000/api/strategies/metadata');
            if (!response.ok) {
                throw new Error('Failed to fetch indicators');
            }
            const data = await response.json();

            // Flatten the grouped data
            const flattened: IndicatorMetadata[] = [];
            Object.entries(data).forEach(([category, indicators]: [string, any]) => {
                if (Array.isArray(indicators)) {
                    indicators.forEach((indicator: any) => {
                        flattened.push({
                            id: indicator.id || indicator.name,
                            name: indicator.name,
                            category,
                            params: indicator.params || []
                        });
                    });
                }
            });
            return flattened.sort((a, b) => a.name.localeCompare(b.name));
        }
    });

    // When strategy changes, fetch its parameter schema and generate suggested ranges
    useEffect(() => {
        console.log('🔍 useEffect triggered:', { strategy: config.strategy, hasIndicatorsData: !!indicatorsData });

        if (!config.strategy || !indicatorsData) {
            console.log('⚠️ Early return - missing strategy or indicators data');
            return;
        }

        const indicator = indicatorsData.find(ind => ind.id === config.strategy);
        console.log('📊 Found indicator:', indicator);

        if (!indicator) {
            console.log('❌ Indicator not found for strategy:', config.strategy);
            return;
        }

        setSelectedIndicator(indicator);
        console.log('✅ Selected indicator set:', indicator.name);
        console.log('📝 Indicator params:', indicator.params);

        // Generate suggested ranges for numeric parameters
        const ranges: Record<string, ParameterRange> = {};
        indicator.params.forEach(param => {
            console.log(`  Checking param: ${param.name}, type: ${param.type}, default: ${param.default}`);

            if (param.type === 'int' || param.type === 'float' || param.type === 'number') {
                const defaultValue = Number(param.default);
                console.log(`    → Numeric param detected, defaultValue: ${defaultValue}`);

                if (!isNaN(defaultValue) && defaultValue > 0) {
                    // Suggest range: [default * 0.5, default * 1.5]
                    const min = Math.max(1, Math.round(defaultValue * 0.5));
                    const max = Math.round(defaultValue * 1.5);
                    ranges[param.name] = {
                        min,
                        max,
                        step: param.type === 'int' ? 1 : 0.1
                    };
                    console.log(`    ✅ Range generated: ${param.name} = [${min}, ${max}], step: ${ranges[param.name].step}`);
                } else {
                    console.log(`    ⚠️ Skipped - invalid default value`);
                }
            } else {
                console.log(`    ⚠️ Skipped - non-numeric type`);
            }
        });

        console.log('📦 Final ranges object:', ranges);
        console.log('📊 Number of ranges:', Object.keys(ranges).length);

        setParameterRanges(ranges);
        setShowParameters(Object.keys(ranges).length > 0);

        console.log('✅ State updated - showParameters:', Object.keys(ranges).length > 0);
    }, [config.strategy, indicatorsData]);

    const updateParameterRange = (paramName: string, field: 'min' | 'max' | 'step', value: number) => {
        setParameterRanges(prev => ({
            ...prev,
            [paramName]: {
                ...prev[paramName],
                [field]: value
            }
        }));
    };

    const handleStartOptimization = async () => {
        if (!config.strategy) {
            alert('Please select a strategy');
            return;
        }

        setStep('running');

        try {
            const response = await fetch('http://localhost:8000/api/optimize/parameters', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    symbol: config.symbol,
                    strategy: config.strategy,
                    timeframe: config.timeframe,
                    custom_ranges: parameterRanges,
                    fee: fee,
                    slippage: slippage
                }),
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            setResults(data);
            setStep('results');
        } catch (error) {
            console.error('Optimization failed:', error);
            alert(`Optimization failed: ${error}`);
            setStep('config');
        }
    };

    // Loading state
    if (step === 'running') {
        return (
            <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 flex items-center justify-center">
                <div className="text-center">
                    <Loader2 className="w-16 h-16 text-teal-400 animate-spin mx-auto mb-6" />
                    <h2 className="text-3xl font-bold text-white mb-3">
                        Optimizing Parameters...
                    </h2>
                    <p className="text-gray-400 text-lg mb-2">
                        Testing all parameter combinations
                    </p>
                    <p className="text-gray-500">
                        This may take a few minutes. Please wait.
                    </p>

                    {/* Progress indicator */}
                    <div className="mt-8 flex items-center justify-center gap-2">
                        <div className="w-2 h-2 bg-teal-400 rounded-full animate-pulse" style={{ animationDelay: '0ms' }}></div>
                        <div className="w-2 h-2 bg-teal-400 rounded-full animate-pulse" style={{ animationDelay: '200ms' }}></div>
                        <div className="w-2 h-2 bg-teal-400 rounded-full animate-pulse" style={{ animationDelay: '400ms' }}></div>
                    </div>
                </div>
            </div>
        );
    }

    // Results state
    if (step === 'results' && results) {
        return (
            <ParameterOptimizationResults
                results={results.results}
                bestCombination={results.best_combination}
                symbol={config.symbol}
                strategy={config.strategy}
                timeframe={config.timeframe}
            />
        );
    }

    // Config state - Enhanced form with dynamic parameters
    return (
        <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 p-8">
            <div className="max-w-4xl mx-auto">
                <div className="mb-8">
                    <h1 className="text-3xl font-bold text-white mb-2">Parameter Optimization</h1>
                    <p className="text-gray-400">Find the best parameter values for your strategy</p>
                </div>

                <div className="bg-gray-800/50 backdrop-blur-sm rounded-xl border border-gray-700 p-6 space-y-6">
                    {/* Basic Configuration */}
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-400 mb-2">Symbol</label>
                            <select
                                value={config.symbol}
                                onChange={(e) => setConfig({ ...config, symbol: e.target.value })}
                                className="w-full px-4 py-2 bg-gray-900 border border-gray-700 rounded-lg text-white focus:border-teal-500 focus:outline-none"
                            >
                                <option value="BTC/USDT">BTC/USDT</option>
                                <option value="ETH/USDT">ETH/USDT</option>
                                <option value="BNB/USDT">BNB/USDT</option>
                                <option value="SOL/USDT">SOL/USDT</option>
                                <option value="ADA/USDT">ADA/USDT</option>
                                <option value="LINK/USDT">LINK/USDT</option>
                                <option value="XMR/USDT">XMR/USDT</option>
                                <option value="ATOM/USDT">ATOM/USDT</option>
                                <option value="LTC/USDT">LTC/USDT</option>
                                <option value="TRX/USDT">TRX/USDT</option>
                            </select>
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-400 mb-2">Timeframe</label>
                            <select
                                value={config.timeframe}
                                onChange={(e) => setConfig({ ...config, timeframe: e.target.value })}
                                className="w-full px-4 py-2 bg-gray-900 border border-gray-700 rounded-lg text-white focus:border-teal-500 focus:outline-none"
                            >
                                <option value="5m">5m</option>
                                <option value="15m">15m</option>
                                <option value="30m">30m</option>
                                <option value="1h">1h</option>
                                <option value="2h">2h</option>
                                <option value="4h">4h</option>
                                <option value="1d">1d</option>
                            </select>
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-400 mb-2">Strategy</label>
                            <select
                                value={config.strategy}
                                onChange={(e) => setConfig({ ...config, strategy: e.target.value })}
                                className="w-full px-4 py-2 bg-gray-900 border border-gray-700 rounded-lg text-white focus:border-teal-500 focus:outline-none"
                                disabled={loadingIndicators}
                            >
                                <option value="">Select a strategy...</option>
                                {indicatorsData?.map(ind => (
                                    <option key={ind.id} value={ind.id}>
                                        {ind.name.toUpperCase()} ({ind.category})
                                    </option>
                                ))}
                            </select>
                        </div>
                    </div>

                    {/* Parameter Ranges Section */}
                    {config.strategy && selectedIndicator && Object.keys(parameterRanges).length > 0 && (
                        <div className="border-t border-gray-700 pt-6">
                            <button
                                onClick={() => setShowParameters(!showParameters)}
                                className="flex items-center justify-between w-full mb-4 text-left"
                            >
                                <div className="flex items-center gap-2">
                                    <Settings className="w-5 h-5 text-teal-400" />
                                    <h3 className="text-lg font-semibold text-white">Parameter Ranges</h3>
                                    <span className="text-sm text-gray-500">
                                        ({Object.keys(parameterRanges).length} parameters)
                                    </span>
                                </div>
                                {showParameters ? (
                                    <ChevronUp className="w-5 h-5 text-gray-400" />
                                ) : (
                                    <ChevronDown className="w-5 h-5 text-gray-400" />
                                )}
                            </button>

                            {showParameters && (
                                <div className="space-y-4">
                                    {Object.entries(parameterRanges).map(([paramName, range]) => {
                                        const param = selectedIndicator.params.find(p => p.name === paramName);
                                        return (
                                            <div key={paramName} className="bg-gray-900/50 rounded-lg p-4 border border-gray-700">
                                                <div className="flex items-center justify-between mb-3">
                                                    <div>
                                                        <h4 className="text-white font-medium uppercase text-sm">{paramName}</h4>
                                                        {param && (
                                                            <p className="text-xs text-gray-500">
                                                                Default: {param.default} • Type: {param.type}
                                                            </p>
                                                        )}
                                                    </div>
                                                </div>
                                                <div className="grid grid-cols-3 gap-3">
                                                    <div>
                                                        <label className="block text-xs text-gray-400 mb-1">Min</label>
                                                        <input
                                                            type="number"
                                                            value={range.min}
                                                            onChange={(e) => updateParameterRange(paramName, 'min', Number(e.target.value))}
                                                            className="w-full px-3 py-2 bg-gray-800 border border-gray-600 rounded text-white text-sm focus:border-teal-500 focus:outline-none"
                                                        />
                                                    </div>
                                                    <div>
                                                        <label className="block text-xs text-gray-400 mb-1">Max</label>
                                                        <input
                                                            type="number"
                                                            value={range.max}
                                                            onChange={(e) => updateParameterRange(paramName, 'max', Number(e.target.value))}
                                                            className="w-full px-3 py-2 bg-gray-800 border border-gray-600 rounded text-white text-sm focus:border-teal-500 focus:outline-none"
                                                        />
                                                    </div>
                                                    <div>
                                                        <label className="block text-xs text-gray-400 mb-1">Step</label>
                                                        <input
                                                            type="number"
                                                            value={range.step}
                                                            onChange={(e) => updateParameterRange(paramName, 'step', Number(e.target.value))}
                                                            step={0.1}
                                                            className="w-full px-3 py-2 bg-gray-800 border border-gray-600 rounded text-white text-sm focus:border-teal-500 focus:outline-none"
                                                        />
                                                    </div>
                                                </div>
                                            </div>
                                        );
                                    })}
                                </div>
                            )}
                        </div>
                    )}

                    {/* Advanced Options */}
                    <div className="border-t border-gray-700 pt-6">
                        <h3 className="text-lg font-semibold text-white mb-4">Advanced Options</h3>
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
                        disabled={!config.strategy}
                        className="w-full px-6 py-3 bg-gradient-to-r from-teal-600 to-emerald-600 hover:from-teal-700 hover:to-emerald-700 disabled:from-gray-700 disabled:to-gray-700 disabled:cursor-not-allowed text-white rounded-lg font-semibold flex items-center justify-center gap-2 transition-all"
                    >
                        <TrendingUp className="w-5 h-5" />
                        Start Optimization
                    </button>
                </div>
            </div>
        </div>
    );
};

export default ParameterOptimizationPage;
