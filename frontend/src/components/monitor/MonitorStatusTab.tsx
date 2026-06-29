import React, { useEffect, useMemo, useState } from 'react';
import {
    getOpportunityAssetType,
    getOpportunityBaseAsset,
    getStrategyDisplayName,
    isDerivedPortfolioRuleActive,
    type Opportunity,
    DEFAULT_MONITOR_THEME,
    normalizeMonitorTheme,
    GLOBAL_MONITOR_PREFERENCE_KEY,
    type MonitorCardMode,
    type MonitorPreference,
    type MonitorPriceTimeframe,
    type MonitorTheme,
} from '@/components/monitor/types';
import { OpportunityCard } from '@/components/monitor/OpportunityCard';
import { ChartModal } from '@/components/monitor/ChartModal';
import { Button } from '@/components/ui/Button';
import {
    ChevronRight,
    LineChart,
    ListChecks,
    RefreshCw,
    Search,
} from 'lucide-react';
import { useToast } from '@/components/ui/use-toast';
import { API_BASE_URL } from '@/lib/apiBase';
import { authFetch } from '@/lib/authFetch';
import { buildTradeMarkers, getLatestMarkerSignalType, type MarkerSignalType } from '@/lib/tradeMarkers';
import { useAuth } from '@/stores/authStore';
import type { MarketCandle } from './MiniCandlesChart';
import { fetchMarketCandles, type ChartTimeframe } from './chartData';
import { resolveOpportunitySignal } from './signalResolution';

type SortOption = 'distance' | 'risk' | 'symbol' | 'tier_distance';
type TierFilter = 'rated' | 'all' | '1_2' | '1' | '2' | '3' | 'none';
type ListFilter = 'in_portfolio' | 'all';
type StrategyFilter = 'all' | string;
type TimeframeFilter = 'all' | '1d';
type StarFilter = 'all' | '3' | '2' | '1';
type WalletSyncState = 'idle' | 'loading' | 'ready' | 'empty' | 'error';
type SectionKey = 'hold' | 'exit';

type BinanceBalanceRow = {
    asset?: string;
    total?: number | string | null;
};

type DerivedPortfolioStatus = {
    active: boolean;
    inPortfolio: boolean;
    message: string | null;
    tone: 'neutral' | 'success' | 'warning';
};

type SectionRecord = {
    title: string;
    label: string;
    dotClass: 'monitor-dot--hold' | 'monitor-dot--exit';
    badgeClass: string;
    countClass: string;
    description: string;
};

type ResolvedSectionRow = {
    opportunity: Opportunity;
    resolved: ReturnType<typeof resolveOpportunitySignal>;
};

type FavoriteMarkerSignalByOpportunityId = Record<number, MarkerSignalType | null>;

const DEFAULT_PREFERENCE: MonitorPreference = {
    in_portfolio: false,
    card_mode: 'price',
    price_timeframe: '1d',
    theme: DEFAULT_MONITOR_THEME,
};
const BINANCE_MONITOR_PORTFOLIO_MIN_USD = 1;
const SPARKLINE_LIMIT = 14;
const symbolTestKey = (symbol: string): string => symbol.replace(/[^a-zA-Z0-9]+/g, '-').toLowerCase();

const getSparklineKey = (symbol: string, timeframe: ChartTimeframe): string => `${symbol}|${timeframe}`;

const renderSparkPath = (values: number[]): { line: string; area: string; dot: { x: number; y: number } } => {
    if (values.length === 0) {
        return { line: '', area: '', dot: { x: 0, y: 0 } };
    }

    const width = 80;
    const height = 22;
    const pad = 2;
    const min = Math.min(...values);
    const max = Math.max(...values);
    const range = max - min || 1;

    const points = values.map((value, index) => {
        const x = pad + (width - 2 * pad) * (index / Math.max(1, values.length - 1));
        const y = pad + (height - 2 * pad) * (1 - (value - min) / range);
        return { x, y };
    });

    const line = points
        .map((point, index) => `${index === 0 ? 'M' : 'L'}${point.x.toFixed(2)},${point.y.toFixed(2)}`)
        .join(' ');

    const first = points[0];
    const last = points[points.length - 1];
    const area = `${line} L ${last.x.toFixed(2)},${height.toFixed(2)} L ${first.x.toFixed(2)},${height.toFixed(2)} Z`;

    return { line, area, dot: { x: last.x, y: last.y } };
};

const SectionConfig: Record<SectionKey, SectionRecord> = {
    hold: {
        title: 'Compra',
        label: 'Posição ativa',
        dotClass: 'monitor-dot--hold',
        badgeClass: 'bg-emerald-500/20 text-emerald-300 border border-emerald-400/40',
        countClass: 'text-emerald-300',
        description: 'Sinais com decisão de compra e gestão ativa.',
    },
    exit: {
        title: 'Venda',
        label: 'Em observação',
        dotClass: 'monitor-dot--exit',
        badgeClass: 'bg-sky-500/20 text-sky-200 border border-sky-400/40',
        countClass: 'text-sky-300',
        description: 'Condição de venda detectada para novo monitoramento.',
    },
};

const SECTION_ORDER: SectionKey[] = ['hold', 'exit'];

const getDistanceLabel = (distance: number | null | undefined): string => {
    if (distance === null || distance === undefined) return '-';
    return `${distance.toFixed(2)}%`;
};

const formatPercent = (value: number | null | undefined): string => {
    if (value === null || value === undefined || Number.isNaN(value)) return '-';
    return `${value.toFixed(2)}%`;
};

const formatPrice = (value: number | null | undefined): string => {
    if (value === null || value === undefined || Number.isNaN(value)) {
        return '-';
    }
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 2,
        maximumFractionDigits: 6,
    }).format(value);
};

const toStringSearch = (value: string | null | undefined): string => String(value || '').toLowerCase().trim();

const getTierStars = (tier: number | null | undefined): string => {
    if (tier === 1) return '★★★';
    if (tier === 2) return '★★';
    if (tier === 3) return '★';
    return '';
};

const isRatedOpportunity = (opportunity: Opportunity): boolean => getTierStars(opportunity.tier).length > 0;

