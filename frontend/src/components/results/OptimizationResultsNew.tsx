import { useState, useEffect } from 'react'
import { Card } from '../ui'
import { TrendingUp, Shield, Award } from 'lucide-react'

interface OptimizationItem {
    params: Record<string, any>
    metrics: {
        total_pnl: number
        total_pnl_pct: number
        win_rate: number
        total_trades: number
        max_drawdown: number
        profit_factor: number
        // Advanced
        expectancy?: number
        max_consecutive_losses?: number
        avg_atr?: number
        avg_adx?: number
        regime_performance?: Record<string, any>
    }
}

interface OptimizationResultsProps {
    results: OptimizationItem[]
    bestResult: OptimizationItem
    timeframe?: string  // Optional timeframe to display in table
}

// Helper to get all keys that exist in params across results (excluding timeframe if handled separately)
function getAllRelevantParams(results: OptimizationItem[]) {
    const keys = new Set<string>()
    results.forEach(r => {
        Object.keys(r.params).forEach(k => {
            if (k !== 'timeframe') keys.add(k)
        })
    })
    return Array.from(keys).sort()
}


function formatParamKey(key: string): string {
    return key.replace(/_/g, ' ').toUpperCase()
}

function formatParamValue(key: string, val: any): string {
    if (val === null || val === undefined) return 'N/A'
    if (typeof val === 'number') {
        // Detect percentage fields by key name
        if (key.toLowerCase().endsWith('pct') || key === 'stop_loss' || key === 'take_profit') {
            return `${(val * 100).toLocaleString('en-US', { maximumFractionDigits: 2 })}%`
        }
        return val.toString()
    }
    return String(val)
}

