import React, { useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { CheckCircle, XCircle, Loader } from 'lucide-react';

interface StageResult {
    stage_number: number;
    stage_name: string;
    status: string;
    result?: any;
}

interface AutoBacktestResponse {
    run_id: string;
    status: string;
    symbol: string;
    strategy: string;
    stages: StageResult[];
    favorite_id?: number;
    created_at: string;
    completed_at?: string;
}

export const AutoBacktestResultsPage: React.FC = () => {
    const { runId } = useParams<{ runId: string }>();
    const navigate = useNavigate();

    const { data, isLoading, error } = useQuery({
        queryKey: ['auto-backtest-result', runId],
        queryFn: async () => {
            const response = await fetch(`http://localhost:8000/api/backtest/auto/${runId}`);
            if (!response.ok) throw new Error('Failed to fetch results');
            return response.json() as Promise<AutoBacktestResponse>;
        },
        refetchInterval: (query) => {
            const status = query.state.data?.status;
            return (status === 'RUNNING' || status === 'PENDING') ? 2000 : false;
        }
    });

    // Auto-redirect to favorites when completed
    useEffect(() => {
        if (data?.status === 'COMPLETED' && data?.favorite_id) {
            const timer = setTimeout(() => {
                navigate('/favorites');
            }, 2000); // Wait 2 seconds to show completion status
            return () => clearTimeout(timer);
        }
    }, [data?.status, data?.favorite_id, navigate]);

    if (isLoading || !data) {
        return (
            <div className="min-h-screen flex items-center justify-center" style={{ backgroundColor: '#0B0E14' }}>
                <Loader className="w-8 h-8 text-teal-500 animate-spin" />
            </div>
        );
    }

    if (error) {
        return (
            <div className="min-h-screen flex items-center justify-center" style={{ backgroundColor: '#0B0E14' }}>
                <div className="text-center">
                    <XCircle className="w-16 h-16 text-red-500 mx-auto mb-4" />
                    <p className="text-white">Failed to load results</p>
                </div>
            </div>
        );
    }

    const isCompleted = data.status === 'COMPLETED';
    const isFailed = data.status === 'FAILED';

    return (
        <div className="min-h-screen font-sans p-6" style={{ backgroundColor: '#0B0E14', color: '#E2E8F0' }}>
            <div className="max-w-5xl mx-auto">
                {/* Header */}
                <div className="mb-8">
                    <h1 className="text-3xl font-bold mb-2" style={{ color: '#14b8a6' }}>
                        Auto Backtest Results
                    </h1>
                    <div className="flex items-center gap-4 text-sm text-gray-400">
                        <span>Run ID: {data.run_id}</span>
                        <span>Symbol: {data.symbol}</span>
                        <span>Strategy: {data.strategy.toUpperCase()}</span>
                    </div>
                </div>

                {/* Status Card */}
                <div className={`rounded-xl p-6 mb-6 ${isCompleted ? 'bg-green-900/20 border-green-500' :
                    isFailed ? 'bg-red-900/20 border-red-500' :
                        'bg-teal-900/20 border-teal-500'
                    }`} style={{ border: '2px solid' }}>
                    <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                            {isCompleted && <CheckCircle className="w-8 h-8 text-green-500" />}
                            {isFailed && <XCircle className="w-8 h-8 text-red-500" />}
                            {!isCompleted && !isFailed && <Loader className="w-8 h-8 text-teal-500 animate-spin" />}
                            <div>
                                <div className="text-2xl font-bold text-white">
                                    {data.status}
                                </div>
                                <div className="text-sm text-gray-400">
                                    Stage {data.stages.length}/3
                                </div>
                            </div>
                        </div>
                        {isCompleted && data.favorite_id && (
                            <button
                                onClick={() => navigate('/favorites')}
                                className="px-6 py-2 bg-teal-500 text-black rounded-md font-bold hover:bg-teal-400"
                            >
                                View in Favorites
                            </button>
                        )}
                    </div>
                </div>

                {/* Stages */}
                <div className="space-y-4">
                    {[1, 2, 3].map(stageNum => {
                        const stage = data.stages.find(s => s.stage_number === stageNum);
                        const isActive = stage?.status === 'COMPLETED';
                        const isPending = !stage;

                        return (
                            <div
                                key={stageNum}
                                className="rounded-xl p-6"
                                style={{
                                    backgroundColor: '#151922',
                                    border: isActive ? '1px solid #14b8a6' : '1px solid #2A2F3A'
                                }}
                            >
                                <div className="flex items-start justify-between">
                                    <div className="flex-1">
                                        <div className="flex items-center gap-3 mb-2">
                                            {isActive && <CheckCircle className="w-6 h-6 text-teal-500" />}
                                            {isPending && <div className="w-6 h-6 rounded-full border-2 border-gray-600" />}
                                            <h3 className="text-lg font-bold text-white">
                                                Stage {stageNum}: {
                                                    stageNum === 1 ? 'Timeframe Optimization' :
                                                        stageNum === 2 ? 'Parameter Optimization' :
                                                            'Risk Optimization'
                                                }
                                            </h3>
                                        </div>
                                        {stage?.result && (
                                            <div className="ml-9 mt-3 p-4 rounded-lg bg-gray-900">
                                                <pre className="text-xs text-gray-400 overflow-auto">
                                                    {JSON.stringify(stage.result, null, 2)}
                                                </pre>
                                            </div>
                                        )}
                                    </div>
                                </div>
                            </div>
                        );
                    })}
                </div>

                {/* Actions */}
                <div className="mt-8 flex gap-4">
                    <button
                        onClick={() => navigate('/backtest/auto')}
                        className="px-6 py-3 rounded-md font-bold bg-gray-700 hover:bg-gray-600 text-white"
                    >
                        Run Another
                    </button>
                    <button
                        onClick={() => navigate('/backtest/auto/history')}
                        className="px-6 py-3 rounded-md font-bold bg-gray-700 hover:bg-gray-600 text-white"
                    >
                        View History
                    </button>
                </div>
            </div>
        </div>
    );
};
