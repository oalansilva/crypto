import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { Bookmark, Play, Trash2, Search, List, ChevronDown } from 'lucide-react';
import TradesViewModal from '../components/TradesViewModal';

import * as XLSX from 'xlsx';

interface FavoriteStrategy {
    id: number;
    name: string;
    symbol: string;
    timeframe: string;
    strategy_name: string;
    parameters: Record<string, any>;
    metrics: Record<string, any>;
    notes?: string;
    created_at: string;
}

const FavoritesDashboard: React.FC = () => {
    const navigate = useNavigate();
    const queryClient = useQueryClient();
    const [searchTerm, setSearchTerm] = useState('');
    const [selectedIds, setSelectedIds] = useState<number[]>([]);
    const [isCompareOpen, setIsCompareOpen] = useState(false);

    // New state for Trades Modal
    const [isTradesModalOpen, setIsTradesModalOpen] = useState(false);
    const [selectedTrades, setSelectedTrades] = useState<any[]>([]);
    const [selectedTradesTitle, setSelectedTradesTitle] = useState('');

    // Fetch favorites
    const { data: favorites, isLoading } = useQuery({
        queryKey: ['favorites'],
        queryFn: async () => {
            const res = await fetch('http://localhost:8000/api/favorites/');
            if (!res.ok) throw new Error('Failed to fetch favorites');
            const data = await res.json() as FavoriteStrategy[];
            console.log('📥 Loaded favorites:', data);
            if (data && data.length > 0) {
                console.log('   First favorite max_loss:', data[0].metrics?.max_loss);
            }
            return data;
        }
    });

    // Delete mutation
    const deleteMutation = useMutation({
        mutationFn: async (id: number) => {
            const res = await fetch(`http://localhost:8000/api/favorites/${id}`, {
                method: 'DELETE'
            });
            if (!res.ok) throw new Error('Failed to delete');
        },
        onSuccess: (_, id) => {
            queryClient.invalidateQueries({ queryKey: ['favorites'] });
            setSelectedIds(prev => prev.filter(sid => sid !== id));
        }
    });

    const handleRun = (fav: FavoriteStrategy) => {
        const params = new URLSearchParams();
        params.set('symbol', fav.symbol);
        params.set('timeframe', fav.timeframe);
        params.set('strategy', fav.strategy_name);
        Object.entries(fav.parameters).forEach(([key, value]) => {
            params.set(key, String(value));
        });
        navigate(`/optimize/risk?${params.toString()}`);
    };

    const handleDelete = (id: number) => {
        if (confirm('Are you sure you want to delete this strategy?')) {
            deleteMutation.mutate(id);
        }
    };

    const toggleSelection = (id: number) => {
        if (selectedIds.includes(id)) {
            setSelectedIds(selectedIds.filter(sid => sid !== id));
        } else {
            if (selectedIds.length >= 3) {
                alert("You can compare up to 3 strategies at a time.");
                return;
            }
            setSelectedIds([...selectedIds, id]);
        }
    };

    const handleViewTrades = (fav: FavoriteStrategy) => {
        const trades = fav.metrics?.trades || [];
        if (!trades || trades.length === 0) {
            alert('No trades saved for this strategy.');
            return;
        }
        setSelectedTrades(trades);
        setSelectedTradesTitle(`${fav.strategy_name} - ${fav.symbol} ${fav.timeframe}`);
        setIsTradesModalOpen(true);
    };

    const [selectedSymbol, setSelectedSymbol] = useState<string>('ALL');
    const [selectedIndicator, setSelectedIndicator] = useState<string>('ALL');

    // ... existing code ...

    // Get unique symbols for filter
    const uniqueSymbols = React.useMemo(() => {
        if (!favorites) return [];
        return Array.from(new Set(favorites.map(f => f.symbol))).sort();
    }, [favorites]);

    // Get unique indicators (strategies) for filter
    const uniqueIndicators = React.useMemo(() => {
        if (!favorites) return [];
        return Array.from(new Set(favorites.map(f => f.strategy_name))).sort();
    }, [favorites]);

    const filteredFavorites = (favorites?.filter(fav => {
        const matchesSearch = fav.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
            fav.symbol.toLowerCase().includes(searchTerm.toLowerCase()) ||
            fav.strategy_name.toLowerCase().includes(searchTerm.toLowerCase());

        const matchesSymbol = selectedSymbol === 'ALL' || fav.symbol === selectedSymbol;
        const matchesIndicator = selectedIndicator === 'ALL' || fav.strategy_name === selectedIndicator;

        return matchesSearch && matchesSymbol && matchesIndicator;
    }) || []).sort((a, b) => {
        const valA = a.metrics?.total_return_pct ?? a.metrics?.total_return ?? -Infinity;
        const valB = b.metrics?.total_return_pct ?? b.metrics?.total_return ?? -Infinity;
        return valB - valA; // Descending
    });

    const selectedStrategies = favorites?.filter(f => selectedIds.includes(f.id)) || [];

    const handleExportExcel = () => {
        if (!favorites || favorites.length === 0) {
            alert("No data to export.");
            return;
        }

        // Prepare data for export
        const dataToExport = filteredFavorites.map(fav => {
            const m = fav.metrics || {};
            // derived
            const totalReturn = m.total_return_pct ?? m.total_return;
            const expectancy = m.expectancy ?? (m.total_pnl && m.total_trades ? m.total_pnl / m.total_trades : null);
            const stopLoss = fav.parameters.stop_loss || null;

            return {
                Name: fav.name,
                Symbol: fav.symbol,
                Strategy: fav.strategy_name,
                Timeframe: fav.timeframe,
                Parameters: formatParams(fav.parameters),
                "Stop Loss": formatPct(stopLoss),
                Sharpe: formatNum(m.sharpe_ratio),
                Trades: m.total_trades || m.trades || 0,
                "Win Rate": formatPct(m.win_rate),
                "Total Return": formatPct(totalReturn),
                "Exp/Trade": formatCurrency(expectancy),
                "Max DD": formatPct(m.max_drawdown),
                "Profit Factor": formatNum(m.profit_factor),
                Sortino: formatNum(m.sortino),
                "Max Loss": m.max_consecutive_losses ?? m.stop_loss_count ?? 0,
                "Avg ATR": formatNum(m.avg_atr),
                "WR Bull": formatPct(m.win_rate_bull),
                "WR Bear": formatPct(m.win_rate_bear),
                "Avg ADX": formatNum(m.avg_adx),
                Notes: fav.notes || '',
                "Created At": new Date(fav.created_at).toLocaleString()
            };
        });

        // Create workbook
        const ws = XLSX.utils.json_to_sheet(dataToExport);
        const wb = XLSX.utils.book_new();
        XLSX.utils.book_append_sheet(wb, ws, "Favorites");

        // Generate filename
        const filename = `Crypto_Backtest_Favorites_${new Date().toISOString().slice(0, 10)}.xlsx`;

        // Download
        XLSX.writeFile(wb, filename);
    };

    // Formatters
    const formatParams = (params: Record<string, any>) => {
        return Object.entries(params)
            .map(([k, v]) => `${k}=${v}`)
            .join('&');
    };

    const formatPct = (val?: number) => {
        if (val === undefined || val === null) return '-';
        return val > 1 || val < -1 ? `${val.toFixed(2)}%` : `${(val * 100).toFixed(2)}%`;
    };

    const formatNum = (val?: number, decimals = 2) => {
        if (val === undefined || val === null) return '-';
        return val.toFixed(decimals);
    };

    const formatCurrency = (val?: number) => {
        if (val === undefined || val === null) return '-';
        return `$${val.toFixed(2)}`;
    };

    return (
        <div className="min-h-screen bg-gray-900 text-white p-4">
            <div className="max-w-[1920px] mx-auto">
                {/* Header */}
                <div className="flex justify-between items-center mb-6">
                    <div className="flex items-center gap-3">
                        <Bookmark className="w-6 h-6 text-purple-500" />
                        <h1 className="text-2xl font-bold text-gray-100">Favorite Strategies</h1>
                    </div>

                    <div className="flex items-center gap-4">
                        {/* Symbol Filter */}
                        <div className="relative">
                            <select
                                value={selectedSymbol}
                                onChange={(e) => setSelectedSymbol(e.target.value)}
                                className="bg-gray-800 border border-gray-700 rounded-lg pl-3 pr-8 py-1.5 text-sm text-white focus:ring-1 focus:ring-purple-500 outline-none appearance-none cursor-pointer hover:bg-gray-750"
                            >
                                <option value="ALL">All Symbols</option>
                                {uniqueSymbols.map(sym => (
                                    <option key={sym} value={sym}>{sym}</option>
                                ))}
                            </select>
                            <div className="absolute right-2 top-1/2 transform -translate-y-1/2 pointer-events-none">
                                <ChevronDown className="w-4 h-4 text-gray-400" />
                            </div>
                        </div>

                        {/* Indicator Filter */}
                        <div className="relative">
                            <select
                                value={selectedIndicator}
                                onChange={(e) => setSelectedIndicator(e.target.value)}
                                className="bg-gray-800 border border-gray-700 rounded-lg pl-3 pr-8 py-1.5 text-sm text-white focus:ring-1 focus:ring-purple-500 outline-none appearance-none cursor-pointer hover:bg-gray-750"
                            >
                                <option value="ALL">All Strategies</option>
                                {uniqueIndicators.map(ind => (
                                    <option key={ind} value={ind}>{ind}</option>
                                ))}
                            </select>
                            <div className="absolute right-2 top-1/2 transform -translate-y-1/2 pointer-events-none">
                                <ChevronDown className="w-4 h-4 text-gray-400" />
                            </div>
                        </div>

                        <div className="relative">
                            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-500 w-4 h-4" />
                            <input
                                type="text"
                                placeholder="Search..."
                                value={searchTerm}
                                onChange={(e) => setSearchTerm(e.target.value)}
                                className="bg-gray-800 border border-gray-700 rounded-lg pl-9 pr-4 py-1.5 text-sm text-white focus:ring-1 focus:ring-purple-500 outline-none w-64"
                            />
                        </div>
                        <button
                            onClick={handleExportExcel}
                            className="bg-green-600 hover:bg-green-700 text-white px-4 py-1.5 rounded-lg text-sm font-medium transition-colors flex items-center gap-2"
                        >
                            <List className="w-4 h-4" /> Export Excel
                        </button>
                        <button
                            onClick={() => navigate('/optimize/parameters')}
                            className="px-4 py-1.5 bg-purple-600 hover:bg-purple-700 text-sm font-medium rounded-lg transition-colors"
                        >
                            Find New Strategies
                        </button>
                    </div>
                </div>

                {/* Table Container */}
                <div className="bg-gray-800 border border-gray-600 rounded-lg overflow-hidden shadow-xl ring-1 ring-gray-700">
                    <div className="overflow-x-auto">
                        <table className="w-full text-left border-collapse text-sm"> {/* Changed text-xs to text-sm */}
                            <thead className="bg-gray-900/95 text-gray-300 font-bold uppercase tracking-wider backdrop-blur-sm sticky top-0 z-10">
                                <tr>
                                    <th className="p-3 border-b-2 border-gray-600 w-10 text-center bg-gray-900">
                                        <input type="checkbox" disabled className="rounded border-gray-500 bg-gray-800" />
                                    </th>
                                    <th className="p-3 border-b-2 border-gray-600 border-r border-gray-700 font-bold text-white bg-gray-900">Moeda</th>
                                    <th className="p-3 border-b-2 border-gray-600 border-r border-gray-700 font-bold text-white bg-gray-900">Indicador</th>
                                    <th className="p-3 border-b-2 border-gray-600 border-r border-gray-700 font-bold text-white bg-gray-900">TimeFrame</th>
                                    <th className="p-3 border-b-2 border-gray-600 border-r border-gray-700 font-bold text-white w-96 bg-gray-900">Parametros</th>
                                    <th className="p-3 border-b-2 border-gray-600 border-r border-gray-700 text-right text-gray-200 bg-gray-900">Stop</th>
                                    <th className="p-3 border-b-2 border-gray-600 border-r border-gray-700 text-right text-gray-200 bg-gray-900">Sharpe</th>
                                    <th className="p-3 border-b-2 border-gray-600 border-r border-gray-700 text-right text-gray-200 bg-gray-900">Trades</th>
                                    <th className="p-3 border-b-2 border-gray-600 border-r border-gray-700 text-right text-gray-200 bg-gray-900">Win Rate</th>
                                    <th className="p-3 border-b-2 border-gray-600 border-r border-gray-700 text-right text-gray-200 bg-gray-900">Retorno Total</th>
                                    <th className="p-3 border-b-2 border-gray-600 border-r border-gray-700 text-right text-gray-200 bg-gray-900">Exp/Trade</th>
                                    <th className="p-3 border-b-2 border-gray-600 border-r border-gray-700 text-right text-gray-200 bg-gray-900">Max DD</th>
                                    <th className="p-3 border-b-2 border-gray-600 border-r border-gray-700 text-right text-gray-200 bg-gray-900">Profit Factor</th>
                                    <th className="p-3 border-b-2 border-gray-600 border-r border-gray-700 text-right text-gray-200 bg-gray-900">Sortino</th>
                                    <th className="p-3 border-b-2 border-gray-600 border-r border-gray-700 text-right text-gray-200 bg-gray-900">Max Loss</th>
                                    <th className="p-3 border-b-2 border-gray-600 border-r border-gray-700 text-right text-gray-200 bg-gray-900">Avg ATR</th>
                                    <th className="p-3 border-b-2 border-gray-600 border-r border-gray-700 text-right text-gray-200 bg-gray-900">WR Bull</th>
                                    <th className="p-3 border-b-2 border-gray-600 border-r border-gray-700 text-right text-gray-200 bg-gray-900">WR Bear</th>
                                    <th className="p-3 border-b-2 border-gray-600 border-r border-gray-700 text-right text-gray-200 bg-gray-900">Avg ADX</th>
                                    <th className="p-3 border-b-2 border-gray-600 border-r border-gray-700 text-left text-gray-200 bg-gray-900">Notes</th>
                                    <th className="p-3 border-b-2 border-gray-600 text-center text-gray-200 bg-gray-900">Actions</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-gray-700">
                                {isLoading ? (
                                    <tr><td colSpan={14} className="p-8 text-center text-gray-500">Loading data...</td></tr>
                                ) : filteredFavorites.length === 0 ? (
                                    <tr><td colSpan={14} className="p-8 text-center text-gray-500">No favorites found. Save some strategies first!</td></tr>
                                ) : (
                                    filteredFavorites.map((fav, index) => {
                                        const isSelected = selectedIds.includes(fav.id);
                                        const m = fav.metrics || {};
                                        // Try to find derived metrics, fallback to N/A
                                        const totalReturn = m.total_return_pct ?? m.total_return;
                                        const expectancy = m.expectancy ?? (m.total_pnl && m.total_trades ? m.total_pnl / m.total_trades : null);
                                        // Stop loss usually in parameters
                                        const stopLoss = fav.parameters.stop_loss ? fav.parameters.stop_loss : null;

                                        return (
                                            <tr
                                                key={fav.id}
                                                className={`
                                                    group transition-colors
                                                    ${isSelected ? 'bg-purple-900/30' : (index % 2 === 0 ? 'bg-gray-800/40' : 'bg-transparent')}
                                                    hover:bg-gray-700
                                                `}
                                            >
                                                <td className="p-3 border-r border-gray-600 border-b border-gray-700 text-center">
                                                    <input
                                                        type="checkbox"
                                                        checked={isSelected}
                                                        onChange={() => toggleSelection(fav.id)}
                                                        className="rounded border-gray-500 bg-gray-700 text-purple-500 focus:ring-offset-0 focus:ring-1 focus:ring-purple-500 cursor-pointer"
                                                    />
                                                </td>
                                                <td className="p-3 border-r border-gray-600 border-b border-gray-700 font-bold text-gray-100">{fav.symbol}</td>
                                                <td className="p-3 border-r border-gray-600 border-b border-gray-700 text-blue-300 font-medium">{fav.strategy_name}</td>
                                                <td className="p-3 border-r border-gray-600 border-b border-gray-700 text-center bg-gray-800/20 text-gray-200">{fav.timeframe}</td>
                                                <td className="p-3 border-r border-gray-600 border-b border-gray-700 font-mono text-gray-300 truncate max-w-xs text-xs" title={formatParams(fav.parameters)}>
                                                    {formatParams(fav.parameters)}
                                                </td>
                                                <td className="p-3 border-r border-gray-600 border-b border-gray-700 text-right font-mono text-gray-200">
                                                    {formatPct(stopLoss)}
                                                </td>
                                                <td className="p-3 border-r border-gray-600 border-b border-gray-700 text-right font-mono text-white font-bold">
                                                    {formatNum(m.sharpe_ratio)}
                                                </td>
                                                <td className="p-3 border-r border-gray-600 border-b border-gray-700 text-right font-mono text-gray-200">
                                                    {m.total_trades || m.trades || 0}
                                                </td>
                                                <td className="p-3 border-r border-gray-600 border-b border-gray-700 text-right font-mono text-white">
                                                    {formatPct(m.win_rate)}
                                                </td>
                                                <td className={`p-3 border-r border-gray-600 border-b border-gray-700 text-right font-mono font-bold ${(totalReturn || 0) >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                                                    {formatPct(totalReturn)}
                                                </td>
                                                <td className="p-3 border-r border-gray-600 border-b border-gray-700 text-right font-mono text-gray-200">
                                                    {formatCurrency(expectancy)}
                                                </td>
                                                <td className="p-3 border-r border-gray-600 border-b border-gray-700 text-right font-mono text-red-300">
                                                    {formatPct(m.max_drawdown)}
                                                </td>
                                                <td className="p-3 border-r border-gray-600 border-b border-gray-700 text-right font-mono text-white">
                                                    {formatNum(m.profit_factor)}
                                                </td>
                                                <td className="p-3 border-r border-gray-600 border-b border-gray-700 text-right font-mono text-white">
                                                    {formatNum(m.sortino_ratio ?? m.sortino)}
                                                </td>
                                                <td className="p-3 border-r border-gray-600 border-b border-gray-700 text-right font-mono text-red-300">
                                                    {formatPct(m.max_loss)}
                                                </td>
                                                <td className="p-3 border-r border-gray-600 border-b border-gray-700 text-right font-mono text-gray-300">
                                                    {formatNum(m.avg_atr)}
                                                </td>
                                                <td className="p-3 border-r border-gray-600 border-b border-gray-700 text-right font-mono text-green-300">
                                                    {formatPct(m.win_rate_bull)}
                                                </td>
                                                <td className="p-3 border-r border-gray-600 border-b border-gray-700 text-right font-mono text-red-300">
                                                    {formatPct(m.win_rate_bear)}
                                                </td>
                                                <td className="p-3 border-r border-gray-600 border-b border-gray-700 text-right font-mono text-gray-300">
                                                    {formatNum(m.avg_adx)}
                                                </td>
                                                <td className="p-3 border-r border-gray-600 border-b border-gray-700 text-left text-gray-400 text-sm max-w-[200px] truncate" title={fav.notes || ''}>
                                                    {fav.notes || '-'}
                                                </td>
                                                <td className="p-3 border-b border-gray-700 text-center flex items-center justify-center gap-2">
                                                    <button
                                                        onClick={() => handleViewTrades(fav)}
                                                        className="p-1.5 hover:bg-cyan-500/20 text-cyan-400 rounded transition-colors ring-1 ring-transparent hover:ring-cyan-500/50"
                                                        title="View Trades"
                                                    >
                                                        <List className="w-4 h-4" />
                                                    </button>
                                                    <button
                                                        onClick={() => handleRun(fav)}
                                                        className="p-1.5 hover:bg-green-500/20 text-green-400 rounded transition-colors ring-1 ring-transparent hover:ring-green-500/50"
                                                        title="Run Strategy"
                                                    >
                                                        <Play className="w-4 h-4" />
                                                    </button>
                                                    <button
                                                        onClick={() => handleDelete(fav.id)}
                                                        className="p-1.5 hover:bg-red-500/20 text-red-400 rounded transition-colors ring-1 ring-transparent hover:ring-red-500/50"
                                                        title="Delete"
                                                    >
                                                        <Trash2 className="w-4 h-4" />
                                                    </button>
                                                </td>
                                            </tr>
                                        );
                                    })
                                )}
                            </tbody>
                        </table>
                    </div>
                    <div className="p-2 bg-gray-900 border-t border-gray-700 text-xs text-gray-500 flex justify-between items-center">
                        <div>
                            {filteredFavorites.length} strategies loaded
                        </div>
                        {selectedIds.length > 0 && (
                            <div className="flex items-center gap-4">
                                <span className="text-purple-400">{selectedIds.length} selected</span>
                                <button
                                    onClick={() => setIsCompareOpen(true)}
                                    disabled={selectedIds.length < 2}
                                    className="px-3 py-1 bg-purple-600 hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed text-white rounded text-xs font-bold transition-all"
                                >
                                    Compare Selected
                                </button>
                            </div>
                        )}
                    </div>
                </div>

                {/* Compare Modal */}
                {/* Compare Modal */}
                {isCompareOpen && (
                    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm">
                        <div className="bg-gray-900 border border-gray-700 rounded-2xl w-full max-w-6xl max-h-[90vh] flex flex-col shadow-2xl">
                            <div className="flex items-center justify-between p-6 border-b border-gray-800">
                                <h2 className="text-2xl font-bold text-white">Strategy Comparison</h2>
                                <button onClick={() => setIsCompareOpen(false)} className="text-gray-400 hover:text-white">
                                    Close
                                </button>
                            </div>

                            <div className="flex-1 overflow-auto p-6">
                                <table className="w-full text-left border-collapse">
                                    <thead>
                                        <tr>
                                            <th className="p-4 bg-gray-800 text-gray-400 font-medium border-b border-gray-700 sticky top-0 left-0 z-10 w-48">Metric</th>
                                            {selectedStrategies.map(s => (
                                                <th key={s.id} className="p-4 bg-gray-800 text-white font-bold border-b border-gray-700 sticky top-0 min-w-[200px]">
                                                    {s.name}
                                                    <div className="text-xs text-gray-500 font-normal mt-1">{s.symbol} • {s.timeframe}</div>
                                                </th>
                                            ))}
                                        </tr>
                                    </thead>
                                    <tbody className="divide-y divide-gray-800">
                                        <tr className="bg-gray-800/20">
                                            <td className="p-4 font-bold text-gray-300">Total Return</td>
                                            {selectedStrategies.map(s => {
                                                const val = s.metrics.total_return || s.metrics.total_return_pct || 0;
                                                return (
                                                    <td key={s.id} className={`p-4 font-bold text-lg ${val >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                                                        {formatPct(val)}
                                                    </td>
                                                );
                                            })}
                                        </tr>
                                        <tr>
                                            <td className="p-4 text-gray-400">Sharpe Ratio</td>
                                            {selectedStrategies.map(s => (
                                                <td key={s.id} className="p-4 text-white font-mono">{formatNum(s.metrics.sharpe_ratio)}</td>
                                            ))}
                                        </tr>
                                        <tr>
                                            <td className="p-4 text-gray-400">Win Rate</td>
                                            {selectedStrategies.map(s => (
                                                <td key={s.id} className="p-4 text-white font-mono">{formatPct(s.metrics.win_rate)}</td>
                                            ))}
                                        </tr>
                                        <tr>
                                            <td className="p-4 text-gray-400">Max Drawdown</td>
                                            {selectedStrategies.map(s => (
                                                <td key={s.id} className="p-4 text-rose-400 font-mono">{formatPct(s.metrics.max_drawdown)}</td>
                                            ))}
                                        </tr>
                                        <tr>
                                            <td className="p-4 text-gray-400">Profit Factor</td>
                                            {selectedStrategies.map(s => (
                                                <td key={s.id} className="p-4 text-white font-mono">{formatNum(s.metrics.profit_factor)}</td>
                                            ))}
                                        </tr>
                                        <tr>
                                            <td className="p-4 text-gray-400">Sortino Ratio</td>
                                            {selectedStrategies.map(s => (
                                                <td key={s.id} className="p-4 text-white font-mono">{formatNum(s.metrics.sortino_ratio ?? s.metrics.sortino)}</td>
                                            ))}
                                        </tr>
                                        <tr>
                                            <td className="p-4 text-gray-400">Max Loss</td>
                                            {selectedStrategies.map(s => (
                                                <td key={s.id} className="p-4 text-red-500 font-mono">{formatPct(s.metrics.max_loss)}</td>
                                            ))}
                                        </tr>
                                        <tr>
                                            <td className="p-4 text-gray-400">Max Cons. Losses</td>
                                            {selectedStrategies.map(s => (
                                                <td key={s.id} className="p-4 text-orange-400 font-mono">{s.metrics.max_consecutive_losses ?? 0}</td>
                                            ))}
                                        </tr>
                                        <tr>
                                            <td className="p-4 text-gray-400">Avg ATR</td>
                                            {selectedStrategies.map(s => (
                                                <td key={s.id} className="p-4 text-white font-mono">{formatNum(s.metrics.avg_atr)}</td>
                                            ))}
                                        </tr>
                                        <tr>
                                            <td className="p-4 text-gray-400">Win Rate Bull</td>
                                            {selectedStrategies.map(s => (
                                                <td key={s.id} className="p-4 text-green-300 font-mono">{formatPct(s.metrics.win_rate_bull)}</td>
                                            ))}
                                        </tr>
                                        <tr>
                                            <td className="p-4 text-gray-400">Win Rate Bear</td>
                                            {selectedStrategies.map(s => (
                                                <td key={s.id} className="p-4 text-red-300 font-mono">{formatPct(s.metrics.win_rate_bear)}</td>
                                            ))}
                                        </tr>
                                        <tr>
                                            <td className="p-4 text-gray-400">Avg ADX</td>
                                            {selectedStrategies.map(s => (
                                                <td key={s.id} className="p-4 text-white font-mono">{formatNum(s.metrics.avg_adx)}</td>
                                            ))}
                                        </tr>
                                        <tr>
                                            <td className="p-4 text-gray-400">Total Trades</td>
                                            {selectedStrategies.map(s => (
                                                <td key={s.id} className="p-4 text-white font-mono">{s.metrics.total_trades || s.metrics.trades || 0}</td>
                                            ))}
                                        </tr>
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                )}

                <TradesViewModal
                    isOpen={isTradesModalOpen}
                    onClose={() => setIsTradesModalOpen(false)}
                    trades={selectedTrades}
                    title={selectedTradesTitle}
                    subtitle={`Total Trades: ${selectedTrades.length}`}
                />
            </div>
        </div>
    );
};

export default FavoritesDashboard;
