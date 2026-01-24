import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { Play, Trash2, Search, List, ChevronDown, Activity } from 'lucide-react';
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
        <div className="min-h-screen relative overflow-hidden bg-black text-white font-sans selection:bg-blue-500/30">
            {/* Animated background */}
            <div className="fixed inset-0 -z-10">
                <div className="absolute top-0 left-1/4 w-96 h-96 bg-blue-500/10 rounded-full blur-3xl animate-float"></div>
                <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl animate-float" style={{ animationDelay: '2s' }}></div>
            </div>
            <div className="max-w-[1920px] mx-auto border-l-4 border-primary-600 pl-4">
                {/* Header */}
                <header className="glass-strong border-b border-white/10 sticky top-0 z-50 mb-8">
                    <div className="container mx-auto px-6 py-6">
                        <div className="flex items-center justify-between">
                            <div className="flex items-center gap-4">
                                <div className="relative">
                                    <div className="absolute inset-0 bg-gradient-to-r from-blue-500 to-purple-500 rounded-xl blur opacity-75 animate-pulse"></div>
                                    <div className="relative bg-gradient-to-br from-blue-500 to-purple-600 p-2.5 rounded-xl shadow-glow-blue">
                                        <Activity className="w-7 h-7 text-white" />
                                    </div>
                                </div>
                                <div>
                                    <h1 className="text-3xl font-bold gradient-text">Strategy Favorites</h1>
                                    <p className="text-sm text-gray-400 mt-0.5 flex items-center gap-2">
                                        <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
                                        System Operational
                                    </p>
                                </div>
                            </div>

                            <div className="flex items-center gap-4">
                                {/* Filters */}
                                <div className="flex gap-2">
                                    <div className="relative group">
                                        <select
                                            value={selectedSymbol}
                                            onChange={(e) => setSelectedSymbol(e.target.value)}
                                            className="bg-white/5 border border-white/10 rounded-lg pl-3 pr-8 py-2 text-sm text-gray-300 focus:border-blue-500 focus:ring-1 focus:ring-blue-500 outline-none appearance-none cursor-pointer transition-colors hover:bg-white/10"
                                        >
                                            <option value="ALL">Symbol: All</option>
                                            {uniqueSymbols.map(sym => (
                                                <option key={sym} value={sym}>{sym}</option>
                                            ))}
                                        </select>
                                        <ChevronDown className="absolute right-2 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-500 pointer-events-none" />
                                    </div>

                                    <div className="relative group">
                                        <select
                                            value={selectedIndicator}
                                            onChange={(e) => setSelectedIndicator(e.target.value)}
                                            className="bg-white/5 border border-white/10 rounded-lg pl-3 pr-8 py-2 text-sm text-gray-300 focus:border-blue-500 focus:ring-1 focus:ring-blue-500 outline-none appearance-none cursor-pointer transition-colors hover:bg-white/10"
                                        >
                                            <option value="ALL">Strategy: All</option>
                                            {uniqueIndicators.map(ind => (
                                                <option key={ind} value={ind}>{ind}</option>
                                            ))}
                                        </select>
                                        <ChevronDown className="absolute right-2 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-500 pointer-events-none" />
                                    </div>
                                </div>

                                <div className="relative">
                                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-500 w-4 h-4" />
                                    <input
                                        type="text"
                                        placeholder="Search strategies..."
                                        value={searchTerm}
                                        onChange={(e) => setSearchTerm(e.target.value)}
                                        className="bg-white/5 border border-white/10 rounded-lg pl-10 pr-4 py-2 text-sm text-white focus:border-blue-500 focus:ring-1 focus:ring-blue-500 outline-none w-64 placeholder-gray-600 transition-colors hover:bg-white/10"
                                    />
                                </div>

                                <div className="h-8 w-[1px] bg-white/10 mx-2"></div>

                                <button
                                    onClick={handleExportExcel}
                                    className="bg-white/5 hover:bg-white/10 text-gray-300 hover:text-white px-4 py-2 text-sm font-medium rounded-lg border border-white/10 hover:border-white/20 transition-all flex items-center gap-2"
                                >
                                    <List className="w-4 h-4" /> Export
                                </button>
                                <button
                                    onClick={() => navigate('/optimize/parameters')}
                                    className="px-6 py-2 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-500 hover:to-purple-500 text-white text-sm font-bold rounded-lg shadow-lg shadow-blue-500/20 hover:shadow-blue-500/40 transition-all transform hover:-translate-y-0.5"
                                >
                                    Find New
                                </button>
                            </div>
                        </div>
                    </div>
                </header>

                <main className="container mx-auto px-6 pb-12">
                    {/* Table Container */}
                    <div className="glass-strong rounded-2xl border border-white/10 overflow-hidden shadow-2xl">


                        <div className="overflow-x-auto">
                            <table className="w-full text-left border-collapse text-sm">
                                <thead className="bg-white/5 border-b border-white/10 text-gray-400 font-semibold uppercase tracking-wider text-xs">
                                    <tr>
                                        <th className="p-4 w-10 text-center">
                                            <div className="w-4 h-4 rounded border border-white/20"></div>
                                        </th>
                                        <th className="p-4 border-r border-white/5 font-medium text-white">Symbol</th>
                                        <th className="p-4 border-r border-white/5 font-medium text-white">Strategy</th>
                                        <th className="p-4 border-r border-white/5 text-center text-gray-400">TF</th>
                                        <th className="p-4 border-r border-white/5 text-gray-400 w-96">Config</th>
                                        <th className="p-4 border-r border-white/5 text-right text-gray-400">Stop</th>
                                        <th className="p-4 border-r border-white/5 text-right text-blue-400">Sharpe</th>
                                        <th className="p-4 border-r border-white/5 text-right text-gray-400">Trades</th>
                                        <th className="p-4 border-r border-white/5 text-right text-gray-400">Win%</th>
                                        <th className="p-4 border-r border-white/5 text-right text-white">Return</th>
                                        <th className="p-4 border-r border-white/5 text-right text-gray-400">Exp/T</th>
                                        <th className="p-4 border-r border-white/5 text-right text-red-400">Max DD</th>
                                        <th className="p-4 border-r border-white/5 text-right text-gray-400">PF</th>
                                        <th className="p-4 border-r border-white/5 text-right text-gray-400">Sort</th>
                                        <th className="p-4 border-r border-white/5 text-right text-red-400">Max L</th>
                                        <th className="p-4 border-r border-white/5 text-right text-gray-400">ATR</th>
                                        <th className="p-4 border-r border-white/5 text-right text-green-400">Bull</th>
                                        <th className="p-4 border-r border-white/5 text-right text-red-400">Bear</th>
                                        <th className="p-4 border-r border-white/5 text-right text-gray-400">ADX</th>
                                        <th className="p-4 border-r border-white/5 text-left text-gray-500">Notes</th>
                                        <th className="p-4 text-center text-gray-400">Actions</th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-industrial-800">
                                    {isLoading ? (
                                        <tr><td colSpan={14} className="p-12 text-center text-gray-500 animate-pulse">Scanning database...</td></tr>
                                    ) : filteredFavorites.length === 0 ? (
                                        <tr><td colSpan={14} className="p-12 text-center text-gray-500">No favorite strategies found.</td></tr>
                                    ) : (
                                        filteredFavorites.map((fav) => {
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
                                                    group transition-all duration-200 border-b border-white/5 hover:bg-white/5
                                                    ${isSelected ? 'bg-blue-500/10 border-blue-500/30' : ''}
                                                `}
                                                >
                                                    <td className="p-4 border-r border-white/5 text-center">
                                                        <div
                                                            onClick={() => toggleSelection(fav.id)}
                                                            className={`w-5 h-5 rounded-md border mx-auto cursor-pointer flex items-center justify-center transition-all
                                                            ${isSelected ? 'bg-blue-500 border-blue-500 shadow-glow-blue' : 'bg-transparent border-gray-600 group-hover:border-blue-400'}
                                                        `}
                                                        >
                                                            {isSelected && <div className="w-2 h-2 bg-white rounded-full"></div>}
                                                        </div>
                                                    </td>
                                                    <td className="p-2 border-r border-white/5 font-bold text-white tracking-wide">{fav.symbol}</td>
                                                    <td className="p-2 border-r border-white/5 text-blue-300 font-medium">{fav.strategy_name.replace(/_/g, ' ')}</td>
                                                    <td className="p-2 border-r border-white/5 text-center text-white/70">
                                                        <span className="px-2 py-1 rounded bg-white/5 text-xs font-mono">{fav.timeframe}</span>
                                                    </td>
                                                    <td className="p-2 border-r border-white/5 text-gray-400 truncate max-w-xs text-xs font-mono" title={formatParams(fav.parameters)}>
                                                        {formatParams(fav.parameters).split('&').join(' ')}
                                                    </td>
                                                    <td className="p-2 border-r border-white/5 text-right text-gray-300 font-mono">
                                                        {formatPct(stopLoss)}
                                                    </td>
                                                    <td className="p-2 border-r border-white/5 text-right text-blue-400 font-bold text-sm font-mono bg-blue-500/5">
                                                        {formatNum(m.sharpe_ratio)}
                                                    </td>
                                                    <td className="p-2 border-r border-white/5 text-right text-gray-300 font-mono">
                                                        {m.total_trades || m.trades || 0}
                                                    </td>
                                                    <td className="p-2 border-r border-white/5 text-right text-gray-300 font-mono">
                                                        {formatPct(m.win_rate)}
                                                    </td>
                                                    <td className={`p-2 border-r border-white/5 text-right font-bold font-mono ${(totalReturn || 0) >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                                                        {formatPct(totalReturn)}
                                                    </td>
                                                    <td className="p-2 border-r border-white/5 text-right text-gray-400 font-mono">
                                                        {formatCurrency(expectancy)}
                                                    </td>
                                                    <td className="p-2 border-r border-white/5 text-right text-red-400 font-mono">
                                                        {formatPct(m.max_drawdown)}
                                                    </td>
                                                    <td className="p-2 border-r border-white/5 text-right text-gray-300 font-mono">
                                                        {formatNum(m.profit_factor)}
                                                    </td>
                                                    <td className="p-2 border-r border-white/5 text-right text-gray-300 font-mono">
                                                        {formatNum(m.sortino_ratio ?? m.sortino)}
                                                    </td>
                                                    <td className="p-2 border-r border-white/5 text-right text-red-400 font-bold font-mono">
                                                        {formatPct(m.max_loss)}
                                                    </td>
                                                    <td className="p-2 border-r border-white/5 text-right text-gray-400 font-mono">
                                                        {formatNum(m.avg_atr)}
                                                    </td>
                                                    <td className="p-2 border-r border-white/5 text-right text-green-500/80 font-mono">
                                                        {formatPct(m.win_rate_bull)}
                                                    </td>
                                                    <td className="p-2 border-r border-white/5 text-right text-red-500/80 font-mono">
                                                        {formatPct(m.win_rate_bear)}
                                                    </td>
                                                    <td className="p-2 border-r border-white/5 text-right text-gray-500 font-mono">
                                                        {formatNum(m.avg_adx)}
                                                    </td>
                                                    <td className="p-2 border-r border-white/5 text-left text-gray-500 text-xs italic max-w-[150px] truncate" title={fav.notes || ''}>
                                                        {fav.notes || '-'}
                                                    </td>
                                                    <td className="p-2 text-center flex items-center justify-center gap-2">
                                                        <button
                                                            onClick={() => handleViewTrades(fav)}
                                                            className="p-1.5 hover:bg-white/10 rounded-lg text-gray-400 hover:text-white transition-colors"
                                                            title="View Trades"
                                                        >
                                                            <List className="w-4 h-4" />
                                                        </button>
                                                        <button
                                                            onClick={() => handleRun(fav)}
                                                            className="p-1.5 hover:bg-blue-500/20 rounded-lg text-blue-400 hover:text-blue-300 transition-colors"
                                                            title="Run Strategy"
                                                        >
                                                            <Play className="w-4 h-4" />
                                                        </button>
                                                        <button
                                                            onClick={() => handleDelete(fav.id)}
                                                            className="p-1.5 hover:bg-red-500/20 rounded-lg text-gray-400 hover:text-red-400 transition-colors"
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

                        {/* Footer / Status Bar - Replaces System Status */}
                        <div className="p-4 bg-white/5 border-t border-white/10 flex justify-between items-center text-sm">
                            <div className="flex items-center gap-2 text-gray-400">
                                <span className="w-2 h-2 rounded-full bg-blue-500"></span>
                                {filteredFavorites.length} strategies loaded
                            </div>
                            {selectedIds.length > 0 && (
                                <div className="flex items-center gap-4 animate-in fade-in slide-in-from-right-4">
                                    <span className="text-blue-400 font-medium">{selectedIds.length} selected</span>
                                    <button
                                        onClick={() => setIsCompareOpen(true)}
                                        disabled={selectedIds.length < 2}
                                        className="px-4 py-1.5 bg-blue-600 hover:bg-blue-500 text-white text-sm font-semibold rounded-lg shadow-lg shadow-blue-500/20 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                                    >
                                        Compare Strategies
                                    </button>
                                </div>
                            )}
                        </div>
                    </div>
                </main>

                {/* Compare Modal */}
                {
                    isCompareOpen && (
                        <div className="fixed inset-0 z-50 flex items-center justify-center p-6 bg-black/90 backdrop-blur-none bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-industrial-900/50 via-black to-black">
                            <div className="bg-black border-2 border-industrial-700 w-full max-w-6xl max-h-[90vh] flex flex-col shadow-2xl relative">
                                {/* Decorative corners */}
                                <div className="absolute -top-1 -left-1 w-4 h-4 border-t-2 border-l-2 border-primary-500"></div>
                                <div className="absolute -bottom-1 -right-1 w-4 h-4 border-b-2 border-r-2 border-primary-500"></div>

                                <div className="flex items-center justify-between p-4 border-b-2 border-industrial-800 bg-industrial-900/50">
                                    <h2 className="text-xl font-black uppercase tracking-widest text-white flex items-center gap-2">
                                        <Activity className="w-5 h-5 text-primary-500" />
                                        Data.Comparison_Module
                                    </h2>
                                    <button
                                        onClick={() => setIsCompareOpen(false)}
                                        className="text-industrial-500 hover:text-red-500 font-mono text-xs uppercase hover:underline"
                                    >
                                        [CLOSE]
                                    </button>
                                </div>

                                <div className="flex-1 overflow-auto p-0">
                                    <table className="w-full text-left border-collapse font-mono text-sm">
                                        <thead>
                                            <tr>
                                                <th className="p-4 bg-industrial-900 text-industrial-500 font-bold border-b border-industrial-800 sticky top-0 left-0 z-10 w-48 uppercase tracking-wider text-xs border-r border-industrial-800">
                                                    Metric_ID
                                                </th>
                                                {selectedStrategies.map(s => (
                                                    <th key={s.id} className="p-4 bg-black text-white border-b border-industrial-800 sticky top-0 min-w-[200px] border-r border-industrial-800">
                                                        <div className="text-primary-500 text-xs font-bold uppercase mb-1">Strat_ID: #{s.id}</div>
                                                        <div className="font-bold truncate">{s.name}</div>
                                                        <div className="text-[10px] text-industrial-500 font-normal mt-1 uppercase tracking-widest">{s.symbol} • {s.timeframe}</div>
                                                    </th>
                                                ))}
                                            </tr>
                                        </thead>
                                        <tbody className="divide-y divide-industrial-800">
                                            <tr className="bg-industrial-900/20">
                                                <td className="p-4 font-bold text-industrial-300 border-r border-industrial-800 text-xs uppercase">Total Return</td>
                                                {selectedStrategies.map(s => {
                                                    const val = s.metrics.total_return || s.metrics.total_return_pct || 0;
                                                    return (
                                                        <td key={s.id} className={`p-4 font-bold text-lg border-r border-industrial-800 ${val >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                                                            {formatPct(val)}
                                                        </td>
                                                    );
                                                })}
                                            </tr>
                                            <tr>
                                                <td className="p-4 text-industrial-400 border-r border-industrial-800 text-xs uppercase">Sharpe Ratio</td>
                                                {selectedStrategies.map(s => (
                                                    <td key={s.id} className="p-4 text-white font-mono border-r border-industrial-800">{formatNum(s.metrics.sharpe_ratio)}</td>
                                                ))}
                                            </tr>
                                            <tr>
                                                <td className="p-4 text-industrial-400 border-r border-industrial-800 text-xs uppercase">Win Rate</td>
                                                {selectedStrategies.map(s => (
                                                    <td key={s.id} className="p-4 text-white font-mono border-r border-industrial-800">{formatPct(s.metrics.win_rate)}</td>
                                                ))}
                                            </tr>
                                            <tr>
                                                <td className="p-4 text-industrial-400 border-r border-industrial-800 text-xs uppercase">Max Drawdown</td>
                                                {selectedStrategies.map(s => (
                                                    <td key={s.id} className="p-4 text-red-500 font-mono border-r border-industrial-800">{formatPct(s.metrics.max_drawdown)}</td>
                                                ))}
                                            </tr>
                                            <tr>
                                                <td className="p-4 text-industrial-400 border-r border-industrial-800 text-xs uppercase">Profit Factor</td>
                                                {selectedStrategies.map(s => (
                                                    <td key={s.id} className="p-4 text-white font-mono border-r border-industrial-800">{formatNum(s.metrics.profit_factor)}</td>
                                                ))}
                                            </tr>
                                            <tr>
                                                <td className="p-4 text-industrial-400 border-r border-industrial-800 text-xs uppercase">Sortino Ratio</td>
                                                {selectedStrategies.map(s => (
                                                    <td key={s.id} className="p-4 text-white font-mono border-r border-industrial-800">{formatNum(s.metrics.sortino_ratio ?? s.metrics.sortino)}</td>
                                                ))}
                                            </tr>
                                            <tr>
                                                <td className="p-4 text-industrial-400 border-r border-industrial-800 text-xs uppercase">Max Loss</td>
                                                {selectedStrategies.map(s => (
                                                    <td key={s.id} className="p-4 text-red-500 font-mono border-r border-industrial-800">{formatPct(s.metrics.max_loss)}</td>
                                                ))}
                                            </tr>
                                            <tr>
                                                <td className="p-4 text-industrial-400 border-r border-industrial-800 text-xs uppercase">Max Cons. Losses</td>
                                                {selectedStrategies.map(s => (
                                                    <td key={s.id} className="p-4 text-white font-mono border-r border-industrial-800">{s.metrics.max_consecutive_losses ?? 0}</td>
                                                ))}
                                            </tr>
                                            <tr>
                                                <td className="p-4 text-industrial-400 border-r border-industrial-800 text-xs uppercase">Avg ATR</td>
                                                {selectedStrategies.map(s => (
                                                    <td key={s.id} className="p-4 text-industrial-200 font-mono border-r border-industrial-800">{formatNum(s.metrics.avg_atr)}</td>
                                                ))}
                                            </tr>
                                            <tr>
                                                <td className="p-4 text-industrial-400 border-r border-industrial-800 text-xs uppercase">Win Rate Bull</td>
                                                {selectedStrategies.map(s => (
                                                    <td key={s.id} className="p-4 text-green-600 font-mono border-r border-industrial-800">{formatPct(s.metrics.win_rate_bull)}</td>
                                                ))}
                                            </tr>
                                            <tr>
                                                <td className="p-4 text-industrial-400 border-r border-industrial-800 text-xs uppercase">Win Rate Bear</td>
                                                {selectedStrategies.map(s => (
                                                    <td key={s.id} className="p-4 text-red-600 font-mono border-r border-industrial-800">{formatPct(s.metrics.win_rate_bear)}</td>
                                                ))}
                                            </tr>
                                            <tr>
                                                <td className="p-4 text-industrial-400 border-r border-industrial-800 text-xs uppercase">Avg ADX</td>
                                                {selectedStrategies.map(s => (
                                                    <td key={s.id} className="p-4 text-industrial-200 font-mono border-r border-industrial-800">{formatNum(s.metrics.avg_adx)}</td>
                                                ))}
                                            </tr>
                                            <tr>
                                                <td className="p-4 text-industrial-400 border-r border-industrial-800 text-xs uppercase">Total Trades</td>
                                                {selectedStrategies.map(s => (
                                                    <td key={s.id} className="p-4 text-industrial-200 font-mono border-r border-industrial-800">{s.metrics.total_trades || s.metrics.trades || 0}</td>
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
