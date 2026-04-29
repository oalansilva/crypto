import React, { useEffect, useMemo, useState } from 'react';
import {
    getOpportunityAssetType,
    getOpportunityBaseAsset,
    isDerivedPortfolioRuleActive,
    type Opportunity,
    type MonitorCardMode,
    type MonitorPreference,
    type MonitorPriceTimeframe,
    type MonitorTheme,
} from '@/components/monitor/types';
import { OpportunityCard } from '@/components/monitor/OpportunityCard';
import { ChartModal } from '@/components/monitor/ChartModal';
import { Button } from '@/components/ui/Button';
import { RefreshCw, ChevronDown, ArrowUpDown } from 'lucide-react';
import { useToast } from '@/components/ui/use-toast';
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
type SectionKey = 'hold' | 'wait' | 'exit';

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

type RowMode = {
    symbol: string;
    expanded: boolean;
};

type SectionRecord = {
    title: string;
    label: string;
    dotClass: 'monitor-dot--hold' | 'monitor-dot--wait' | 'monitor-dot--exit';
    badgeClass: string;
    countClass: string;
    description: string;
};

type ResolvedSectionRow = {
    opportunity: Opportunity;
    resolved: ReturnType<typeof resolveOpportunitySignal>;
};

const DEFAULT_PREFERENCE: MonitorPreference = {
    in_portfolio: false,
    card_mode: 'price',
    price_timeframe: '1d',
    theme: 'dark-green',
};

const DEFAULT_THEME: MonitorTheme = 'dark-green';
const BINANCE_MONITOR_PORTFOLIO_MIN_USD = 1;
const ROWS_WITH_EXPANSION_INITIAL: RowMode[] = [];

const SECTION_DOT_COLOR: Record<SectionKey, string> = {
    hold: 'var(--accent-success)',
    wait: 'var(--accent-warning)',
    exit: 'var(--monitor-primary)',
};

const SectionConfig: Record<SectionKey, SectionRecord> = {
    hold: {
        title: 'HOLD',
        label: 'Posição ativa',
        dotClass: 'monitor-dot--hold',
        badgeClass: 'bg-emerald-500/20 text-emerald-300 border border-emerald-400/40',
        countClass: 'text-emerald-300',
        description: 'Sinais com decisão favorável e gestão ativa.',
    },
    wait: {
        title: 'WAIT',
        label: 'Aguardando',
        dotClass: 'monitor-dot--wait',
        badgeClass: 'bg-slate-400/20 text-slate-200 border border-slate-400/40',
        countClass: 'text-slate-300',
        description: 'Aguardando confirmação para entrada ou saída.',
    },
    exit: {
        title: 'EXIT',
        label: 'Em observação',
        dotClass: 'monitor-dot--exit',
        badgeClass: 'bg-sky-500/20 text-sky-200 border border-sky-400/40',
        countClass: 'text-sky-300',
        description: 'Condição de saída detectada para novo monitoramento.',
    },
};

const SECTION_ORDER: SectionKey[] = ['hold', 'wait', 'exit'];

