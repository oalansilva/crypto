// src/components/TradesTable.tsx
import { useState } from 'react'
import { TrendingUp, TrendingDown, ArrowUpDown } from 'lucide-react'

interface Trade {
    entry_time: string
    exit_time: string
    entry_price: number
    exit_price: number
    size: number
    pnl: number
    pnl_pct: number
    side: 'long' | 'short'
}

interface TradesTableProps {
    trades: Trade[]
    strategyName: string
    color: string
}

export function TradesTable({ trades, strategyName, color }: TradesTableProps) {
    const [sortBy, setSortBy] = useState<'time' | 'pnl'>('time')
    const [filterSide, setFilterSide] = useState<'all' | 'long' | 'short'>('all')

    const filteredTrades = trades.filter(trade => {
        if (filterSide === 'all') return true
        return trade.side === filterSide
    })

    const sortedTrades = [...filteredTrades].sort((a, b) => {
        if (sortBy === 'time') {
            return new Date(b.entry_time).getTime() - new Date(a.entry_time).getTime()
        }
        return b.pnl - a.pnl
    })

    const winningTrades = trades.filter(t => t.pnl > 0).length
    const losingTrades = trades.filter(t => t.pnl < 0).length
    const totalPnl = trades.reduce((sum, t) => sum + t.pnl, 0)

    return (
        <div className="glass-strong rounded-2xl p-6 border border-white/10">
            {/* Header */}
            <div className="flex items-center justify-between mb-6">
                <div className="flex items-center gap-3">
                    <div
                        className="p-2.5 rounded-xl"
                        style={{ backgroundColor: `${color}20` }}
                    >
                        <ArrowUpDown className="w-6 h-6" style={{ color }} />
                    </div>
                    <div>
                        <h3 className="text-xl font-bold text-white">{strategyName} Trades</h3>
                        <p className="text-sm text-gray-400">
                            {winningTrades}W / {losingTrades}L • Total P&L:
                            <span className={totalPnl >= 0 ? 'text-emerald-400' : 'text-rose-400'}>
                                {' '}${totalPnl.toFixed(2)}
                            </span>
                        </p>
                    </div>
                </div>

                {/* Filters */}
                <div className="flex gap-2">
                    <select
                        value={sortBy}
                        onChange={(e) => setSortBy(e.target.value as 'time' | 'pnl')}
                        className="glass px-4 py-2 rounded-lg border border-white/10 text-white text-sm focus:border-blue-500 focus:outline-none"
                    >
                        <option value="time" className="bg-slate-900">Recent First</option>
                        <option value="pnl" className="bg-slate-900">Best P&L</option>
                    </select>

                    <select
                        value={filterSide}
                        onChange={(e) => setFilterSide(e.target.value as 'all' | 'long' | 'short')}
                        className="glass px-4 py-2 rounded-lg border border-white/10 text-white text-sm focus:border-blue-500 focus:outline-none"
                    >
                        <option value="all" className="bg-slate-900">All Sides</option>
                        <option value="long" className="bg-slate-900">Long Only</option>
                        <option value="short" className="bg-slate-900">Short Only</option>
                    </select>
                </div>
            </div>

            {/* Table */}
            <div className="overflow-x-auto">
                <table className="w-full">
                    <thead>
                        <tr className="border-b border-white/10">
                            <th className="px-4 py-3 text-left text-xs font-semibold text-gray-400 uppercase">Side</th>
                            <th className="px-4 py-3 text-left text-xs font-semibold text-gray-400 uppercase">Entry</th>
                            <th className="px-4 py-3 text-left text-xs font-semibold text-gray-400 uppercase">Exit</th>
                            <th className="px-4 py-3 text-right text-xs font-semibold text-gray-400 uppercase">Entry Price</th>
                            <th className="px-4 py-3 text-right text-xs font-semibold text-gray-400 uppercase">Exit Price</th>
                            <th className="px-4 py-3 text-right text-xs font-semibold text-gray-400 uppercase">Size</th>
                            <th className="px-4 py-3 text-right text-xs font-semibold text-gray-400 uppercase">P&L</th>
                            <th className="px-4 py-3 text-right text-xs font-semibold text-gray-400 uppercase">P&L %</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-white/5">
                        {sortedTrades.slice(0, 50).map((trade, index) => (
                            <tr key={index} className="hover:bg-white/5 transition-colors">
                                <td className="px-4 py-3">
                                    <span className={`px-2 py-1 rounded-md text-xs font-semibold ${trade.side === 'long'
                                        ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                                        : 'bg-rose-500/20 text-rose-400 border border-rose-500/30'
                                        }`}>
                                        {trade.side.toUpperCase()}
                                    </span>
                                </td>
                                <td className="px-4 py-3 text-sm text-gray-300">
                                    {new Date(trade.entry_time).toLocaleString('pt-BR', {
                                        day: '2-digit',
                                        month: '2-digit',
                                        year: 'numeric',
                                        hour: '2-digit',
                                        minute: '2-digit',
                                        second: '2-digit',
                                        timeZone: 'UTC'
                                    })}
                                </td>
                                <td className="px-4 py-3 text-sm text-gray-300">
                                    {new Date(trade.exit_time).toLocaleString('pt-BR', {
                                        day: '2-digit',
                                        month: '2-digit',
                                        year: 'numeric',
                                        hour: '2-digit',
                                        minute: '2-digit',
                                        second: '2-digit',
                                        timeZone: 'UTC'
                                    })}
                                </td>
                                <td className="px-4 py-3 text-right text-sm text-white font-mono">
                                    ${(trade.entry_price ?? 0).toFixed(2)}
                                </td>
                                <td className="px-4 py-3 text-right text-sm text-white font-mono">
                                    ${(trade.exit_price ?? 0).toFixed(2)}
                                </td>
                                <td className="px-4 py-3 text-right text-sm text-gray-300 font-mono">
                                    {(trade.size ?? 0).toFixed(4)}
                                </td>
                                <td className="px-4 py-3 text-right">
                                    <div className={`flex items-center justify-end gap-1 font-semibold ${trade.pnl >= 0 ? 'text-emerald-400' : 'text-rose-400'
                                        }`}>
                                        {trade.pnl >= 0 ? (
                                            <TrendingUp className="w-4 h-4" />
                                        ) : (
                                            <TrendingDown className="w-4 h-4" />
                                        )}
                                        <span className="font-mono">${Math.abs(trade.pnl ?? 0).toFixed(2)}</span>
                                    </div>
                                </td>
                                <td className="px-4 py-3 text-right">
                                    <span className={`font-semibold font-mono ${trade.pnl_pct >= 0 ? 'text-emerald-400' : 'text-rose-400'
                                        }`}>
                                        {trade.pnl_pct >= 0 ? '+' : ''}{((trade.pnl_pct ?? 0) * 100).toFixed(2)}%
                                    </span>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>

            {sortedTrades.length > 50 && (
                <div className="mt-4 text-center text-sm text-gray-400">
                    Showing 50 of {sortedTrades.length} trades
                </div>
            )}

            {sortedTrades.length === 0 && (
                <div className="text-center py-12 text-gray-400">
                    No trades match the selected filters
                </div>
            )}
        </div>
    )
}
