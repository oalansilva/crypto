import React, { useEffect, useRef, useState } from 'react';
import { keepPreviousData, useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import { Trash2, Search, List, Activity, BarChart3, Bell, Star, RefreshCw, X } from 'lucide-react';
import { useInfiniteScroll } from '@/hooks/useInfiniteScroll';
import { API_BASE_URL } from '../lib/apiBase';
import { authFetch } from '@/lib/authFetch';
import { AuthSessionExpiredError, fetchAuthJson } from '@/lib/authJson';
import { useAuth } from '@/stores/authStore';
import { ScreenHelpPanel } from '@/components/onboarding/ScreenHelpPanel';
import {
    hasAvailableIndicatorSeries,
    mergeStrategyTransparencySeries,
    normalizeStrategyTransparency,
    type StrategyTransparency,
} from '@/lib/strategyTransparency';
import type { TradeExplanation } from '@/types/tradeExplanation';
import type { MonitorSyncStatus } from '@/lib/signalHistory';
import { OosMetricsTable, OosVerdictBadge } from '@/components/results/OosComparison';
import {
    favoriteGridMetrics,
    formatPtBrDate,
    isDiscoveryOrigin,
} from '@/lib/discoveryFavoriteMetrics';
import { formatCompoundReturn } from '@/lib/compoundReturn';
import {
    OUTSIDE_PORTFOLIO_WARNING,
    alertarLabel,
    atrWithCurrency,
    chipLabel,
    classCounts,
    classFilterOptions,
    favoriteClass,
    favoriteLoteId,
    favoriteRowData,
    formatFavoriteRefreshStatus,
    isEquityClass,
    loteBannerText,
    FILTER_EMPTY_LOTE,
    type FavoriteConfiguration,
    type ClassFilterValue,
    type RowData,
} from '@/lib/favoriteClass';
import '../styles/lote.css';
import '../styles/favoriteAlerts.css';

import { favoriteRefTag, type BenchmarkComparison as BenchmarkComparisonPayload, type ComparisonSummary } from '@/lib/benchmarkComparison';
import '../components/results/BenchmarkComparison.css';

type MonitorSignalSyncResult = {
    trades: any[] | null;
    signal_history: MonitorSignalHistoryItem[];
    status: MonitorSyncStatus;
    strategy_transparency?: StrategyTransparency | Record<string, unknown> | null;
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
    /** Identidade do ativo (card #1120): classe, moeda e nome; cripto, ação e ETF na mesma lista. */
    asset?: { symbol: string; asset_id?: string | null; asset_class?: 'crypto' | 'stock' | 'etf' | null; name?: string | null; currency?: string | null } | null;
    /** Card #1122: fonte, sessão e ajuste (e rótulos). */
    configuration?: FavoriteConfiguration | null;
    /** Card #1122: linha do catálogo do Cripto Farol (vitrine), sem "Alertar". */
    is_curated_fallback?: boolean;
    /** Card #1123: comparação com referência gravada (resumo; a análise lê a inteira). */
    benchmark_comparison_id?: string | null;
    benchmark_comparison?: ComparisonSummary | null;
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
    strategy_transparency?: StrategyTransparency | Record<string, unknown> | null;
}

interface RevalidationReport {
    favorite_id: number;
    symbol: string;
    timeframe: string;
    strategy_name: string;
    verdict: string;
    window: { start: string; end: string };
    revalidation: {
        best_metrics: Record<string, any>;
        oos_metrics?: Record<string, any> | null;
        oos_verdict?: Record<string, any> | null;
    };
}

const CURRENT_CHART_CANDLE_LIMIT = 300;
const FAVORITE_ANALYSIS_OPTIONAL_SYNC_TIMEOUT_MS = 2500;
// Monitor signal history is required for Favoritos parity. Cold recompute of
// /opportunities can take several seconds when the short-lived cache misses.
const FAVORITE_MONITOR_SIGNAL_SYNC_TIMEOUT_MS = 15_000;

const getSavedAnalysisCandles = (fav: FavoriteStrategy): any[] => {
    const candles = fav.metrics?.analysis_candles;
    return Array.isArray(candles) ? candles : [];
};

const getFavoriteDirection = (fav: FavoriteStrategy): string => (
    String(
        fav.parameters?.direction
        || normalizeStrategyTransparency(fav.strategy_transparency)?.direction
        || 'long',
    ).toLowerCase() === 'short' ? 'short' : 'long'
);

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
    const [searchParams, setSearchParams] = useSearchParams();
    const queryClient = useQueryClient();
    const { user } = useAuth();
    const isAdmin = user?.isAdmin === true;
    const [searchTerm, setSearchTerm] = useState('');
    const [selectedIds, setSelectedIds] = useState<number[]>([]);
    const [isCompareOpen, setIsCompareOpen] = useState(false);
    const [revalidationReport, setRevalidationReport] = useState<RevalidationReport | null>(null);
    const [revalidationError, setRevalidationError] = useState<string | null>(null);
    const revalidationCloseRef = useRef<HTMLButtonElement | null>(null);
    const revalidationTriggerRef = useRef<HTMLElement | null>(null);
    const [tierFilter, setTierFilter] = useState<'all' | '1' | '2' | '3' | 'none'>('all');
    const [classFilter, setClassFilter] = useState<ClassFilterValue>('all');
    // Faixa do lote (card #1120): `/favorites?lote=<id8>` mostra só o que o lote gravou, de todas as classes.
    const loteFilter = (searchParams.get('lote') || '').trim().toLowerCase() || null;
    const classSelectRef = useRef<HTMLSelectElement | null>(null);

    const [loadingAnalysisId, setLoadingAnalysisId] = useState<number | null>(null);

    // Fetch favorites
    const {
        data: favorites,
        isLoading,
        isError,
        error: favoritesError,
        refetch,
        isFetching,
    } = useQuery({
        queryKey: ['favorites', user?.id ?? 'anonymous'],
        queryFn: async () => {
            const data = await fetchAuthJson<FavoriteStrategy[]>('/favorites/');
            if (!Array.isArray(data)) {
                throw new Error('Invalid favorites payload');
            }
            // Avoid logging large payloads in production/dev UI: can freeze browser on slower devices.
            console.log(`📥 Loaded favorites: ${data.length} items`);
            return data;
        },
        placeholderData: keepPreviousData,
        retry: false,
    });

    // Card #1122: carteira manual do Monitor, para o aviso "Fora da carteira: sem alerta".
    const { data: monitorPreferences } = useQuery({
        queryKey: ['monitor-preferences', user?.id ?? 'anonymous'],
        queryFn: async () => {
            const response = await authFetch(`${API_BASE_URL}/monitor/preferences`);
            if (!response.ok) return {} as Record<string, { in_portfolio?: boolean }>;
            const payload = await response.json();
            return (payload && typeof payload === 'object' ? payload : {}) as Record<string, { in_portfolio?: boolean }>;
        },
        retry: false,
    });
    const isOutsidePortfolio = (fav: FavoriteStrategy): boolean => (
        fav.notify_telegram === true
        && !fav.is_curated_fallback
        && isEquityClass(favoriteClass(fav))
        && monitorPreferences !== undefined
        && monitorPreferences?.[fav.symbol]?.in_portfolio !== true
    );

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

    const revalidateMutation = useMutation({
        mutationFn: async (id: number) => {
            const res = await authFetch(`${API_BASE_URL}/favorites/${id}/revalidate`, { method: 'POST' });
            if (!res.ok) {
                const error = await res.json().catch(() => ({}));
                throw new Error(error.detail || 'Falha ao revalidar estratégia');
            }
            return res.json() as Promise<RevalidationReport>;
        },
        onSuccess: (report) => {
            setRevalidationError(null);
            setRevalidationReport(report);
            queryClient.invalidateQueries({ queryKey: ['favorites', user?.id ?? 'anonymous'] });
        },
        onError: (error) => {
            setRevalidationError(error instanceof Error ? error.message : 'Falha ao revalidar estratégia');
        },
    });

    const handleRevalidate = (fav: FavoriteStrategy, trigger: HTMLElement) => {
        revalidationTriggerRef.current = trigger;
        setRevalidationError(null);
        revalidateMutation.mutate(fav.id);
    };

    const closeRevalidationReport = () => {
        setRevalidationReport(null);
        window.setTimeout(() => revalidationTriggerRef.current?.focus(), 0);
    };

    useEffect(() => {
        if (!revalidationReport) return;
        revalidationCloseRef.current?.focus();
        const handleKeyDown = (event: KeyboardEvent) => {
            if (event.key === 'Escape') {
                closeRevalidationReport();
                return;
            }
            if (event.key === 'Tab') {
                event.preventDefault();
                revalidationCloseRef.current?.focus();
            }
        };
        window.addEventListener('keydown', handleKeyDown);
        return () => window.removeEventListener('keydown', handleKeyDown);
    }, [revalidationReport]);

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

    /** Precisão, convenções e período efetivo à vista; "Limitações e origem" atrás de um `<details>` fechado. */
    const renderRowData = (row: RowData, fav?: FavoriteStrategy) => (
        <div className="lote-rowdata">
            <span className="lote-prec" data-tone={row.precision.tone} data-testid="fav-precision">
                <svg aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    {row.precision.tone === 'warn' ? (
                        <>
                            <path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3" />
                            <path d="M12 9v4" />
                            <path d="M12 17h.01" />
                        </>
                    ) : (
                        <>
                            <circle cx="12" cy="12" r="10" />
                            <path d="M12 16v-4" />
                            <path d="M12 8h.01" />
                        </>
                    )}
                </svg>
                <span>{row.precision.text}</span>
            </span>
            <span className="lote-conv" data-testid="fav-conventions">{row.conventions}</span>
            <span className="lote-conv" data-testid="fav-effective">{row.effective}</span>
            {/* Card #1123: só fora do padrão (próprio ativo), para não pesar a coluna Estratégia. */}
            {fav && favoriteRefTag(fav.benchmark_comparison) ? (
                <span className="lote-conv b23-favref" data-testid="fav-reference">{favoriteRefTag(fav.benchmark_comparison)}</span>
            ) : null}
            {row.details ? (
                <details className="lote-more-info" data-testid="fav-more-info">
                    <summary>{row.details.summary}</summary>
                    {row.details.conventionsFull ? <span className="lote-conv" data-testid="fav-conventions-full">{row.details.conventionsFull}</span> : null}
                    {row.details.limitations ? <span className="lote-lim">{row.details.limitations}</span> : null}
                    {row.details.lote ? <span className="lote-lote-tag">{row.details.lote}</span> : null}
                </details>
            ) : null}
        </div>
    );

    const renderStarTierControl = (fav: FavoriteStrategy, compact = false) => {
        const selectedStars = getStarCount(fav.tier);
        const isSaving = updateTierMutation.isPending;
        // Card #1122: estrelas de ação e ETF funcionam como na cripto.
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

    /**
     * "Alertar" do dono (card #1122, decisão 3): coluna a partir de 1280 px, sino na célula Ações de
     * 1024 a 1279 px e "Alertar: on/off" com 44 px no celular. A vitrine do catálogo não tem controle.
     */
    const renderTelegramControl = (fav: FavoriteStrategy, variant: 'column' | 'mobile' | 'actions' = 'column') => {
        if (fav.is_curated_fallback) {
            return variant === 'actions' ? null : (
                <span className="alert-catalog-none" data-testid={`alertar-catalog-${fav.id}`}>Catálogo · não alerta</span>
            );
        }
        const active = fav.notify_telegram === true;
        const isSaving = updateTelegramMutation.isPending;
        const label = alertarLabel(active);
        if (variant === 'actions') {
            return (
                <button
                    type="button"
                    className="alertar-in-actions"
                    aria-pressed={active}
                    aria-label={label}
                    title={label}
                    disabled={isSaving}
                    data-testid={`alertar-actions-${fav.id}`}
                    onClick={(event) => {
                        event.stopPropagation();
                        handleToggleTelegram(fav);
                    }}
                >
                    <Bell className="h-4 w-4" fill={active ? 'currentColor' : 'none'} aria-hidden="true" />
                </button>
            );
        }
        const compact = variant === 'mobile';
        return (
            <button
                type="button"
                disabled={isSaving}
                aria-pressed={active}
                aria-label={label}
                title={label}
                data-testid={`alertar-${compact ? 'mobile' : 'column'}-${fav.id}`}
                onClick={(event) => {
                    event.stopPropagation();
                    handleToggleTelegram(fav);
                }}
                className={[
                    'telegram-toggle inline-flex items-center justify-center gap-1 rounded-md border transition-colors',
                    compact ? 'alertar-mobile h-11 min-w-[7.5rem] px-2 text-xs font-semibold' : 'h-8 min-w-[4.5rem] px-2 text-xs',
                    active
                        ? 'border-emerald-400 bg-emerald-400/15 text-emerald-600'
                        : 'border-zinc-200 bg-zinc-50 text-zinc-400 hover:text-emerald-600',
                    isSaving ? 'opacity-60 cursor-wait' : '',
                ].join(' ')}
            >
                <Bell className={compact ? 'h-4 w-4' : 'h-3.5 w-3.5'} fill={active ? 'currentColor' : 'none'} aria-hidden="true" />
                {compact ? (active ? 'Alertar: on' : 'Alertar: off') : active ? 'On' : 'Off'}
            </button>
        );
    };

    const renderOutsidePortfolioWarning = (fav: FavoriteStrategy) => (
        isOutsidePortfolio(fav) ? (
            <span className="alert-portfolio-warning" data-testid={`alertar-outside-portfolio-${fav.id}`}>
                {OUTSIDE_PORTFOLIO_WARNING}{' '}
                <Link to="/monitor">Marque o ativo como "No portfólio" no Monitor</Link>.
            </span>
        ) : null
    );

    const getFavoriteStrategyLabel = (fav: FavoriteStrategy): string => {
        const manifestDisplayName = fav.strategy_transparency?.display_name;
        return fav.strategy_display_name || (typeof manifestDisplayName === 'string' ? manifestDisplayName : '') || (
            fav.is_strategy_protected ? 'Detalhes da estratégia indisponíveis' : fav.strategy_name.replace(/_/g, ' ')
        );
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
        const title = getFavoriteStrategyLabel(fav).trim()
        const alias = String(fav.name || '').trim()
        if (!alias || normalizeStrategyComparison(alias) === normalizeStrategyComparison(title)) return null
        if (fav.is_strategy_protected && alias.toLowerCase() === 'detalhes da estratégia indisponíveis') return null
        return `Apelido do favorito: ${alias}`
    };

    const getFavoriteCatalogTitle = (fav: FavoriteStrategy): string => getFavoriteStrategyLabel(fav).trim();

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
        const metrics = favoriteGridMetrics(fav.metrics);
        const summaryTradeCount = Number(
            metrics.total_trades ?? (typeof metrics.trades === 'number' ? metrics.trades : 0)
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
                return { trades: null, signal_history: [], status: 'missing', strategy_transparency: null };
            }

            const history = Array.isArray(opportunity.signal_history) ? opportunity.signal_history : [];
            if (history.length === 0) {
                return {
                    trades: null,
                    signal_history: [],
                    status: 'empty',
                    strategy_transparency: opportunity.strategy_transparency ?? null,
                };
            }

            const direction = getFavoriteDirection(fav);
            return {
                trades: buildTradesFromSignalHistory(
                    history,
                    direction,
                    opportunity?.trade_explanation,
                ),
                signal_history: history,
                status: 'ok',
                strategy_transparency: opportunity.strategy_transparency ?? null,
            };
        } catch (error) {
            console.warn(`Falling back to saved favorite trades for ${fav.symbol} ${fav.timeframe}`, error);
            return { trades: null, signal_history: [], status: 'error', strategy_transparency: null };
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
        const sourceMetrics = favoriteGridMetrics(recovered.metrics || fav.metrics || {});
        const trades = Array.isArray(recovered.trades) ? recovered.trades : [];
        const discoveryOrigin = isDiscoveryOrigin(sourceMetrics) || isDiscoveryOrigin(fav.metrics);
        const totalReturn = Number(
            sourceMetrics.total_return ?? (
                sourceMetrics.total_return_pct != null ? Number(sourceMetrics.total_return_pct) / 100 : 0
            )
        );
        const totalTrades = Number(
            sourceMetrics.total_trades ?? (discoveryOrigin ? sourceMetrics.total_trades : trades.length)
        );
        const metrics = {
            ...sourceMetrics,
            total_trades: Number.isFinite(totalTrades) ? totalTrades : (discoveryOrigin ? sourceMetrics.total_trades : trades.length),
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
            start_date: fav.start_date ?? null,
            end_date: fav.end_date ?? null,
            origin_type: sourceMetrics.origin_type || fav.metrics?.origin_type || null,
            promotion_metrics: sourceMetrics.metrics_snapshot || null,
            parameters: isFavoriteProtected(fav) && !isAdmin ? {} : fav.parameters || {},
            metrics,
            trades,
            indicator_data: isFavoriteProtected(fav) && !isAdmin ? {} : recovered.indicatorData || {},
            candles: recovered.candles || [],
            execution_mode: recovered.executionMode,
            direction: getFavoriteDirection(fav),
            is_strategy_protected: isFavoriteProtected(fav) && !isAdmin,
            strategy_transparency: recovered.strategyTransparency ?? fav.strategy_transparency ?? null,
            strategy_description: getFavoriteStrategyDescription(fav),
            // Card #1123: a troca grava no favorito; identidade e janela para o seletor.
            favorite_id: fav.is_curated_fallback ? null : fav.id,
            favorite_name: fav.name,
            asset: fav.asset ?? null,
            execution: (fav.metrics?.analysis_execution as any) ?? null,
            benchmark_comparison: null as BenchmarkComparisonPayload | null,
        };
    };

    const loadFavoriteComparison = async (fav: FavoriteStrategy): Promise<BenchmarkComparisonPayload | null> => {
        const id = fav.benchmark_comparison?.id || fav.benchmark_comparison_id;
        if (!id) return null;
        try {
            const response = await authFetch(`${API_BASE_URL}/benchmark-comparisons/${encodeURIComponent(id)}`);
            if (!response.ok) return null;
            return (await response.json()) as BenchmarkComparisonPayload;
        } catch {
            return null;
        }
    };

    const handleViewAnalysis = async (fav: FavoriteStrategy) => {
        setLoadingAnalysisId(fav.id);
        try {
            // List payloads strip trades/candles; wait for /favorites/{id}/trades instead of timing out to empty cache.
            const recovered = await loadTradesForAnalysis(fav);
            const monitorSyncFallback: MonitorSignalSyncResult = {
                trades: null,
                signal_history: [],
                status: 'timeout',
                strategy_transparency: null,
            };
            const [currentCandles, monitorSync, savedComparison] = await Promise.all([
                resolveWithTimeout(
                    loadCurrentChartCandles(fav),
                    recovered.candles || [],
                    FAVORITE_ANALYSIS_OPTIONAL_SYNC_TIMEOUT_MS,
                    () => console.warn(`Using saved favorite candles for ${fav.symbol} ${fav.timeframe}; current candle load timed out.`),
                ),
                resolveWithTimeout(
                    loadMonitorSyncedTrades(fav),
                    monitorSyncFallback,
                    FAVORITE_MONITOR_SIGNAL_SYNC_TIMEOUT_MS,
                    () => console.warn(`Opening favorite analysis without monitor trade sync for ${fav.symbol} ${fav.timeframe}; monitor sync timed out.`),
                ),
                loadFavoriteComparison(fav),
            ]);
            const analysisResult = buildFavoriteAnalysisResult(fav, recovered);
            analysisResult.benchmark_comparison = savedComparison;
            // Extend cached MA series with live Monitor points so overlays reach the newest candles.
            analysisResult.strategy_transparency = mergeStrategyTransparencySeries(
                analysisResult.strategy_transparency,
                monitorSync.strategy_transparency,
            ) ?? analysisResult.strategy_transparency ?? null;
            const chartCandles = mergeAnalysisCandles(currentCandles, recovered.candles || []);
            analysisResult.candles = chartCandles || [];
            if (monitorSync.trades && monitorSync.trades.length > 0) {
                const mergedTrades = mergeFavoriteAndMonitorTrades(analysisResult.trades, monitorSync.trades);
                analysisResult.trades = mergedTrades;
                if (!isDiscoveryOrigin(analysisResult.metrics)) {
                    analysisResult.metrics = {
                        ...analysisResult.metrics,
                        total_trades: mergedTrades.filter((trade: any) => trade.exit_time && trade.exit_price).length,
                    };
                }
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

    /** Número de trades: combo-saved usa a lista; Descoberta usa o snapshot da promoção. */
    const getTradesCount = (fav: FavoriteStrategy): number => {
        const m = favoriteGridMetrics(fav.metrics);
        if (isDiscoveryOrigin(fav.metrics)) {
            const n = m.total_trades ?? (typeof m.trades === 'number' ? m.trades : null);
            return n != null && Number.isFinite(Number(n)) ? Math.max(0, Number(n)) : 0;
        }
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
        const metrics = favoriteGridMetrics(fav.metrics);
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
                return getSortableNumber(favoriteGridMetrics(fav.metrics).sharpe_ratio);
            case 'trades':
                return trades;
            case 'returnPerTrade':
            default:
                return returnPct === -Infinity ? -Infinity : returnPct / trades;
        }
    };

    // Get unique symbols for filter (lista única: cripto, ação e ETF)
    const uniqueSymbols = React.useMemo(() => {
        if (!favorites) return [];
        return Array.from(new Set(favorites.map(f => f.symbol))).sort();
    }, [favorites]);

    // Get unique strategy labels for filter
    const uniqueIndicators = React.useMemo(() => {
        if (!favorites) return [];
        return Array.from(new Set(favorites.map(getFavoriteStrategyLabel))).sort();
    }, [favorites]);

    const uniqueTimeframes = React.useMemo(() => {
        if (!favorites) return [];
        return Array.from(new Set(favorites.map(f => f.timeframe))).sort();
    }, [favorites]);

    const classTotals = React.useMemo(() => classCounts(favorites || []), [favorites]);

    const filteredFavorites = (favorites?.filter(fav => {
        const matchesSearch = favoriteMatchesSearch(fav, searchTerm);

        const matchesSymbol = selectedSymbol === 'ALL' || fav.symbol === selectedSymbol;
        const matchesIndicator = selectedIndicator === 'ALL' || getFavoriteStrategyLabel(fav) === selectedIndicator;
        const matchesTimeframe = selectedTimeframe === 'ALL' || fav.timeframe === selectedTimeframe;
        const favClass = favoriteClass(fav);
        // Card #1122: o filtro por estrelas vale para todas as classes.
        const matchesTier = tierFilter === 'all' ||
            (tierFilter === 'none' && fav.tier === null) ||
            (tierFilter !== 'none' && fav.tier === parseInt(tierFilter));
        const matchesClass = classFilter === 'all' || favClass === classFilter;
        const matchesLote = !loteFilter || favoriteLoteId(fav) === loteFilter;

        const favDirection = getFavoriteDirection(fav);
        const matchesDirection = directionFilter === 'all' || favDirection === directionFilter;

        return matchesClass && matchesLote && matchesSearch && matchesSymbol && matchesIndicator && matchesTimeframe && matchesTier && matchesDirection;
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

    // Card #1123: a planilha sai do servidor com as colunas de hoje e as 22 de contexto (sem SheetJS).
    const [exportStatus, setExportStatus] = useState('');
    const handleExportExcel = async () => {
        if (!favorites || favorites.length === 0 || filteredFavorites.length === 0) {
            setExportStatus('Nenhum favorito na lista filtrada para exportar.');
            return;
        }
        setExportStatus('Gerando a planilha…');
        try {
            const ids = filteredFavorites.map((fav) => fav.id).join(',');
            const response = await authFetch(`${API_BASE_URL}/favorites/export?ids=${encodeURIComponent(ids)}`);
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            const blob = await response.blob();
            const disposition = response.headers.get('Content-Disposition') || '';
            const match = disposition.match(/filename="?([^";]+)"?/);
            const filename = match ? match[1] : `Crypto_Backtest_Favorites_${new Date().toISOString().slice(0, 10)}.xlsx`;
            const url = window.URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.href = url;
            link.download = filename;
            document.body.appendChild(link);
            link.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(link);
            setExportStatus(
                `Planilha baixada: ${filename} · ${filteredFavorites.length} ${filteredFavorites.length === 1 ? 'favorito' : 'favoritos'} da lista filtrada · colunas de hoje + contexto · abas Favoritos e Legenda.`,
            );
        } catch (error) {
            console.error('Erro ao exportar favoritos:', error);
            setExportStatus('Não foi possível exportar a planilha. Tente de novo.');
        }
    };

    // Formatters
    const formatPct = (val?: number) => {
        if (val === undefined || val === null) return '-';
        return val > 1 || val < -1 ? `${val.toFixed(2)}%` : `${(val * 100).toFixed(2)}%`;
    };

    const formatNum = (val?: number, decimals = 2) => {
        if (val === undefined || val === null) return '-';
        return val.toFixed(decimals);
    };

    const formatPeriod = (fav: FavoriteStrategy): string => {
        const s = fav.start_date;
        const e = fav.end_date;
        if (!s && !e) return 'Todo';
        const startLabel = formatPtBrDate(s);
        const endLabel = formatPtBrDate(e);
        if (startLabel && endLabel) return `${startLabel} → ${endLabel}`;
        if (startLabel) return `≥ ${startLabel}`;
        if (endLabel) return `≤ ${endLabel}`;
        return 'Todo';
    };

    // Card #1122: ação/ETF mostra o último pregão; série curta, "Aguardando dados: N de M candles".
    const formatRefreshStatus = (fav: FavoriteStrategy) => formatFavoriteRefreshStatus(fav);

    const formatRevalidationStatus = (fav: FavoriteStrategy): { label: string; className: string; title?: string } | null => {
        const metrics = fav.metrics || {};
        const verdict = String(metrics.revalidation_verdict || '').toUpperCase();
        const revalidatedAt = metrics.revalidation_at;
        const formattedDate = revalidatedAt
            ? new Date(revalidatedAt).toLocaleString('pt-BR', {
                day: '2-digit',
                month: '2-digit',
                hour: '2-digit',
                minute: '2-digit',
            })
            : null;
        if (!verdict) return null;
        if (verdict === 'GO') {
            return { label: formattedDate ? `Revalidado (GO): ${formattedDate}` : 'Revalidado (GO)', className: 'revalidated-go' };
        }
        if (verdict === 'ERROR') {
            return { label: 'Revalidação com erro', className: 'revalidated-error', title: 'Erro no holdout da revalidação' };
        }
        return {
            label: formattedDate ? `Degradado (${verdict}): ${formattedDate}` : `Degradado (${verdict})`,
            className: 'revalidated-no-go',
            title: 'Reprovado na revalidação walk-forward (janela recente). Decisão de remoção permanece manual.',
        };
    };

    // Card #1122: estrelas, resumo por nível e filtro por estrelas contam todas as classes.
    const ratedFavorites = React.useMemo(() => favorites || [], [favorites]);
    const showsCatalogFallback = ratedFavorites.some((fav) => fav.is_curated_fallback);
    const rowDataOf = (fav: FavoriteStrategy): RowData => favoriteRowData(fav);

    const favoritesUsingDefaultFilters = searchTerm.trim() === ''
        && tierFilter === 'all'
        && classFilter === 'all'
        && !loteFilter
        && selectedSymbol === 'ALL'
        && selectedIndicator === 'ALL'
        && selectedTimeframe === 'ALL'
        && directionFilter === 'all';

    const favoritesListFailed =
        isError
        && favorites === undefined
        && user != null
        && !(favoritesError instanceof AuthSessionExpiredError);

    useEffect(() => {
        if (favoritesError instanceof AuthSessionExpiredError) {
            navigate('/login', { replace: true, state: { returnTo: '/favorites' } });
        }
    }, [favoritesError, navigate]);
    const favoritesListLoading = isLoading || (isFetching && favorites === undefined);
    const favoritesCatalogEmpty = !favoritesListLoading
        && !favoritesListFailed
        && favorites !== undefined
        && favorites.length === 0
        && favoritesUsingDefaultFilters;
    const favoritesFilterEmpty = !favoritesListLoading
        && !favoritesListFailed
        && !favoritesCatalogEmpty
        && filteredFavorites.length === 0;

    const renderFavoritesLoadError = (compactCell = false) => (
        <div
            className={compactCell ? 'fav-error fav-error--cell' : 'fav-error'}
            role="alert"
            data-testid="favorites-load-error"
        >
            <p>Não foi possível carregar as estratégias favoritas.</p>
            <span>Isto não significa que o catálogo está vazio. A sessão continua válida.</span>
            <button
                type="button"
                className="fav-retry"
                onClick={() => void refetch({ cancelRefetch: false })}
                disabled={isFetching}
            >
                Tentar de novo
            </button>
        </div>
    );

    const renderFavoritesFilterEmpty = () => (
        <div className="fav-empty" role="status" data-testid="favorites-filter-empty">
            {classFilter !== 'all' || loteFilter ? FILTER_EMPTY_LOTE : 'Não há resultado com estes filtros.'}
        </div>
    );

    const renderFavoritesCatalogEmpty = () => (
        <div className="fav-empty">Nenhuma estratégia favorita encontrada.</div>
    );

    const tierCounts = React.useMemo(() => {
        return ratedFavorites.reduce(
            (acc, fav) => {
                if (fav.tier === 1) acc.top += 1;
                else if (fav.tier === 2) acc.high += 1;
                else if (fav.tier === 3) acc.watch += 1;
                else acc.none += 1;
                return acc;
            },
            { top: 0, high: 0, watch: 0, none: 0 }
        );
    }, [ratedFavorites]);

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

    const formatSignedPct = (metrics?: Record<string, any>) => formatCompoundReturn(metrics, { empty: '-' });

    const tableColumnCount = isAdmin ? 19 : 18;

    const clearLoteFilter = () => {
        const next = new URLSearchParams(searchParams);
        next.delete('lote');
        setSearchParams(next, { replace: true });
        classSelectRef.current?.focus();
    };

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
                            <span data-testid="fav-count">{filteredFavorites.length} filtradas</span>
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

                    {showsCatalogFallback ? (
                        <div className="alert-catalog-banner" role="status" data-testid="favorites-catalog-banner">
                            <strong>Estas estratégias são o catálogo do Cripto Farol e não mandam alerta.</strong>{' '}
                            Os alertas do Telegram vêm só dos seus favoritos marcados "Alertar". Salve os seus no Combo, na Descoberta ou no lote e marque "Alertar" aqui.
                        </div>
                    ) : null}

                    <div className="tier-filter" aria-label="Filtro por tier">
                        {[
                            { value: 'all', label: `Todas ${(favorites || []).length}` },
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
                            <span>Classe</span>
                            <select
                                ref={classSelectRef}
                                value={classFilter}
                                data-testid="fav-class-filter"
                                onChange={(e) => setClassFilter(e.target.value as ClassFilterValue)}
                            >
                                {classFilterOptions(classTotals).map((option) => (
                                    <option key={option.value} value={option.value}>{option.label}</option>
                                ))}
                            </select>
                        </label>
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
                                <button type="button" onClick={() => void handleExportExcel()} className="fav-secondary-action" data-testid="export-favorites">
                                    <List className="h-4 w-4" />
                                    Exportar
                                </button>
                                <button type="button" onClick={() => navigate('/combo/select')} className="fav-primary-action">
                                    Nova estratégia
                                </button>
                            </div>
                        ) : null}
                        {isAdmin ? (
                            <p className="b23-export-status b23-fav-status" role="status" aria-live="polite" data-testid="favorites-export-status">
                                {exportStatus}
                            </p>
                        ) : null}
                    </div>
                </section>

                {loteFilter ? (
                    <div className="lote-lote" role="status" data-testid="fav-lote-filter">
                        <span>{loteBannerText(loteFilter, favorites || [])}</span>
                        <button type="button" onClick={clearLoteFilter}>Mostrar todos os favoritos</button>
                    </div>
                ) : null}

                <main
                    className="fav-main"
                    data-testid={(favorites || []).length > 0 ? 'favorites-renewal-ok' : undefined}
                >
                    <div className="fav-mobile-list">
                        {favoritesListLoading ? (
                            <div className="fav-empty">Carregando estratégias...</div>
                        ) : favoritesListFailed ? (
                            renderFavoritesLoadError()
                        ) : favoritesCatalogEmpty ? (
                            renderFavoritesCatalogEmpty()
                        ) : favoritesFilterEmpty ? (
                            renderFavoritesFilterEmpty()
                        ) : (
                            visibleFavorites.map((fav: FavoriteStrategy) => {
                                const m = favoriteGridMetrics(fav.metrics);
                                const tier = getTierDisplay(fav.tier);
                                const totalReturn = formatSignedPct(m);
                                const direction = getFavoriteDirection(fav);
                                const strategyDetail = getGridStrategyDetail(fav);
                                const strategyDescription = getFavoriteStrategyDescription(fav);
                                const refreshStatus = formatRefreshStatus(fav);
                                const revalidationStatus = formatRevalidationStatus(fav);
                                const origin = isDiscoveryOrigin(fav.metrics) ? 'discovery' : 'combo';
                                const row = rowDataOf(fav);
                                return (
                                    <article
                                        key={fav.id}
                                        className={`fav-mobile-card ${tier.className}`}
                                        data-testid={`favorite-${fav.id}-mobile`}
                                        data-origin={origin}
                                        data-favorite-id={fav.id}
                                        data-class={row.cls}
                                        data-lote={row.lote ?? ''}
                                    >
                                        <div className="fav-mobile-card-head">
                                            <div>
                                                <strong>{fav.symbol}</strong>
                                                <span className="lote-cardline">
                                                    <span className="lote-cls" data-class={row.cls}>{chipLabel(row.cls)}</span> · <span className="lote-cur">{row.currency}</span>
                                                </span>
                                                <span className="fav-strategy-name">{getFavoriteCatalogTitle(fav)}</span>
                                                {strategyDetail ? <span className="fav-strategy-meta">{strategyDetail}</span> : null}
                                                {strategyDescription ? <span className="fav-strategy-description">{strategyDescription}</span> : null}
                                                <span className={`fav-refresh-status ${refreshStatus.className}`} title={refreshStatus.title} data-testid="fav-refresh-status">
                                                    {refreshStatus.label}
                                                </span>
                                                {renderOutsidePortfolioWarning(fav)}
                                                {revalidationStatus ? (
                                                    <span className={`fav-refresh-status ${revalidationStatus.className}`} title={revalidationStatus.title}>
                                                        {revalidationStatus.label}
                                                    </span>
                                                ) : null}
                                                {renderRowData(row, fav)}
                                            </div>
                                            <span className={`fav-direction ${direction === 'short' ? 'short' : 'long'}`}>
                                                {direction === 'short' ? 'Short' : 'Long'}
                                            </span>
                                        </div>
                                        <div className="fav-mobile-stars">
                                            {renderStarTierControl(fav, true)}
                                            {renderTelegramControl(fav, 'mobile')}
                                        </div>
                                        <div className="fav-mobile-metrics">
                                            <span><b>TF</b>{fav.timeframe}</span>
                                            <span data-metric="sharpe"><b>Sharpe</b>{formatNum(m.sharpe_ratio)}</span>
                                            <span data-metric="trades"><b>Trades</b>{getTradesCount(fav)}</span>
                                            <span className={totalReturn.positive ? 'positive' : 'negative'} data-metric="return"><b>Return</b>{totalReturn.text}</span>
                                        </div>
                                        <div className="fav-mobile-actions">
                                            <button type="button" onClick={() => handleViewAnalysis(fav)} disabled={loadingAnalysisId === fav.id} title="Ver análise completa">
                                                {loadingAnalysisId === fav.id ? <span className="fav-spinner" /> : <BarChart3 className="h-4 w-4" />}
                                                Analisar
                                            </button>
                                            {isAdmin ? (
                                                <>
                                                    <button type="button" onClick={(event) => handleRevalidate(fav, event.currentTarget)} disabled={revalidateMutation.isPending} title="Revalidar na janela recente">
                                                        <RefreshCw className={`h-4 w-4 ${revalidateMutation.isPending ? 'animate-spin' : ''}`} />Revalidar
                                                    </button>
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
                                    <th className="telegram-col">Alertar</th>
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
                                {favoritesListLoading ? (
                                    <tr><td colSpan={tableColumnCount} className="fav-empty-cell">Carregando estratégias...</td></tr>
                                ) : favoritesListFailed ? (
                                    <tr>
                                        <td colSpan={tableColumnCount} className="fav-empty-cell">
                                            {renderFavoritesLoadError(true)}
                                        </td>
                                    </tr>
                                ) : favoritesCatalogEmpty ? (
                                    <tr><td colSpan={tableColumnCount} className="fav-empty-cell">Nenhuma estratégia favorita encontrada.</td></tr>
                                ) : favoritesFilterEmpty ? (
                                    <tr>
                                        <td colSpan={tableColumnCount} className="fav-empty-cell">
                                            {renderFavoritesFilterEmpty()}
                                        </td>
                                    </tr>
                                ) : (
                                    visibleFavorites.map((fav: FavoriteStrategy) => {
                                        const isSelected = selectedIds.includes(fav.id);
                                        const m = favoriteGridMetrics(fav.metrics);
                                        const tier = getTierDisplay(fav.tier);
                                        const totalReturn = formatSignedPct(m);
                                        const direction = getFavoriteDirection(fav);
                                        const symbol = splitSymbol(fav.symbol);
                                        const stopLoss = fav.parameters?.stop_loss ?? null;
                                        const strategyDetail = getGridStrategyDetail(fav);
                                        const strategyDescription = getFavoriteStrategyDescription(fav);
                                        const refreshStatus = formatRefreshStatus(fav);
                                        const revalidationStatus = formatRevalidationStatus(fav);
                                        const origin = isDiscoveryOrigin(fav.metrics) ? 'discovery' : 'combo';
                                        const row = rowDataOf(fav);

                                        return (
                                            <tr
                                                key={fav.id}
                                                className={`${tier.className} ${isSelected ? 'selected' : ''}`}
                                                data-testid={`favorite-${fav.id}`}
                                                data-origin={origin}
                                                data-favorite-id={fav.id}
                                                data-class={row.cls}
                                                data-lote={row.lote ?? ''}
                                            >
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
                                                <td className="telegram-col">{renderTelegramControl(fav, 'column')}</td>
                                                <td className="symbol-col">
                                                    <div className="sym-cell">
                                                        <span className="sym-tile">{symbol.base.slice(0, 3)}</span>
                                                        <span>
                                                            <strong>{fav.symbol}</strong>
                                                            <small className="lote-symline">
                                                                {/* o par classe · moeda nunca se parte em duas linhas (P3 de Apply) */}
                                                                <span className="lote-pair">
                                                                    <span className="lote-cls" data-class={row.cls}>{chipLabel(row.cls)}</span> · <span className="lote-cur">{row.currency}</span>
                                                                </span>
                                                            </small>
                                                        </span>
                                                    </div>
                                                </td>
                                                <td className="strategy-cell">
                                                    <div className="strategy-stack" data-testid="favorites-strategy-identity">
                                                        <strong data-testid="favorites-strategy-title">{getFavoriteCatalogTitle(fav)}</strong>
                                                        {strategyDescription ? <span className="strategy-description" data-testid="favorites-strategy-description">{strategyDescription}</span> : null}
                                                        {strategyDetail ? <span className="fav-strategy-meta">{strategyDetail}</span> : null}
                                                        <span className={`fav-refresh-status ${refreshStatus.className}`} title={refreshStatus.title} data-testid="fav-refresh-status">
                                                            {refreshStatus.label}
                                                        </span>
                                                        {renderOutsidePortfolioWarning(fav)}
                                                        {revalidationStatus ? (
                                                            <span className={`fav-refresh-status ${revalidationStatus.className}`} title={revalidationStatus.title}>
                                                                {revalidationStatus.label}
                                                            </span>
                                                        ) : null}
                                                        {renderRowData(row, fav)}
                                                    </div>
                                                </td>
                                                <td className="direction-col">
                                                    <span className={`fav-direction ${direction === 'short' ? 'short' : 'long'}`}>
                                                        {direction === 'short' ? 'Short' : 'Long'}
                                                    </span>
                                                </td>
                                                <td><span className="tf-pill">{fav.timeframe}</span></td>
                                                <td className="muted-cell period-col">
                                                    {formatPeriod(fav)}
                                                    {row.effectiveRange ? <span className="lote-eff">efetivo {row.effectiveRange}</span> : null}
                                                </td>
                                                <td className="metric-cell risk-col">{formatPct(stopLoss)}</td>
                                                <td className="metric-cell accent" data-metric="sharpe">{formatNum(m.sharpe_ratio)}</td>
                                                <td className="metric-cell" data-metric="trades">{getTradesCount(fav)}</td>
                                                <td className="metric-cell win-col" data-metric="win">{formatPct(m.win_rate)}</td>
                                                <td className={`metric-cell strong ${totalReturn.positive ? 'positive' : 'negative'}`} data-metric="return">{totalReturn.text}</td>
                                                <td className="metric-cell negative risk-col" data-metric="maxdd">{formatPct(m.max_drawdown)}</td>
                                                <td className="metric-cell advanced-col">{formatNum(m.profit_factor)}</td>
                                                <td className="metric-cell advanced-col">{formatNum(m.sqn ?? m.sortino_ratio ?? m.sortino)}</td>
                                                <td className="metric-cell negative advanced-col">{formatPct(m.max_loss)}</td>
                                                <td className="metric-cell advanced-col">{atrWithCurrency(m.avg_atr, row.currency)}</td>
                                                <td>
                                                    <div className="fav-row-actions">
                                                        {renderTelegramControl(fav, 'actions')}
                                                        <button type="button" onClick={() => handleViewAnalysis(fav)} disabled={loadingAnalysisId === fav.id} title="Ver análise completa" aria-label="Ver análise completa" data-testid={`open-chart-${fav.id}`}>
                                                            {loadingAnalysisId === fav.id ? <span className="fav-spinner" /> : <BarChart3 className="h-4 w-4" />}
                                                        </button>
                                                        {isAdmin ? (
                                                            <>
                                                                <button type="button" onClick={(event) => handleRevalidate(fav, event.currentTarget)} disabled={revalidateMutation.isPending} title="Revalidar na janela recente" aria-label="Revalidar na janela recente">
                                                                    <RefreshCw className={`h-4 w-4 ${revalidateMutation.isPending ? 'animate-spin' : ''}`} />
                                                                </button>
                                                                <button type="button" onClick={() => handleDelete(fav.id)} title="Delete"><Trash2 className="h-4 w-4" /></button>
                                                            </>
                                                        ) : null}
                                                    </div>
                                                </td>
                                            </tr>
                                        );
                                    })
                                )}
                                {!favoritesListLoading && filteredFavorites.length > 0 && hasMore && (
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
                            {favoritesListLoading
                                ? 'Carregando estratégias...'
                                : favoritesListFailed
                                    ? 'Carga falhou'
                                    : hasMore
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

                {revalidationError ? (
                    <div className="fixed bottom-4 right-4 z-50 max-w-sm rounded-lg border border-[#f6465d]/50 bg-[#2b1720] px-4 py-3 text-sm text-[#f6465d] shadow-xl" role="alert">
                        {revalidationError}
                    </div>
                ) : null}

                {revalidationReport ? (
                    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 p-4 backdrop-blur-sm" data-testid="revalidation-report-modal" role="dialog" aria-modal="true" aria-labelledby="revalidation-report-title">
                        <div className="max-h-[90vh] w-full max-w-4xl overflow-y-auto rounded-2xl border border-[#2b3139] bg-[#181a20] text-[#eaecef] shadow-2xl">
                            <div className="flex items-start justify-between gap-4 border-b border-[#2b3139] p-5 sm:p-6">
                                <div>
                                    <div className="flex flex-wrap items-center gap-3">
                                        <h2 id="revalidation-report-title" className="text-xl font-semibold">Relatório de revalidação</h2>
                                        <OosVerdictBadge verdict={revalidationReport.revalidation.oos_verdict} />
                                    </div>
                                    <p className="mt-2 text-sm text-[#929aa5]">
                                        {revalidationReport.symbol} · {revalidationReport.timeframe} · {revalidationReport.window.start} a {revalidationReport.window.end}
                                    </p>
                                    <p className="mt-1 text-xs text-[#929aa5]">A revalidação atualiza somente o relatório; parâmetros e ativação permanecem inalterados.</p>
                                </div>
                                <button ref={revalidationCloseRef} type="button" onClick={closeRevalidationReport} className="inline-flex h-10 w-10 items-center justify-center rounded-md border border-[#2b3139] text-[#b7bdc6] hover:bg-[#2b3139]" aria-label="Fechar relatório">
                                    <X className="h-5 w-5" />
                                </button>
                            </div>
                            <OosMetricsTable
                                trainMetrics={revalidationReport.revalidation.best_metrics}
                                oosMetrics={revalidationReport.revalidation.oos_metrics}
                                verdict={revalidationReport.revalidation.oos_verdict}
                            />
                        </div>
                    </div>
                ) : null}

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
                                                    const totalReturn = formatCompoundReturn(s.metrics, { empty: '-' });
                                                    return (
                                                        <td key={s.id} className={`p-4 font-bold text-lg border-r border-zinc-200 ${totalReturn.positive ? 'text-green-500' : 'text-red-500'}`}>
                                                            {totalReturn.text}
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
