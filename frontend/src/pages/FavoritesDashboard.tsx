import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { Trash2, Search, List, Activity, BarChart3, Bell, Star } from 'lucide-react';
import { useInfiniteScroll } from '@/hooks/useInfiniteScroll';
import { API_BASE_URL } from '../lib/apiBase';
import { authFetch } from '@/lib/authFetch';
import { useAuth } from '@/stores/authStore';
import { ScreenHelpPanel } from '@/components/onboarding/ScreenHelpPanel';
import {
    hasAvailableIndicatorSeries,
    type StrategyTransparency,
} from '@/lib/strategyTransparency';
import type { TradeExplanation } from '@/types/tradeExplanation';
import type { MonitorSyncStatus } from '@/lib/signalHistory';

import * as XLSX from 'xlsx';

type MonitorSignalSyncResult = {
    trades: any[] | null;
    signal_history: MonitorSignalHistoryItem[];
    status: MonitorSyncStatus;
};

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
    notify_telegram: boolean;
    start_date?: string | null;
    end_date?: string | null;
    is_strategy_protected?: boolean;
    strategy_display_name?: string | null;
    strategy_description?: string | null;
    strategy_transparency?: StrategyTransparency | Record<string, unknown> | null;
    auto_refresh_status?: string | null;
    auto_refresh_error?: string | null;
    auto_refresh_started_at?: string | null;
    auto_refresh_completed_at?: string | null;
    auto_refresh_run_id?: string | null;
}

interface MonitorSignalHistoryItem {
    timestamp?: string | null;
    signal?: number | null;
    type?: string | null;
    reason?: string | null;
    price?: number | null;
    explanation?: TradeExplanation | null;
}

interface MonitorOpportunity {
    id?: number;
    symbol?: string;
    timeframe?: string;
    template_name?: string;
    name?: string;
    signal_history?: MonitorSignalHistoryItem[] | null;
    trade_explanation?: TradeExplanation | null;
}

const isCryptoPair = (symbol: string): boolean => String(symbol || '').includes('/');

const CURRENT_CHART_CANDLE_LIMIT = 300;
const FAVORITE_ANALYSIS_OPTIONAL_SYNC_TIMEOUT_MS = 2500;

const getSavedAnalysisCandles = (fav: FavoriteStrategy): any[] => {
    const candles = fav.metrics?.analysis_candles;
    return Array.isArray(candles) ? candles : [];
};

const normalizeText = (value: unknown): string => String(value || '').trim().toLowerCase();

