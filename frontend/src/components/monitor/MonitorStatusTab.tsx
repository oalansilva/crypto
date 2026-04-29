import React, { useEffect, useMemo, useState } from 'react';
import { getOpportunityAssetType, getOpportunityBaseAsset, isDerivedPortfolioRuleActive, type Opportunity, type MonitorCardMode, type MonitorPreference, type MonitorPriceTimeframe, type MonitorTheme } from '@/components/monitor/types';
import { OpportunityCard } from '@/components/monitor/OpportunityCard';
import { ChartModal } from '@/components/monitor/ChartModal';
import { Button } from '@/components/ui/Button';
import { Card, CardContent, CardHeader } from '@/components/ui/Card';
import { RefreshCw, ArrowUpDown, ChevronDown } from 'lucide-react';
import { useToast } from "@/components/ui/use-toast";
import { useInfiniteScroll } from '@/hooks/useInfiniteScroll';
import { API_BASE_URL } from '@/lib/apiBase';
import { authFetch } from '@/lib/authFetch';
import type { MarketCandle } from './MiniCandlesChart';
import { fetchMarketCandles, toChartTimeframe, type ChartTimeframe } from './chartData';
import { resolveOpportunitySignal } from './signalResolution';

type SortOption = 'distance' | 'tier_distance' | 'symbol';
type TierFilter = 'all' | '1_2' | '1' | '2' | '3' | 'none';
type ListFilter = 'in_portfolio' | 'all';
type AssetTypeFilter = 'all' | 'crypto' | 'stocks';
type WalletSyncState = 'idle' | 'loading' | 'ready' | 'empty' | 'error';

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

const DEFAULT_PREFERENCE: MonitorPreference = {
    in_portfolio: false,
    card_mode: 'price',
    price_timeframe: '1d',
    theme: 'dark-green',
};

const DEFAULT_THEME: MonitorTheme = 'dark-green';
const BINANCE_MONITOR_PORTFOLIO_MIN_USD = 1;

