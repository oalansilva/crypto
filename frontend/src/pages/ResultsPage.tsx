// src/pages/ResultsPage.tsx
import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { useParams, useNavigate } from 'react-router-dom'
import { backtestApi } from '../lib/api'
import {
    ArrowLeft,
    Activity,
    AlertCircle
} from 'lucide-react'
import { RunSummary } from '../components/results/RunSummary'
import { ComparisonGrid } from '../components/results/ComparisonGrid'
import { StrategyDetail } from '../components/results/StrategyDetail'
import { OptimizationResults } from '../components/results/OptimizationResultsNew'
import { StrategyGridResults } from '../components/results/StrategyGridResults'
import { EnhancedMetricsDisplay } from '../components/results/EnhancedMetricsDisplay'

export function ResultsPage() {
    const { runId } = useParams<{ runId: string }>()
    const navigate = useNavigate()
    const [selectedStrategy, setSelectedStrategy] = useState<string | null>(null)

    const { data: result, isLoading, error } = useQuery({
        queryKey: ['result', runId],
        queryFn: async () => {
            const response = await backtestApi.getResult(runId!)
            return response.data
        },
        enabled: !!runId,
        refetchInterval: (query) => {
            const data = query.state.data as any
            if (data && (data.status === 'RUNNING' || data.status === 'PENDING')) return 1000
            return false
        }
    })

    if (isLoading || (result && (result.status === 'RUNNING' || result.status === 'PENDING'))) {
        const progress = result?.progress || 0
        const step = result?.current_step || 'Inicializando...'

        return (
            <div className="min-h-screen flex items-center justify-center relative overflow-hidden">
                <div className="fixed inset-0 -z-10">
                    <div className="absolute top-0 left-1/4 w-96 h-96 bg-blue-500/20 rounded-full blur-3xl animate-float"></div>
                    <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-purple-500/20 rounded-full blur-3xl animate-float" style={{ animationDelay: '2s' }}></div>
                </div>
                <div className="text-center w-full max-w-md px-6 backdrop-blur-md bg-black/20 p-8 rounded-2xl border border-white/10">
                    <Activity className="w-16 h-16 animate-spin text-blue-400 mx-auto mb-6" />
                    <h2 className="text-2xl font-bold text-white mb-2">Executando Backtest...</h2>
                    <p className="text-gray-400 mb-6 animate-pulse">{step}</p>

                    {/* Progress Bar */}
                    <div className="w-full bg-gray-800 h-2 rounded-full overflow-hidden border border-gray-700">
                        <div
                            className="h-full bg-gradient-to-r from-blue-500 to-purple-600 transition-all duration-500 ease-out"
                            style={{ width: `${progress}%` }}
                        />
                    </div>
                    <div className="flex justify-between items-center mt-2">
                        <span className="text-xs text-gray-500 font-mono">Status: {result?.status || 'Loading'}</span>
                        <span className="text-xs text-blue-400 font-mono font-bold">{progress.toFixed(0)}%</span>
                    </div>
                </div>
            </div>
        )
    }

    if (error || !result) {
        return (
            <div className="min-h-screen flex items-center justify-center relative overflow-hidden">
                <div className="fixed inset-0 -z-10">
                    <div className="absolute top-0 left-1/4 w-96 h-96 bg-rose-500/20 rounded-full blur-3xl"></div>
                </div>
                <div className="text-center glass-strong p-12 rounded-2xl border border-white/10 max-w-md">
                    <AlertCircle className="w-20 h-20 text-rose-400 mx-auto mb-6" />
                    <h2 className="text-3xl font-bold text-white mb-3">Error Loading Results</h2>
                    <p className="text-gray-400 mb-8">Could not load backtest results</p>
                    <button
                        onClick={() => navigate('/')}
                        className="bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 text-white px-8 py-3 rounded-xl font-semibold transition-all duration-300 inline-flex items-center gap-2"
                    >
                        <ArrowLeft className="w-5 h-5" />
                        Back to Home
                    </button>
                </div>
            </div>
        )
    }

    // Prepare data for ComparisonGrid
    // Prepare data for ComparisonGrid - only for standard runs
    const comparisonResults = result.results
        ? Object.entries(result.results).map(([name, res]: [string, any]) => ({
            strategyName: name,
            metrics: res.metrics
        }))
        : []

    // Prepare data for StrategyDetail if selected
    const detailData = selectedStrategy ? {
        strategyName: selectedStrategy,
        result: result.results[selectedStrategy]
    } : null

    return (
        <div className="min-h-screen relative overflow-hidden">
            {/* Animated background */}
            <div className="fixed inset-0 -z-10">
                <div className="absolute top-0 left-1/4 w-96 h-96 bg-blue-500/20 rounded-full blur-3xl animate-float"></div>
                <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-purple-500/20 rounded-full blur-3xl animate-float" style={{ animationDelay: '2s' }}></div>
                <div className="absolute top-1/2 left-1/2 w-96 h-96 bg-pink-500/10 rounded-full blur-3xl animate-float" style={{ animationDelay: '4s' }}></div>
            </div>

            {/* Header */}
            <header className="glass-strong border-b border-white/10 sticky top-0 z-50">
                <div className="container mx-auto px-6 py-6">
                    <button
                        onClick={() => selectedStrategy ? setSelectedStrategy(null) : navigate('/')}
                        className="flex items-center gap-3 text-gray-400 hover:text-white transition-all duration-300 group"
                    >
                        <div className="bg-white/5 p-2 rounded-lg group-hover:bg-white/10 transition-all">
                            <ArrowLeft className="w-5 h-5" />
                        </div>
                        <span className="font-semibold">{selectedStrategy ? 'Back to Overview' : 'Back to Home'}</span>
                    </button>
                </div>
            </header>

            {/* Main Content */}
            <main className="container mx-auto px-6 py-12">
                {/* Title Section */}
                <div className="mb-8">
                    <h1 className="text-4xl font-bold mb-4">
                        <span className="gradient-text">Backtest Results</span>
                    </h1>
                </div>

                {!selectedStrategy ? (
                    <div className="animate-fade-in">
                        <RunSummary
                            dataset={result.dataset}
                            capital={result.params?.cash || 10000}
                            fee={result.params?.fee || 0.001}
                            strategiesCount={result.mode === 'optimize' ? result.combinations_tested : Object.keys(result.results).length}
                        />

                        {result.mode === 'optimize' && result.multi_strategy ? (
                            <StrategyGridResults
                                strategies={result.strategies}
                                overall_best={result.overall_best}
                                onDrillDown={(strategy) => {
                                    // Find the strategy's results and show them in OptimizationResults
                                    const stratData = result.strategies.find((s: any) => s.strategy === strategy)
                                    if (stratData) {
                                        setSelectedStrategy(strategy)
                                    }
                                }}
                            />
                        ) : result.mode === 'optimize' ? (
                            <>
                                <OptimizationResults
                                    results={result.optimization_results}
                                    bestResult={result.best_result}
                                    timeframe={result.dataset?.timeframe}
                                />
                                {/* Enhanced Metrics Display - Debug */}
                                {(() => {
                                    console.log('=== Enhanced Metrics Debug ===');
                                    console.log('result.best_result:', result.best_result);
                                    console.log('result.best_result?.metrics:', result.best_result?.metrics);

                                    if (result.best_result?.metrics) {
                                        return <EnhancedMetricsDisplay metrics={result.best_result.metrics} />;
                                    } else {
                                        console.log('No metrics found in best_result');
                                        return null;
                                    }
                                })()}
                            </>
                        ) : (
                            <ComparisonGrid
                                results={comparisonResults}
                                onSelectStrategy={setSelectedStrategy}
                            />
                        )}
                    </div>
                ) : (
                    detailData && (
                        <StrategyDetail
                            data={detailData}
                            candles={result.candles} // Global candles
                            onBack={() => setSelectedStrategy(null)}
                        />
                    )
                )}
            </main>
        </div>
    )
}
