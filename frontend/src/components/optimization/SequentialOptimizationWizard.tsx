import React, { useState, useEffect, useRef } from 'react';
import { Play, Pause, SkipForward, X, CheckCircle, Clock, TrendingUp, TrendingDown } from 'lucide-react';

interface OptimizationWizardProps {
    jobId: string;
    symbol: string;
    strategy: string;
    totalStages: number;
    onComplete: (results: any) => void;
    onCancel: () => void;
}

interface StageResult {
    stage_num: number;
    stage_name: string;
    parameter: string;
    best_value: any;
    best_metrics: any;
    status: 'pending' | 'running' | 'complete';
    progress: number;
}

interface TestResult {
    params: Record<string, any>;
    metrics: {
        total_pnl: number;
        win_rate: number;
        total_trades: number;
    };
}

const SequentialOptimizationWizard: React.FC<OptimizationWizardProps> = ({
    jobId,
    symbol,
    strategy,
    totalStages,
    onComplete,
    onCancel
}) => {
    const [currentStage, setCurrentStage] = useState(1);
    const [stages, setStages] = useState<StageResult[]>([]);
    const [currentTests, setCurrentTests] = useState<TestResult[]>([]);
    const [bestResult, setBestResult] = useState<TestResult | null>(null);
    const [overallProgress, setOverallProgress] = useState(0);
    const [status, setStatus] = useState<'running' | 'paused' | 'complete' | 'error'>('running');
    const [errorMessage, setErrorMessage] = useState<string | null>(null);
    const wsRef = useRef<WebSocket | null>(null);

    // Initialize stages
    useEffect(() => {
        const initialStages: StageResult[] = Array.from({ length: totalStages }, (_, i) => ({
            stage_num: i + 1,
            stage_name: `Stage ${i + 1}`,
            parameter: '',
            best_value: null,
            best_metrics: null,
            status: i === 0 ? 'running' : 'pending',
            progress: 0
        }));
        setStages(initialStages);
    }, [totalStages]);

    // WebSocket connection
    useEffect(() => {
        const ws = new WebSocket(`ws://localhost:8000/api/optimize/sequential/ws/${jobId}`);
        wsRef.current = ws;

        ws.onopen = () => {
            console.log('WebSocket connected');
        };

        ws.onmessage = (event) => {
            const message = JSON.parse(event.data);
            handleWebSocketMessage(message);
        };

        ws.onerror = (error) => {
            console.error('WebSocket error:', error);
            setStatus('error');
            setErrorMessage('Connection error');
        };

        ws.onclose = () => {
            console.log('WebSocket disconnected');
        };

        return () => {
            if (ws.readyState === WebSocket.OPEN) {
                ws.close();
            }
        };
    }, [jobId]);

    const handleWebSocketMessage = (message: any) => {
        switch (message.event) {
            case 'test_complete':
                handleTestComplete(message);
                break;
            case 'stage_complete':
                handleStageComplete(message);
                break;
            case 'progress_update':
                handleProgressUpdate(message);
                break;
            case 'error':
                handleError(message);
                break;
            case 'state_sync':
                handleStateSync(message);
                break;
        }
    };

    const handleTestComplete = (message: any) => {
        const newTest: TestResult = {
            params: message.params,
            metrics: message.metrics
        };

        setCurrentTests(prev => [...prev, newTest]);

        // Update best result
        if (!bestResult || message.metrics.total_pnl > bestResult.metrics.total_pnl) {
            setBestResult(newTest);
        }

        // Update stage progress
        setStages(prev => prev.map(stage =>
            stage.stage_num === message.stage
                ? { ...stage, progress: message.progress }
                : stage
        ));
    };

    const handleStageComplete = (message: any) => {
        setStages(prev => prev.map(stage => {
            if (stage.stage_num === message.stage) {
                return {
                    ...stage,
                    stage_name: message.stage_name,
                    parameter: message.stage_name,
                    best_value: message.best_value,
                    best_metrics: message.best_metrics,
                    status: 'complete',
                    progress: 100
                };
            } else if (stage.stage_num === message.stage + 1) {
                return { ...stage, status: 'running' };
            }
            return stage;
        }));

        setCurrentStage(message.stage + 1);
        setCurrentTests([]);
    };

    const handleProgressUpdate = (message: any) => {
        setOverallProgress(message.overall_progress);
        setStatus(message.status);
    };

    const handleError = (message: any) => {
        setStatus('error');
        setErrorMessage(message.error);
    };

    const handleStateSync = (message: any) => {
        // Sync state on reconnect
        const state = message.state;
        setCurrentStage(state.current_stage);
        setOverallProgress((state.current_stage / totalStages) * 100);
    };

    const handlePause = async () => {
        try {
            await fetch(`http://localhost:8000/api/optimize/sequential/pause/${jobId}`, {
                method: 'POST'
            });
        } catch (error) {
            console.error('Failed to pause:', error);
        }
    };

    const handleResume = async () => {
        try {
            await fetch(`http://localhost:8000/api/optimize/sequential/resume/${jobId}`, {
                method: 'POST'
            });
        } catch (error) {
            console.error('Failed to resume:', error);
        }
    };

    const handleSkip = async () => {
        try {
            await fetch(`http://localhost:8000/api/optimize/sequential/skip/${jobId}/stage/${currentStage}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ default_value: null })
            });
        } catch (error) {
            console.error('Failed to skip:', error);
        }
    };

    const handleCancel = async () => {
        try {
            await fetch(`http://localhost:8000/api/optimize/sequential/cancel/${jobId}`, {
                method: 'DELETE'
            });
            onCancel();
        } catch (error) {
            console.error('Failed to cancel:', error);
        }
    };

    const formatPnL = (value: number) => {
        return value >= 0 ? `+$${value.toFixed(2)}` : `-$${Math.abs(value).toFixed(2)}`;
    };

    const formatPercent = (value: number) => {
        return `${(value * 100).toFixed(2)}%`;
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 p-8">
            <div className="max-w-7xl mx-auto">
                {/* Header */}
                <div className="mb-8">
                    <h1 className="text-3xl font-bold text-white mb-2">
                        🚀 Sequential Optimization
                    </h1>
                    <p className="text-gray-400">
                        {strategy.toUpperCase()} on {symbol}
                    </p>
                </div>

                {/* Overall Progress */}
                <div className="bg-gray-800/50 backdrop-blur-sm rounded-xl p-6 mb-6 border border-gray-700">
                    <div className="flex items-center justify-between mb-4">
                        <h2 className="text-xl font-semibold text-white">
                            Overall Progress: Stage {currentStage}/{totalStages}
                        </h2>
                        <div className="flex gap-2">
                            {status === 'running' ? (
                                <button
                                    onClick={handlePause}
                                    className="flex items-center gap-2 px-4 py-2 bg-yellow-600 hover:bg-yellow-700 text-white rounded-lg transition-colors"
                                >
                                    <Pause className="w-4 h-4" />
                                    Pause
                                </button>
                            ) : status === 'paused' ? (
                                <button
                                    onClick={handleResume}
                                    className="flex items-center gap-2 px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg transition-colors"
                                >
                                    <Play className="w-4 h-4" />
                                    Resume
                                </button>
                            ) : null}
                            <button
                                onClick={handleSkip}
                                className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
                            >
                                <SkipForward className="w-4 h-4" />
                                Skip Stage
                            </button>
                            <button
                                onClick={handleCancel}
                                className="flex items-center gap-2 px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors"
                            >
                                <X className="w-4 h-4" />
                                Cancel
                            </button>
                        </div>
                    </div>

                    <div className="w-full bg-gray-700 rounded-full h-4 overflow-hidden">
                        <div
                            className="h-full bg-gradient-to-r from-blue-500 to-purple-500 transition-all duration-500"
                            style={{ width: `${overallProgress}%` }}
                        />
                    </div>
                    <p className="text-sm text-gray-400 mt-2">{overallProgress.toFixed(1)}% complete</p>
                </div>

                {/* Stages */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
                    {stages.map((stage) => (
                        <div
                            key={stage.stage_num}
                            className={`bg-gray-800/50 backdrop-blur-sm rounded-xl p-4 border ${stage.status === 'complete'
                                    ? 'border-green-500'
                                    : stage.status === 'running'
                                        ? 'border-blue-500'
                                        : 'border-gray-700'
                                }`}
                        >
                            <div className="flex items-center justify-between mb-2">
                                <h3 className="font-semibold text-white">
                                    {stage.stage_name || `Stage ${stage.stage_num}`}
                                </h3>
                                {stage.status === 'complete' ? (
                                    <CheckCircle className="w-5 h-5 text-green-500" />
                                ) : stage.status === 'running' ? (
                                    <Clock className="w-5 h-5 text-blue-500 animate-pulse" />
                                ) : (
                                    <div className="w-5 h-5 rounded-full bg-gray-600" />
                                )}
                            </div>

                            {stage.status === 'running' && (
                                <div className="w-full bg-gray-700 rounded-full h-2 mb-2">
                                    <div
                                        className="h-full bg-blue-500 rounded-full transition-all"
                                        style={{ width: `${stage.progress}%` }}
                                    />
                                </div>
                            )}

                            {stage.best_value !== null && (
                                <div className="text-sm text-gray-300 mt-2">
                                    <p>Best: {JSON.stringify(stage.best_value)}</p>
                                    {stage.best_metrics && (
                                        <p className="text-green-400">
                                            {formatPnL(stage.best_metrics.total_pnl)}
                                        </p>
                                    )}
                                </div>
                            )}
                        </div>
                    ))}
                </div>

                {/* Current Tests */}
                {currentTests.length > 0 && (
                    <div className="bg-gray-800/50 backdrop-blur-sm rounded-xl p-6 border border-gray-700">
                        <h2 className="text-xl font-semibold text-white mb-4">
                            Live Test Results - Stage {currentStage}
                        </h2>

                        <div className="overflow-x-auto">
                            <table className="w-full">
                                <thead>
                                    <tr className="border-b border-gray-700">
                                        <th className="text-left text-gray-400 pb-2">Parameters</th>
                                        <th className="text-right text-gray-400 pb-2">PnL</th>
                                        <th className="text-right text-gray-400 pb-2">Win Rate</th>
                                        <th className="text-right text-gray-400 pb-2">Trades</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {currentTests.map((test, index) => {
                                        const isBest = bestResult && test === bestResult;
                                        return (
                                            <tr
                                                key={index}
                                                className={`border-b border-gray-700/50 ${isBest ? 'bg-green-900/20' : ''
                                                    }`}
                                            >
                                                <td className="py-2 text-white">
                                                    {JSON.stringify(test.params)}
                                                    {isBest && <span className="ml-2">⭐</span>}
                                                </td>
                                                <td className={`py-2 text-right ${test.metrics.total_pnl >= 0 ? 'text-green-400' : 'text-red-400'
                                                    }`}>
                                                    {formatPnL(test.metrics.total_pnl)}
                                                </td>
                                                <td className="py-2 text-right text-white">
                                                    {formatPercent(test.metrics.win_rate)}
                                                </td>
                                                <td className="py-2 text-right text-white">
                                                    {test.metrics.total_trades}
                                                </td>
                                            </tr>
                                        );
                                    })}
                                </tbody>
                            </table>
                        </div>

                        {bestResult && (
                            <div className="mt-4 p-4 bg-green-900/20 border border-green-700 rounded-lg">
                                <p className="text-sm text-gray-400">Best so far:</p>
                                <p className="text-lg font-semibold text-green-400">
                                    {formatPnL(bestResult.metrics.total_pnl)} - {formatPercent(bestResult.metrics.win_rate)} win rate
                                </p>
                            </div>
                        )}
                    </div>
                )}

                {/* Error Message */}
                {status === 'error' && errorMessage && (
                    <div className="mt-6 p-4 bg-red-900/20 border border-red-700 rounded-lg">
                        <p className="text-red-400">❌ Error: {errorMessage}</p>
                    </div>
                )}
            </div>
        </div>
    );
};

export default SequentialOptimizationWizard;