const getDistanceLabel = (distance: number | null | undefined): string => {
    if (distance === null || distance === undefined) return '-';
    return `${distance.toFixed(2)}%`;
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
    const [expandedRows, setExpandedRows] = useState<Record<string, boolean>>(
        Object.fromEntries(ROWS_WITH_EXPANSION_INITIAL.map((row) => [row.symbol, row.expanded]))
    );
    const { toast } = useToast();

    const getPreference = (symbol: string): MonitorPreference => {
        return preferences[symbol] ?? DEFAULT_PREFERENCE;
    };

    const getActiveRowCount = (sectionRows: Record<SectionKey, ResolvedSectionRow[]>, sectionKey: SectionKey) => {
        return sectionRows[sectionKey]?.length ?? 0;
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

            const baseUrl = import.meta.env.VITE_API_URL || '/api';
            const refreshParam = options?.refresh ? '&refresh=true' : '';
            const url = `${baseUrl}/opportunities/?tier=${encodeURIComponent(apiTier)}${refreshParam}`;
            const response = await authFetch(url);
            if (!response.ok) throw new Error('Failed to fetch opportunities');
            const data = await response.json();
            setOpportunities(data);
            setLastUpdated(new Date());

            toast({
                title: 'Atualizado',
                description: `${data.length} estratégias analisadas`,
            });
        } catch (error) {
            console.error(error);
            toast({
                title: 'Erro',
                description: 'Não foi possível carregar. O backend está rodando?',
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
        const preference = getPreference(opportunity.symbol);
        const requested = toChartTimeframe(preference.price_timeframe || opportunity.timeframe);
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
            setOpeningChartSymbol((current) => (current === opportunity.symbol ? null : current));
        }
    };

    const handleToggleRow = (symbol: string) => {
        setExpandedRows((current) => ({
            ...current,
            [symbol]: !(current[symbol] ?? true),
        }));
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

    const resolvedSections = useMemo(() => {
        const groups: Record<SectionKey, ResolvedSectionRow[]> = {
            hold: [],
            wait: [],
            exit: [],
        };

        for (const opportunity of filteredOpportunities) {
            const preference = preferences[opportunity.symbol] ?? DEFAULT_PREFERENCE;
            const effectiveTimeframe: MonitorPriceTimeframe =
                getOpportunityAssetType(opportunity) === 'crypto' ? preference.price_timeframe : '1d';
            const resolved = resolveOpportunitySignal(opportunity, { selectedTimeframe: effectiveTimeframe });
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
    }, [filteredOpportunities, preferences]);

    const sectionCountByType = useMemo(() => ({
        hold: resolvedSections.hold.length,
        wait: resolvedSections.wait.length,
        exit: resolvedSections.exit.length,
    }), [resolvedSections]);

    const inPortfolioCount = useMemo(() => {
        return Object.values(portfolioStatusBySymbol).filter((item) => item.inPortfolio).length;
    }, [portfolioStatusBySymbol]);

    const noResultsForInPortfolio = !loading && opportunities.length > 0 && filteredOpportunities.length === 0 && listFilter === 'in_portfolio';

    const totalKpi = {
        active: opportunities.length,
        visible: filteredOpportunities.length,
        inPortfolio: inPortfolioCount,
    };

    const theme: MonitorTheme = preferences['__global__']?.theme ?? DEFAULT_THEME;

    return (
        <div className={`min-h-screen monitor-theme monitor-theme--${theme} py-6`} data-testid="monitor-status-tab">
            <div className="container mx-auto monitor-shell p-6 space-y-6">
                <header className="monitor-board-header">
                    <div className="space-y-2">
                        <p className="text-xs uppercase tracking-[0.14em] text-[var(--monitor-muted)]">Crypto / Monitor</p>
                        <h1 className="text-3xl font-bold text-[var(--monitor-text)]">Monitor de sinais</h1>
                        {lastUpdated ? (
                            <p className="text-xs text-[var(--monitor-muted)]">
                                Última atualização: {lastUpdated.toLocaleTimeString('pt-BR')}
                            </p>
                        ) : null}
                        <p className="text-sm text-[var(--monitor-muted)]">
                            Filtro por carteira, seção e timeframe em tabela para leitura rápida.
                        </p>
                    </div>

                    <div className="monitor-actions-row">
                        <button
                            type="button"
                            className="monitor-btn"
                            onClick={() => {
                                const next: MonitorTheme = theme === 'dark-green' ? 'black' : 'dark-green';
                                void persistPreference('__global__', { theme: next });
                            }}
                            data-testid="monitor-theme-toggle"
                            title="Alternar tema do monitor"
                        >
                            Tema: {theme}
                        </button>

                        <Button
                            variant="secondary"
                            onClick={() => {
                                void Promise.all([fetchOpportunities(undefined, { refresh: true }), fetchMonitorContext()]);
                            }}
                            disabled={loading}
                        >
                            <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
                            Atualizar
                        </Button>
                    </div>
                </header>

                <section className="monitor-layout-grid" aria-label="Painel do monitor">
                    <aside className="monitor-side-panel">
                        <header className="monitor-side-header">
                            <h2 className="text-sm font-semibold text-[var(--monitor-text)]">Resumo</h2>
                            <p className="text-xs text-[var(--monitor-muted)]">Indicadores rápidos</p>
                        </header>

                        <div className="monitor-kpis">
                            <div className="monitor-kpi-card">
                                <span className="monitor-kpi-label">Total</span>
                                <span className="monitor-kpi-value">{totalKpi.active}</span>
                            </div>
                            <div className="monitor-kpi-card">
                                <span className="monitor-kpi-label">Visíveis</span>
                                <span className="monitor-kpi-value">{totalKpi.visible}</span>
                            </div>
                            <div className="monitor-kpi-card">
                                <span className="monitor-kpi-label">Em carteira</span>
                                <span className="monitor-kpi-value">{totalKpi.inPortfolio}</span>
                            </div>
                        </div>

                        <div className="monitor-kpi-card monitor-kpi-stack">
                            <span className="monitor-kpi-label">Estados</span>
                            <div className="monitor-state-list">
                                {SECTION_ORDER.map((section) => {
                                    const cfg = SectionConfig[section];
                                    return (
                                        <div key={section} className="monitor-state-item">
                                            <span className="monitor-state-dot" style={{ backgroundColor: SECTION_DOT_COLOR[section] }} />
                                            <span>{cfg.title}</span>
                                            <span className="ml-auto text-[var(--monitor-text)] font-semibold">{getActiveRowCount(resolvedSections, section)}</span>
                                        </div>
                                    );
                                })}
                            </div>
                        </div>

                        <div className="monitor-kpi-card monitor-kpi-stack">
                            <span className="monitor-kpi-label">Carteira Binance</span>
                            <span className="text-sm text-[var(--monitor-muted)]">
                                {walletSyncState === 'idle' && 'Não configurada para sincronização'}
                                {walletSyncState === 'loading' && 'Sincronizando ativos...'}
                                {walletSyncState === 'ready' && 'Sincronização ativa'}
                                {walletSyncState === 'empty' && 'Carteira sem ativo elegível'}
                                {walletSyncState === 'error' && 'Erro na sincronização'}
                            </span>
                            {walletSyncMessage ? <p className="monitor-guard-text">{walletSyncMessage}</p> : null}
                        </div>

                        <div className="monitor-kpi-card monitor-kpi-stack">
                            <span className="monitor-kpi-label">Ações</span>
                            <div className="flex flex-wrap gap-2">
                                <button
                                    type="button"
                                    className={`monitor-filter-chip ${listFilter === 'in_portfolio' ? 'monitor-filter-chip--active' : ''}`}
                                    onClick={() => setListFilter('in_portfolio')}
                                    data-testid="monitor-filter-in-portfolio"
                                >
                                    In Portfolio
                                </button>
                                <button
                                    type="button"
                                    className={`monitor-filter-chip ${listFilter === 'all' ? 'monitor-filter-chip--active' : ''}`}
                                    onClick={() => setListFilter('all')}
                                    data-testid="monitor-filter-all"
                                >
                                    All
                                </button>
                            </div>

                            <div className="monitor-control-group">
                                <label htmlFor="monitor-filter-asset-type" className="monitor-kpi-label">Ativo</label>
                                <select
                                    id="monitor-filter-asset-type"
                                    value={assetTypeFilter}
                                    onChange={(e) => setAssetTypeFilter(e.target.value as AssetTypeFilter)}
                                    className="monitor-select"
                                    data-testid="monitor-filter-asset-type"
                                >
                                    <option value="all">Todos</option>
                                    <option value="crypto">Crypto</option>
                                    <option value="stocks">Ações</option>
                                </select>
                            </div>

                            <div className="monitor-control-group">
                                <label htmlFor="monitor-tier-filter" className="monitor-kpi-label">Tier</label>
                                <select
                                    id="monitor-tier-filter"
                                    value={tierFilter}
                                    onChange={(e) => setTierFilter(e.target.value as TierFilter)}
                                    className="monitor-select"
                                >
                                    <option value="all">Todas</option>
                                    <option value="1">Tier 1</option>
                                    <option value="2">Tier 2</option>
                                    <option value="3">Tier 3</option>
                                    <option value="1_2">1 + 2</option>
                                    <option value="none">Sem tier</option>
                                </select>
                            </div>

                            <div className="monitor-control-group">
                                <div className="monitor-sort-label">
                                    <ArrowUpDown className="h-4 w-4" />
                                    <label htmlFor="monitor-sort-select">Ordenação</label>
                                </div>
                                <select
                                    id="monitor-sort-select"
                                    value={sortBy}
                                    onChange={(e) => setSortBy(e.target.value as SortOption)}
                                    className="monitor-select"
                                >
                                    <option value="tier_distance">Tier + Distância</option>
                                    <option value="distance">Distância</option>
                                    <option value="symbol">Símbolo</option>
                                </select>
                            </div>
                        </div>
                    </aside>

                    <main className="monitor-main-panel">
                        {loading && opportunities.length === 0 ? (
                            <div className="space-y-4">
                                {SECTION_ORDER.map((sectionKey) => {
                                    const cfg = SectionConfig[sectionKey];
                                    return (
                                        <section key={sectionKey} className="space-y-3 rounded-2xl border border-[var(--monitor-border)] bg-[var(--monitor-surface)] p-4">
                                            <div className="monitor-section-head">
                                                <div className="flex items-center gap-2">
                                                    <span className={`monitor-dot ${cfg.dotClass}`} />
                                                    <div>
                                                        <p className="monitor-section-title">{cfg.title}</p>
                                                        <p className="monitor-section-subtitle">{cfg.label}</p>
                                                    </div>
                                                </div>
                                                <span className="monitor-section-count">0</span>
                                            </div>
                                            <div className="h-28 animate-pulse rounded-xl bg-white/5" />
                                        </section>
                                    );
                                })}
                            </div>
                        ) : opportunities.length === 0 && !loading ? (
                            <section className="rounded-2xl border border-[var(--monitor-border)] bg-[var(--monitor-surface)] p-8 text-center space-y-4">
                                <p className="text-[var(--monitor-muted)]">Nenhum ativo favoritado ainda.</p>
                                <Button variant="secondary" onClick={() => window.location.href = '/' }>
                                    Ir para Backtester
                                </Button>
                            </section>
                        ) : noResultsForInPortfolio ? (
                            <section className="rounded-2xl border border-[var(--monitor-border)] bg-[var(--monitor-surface)] p-8 text-center space-y-4" data-testid="monitor-empty-in-portfolio">
                                <p className="text-[var(--monitor-muted)]">Nenhum ativo na lista portfolio.</p>
                                <Button variant="secondary" onClick={() => setListFilter('all')}>Mostrar todos</Button>
                            </section>
                        ) : (
                            <div className="space-y-6">
                                {SECTION_ORDER.map((sectionKey) => {
                                    const cfg = SectionConfig[sectionKey];
                                    const rows = resolvedSections[sectionKey];

                                    return (
                                        <section key={sectionKey} className="monitor-table-section">
                                            <header className="monitor-table-section-head">
                                                <div className="flex items-center gap-2">
                                                    <span className={`monitor-dot ${cfg.dotClass}`} />
                                                    <h3 className="text-lg font-semibold">{cfg.title}</h3>
                                                    <span className={`rounded-full border px-2.5 py-1 text-[10px] uppercase tracking-[0.12em] ${cfg.badgeClass}`}>
                                                        {cfg.label}
                                                    </span>
                                                </div>
                                                <div className={`text-sm font-medium ${cfg.countClass}`}>{rows.length}</div>
                                            </header>
                                            <p className="text-xs text-[var(--monitor-muted)]">{cfg.description}</p>

                                            {rows.length === 0 ? (
                                                <p className="monitor-empty-row">Sem registros nesta seção.</p>
                                            ) : (
                                                <div className="monitor-table-wrap">
                                                    <table className="monitor-table">
                                                        <thead>
                                                            <tr>
                                                                <th scope="col" className="w-[33%]">Sinal</th>
                                                                <th scope="col">Tier</th>
                                                                <th scope="col">Distância</th>
                                                                <th scope="col">Último preço</th>
                                                                <th scope="col">Status</th>
                                                                <th scope="col">Portfólio</th>
                                                                <th scope="col">Timeframe</th>
                                                                <th scope="col" />
                                                            </tr>
                                                        </thead>
                                                        <tbody>
                                                            {rows.map(({ opportunity, resolved }) => {
                                                                const pref = getPreference(opportunity.symbol);
                                                                const derived = portfolioStatusBySymbol[opportunity.symbol];
                                                                const inPortfolio = derived?.inPortfolio ?? pref.in_portfolio;
                                                                const expanded = expandedRows[opportunity.symbol] ?? true;

                                                                return (
                                                                    <React.Fragment key={opportunity.id}>
                                                                        <tr className="monitor-table-row">
                                                                            <td>
                                                                                <button
                                                                                    type="button"
                                                                                    onClick={() => handleToggleRow(opportunity.symbol)}
                                                                                    className="monitor-row-toggler"
                                                                                >
                                                                                    <ChevronDown
                                                                                        className={`h-4 w-4 transition-transform ${expanded ? 'rotate-180' : ''}`}
                                                                                    />
                                                                                    <span className="font-semibold text-[var(--monitor-text)]">{opportunity.symbol}</span>
                                                                                </button>
                                                                                <div className="monitor-row-subtitle">{opportunity.name || opportunity.template_name}</div>
                                                                            </td>
                                                                            <td>
                                                                                <span className="monitor-row-badge">
                                                                                    {opportunity.tier ? `Tier ${opportunity.tier}` : 'Sem tier'}
                                                                                </span>
                                                                            </td>
                                                                            <td>{getDistanceLabel(opportunity.distance_to_next_status)}</td>
                                                                            <td className="font-mono">{formatPrice(opportunity.last_price)}</td>
                                                                            <td>
                                                                                <span className={`monitor-row-badge ${resolved.isUncertain ? 'monitor-row-badge-warning' : 'monitor-row-badge-neutral'}`}>
                                                                                    {resolved.visual.badgeText}
                                                                                </span>
                                                                            </td>
                                                                            <td>
                                                                                <span className={`monitor-row-badge ${inPortfolio ? 'monitor-row-badge-success' : 'monitor-row-badge-danger'}`}>
                                                                                    {inPortfolio ? 'Sim' : 'Não'}
                                                                                </span>
                                                                            </td>
                                                                            <td>{getOpportunityAssetType(opportunity) === 'stock' ? '1d' : pref.price_timeframe}</td>
                                                                            <td className="text-right">
                                                                                <button
                                                                                    type="button"
                                                                                    onClick={() => handleOpenChart(opportunity)}
                                                                                    className="monitor-table-action"
                                                                                    disabled={openingChartSymbol === opportunity.symbol}
                                                                                >
                                                                                    {openingChartSymbol === opportunity.symbol ? 'Abrindo...' : 'Abrir gráfico'}
                                                                                </button>
                                                                            </td>
                                                                        </tr>
                                                                        {expanded ? (
                                                                            <tr>
                                                                                <td colSpan={8} className="monitor-row-expanded-cell">
                                                                                    <OpportunityCard
                                                                                        opportunity={opportunity}
                                                                                        preference={{
                                                                                            ...pref,
                                                                                            in_portfolio: inPortfolio,
                                                                                        }}
                                                                                        isPortfolioDerived={Boolean(derived?.active)}
                                                                                        portfolioStatusMessage={derived?.message}
                                                                                        portfolioStatusTone={derived?.tone}
                                                                                        isSavingPreference={Boolean(savingSymbols[opportunity.symbol])}
                                                                                        isOpeningChart={openingChartSymbol === opportunity.symbol}
                                                                                        onToggleInPortfolio={handleToggleInPortfolio}
                                                                                        onToggleCardMode={handleToggleCardMode}
                                                                                        onChangePriceTimeframe={handleChangePriceTimeframe}
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
                                            )}
                                        </section>
                                    );
                                })}
                            </div>
                        )}
                    </main>
                </section>

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
