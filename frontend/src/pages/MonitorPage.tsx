import React, { useEffect, useState, useMemo } from 'react';
import type { Opportunity } from '@/components/monitor/types';
import { OpportunityCard } from '@/components/monitor/OpportunityCard';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader } from '@/components/ui/Card';
import { RefreshCw, ArrowUpDown, ChevronDown } from 'lucide-react';
import { useToast } from "@/components/ui/use-toast";
import { useInfiniteScroll } from '@/hooks/useInfiniteScroll';

type SortOption = 'distance' | 'symbol';
type TierFilter = 'all' | '1' | '2' | '3' | 'none';

export const MonitorPage: React.FC = () => {
    const [opportunities, setOpportunities] = useState<Opportunity[]>([]);
    const [loading, setLoading] = useState(false);
    const [sortBy, setSortBy] = useState<SortOption>('distance');
    const [tierFilter, setTierFilter] = useState<TierFilter>('1');
    const [lastUpdated, setLastUpdated] = useState<Date | null>(null);
    const { toast } = useToast();

    const fetchOpportunities = async () => {
        setLoading(true);
        try {
            const response = await fetch('http://localhost:8000/api/opportunities/');
            if (!response.ok) throw new Error('Failed to fetch opportunities');
            const data = await response.json();
            setOpportunities(data);
            setLastUpdated(new Date());

            toast({
                title: "Updated",
                description: `Analyzed ${data.length} strategies`,
            });
        } catch (error) {
            console.error(error);
            toast({
                title: "Error",
                description: "Could not load opportunities. Is backend running?",
                variant: "destructive"
            });
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        // Load once when page opens (no auto-refresh)
        fetchOpportunities();
    }, []);

    const matchesTier = (o: Opportunity) => {
        if (tierFilter === 'all') return true;
        if (tierFilter === 'none') return o.tier == null;
        return o.tier === parseInt(tierFilter);
    };

    // Sort opportunities by distance (closest first) or symbol
    // Regra desejada:
    // - HOLD sempre primeiro
    // - Depois, independente do tier, os mais próximos (menor distância) vêm primeiro
    // - Tier serve apenas como filtro visual/por dropdown, não como prioridade na ordenação
    const sortedOpportunities = useMemo(() => {
        const sorted = [...opportunities].sort((a, b) => {
            if (sortBy === 'distance') {
                // HOLD primeiro
                if (a.is_holding !== b.is_holding) {
                    return a.is_holding ? -1 : 1;
                }
                // Depois, ordenar apenas pela distância (mais próximo primeiro)
                const distA = a.distance_to_next_status ?? 999;
                const distB = b.distance_to_next_status ?? 999;
                if (distA !== distB) {
                    return distA - distB;
                }
                // Desempate opcional por tier (1, 2, 3, null)
                const tierA = a.tier ?? 999;
                const tierB = b.tier ?? 999;
                if (tierA !== tierB) {
                    return tierA - tierB;
                }
                // Último critério: símbolo
                return a.symbol.localeCompare(b.symbol);
            } else if (sortBy === 'symbol') {
                return a.symbol.localeCompare(b.symbol);
            }
            return 0;
        });
        return sorted;
    }, [opportunities, sortBy]);

    // Separate opportunities by status, then apply tier filter
    const holding = sortedOpportunities.filter(o => o.is_holding && matchesTier(o));
    const stoppedOut = sortedOpportunities.filter(o => !o.is_holding && o.status === 'STOPPED_OUT' && matchesTier(o));
    const missedEntry = sortedOpportunities.filter(o => !o.is_holding && o.status === 'MISSED_ENTRY' && matchesTier(o));
    const waiting = sortedOpportunities.filter(o => !o.is_holding && o.status !== 'STOPPED_OUT' && o.status !== 'MISSED_ENTRY' && matchesTier(o));

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
                        <Button variant="outline" onClick={fetchOpportunities} disabled={loading}>
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
                                className="text-sm border rounded pl-2 pr-8 py-1.5 bg-background appearance-none cursor-pointer"
                            >
                                <option value="all">All</option>
                                <option value="1">Tier 1 – Core</option>
                                <option value="2">Tier 2 – Complementares</option>
                                <option value="3">Tier 3</option>
                                <option value="none">Sem tier</option>
                            </select>
                            <ChevronDown className="absolute right-2 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground pointer-events-none" />
                        </div>
                    </div>
                    <div className="flex items-center gap-2">
                        <ArrowUpDown className="w-4 h-4 text-muted-foreground" />
                        <span className="text-sm font-medium">Sort:</span>
                        <select
                            value={sortBy}
                            onChange={(e) => setSortBy(e.target.value as SortOption)}
                            className="text-sm border rounded px-2 py-1 bg-background"
                        >
                            <option value="distance">Distance (closest first)</option>
                            <option value="symbol">Symbol</option>
                        </select>
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
                    <Button variant="outline" onClick={() => window.location.href = '/'}>
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
