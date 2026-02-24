import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { Trash2, Search, List, ChevronDown, Activity, BarChart3, MessageCircle } from 'lucide-react';
import TradesViewModal from '../components/TradesViewModal';
import { AgentChatModal } from '../components/AgentChatModal';
import { useInfiniteScroll } from '@/hooks/useInfiniteScroll';
import { API_BASE_URL } from '../lib/apiBase';

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
    tier: number | null;  // 1=Core obrigatório, 2=Bons complementares, 3=Outros, null=Sem tier
    start_date?: string | null;
    end_date?: string | null;
}

const FavoritesDashboard: React.FC = () => {
    const navigate = useNavigate();
    const queryClient = useQueryClient();
    const [searchTerm, setSearchTerm] = useState('');
    const [selectedIds, setSelectedIds] = useState<number[]>([]);
    const [isCompareOpen, setIsCompareOpen] = useState(false);
    const [tierFilter, setTierFilter] = useState<'all' | '1' | '2' | '3' | '1_2' | 'none'>('all');

    // New state for Trades Modal
    const [isTradesModalOpen, setIsTradesModalOpen] = useState(false);
    const [selectedTrades, setSelectedTrades] = useState<any[]>([]);
    const [selectedTradesTitle, setSelectedTradesTitle] = useState('');
    const [selectedTradesSymbol, setSelectedTradesSymbol] = useState('');
    const [selectedTradesTemplate, setSelectedTradesTemplate] = useState('');
    const [selectedTradesTimeframe, setSelectedTradesTimeframe] = useState('');
    
    // State for loading backtest
    const [loadingBacktestId, setLoadingBacktestId] = useState<number | null>(null);

    // Agent chat modal
    const [isAgentModalOpen, setIsAgentModalOpen] = useState(false);
    const [selectedAgentFavorite, setSelectedAgentFavorite] = useState<FavoriteStrategy | null>(null);

    // Fetch favorites
    const { data: favorites, isLoading } = useQuery({
        queryKey: ['favorites'],
        queryFn: async () => {
            const res = await fetch(`${API_BASE_URL}/favorites/`);
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
            const res = await fetch(`${API_BASE_URL}/favorites/${id}`, {
                method: 'DELETE'
            });
            if (!res.ok) throw new Error('Failed to delete');
        },
        onSuccess: (_, id) => {
            queryClient.invalidateQueries({ queryKey: ['favorites'] });
            setSelectedIds(prev => prev.filter(sid => sid !== id));
        }
    });

    // Update tier mutation
    const updateTierMutation = useMutation({
        mutationFn: async ({ id, tier }: { id: number; tier: number | null }) => {
            const res = await fetch(`${API_BASE_URL}/favorites/${id}`, {
                method: 'PATCH',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ tier })
            });
            if (!res.ok) throw new Error('Failed to update tier');
            return res.json();
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['favorites'] });
        }
    });

    const handleUpdateTier = (fav: FavoriteStrategy, tier: number | null) => {
        updateTierMutation.mutate({ id: fav.id, tier });
    };

    // Helper function to get tier color and label
    const getTierInfo = (tier: number | null) => {
        switch (tier) {
            case 1:
                return { color: 'bg-green-500', textColor: 'text-green-400', label: 'Tier 1 – Core obrigatório', borderColor: 'border-green-500' };
            case 2:
                return { color: 'bg-yellow-500', textColor: 'text-yellow-400', label: 'Tier 2 – Bons complementares', borderColor: 'border-yellow-500' };
            case 3:
                return { color: 'bg-red-500', textColor: 'text-red-400', label: 'Tier 3', borderColor: 'border-red-500' };
            default:
                return { color: 'bg-gray-500', textColor: 'text-gray-400', label: 'Sem tier', borderColor: 'border-gray-500' };
        }
    };

    const handleViewResults = async (fav: FavoriteStrategy) => {
        setLoadingBacktestId(fav.id);
        try {
            // Executar backtest com os parâmetros do favorito
            const response = await fetch(`${API_BASE_URL}/combos/backtest`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    template_name: fav.strategy_name,
                    symbol: fav.symbol,
                    timeframe: fav.timeframe,
                    parameters: fav.parameters,
                    direction: (fav.parameters?.direction as string) || 'long',
                    stop_loss: fav.parameters.stop_loss || null,
                    start_date: null, // Usar todos os dados disponíveis
                    end_date: null,
                    deep_backtest: true,
                    initial_capital: 100
                })
            });

            if (!response.ok) {
                const error = await response.json();
                alert(`Erro ao executar backtest: ${error.detail || 'Erro desconhecido'}`);
                return;
            }

            const result = await response.json();
            
            // Navegar para a tela de resultados com os dados
            navigate('/combo/results', { state: { result, isOptimization: false } });
        } catch (error) {
            console.error('Erro ao executar backtest:', error);
            alert('Erro ao executar backtest. Verifique o console para mais detalhes.');
        } finally {
            setLoadingBacktestId(null);
        }
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
        setSelectedTradesSymbol(fav.symbol);
        setSelectedTradesTemplate(fav.strategy_name);
        setSelectedTradesTimeframe(fav.timeframe);
        setIsTradesModalOpen(true);
    };

    const handleOpenAgent = (fav: FavoriteStrategy) => {
        setSelectedAgentFavorite(fav);
        setIsAgentModalOpen(true);
    };

    const [selectedSymbol, setSelectedSymbol] = useState<string>('ALL');
    const [selectedIndicator, setSelectedIndicator] = useState<string>('ALL');
    const [directionFilter, setDirectionFilter] = useState<'all' | 'long' | 'short'>('all');
    type SortByOption = 'return' | 'sharpe' | 'trades' | 'returnPerTrade';
    const [sortBy, setSortBy] = useState<SortByOption>('returnPerTrade');

    /** Número de trades: preferir tamanho da lista metrics.trades para bater com a "List of trades". */
    const getTradesCount = (fav: FavoriteStrategy): number => {
        const m = fav.metrics || {};
        if (Array.isArray(m.trades) && m.trades.length >= 0) return m.trades.length;
        const n = m.total_trades ?? (typeof m.trades === 'number' ? m.trades : null);
        return n != null ? Math.max(0, Number(n)) : 0;
    };

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
        const matchesTier = tierFilter === 'all' ||
            (tierFilter === '1_2' && (fav.tier === 1 || fav.tier === 2)) ||
            (tierFilter === 'none' && fav.tier === null) ||
            (tierFilter !== 'none' && tierFilter !== '1_2' && fav.tier === parseInt(tierFilter));

        const favDirection = ((fav.parameters?.direction as string) || 'long').toLowerCase();
        const matchesDirection = directionFilter === 'all' || favDirection === directionFilter;

        return matchesSearch && matchesSymbol && matchesIndicator && matchesTier && matchesDirection;
    }) || []).sort((a, b) => {
        const tierA = a.tier ?? 999;
        const tierB = b.tier ?? 999;
        if (tierA !== tierB) return tierA - tierB;

        const returnPctA = a.metrics?.total_return_pct ?? (a.metrics?.total_return != null ? a.metrics.total_return * 100 : -Infinity);
        const returnPctB = b.metrics?.total_return_pct ?? (b.metrics?.total_return != null ? b.metrics.total_return * 100 : -Infinity);
        const tradesA = Math.max(1, getTradesCount(a));
        const tradesB = Math.max(1, getTradesCount(b));
        const sharpeA = a.metrics?.sharpe_ratio ?? -Infinity;
        const sharpeB = b.metrics?.sharpe_ratio ?? -Infinity;

        let valA: number, valB: number;
        switch (sortBy) {
            case 'return':
                valA = returnPctA === -Infinity ? -Infinity : returnPctA;
                valB = returnPctB === -Infinity ? -Infinity : returnPctB;
                break;
            case 'sharpe':
                valA = sharpeA;
                valB = sharpeB;
                break;
            case 'trades':
                valA = tradesA;
                valB = tradesB;
                break;
            case 'returnPerTrade':
                valA = returnPctA === -Infinity ? -Infinity : returnPctA / tradesA;
                valB = returnPctB === -Infinity ? -Infinity : returnPctB / tradesB;
                break;
            default:
                valA = returnPctA === -Infinity ? -Infinity : returnPctA / tradesA;
                valB = returnPctB === -Infinity ? -Infinity : returnPctB / tradesB;
        }
        return valB - valA; // Descending
    });

    const { visibleItems: visibleFavorites, hasMore, sentinelRef } = useInfiniteScroll(
        filteredFavorites,
        30,
        30
    );

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
            const totalReturnPct = m.total_return_pct ?? (m.total_return != null ? m.total_return * 100 : null);
            const tradesN = Math.max(1, getTradesCount(fav));
            const returnPerTradePct = totalReturnPct != null ? totalReturnPct / tradesN : null;
            const expectancy = m.expectancy ?? (m.total_pnl && tradesN ? m.total_pnl / tradesN : null);
            const stopLoss = fav.parameters.stop_loss || null;

            const direction = ((fav.parameters?.direction as string) || 'long').toLowerCase();
            return {
                Name: fav.name,
                Symbol: fav.symbol,
                Strategy: fav.strategy_name,
                Direção: direction === 'short' ? 'Short' : 'Long',
                Timeframe: fav.timeframe,
                Período: formatPeriod(fav),
                Parameters: formatParams(fav.parameters),
                "Stop Loss": formatPct(stopLoss),
                Sharpe: formatNum(m.sharpe_ratio),
                Trades: getTradesCount(fav),
                "Win Rate": formatPct(m.win_rate),
                "Total Return": formatPct(totalReturn),
                "Ret/T %": returnPerTradePct != null ? formatPct(returnPerTradePct) : '-',
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

    const formatPeriod = (fav: FavoriteStrategy): string => {
        const s = fav.start_date;
        const e = fav.end_date;
        if (!s && !e) return 'Todo';
        if (s && e) return `${s} → ${e}`;
        if (s) return `≥ ${s}`;
        return `≤ ${e!}`;
    };

    const getFavoriteStatus = (fav: FavoriteStrategy): string => {
        const metricStatus = String(fav.metrics?.status || '').toUpperCase();
        if (metricStatus.includes('HOLD')) return 'HOLD';
        if (fav.metrics?.is_holding === true) return 'HOLD';
        if (metricStatus === '') return 'WAITING';
        return metricStatus.replaceAll('_', ' ');
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
                    <div className="container mx-auto px-3 sm:px-6 py-4 sm:py-6">
                        <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
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

                            <div className="w-full lg:w-auto flex flex-col gap-3 lg:flex-row lg:items-center lg:gap-4">
                                {/* Filters */}
                                <div className="grid grid-cols-1 gap-2 sm:grid-cols-2 lg:flex lg:gap-2 w-full lg:w-auto">
                                    <div className="relative group">
                                        <select
                                            value={tierFilter}
                                            onChange={(e) => setTierFilter(e.target.value as 'all' | '1' | '2' | '3' | '1_2' | 'none')}
                                            className="w-full bg-white/5 border border-white/10 rounded-lg pl-3 pr-8 py-2.5 lg:py-2 text-sm text-gray-300 focus:border-blue-500 focus:ring-1 focus:ring-blue-500 outline-none appearance-none cursor-pointer transition-colors hover:bg-white/10 min-h-11"
                                        >
                                            <option value="all" className="bg-gray-900">Tier: All</option>
                                            <option value="1_2" className="bg-gray-900">Tier 1 + Tier 2</option>
                                            <option value="1" className="bg-gray-900">Tier 1 – Core obrigatório</option>
                                            <option value="2" className="bg-gray-900">Tier 2 – Bons complementares</option>
                                            <option value="3" className="bg-gray-900">Tier 3</option>
                                            <option value="none" className="bg-gray-900">Sem tier</option>
                                        </select>
                                        <ChevronDown className="absolute right-2 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-500 pointer-events-none" />
                                    </div>

                                    <div className="relative group">
                                        <select
                                            value={selectedSymbol}
                                            onChange={(e) => setSelectedSymbol(e.target.value)}
                                            className="w-full bg-white/5 border border-white/10 rounded-lg pl-3 pr-8 py-2.5 lg:py-2 text-sm text-gray-300 focus:border-blue-500 focus:ring-1 focus:ring-blue-500 outline-none appearance-none cursor-pointer transition-colors hover:bg-white/10 min-h-11"
                                        >
                                            <option value="ALL" className="bg-gray-900">Symbol: All</option>
                                            {uniqueSymbols.map(sym => (
                                                <option key={sym} value={sym} className="bg-gray-900">{sym}</option>
                                            ))}
                                        </select>
                                        <ChevronDown className="absolute right-2 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-500 pointer-events-none" />
                                    </div>

                                    <div className="relative group">
                                        <select
                                            value={selectedIndicator}
                                            onChange={(e) => setSelectedIndicator(e.target.value)}
                                            className="w-full bg-white/5 border border-white/10 rounded-lg pl-3 pr-8 py-2.5 lg:py-2 text-sm text-gray-300 focus:border-blue-500 focus:ring-1 focus:ring-blue-500 outline-none appearance-none cursor-pointer transition-colors hover:bg-white/10 min-h-11"
                                        >
                                            <option value="ALL" className="bg-gray-900">Strategy: All</option>
                                            {uniqueIndicators.map(ind => (
                                                <option key={ind} value={ind} className="bg-gray-900">{ind}</option>
                                            ))}
                                        </select>
                                        <ChevronDown className="absolute right-2 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-500 pointer-events-none" />
                                    </div>

                                    <div className="relative group">
                                        <select
                                            value={directionFilter}
                                            onChange={(e) => setDirectionFilter(e.target.value as 'all' | 'long' | 'short')}
                                            className="w-full bg-white/5 border border-white/10 rounded-lg pl-3 pr-8 py-2.5 lg:py-2 text-sm text-gray-300 focus:border-blue-500 focus:ring-1 focus:ring-blue-500 outline-none appearance-none cursor-pointer transition-colors hover:bg-white/10 min-h-11"
                                        >
                                            <option value="all" className="bg-gray-900">Direção: All</option>
                                            <option value="long" className="bg-gray-900">Long</option>
                                            <option value="short" className="bg-gray-900">Short</option>
                                        </select>
                                        <ChevronDown className="absolute right-2 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-500 pointer-events-none" />
                                    </div>

                                    <div className="relative group">
                                        <select
                                            value={sortBy}
                                            onChange={(e) => setSortBy(e.target.value as SortByOption)}
                                            className="w-full bg-white/5 border border-white/10 rounded-lg pl-3 pr-8 py-2.5 lg:py-2 text-sm text-gray-300 focus:border-blue-500 focus:ring-1 focus:ring-blue-500 outline-none appearance-none cursor-pointer transition-colors hover:bg-white/10 min-h-11"
                                        >
                                            <option value="returnPerTrade" className="bg-gray-900">Ordenar: Ret/T %</option>
                                            <option value="return" className="bg-gray-900">Ordenar: Return</option>
                                            <option value="sharpe" className="bg-gray-900">Ordenar: Sharpe</option>
                                            <option value="trades" className="bg-gray-900">Ordenar: Trades</option>
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
                                        className="bg-white/5 border border-white/10 rounded-lg pl-10 pr-4 py-2.5 lg:py-2 text-sm text-white focus:border-blue-500 focus:ring-1 focus:ring-blue-500 outline-none w-full lg:w-64 min-h-11 placeholder-gray-600 transition-colors hover:bg-white/10"
                                    />
                                </div>

                                <div className="hidden lg:block h-8 w-[1px] bg-white/10 mx-2"></div>

                                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 w-full lg:flex lg:w-auto">
                                    <button
                                        onClick={handleExportExcel}
                                        className="bg-white/5 hover:bg-white/10 text-gray-300 hover:text-white px-4 py-2.5 lg:py-2 text-sm font-medium rounded-lg border border-white/10 hover:border-white/20 transition-all flex items-center justify-center gap-2 min-h-11"
                                    >
                                        <List className="w-4 h-4" /> Export
                                    </button>
                                    <button
                                        onClick={() => navigate('/combo/select')}
                                        className="px-6 py-2.5 lg:py-2 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-500 hover:to-purple-500 text-white text-sm font-bold rounded-lg shadow-lg shadow-blue-500/20 hover:shadow-blue-500/40 transition-all transform hover:-translate-y-0.5 min-h-11"
                                    >
                                        Find New
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                </header>

                <main className="container mx-auto px-3 sm:px-6 pb-12">
                    {/* Table Container */}
                    <div className="glass-strong rounded-2xl border border-white/10 overflow-hidden shadow-2xl">

                        <div className="lg:hidden p-3 sm:p-4 space-y-3">
                            {isLoading ? (
                                <div className="p-8 text-center text-gray-500 animate-pulse">Scanning database...</div>
                            ) : filteredFavorites.length === 0 ? (
                                <div className="p-8 text-center text-gray-500">No favorite strategies found.</div>
                            ) : (
                                visibleFavorites.map((fav: FavoriteStrategy) => {
                                    const isSelected = selectedIds.includes(fav.id);
                                    const m = fav.metrics || {};
                                    const totalReturn = m.total_return_pct ?? m.total_return;
                                    const tierInfo = getTierInfo(fav.tier);
                                    const statusLabel = getFavoriteStatus(fav);
                                    return (
                                        <article
                                            key={fav.id}
                                            className={`rounded-xl border bg-white/5 p-3 space-y-3 ${
                                                fav.tier === 1
                                                    ? 'border-green-500/40'
                                                    : fav.tier === 2
                                                        ? 'border-yellow-500/40'
                                                        : fav.tier === 3
                                                            ? 'border-red-500/40'
                                                            : 'border-white/10'
                                            } ${isSelected ? 'ring-1 ring-blue-500/60' : ''}`}
                                        >
                                            <div className="flex items-start justify-between gap-3">
                                                <div className="min-w-0">
                                                    <p className="text-base font-bold tracking-wide break-words">{fav.symbol}</p>
                                                    <p className="text-sm text-blue-300 break-words">{fav.strategy_name.replace(/_/g, ' ')}</p>
                                                </div>
                                                <span className={`px-2 py-1 rounded-md text-xs font-semibold border ${statusLabel === 'HOLD' ? 'text-emerald-300 border-emerald-500/50 bg-emerald-500/10' : 'text-gray-300 border-white/20 bg-white/10'}`}>
                                                    {statusLabel}
                                                </span>
                                            </div>

                                            <div className="grid grid-cols-2 gap-2 text-xs">
                                                <div className="rounded-lg bg-white/5 border border-white/10 p-2">
                                                    <p className="text-gray-500">Tier</p>
                                                    <p className={`font-medium ${tierInfo.textColor}`}>{tierInfo.label}</p>
                                                </div>
                                                <div className="rounded-lg bg-white/5 border border-white/10 p-2">
                                                    <p className="text-gray-500">Return</p>
                                                    <p className={`font-semibold ${(totalReturn || 0) >= 0 ? 'text-green-400' : 'text-red-400'}`}>{formatPct(totalReturn)}</p>
                                                </div>
                                            </div>

                                            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                                                <select
                                                    value={fav.tier ?? ''}
                                                    onChange={(e) => {
                                                        const tierValue = e.target.value === '' ? null : parseInt(e.target.value);
                                                        handleUpdateTier(fav, tierValue);
                                                    }}
                                                    className={`w-full min-h-11 text-xs font-medium px-3 py-2 rounded-lg border transition-all ${
                                                        fav.tier === 1
                                                            ? 'bg-green-500/20 text-green-400 border-green-500/50 hover:bg-green-500/30'
                                                            : fav.tier === 2
                                                                ? 'bg-yellow-500/20 text-yellow-400 border-yellow-500/50 hover:bg-yellow-500/30'
                                                                : fav.tier === 3
                                                                    ? 'bg-red-500/20 text-red-400 border-red-500/50 hover:bg-red-500/30'
                                                                    : 'bg-white/5 text-gray-400 border-white/10 hover:bg-white/10'
                                                    }`}
                                                >
                                                    <option value="">Sem tier</option>
                                                    <option value="1">Tier 1</option>
                                                    <option value="2">Tier 2</option>
                                                    <option value="3">Tier 3</option>
                                                </select>
                                                <button
                                                    onClick={() => toggleSelection(fav.id)}
                                                    className={`min-h-11 rounded-lg border text-sm font-medium transition-colors ${
                                                        isSelected
                                                            ? 'border-blue-500/60 bg-blue-500/15 text-blue-300'
                                                            : 'border-white/10 bg-white/5 text-gray-300 hover:bg-white/10'
                                                    }`}
                                                >
                                                    {isSelected ? 'Selected for compare' : 'Select to compare'}
                                                </button>
                                            </div>

                                            <div className="grid grid-cols-2 gap-2">
                                                <button
                                                    onClick={() => handleViewTrades(fav)}
                                                    className="min-h-11 rounded-lg border border-white/10 bg-white/5 text-gray-200 text-sm font-medium flex items-center justify-center gap-2 hover:bg-white/10 transition-colors"
                                                >
                                                    <List className="w-4 h-4" />
                                                    Trades
                                                </button>
                                                <button
                                                    onClick={() => handleViewResults(fav)}
                                                    disabled={loadingBacktestId === fav.id}
                                                    className="min-h-11 rounded-lg border border-green-500/30 bg-green-500/10 text-green-300 text-sm font-medium flex items-center justify-center gap-2 hover:bg-green-500/20 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                                                >
                                                    {loadingBacktestId === fav.id ? (
                                                        <div className="w-4 h-4 border-2 border-green-400 border-t-transparent rounded-full animate-spin"></div>
                                                    ) : (
                                                        <BarChart3 className="w-4 h-4" />
                                                    )}
                                                    Results
                                                </button>
                                                <button
                                                    onClick={() => handleOpenAgent(fav)}
                                                    className="min-h-11 rounded-lg border border-purple-500/30 bg-purple-500/10 text-purple-300 text-sm font-medium flex items-center justify-center gap-2 hover:bg-purple-500/20 transition-colors"
                                                >
                                                    <MessageCircle className="w-4 h-4" />
                                                    Trader
                                                </button>
                                                <button
                                                    onClick={() => handleDelete(fav.id)}
                                                    className="min-h-11 rounded-lg border border-red-500/30 bg-red-500/10 text-red-300 text-sm font-medium flex items-center justify-center gap-2 hover:bg-red-500/20 transition-colors"
                                                >
                                                    <Trash2 className="w-4 h-4" />
                                                    Delete
                                                </button>
                                            </div>

                                            <details className="rounded-lg border border-white/10 bg-black/20">
                                                <summary className="cursor-pointer list-none px-3 py-2.5 text-sm font-medium text-gray-200 flex items-center justify-between min-h-11">
                                                    <span>More details</span>
                                                    <ChevronDown className="w-4 h-4 text-gray-400" />
                                                </summary>
                                                <div className="px-3 pb-3 space-y-3 text-xs text-gray-300">
                                                    <div className="grid grid-cols-2 gap-2">
                                                        <div>
                                                            <p className="text-gray-500">Timeframe</p>
                                                            <p className="font-mono">{fav.timeframe}</p>
                                                        </div>
                                                        <div>
                                                            <p className="text-gray-500">Período</p>
                                                            <p>{formatPeriod(fav)}</p>
                                                        </div>
                                                    </div>
                                                    <div>
                                                        <p className="text-gray-500 mb-1">Params</p>
                                                        <p className="font-mono break-words">{formatParams(fav.parameters).split('&').join(' ')}</p>
                                                    </div>
                                                    <div className="grid grid-cols-2 gap-2">
                                                        <div>
                                                            <p className="text-gray-500">Sharpe</p>
                                                            <p>{formatNum(m.sharpe_ratio)}</p>
                                                        </div>
                                                        <div>
                                                            <p className="text-gray-500">Trades</p>
                                                            <p>{getTradesCount(fav)}</p>
                                                        </div>
                                                    </div>
                                                    <div>
                                                        <p className="text-gray-500 mb-1">Notes</p>
                                                        <p className="break-words italic">{fav.notes || '-'}</p>
                                                    </div>
                                                </div>
                                            </details>
                                        </article>
                                    );
                                })
                            )}
                            {!isLoading && filteredFavorites.length > 0 && hasMore && (
                                <div className="p-4 text-center text-gray-500 text-sm">
                                    <div ref={sentinelRef} />
                                    <span className="animate-pulse">Carregando mais…</span>
                                </div>
                            )}
                        </div>

                        <div className="hidden lg:block overflow-x-auto">
                            <table className="w-full text-left border-collapse text-sm">
                                <thead className="bg-white/5 border-b border-white/10 text-gray-400 font-semibold uppercase tracking-wider text-xs">
                                    <tr>
                                        <th className="p-4 w-10 text-center">
                                            <div className="w-4 h-4 rounded border border-white/20"></div>
                                        </th>
                                        <th className="p-4 border-r border-white/5 text-center text-gray-400 w-32">Tier</th>
                                        <th className="p-4 border-r border-white/5 font-medium text-white">Symbol</th>
                                        <th className="p-4 border-r border-white/5 font-medium text-white">Strategy</th>
                                        <th className="p-4 border-r border-white/5 text-center text-gray-400 whitespace-nowrap">Direção</th>
                                        <th className="p-4 border-r border-white/5 text-center text-gray-400">Timeframe</th>
                                        <th className="p-4 border-r border-white/5 text-center text-gray-400 whitespace-nowrap">Período</th>
                                        <th className="p-4 border-r border-white/5 text-gray-400 w-96">Config</th>
                                        <th className="p-4 border-r border-white/5 text-right text-gray-400">Stop</th>
                                        <th className="p-4 border-r border-white/5 text-right text-blue-400">Sharpe</th>
                                        <th className="p-4 border-r border-white/5 text-right text-gray-400">Trades</th>
                                        <th className="p-4 border-r border-white/5 text-right text-gray-400">Win%</th>
                                        <th className="p-4 border-r border-white/5 text-right text-white">Return</th>
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
                                        <tr><td colSpan={21} className="p-12 text-center text-gray-500 animate-pulse">Scanning database...</td></tr>
                                    ) : filteredFavorites.length === 0 ? (
                                        <tr><td colSpan={21} className="p-12 text-center text-gray-500">No favorite strategies found.</td></tr>
                                    ) : (
                                        visibleFavorites.map((fav: FavoriteStrategy) => {
                                            const isSelected = selectedIds.includes(fav.id);
                                            const m = fav.metrics || {};
                                            // Try to find derived metrics, fallback to N/A
                                            const totalReturn = m.total_return_pct ?? m.total_return;
                                            const totalReturnPct = m.total_return_pct ?? (m.total_return != null ? m.total_return * 100 : null);
                                            const tradesN = Math.max(1, getTradesCount(fav));
                                            const returnPerTradePct = totalReturnPct != null ? totalReturnPct / tradesN : null;
                                            const expectancy = m.expectancy ?? (m.total_pnl && tradesN ? m.total_pnl / tradesN : null);
                                            // Stop loss usually in parameters
                                            const stopLoss = fav.parameters.stop_loss ? fav.parameters.stop_loss : null;

                                            return (

                                                <tr
                                                    key={fav.id}
                                                    className={`
                                                    group transition-all duration-200 border-b border-white/5 hover:bg-white/5
                                                    ${isSelected ? 'bg-blue-500/10 border-blue-500/30' : ''}
                                                    ${fav.tier === 1 ? 'bg-green-500/5 border-l-2 border-l-green-500' : ''}
                                                    ${fav.tier === 2 ? 'bg-yellow-500/5 border-l-2 border-l-yellow-500' : ''}
                                                    ${fav.tier === 3 ? 'bg-red-500/5 border-l-2 border-l-red-500' : ''}
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
                                                    <td className="p-4 border-r border-white/5 text-center">
                                                        <select
                                                            value={fav.tier ?? ''}
                                                            onChange={(e) => {
                                                                const tierValue = e.target.value === '' ? null : parseInt(e.target.value);
                                                                handleUpdateTier(fav, tierValue);
                                                            }}
                                                            className={`text-xs font-medium px-2 py-1 rounded border transition-all ${
                                                                fav.tier === 1 
                                                                    ? 'bg-green-500/20 text-green-400 border-green-500/50 hover:bg-green-500/30' 
                                                                    : fav.tier === 2
                                                                    ? 'bg-yellow-500/20 text-yellow-400 border-yellow-500/50 hover:bg-yellow-500/30'
                                                                    : fav.tier === 3
                                                                    ? 'bg-red-500/20 text-red-400 border-red-500/50 hover:bg-red-500/30'
                                                                    : 'bg-white/5 text-gray-400 border-white/10 hover:bg-white/10'
                                                            }`}
                                                            onClick={(e) => e.stopPropagation()}
                                                        >
                                                            <option value="">Sem tier</option>
                                                            <option value="1">Tier 1</option>
                                                            <option value="2">Tier 2</option>
                                                            <option value="3">Tier 3</option>
                                                        </select>
                                                    </td>
                                                    <td className="p-2 border-r border-white/5 font-bold text-white tracking-wide">{fav.symbol}</td>
                                                    <td className="p-2 border-r border-white/5 text-blue-300 font-medium">{fav.strategy_name.replace(/_/g, ' ')}</td>
                                                    <td className="p-2 border-r border-white/5 text-center" title="Long = compra na entrada / Short = venda na entrada">
                                                        {((fav.parameters?.direction as string) || 'long').toLowerCase() === 'short' ? (
                                                            <span className="px-2 py-1 rounded text-xs font-medium bg-orange-500/20 text-orange-400 border border-orange-500/40">Short</span>
                                                        ) : (
                                                            <span className="px-2 py-1 rounded text-xs font-medium bg-emerald-500/20 text-emerald-400 border border-emerald-500/40">Long</span>
                                                        )}
                                                    </td>
                                                    <td className="p-2 border-r border-white/5 text-center text-white/90" title="Timeframe rodado">
                                                        <span className="px-2 py-1 rounded bg-white/5 text-xs font-mono">{fav.timeframe}</span>
                                                    </td>
                                                    <td className="p-2 border-r border-white/5 text-center text-gray-300 text-xs whitespace-nowrap" title="Período em que a estratégia foi testada">
                                                        {formatPeriod(fav)}
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
                                                        {getTradesCount(fav)}
                                                    </td>
                                                    <td className="p-2 border-r border-white/5 text-right text-gray-300 font-mono">
                                                        {formatPct(m.win_rate)}
                                                    </td>
                                                    <td className={`p-2 border-r border-white/5 text-right font-bold font-mono ${(totalReturn || 0) >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                                                        {formatPct(totalReturn)}
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
                                                            onClick={() => handleViewResults(fav)}
                                                            disabled={loadingBacktestId === fav.id}
                                                            className="p-1.5 hover:bg-green-500/20 rounded-lg text-green-400 hover:text-green-300 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                                                            title="View Results"
                                                        >
                                                            {loadingBacktestId === fav.id ? (
                                                                <div className="w-4 h-4 border-2 border-green-400 border-t-transparent rounded-full animate-spin"></div>
                                                            ) : (
                                                                <BarChart3 className="w-4 h-4" />
                                                            )}
                                                        </button>
                                                        <button
                                                            onClick={() => handleOpenAgent(fav)}
                                                            className="p-1.5 hover:bg-purple-500/20 rounded-lg text-gray-400 hover:text-purple-300 transition-colors"
                                                            title="Chat com o agente"
                                                        >
                                                            <MessageCircle className="w-4 h-4" />
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
                                    {!isLoading && filteredFavorites.length > 0 && hasMore && (
                                        <tr>
                                            <td colSpan={21} className="p-6 text-center text-gray-500 text-sm">
                                                <div ref={sentinelRef} />
                                                <span className="animate-pulse">Carregando mais…</span>
                                            </td>
                                        </tr>
                                    )}
                                </tbody>
                            </table>
                        </div>

                        {/* Footer / Status Bar - Replaces System Status */}
                        <div className="p-4 bg-white/5 border-t border-white/10 flex flex-col gap-3 lg:flex-row lg:justify-between lg:items-center text-sm">
                            <div className="flex items-center gap-2 text-gray-400">
                                <span className="w-2 h-2 rounded-full bg-blue-500"></span>
                                {hasMore
                                    ? `Mostrando ${visibleFavorites.length} de ${filteredFavorites.length} estratégias — role para carregar mais`
                                    : `${filteredFavorites.length} estratégias carregadas`}
                            </div>
                            {selectedIds.length > 0 && (
                                <div className="flex flex-col sm:flex-row sm:items-center gap-2 sm:gap-4 animate-in fade-in slide-in-from-right-4 w-full lg:w-auto">
                                    <span className="text-blue-400 font-medium">{selectedIds.length} selected</span>
                                    <button
                                        onClick={() => setIsCompareOpen(true)}
                                        disabled={selectedIds.length < 2}
                                        className="px-4 py-2.5 lg:py-1.5 bg-blue-600 hover:bg-blue-500 text-white text-sm font-semibold rounded-lg shadow-lg shadow-blue-500/20 disabled:opacity-50 disabled:cursor-not-allowed transition-all min-h-11 lg:min-h-0 w-full sm:w-auto"
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
                    symbol={selectedTradesSymbol}
                    templateName={selectedTradesTemplate}
                    timeframe={selectedTradesTimeframe}
                />

                <AgentChatModal
                    open={isAgentModalOpen}
                    onClose={() => setIsAgentModalOpen(false)}
                    favorite={selectedAgentFavorite ? {
                        id: selectedAgentFavorite.id,
                        name: selectedAgentFavorite.name,
                        symbol: selectedAgentFavorite.symbol,
                        timeframe: selectedAgentFavorite.timeframe,
                        strategy_name: selectedAgentFavorite.strategy_name,
                    } : null}
                />
            </div>
        </div>
    );
};

export default FavoritesDashboard;
