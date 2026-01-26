import React, { useEffect, useState } from 'react';
import type { Opportunity } from '@/components/monitor/types';
import { OpportunityCard } from '@/components/monitor/OpportunityCard';
import { Button } from '@/components/ui/button';
import { RefreshCw, LayoutDashboard } from 'lucide-react';
import { useToast } from "@/components/ui/use-toast";

export const MonitorPage: React.FC = () => {
    const [opportunities, setOpportunities] = useState<Opportunity[]>([]);
    const [loading, setLoading] = useState(false);
    const { toast } = useToast();

    const fetchOpportunities = async () => {
        setLoading(true);
        try {
            const response = await fetch('http://localhost:8000/api/opportunities/');
            if (!response.ok) throw new Error('Failed to fetch opportunities');
            const data = await response.json();
            setOpportunities(data);

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
        fetchOpportunities();

        // Auto-refresh every 60s
        const interval = setInterval(fetchOpportunities, 60000);
        return () => clearInterval(interval);
    }, []);

    const signals = opportunities.filter(o => ['BUY_SIGNAL', 'EXIT_SIGNAL', 'SIGNAL', 'EXIT'].includes(o.status));
    const holding = opportunities.filter(o => o.status === 'HOLDING');
    const approaching = opportunities.filter(o => ['BUY_NEAR', 'EXIT_NEAR', 'NEAR'].includes(o.status));
    const neutral = opportunities.filter(o => ['NEUTRAL', 'ERROR', 'WAITING'].includes(o.status));

    return (
        <div className="container mx-auto p-6 space-y-8">
            <div className="flex justify-between items-center">
                <div className="space-y-1">
                    <h1 className="text-3xl font-bold tracking-tight">Opportunity Board</h1>
                    <p className="text-muted-foreground">Monitor your favorite strategies for entry and exit signals (1D Timeframe)</p>
                </div>
                <div className="flex gap-2">
                    <Button variant="outline" onClick={fetchOpportunities} disabled={loading}>
                        <RefreshCw className={`mr-2 h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
                        Refresh
                    </Button>
                </div>
            </div>

            {loading && opportunities.length === 0 ? (
                <div className="flex items-center justify-center h-64">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
                </div>
            ) : (
                <div className="space-y-10">
                    {/* Active Signals Section (Buy or Sell) */}
                    {signals.length > 0 && (
                        <section className="space-y-4">
                            <h2 className="text-xl font-semibold flex items-center gap-2 text-primary">
                                <LayoutDashboard className="w-5 h-5" /> Active Signals
                                <span className="bg-primary/10 text-primary text-xs px-2 py-0.5 rounded-full ml-2">
                                    Action Required
                                </span>
                            </h2>
                            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
                                {signals.map(opp => (
                                    <OpportunityCard key={opp.id} opportunity={opp} />
                                ))}
                            </div>
                        </section>
                    )}

                    {/* Holding Section (New) */}
                    {holding.length > 0 && (
                        <section className="space-y-4">
                            <h2 className="text-xl font-semibold flex items-center gap-2 text-blue-500">
                                <LayoutDashboard className="w-5 h-5" /> Active Positions (Holding)
                                <span className="bg-blue-500/10 text-blue-600 dark:text-blue-400 text-xs px-2 py-0.5 rounded-full ml-2">
                                    Portfolio
                                </span>
                            </h2>
                            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
                                {holding.map(opp => (
                                    <OpportunityCard key={opp.id} opportunity={opp} />
                                ))}
                            </div>
                        </section>
                    )}

                    {/* Approaching Section */}
                    {approaching.length > 0 && (
                        <section className="space-y-4">
                            <h2 className="text-xl font-semibold flex items-center gap-2 text-yellow-500">
                                <LayoutDashboard className="w-5 h-5" /> Approaching Setup
                                <span className="bg-yellow-500/10 text-yellow-600 dark:text-yellow-400 text-xs px-2 py-0.5 rounded-full ml-2">
                                    Watchlist
                                </span>
                            </h2>
                            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
                                {approaching.map(opp => (
                                    <OpportunityCard key={opp.id} opportunity={opp} />
                                ))}
                            </div>
                        </section>
                    )}

                    {/* Neutral Section */}
                    {neutral.length > 0 && (
                        <section className="space-y-4">
                            <h2 className="text-xl font-semibold flex items-center gap-2 text-muted-foreground">
                                <LayoutDashboard className="w-5 h-5" /> Waiting
                            </h2>
                            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 opacity-75 grayscale-[0.5] hover:grayscale-0 transition-all">
                                {neutral.map(opp => (
                                    <OpportunityCard key={opp.id} opportunity={opp} />
                                ))}
                            </div>
                        </section>
                    )}

                    {opportunities.length === 0 && !loading && (
                        <div className="text-center py-20 text-muted-foreground">
                            <p>No favorites found. Star some strategies in the Backtester to see them here!</p>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
};