const normalizeSearchText = (value: unknown): string => normalizeText(value)
    .replace(/[/_-]+/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();

const getSearchTerms = (value: string): string[] => normalizeSearchText(value)
    .split(/\s+/)
    .filter(Boolean);

const getCandleTimestampKey = (candle: any): string => {
    const rawTimestamp = candle?.timestamp_utc ?? candle?.timestamp ?? candle?.time;
    if (!rawTimestamp) return '';
    const parsed = Date.parse(String(rawTimestamp));
    return Number.isFinite(parsed) ? new Date(parsed).toISOString() : String(rawTimestamp);
};

const mergeAnalysisCandles = (currentCandles: any[], savedCandles: any[]): any[] => {
    if (savedCandles.length === 0) return currentCandles;
    if (currentCandles.length === 0) return savedCandles;

    const byTimestamp = new Map<string, any>();
    savedCandles.forEach((candle) => {
        const key = getCandleTimestampKey(candle);
        if (key) byTimestamp.set(key, candle);
    });
    currentCandles.forEach((candle) => {
        const key = getCandleTimestampKey(candle);
        if (key) byTimestamp.set(key, candle);
    });

    const merged = Array.from(byTimestamp.values()).sort((left, right) => (
        Date.parse(getCandleTimestampKey(left)) - Date.parse(getCandleTimestampKey(right))
    ));
    return merged.length > 0 ? merged : (savedCandles.length > currentCandles.length ? savedCandles : currentCandles);
};

const resolveWithTimeout = <T,>(
    promise: Promise<T>,
    fallback: T,
    timeoutMs = FAVORITE_ANALYSIS_OPTIONAL_SYNC_TIMEOUT_MS,
    onTimeout?: () => void,
): Promise<T> => new Promise((resolve) => {
    let settled = false;
    const timeoutId = window.setTimeout(() => {
        if (settled) return;
        settled = true;
        onTimeout?.();
        resolve(fallback);
    }, timeoutMs);

    promise
        .then((value) => {
            if (settled) return;
            settled = true;
            window.clearTimeout(timeoutId);
            resolve(value);
        })
        .catch(() => {
            if (settled) return;
            settled = true;
            window.clearTimeout(timeoutId);
            resolve(fallback);
        });
});

const calculateSignalProfit = (
    entryPrice: number | null | undefined,
    exitPrice: number | null | undefined,
    direction: string,
): number | undefined => {
    const entry = Number(entryPrice);
    const exit = Number(exitPrice);
    if (!Number.isFinite(entry) || !Number.isFinite(exit) || entry <= 0) return undefined;
    return direction === 'short' ? (entry - exit) / entry : (exit - entry) / entry;
};

const buildTradesFromSignalHistory = (
    history: MonitorSignalHistoryItem[] | null | undefined,
    direction: string,
    currentStateExplanation?: TradeExplanation | null,
): any[] | null => {
    if (!Array.isArray(history) || history.length === 0) return null;

    const sortedHistory = history
        .filter((item) => item && item.timestamp && (item.type === 'entry' || item.type === 'exit'))
        .sort((left, right) => Date.parse(String(left.timestamp)) - Date.parse(String(right.timestamp)));

    const trades: any[] = [];
    let activeEntry: MonitorSignalHistoryItem | null = null;

    sortedHistory.forEach((item) => {
        if (item.type === 'entry') {
            activeEntry = item;
            return;
        }

        if (item.type === 'exit' && activeEntry) {
            const entryPrice = Number(activeEntry.price);
            const exitPrice = Number(item.price);
            trades.push({
                entry_time: activeEntry.timestamp,
                entry_price: Number.isFinite(entryPrice) ? entryPrice : 0,
                exit_time: item.timestamp,
                exit_price: Number.isFinite(exitPrice) ? exitPrice : undefined,
                profit: calculateSignalProfit(entryPrice, exitPrice, direction),
                type: direction === 'short' ? 'short' : 'long',
                signal_type: item.reason === 'stop_loss' ? 'Stop' : 'Monitor',
                entry_signal_type: direction === 'short' ? 'Vender' : 'Comprar',
                exit_reason: item.reason || 'monitor_signal',
                source: 'monitor_signal_history',
                entry_explanation: activeEntry.explanation,
                exit_explanation: item.explanation,
            });
            activeEntry = null;
        }
    });

    if (activeEntry) {
        const entryPrice = Number(activeEntry.price);
        trades.push({
            entry_time: activeEntry.timestamp,
            entry_price: Number.isFinite(entryPrice) ? entryPrice : 0,
            type: direction === 'short' ? 'short' : 'long',
            entry_signal_type: direction === 'short' ? 'Vender' : 'Comprar',
            source: 'monitor_signal_history',
            entry_explanation: activeEntry.explanation,
            current_state_explanation: currentStateExplanation,
        });
    }

    return trades.length > 0 ? trades : null;
};

const normalizeTradeTime = (value: unknown): string => {
    if (!value) return '';
    const timestamp = Date.parse(String(value));
    return Number.isFinite(timestamp) ? new Date(timestamp).toISOString() : String(value);
};

const normalizeTradeNumber = (value: unknown): string => {
    const numberValue = Number(value);
    return Number.isFinite(numberValue) ? numberValue.toFixed(8) : '';
};

const getTradeDedupeKey = (trade: any): string => [
    normalizeTradeTime(trade?.entry_time),
    normalizeTradeTime(trade?.exit_time),
    normalizeTradeNumber(trade?.entry_price),
    normalizeTradeNumber(trade?.exit_price),
    normalizeText(trade?.type),
].join('|');

const mergeFavoriteAndMonitorTrades = (
    favoriteTrades: any[],
    monitorTrades: any[] | null | undefined,
): any[] => {
    const merged = Array.isArray(favoriteTrades) ? [...favoriteTrades] : [];
    if (!Array.isArray(monitorTrades) || monitorTrades.length === 0) return merged;

    const seen = new Set(merged.map(getTradeDedupeKey));
    monitorTrades.forEach((trade) => {
        const key = getTradeDedupeKey(trade);
        if (!seen.has(key)) {
            merged.push(trade);
            seen.add(key);
        }
    });

    return merged;
};

const FavoritesDashboard: React.FC = () => {
    const navigate = useNavigate();
    const queryClient = useQueryClient();
    const { user } = useAuth();
    const isAdmin = user?.isAdmin === true;
    const [searchTerm, setSearchTerm] = useState('');
    const [selectedIds, setSelectedIds] = useState<number[]>([]);
    const [isCompareOpen, setIsCompareOpen] = useState(false);
    const [tierFilter, setTierFilter] = useState<'all' | '1' | '2' | '3' | 'none'>('all');

    const [loadingAnalysisId, setLoadingAnalysisId] = useState<number | null>(null);

    // Fetch favorites
    const { data: favorites, isLoading } = useQuery({
        queryKey: ['favorites', user?.id ?? 'anonymous'],
        queryFn: async () => {
            const res = await authFetch(`${API_BASE_URL}/favorites/`);
            if (!res.ok) throw new Error('Failed to fetch favorites');
            const data = await res.json() as FavoriteStrategy[];
            // Avoid logging large payloads in production/dev UI: can freeze browser on slower devices.
            console.log(`📥 Loaded favorites: ${data?.length ?? 0} items`);
            return data;
        }
    });

    // Delete mutation
    const deleteMutation = useMutation({
        mutationFn: async (id: number) => {
            const res = await authFetch(`${API_BASE_URL}/favorites/${id}`, {
                method: 'DELETE'
            });
            if (!res.ok) throw new Error('Failed to delete');
        },
        onSuccess: (_, id) => {
            queryClient.invalidateQueries({ queryKey: ['favorites', user?.id ?? 'anonymous'] });
            setSelectedIds(prev => prev.filter(sid => sid !== id));
        }
    });

    // Update tier mutation
    const updateTierMutation = useMutation({
        mutationFn: async ({ id, tier }: { id: number; tier: number | null }) => {
            const res = await authFetch(`${API_BASE_URL}/favorites/${id}`, {
                method: 'PATCH',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ tier })
            });
            if (!res.ok) throw new Error('Failed to update tier');
            return res.json();
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['favorites', user?.id ?? 'anonymous'] });
        }
    });

    const handleUpdateTier = (fav: FavoriteStrategy, tier: number | null) => {
        updateTierMutation.mutate({ id: fav.id, tier });
    };

    const updateTelegramMutation = useMutation({
        mutationFn: async ({ id, notify_telegram }: { id: number; notify_telegram: boolean }) => {
            const res = await authFetch(`${API_BASE_URL}/favorites/${id}`, {
                method: 'PATCH',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ notify_telegram })
            });
            if (!res.ok) throw new Error('Failed to update Telegram notification');
            return res.json();
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['favorites', user?.id ?? 'anonymous'] });
        }
    });

    const handleToggleTelegram = (fav: FavoriteStrategy) => {
        updateTelegramMutation.mutate({ id: fav.id, notify_telegram: !fav.notify_telegram });
    };

    const getStarCount = (tier: number | null): number => {
        if (tier === 1) return 3;
        if (tier === 2) return 2;
        if (tier === 3) return 1;
        return 0;
    };

    const getTierFromStars = (stars: number): number | null => {
        if (stars === 3) return 1;
        if (stars === 2) return 2;
        if (stars === 1) return 3;
        return null;
    };

    const renderStarTierControl = (fav: FavoriteStrategy, compact = false) => {
        const selectedStars = getStarCount(fav.tier);
        const isSaving = updateTierMutation.isPending;

        return (
            <div className="flex items-center justify-center gap-1" aria-label="Prioridade por estrelas">
                {[1, 2, 3].map((stars) => {
                    const active = stars <= selectedStars;
                    return (
                        <button
                            key={stars}
                            type="button"
                            disabled={isSaving}
                            aria-pressed={active}
                            title={`${stars} ${stars === 1 ? 'estrela' : 'estrelas'}`}
                            onClick={(event) => {
                                event.stopPropagation();
                                handleUpdateTier(fav, selectedStars === stars ? null : getTierFromStars(stars));
                            }}
                            className={[
                                'inline-flex items-center justify-center rounded-md border transition-colors',
                                compact ? 'h-9 w-9' : 'h-8 w-8',
                                active
                                    ? 'border-amber-400 bg-amber-400/15 text-amber-500'
                                    : 'border-zinc-200 bg-zinc-50 text-zinc-400 hover:text-amber-500',
                                isSaving ? 'opacity-60 cursor-wait' : '',
                            ].join(' ')}
                        >
                            <Star className={compact ? 'h-4 w-4' : 'h-3.5 w-3.5'} fill={active ? 'currentColor' : 'none'} />
                        </button>
                    );
                })}
            </div>
        );
    };

    const renderTelegramControl = (fav: FavoriteStrategy, compact = false) => {
        const active = fav.notify_telegram !== false;
        const isSaving = updateTelegramMutation.isPending;

        return (
            <button
                type="button"
                disabled={isSaving}
                aria-pressed={active}
                title={active ? 'Notificar Telegram ativo' : 'Notificar Telegram desligado'}
                onClick={(event) => {
                    event.stopPropagation();
                    handleToggleTelegram(fav);
                }}
                className={[
                    'telegram-toggle inline-flex items-center justify-center gap-1 rounded-md border transition-colors',
                    compact ? 'h-9 min-w-[3.5rem] px-2 text-xs' : 'h-8 min-w-[4.5rem] px-2 text-xs',
                    active
                        ? 'border-emerald-400 bg-emerald-400/15 text-emerald-600'
                        : 'border-zinc-200 bg-zinc-50 text-zinc-400 hover:text-emerald-600',
                    isSaving ? 'opacity-60 cursor-wait' : '',
                ].join(' ')}
            >
                <Bell className={compact ? 'h-4 w-4' : 'h-3.5 w-3.5'} fill={active ? 'currentColor' : 'none'} />
                {compact ? 'TG' : active ? 'On' : 'Off'}
            </button>
        );
    };

    const getFavoriteStrategyLabel = (fav: FavoriteStrategy): string => {
        const manifestDisplayName = fav.strategy_transparency?.display_name;
        return fav.strategy_display_name || (typeof manifestDisplayName === 'string' ? manifestDisplayName : '') || (fav.is_strategy_protected
            ? 'Estratégia protegida'
            : fav.strategy_name.replace(/_/g, ' '));
    };

    const normalizeStrategyComparison = (value: string): string => {
        return value
            .toLowerCase()
            .replace(/[_-]+/g, ' ')
            .replace(/\([^)]*\)/g, ' ')
            .replace(/\s+/g, ' ')
            .trim();
    };

    const getFavoriteName = (fav: FavoriteStrategy): string => {
        const label = getFavoriteStrategyLabel(fav).trim();
        return label || fav.name || fav.symbol || 'Estratégia';
    };

    const getFavoriteStrategyName = (fav: FavoriteStrategy): string => {
        let name = getFavoriteName(fav).trim();
        const symbolPattern = fav.symbol.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
        const timeframePattern = fav.timeframe.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
        name = name
            .replace(new RegExp(`\\b${symbolPattern}\\b`, 'gi'), ' ')
            .replace(new RegExp(`\\b${timeframePattern}\\b`, 'gi'), ' ')
            .replace(/\s*[-–—|/]\s*$/g, ' ')
            .replace(/^\s*[-–—|/]\s*/g, ' ')
            .replace(/\s{2,}/g, ' ')
            .trim();
        const label = getFavoriteStrategyLabel(fav).trim();
        const readableName = name.replace(/_/g, ' ').replace(/\s{2,}/g, ' ').trim();
        const comparableName = normalizeStrategyComparison(readableName);
        const comparableLabel = normalizeStrategyComparison(label);
        if (label && comparableLabel && (
            comparableName === comparableLabel
            || comparableName.startsWith(`${comparableLabel} `)
        )) {
            return label;
        }
        return label || readableName;
    };

    const getGridStrategyDetail = (fav: FavoriteStrategy): string | null => {
        const label = getFavoriteStrategyLabel(fav).trim();
        if (!label || label.toLowerCase() === getFavoriteStrategyName(fav).trim().toLowerCase()) return null;
        if (fav.is_strategy_protected && label.toLowerCase() === 'estratégia protegida') return null;
        return label;
    };

    const getFavoriteStrategyDescription = (fav: FavoriteStrategy): string | null => {
        const description = String(fav.strategy_description || '').trim();
        return description || null;
    };

    const favoriteMatchesSearch = (fav: FavoriteStrategy, query: string): boolean => {
        const normalizedQuery = normalizeSearchText(query);
        if (!normalizedQuery) return true;

        const symbol = String(fav.symbol || '');
        const [baseAsset, quoteAsset] = symbol.split('/');
        const searchHaystack = [
            fav.name,
            symbol,
            baseAsset,
            quoteAsset,
            fav.strategy_name,
            getFavoriteStrategyLabel(fav),
            getFavoriteStrategyName(fav),
            fav.strategy_description,
            fav.timeframe,
        ]
            .map(normalizeSearchText)
            .filter(Boolean)
            .join(' ');

        if (searchHaystack.includes(normalizedQuery)) {
            return true;
        }

        return getSearchTerms(query).every((term) => searchHaystack.includes(term));
    };

    const isFavoriteProtected = (fav: FavoriteStrategy): boolean => Boolean(fav.is_strategy_protected);

    const getSavedTrades = (fav: FavoriteStrategy): any[] | null => {
        const savedTrades = fav.metrics?.trades;
        return Array.isArray(savedTrades) ? savedTrades : null;
    };

    const getSummaryTradeCount = (fav: FavoriteStrategy): number => {
        const summaryTradeCount = Number(
            fav.metrics?.total_trades ?? (typeof fav.metrics?.trades === 'number' ? fav.metrics.trades : 0)
        );
        return Number.isFinite(summaryTradeCount) ? summaryTradeCount : 0;
    };

    const loadCurrentChartCandles = async (fav: FavoriteStrategy): Promise<any[]> => {
        const url = new URL(`${API_BASE_URL}/market/candles`, window.location.origin);
        url.searchParams.set('symbol', fav.symbol);
        url.searchParams.set('timeframe', fav.timeframe);
        url.searchParams.set('limit', String(CURRENT_CHART_CANDLE_LIMIT));
        url.searchParams.set('full_history', 'true');

        try {
            const response = await authFetch(url.toString());
            const payload = await response.json().catch(() => ({}));
            if (!response.ok) {
                throw new Error(String(payload?.detail || `Failed to load candles (${response.status})`));
            }
            const candles = Array.isArray(payload?.candles) ? payload.candles : [];
            return candles.length > 0 ? candles : getSavedAnalysisCandles(fav);
        } catch (error) {
            console.warn(`Falling back to saved favorite candles for ${fav.symbol} ${fav.timeframe}`, error);
            return getSavedAnalysisCandles(fav);
        }
    };

    const findMatchingOpportunity = (
        fav: FavoriteStrategy,
        opportunities: MonitorOpportunity[],
    ): MonitorOpportunity | null => {
        const byId = opportunities.find((item) => Number(item.id) === Number(fav.id));
        if (byId) return byId;

        const favoriteSymbol = normalizeText(fav.symbol);
        const favoriteTimeframe = normalizeText(fav.timeframe);
        const favoriteStrategy = normalizeText(fav.strategy_name);
        return opportunities.find((item) => (
            normalizeText(item.symbol) === favoriteSymbol
            && normalizeText(item.timeframe) === favoriteTimeframe
            && (
                normalizeText(item.template_name) === favoriteStrategy
                || normalizeText(item.name).includes(favoriteSymbol)
                || isFavoriteProtected(fav)
            )
        )) || null;
    };

    const loadMonitorSyncedTrades = async (fav: FavoriteStrategy): Promise<MonitorSignalSyncResult> => {
        const url = new URL(`${API_BASE_URL}/opportunities/`, window.location.origin);
        // Prefer Monitor cache so "Ver resultados" does not wait on a full refresh.
        url.searchParams.set('refresh', 'false');
        url.searchParams.set('tier', 'all');

        try {
            const response = await authFetch(url.toString());
            const payload = await response.json().catch(() => []);
            if (!response.ok || !Array.isArray(payload)) {
                throw new Error(`Failed to sync monitor signals (${response.status})`);
            }

            const opportunity = findMatchingOpportunity(fav, payload);
            if (!opportunity) {
                return { trades: null, signal_history: [], status: 'missing' };
            }

            const history = Array.isArray(opportunity.signal_history) ? opportunity.signal_history : [];
            if (history.length === 0) {
                return { trades: null, signal_history: [], status: 'empty' };
            }

            const direction = String(fav.parameters?.direction || 'long').toLowerCase();
            return {
                trades: buildTradesFromSignalHistory(
                    history,
                    direction,
                    opportunity?.trade_explanation,
                ),
                signal_history: history,
                status: 'ok',
            };
        } catch (error) {
            console.warn(`Falling back to saved favorite trades for ${fav.symbol} ${fav.timeframe}`, error);
            return { trades: null, signal_history: [], status: 'error' };
        }
    };

    const loadTradesForAnalysis = async (fav: FavoriteStrategy) => {
        const savedTrades = getSavedTrades(fav);
        const summaryTradeCount = getSummaryTradeCount(fav);
        const hasCachedHistory = fav.metrics?.trades_history_cached === true;
        const hasChartContext = Array.isArray(fav.metrics?.analysis_candles)
            && fav.metrics.analysis_candles.length > 0;
        const isProtectedForCommonUser = isFavoriteProtected(fav) && !isAdmin;
        const cachedStrategyTransparency = fav.metrics?.analysis_strategy_transparency
            ?? fav.strategy_transparency
            ?? null;
        const hasUsableCachedTransparency = hasAvailableIndicatorSeries(
            cachedStrategyTransparency,
            fav.timeframe,
        );
        const hasRecoverableCachedAnalysis = Boolean(savedTrades)
            && (hasChartContext || hasCachedHistory);
        const needsLegacyTransparencyHydration = hasRecoverableCachedAnalysis
            && !hasUsableCachedTransparency;

        if (
            hasUsableCachedTransparency
            && savedTrades
            && (hasChartContext || hasCachedHistory || summaryTradeCount <= 0)
        ) {
            return {
                trades: savedTrades,
                metrics: fav.metrics || {},
                candles: getSavedAnalysisCandles(fav),
                indicatorData: fav.metrics?.analysis_indicator_data && typeof fav.metrics.analysis_indicator_data === 'object'
                    ? fav.metrics.analysis_indicator_data
                    : {},
                executionMode: typeof fav.metrics?.analysis_execution_mode === 'string'
                    ? fav.metrics.analysis_execution_mode
                    : 'favorite_cache',
                strategyTransparency: cachedStrategyTransparency,
            };
        }

        if (isProtectedForCommonUser && !needsLegacyTransparencyHydration) {
            return {
                trades: savedTrades || [],
                metrics: fav.metrics || {},
                candles: getSavedAnalysisCandles(fav),
                indicatorData: {},
                executionMode: 'favorite_protected_cache',
                strategyTransparency: cachedStrategyTransparency,
            };
        }

        if (summaryTradeCount <= 0 && !needsLegacyTransparencyHydration) {
            return {
                trades: [],
                metrics: fav.metrics || {},
                candles: [],
                indicatorData: {},
                executionMode: 'favorite_cache',
                strategyTransparency: cachedStrategyTransparency,
            };
        }

        try {
            const res = await authFetch(`${API_BASE_URL}/favorites/${fav.id}/trades`);
            if (!res.ok) {
                throw new Error(`Failed to load trades (${res.status})`);
            }

            const payload = await res.json();
            const regeneratedTrades = Array.isArray(payload.trades) ? payload.trades : [];
            const nextMetrics = payload.metrics && typeof payload.metrics === 'object'
                ? payload.metrics
                : {
                    ...(fav.metrics || {}),
                    trades: regeneratedTrades,
                    trades_history_cached: true,
                    trades_metrics_match: payload.metrics_match !== false,
                    trades_metrics_deltas: payload.metrics_deltas || {},
                };

            queryClient.setQueryData<FavoriteStrategy[]>(
                ['favorites', user?.id ?? 'anonymous'],
                (current) => current?.map((item) => (
                    item.id === fav.id
                        ? {
                            ...item,
                            metrics: nextMetrics,
                            strategy_transparency: payload.strategy_transparency
                                ?? item.strategy_transparency
                                ?? null,
                        }
                        : item
                ))
            );

            return {
                trades: regeneratedTrades,
                metrics: nextMetrics,
                candles: Array.isArray(payload.candles) ? payload.candles : [],
                indicatorData: payload.indicator_data && typeof payload.indicator_data === 'object'
                    ? payload.indicator_data
                    : {},
                executionMode: typeof payload.execution_mode === 'string'
                    ? payload.execution_mode
                    : 'favorite_regenerated',
                strategyTransparency: payload.strategy_transparency ?? fav.strategy_transparency ?? null,
            };
        } catch (error) {
            if (!needsLegacyTransparencyHydration) throw error;

            console.warn(
                `Opening cached favorite without hydrated indicator series for ${fav.symbol} ${fav.timeframe}`,
                error,
            );
            return {
                trades: savedTrades || [],
                metrics: fav.metrics || {},
                candles: getSavedAnalysisCandles(fav),
                indicatorData: isProtectedForCommonUser
                    ? {}
                    : fav.metrics?.analysis_indicator_data && typeof fav.metrics.analysis_indicator_data === 'object'
                        ? fav.metrics.analysis_indicator_data
                        : {},
                executionMode: typeof fav.metrics?.analysis_execution_mode === 'string'
                    ? fav.metrics.analysis_execution_mode
                    : isProtectedForCommonUser
                        ? 'favorite_protected_cache'
                        : 'favorite_cache',
                strategyTransparency: cachedStrategyTransparency,
            };
        }
    };

    const buildFavoriteAnalysisResult = (
        fav: FavoriteStrategy,
        recovered: Awaited<ReturnType<typeof loadTradesForAnalysis>>
    ) => {
        const sourceMetrics = recovered.metrics || fav.metrics || {};
        const trades = Array.isArray(recovered.trades) ? recovered.trades : [];
        const totalReturn = Number(
            sourceMetrics.total_return ?? (
                sourceMetrics.total_return_pct != null ? Number(sourceMetrics.total_return_pct) / 100 : 0
            )
        );
        const totalTrades = Number(sourceMetrics.total_trades ?? trades.length);
        const metrics = {
            ...sourceMetrics,
            total_trades: Number.isFinite(totalTrades) ? totalTrades : trades.length,
            total_return: Number.isFinite(totalReturn) ? totalReturn : 0,
            win_rate: Number(sourceMetrics.win_rate ?? 0),
            avg_profit: Number(sourceMetrics.avg_profit ?? (
                totalTrades > 0 && Number.isFinite(totalReturn) ? totalReturn / totalTrades : 0
            )),
        };
        return {
            template_name: isFavoriteProtected(fav) ? getFavoriteStrategyLabel(fav) : fav.strategy_name,
            symbol: fav.symbol,
            timeframe: fav.timeframe,
            parameters: isFavoriteProtected(fav) && !isAdmin ? {} : fav.parameters || {},
            metrics,
            trades,
            indicator_data: isFavoriteProtected(fav) && !isAdmin ? {} : recovered.indicatorData || {},
            candles: recovered.candles || [],
            execution_mode: recovered.executionMode,
            direction: (fav.parameters?.direction as string) || 'long',
            is_strategy_protected: isFavoriteProtected(fav) && !isAdmin,
            strategy_transparency: recovered.strategyTransparency ?? fav.strategy_transparency ?? null,
        };
    };

    const handleViewAnalysis = async (fav: FavoriteStrategy) => {
        setLoadingAnalysisId(fav.id);
        try {
            const cachedAnalysisFallback = {
                trades: getSavedTrades(fav) || [],
                metrics: fav.metrics || {},
                candles: getSavedAnalysisCandles(fav),
                indicatorData: fav.metrics?.analysis_indicator_data && typeof fav.metrics.analysis_indicator_data === 'object'
                    ? fav.metrics.analysis_indicator_data
                    : {},
                executionMode: 'favorite_cache_timeout',
                strategyTransparency: fav.metrics?.analysis_strategy_transparency ?? fav.strategy_transparency ?? null,
            };
            const recovered = await resolveWithTimeout(
                loadTradesForAnalysis(fav),
                cachedAnalysisFallback,
                FAVORITE_ANALYSIS_OPTIONAL_SYNC_TIMEOUT_MS,
                () => console.warn(`Opening favorite analysis from saved summary for ${fav.symbol} ${fav.timeframe}; trade recovery timed out.`),
            );
            const monitorSyncFallback: MonitorSignalSyncResult = {
                trades: null,
                signal_history: [],
                status: 'timeout',
            };
            const [currentCandles, monitorSync] = await Promise.all([
                resolveWithTimeout(
                    loadCurrentChartCandles(fav),
                    recovered.candles || [],
                    FAVORITE_ANALYSIS_OPTIONAL_SYNC_TIMEOUT_MS,
                    () => console.warn(`Using saved favorite candles for ${fav.symbol} ${fav.timeframe}; current candle load timed out.`),
                ),
                resolveWithTimeout(
                    loadMonitorSyncedTrades(fav),
                    monitorSyncFallback,
                    FAVORITE_ANALYSIS_OPTIONAL_SYNC_TIMEOUT_MS,
                    () => console.warn(`Opening favorite analysis without monitor trade sync for ${fav.symbol} ${fav.timeframe}; monitor sync timed out.`),
                ),
            ]);
            const chartCandles = mergeAnalysisCandles(currentCandles, recovered.candles || []);
            const analysisResult = buildFavoriteAnalysisResult(fav, recovered);
            analysisResult.candles = chartCandles || [];
            if (monitorSync.trades && monitorSync.trades.length > 0) {
                const mergedTrades = mergeFavoriteAndMonitorTrades(analysisResult.trades, monitorSync.trades);
                analysisResult.trades = mergedTrades;
                analysisResult.metrics = {
                    ...analysisResult.metrics,
                    total_trades: mergedTrades.filter((trade: any) => trade.exit_time && trade.exit_price).length,
                };
                analysisResult.execution_mode = 'favorite_monitor_sync_all_trades';
            }

            navigate('/combo/results', {
                state: {
                    result: {
                        ...analysisResult,
                        signal_history: monitorSync.signal_history,
                        monitor_sync_status: monitorSync.status,
                    },
                    isOptimization: false,
                    returnTo: '/favorites',
                }
            });
        } catch (error) {
            console.error('Erro ao abrir análise do favorito:', error);
            alert('Erro ao abrir análise do favorito. Verifique o console para mais detalhes.');
        } finally {
            setLoadingAnalysisId(null);
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

    const [selectedSymbol, setSelectedSymbol] = useState<string>('ALL');
    const [selectedIndicator, setSelectedIndicator] = useState<string>('ALL');
    const [selectedTimeframe, setSelectedTimeframe] = useState<string>('ALL');
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

    const getSortableNumber = (value: unknown, fallback = -Infinity): number => {
        if (value === null || value === undefined || value === '') return fallback;
        const numberValue = Number(value);
        return Number.isFinite(numberValue) ? numberValue : fallback;
    };

    const getReturnPct = (fav: FavoriteStrategy): number => {
        const metrics = fav.metrics || {};
        if (metrics.total_return_pct != null) {
            return getSortableNumber(metrics.total_return_pct);
        }
        if (metrics.total_return != null) {
            return getSortableNumber(metrics.total_return) * 100;
        }
        return -Infinity;
    };

    const getFavoriteSortValue = (fav: FavoriteStrategy, option: SortByOption): number => {
        const returnPct = getReturnPct(fav);
        const trades = Math.max(1, getTradesCount(fav));

        switch (option) {
            case 'return':
                return returnPct;
            case 'sharpe':
                return getSortableNumber(fav.metrics?.sharpe_ratio);
            case 'trades':
                return trades;
            case 'returnPerTrade':
            default:
                return returnPct === -Infinity ? -Infinity : returnPct / trades;
        }
    };

    // Get unique symbols for filter
    const uniqueSymbols = React.useMemo(() => {
        if (!favorites) return [];
        return Array.from(new Set(favorites.filter(f => isCryptoPair(f.symbol)).map(f => f.symbol))).sort();
    }, [favorites]);

    // Get unique strategy labels for filter
    const uniqueIndicators = React.useMemo(() => {
        if (!favorites) return [];
        return Array.from(new Set(favorites.filter(f => isCryptoPair(f.symbol)).map(getFavoriteStrategyLabel))).sort();
    }, [favorites]);

    const uniqueTimeframes = React.useMemo(() => {
        if (!favorites) return [];
        return Array.from(new Set(favorites.filter(f => isCryptoPair(f.symbol)).map(f => f.timeframe))).sort();
    }, [favorites]);

    const filteredFavorites = (favorites?.filter(fav => {
        const matchesSearch = favoriteMatchesSearch(fav, searchTerm);

        const matchesSymbol = selectedSymbol === 'ALL' || fav.symbol === selectedSymbol;
        const matchesIndicator = selectedIndicator === 'ALL' || getFavoriteStrategyLabel(fav) === selectedIndicator;
        const matchesTimeframe = selectedTimeframe === 'ALL' || fav.timeframe === selectedTimeframe;
        const matchesTier = tierFilter === 'all' ||
            (tierFilter === 'none' && fav.tier === null) ||
            (tierFilter !== 'none' && fav.tier === parseInt(tierFilter));
        const matchesCryptoOnly = isCryptoPair(fav.symbol);

        const favDirection = ((fav.parameters?.direction as string) || 'long').toLowerCase();
        const matchesDirection = directionFilter === 'all' || favDirection === directionFilter;

        return matchesCryptoOnly && matchesSearch && matchesSymbol && matchesIndicator && matchesTimeframe && matchesTier && matchesDirection;
    }) || []).sort((a, b) => {
        const sortValueA = getFavoriteSortValue(a, sortBy);
        const sortValueB = getFavoriteSortValue(b, sortBy);
        if (sortValueA !== sortValueB) return sortValueB > sortValueA ? 1 : -1;

        const tierA = a.tier ?? 999;
        const tierB = b.tier ?? 999;
        if (tierA !== tierB) return tierA - tierB;

        const createdDelta = Date.parse(b.created_at || '') - Date.parse(a.created_at || '');
        if (Number.isFinite(createdDelta) && createdDelta !== 0) return createdDelta;

        return a.id - b.id;
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
                Strategy: getFavoriteStrategyLabel(fav),
                Direção: direction === 'short' ? 'Short' : 'Long',
                Timeframe: fav.timeframe,
                Período: formatPeriod(fav),
                Parameters: formatParams(fav.parameters, isFavoriteProtected(fav)),
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
    const formatParams = (params: Record<string, any>, protectedStrategy = false) => {
        if (protectedStrategy) return 'Protegido';
        if (!params || Object.keys(params).length === 0) return 'Sem parametros';
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

    const formatRefreshStatus = (fav: FavoriteStrategy): { label: string; className: string; title?: string } => {
        const status = (fav.auto_refresh_status || '').toUpperCase();
        const completedAt = fav.auto_refresh_completed_at || fav.auto_refresh_started_at;
        const formattedDate = completedAt
            ? new Date(completedAt).toLocaleString('pt-BR', {
                day: '2-digit',
                month: '2-digit',
                hour: '2-digit',
                minute: '2-digit',
            })
            : null;
        if (status === 'RUNNING') {
            return { label: 'Atualizando backtest', className: 'running' };
        }
        if (status === 'FAILED') {
            return {
                label: formattedDate ? `Falha na atualização: ${formattedDate}` : 'Falha na atualização',
                className: 'failed',
                title: fav.auto_refresh_error || undefined,
            };
        }
        if (status === 'SUCCESS') {
            return {
                label: formattedDate ? `Backtest atualizado: ${formattedDate}` : 'Backtest atualizado',
                className: 'success',
            };
        }
        return { label: 'Backtest aguardando atualização', className: 'pending' };
    };

    const cryptoFavorites = React.useMemo(
        () => (favorites || []).filter((fav) => isCryptoPair(fav.symbol)),
        [favorites]
    );

    const tierCounts = React.useMemo(() => {
        return cryptoFavorites.reduce(
            (acc, fav) => {
                if (fav.tier === 1) acc.top += 1;
                else if (fav.tier === 2) acc.high += 1;
                else if (fav.tier === 3) acc.watch += 1;
                else acc.none += 1;
                return acc;
            },
            { top: 0, high: 0, watch: 0, none: 0 }
        );
    }, [cryptoFavorites]);

    const getTierDisplay = (tier: number | null) => {
        if (tier === 1) return { label: 'Top picks', stars: 3, className: 'tier-top' };
        if (tier === 2) return { label: 'Interesse alto', stars: 2, className: 'tier-high' };
        if (tier === 3) return { label: 'Acompanhar', stars: 1, className: 'tier-watch' };
        return { label: 'Sem estrela', stars: 0, className: 'tier-none' };
    };

    const splitSymbol = (symbol: string) => {
        const [base, quote] = String(symbol || '').split('/');
        return { base: base || symbol || '-', quote: quote || '' };
    };

    const formatSignedPct = (val?: number) => {
        if (val === undefined || val === null) return { text: '-', positive: true };
        const normalized = val > 1 || val < -1 ? val : val * 100;
        return { text: `${normalized >= 0 ? '+' : ''}${normalized.toFixed(2)}%`, positive: normalized >= 0 };
    };

    const tableColumnCount = isAdmin ? 19 : 17;

    return (
        <div className="app-page favorites-page favorites-workbench">
            <div className="max-w-[1920px] mx-auto page-stack">
                <ScreenHelpPanel title="Como usar Favoritos">
                    Comece por aqui: compare estrategias, abra graficos, revise trades, marque estrelas nas melhores opcoes e depois acompanhe no Monitor.
                </ScreenHelpPanel>
                <section className="fav-header">
                    <div className="fav-title-row">
                        <div className="fav-title-block">
                            <div className="fav-title-icon">
                                <Activity className="h-5 w-5" />
                            </div>
                            <div>
                                <h1>Estratégias favoritas</h1>
                                <p>Catálogo operacional para escolher quais setups entram no Monitor por estrelas.</p>
                            </div>
                        </div>
                        <div className="fav-meta">
                            <span className="fav-live-dot" />
                            <span>System Operational</span>
                            <span className="fav-meta-separator" />
                            <span>{filteredFavorites.length} filtradas</span>
                            {isAdmin ? <span>{selectedIds.length} comparadas</span> : null}
                        </div>
                    </div>

                    <div className="tier-cards" aria-label="Resumo por estrelas">
                        {[
                            { key: 'watch', label: 'Acompanhar', value: tierCounts.watch, stars: 1, helper: 'Monitorar quando fizer sentido', tone: 'watch' },
                            { key: 'high', label: 'Interesse alto', value: tierCounts.high, stars: 2, helper: 'Prioridade intermediária', tone: 'high' },
                            { key: 'top', label: 'Top picks', value: tierCounts.top, stars: 3, helper: 'Fila principal do Monitor', tone: 'top' },
                        ].map((card) => (
                            <button
                                key={card.key}
                                type="button"
                                className={`tier-card tier-card-${card.tone}`}
                                onClick={() => setTierFilter(card.key === 'top' ? '1' : card.key === 'high' ? '2' : '3')}
                            >
                                <span className="tier-card-label">{card.label}</span>
                                <span className="tier-card-count">{card.value}</span>
                                <span className="tier-card-stars">
                                    {Array.from({ length: 3 }).map((_, index) => (
                                        <Star key={index} className="h-4 w-4" fill={index < card.stars ? 'currentColor' : 'none'} />
                                    ))}
                                </span>
                                <span className="tier-card-helper">{card.helper}</span>
                            </button>
                        ))}
                    </div>

                    <div className="tier-filter" aria-label="Filtro por tier">
                        {[
                            { value: 'all', label: `Todas ${cryptoFavorites.length}` },
                            { value: '1', label: `Top picks ${tierCounts.top}` },
                            { value: '2', label: `Alto ${tierCounts.high}` },
                            { value: '3', label: `Acompanhar ${tierCounts.watch}` },
                            { value: 'none', label: `Sem estrela ${tierCounts.none}` },
                        ].map((option) => (
                            <button
                                key={option.value}
                                type="button"
                                className={tierFilter === option.value ? 'active' : ''}
                                aria-pressed={tierFilter === option.value}
                                onClick={() => setTierFilter(option.value as 'all' | '1' | '2' | '3' | 'none')}
                            >
                                {option.label}
                            </button>
                        ))}
                    </div>
                </section>

                <section className="fav-controls" aria-label="Filtros de favoritos">
                    <div className="fav-filters">
                        <label>
                            <span>Symbol</span>
                            <select value={selectedSymbol} onChange={(e) => setSelectedSymbol(e.target.value)}>
                                <option value="ALL">Todos</option>
                                {uniqueSymbols.map(sym => (
                                    <option key={sym} value={sym}>{sym}</option>
                                ))}
                            </select>
                        </label>
                        <label>
                            <span>Strategy</span>
                            <select value={selectedIndicator} onChange={(e) => setSelectedIndicator(e.target.value)}>
                                <option value="ALL">Todas</option>
                                {uniqueIndicators.map(ind => (
                                    <option key={ind} value={ind}>{ind}</option>
                                ))}
                            </select>
                        </label>
                        <label>
                            <span>Time</span>
                            <select value={selectedTimeframe} onChange={(e) => setSelectedTimeframe(e.target.value)}>
                                <option value="ALL">Todos</option>
                                {uniqueTimeframes.map(tf => (
                                    <option key={tf} value={tf}>{tf}</option>
                                ))}
                            </select>
                        </label>
                        <label>
                            <span>Direção</span>
                            <select value={directionFilter} onChange={(e) => setDirectionFilter(e.target.value as 'all' | 'long' | 'short')}>
                                <option value="all">Todas</option>
                                <option value="long">Long</option>
                                <option value="short">Short</option>
                            </select>
                        </label>
                        <label>
                            <span>Ordenar</span>
                            <select value={sortBy} onChange={(e) => setSortBy(e.target.value as SortByOption)}>
                                <option value="returnPerTrade">Ret/T %</option>
                                <option value="return">Return</option>
                                <option value="sharpe">Sharpe</option>
                                <option value="trades">Trades</option>
                            </select>
                        </label>
                    </div>

                    <div className="fav-search-row">
                        <label className="fav-search">
                            <Search className="h-4 w-4" />
                            <input
                                type="text"
                                placeholder="Buscar por símbolo ou estratégia"
                                value={searchTerm}
                                onChange={(e) => setSearchTerm(e.target.value)}
                            />
                        </label>
                        {isAdmin ? (
                            <div className="fav-actions">
                                <button type="button" onClick={handleExportExcel} className="fav-secondary-action">
                                    <List className="h-4 w-4" />
                                    Exportar
                                </button>
                                <button type="button" onClick={() => navigate('/combo/select')} className="fav-primary-action">
                                    Nova estratégia
                                </button>
                            </div>
                        ) : null}
                    </div>
                </section>

                <main className="fav-main">
                    <div className="fav-mobile-list">
                        {isLoading ? (
                            <div className="fav-empty">Carregando estratégias...</div>
                        ) : filteredFavorites.length === 0 ? (
                            <div className="fav-empty">Nenhuma estratégia favorita encontrada.</div>
                        ) : (
                            visibleFavorites.map((fav: FavoriteStrategy) => {
                                const m = fav.metrics || {};
                                const tier = getTierDisplay(fav.tier);
                                const totalReturn = formatSignedPct(m.total_return_pct ?? m.total_return);
                                const direction = ((fav.parameters?.direction as string) || 'long').toLowerCase();
                                const strategyDetail = getGridStrategyDetail(fav);
                                const strategyDescription = getFavoriteStrategyDescription(fav);
                                const refreshStatus = formatRefreshStatus(fav);
                                return (
                                    <article key={fav.id} className={`fav-mobile-card ${tier.className}`}>
                                        <div className="fav-mobile-card-head">
                                            <div>
                                                <strong>{fav.symbol}</strong>
                                                <span className="fav-strategy-name">{getFavoriteStrategyName(fav)}</span>
                                                {strategyDetail ? <span>{strategyDetail}</span> : null}
                                                {strategyDescription ? <span className="fav-strategy-description">{strategyDescription}</span> : null}
                                                <span className={`fav-refresh-status ${refreshStatus.className}`} title={refreshStatus.title}>
                                                    {refreshStatus.label}
                                                </span>
                                            </div>
                                            <span className={`fav-direction ${direction === 'short' ? 'short' : 'long'}`}>
                                                {direction === 'short' ? 'Short' : 'Long'}
                                            </span>
                                        </div>
                                        <div className="fav-mobile-stars">
                                            {renderStarTierControl(fav, true)}
                                            {isAdmin ? renderTelegramControl(fav, true) : null}
                                        </div>
                                        <div className="fav-mobile-metrics">
                                            <span><b>TF</b>{fav.timeframe}</span>
                                            <span><b>Sharpe</b>{formatNum(m.sharpe_ratio)}</span>
                                            <span><b>Trades</b>{getTradesCount(fav)}</span>
                                            <span className={totalReturn.positive ? 'positive' : 'negative'}><b>Return</b>{totalReturn.text}</span>
                                        </div>
                                        <div className="fav-mobile-actions">
                                            <button type="button" onClick={() => handleViewAnalysis(fav)} disabled={loadingAnalysisId === fav.id} title="Ver análise completa">
                                                {loadingAnalysisId === fav.id ? <span className="fav-spinner" /> : <BarChart3 className="h-4 w-4" />}
                                                Analisar
                                            </button>
                                            {isAdmin ? (
                                                <>
                                                    <button type="button" onClick={() => handleDelete(fav.id)} title="Delete"><Trash2 className="h-4 w-4" />Delete</button>
                                                </>
                                            ) : null}
                                        </div>
                                    </article>
                                );
                            })
                        )}
                    </div>

                    <div className="fav-table-shell">
                        <table className="fav-strategies">
                            <thead>
                                <tr>
                                    {isAdmin ? <th className="select-col">Sel</th> : null}
                                    <th className="stars-cell">Tier</th>
                                    {isAdmin ? <th className="telegram-col">Telegram</th> : null}
                                    <th className="symbol-col">Symbol</th>
                                    <th className="strategy-col">Estratégia</th>
                                    <th className="direction-col">Direção</th>
                                    <th className="timeframe-col">TF</th>
                                    <th className="period-col">Período</th>
                                    <th className="risk-col">Stop</th>
                                    <th className="metric-col">Sharpe</th>
                                    <th className="metric-col">Trades</th>
                                    <th className="win-col">Win%</th>
                                    <th className="return-col">Return</th>
                                    <th className="risk-col">Max DD</th>
                                    <th className="advanced-col">PF</th>
                                    <th className="advanced-col">SQN</th>
                                    <th className="advanced-col">Max L</th>
                                    <th className="advanced-col">ATR</th>
                                    <th className="actions-col">Ações</th>
                                </tr>
                            </thead>
                            <tbody>
                                {isLoading ? (
                                    <tr><td colSpan={tableColumnCount} className="fav-empty-cell">Carregando estratégias...</td></tr>
                                ) : filteredFavorites.length === 0 ? (
                                    <tr><td colSpan={tableColumnCount} className="fav-empty-cell">Nenhuma estratégia favorita encontrada.</td></tr>
                                ) : (
                                    visibleFavorites.map((fav: FavoriteStrategy) => {
                                        const isSelected = selectedIds.includes(fav.id);
                                        const m = fav.metrics || {};
                                        const tier = getTierDisplay(fav.tier);
                                        const totalReturn = formatSignedPct(m.total_return_pct ?? m.total_return);
                                        const direction = ((fav.parameters?.direction as string) || 'long').toLowerCase();
                                        const symbol = splitSymbol(fav.symbol);
                                        const stopLoss = fav.parameters?.stop_loss ?? null;
                                        const strategyDetail = getGridStrategyDetail(fav);
                                        const strategyDescription = getFavoriteStrategyDescription(fav);
                                        const refreshStatus = formatRefreshStatus(fav);

                                        return (
                                            <tr key={fav.id} className={`${tier.className} ${isSelected ? 'selected' : ''}`}>
                                                {isAdmin ? (
                                                    <td className="select-col">
                                                        <button
                                                            type="button"
                                                            onClick={() => toggleSelection(fav.id)}
                                                            className={`fav-select-row ${isSelected ? 'selected' : ''}`}
                                                            aria-label={isSelected ? 'Remover da comparação' : 'Selecionar para comparar'}
                                                        />
                                                    </td>
                                                ) : null}
                                                <td className="stars-cell">{renderStarTierControl(fav)}</td>
                                                {isAdmin ? <td className="telegram-col">{renderTelegramControl(fav)}</td> : null}
                                                <td className="symbol-col" aria-label={fav.symbol}>
                                                    <div className="sym-cell">
                                                        <span className="sym-tile">{symbol.base.slice(0, 3)}</span>
                                                        <span>
                                                            <strong>{fav.symbol}</strong>
                                                            {symbol.quote ? <small>{symbol.quote}</small> : null}
                                                        </span>
                                                    </div>
                                                </td>
                                                <td className="strategy-cell" aria-label={`${getFavoriteStrategyName(fav)} ${strategyDetail || ''} ${strategyDescription || ''}`}>
                                                    <div className="strategy-stack">
                                                        <strong>{getFavoriteStrategyName(fav)}</strong>
                                                        {strategyDetail ? <span>{strategyDetail}</span> : null}
                                                        {strategyDescription ? <span className="strategy-description">{strategyDescription}</span> : null}
                                                        <span className={`fav-refresh-status ${refreshStatus.className}`} title={refreshStatus.title}>
                                                            {refreshStatus.label}
                                                        </span>
                                                    </div>
                                                </td>
                                                <td className="direction-col">
                                                    <span className={`fav-direction ${direction === 'short' ? 'short' : 'long'}`}>
                                                        {direction === 'short' ? 'Short' : 'Long'}
                                                    </span>
                                                </td>
                                                <td><span className="tf-pill">{fav.timeframe}</span></td>
                                                <td className="muted-cell period-col">{formatPeriod(fav)}</td>
                                                <td className="metric-cell risk-col">{formatPct(stopLoss)}</td>
                                                <td className="metric-cell accent">{formatNum(m.sharpe_ratio)}</td>
                                                <td className="metric-cell">{getTradesCount(fav)}</td>
                                                <td className="metric-cell win-col">{formatPct(m.win_rate)}</td>
                                                <td className={`metric-cell strong ${totalReturn.positive ? 'positive' : 'negative'}`}>{totalReturn.text}</td>
                                                <td className="metric-cell negative risk-col">{formatPct(m.max_drawdown)}</td>
                                                <td className="metric-cell advanced-col">{formatNum(m.profit_factor)}</td>
                                                <td className="metric-cell advanced-col">{formatNum(m.sqn ?? m.sortino_ratio ?? m.sortino)}</td>
                                                <td className="metric-cell negative advanced-col">{formatPct(m.max_loss)}</td>
                                                <td className="metric-cell advanced-col">{formatNum(m.avg_atr)}</td>
                                                <td>
                                                    <div className="fav-row-actions">
                                                        <button type="button" onClick={() => handleViewAnalysis(fav)} disabled={loadingAnalysisId === fav.id} title="Ver análise completa" aria-label="Ver análise completa">
                                                            {loadingAnalysisId === fav.id ? <span className="fav-spinner" /> : <BarChart3 className="h-4 w-4" />}
                                                        </button>
                                                        {isAdmin ? (
                                                            <>
                                                                <button type="button" onClick={() => handleDelete(fav.id)} title="Delete"><Trash2 className="h-4 w-4" /></button>
                                                            </>
                                                        ) : null}
                                                    </div>
                                                </td>
                                            </tr>
                                        );
                                    })
                                )}
                                {!isLoading && filteredFavorites.length > 0 && hasMore && (
                                    <tr>
                                        <td colSpan={tableColumnCount} className="fav-empty-cell">
                                            <div ref={sentinelRef} />
                                            Carregando mais...
                                        </td>
                                    </tr>
                                )}
                            </tbody>
                        </table>
                    </div>

                    <div className="fav-footer">
                        <span>
                            {hasMore
                                ? `Mostrando ${visibleFavorites.length} de ${filteredFavorites.length}`
                                : `${filteredFavorites.length} estratégias carregadas`}
                        </span>
                        {isAdmin && selectedIds.length > 0 ? (
                            <button
                                type="button"
                                onClick={() => setIsCompareOpen(true)}
                                disabled={selectedIds.length < 2}
                                className="fav-primary-action"
                            >
                                Comparar {selectedIds.length}
                            </button>
                        ) : null}
                    </div>
                </main>

                {/* Compare Modal */}
                {
                    isCompareOpen && (
                        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6 bg-[rgba(4,10,18,0.82)] backdrop-blur-sm">
                            <div className="page-card w-full max-w-6xl max-h-[90vh] flex flex-col shadow-2xl relative overflow-hidden">
                                <div className="flex items-center justify-between px-5 py-4 border-b border-zinc-200 bg-zinc-50/5">
                                    <h2 className="text-lg sm:text-xl font-bold tracking-wide text-zinc-900 flex items-center gap-2">
                                        <Activity className="w-5 h-5 text-primary-500" />
                                        Strategy Comparison
                                    </h2>
                                    <button
                                        onClick={() => setIsCompareOpen(false)}
                                        className="text-zinc-500 hover:text-red-400 text-xs font-semibold uppercase tracking-[0.2em]"
                                    >
                                        Close
                                    </button>
                                </div>

                                <div className="flex-1 overflow-auto p-0">
                                    <table className="w-full text-left border-collapse text-sm">
                                        <thead>
                                            <tr>
                                                <th className="p-4 bg-zinc-50 text-zinc-500 font-bold border-b border-zinc-200 sticky top-0 left-0 z-10 w-48 uppercase tracking-wider text-xs border-r border-zinc-200">
                                                    Metric
                                                </th>
                                                {selectedStrategies.map(s => (
                                                    <th key={s.id} className="p-4 bg-zinc-50 text-zinc-900 border-b border-zinc-200 sticky top-0 min-w-[200px] border-r border-zinc-200">
                                                        <div className="text-primary-500 text-xs font-bold uppercase mb-1">Strat ID: #{s.id}</div>
                                                        <div className="font-bold truncate">{s.name}</div>
                                                        <div className="text-[10px] text-zinc-500 font-normal mt-1 uppercase tracking-widest">{s.symbol} • {s.timeframe}</div>
                                                    </th>
                                                ))}
                                            </tr>
                                        </thead>
                                        <tbody className="divide-y divide-zinc-200">
                                            <tr className="bg-zinc-50/10">
                                                <td className="p-4 font-bold text-zinc-400 border-r border-zinc-200 text-xs uppercase">Total Return</td>
                                                {selectedStrategies.map(s => {
                                                    const val = s.metrics.total_return_pct ?? s.metrics.total_return ?? 0;
                                                    return (
                                                        <td key={s.id} className={`p-4 font-bold text-lg border-r border-zinc-200 ${val >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                                                            {formatPct(val)}
                                                        </td>
                                                    );
                                                })}
                                            </tr>
                                            <tr>
                                                <td className="p-4 text-zinc-500 border-r border-zinc-200 text-xs uppercase">Sharpe Ratio</td>
                                                {selectedStrategies.map(s => (
                                                    <td key={s.id} className="p-4 text-zinc-900 font-mono border-r border-zinc-200">{formatNum(s.metrics.sharpe_ratio)}</td>
                                                ))}
                                            </tr>
                                            <tr>
                                                <td className="p-4 text-zinc-500 border-r border-zinc-200 text-xs uppercase">Win Rate</td>
                                                {selectedStrategies.map(s => (
                                                    <td key={s.id} className="p-4 text-zinc-900 font-mono border-r border-zinc-200">{formatPct(s.metrics.win_rate)}</td>
                                                ))}
                                            </tr>
                                            <tr>
                                                <td className="p-4 text-zinc-500 border-r border-zinc-200 text-xs uppercase">Max Drawdown</td>
                                                {selectedStrategies.map(s => (
                                                    <td key={s.id} className="p-4 text-red-500 font-mono border-r border-zinc-200">{formatPct(s.metrics.max_drawdown)}</td>
                                                ))}
                                            </tr>
                                            <tr>
                                                <td className="p-4 text-zinc-500 border-r border-zinc-200 text-xs uppercase">Profit Factor</td>
                                                {selectedStrategies.map(s => (
                                                    <td key={s.id} className="p-4 text-zinc-900 font-mono border-r border-zinc-200">{formatNum(s.metrics.profit_factor)}</td>
                                                ))}
                                            </tr>
                                            <tr>
                                                <td className="p-4 text-zinc-500 border-r border-zinc-200 text-xs uppercase">Sortino Ratio</td>
                                                {selectedStrategies.map(s => (
                                                    <td key={s.id} className="p-4 text-zinc-900 font-mono border-r border-zinc-200">{formatNum(s.metrics.sortino_ratio ?? s.metrics.sortino)}</td>
                                                ))}
                                            </tr>
                                            <tr>
                                                <td className="p-4 text-zinc-500 border-r border-zinc-200 text-xs uppercase">Max Loss</td>
                                                {selectedStrategies.map(s => (
                                                    <td key={s.id} className="p-4 text-red-500 font-mono border-r border-zinc-200">{formatPct(s.metrics.max_loss)}</td>
                                                ))}
                                            </tr>
                                            <tr>
                                                <td className="p-4 text-zinc-500 border-r border-zinc-200 text-xs uppercase">Max Cons. Losses</td>
                                                {selectedStrategies.map(s => (
                                                    <td key={s.id} className="p-4 text-zinc-900 font-mono border-r border-zinc-200">{s.metrics.max_consecutive_losses ?? 0}</td>
                                                ))}
                                            </tr>
                                            <tr>
                                                <td className="p-4 text-zinc-500 border-r border-zinc-200 text-xs uppercase">Avg ATR</td>
                                                {selectedStrategies.map(s => (
                                                    <td key={s.id} className="p-4 text-zinc-400 font-mono border-r border-zinc-200">{formatNum(s.metrics.avg_atr)}</td>
                                                ))}
                                            </tr>
                                            <tr>
                                                <td className="p-4 text-zinc-500 border-r border-zinc-200 text-xs uppercase">Win Rate Bull</td>
                                                {selectedStrategies.map(s => (
                                                    <td key={s.id} className="p-4 text-green-600 font-mono border-r border-zinc-200">{formatPct(s.metrics.win_rate_bull)}</td>
                                                ))}
                                            </tr>
                                            <tr>
                                                <td className="p-4 text-zinc-500 border-r border-zinc-200 text-xs uppercase">Win Rate Bear</td>
                                                {selectedStrategies.map(s => (
                                                    <td key={s.id} className="p-4 text-red-600 font-mono border-r border-zinc-200">{formatPct(s.metrics.win_rate_bear)}</td>
                                                ))}
                                            </tr>
                                            <tr>
                                                <td className="p-4 text-zinc-500 border-r border-zinc-200 text-xs uppercase">Avg ADX</td>
                                                {selectedStrategies.map(s => (
                                                    <td key={s.id} className="p-4 text-zinc-400 font-mono border-r border-zinc-200">{formatNum(s.metrics.avg_adx)}</td>
                                                ))}
                                            </tr>
                                            <tr>
                                                <td className="p-4 text-zinc-500 border-r border-zinc-200 text-xs uppercase">Total Trades</td>
                                                {selectedStrategies.map(s => (
                                                    <td key={s.id} className="p-4 text-zinc-400 font-mono border-r border-zinc-200">{s.metrics.total_trades || s.metrics.trades || 0}</td>
                                                ))}
                                            </tr>
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                        </div>
                    )}
            </div>
        </div>
    );
};

export default FavoritesDashboard;
