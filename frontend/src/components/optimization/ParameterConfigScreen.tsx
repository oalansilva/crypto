import React, { useState, useEffect } from 'react';
import { ChevronRight, Info, RotateCcw } from 'lucide-react';

interface ParameterRange {
    min: number;
    max: number;
    step: number;
}

interface ParameterSchema {
    default: any;
    optimization_range?: ParameterRange;
    options?: any[];
    market_standard: string;
    description: string;
}

interface IndicatorSchema {
    name: string;
    parameters: Record<string, ParameterSchema>;
}

interface ParameterConfigScreenProps {
    strategy: string;
    symbol: string;
    onStart: (config: any) => void;
    onCancel: () => void;
}

const ParameterConfigScreen: React.FC<ParameterConfigScreenProps> = ({
    strategy,
    symbol,
    onStart,
    onCancel
}) => {
    const [indicatorSchema, setIndicatorSchema] = useState<IndicatorSchema | null>(null);
    const [paramRanges, setParamRanges] = useState<Record<string, any>>({});
    const [stopLossRange, setStopLossRange] = useState({ min: 0.5, max: 5, step: 0.5 });
    const [stopGainOptions, setStopGainOptions] = useState([
        { value: null, label: 'None', checked: true },
        { value: 1, label: '1%', checked: true },
        { value: 2, label: '2%', checked: true },
        { value: 3, label: '3%', checked: true },
        { value: 4, label: '4%', checked: true },
        { value: 5, label: '5%', checked: true },
        { value: 7.5, label: '7.5%', checked: true },
        { value: 10, label: '10%', checked: true }
    ]);
    const [showTooltip, setShowTooltip] = useState<string | null>(null);

    // Load indicator schema (mock data for now - will fetch from API)
    useEffect(() => {
        // Mock MACD schema
        const mockSchema: IndicatorSchema = {
            name: 'MACD',
            parameters: {
                fast_period: {
                    default: 12,
                    optimization_range: { min: 6, max: 18, step: 1 },
                    market_standard: 'Most traders use 12. 70% use values between 10-14.',
                    description: 'Fast EMA period for MACD calculation'
                },
                slow_period: {
                    default: 26,
                    optimization_range: { min: 20, max: 32, step: 1 },
                    market_standard: 'Most traders use 26. Conservative range captures most variations.',
                    description: 'Slow EMA period for MACD calculation'
                },
                signal_period: {
                    default: 9,
                    optimization_range: { min: 6, max: 12, step: 1 },
                    market_standard: 'Most traders use 9. Range 6-12 covers common variations.',
                    description: 'Signal line period for MACD'
                }
            }
        };

        setIndicatorSchema(mockSchema);

        // Initialize param ranges with defaults
        const initialRanges: Record<string, any> = {};
        Object.entries(mockSchema.parameters).forEach(([key, schema]) => {
            if (schema.optimization_range) {
                initialRanges[key] = { ...schema.optimization_range };
            }
        });
        setParamRanges(initialRanges);
    }, [strategy]);

    const handleParamRangeChange = (param: string, field: string, value: number) => {
        setParamRanges(prev => ({
            ...prev,
            [param]: {
                ...prev[param],
                [field]: value
            }
        }));
    };

    const handleStopGainToggle = (index: number) => {
        setStopGainOptions(prev => prev.map((opt, i) =>
            i === index ? { ...opt, checked: !opt.checked } : opt
        ));
    };

    const handleResetDefaults = () => {
        if (!indicatorSchema) return;

        // Reset indicator params
        const resetRanges: Record<string, any> = {};
        Object.entries(indicatorSchema.parameters).forEach(([key, schema]) => {
            if (schema.optimization_range) {
                resetRanges[key] = { ...schema.optimization_range };
            }
        });
        setParamRanges(resetRanges);

        // Reset stop-loss
        setStopLossRange({ min: 0.5, max: 5, step: 0.5 });

        // Reset stop-gain
        setStopGainOptions(prev => prev.map(opt => ({ ...opt, checked: true })));
    };

    const handleStartOptimization = () => {
        const config = {
            symbol,
            strategy,
            custom_ranges: {
                ...paramRanges,
                stop_loss: stopLossRange,
                stop_gain: stopGainOptions.filter(opt => opt.checked).map(opt => opt.value)
            }
        };
        onStart(config);
    };

    const calculateTotalTests = () => {
        if (!indicatorSchema) return 0;

        let total = 7; // Timeframes

        // Indicator params
        Object.values(paramRanges).forEach(range => {
            const count = Math.floor((range.max - range.min) / range.step) + 1;
            total += count;
        });

        // Stop-loss
        const slCount = Math.floor((stopLossRange.max - stopLossRange.min) / stopLossRange.step) + 1;
        total += slCount;

        // Stop-gain
        total += stopGainOptions.filter(opt => opt.checked).length;

        return total;
    };

    if (!indicatorSchema) {
        return <div className="p-8 text-center">Loading...</div>;
    }

    return (
        <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 p-8">
            <div className="max-w-4xl mx-auto">
                {/* Header */}
                <div className="mb-8">
                    <h1 className="text-3xl font-bold text-white mb-2">
                        📋 Review Optimization Parameters
                    </h1>
                    <p className="text-gray-400">
                        Configure ranges for {indicatorSchema.name} on {symbol}
                    </p>
                </div>

                {/* Indicator Parameters */}
                <div className="bg-gray-800/50 backdrop-blur-sm rounded-xl p-6 mb-6 border border-gray-700">
                    <h2 className="text-xl font-semibold text-white mb-4 flex items-center gap-2">
                        <span className="text-2xl">📊</span>
                        Indicator: {indicatorSchema.name}
                    </h2>

                    <div className="space-y-6">
                        {Object.entries(indicatorSchema.parameters).map(([paramName, schema]) => (
                            <div key={paramName} className="bg-gray-900/50 rounded-lg p-4">
                                <div className="flex items-start justify-between mb-3">
                                    <div className="flex-1">
                                        <h3 className="text-lg font-medium text-white capitalize">
                                            {paramName.replace(/_/g, ' ')}
                                        </h3>
                                        <p className="text-sm text-gray-400 mt-1">{schema.description}</p>
                                    </div>
                                    <button
                                        className="relative"
                                        onMouseEnter={() => setShowTooltip(paramName)}
                                        onMouseLeave={() => setShowTooltip(null)}
                                    >
                                        <Info className="w-5 h-5 text-blue-400" />
                                        {showTooltip === paramName && (
                                            <div className="absolute right-0 top-8 w-64 bg-gray-700 text-white text-sm rounded-lg p-3 shadow-xl z-10">
                                                <p className="font-semibold mb-1">💡 Market Standard:</p>
                                                <p>{schema.market_standard}</p>
                                            </div>
                                        )}
                                    </button>
                                </div>

                                {schema.optimization_range && paramRanges[paramName] && (
                                    <div className="grid grid-cols-2 gap-4">
                                        <div>
                                            <label className="block text-sm text-gray-400 mb-1">Min</label>
                                            <input
                                                type="number"
                                                value={paramRanges[paramName].min}
                                                onChange={(e) => handleParamRangeChange(paramName, 'min', parseFloat(e.target.value))}
                                                className="w-full bg-gray-800 border border-gray-600 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-blue-500"
                                            />
                                        </div>
                                        <div>
                                            <label className="block text-sm text-gray-400 mb-1">Max</label>
                                            <input
                                                type="number"
                                                value={paramRanges[paramName].max}
                                                onChange={(e) => handleParamRangeChange(paramName, 'max', parseFloat(e.target.value))}
                                                className="w-full bg-gray-800 border border-gray-600 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-blue-500"
                                            />
                                        </div>
                                    </div>
                                )}

                                <p className="text-xs text-blue-400 mt-2">
                                    💡 {schema.market_standard}
                                </p>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Risk Management */}
                <div className="bg-gray-800/50 backdrop-blur-sm rounded-xl p-6 mb-6 border border-gray-700">
                    <h2 className="text-xl font-semibold text-white mb-4 flex items-center gap-2">
                        <span className="text-2xl">⚠️</span>
                        Risk Management
                    </h2>

                    {/* Stop-Loss */}
                    <div className="bg-gray-900/50 rounded-lg p-4 mb-4">
                        <h3 className="text-lg font-medium text-white mb-3">Stop-Loss (Range)</h3>
                        <div className="grid grid-cols-2 gap-4">
                            <div>
                                <label className="block text-sm text-gray-400 mb-1">Min (%)</label>
                                <input
                                    type="number"
                                    value={stopLossRange.min}
                                    onChange={(e) => setStopLossRange(prev => ({ ...prev, min: parseFloat(e.target.value) }))}
                                    step="0.1"
                                    className="w-full bg-gray-800 border border-gray-600 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-blue-500"
                                />
                            </div>
                            <div>
                                <label className="block text-sm text-gray-400 mb-1">Max (%)</label>
                                <input
                                    type="number"
                                    value={stopLossRange.max}
                                    onChange={(e) => setStopLossRange(prev => ({ ...prev, max: parseFloat(e.target.value) }))}
                                    step="0.1"
                                    className="w-full bg-gray-800 border border-gray-600 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-blue-500"
                                />
                            </div>
                        </div>
                        <p className="text-xs text-blue-400 mt-2">
                            💡 Most traders use 1-2%. Range 0.5%-5% covers conservative to aggressive.
                        </p>
                    </div>

                    {/* Stop-Gain */}
                    <div className="bg-gray-900/50 rounded-lg p-4">
                        <h3 className="text-lg font-medium text-white mb-3">Stop-Gain / Take Profit (Options)</h3>
                        <div className="grid grid-cols-4 gap-3">
                            {stopGainOptions.map((option, index) => (
                                <label key={index} className="flex items-center gap-2 cursor-pointer">
                                    <input
                                        type="checkbox"
                                        checked={option.checked}
                                        onChange={() => handleStopGainToggle(index)}
                                        className="w-4 h-4 rounded border-gray-600 bg-gray-800 text-blue-500 focus:ring-blue-500"
                                    />
                                    <span className="text-white">{option.label}</span>
                                </label>
                            ))}
                        </div>
                        <p className="text-xs text-blue-400 mt-2">
                            💡 Many traders don't use take-profit. Test all options to find best.
                        </p>
                    </div>
                </div>

                {/* Summary */}
                <div className="bg-gradient-to-r from-blue-900/30 to-purple-900/30 backdrop-blur-sm rounded-xl p-6 mb-6 border border-blue-700/50">
                    <h3 className="text-lg font-semibold text-white mb-3">📊 Optimization Summary</h3>
                    <div className="grid grid-cols-2 gap-4 text-sm">
                        <div>
                            <p className="text-gray-400">Total Stages:</p>
                            <p className="text-2xl font-bold text-white">{3 + Object.keys(paramRanges).length}</p>
                        </div>
                        <div>
                            <p className="text-gray-400">Estimated Tests:</p>
                            <p className="text-2xl font-bold text-green-400">{calculateTotalTests()}</p>
                        </div>
                    </div>
                </div>

                {/* Actions */}
                <div className="flex gap-4">
                    <button
                        onClick={handleResetDefaults}
                        className="flex items-center gap-2 px-6 py-3 bg-gray-700 hover:bg-gray-600 text-white rounded-lg transition-colors"
                    >
                        <RotateCcw className="w-5 h-5" />
                        Reset to Defaults
                    </button>
                    <button
                        onClick={onCancel}
                        className="px-6 py-3 bg-gray-700 hover:bg-gray-600 text-white rounded-lg transition-colors"
                    >
                        Cancel
                    </button>
                    <button
                        onClick={handleStartOptimization}
                        className="flex-1 flex items-center justify-center gap-2 px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white rounded-lg font-semibold transition-all transform hover:scale-105"
                    >
                        Start Optimization
                        <ChevronRight className="w-5 h-5" />
                    </button>
                </div>
            </div>
        </div>
    );
};

export default ParameterConfigScreen;
