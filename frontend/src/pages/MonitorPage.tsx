import React, { useEffect, useState, useMemo } from 'react';
import type { Opportunity } from '@/components/monitor/types';
import { OpportunityCard } from '@/components/monitor/OpportunityCard';
import { Button } from '@/components/ui/Button';
import { Card, CardContent, CardHeader } from '@/components/ui/Card';
import { RefreshCw, ArrowUpDown, ChevronDown } from 'lucide-react';
import { useToast } from "@/components/ui/use-toast";
import { useInfiniteScroll } from '@/hooks/useInfiniteScroll';

type SortOption = 'distance' | 'tier_distance' | 'symbol';
type TierFilter = 'all' | '1_2' | '1' | '2' | '3' | 'none';

export const MonitorPage: React.FC = () => {
    const [opportunities, setOpportunities] = useState<Opportunity[]>([]);
    const [loading, setLoading] = useState(false);
    const [sortBy, setSortBy] = useState<SortOption>('tier_distance');
    const [tierFilter, setTierFilter] = useState<TierFilter>('all');
    const [lastUpdated, setLastUpdated] = useState<Date | null>(null);
    const { toast } = useToast();

    const fetchOpportunities = async (tier?: TierFilter) => {
        setLoading(true);
        try {
            // Convert frontend tier filter to API query param
            const tierParam = tier || tierFilter;
            let apiTier: string;
            if (tierParam === 'all') {
                apiTier = 'all';
            } else if (tierParam === '1_2') {
                apiTier = '1,2';  // API expects comma-separated
            } else if (tierParam === 'none') {
                apiTier = 'none';
            } else {
                apiTier = tierParam;  // '1', '2', '3'
            }
            
            // Prefer relative "/api" so Vite proxy routes to backend even when accessing from outside the server.
            // Only use VITE_API_URL when explicitly set.
            const baseUrl = import.meta.env.VITE_API_URL || "/api";
            const url = `${baseUrl}/opportunities/?tier=${encodeURIComponent(apiTier)}`;
            const response = await fetch(url);
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

    // Fetch when page loads or tier filter changes
    useEffect(() => {
        fetchOpportunities(tierFilter);
    }, [tierFilter]);

    // Sort opportunities by selected criteria
    const sortedOpportunities = useMemo(() => {
        const sorted = [...opportunities].sort((a, b) => {
            if (sortBy === 'tier_distance') {
                // Tier + Distância: Tier 1 e 2 primeiro, depois por distância
                // HOLD sempre primeiro dentro de cada grupo de tier
                const tierA = a.tier ?? 999;
                const tierB = b.tier ?? 999;
                // Agrupar Tier 1 e 2 como "prioritários" (< 3), outros depois
                const priorityA = tierA <= 2 ? 0 : 1;
                const priorityB = tierB <= 2 ? 0 : 1;
                if (priorityA !== priorityB) {
                    return priorityA - priorityB;
                }
                // Dentro do mesmo grupo de prioridade, HOLD primeiro
                if (a.is_holding !== b.is_holding) {
                    return a.is_holding ? -1 : 1;
                }
                // Depois por tier específico (1 antes de 2)
                if (tierA !== tierB) {
                    return tierA - tierB;
                }
                // Depois por distância (mais próximo primeiro)
                const distA = a.distance_to_next_status ?? 999;
                const distB = b.distance_to_next_status ?? 999;
                if (distA !== distB) {
                    return distA - distB;
                }
                return a.symbol.localeCompare(b.symbol);
            } else if (sortBy === 'distance') {
                // Distância: HOLD primeiro, depois por distância
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

    // Separate opportunities by status, then apply tier filter
    // Dados já vêm filtrados por tier do backend
    const holding = sortedOpportunities.filter(o => o.is_holding);
    const stoppedOut = sortedOpportunities.filter(o => !o.is_holding && o.status === 'STOPPED_OUT');
    const missedEntry = sortedOpportunities.filter(o => !o.is_holding && o.status === 'MISSED_ENTRY');
    const waiting = sortedOpportunities.filter(o => !o.is_holding && o.status !== 'STOPPED_OUT' && o.status !== 'MISSED_ENTRY');

    // Lista ordenada para paginação infinita: holding → stopped → missed → waiting
    type SectionKey = 'holding' | 'stoppedOut' | 'missedEntry' | 'waiting';
    const orderedCards = useMemo(() => {
        const withSection = (arr: Opportunity[], s: SectionKey) =>
            arr.map((opp) => ({ opp, section: s }));
        return [
            ...withSection(holding, 'holding'),
            ...withSection(stoppedOut, 'stoppedOut'),
            ...withSection(missedEntry, 'missedEntry'),
            ...withSection(waiting, 'waiting'),
        ];
    }, [holding, stoppedOut, missedEntry, waiting]);

    const { visibleItems, hasMore, sentinelRef } = useInfiniteScroll(orderedCards, 24, 24);

    // Agrupa itens visíveis por seção consecutiva para manter headers + grid
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
        holding: {
            title: 'Em Hold',
            subtitle: 'Posições Ativas',
            dotClass: 'bg-green-500',
            h2Class: 'text-green-600',
            badgeClass: 'bg-green-500/10 text-green-600',
            description: 'Estratégias com posição aberta. A distância mostra o quanto falta para o sinal de saída.',
        },
        stoppedOut: {
            title: 'Saiu no Stop',
            subtitle: 'Stop Loss Ativado',
            dotClass: 'bg-red-500',
            h2Class: 'text-red-600',
            badgeClass: 'bg-red-500/10 text-red-600',
            description: 'A média curta está acima da longa (condição de entrada satisfeita), mas a posição foi fechada no stop loss. A distância mostra o spread entre as médias. Aguardando cruzamento para baixo ou nova entrada.',
        },
        missedEntry: {
            title: 'Entrada Perdida',
            subtitle: 'Sem Posição',
            dotClass: 'bg-yellow-500',
            h2Class: 'text-yellow-600',
            badgeClass: 'bg-yellow-500/10 text-yellow-600',
            description: 'A média curta está acima da longa (condição de entrada satisfeita), mas não há posição ativa. Aguardando confirmação ou nova entrada.',
        },
        waiting: {
            title: 'Aguardando',
            subtitle: 'Sem Posição',
            dotClass: 'bg-gray-400',
            h2Class: 'text-gray-500',
            badgeClass: 'bg-gray-500/10 text-gray-600',
            description: 'Estratégias aguardando sinal de entrada. A distância mostra o quanto falta para a média curta cruzar acima da longa.',
        },
    };

    return (
        <div className="container mx-auto p-6 space-y-8">
            <div className="flex flex-col gap-4">
                <div className="flex justify-between items-center">
                    <div className="space-y-1">
                        <h1 className="text-3xl font-bold tracking-tight">Opportunity Board</h1>
                        <p className="text-muted-foreground">
                            Monitor your favorite strategies - See which are in HOLD and how close they are to the next signal
                        </p>
                        {lastUpdated && (
                            <p className="text-xs text-muted-foreground">
                                Last updated: {lastUpdated.toLocaleTimeString()}
                            </p>
                        )}
                    </div>
                    <div className="flex gap-2">
                        <Button variant="secondary" onClick={() => fetchOpportunities()} disabled={loading}>
                            <RefreshCw className={`mr-2 h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
                            Refresh
                        </Button>
                    </div>
                </div>

                <div className="flex items-center gap-4 flex-wrap">
                    <div className="flex items-center gap-2">
                        <span className="text-sm font-medium">Tier:</span>
                        <div className="relative">
                            <select
                                value={tierFilter}
                                onChange={(e) => setTierFilter(e.target.value as TierFilter)}
                                className="text-sm border border-border rounded pl-2 pr-8 py-1.5 bg-gray-900 text-gray-100 appearance-none cursor-pointer focus:ring-1 focus:ring-primary focus:border-primary"
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
                                className="text-sm border border-border rounded pl-2 pr-8 py-1.5 bg-gray-900 text-gray-100 appearance-none cursor-pointer focus:ring-1 focus:ring-primary focus:border-primary"
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
            ) : (
                <div className="space-y-10">
                    {visibleGroups.map(({ section, cards }) => {
                        const cfg = SECTION_CONFIG[section];
                        const total = { holding: holding.length, stoppedOut: stoppedOut.length, missedEntry: missedEntry.length, waiting: waiting.length }[section];
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
                                        <OpportunityCard key={opp.id} opportunity={opp} />
                                    ))}
                                </div>
                            </section>
                        );
                    })}
                    {/* Sentinel: ao entrar na viewport, carrega mais itens */}
                    {hasMore && (
                        <div ref={sentinelRef} className="flex justify-center py-8" aria-hidden="true">
                            <span className="text-sm text-muted-foreground animate-pulse">Carregando mais…</span>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
};