const averageDistance = (values: Array<number | null | undefined>): number | null => {
    const filtered = values.filter((value) => Number.isFinite(value ?? NaN));
    if (filtered.length === 0) return null;
    return filtered.reduce((acc, value) => acc + (value ?? 0), 0) / filtered.length;
};

export const MonitorStatusTab: React.FC = () => {
    const { user } = useAuth();
    const [opportunities, setOpportunities] = useState<Opportunity[]>([]);
    const [loading, setLoading] = useState(false);
    const [openingChartOpportunityId, setOpeningChartOpportunityId] = useState<string | null>(null);
    const [activeChart, setActiveChart] = useState<{
        opportunity: Opportunity;
        initialCandles: MarketCandle[];
        initialTimeframe: ChartTimeframe;
        viewMode: 'chart' | 'trades';
    } | null>(null);
    const sortBy: SortOption = 'tier_distance';
    const [tierFilter, setTierFilter] = useState<TierFilter>('rated');
    const [listFilter, setListFilter] = useState<ListFilter>('in_portfolio');
    const [strategyFilter, setStrategyFilter] = useState<StrategyFilter>('all');
    const [timeframeFilter, setTimeframeFilter] = useState<TimeframeFilter>('all');
    const [starFilter, setStarFilter] = useState<StarFilter>('all');
    const [searchTerm, setSearchTerm] = useState('');
    const [lastUpdated, setLastUpdated] = useState<Date | null>(null);
    const [preferences, setPreferences] = useState<Record<string, MonitorPreference>>({});
    const [binanceConfigured, setBinanceConfigured] = useState(false);
    const [walletHoldingsByAsset, setWalletHoldingsByAsset] = useState<Record<string, number>>({});
    const [walletSyncState, setWalletSyncState] = useState<WalletSyncState>('idle');
    const [walletSyncMessage, setWalletSyncMessage] = useState<string | null>(null);
    const [savingSymbols, setSavingSymbols] = useState<Record<string, boolean>>({});
    const [sparklineByKey, setSparklineByKey] = useState<Record<string, number[]>>({});
    const [sparklineLoadingByKey, setSparklineLoadingByKey] = useState<Record<string, boolean>>({});
    const [sparklineErrorByKey, setSparklineErrorByKey] = useState<Record<string, boolean>>({});
    const [favoriteMarkerSignalByOpportunityId, setFavoriteMarkerSignalByOpportunityId] = useState<FavoriteMarkerSignalByOpportunityId>({});
    const [expandedRows, setExpandedRows] = useState<Record<string, boolean>>(
        {}
    );
    const { toast } = useToast();
    const showTechnicalColumns = user?.isAdmin === true;
    const detailColSpan = showTechnicalColumns ? 9 : 7;

    const getPreference = (symbol: string): MonitorPreference => {
        return preferences[symbol] ?? DEFAULT_PREFERENCE;
    };

    const fetchWalletPortfolio = async (configured: boolean) => {
        if (!configured) {
            setWalletHoldingsByAsset({});
            setWalletSyncState('idle');
            setWalletSyncMessage(null);
            return;
        }

        setWalletSyncState('loading');
        setWalletSyncMessage('Sincronizando carteira Binance...');

        try {
            const response = await authFetch(
                `${API_BASE_URL}/external/binance/spot/balances?min_usd=${BINANCE_MONITOR_PORTFOLIO_MIN_USD}`,
            );
            const payload = await response.json();
            if (!response.ok) {
                throw new Error(String(payload?.detail || `Falha ao carregar carteira Binance (${response.status})`));
            }

            const balances = Array.isArray(payload?.balances) ? payload.balances as BinanceBalanceRow[] : [];
            const nextHoldings: Record<string, number> = {};
            for (const row of balances) {
                const asset = String(row?.asset || '').trim().toUpperCase();
                const total = Number(row?.total ?? 0);
                if (!asset || !Number.isFinite(total) || total <= 0) {
                    continue;
                }
                nextHoldings[asset] = total;
            }

            setWalletHoldingsByAsset(nextHoldings);
            if (Object.keys(nextHoldings).length === 0) {
                setWalletSyncState('empty');
                setWalletSyncMessage(
                    `Nenhum ativo com saldo minimo de US$ ${BINANCE_MONITOR_PORTFOLIO_MIN_USD} foi encontrado na Carteira Binance.`,
                );
                return;
            }

            setWalletSyncState('ready');
            setWalletSyncMessage(null);
        } catch (error) {
            console.error(error);
            setWalletHoldingsByAsset({});
            setWalletSyncState('error');
            setWalletSyncMessage(
                error instanceof Error && error.message
                    ? error.message
                    : 'Carteira Binance indisponível no momento.',
            );
        }
    };

    const fetchMonitorContext = async () => {
        try {
            const preferencesResponse = await authFetch(`${API_BASE_URL}/monitor/preferences`);
            if (!preferencesResponse.ok) {
                throw new Error(`Falha ao carregar preferências do monitor (${preferencesResponse.status})`);
            }

            const preferencesPayload = await preferencesResponse.json();
            if (typeof preferencesPayload === 'object' && preferencesPayload) {
                const normalized: Record<string, MonitorPreference> = {};
                for (const [symbol, raw] of Object.entries(preferencesPayload as Record<string, any>)) {
                    normalized[symbol] = {
                        in_portfolio: Boolean(raw?.in_portfolio),
                        card_mode: raw?.card_mode === 'strategy' ? 'strategy' : 'price',
                        price_timeframe: raw?.price_timeframe === '1d'
                            ? raw.price_timeframe
                            : '1d',
                        theme: normalizeMonitorTheme(raw?.theme),
                    };
                }
                setPreferences(normalized);
            } else {
                setPreferences({});
            }
        } catch (error) {
            console.error(error);
            toast({
                title: 'Erro',
                description: 'Não foi possível carregar preferências do monitor.',
                variant: 'destructive',
            });
        }

        let configured = false;
        try {
            const credentialsResponse = await authFetch(`${API_BASE_URL}/user/binance-credentials`);
            const payload = await credentialsResponse.json();
            if (!credentialsResponse.ok) {
                throw new Error(String(payload?.detail || `Falha ao carregar status das credenciais Binance (${credentialsResponse.status})`));
            }
            configured = Boolean(payload?.configured);
            setBinanceConfigured(configured);
        } catch (error) {
            console.error(error);
            setBinanceConfigured(false);
            configured = false;
        }

        await fetchWalletPortfolio(configured);
    };

    const fetchOpportunities = async (tier?: TierFilter, options?: { refresh?: boolean }) => {
        setLoading(true);
        try {
            const tierParam = tier || tierFilter;
            let apiTier: string;
            if (tierParam === 'rated') {
                apiTier = '1,2,3';
            } else if (tierParam === 'all') {
                apiTier = 'all';
            } else if (tierParam === '1_2') {
                apiTier = '1,2';
            } else if (tierParam === 'none') {
                apiTier = 'none';
            } else {
                apiTier = tierParam;
            }

            const baseUrl = import.meta.env.VITE_API_URL || '/api';
            const refreshParam = options?.refresh ? '&refresh=true' : '';
            const url = `${baseUrl}/opportunities/?tier=${encodeURIComponent(apiTier)}${refreshParam}`;
            const response = await authFetch(url);
            if (!response.ok) throw new Error('Falha ao buscar oportunidades');
            const data = await response.json();
            setOpportunities(data);
            setFavoriteMarkerSignalByOpportunityId({});
            setLastUpdated(new Date());

            toast({
                title: 'Atualizado',
                description: `${data.length} estratégias analisadas`,
            });
        } catch (error) {
            console.error(error);
            toast({
                title: 'Erro',
                description: 'Não foi possível carregar as estratégias.',
                variant: 'destructive',
            });
        } finally {
            setLoading(false);
        }
    };

    const persistPreference = async (symbol: string, patch: Partial<MonitorPreference>) => {
        const prev = getPreference(symbol);
        const next: MonitorPreference = {
            in_portfolio: patch.in_portfolio ?? prev.in_portfolio,
            card_mode: patch.card_mode ?? prev.card_mode,
            price_timeframe: patch.price_timeframe ?? prev.price_timeframe,
            theme: patch.theme ?? prev.theme ?? DEFAULT_MONITOR_THEME,
        };

        setPreferences((current) => ({ ...current, [symbol]: next }));
        setSavingSymbols((current) => ({ ...current, [symbol]: true }));

        try {
            const response = await authFetch(`${API_BASE_URL}/monitor/preferences/${encodeURIComponent(symbol)}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(patch),
            });
            const payload = await response.json();

            if (!response.ok) {
                throw new Error(String(payload?.detail || `Falha ao salvar preferência (${response.status})`));
            }

            setPreferences((current) => ({
                ...current,
                [symbol]: {
                    in_portfolio: Boolean(payload?.in_portfolio),
                    card_mode: payload?.card_mode === 'strategy' ? 'strategy' : 'price',
                    price_timeframe: payload?.price_timeframe === '1d'
                        ? payload.price_timeframe
                        : '1d',
                    theme: normalizeMonitorTheme(payload?.theme),
                },
            }));
        } catch (error) {
            setPreferences((current) => ({ ...current, [symbol]: prev }));
            toast({
                title: 'Erro',
                description: error instanceof Error ? error.message : 'Falha ao salvar preferência.',
                variant: 'destructive',
            });
        } finally {
            setSavingSymbols((current) => ({ ...current, [symbol]: false }));
        }
    };

    const handleToggleInPortfolio = (symbol: string, nextValue: boolean) => {
        void persistPreference(symbol, { in_portfolio: nextValue });
    };

    const handleToggleCardMode = (symbol: string, nextMode: MonitorCardMode) => {
        void persistPreference(symbol, { card_mode: nextMode });
    };

    const handleToggleTimeframe = (symbol: string, nextTimeframe: MonitorPriceTimeframe) => {
        void nextTimeframe;
        void persistPreference(symbol, { price_timeframe: '1d' });
        void fetchMarketCandles(symbol, '1d', undefined, SPARKLINE_LIMIT).catch((error) => {
            console.error(`Falha ao pré-carregar velas para ${symbol} (1d)`, error);
        });
    };

    const resolveChartTimeframe = (opportunity: Opportunity): ChartTimeframe => {
        void opportunity;
        return '1d';
    };

    const getOpeningChartKey = (opportunity: Opportunity): string => String(opportunity.id);

    const handleOpenChart = async (opportunity: Opportunity, viewMode: 'chart' | 'trades' = 'chart') => {
        const initialTimeframe = resolveChartTimeframe(opportunity);
        const currentKey = getOpeningChartKey(opportunity);

        setOpeningChartOpportunityId(currentKey);

        try {
            const rows = await fetchMarketCandles(opportunity.symbol, initialTimeframe);
            if (rows.length === 0) {
                toast({
                    title: 'Gráfico indisponível',
                    description: `Sem dados de candle para ${opportunity.symbol} no timeframe ${initialTimeframe}.`,
                    variant: 'destructive',
                });
                return;
            }

            setActiveChart({
                opportunity,
                initialCandles: rows,
                initialTimeframe,
                viewMode,
            });
        } catch (error) {
            toast({
                title: 'Gráfico indisponível',
                description: error instanceof Error ? error.message : 'Falha ao carregar dados do gráfico.',
                variant: 'destructive',
            });
        } finally {
            setOpeningChartOpportunityId((current) => (current === currentKey ? null : current));
        }
    };

    const handleToggleRow = (rowKey: string) => {
        setExpandedRows((current) => ({
            ...current,
            [rowKey]: !(current[rowKey] ?? false),
        }));
    };

    const getSparklineColor = (sectionKey: SectionKey): string => {
        if (sectionKey === 'exit') return '#f26e7e';
        return '#3dd68c';
    };

    const handleRowClick = (event: React.MouseEvent<HTMLTableRowElement>, rowKey: string) => {
        const target = event.target as HTMLElement;
        if (target.closest('.row-action') || target.closest('.row-toggle')) {
            return;
        }

        handleToggleRow(rowKey);
    };

    useEffect(() => {
        void fetchMonitorContext();
    }, []);

    useEffect(() => {
        void fetchOpportunities(tierFilter);
    }, [tierFilter]);

    const sortedOpportunities = useMemo(() => {
        const sorted = [...opportunities].sort((a, b) => {
            if (sortBy === 'tier_distance') {
                const tierA = a.tier ?? 999;
                const tierB = b.tier ?? 999;
                const priorityA = tierA <= 2 ? 0 : 1;
                const priorityB = tierB <= 2 ? 0 : 1;
                if (priorityA !== priorityB) {
                    return priorityA - priorityB;
                }
                if (a.is_holding !== b.is_holding) {
                    return a.is_holding ? -1 : 1;
                }
                if (tierA !== tierB) {
                    return tierA - tierB;
                }
                const distA = a.distance_to_next_status ?? 999;
                const distB = b.distance_to_next_status ?? 999;
                if (distA !== distB) {
                    return distA - distB;
                }
                return a.symbol.localeCompare(b.symbol);
            } else if (sortBy === 'distance') {
                if (a.is_holding !== b.is_holding) {
                    return a.is_holding ? -1 : 1;
                }
                const distA = a.distance_to_next_status ?? 999;
                const distB = b.distance_to_next_status ?? 999;
                if (distA !== distB) {
                    return distA - distB;
                }
                const tierA = a.tier ?? 999;
                const tierB = b.tier ?? 999;
                if (tierA !== tierB) {
                    return tierA - tierB;
                }
                return a.symbol.localeCompare(b.symbol);
            } else if (sortBy === 'risk') {
                const riskA = a.distance_to_stop_pct ?? 999;
                const riskB = b.distance_to_stop_pct ?? 999;
                if (riskA !== riskB) {
                    return riskA - riskB;
                }
                return a.symbol.localeCompare(b.symbol);
            } else if (sortBy === 'symbol') {
                return a.symbol.localeCompare(b.symbol);
            }
            return 0;
        });
        return sorted;
    }, [opportunities, sortBy]);

    const portfolioStatusBySymbol = useMemo(() => {
        const next: Record<string, DerivedPortfolioStatus> = {};
        for (const opp of sortedOpportunities) {
            if (!String(opp.symbol || '').trim() || next[opp.symbol]) {
                continue;
            }

            const manualPreference = getPreference(opp.symbol);
            const derivedActive = isDerivedPortfolioRuleActive(opp, binanceConfigured);
            if (!derivedActive) {
                next[opp.symbol] = {
                    active: false,
                    inPortfolio: manualPreference.in_portfolio,
                    message: null,
                    tone: 'neutral',
                };
                continue;
            }

            const baseAsset = getOpportunityBaseAsset(opp);
            const hasWalletPosition = (walletHoldingsByAsset[baseAsset] ?? 0) > 0;
            if (walletSyncState === 'loading') {
                next[opp.symbol] = {
                    active: true,
                    inPortfolio: hasWalletPosition || manualPreference.in_portfolio,
                    message: 'Sincronizando carteira Binance...',
                    tone: 'neutral',
                };
                continue;
            }

            if (walletSyncState === 'error') {
                next[opp.symbol] = {
                    active: true,
                    inPortfolio: false,
                    message: walletSyncMessage || 'Carteira Binance indisponível. Portfólio bloqueado até a sincronização voltar.',
                    tone: 'warning',
                };
                continue;
            }

            if (walletSyncState === 'empty') {
                next[opp.symbol] = {
                    active: true,
                    inPortfolio: false,
                    message: 'Sem posição elegível na Carteira Binance.',
                    tone: 'warning',
                };
                continue;
            }

            next[opp.symbol] = {
                active: true,
                inPortfolio: hasWalletPosition,
                message: hasWalletPosition
                    ? `Sincronizado com a Carteira Binance (${baseAsset}).`
                    : `Sem posição comprada de ${baseAsset} na Carteira Binance.`,
                tone: hasWalletPosition ? 'success' : 'warning',
            };
        }
        return next;
    }, [binanceConfigured, sortedOpportunities, walletHoldingsByAsset, walletSyncMessage, walletSyncState, preferences]);

    const strategyOptions = useMemo(() => {
        const next = new Set<string>();
        for (const opp of sortedOpportunities) {
            const strategyName = getStrategyDisplayName(opp);
            const strategy = toStringSearch(strategyName);
            if (strategy) {
                next.add(strategyName.trim());
            }
        }
        return ['all', ...Array.from(next).sort((a, b) => a.localeCompare(b))];
    }, [sortedOpportunities]);

    const filteredOpportunities = useMemo(() => {
        const normalizedSearch = toStringSearch(searchTerm);

        const afterAssetType = sortedOpportunities.filter((opp) => {
            if (!String(opp.symbol || '').trim()) return false;
            return getOpportunityAssetType(opp) === 'crypto' && isRatedOpportunity(opp);
        });

        const effectiveListFilter = showTechnicalColumns ? listFilter : 'all';
        const afterListFilter =
            effectiveListFilter === 'in_portfolio'
                    ? afterAssetType.filter((opp) => portfolioStatusBySymbol[opp.symbol]?.inPortfolio === true)
                    : afterAssetType;

        const afterStrategyFilter =
            strategyFilter === 'all'
                ? afterListFilter
                : afterListFilter.filter((opp) => toStringSearch(getStrategyDisplayName(opp)) === toStringSearch(strategyFilter));

        const afterTimeframeFilter =
            timeframeFilter === 'all'
                ? afterStrategyFilter
                : afterStrategyFilter.filter((opp) => opp.timeframe === timeframeFilter);

        const afterStarFilter =
            starFilter === 'all'
                ? afterTimeframeFilter
                : afterTimeframeFilter.filter((opp) => String(getTierStars(opp.tier).length) === starFilter);

        if (!normalizedSearch) {
            return afterStarFilter;
        }

        return afterStarFilter.filter((opp) => {
            const tierStars = getTierStars(opp.tier);
            const candidate = [
                opp.symbol,
                opp.name,
                getStrategyDisplayName(opp),
                opp.strategy_description,
                getOpportunityAssetType(opp),
                toStringSearch(opp.next_status_label),
                tierStars,
                tierStars ? `${tierStars.length} estrelas` : '',
                opp.tier ? `tier ${opp.tier}` : '',
            ].map((value) => toStringSearch(String(value))).join(' ');

            return candidate.includes(normalizedSearch);
        });
    }, [
        listFilter,
        portfolioStatusBySymbol,
        searchTerm,
        starFilter,
        strategyFilter,
        timeframeFilter,
        sortedOpportunities,
    ]);

    const favoriteMarkerProbeKey = useMemo(
        () => filteredOpportunities
            .map((opportunity) => `${opportunity.id}:${opportunity.timeframe}:${String(opportunity.parameters?.direction || 'long')}`)
            .join('|'),
        [filteredOpportunities],
    );

    useEffect(() => {
        const missing = filteredOpportunities.filter((opportunity) => (
            favoriteMarkerSignalByOpportunityId[opportunity.id] === undefined
        ));
        if (missing.length === 0) {
            return;
        }

        const controller = new AbortController();
        let cancelled = false;

        const loadMarkerSignals = async () => {
            const results = await Promise.all(missing.map(async (opportunity): Promise<readonly [number, MarkerSignalType | null]> => {
                try {
                    const response = await authFetch(`${API_BASE_URL}/favorites/${opportunity.id}/trades`, {
                        signal: controller.signal,
                    });
                    const payload = await response.json().catch(() => ({}));
                    if (!response.ok) {
                        return [opportunity.id, null] as const;
                    }

                    const trades = Array.isArray(payload?.trades) ? payload.trades : [];
                    const markers = buildTradeMarkers(trades, {
                        direction: String(opportunity.parameters?.direction || 'long'),
                        timeframe: opportunity.timeframe,
                    });
                    return [opportunity.id, getLatestMarkerSignalType(markers)] as const;
                } catch {
                    return [opportunity.id, null] as const;
                }
            }));

            if (cancelled) {
                return;
            }

            setFavoriteMarkerSignalByOpportunityId((current) => {
                const next = { ...current };
                results.forEach(([id, markerSignal]) => {
                    next[id] = markerSignal;
                });
                return next;
            });
        };

        void loadMarkerSignals();

        return () => {
            cancelled = true;
            controller.abort();
        };
    }, [favoriteMarkerProbeKey, favoriteMarkerSignalByOpportunityId, filteredOpportunities]);

    const resolvedSections = useMemo(() => {
        const groups: Record<SectionKey, ResolvedSectionRow[]> = {
            hold: [],
            exit: [],
        };

        for (const opportunity of filteredOpportunities) {
            const markerSignal = favoriteMarkerSignalByOpportunityId[opportunity.id] ?? null;
            const resolved = resolveOpportunitySignal(opportunity, {
                selectedTimeframe: opportunity.timeframe,
                latestVisibleMarkerType: markerSignal,
            });
            groups[resolved.section].push({ opportunity, resolved });
        }

        for (const section of SECTION_ORDER) {
            groups[section].sort((a, b) => {
                if (a.opportunity.tier !== b.opportunity.tier) {
                    return (a.opportunity.tier ?? 999) - (b.opportunity.tier ?? 999);
                }
                return getDistanceLabel(a.opportunity.distance_to_next_status).localeCompare(
                    getDistanceLabel(b.opportunity.distance_to_next_status),
                );
            });
        }

        return groups;
    }, [favoriteMarkerSignalByOpportunityId, filteredOpportunities]);

    const visibleOpportunityCount = resolvedSections.hold.length + resolvedSections.exit.length;

    const sectionCountByType = useMemo(() => ({
        hold: resolvedSections.hold.length,
        exit: resolvedSections.exit.length,
    }), [resolvedSections]);

    const inPortfolioCount = useMemo(() => {
        return Object.values(portfolioStatusBySymbol).filter((item) => item.inPortfolio).length;
    }, [portfolioStatusBySymbol]);

    const noResultsForInPortfolio =
        !loading &&
        opportunities.length > 0 &&
        filteredOpportunities.length === 0 &&
        showTechnicalColumns &&
        listFilter === 'in_portfolio';
    const noActionableResults =
        !loading &&
        opportunities.length > 0 &&
        filteredOpportunities.length > 0 &&
        visibleOpportunityCount === 0;
    const emptyFilterMessage = 'Nenhum ativo encontrado na lista de carteira.';

    const sectionAverageRisk = useMemo(() => ({
        hold: averageDistance(resolvedSections.hold.map(({ opportunity }) => opportunity.distance_to_stop_pct)),
        exit: averageDistance(resolvedSections.exit.map(({ opportunity }) => opportunity.distance_to_stop_pct)),
    }), [resolvedSections]);

    useEffect(() => {
        const shouldLoadSparklines = false;
        if (!shouldLoadSparklines) {
            return;
        }

        const rowsToFetch = new Map<string, { symbol: string; timeframe: ChartTimeframe }>();
        for (const section of SECTION_ORDER) {
            for (const { opportunity } of resolvedSections[section]) {
                const timeframe = resolveChartTimeframe(opportunity);
                const key = getSparklineKey(opportunity.symbol, timeframe);

                if (
                    !rowsToFetch.has(key)
                    && !sparklineByKey[key]
                    && !sparklineLoadingByKey[key]
                    && !sparklineErrorByKey[key]
                ) {
                    rowsToFetch.set(key, { symbol: opportunity.symbol, timeframe });
                }
            }
        }

        if (rowsToFetch.size === 0) {
            return;
        }

        setSparklineLoadingByKey((current) => {
            const next = { ...current };
            let changed = false;
            for (const key of rowsToFetch.keys()) {
                if (!next[key]) {
                    next[key] = true;
                    changed = true;
                }
            }
            return changed ? next : current;
        });

        let cancelled = false;
        const controllers = new Map<string, AbortController>();

        void (async () => {
            await Promise.all(
                Array.from(rowsToFetch.entries()).map(async ([key, request]) => {
                    const controller = new AbortController();
                    controllers.set(key, controller);

                    try {
                        const rows = await fetchMarketCandles(
                            request.symbol,
                            request.timeframe,
                            controller.signal,
                            SPARKLINE_LIMIT,
                        );
                        const values = rows
                            .map((row) => Number(row.close))
                            .filter((value) => Number.isFinite(value));

                        if (cancelled) return;

                        setSparklineByKey((current) => {
                            if (current[key]) {
                                return current;
                            }
                            return { ...current, [key]: values };
                        });
                        setSparklineErrorByKey((current) => ({ ...current, [key]: false }));
                    } catch (error) {
                        if (error instanceof DOMException && error.name === 'AbortError') {
                            return;
                        }
                        if (!cancelled) {
                            console.error(`Falha ao carregar sparkline para ${request.symbol} (${request.timeframe})`, error);
                            setSparklineErrorByKey((current) => ({ ...current, [key]: true }));
                        }
                    } finally {
                        if (!cancelled) {
                            setSparklineLoadingByKey((current) => ({ ...current, [key]: false }));
                        }
                    }
                }),
            );
        })();

        return () => {
            cancelled = true;
            for (const controller of controllers.values()) {
                controller.abort();
            }
        };
    }, [resolvedSections, sparklineByKey, sparklineErrorByKey, sparklineLoadingByKey]);

    const totalKpi = {
        hold: sectionCountByType.hold,
        exit: sectionCountByType.exit,
        visible: visibleOpportunityCount,
        inPortfolio: inPortfolioCount,
        avgHoldRisk: formatPercent(sectionAverageRisk.hold),
        avgExitRisk: formatPercent(sectionAverageRisk.exit),
    };

    const theme: MonitorTheme = normalizeMonitorTheme(preferences[GLOBAL_MONITOR_PREFERENCE_KEY]?.theme);
    const effectiveSearchPlaceholder = 'Buscar par, estratégia, tag...';
    const toggleTheme = () => {
        void persistPreference(GLOBAL_MONITOR_PREFERENCE_KEY, { theme: theme === DEFAULT_MONITOR_THEME ? 'black' : DEFAULT_MONITOR_THEME });
    };

    return (
        <div className={`monitor-page-shell monitor-theme monitor-theme--${theme}`} data-testid="monitor-status-tab">
            <div className="monitor-main">
                <header className="topbar">
                    <div className="topbar-spacer" />
                    <label className="search">
                        <Search className="h-4 w-4" />
                        <input
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                            placeholder={effectiveSearchPlaceholder}
                        />
                        <span className="kbd">⌘K</span>
                    </label>
                    <Button
                        variant="secondary"
                        className="topbar-btn"
                        data-testid="monitor-theme-toggle"
                        onClick={toggleTheme}
                    >
                        Tema
                    </Button>
                    <Button
                        variant="secondary"
                        className="topbar-btn primary"
                        onClick={() => {
                            void Promise.all([fetchOpportunities(undefined, { refresh: true }), fetchMonitorContext()]);
                        }}
                        disabled={loading}
                    >
                        <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
                        Atualizar
                    </Button>
                </header>

                <section className="page">
                    <header className="page-head">
                        <div>
                            <h1 className="sr-only">Monitor de sinais</h1>
                            <p className="page-sub">
                                Operações ativas e saídas acionáveis. Atualização contínua a cada 30s.
                            </p>
                            {lastUpdated ? (
                                <div className="updated">
                                    <span>Última leitura</span>
                                    <span className="mono"> {lastUpdated.toLocaleTimeString('pt-BR')} </span>
                                    <span>· BRT</span>
                                </div>
                            ) : null}
                        </div>
                    </header>

                    <div className="kpis">
                        <div className="kpi">
                            <div className="kpi-label">
                                Em posição
                                <span className="tag">Compra</span>
                            </div>
                            <div className="kpi-val">{totalKpi.hold}</div>
                            <div className="kpi-foot up">média risco {totalKpi.avgHoldRisk}</div>
                        </div>
                        <div className="kpi">
                            <div className="kpi-label">
                                Em saída
                                <span className="tag">Venda</span>
                            </div>
                            <div className="kpi-val">{totalKpi.exit}</div>
                            <div className="kpi-foot">média risco {totalKpi.avgExitRisk}</div>
                        </div>
                        <div className="kpi">
                            <div className="kpi-label">Total</div>
                            <div className="kpi-val">{totalKpi.visible}</div>
                            <div className="kpi-foot">sinais filtrados</div>
                        </div>
                        <div className="kpi">
                            <div className="kpi-label">Em carteira</div>
                            <div className="kpi-val">{totalKpi.inPortfolio}</div>
                            <div className="kpi-foot">ativos rastreados</div>
                        </div>
                    </div>

                    <section className="filterbar" aria-label="Filtros do monitor">
                        {showTechnicalColumns ? <div className="seg" data-seg="list">
                            <button
                                className={listFilter === 'in_portfolio' ? 'on' : ''}
                                onClick={() => setListFilter('in_portfolio')}
                                data-testid="monitor-filter-in-portfolio"
                            >
                                Em portfólio
                            </button>
                            <button
                                className={listFilter === 'all' ? 'on' : ''}
                                onClick={() => setListFilter('all')}
                                data-testid="monitor-filter-all"
                            >
                                Todos
                            </button>
                        </div> : null}
                        {showTechnicalColumns ? <div className="filter-divider" /> : null}
                        <select className="select" value={timeframeFilter} onChange={(e) => setTimeframeFilter(e.target.value as TimeframeFilter)}>
                            <option value="all">Timeframe: Todos</option>
                            <option value="1d">1d</option>
                        </select>
                        <select
                            className="select"
                            value={starFilter}
                            onChange={(e) => setStarFilter(e.target.value as StarFilter)}
                            data-testid="monitor-filter-stars"
                        >
                            <option value="all">Estrelas: Todas</option>
                            <option value="3">★★★ 3 estrelas</option>
                            <option value="2">★★ 2 estrelas</option>
                            <option value="1">★ 1 estrela</option>
                        </select>
                        <select
                            className="select"
                            value={strategyFilter}
                            onChange={(e) => setStrategyFilter(e.target.value)}
                        >
                            {strategyOptions.map((strategy) => (
                                <option key={strategy} value={strategy}>
                                    {strategy === 'all' ? 'Estratégia: Todas' : strategy}
                                </option>
                            ))}
                        </select>
                        <div className="filter-spacer" />
                        <span className="chip-count">
                            {visibleOpportunityCount} resultados
                        </span>
                    </section>

                    <main className="monitor-board">
                        {loading && opportunities.length === 0 ? (
                            <div className="status-empty">Carregando sinais...</div>
                        ) : opportunities.length === 0 && !loading ? (
                            <section className="monitor-empty-card">
                                <p className="monitor-empty-text">Nenhum ativo disponível no monitor.</p>
                                <Button variant="secondary" onClick={() => (window.location.href = '/')}>
                                    Ir para Backtester
                                </Button>
                            </section>
                        ) : noResultsForInPortfolio ? (
                            <section className="monitor-empty-card" data-testid="monitor-empty-in-portfolio">
                                                        <p className="monitor-empty-text">{emptyFilterMessage}</p>
                                <Button variant="secondary" onClick={() => setListFilter('all')}>
                                    Mostrar todos
                                </Button>
                            </section>
                        ) : noActionableResults ? (
                            <section className="monitor-empty-card" data-testid="monitor-empty-actionable">
                                <p className="monitor-empty-text">Nenhum sinal acionável no monitor.</p>
                            </section>
                        ) : (
                            SECTION_ORDER.map((sectionKey) => {
                                const cfg = SectionConfig[sectionKey];
                                const rows = resolvedSections[sectionKey];

                                return (
                                    <section key={sectionKey} data-testid={`monitor-section-${sectionKey}`}>
                                        <div className="status-row">
                                            <span className="status-section-label">Estado {cfg.title}</span>
                                            <h3>
                                                <span className={`pip ${sectionKey}`} />
                                                {sectionKey === 'hold' ? 'Em posição' : 'Saída / cobertura'}
                                                <span className="meta">({rows.length})</span>
                                            </h3>
                            <p className="desc">
                                {sectionKey === 'hold'
                                    ? 'Posição ativa com gestão em acompanhamento contínuo.'
                                    : 'Saída ou cobertura acionável para nova análise.'}
                            </p>
                                        </div>

                                        <div className="mobile-cards">
                                            {rows.map(({ opportunity, resolved }) => {
                                                const pref = getPreference(opportunity.symbol);
                                                const derived = portfolioStatusBySymbol[opportunity.symbol];
                                                const inPortfolio = derived?.inPortfolio ?? pref.in_portfolio;

                                                return (
                                                    <article
                                                        key={`mobile-${sectionKey}-${opportunity.id}`}
                                                        className="mobile-card"
                                                    >
                                                        <OpportunityCard
                                                            opportunity={opportunity}
                                                            preference={{
                                                                ...pref,
                                                                in_portfolio: inPortfolio,
                                                            }}
                                                            isPortfolioDerived={Boolean(derived?.active)}
                                                            portfolioStatusMessage={derived?.message}
                                                            portfolioStatusTone={derived?.tone}
                                                            resolvedSignal={resolved}
                                                            isSavingPreference={Boolean(savingSymbols[opportunity.symbol])}
                                                            isOpeningChart={openingChartOpportunityId === getOpeningChartKey(opportunity)}
                                                            isAdmin={showTechnicalColumns}
                                                            onToggleInPortfolio={handleToggleInPortfolio}
                                                            onToggleCardMode={handleToggleCardMode}
                                                            onToggleTimeframe={handleToggleTimeframe}
                                                            onOpenChart={handleOpenChart}
                                                        />
                                                    </article>
                                                );
                                            })}
                                        </div>

                                        <div className="table-wrap">
                                            <table className="signals">
                                                <thead>
                                                    <tr>
                                                        <th style={{ width: '32px' }} />
                                                        <th>Par / Estratégia</th>
                                                        <th>Status</th>
                                                        <th>Preço</th>
                                                        {showTechnicalColumns ? <th>Distância</th> : null}
                                                        {showTechnicalColumns ? <th className="col-spark">7d</th> : null}
                                                        <th>Risco até stop</th>
                                                        <th className="col-tags">Tags</th>
                                                        <th className="actions-cell" />
                                                    </tr>
                                                </thead>
                                                <tbody>
                                                        {rows.map(({ opportunity, resolved }) => {
                                                            const chartTimeframe = resolveChartTimeframe(opportunity);
                                                            const pref = getPreference(opportunity.symbol);
                                                            const derived = portfolioStatusBySymbol[opportunity.symbol];
                                                            const inPortfolio = derived?.inPortfolio ?? pref.in_portfolio;
                                                            const expanded = expandedRows[`${sectionKey}-${opportunity.id}`] ?? false;
                                                            const rowKey = `${sectionKey}-${opportunity.id}`;
                                                            const riskStop = opportunity.distance_to_stop_pct ?? 0;
                                                            const pairPrefix = getOpportunityBaseAsset(opportunity)
                                                                .slice(0, 3)
                                                                .toUpperCase();
                                                            const sparklineKey = getSparklineKey(opportunity.symbol, chartTimeframe);
                                                            const sparklinePoints = sparklineByKey[sparklineKey] ?? [];
                                                            const showSparkline = sparklinePoints.length >= 2;
                                                            const spark = renderSparkPath(sparklinePoints);
                                                            const sparkColor = getSparklineColor(sectionKey);

                                                        return (
                                                            <React.Fragment key={opportunity.id}>
                                                                <tr
                                                                    className={`head-row ${expanded ? 'expanded' : ''}`}
                                                                    data-idx={rowKey}
                                                                    aria-expanded={expanded}
                                                                    data-testid={`monitor-row-${symbolTestKey(opportunity.symbol)}`}
                                                                    onClick={(event) => handleRowClick(event, rowKey)}
                                                                >
                                                                    <td>
                                                                        <button
                                                                            type="button"
                                                                            className={`row-toggle ${expanded ? 'open' : ''}`}
                                                                            aria-expanded={expanded}
                                                                            onClick={(event) => {
                                                                                event.stopPropagation();
                                                                                handleToggleRow(rowKey);
                                                                            }}
                                                                            aria-label="Expandir"
                                                                        >
                                                                            <ChevronRight className="h-4 w-4" />
                                                                        </button>
                                                                    </td>
                                                                    <td>
                                                                            <div className="pair-cell">
                                                                                <div className={`pair-icon ${pairPrefix.toLowerCase()}`}>{pairPrefix}</div>
                                                                                <div className="pair-meta">
                                                                                    <div className="pair-name">
                                                                                        {opportunity.symbol}
                                                                                        <span className="pair-tf">{chartTimeframe}</span>
                                                                                    </div>
                                                                                    <div className="pair-strat">{getStrategyDisplayName(opportunity)}</div>
                                                                                    {opportunity.strategy_description ? (
                                                                                        <div className="pair-strat-desc">{opportunity.strategy_description}</div>
                                                                                    ) : null}
                                                                                </div>
                                                                            </div>
                                                                    </td>
                                                                    <td>
                                                                        <span
                                                                            className={`status-pill ${resolved.section}`}
                                                                            data-testid={`monitor-row-signal-${symbolTestKey(opportunity.symbol)}`}
                                                                        >
                                                                            {resolved.visual.badgeText}
                                                                        </span>
                                                                    </td>
                                                                    <td className="num lg">{formatPrice(opportunity.last_price)}</td>
                                                                    {showTechnicalColumns ? <td>{formatPercent(opportunity.distance_to_next_status)}</td> : null}
                                                                    {showTechnicalColumns ? (
                                                                        <td className="col-spark">
                                                                            {showSparkline ? (
                                                                                    <svg
                                                                                        className="spark"
                                                                                        viewBox="0 0 80 22"
                                                                                        preserveAspectRatio="none"
                                                                                        aria-hidden
                                                                                    >
                                                                                        <path d={spark.area} fill={sparkColor} fillOpacity={0.12} />
                                                                                        <path
                                                                                            d={spark.line}
                                                                                            fill="none"
                                                                                            stroke={sparkColor}
                                                                                            strokeWidth={1.4}
                                                                                            strokeLinejoin="round"
                                                                                            strokeLinecap="round"
                                                                                        />
                                                                                        <circle cx={spark.dot.x} cy={spark.dot.y} r={1.6} fill={sparkColor} />
                                                                                    </svg>
                                                                            ) : (
                                                                                '-'
                                                                            )}
                                                                        </td>
                                                                    ) : null}
                                                                    <td>
                                                                        <div className="risk-bar">
                                                                            <div
                                                                                className="risk-fill"
                                                                                style={{
                                                                                    width: `${Math.min(100, Math.max(0, riskStop * 7))}%`,
                                                                                }}
                                                                            />
                                                                        </div>
                                                                        <div className="risk-meta">
                                                                            <span>{formatPercent(opportunity.distance_to_stop_pct)}</span>
                                                                            <span>stop</span>
                                                                        </div>
                                                                    </td>
                                                                    <td className="col-tags">
                                                                        <div className="tags">
                                                                            <span className="tag portfolio">{inPortfolio ? '● Carteira' : '○ Carteira'}</span>
                                                                            {getTierStars(opportunity.tier) ? (
                                                                                <span className="tag strategy" data-testid={`tier-stars-${symbolTestKey(opportunity.symbol)}`}>
                                                                                    {getTierStars(opportunity.tier)}
                                                                                </span>
                                                                            ) : null}
                                                                            {showTechnicalColumns ? <span className="tag strategy">▲ Strategy</span> : null}
                                                                        </div>
                                                                    </td>
                                                                    <td className="actions-cell">
                                                                        <div className="row-actions" aria-label={`Ações ${opportunity.symbol}`}>
                                                                        <button
                                                                            type="button"
                                                                            className="row-action"
                                                                            title="Abrir Gráfico"
                                                                            aria-label={`Abrir Gráfico ${opportunity.symbol}`}
                                                                            onClick={(event) => {
                                                                                event.stopPropagation();
                                                                                void handleOpenChart(opportunity, 'chart');
                                                                            }}
                                                                            disabled={openingChartOpportunityId === getOpeningChartKey(opportunity)}
                                                                        >
                                                                            <LineChart className="h-4 w-4" />
                                                                            <span>Abrir Gráfico</span>
                                                                        </button>
                                                                        <button
                                                                            type="button"
                                                                            className="row-action row-action-primary"
                                                                            title="Ver Trades"
                                                                            aria-label={`Ver Trades ${opportunity.symbol}`}
                                                                            onClick={(event) => {
                                                                                event.stopPropagation();
                                                                                void handleOpenChart(opportunity, 'trades');
                                                                            }}
                                                                            disabled={openingChartOpportunityId === getOpeningChartKey(opportunity)}
                                                                        >
                                                                            <ListChecks className="h-4 w-4" />
                                                                            <span>Ver Trades</span>
                                                                        </button>
                                                                        </div>
                                                                    </td>
                                                                </tr>
                                                                {expanded ? (
                                                                    <tr
                                                                        className="detail-row"
                                                                        data-detail={rowKey}
                                                                        data-expanded={expanded}
                                                                        aria-hidden={false}
                                                                    >
                                                                        <td colSpan={detailColSpan}>
                                                                            <OpportunityCard
                                                                                opportunity={opportunity}
                                                                                preference={{
                                                                                    ...pref,
                                                                                    in_portfolio: inPortfolio,
                                                                                }}
                                                                                isPortfolioDerived={Boolean(derived?.active)}
                                                                                portfolioStatusMessage={derived?.message}
                                                                                portfolioStatusTone={derived?.tone}
                                                                                resolvedSignal={resolved}
                                                                                isSavingPreference={Boolean(savingSymbols[opportunity.symbol])}
                                                                                isOpeningChart={openingChartOpportunityId === getOpeningChartKey(opportunity)}
                                                                                isAdmin={showTechnicalColumns}
                                                                                onToggleInPortfolio={handleToggleInPortfolio}
                                                                                onToggleCardMode={handleToggleCardMode}
                                                                                onToggleTimeframe={handleToggleTimeframe}
                                                                                onOpenChart={handleOpenChart}
                                                                            />
                                                                        </td>
                                                                    </tr>
                                                                ) : null}
                                                            </React.Fragment>
                                                        );
                                                    })}
                                                </tbody>
                                            </table>
                                        </div>
                                    </section>
                                );
                            })
                        )}
                    </main>
                </section>
            </div>

            {activeChart ? (
                <ChartModal
                    symbol={activeChart.opportunity.symbol}
                    opportunity={activeChart.opportunity}
                    initialCandles={activeChart.initialCandles}
                    initialTimeframe={activeChart.initialTimeframe}
                    viewMode={activeChart.viewMode}
                    onClose={() => setActiveChart(null)}
                />
            ) : null}
        </div>
    );
};