export const MonitorStatusTab: React.FC = () => {
    const [opportunities, setOpportunities] = useState<Opportunity[]>([]);
    const [loading, setLoading] = useState(false);
    const [openingChartSymbol, setOpeningChartSymbol] = useState<string | null>(null);
    const [activeChart, setActiveChart] = useState<{
        opportunity: Opportunity;
        initialCandles: MarketCandle[];
        initialTimeframe: ChartTimeframe;
    } | null>(null);
    const [sortBy, setSortBy] = useState<SortOption>('tier_distance');
    const [tierFilter, setTierFilter] = useState<TierFilter>('all');
    const [listFilter, setListFilter] = useState<ListFilter>('in_portfolio');
    const [assetTypeFilter, setAssetTypeFilter] = useState<AssetTypeFilter>('all');
    const [lastUpdated, setLastUpdated] = useState<Date | null>(null);
    const [preferences, setPreferences] = useState<Record<string, MonitorPreference>>({});
    const [binanceConfigured, setBinanceConfigured] = useState(false);
    const [walletHoldingsByAsset, setWalletHoldingsByAsset] = useState<Record<string, number>>({});
    const [walletSyncState, setWalletSyncState] = useState<WalletSyncState>('idle');
    const [walletSyncMessage, setWalletSyncMessage] = useState<string | null>(null);
    const [savingSymbols, setSavingSymbols] = useState<Record<string, boolean>>({});
    const { toast } = useToast();

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
                throw new Error(String(payload?.detail || `Failed to load Binance wallet (${response.status})`));
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
                throw new Error(`Failed to load monitor preferences (${preferencesResponse.status})`);
            }

            const preferencesPayload = await preferencesResponse.json();
            if (typeof preferencesPayload === 'object' && preferencesPayload) {
                const normalized: Record<string, MonitorPreference> = {};
                for (const [symbol, raw] of Object.entries(preferencesPayload as Record<string, any>)) {
                    normalized[symbol] = {
                        in_portfolio: Boolean(raw?.in_portfolio),
                        card_mode: raw?.card_mode === 'strategy' ? 'strategy' : 'price',
                        price_timeframe: raw?.price_timeframe === '15m'
                            || raw?.price_timeframe === '1h'
                            || raw?.price_timeframe === '4h'
                            || raw?.price_timeframe === '1d'
                            ? raw.price_timeframe
                            : '1d',
                        theme: raw?.theme === 'black' ? 'black' : 'dark-green',
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
                throw new Error(String(payload?.detail || `Failed to load Binance credential status (${credentialsResponse.status})`));
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
            if (tierParam === 'all') {
                apiTier = 'all';
            } else if (tierParam === '1_2') {
                apiTier = '1,2';
            } else if (tierParam === 'none') {
                apiTier = 'none';
            } else {
                apiTier = tierParam;
            }

            const baseUrl = import.meta.env.VITE_API_URL || "/api";
            const refreshParam = options?.refresh ? '&refresh=true' : '';
            const url = `${baseUrl}/opportunities/?tier=${encodeURIComponent(apiTier)}${refreshParam}`;
            const response = await authFetch(url);
            if (!response.ok) throw new Error('Failed to fetch opportunities');
            const data = await response.json();
            setOpportunities(data);
            setLastUpdated(new Date());

            toast({
                title: "Atualizado",
                description: `${data.length} estratégias analisadas`,
            });
        } catch (error) {
            console.error(error);
            toast({
                title: "Erro",
                description: "Não foi possível carregar. O backend está rodando?",
                variant: "destructive"
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
            theme: patch.theme ?? prev.theme ?? DEFAULT_THEME,
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
                throw new Error(String(payload?.detail || `Failed to save preference (${response.status})`));
            }

            setPreferences((current) => ({
                ...current,
                [symbol]: {
                    in_portfolio: Boolean(payload?.in_portfolio),
                    card_mode: payload?.card_mode === 'strategy' ? 'strategy' : 'price',
                    price_timeframe: payload?.price_timeframe === '15m'
                        || payload?.price_timeframe === '1h'
                        || payload?.price_timeframe === '4h'
                        || payload?.price_timeframe === '1d'
                        ? payload.price_timeframe
                        : '1d',
                    theme: payload?.theme === 'black' ? 'black' : 'dark-green',
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

    const handleChangePriceTimeframe = (symbol: string, nextTimeframe: MonitorPriceTimeframe) => {
        void persistPreference(symbol, { price_timeframe: nextTimeframe });
    };

    const resolveChartTimeframe = (opportunity: Opportunity): ChartTimeframe => {
        const preference = getPreference(opportunity.symbol).price_timeframe;
        const requested = toChartTimeframe(preference || opportunity.timeframe);
        return getOpportunityAssetType(opportunity) === 'stock' ? '1d' : requested;
    };

    const handleOpenChart = async (opportunity: Opportunity) => {
        const initialTimeframe = resolveChartTimeframe(opportunity);

        setOpeningChartSymbol(opportunity.symbol);

        try {
            const rows = await fetchMarketCandles(opportunity.symbol, initialTimeframe);
            if (rows.length === 0) {
                toast({
                    title: 'Chart unavailable',
                    description: `No candle data available for ${opportunity.symbol} on ${initialTimeframe}.`,
                    variant: 'destructive',
                });
                return;
            }

            setActiveChart({
                opportunity,
                initialCandles: rows,
                initialTimeframe,
            });
        } catch (error) {
            toast({
                title: 'Chart unavailable',
                description: error instanceof Error ? error.message : 'Failed to load chart data.',
                variant: 'destructive',
            });
        } finally {
            setOpeningChartSymbol((current) => current === opportunity.symbol ? null : current);
        }
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

    const filteredOpportunities = useMemo(() => {
        const afterAssetType = sortedOpportunities.filter((opp) => {
            if (!String(opp.symbol || '').trim()) return false;
            const assetType = getOpportunityAssetType(opp);
            if (assetTypeFilter === 'crypto') return assetType === 'crypto';
            if (assetTypeFilter === 'stocks') return assetType === 'stock';
            return true;
        });

        if (listFilter === 'all') {
            return afterAssetType;
        }
        return afterAssetType.filter((opp) => portfolioStatusBySymbol[opp.symbol]?.inPortfolio === true);
    }, [assetTypeFilter, listFilter, portfolioStatusBySymbol, sortedOpportunities]);

    const resolvedSections = useMemo(
        () => filteredOpportunities.map((opp) => {
            const preference = preferences[opp.symbol] ?? DEFAULT_PREFERENCE;
            const effectiveTimeframe: MonitorPriceTimeframe = getOpportunityAssetType(opp) === 'crypto' ? preference.price_timeframe : '1d';
            return {
                opportunity: opp,
                resolved: resolveOpportunitySignal(opp, { selectedTimeframe: effectiveTimeframe }),
            };
        }),
        [filteredOpportunities, preferences],
    );

    const holding = resolvedSections.filter(({ resolved }) => resolved.section === 'hold').map(({ opportunity }) => opportunity);
    const exited = resolvedSections.filter(({ resolved }) => resolved.section === 'exit').map(({ opportunity }) => opportunity);
    const waiting = resolvedSections.filter(({ resolved }) => resolved.section === 'wait').map(({ opportunity }) => opportunity);

    type SectionKey = 'hold' | 'exit' | 'wait';
    const orderedCards = useMemo(() => {
        const withSection = (arr: Opportunity[], section: SectionKey) =>
            arr.map((opp) => ({ opp, section }));
        return [
            ...withSection(holding, 'hold'),
            ...withSection(exited, 'exit'),
            ...withSection(waiting, 'wait'),
        ];
    }, [holding, exited, waiting]);

    const { visibleItems, hasMore, sentinelRef } = useInfiniteScroll(orderedCards, 12, 12);

    const visibleGroups = useMemo(() => {
        const g: { section: SectionKey; cards: Opportunity[] }[] = [];
        for (const { opp, section } of visibleItems) {
            if (g.length > 0 && g[g.length - 1].section === section)
                g[g.length - 1].cards.push(opp);
            else
                g.push({ section, cards: [opp] });
        }
        return g;
    }, [visibleItems]);

    const SECTION_CONFIG: Record<SectionKey, { title: string; subtitle: string; dotClass: string; h2Class: string; badgeClass: string; description: string }> = {
        hold: {
            title: 'Estado HOLD',
            subtitle: 'Posição ativa',
            dotClass: 'bg-green-500',
            h2Class: 'text-green-600',
            badgeClass: 'bg-green-500/10 text-green-600',
            description: 'Padrão atual de decisão: posição ativa com gestão em acompanhamento contínuo.',
        },
        exit: {
            title: 'Estado EXIT',
            subtitle: 'Sem posição ativa',
            dotClass: 'bg-sky-500',
            h2Class: 'text-sky-600',
            badgeClass: 'bg-sky-500/10 text-sky-600',
            description: 'Condição de saída detectada; monitorando nova oportunidade com base em contexto técnico.',
        },
        wait: {
            title: 'Estado WAIT',
            subtitle: 'Sem posição ativa',
            dotClass: 'bg-gray-400',
            h2Class: 'text-gray-500',
            badgeClass: 'bg-gray-500/10 text-gray-600',
            description: 'Contexto técnico em monitoramento sem recomendação ativa de compra/venda.',
        },
    };

    const noResultsForInPortfolio = !loading && opportunities.length > 0 && filteredOpportunities.length === 0 && listFilter === 'in_portfolio';

    const theme: MonitorTheme = (
        preferences['__global__']?.theme ?? DEFAULT_THEME
    );

    return (
        <div
            className={`min-h-screen monitor-theme monitor-theme--${theme} py-6`}
            data-testid="monitor-status-tab"
        >
            <div className="container mx-auto p-6 space-y-8">

            <div className="flex flex-col gap-4">
                <div className="flex justify-between items-center">
                    <div className="space-y-1">
                        <h1 className="text-3xl font-bold tracking-tight">Opportunity Board</h1>
                        <p className="text-muted-foreground">
                            Monitor your favorite strategies.
                        </p>
                        {lastUpdated && (
                            <p className="text-xs text-muted-foreground">
                                Last updated: {lastUpdated.toLocaleTimeString()}
                            </p>
                        )}
                    </div>
                    <div className="flex gap-2 items-center">
                        <button
                            type="button"
                            className="text-sm border rounded px-2 py-1.5 bg-[var(--monitor-surface)] text-[var(--monitor-text)] border-[var(--monitor-border)]"
                            onClick={() => {
                                const next: MonitorTheme = theme === 'dark-green' ? 'black' : 'dark-green';
                                void persistPreference('__global__', { theme: next });
                            }}
                            data-testid="monitor-theme-toggle"
                            title="Toggle Monitor theme"
                        >
                            Theme: {theme}
                        </button>

                        <Button
                            variant="secondary"
                            onClick={() => {
                                void Promise.all([fetchOpportunities(undefined, { refresh: true }), fetchMonitorContext()]);
                            }}
                            disabled={loading}
                        >
                            <RefreshCw className={`mr-2 h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
                            Refresh
                        </Button>
                    </div>
                </div>

                <div className="flex items-center gap-4 flex-wrap">
                    <div className="flex items-center gap-2" role="group" aria-label="Monitor list filter">
                        <span className="text-sm font-medium">List:</span>
                        <button
                            type="button"
                            className={`text-sm border rounded px-2 py-1.5 ${listFilter === 'in_portfolio' ? 'bg-blue-600 text-white border-blue-600' : 'bg-[var(--monitor-surface)] text-[var(--monitor-text)] border-[var(--monitor-border)]'}`}
                            onClick={() => setListFilter('in_portfolio')}
                            data-testid="monitor-filter-in-portfolio"
                        >
                            In Portfolio
                        </button>
                        <button
                            type="button"
                            className={`text-sm border rounded px-2 py-1.5 ${listFilter === 'all' ? 'bg-blue-600 text-white border-blue-600' : 'bg-[var(--monitor-surface)] text-[var(--monitor-text)] border-[var(--monitor-border)]'}`}
                            onClick={() => setListFilter('all')}
                            data-testid="monitor-filter-all"
                        >
                            All
                        </button>
                    </div>

                    <div className="flex items-center gap-2">
                        <span className="text-sm font-medium">Asset Type:</span>
                        <div className="relative">
                            <select
                                value={assetTypeFilter}
                                onChange={(e) => setAssetTypeFilter(e.target.value as AssetTypeFilter)}
                                className="text-sm border rounded pl-2 pr-8 py-1.5 bg-[var(--monitor-surface)] text-[var(--monitor-text)] border-[var(--monitor-border)] appearance-none cursor-pointer focus:ring-1 focus:ring-primary focus:border-primary"
                                title="Filtrar por tipo de ativo"
                                data-testid="monitor-filter-asset-type"
                            >
                                <option value="all" className="bg-gray-900">Asset Type: All</option>
                                <option value="crypto" className="bg-gray-900">Asset Type: Crypto</option>
                                <option value="stocks" className="bg-gray-900">Asset Type: Stocks</option>
                            </select>
                            <ChevronDown className="absolute right-2 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none" />
                        </div>
                    </div>

                    <div className="flex items-center gap-2">
                        <span className="text-sm font-medium">Tier:</span>
                        <div className="relative">
                            <select
                                value={tierFilter}
                                onChange={(e) => setTierFilter(e.target.value as TierFilter)}
                                className="text-sm border rounded pl-2 pr-8 py-1.5 bg-[var(--monitor-surface)] text-[var(--monitor-text)] border-[var(--monitor-border)] appearance-none cursor-pointer focus:ring-1 focus:ring-primary focus:border-primary"
                                title="Filtrar por tier"
                            >
                                <option value="all" className="bg-gray-900">Tier: All</option>
                                <option value="1" className="bg-gray-900">Tier 1 – Core</option>
                                <option value="2" className="bg-gray-900">Tier 2 – Complementares</option>
                                <option value="3" className="bg-gray-900">Tier 3</option>
                                <option value="1_2" className="bg-gray-900">Tier 1 + Tier 2</option>
                                <option value="none" className="bg-gray-900">Sem tier</option>
                            </select>
                            <ChevronDown className="absolute right-2 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none" />
                        </div>
                    </div>

                    <div className="flex items-center gap-2">
                        <ArrowUpDown className="w-4 h-4 text-muted-foreground" />
                        <span className="text-sm font-medium">Sort:</span>
                        <div className="relative">
                            <select
                                value={sortBy}
                                onChange={(e) => setSortBy(e.target.value as SortOption)}
                                className="text-sm border rounded pl-2 pr-8 py-1.5 bg-[var(--monitor-surface)] text-[var(--monitor-text)] border-[var(--monitor-border)] appearance-none cursor-pointer focus:ring-1 focus:ring-primary focus:border-primary"
                            >
                                <option value="tier_distance" className="bg-gray-900">Tier + Distância</option>
                                <option value="distance" className="bg-gray-900">Distância (mais próximo)</option>
                                <option value="symbol" className="bg-gray-900">Símbolo</option>
                            </select>
                            <ChevronDown className="absolute right-2 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none" />
                        </div>
                    </div>
                </div>
            </div>

            {loading && opportunities.length === 0 ? (
                <div className="space-y-4">
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
                        {[1, 2, 3, 4].map(i => (
                            <Card key={i} className="border-l-4 border-l-gray-300 animate-pulse">
                                <CardHeader className="space-y-2">
                                    <div className="h-5 bg-gray-200 rounded w-3/4"></div>
                                    <div className="h-4 bg-gray-200 rounded w-1/2"></div>
                                </CardHeader>
                                <CardContent className="space-y-3">
                                    <div className="h-4 bg-gray-200 rounded"></div>
                                    <div className="h-4 bg-gray-200 rounded"></div>
                                    <div className="h-12 bg-gray-200 rounded"></div>
                                </CardContent>
                            </Card>
                        ))}
                    </div>
                </div>
            ) : opportunities.length === 0 && !loading ? (
                <div className="text-center py-20 space-y-4">
                    <p className="text-muted-foreground">No favorites found. Star some strategies in the Backtester to see them here!</p>
                    <Button variant="secondary" onClick={() => window.location.href = '/'}>
                        Go to Backtester
                    </Button>
                </div>
            ) : noResultsForInPortfolio ? (
                <div className="text-center py-16 space-y-4" data-testid="monitor-empty-in-portfolio">
                    <p className="text-muted-foreground">No symbols are marked as In Portfolio yet.</p>
                    <Button variant="secondary" onClick={() => setListFilter('all')}>Show All Symbols</Button>
                </div>
            ) : (
                <div className="space-y-10">
                    {visibleGroups.map(({ section, cards }) => {
                        const cfg = SECTION_CONFIG[section];
                        const total = { hold: holding.length, exit: exited.length, wait: waiting.length }[section];
                        return (
                            <section key={section} className="space-y-4">
                                <h2 className={`text-xl font-semibold flex items-center gap-2 ${cfg.h2Class}`}>
                                    <span className={`w-3 h-3 ${cfg.dotClass} rounded-full`}></span>
                                    {cfg.title} ({total})
                                    <span className={`${cfg.badgeClass} text-xs px-2 py-0.5 rounded-full ml-2`}>
                                        {cfg.subtitle}
                                    </span>
                                </h2>
                                <p className="text-sm text-muted-foreground ml-5">
                                    {cfg.description}
                                </p>
                                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
                                    {cards.map((opp) => (
                                        <OpportunityCard
                                            key={opp.id}
                                            opportunity={opp}
                                            preference={{
                                                ...getPreference(opp.symbol),
                                                in_portfolio: portfolioStatusBySymbol[opp.symbol]?.inPortfolio ?? getPreference(opp.symbol).in_portfolio,
                                            }}
                                            isPortfolioDerived={Boolean(portfolioStatusBySymbol[opp.symbol]?.active)}
                                            portfolioStatusMessage={portfolioStatusBySymbol[opp.symbol]?.message}
                                            portfolioStatusTone={portfolioStatusBySymbol[opp.symbol]?.tone}
                                            isSavingPreference={Boolean(savingSymbols[opp.symbol])}
                                            isOpeningChart={openingChartSymbol === opp.symbol}
                                            onToggleInPortfolio={handleToggleInPortfolio}
                                            onToggleCardMode={handleToggleCardMode}
                                            onChangePriceTimeframe={handleChangePriceTimeframe}
                                            onOpenChart={handleOpenChart}
                                        />
                                    ))}
                                </div>
                            </section>
                        );
                    })}
                    {hasMore && (
                        <div ref={sentinelRef} className="flex justify-center py-8" aria-hidden="true">
                            <span className="text-sm text-muted-foreground animate-pulse">Carregando mais…</span>
                        </div>
                    )}
                </div>
            )}
            {activeChart ? (
                <ChartModal
                    symbol={activeChart.opportunity.symbol}
                    opportunity={activeChart.opportunity}
                    initialCandles={activeChart.initialCandles}
                    initialTimeframe={activeChart.initialTimeframe}
                    onClose={() => setActiveChart(null)}
                />
            ) : null}
            </div>
        </div>
    );
};
