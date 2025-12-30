import { useState, useMemo, useEffect } from 'react'
import { Card } from '../ui'
import {
    ScatterChart,
    Scatter,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer
} from 'recharts'
import { TrendingUp, Filter } from 'lucide-react'

interface OptimizationItem {
    params: Record<string, any>
    metrics: {
        total_pnl: number
        total_pnl_pct: number
        win_rate: number
        total_trades: number
        max_drawdown: number
        profit_factor: number
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

// Helper to identify which params actually change values
function getVaryingParams(results: OptimizationItem[]) {
    const paramValues: Record<string, Set<any>> = {}

    // Initialize sets
    if (results.length > 0) {
        Object.keys(results[0].params).forEach(k => {
            paramValues[k] = new Set()
        })
    }

    // Collect all values
    results.forEach(r => {
        Object.entries(r.params).forEach(([k, v]) => {
            if (!paramValues[k]) paramValues[k] = new Set()
            paramValues[k].add(JSON.stringify(v)) // Stringify to handle objects/arrays uniqueness
        })
    })

    // Return keys with > 1 unique value
    return Object.keys(paramValues).filter(k => paramValues[k].size > 1)
}

function formatParamKey(key: string): string {
    return key.replace(/_/g, ' ').toUpperCase()
}

function formatParamValue(key: string, val: any): string {
    if (val === null || val === undefined) return 'N/A'
    if (typeof val === 'number') {
        // Detect percentage fields by key name
        if (key.toLowerCase().endsWith('pct') || key === 'stop_loss' || key === 'take_profit') {
            // Heuristic: if value is small (< 1), assuming it's decimal representation of percentage
            // But valid percentage could be 0.5 (meaning 0.5% or 50%?). 
            // In our system, 0.015 is 1.5%. 
            return `${(val * 100).toLocaleString('en-US', { maximumFractionDigits: 2 })}%`
        }
        return val.toString()
    }
    return String(val)
}

export function OptimizationResults({ results, bestResult, timeframe }: OptimizationResultsProps) {
    // Identify which params actually vary (for chart axis selector)
    const varyingParams = getVaryingParams(results)

    // Get all relevant params (for table display)
    const allParams = getAllRelevantParams(results)

    // Prepare chart data
    const xAxisParam = useMemo(() => {
        return varyingParams.length > 0 ? varyingParams[0] : ''
    }, [varyingParams])

    const [activeXAxis, setActiveXAxis] = useState(xAxisParam)

    // Update activeXAxis if params change
    useEffect(() => {
        if (xAxisParam) setActiveXAxis(xAxisParam)
    }, [xAxisParam])

    const chartData = useMemo(() => {
        if (!activeXAxis) return []
        return results.map((r, idx) => ({
            id: idx,
            [activeXAxis]: r.params[activeXAxis],
            pnl: r.metrics.total_pnl_pct * 100, // Convert to %
            trades: r.metrics.total_trades,
            win_rate: r.metrics.win_rate * 100,
            ...r.params // Include all params for tooltip
        }))
    }, [results, activeXAxis])

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

    return (
        <div className="space-y-6 animate-fade-in">
            {/* Key Metrics Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <Card className="p-6">
                    <p className="text-sm text-[var(--text-secondary)] font-medium mb-1">Melhor Retorno</p>
                    <div className="mt-2">
                        <span className="text-2xl font-bold text-[var(--accent-primary)]">
                            {bestResult?.metrics?.total_pnl_pct != null
                                ? `${(bestResult.metrics.total_pnl_pct * 100).toFixed(2)}%`
                                : '0.00%'}
                        </span>
                        <div className="flex items-center gap-1 text-sm text-[var(--text-tertiary)] mt-1">
                            <span>PnL:</span>
                            <span className="text-white">
                                ${bestResult?.metrics?.total_pnl != null
                                    ? bestResult.metrics.total_pnl.toFixed(2)
                                    : '0.00'}
                            </span>
                        </div>
                        <div className="mt-2">
                            <TrendingUp className="w-5 h-5 text-[var(--accent-primary)]" />
                        </div>
                    </div>
                </Card>

                <Card className="p-6">
                    <p className="text-sm text-[var(--text-secondary)] font-medium mb-1">Melhor Configuração</p>
                    <div className="space-y-3 mt-4">
                        {bestResult?.params ? Object.entries(bestResult.params)
                            .filter(([_, val]) => val !== null && val !== undefined && val !== '')
                            .map(([key, val]) => (
                                <div key={key} className="flex justify-between items-center text-sm border-b border-white/5 pb-2 last:border-0 last:pb-0">
                                    <span className="text-[var(--text-tertiary)] text-xs font-semibold tracking-wider">{formatParamKey(key)}</span>
                                    <span className="text-white font-mono bg-white/5 px-2 py-0.5 rounded text-xs">
                                        {formatParamValue(key, val)}
                                    </span>
                                </div>
                            )) : <p className="text-gray-500 text-sm">Nenhum resultado</p>}
                    </div>
                </Card>

                <Card className="p-6">
                    <p className="text-sm text-[var(--text-secondary)] font-medium mb-1">Trades & Win Rate</p>
                    <div className="mt-4 space-y-3">
                        <div className="flex justify-between items-center mb-2">
                            <span className="text-2xl font-bold text-white">
                                {bestResult?.metrics?.win_rate != null ? bestResult.metrics.win_rate.toFixed(1) : '0.0'}%
                            </span>
                            <span className="text-xs text-[var(--text-tertiary)] uppercase tracking-wide">Taxa de Acerto</span>
                        </div>
                        <div className="flex justify-between items-center">
                            <span className="text-xl font-bold text-white">
                                {bestResult?.metrics?.total_trades || 0}
                            </span>
                            <span className="text-xs text-[var(--text-tertiary)] uppercase tracking-wide">Trades Totais</span>
                        </div>
                    </div>
                </Card>
            </div>

            {/* Chart Section */}
            {varyingParams.length > 0 ? (
                <Card className="p-6">
                    <div className="flex justify-between items-center mb-6">
                        <h3 className="text-xl font-bold text-white flex items-center gap-2">
                            <Filter className="w-5 h-5 text-blue-400" />
                            Dispersão de Resultados
                        </h3>

                        {/* Axis Selector */}
                        <div className="flex items-center gap-2">
                            <span className="text-sm text-gray-400">Eixo X:</span>
                            <div className="flex bg-[var(--bg-elevated)] rounded-lg p-1">
                                {varyingParams.map(param => (
                                    <button
                                        key={param}
                                        onClick={() => setActiveXAxis(param)}
                                        className={`px-3 py-1 text-xs font-bold rounded-md transition-all ${activeXAxis === param
                                            ? 'bg-blue-600 text-white'
                                            : 'text-gray-400 hover:text-white'
                                            }`}
                                    >
                                        {param.toUpperCase()}
                                    </button>
                                ))}
                            </div>
                        </div>
                    </div>

                    <div className="w-full h-[400px]">
                        <ResponsiveContainer width="100%" height={400}>
                            <ScatterChart margin={{ top: 20, right: 30, bottom: 20, left: 10 }}>
                                <CartesianGrid strokeDasharray="3 3" stroke="#334155" opacity={0.5} />
                                <XAxis
                                    type="number"
                                    dataKey={activeXAxis}
                                    name={activeXAxis}
                                    unit=""
                                    stroke="#94a3b8"
                                    tick={{ fill: '#94a3b8', fontSize: 12 }}
                                    domain={['auto', 'auto']}
                                />
                                <YAxis
                                    type="number"
                                    dataKey="pnl"
                                    name="PnL %"
                                    unit="%"
                                    stroke="#94a3b8"
                                    tick={{ fill: '#94a3b8', fontSize: 12 }}
                                />
                                <Tooltip
                                    cursor={{ strokeDasharray: '3 3' }}
                                    content={({ active, payload }) => {
                                        if (active && payload && payload.length) {
                                            const data = payload[0].payload
                                            return (
                                                <div className="bg-gray-900 border border-gray-700 p-3 rounded-lg shadow-xl">
                                                    <p className="text-white font-bold mb-2">Resultado #{data.id + 1}</p>
                                                    <div className="space-y-1 text-xs">
                                                        <p className="text-blue-400">PnL: {data.pnl.toFixed(2)}%</p>
                                                        <p className="text-gray-300">Trades: {data.trades}</p>
                                                        <div className="border-t border-gray-700 my-2 pt-2">
                                                            {varyingParams.map(p => (
                                                                <p key={p} className="text-gray-400 flex justify-between gap-4">
                                                                    <span>{formatParamKey(p)}:</span>
                                                                    <span className="text-white font-mono">{formatParamValue(p, data[p])}</span>
                                                                </p>
                                                            ))}
                                                        </div>
                                                    </div>
                                                </div>
                                            )
                                        }
                                        return null
                                    }}
                                />
                                <Scatter name="Execuções" data={chartData} fill="#3b82f6" fillOpacity={0.6} />
                            </ScatterChart>
                        </ResponsiveContainer>
                    </div>
                </Card>
            ) : (
                <Card className="p-6">
                    <div className="text-center text-gray-500 py-12">
                        <Filter className="w-12 h-12 mx-auto mb-4 opacity-50" />
                        <p>Nenhum parâmetro variável detectado para gerar gráfico</p>
                    </div>
                </Card>
            )}

            {/* Results Table with Pagination */}
            <Card className="p-0 overflow-hidden text-sm border-t border-white/10">
                <div className="p-6 border-b border-white/10 flex flex-col sm:flex-row justify-between items-center gap-4 bg-white/5">
                    <h3 className="text-lg font-bold text-red-500 flex items-center gap-2">
                        <TrendingUp className="w-4 h-4 text-blue-400" />
                        Resultados da Otimização (DEBUG MODE)
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
                    <table className="w-full whitespace-nowrap">
                        <thead>
                            <tr className="bg-black/20 text-left">
                                <th className="py-3 px-6 text-xs font-bold text-[var(--text-tertiary)] uppercase tracking-wider border-b border-white/5">Rank</th>
                                <th className="py-3 px-6 text-xs font-bold text-[var(--text-tertiary)] uppercase tracking-wider border-b border-white/5">Timeframe</th>
                                <th className="py-3 px-6 text-xs font-bold text-[var(--text-tertiary)] uppercase tracking-wider border-b border-white/5 text-right">Retorno</th>
                                <th className="py-3 px-6 text-xs font-bold text-[var(--text-tertiary)] uppercase tracking-wider border-b border-white/5 text-right">Lucro ($)</th>
                                {allParams.map(p => (
                                    <th key={p} className="py-3 px-6 text-xs font-bold text-[var(--text-tertiary)] uppercase tracking-wider border-b border-white/5 text-center">{formatParamKey(p)}</th>
                                ))}
                                <th className="py-3 px-6 text-xs font-bold text-[var(--text-tertiary)] uppercase tracking-wider border-b border-white/5 text-right">Win Rate</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-white/5">
                            {displayedResults.map((r, i) => (
                                <tr key={startIndex + i} className="hover:bg-white/5 transition-colors group">
                                    <td className="py-3 px-6 text-[var(--text-secondary)] font-mono text-xs">
                                        <span className={`inline-block w-6 text-right ${(startIndex + i) < 3 ? 'text-yellow-400 font-bold' : ''}`}>
                                            #{(startIndex + i + 1)}
                                        </span>
                                    </td>
                                    <td className="py-3 px-6 font-mono text-blue-300 text-xs font-bold">{r.params.timeframe || timeframe || 'N/A'}</td>
                                    <td className={`py-3 px-6 font-mono font-bold text-right text-sm ${r.metrics.total_pnl >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                                        {(r.metrics.total_pnl_pct * 100).toFixed(2)}%
                                    </td>
                                    <td className={`py-3 px-6 font-mono text-right text-sm ${r.metrics.total_pnl >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                                        ${r.metrics.total_pnl.toFixed(2)}
                                    </td>
                                    {allParams.map(p => (
                                        <td key={p} className="py-3 px-6 font-mono text-gray-400 text-center text-xs group-hover:text-white transition-colors">
                                            <span className="bg-white/5 px-2 py-0.5 rounded">
                                                {formatParamValue(p, r.params[p])}
                                            </span>
                                        </td>
                                    ))}
                                    <td className="py-3 px-6 font-mono text-white text-right text-xs">{(r.metrics.win_rate * 100).toFixed(1)}%</td>
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