export function OptimizationResults({ results, bestResult, timeframe }: OptimizationResultsProps) {
    // Get all relevant params (for table display)
    const allParams = getAllRelevantParams(results)

    // Sort table data
    const sortedResults = [...results].sort((a, b) => b.metrics.total_pnl - a.metrics.total_pnl)

    // Pagination State
    const [currentPage, setCurrentPage] = useState(1)
    const [itemsPerPage, setItemsPerPage] = useState(10)

    const totalPages = Math.ceil(sortedResults.length / itemsPerPage)
    const startIndex = (currentPage - 1) * itemsPerPage
    const displayedResults = sortedResults.slice(startIndex, startIndex + itemsPerPage)

    // Reset page when itemsPerPage changes
    useEffect(() => {
        setCurrentPage(1)
    }, [itemsPerPage, results])

    // --- Helper for Regime Display ---
    const renderRegimeInfo = (regimePerf: Record<string, any> | undefined) => {
        if (!regimePerf) return null;
        // Limit to Bull/Bear for simplicity
        const regimes = ['Bull', 'Bear'];

        // Check if we have any data to show
        const hasData = regimes.some(r => regimePerf[r] && regimePerf[r].count > 0);

        if (!hasData) return (
            <div className="mt-3 pt-3 border-t border-white/5">
                <p className="text-[10px] text-[var(--text-secondary)] uppercase font-bold mb-2 text-center">Win Rate por Cenário</p>
                <div className="text-xs text-gray-500 italic text-center py-2">Sem dados suficientes</div>
            </div>
        );

        return (
            <div className="mt-3 pt-3 border-t border-white/5">
                <p className="text-[10px] text-[var(--text-secondary)] uppercase font-bold mb-2">Win Rate por Cenário</p>
                <div className="grid grid-cols-2 gap-2">
                    {regimes.map(r => {
                        const stats = regimePerf[r];
                        if (!stats || !stats.count) {
                            return (
                                <div key={r} className="bg-white/5 rounded-lg p-2 flex flex-col items-center justify-center border border-white/5 opacity-50">
                                    <span className="text-[10px] font-bold uppercase tracking-wider mb-0.5 text-gray-500">
                                        {r === 'Bull' ? 'Alta' : 'Baixa'}
                                    </span>
                                    <span className="text-xs text-gray-600">-</span>
                                </div>
                            );
                        }

                        const wr = stats.win_rate || 0;
                        const count = stats.count || 0;

                        return (
                            <div key={r} className="bg-white/5 rounded-lg p-2 flex flex-col items-center justify-center border border-white/5">
                                <span className={`text-[10px] font-bold uppercase tracking-wider mb-0.5 ${r === 'Bull' ? 'text-green-400/80' : 'text-red-400/80'}`}>
                                    {r === 'Bull' ? 'Alta' : 'Baixa'}
                                </span>
                                <span className={`text-lg font-mono font-bold leading-none ${wr >= 50 ? 'text-green-400' : 'text-red-400'}`}>
                                    {wr.toFixed(0)}%
                                </span>
                                <span className="text-[9px] text-[var(--text-tertiary)] mt-1">
                                    {count} trades
                                </span>
                            </div>
                        )
                    })}
                </div>
            </div>
        )
    }


    return (
        <div className="space-y-6 animate-fade-in">
            {/* Key Metrics Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <Card className="p-6 relative overflow-hidden group">
                    <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
                        <TrendingUp className="w-16 h-16 text-[var(--accent-primary)]" />
                    </div>
                    <p className="text-sm text-[var(--text-secondary)] font-medium mb-1">Retorno Total</p>
                    <div className="mt-2 relative z-10">
                        <span className="text-3xl font-bold text-[var(--accent-primary)] tracking-tight block">
                            {bestResult?.metrics?.total_pnl_pct != null
                                ? `${(bestResult.metrics.total_pnl_pct * 100).toFixed(2)}%`
                                : '0.00%'}
                        </span>
                        <div className="flex items-center gap-2 text-sm text-[var(--text-tertiary)] mt-1 font-mono">
                            <span className="text-white bg-white/10 px-1.5 rounded text-xs py-0.5">
                                ${bestResult?.metrics?.total_pnl != null
                                    ? bestResult.metrics.total_pnl.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
                                    : '0.00'}
                            </span>
                            <span className="text-xs">Lucro Líquido</span>
                        </div>
                    </div>
                </Card>

                <Card className="p-6">
                    <p className="text-sm text-[var(--text-secondary)] font-medium mb-3 flex items-center gap-2">
                        <Shield className="w-4 h-4 text-orange-400" />
                        Análise de Risco
                    </p>
                    <div className="space-y-4">
                        <div className="flex justify-between items-center group w-full">
                            <span className="text-xs text-[var(--text-tertiary)] group-hover:text-[var(--text-secondary)] transition-colors pr-2">Expectativa / Trade</span>
                            <span className={`font-mono font-bold text-sm whitespace-nowrap ${bestResult?.metrics?.expectancy && bestResult.metrics.expectancy > 0 ? 'text-green-400' : 'text-red-400'}`}>
                                ${bestResult?.metrics?.expectancy?.toFixed(2) ?? 'N/A'}
                            </span>
                        </div>
                        <div className="flex justify-between items-center group w-full">
                            <span className="text-xs text-[var(--text-tertiary)] group-hover:text-[var(--text-secondary)] transition-colors pr-2">Seq. Perdas (Max)</span>
                            <span className="font-mono text-white text-sm bg-red-900/20 px-2 py-0.5 rounded text-red-200">
                                {bestResult?.metrics?.max_consecutive_losses ?? 0}
                            </span>
                        </div>
                        <div className="w-full h-px bg-white/5 my-2"></div>
                        <div className="flex justify-between items-center group w-full">
                            <div className="flex flex-col">
                                <span className="text-xs text-[var(--text-tertiary)] pr-2">Volatilidade (ATR)</span>
                            </div>
                            <span className="font-mono text-[var(--accent-secondary)] text-sm whitespace-nowrap">
                                {bestResult?.metrics?.avg_atr?.toFixed(2) ?? 'N/A'}
                            </span>
                        </div>
                    </div>
                </Card>

                <Card className="p-6 flex flex-col">
                    <p className="text-sm text-[var(--text-secondary)] font-medium mb-1 flex items-center gap-2">
                        <Award className="w-4 h-4 text-purple-400" />
                        Performance Contextual
                    </p>
                    {/* Regime Breakdown */}
                    <div className="flex-1">
                        {bestResult?.metrics?.regime_performance ? (
                            renderRegimeInfo(bestResult.metrics.regime_performance)
                        ) : (
                            <div className="h-full flex items-center justify-center text-xs text-gray-600 italic mt-4">
                                Sem dados de regime
                            </div>
                        )}
                    </div>
                    <div className="flex justify-between items-center pt-3 mt-auto border-t border-white/5">
                        <span className="text-[10px] text-[var(--text-tertiary)] uppercase font-bold pr-2">Força Tendência (ADX)</span>
                        <span className="text-sm font-bold text-yellow-400 font-mono whitespace-nowrap">
                            {bestResult?.metrics?.avg_adx?.toFixed(1) ?? 'N/A'}
                        </span>
                    </div>
                </Card>

                <Card className="p-6">
                    <p className="text-sm text-[var(--text-secondary)] font-medium mb-1">Estatísticas Gerais</p>
                    <div className="mt-4 space-y-4">
                        <div className="flex items-end justify-between">
                            <div>
                                <div className="text-xs text-[var(--text-tertiary)] uppercase tracking-wide mb-1">Taxa de Acerto</div>
                                <span className={`text-2xl font-bold ${bestResult?.metrics?.win_rate && bestResult.metrics.win_rate >= 50 ? 'text-green-400' : 'text-yellow-400'}`}>
                                    {bestResult?.metrics?.win_rate != null ? bestResult.metrics.win_rate.toFixed(1) : '0.0'}%
                                </span>
                            </div>
                            <div className="text-right">
                                <div className="text-xs text-[var(--text-tertiary)] uppercase tracking-wide mb-1">Trades</div>
                                <span className="text-xl font-bold text-white">
                                    {bestResult?.metrics?.total_trades || 0}
                                </span>
                            </div>
                        </div>

                        <div className="pt-3 border-t border-white/5">
                            <div className="flex justify-between items-center text-xs">
                                <span className="text-[var(--text-tertiary)]">Profit Factor</span>
                                <span className="font-mono text-white">
                                    {bestResult?.metrics?.profit_factor?.toFixed(2) ?? 'N/A'}
                                </span>
                            </div>
                        </div>
                    </div>
                </Card>
            </div>


            {/* Results Table with Pagination */}
            <Card className="p-0 overflow-hidden text-sm border-t border-white/10">
                <div className="p-6 border-b border-white/10 flex flex-col sm:flex-row justify-between items-center gap-4 bg-white/5">
                    <h3 className="text-lg font-bold text-red-500 flex items-center gap-2">
                        <TrendingUp className="w-4 h-4 text-blue-400" />
                        Resultados da Otimização (INLINE BORDERS)
                    </h3>

                    {/* Pagination Controls Header */}
                    <div className="flex items-center gap-4 text-xs font-medium text-[var(--text-secondary)]">
                        <div className="flex items-center gap-2 bg-black/20 rounded-lg p-1 border border-white/5">
                            <span className="pl-2">Linhas:</span>
                            <select
                                value={itemsPerPage}
                                onChange={(e) => setItemsPerPage(Number(e.target.value))}
                                className="bg-transparent border-none text-white focus:ring-0 cursor-pointer text-xs font-bold"
                            >
                                <option value={10}>10</option>
                                <option value={20}>20</option>
                                <option value={50}>50</option>
                                <option value={100}>100</option>
                                <option value={sortedResults.length}>Todos</option>
                            </select>
                        </div>
                        <span className="text-[var(--text-tertiary)]">
                            {startIndex + 1}-{Math.min(startIndex + itemsPerPage, sortedResults.length)} de <span className="text-white font-bold">{sortedResults.length}</span>
                        </span>
                    </div>
                </div>

                <div className="overflow-x-auto">
                    <table style={{ borderCollapse: 'collapse', border: '2px solid #4b5563', width: '100%' }}>
                        <thead>
                            <tr className="bg-black/50 text-left">
                                <th style={{ border: '1px solid #4b5563', padding: '12px 24px' }} className="text-xs font-bold text-[var(--text-tertiary)] uppercase tracking-wider">Rank</th>
                                <th style={{ border: '1px solid #4b5563', padding: '12px 24px' }} className="text-xs font-bold text-[var(--text-tertiary)] uppercase tracking-wider">Timeframe</th>
                                <th style={{ border: '1px solid #4b5563', padding: '12px 24px', textAlign: 'right' }} className="text-xs font-bold text-[var(--text-tertiary)] uppercase tracking-wider">Retorno</th>
                                <th style={{ border: '1px solid #4b5563', padding: '12px 24px', textAlign: 'right' }} className="text-xs font-bold text-[var(--text-tertiary)] uppercase tracking-wider">Lucro ($)</th>
                                <th style={{ border: '1px solid #4b5563', padding: '12px 24px', textAlign: 'right' }} className="text-xs font-bold text-[var(--text-tertiary)] uppercase tracking-wider">Trades</th>
                                {allParams.map((p) => (
                                    <th key={p} style={{ border: '1px solid #4b5563', padding: '12px 24px', textAlign: 'center' }} className="text-xs font-bold text-[var(--text-tertiary)] uppercase tracking-wider">{formatParamKey(p)}</th>
                                ))}
                                <th style={{ border: '1px solid #4b5563', padding: '12px 24px', textAlign: 'right' }} className="text-xs font-bold text-[var(--text-tertiary)] uppercase tracking-wider">Win Rate</th>
                            </tr>
                        </thead>
                        <tbody>
                            {displayedResults.map((r, i) => (
                                <tr
                                    key={startIndex + i}
                                    className={`transition-colors group ${i % 2 === 0
                                        ? 'bg-emerald-900/40 hover:bg-emerald-800/50'
                                        : 'bg-gray-800/40 hover:bg-gray-700/50'
                                        }`}
                                >
                                    <td style={{ border: '1px solid #4b5563', padding: '12px 24px' }} className="text-[var(--text-secondary)] font-mono text-xs">
                                        <span className={`inline-block w-6 text-right ${(startIndex + i) < 3 ? 'text-yellow-400 font-bold' : ''}`}>
                                            #{(startIndex + i + 1)}
                                        </span>
                                    </td>
                                    <td style={{ border: '1px solid #4b5563', padding: '12px 24px' }} className="font-mono text-blue-300 text-xs font-bold">{r.params.timeframe || timeframe || 'N/A'}</td>
                                    <td style={{ border: '1px solid #4b5563', padding: '12px 24px', textAlign: 'right' }} className={`font-mono font-bold text-sm ${r.metrics.total_pnl >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                                        {(r.metrics.total_pnl_pct * 100).toFixed(2)}%
                                    </td>
                                    <td style={{ border: '1px solid #4b5563', padding: '12px 24px', textAlign: 'right' }} className={`font-mono text-sm ${r.metrics.total_pnl >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                                        ${r.metrics.total_pnl.toFixed(2)}
                                    </td>
                                    <td style={{ border: '1px solid #4b5563', padding: '12px 24px', textAlign: 'right' }} className="font-mono text-white text-sm">
                                        {r.metrics.total_trades}
                                    </td>
                                    {allParams.map((p) => (
                                        <td key={p} style={{ border: '1px solid #4b5563', padding: '12px 24px', textAlign: 'center' }} className="font-mono text-gray-400 text-xs group-hover:text-white transition-colors">
                                            <span className="bg-white/5 px-2 py-0.5 rounded">
                                                {formatParamValue(p, r.params[p])}
                                            </span>
                                        </td>
                                    ))}
                                    <td style={{ border: '1px solid #4b5563', padding: '12px 24px', textAlign: 'right' }} className="font-mono text-white text-xs">{(r.metrics.win_rate * 100).toFixed(1)}%</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>

                {/* Pagination Footer */}
                {itemsPerPage < sortedResults.length && (
                    <div className="p-4 border-t border-white/10 flex justify-center items-center gap-2 bg-black/10">
                        <button
                            disabled={currentPage === 1}
                            onClick={() => setCurrentPage(prev => Math.max(1, prev - 1))}
                            className="px-3 py-1.5 bg-white/5 hover:bg-white/10 rounded-md text-xs font-medium disabled:opacity-30 disabled:cursor-not-allowed transition-all border border-white/5 hover:border-white/20"
                        >
                            Anterior
                        </button>

                        <div className="flex gap-1 bg-black/20 p-1 rounded-lg">
                            {Array.from({ length: Math.min(7, totalPages) }, (_, i) => {
                                let pageNum = i + 1;
                                // Simple logic to show range around current page if many pages
                                if (totalPages > 7) {
                                    if (currentPage <= 4) {
                                        pageNum = i + 1;
                                    } else if (currentPage >= totalPages - 3) {
                                        pageNum = totalPages - 6 + i;
                                    } else {
                                        pageNum = currentPage - 3 + i;
                                    }
                                }

                                return (
                                    <button
                                        key={pageNum}
                                        onClick={() => setCurrentPage(pageNum)}
                                        className={`w-7 h-7 flex items-center justify-center rounded-md text-xs font-bold transition-all ${currentPage === pageNum
                                            ? 'bg-blue-600 text-white shadow-lg shadow-blue-900/50'
                                            : 'text-gray-400 hover:text-white hover:bg-white/10'
                                            }`}
                                    >
                                        {pageNum}
                                    </button>
                                )
                            })}
                        </div>

                        <button
                            disabled={currentPage >= totalPages}
                            onClick={() => setCurrentPage(prev => Math.min(totalPages, prev + 1))}
                            className="px-3 py-1.5 bg-white/5 hover:bg-white/10 rounded-md text-xs font-medium disabled:opacity-30 disabled:cursor-not-allowed transition-all border border-white/5 hover:border-white/20"
                        >
                            Próximo
                        </button>
                    </div>
                )}
            </Card>
        </div>
    )
}
