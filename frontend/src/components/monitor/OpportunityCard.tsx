import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { ArrowUpRight, Clock, Activity, Target } from "lucide-react";

import type { Opportunity } from './types';

export type { Opportunity }; // Re-export if needed, or just use it internally.
// But MonitorPage imports it from here currently. Let's re-export to minimize MonitorPage changes if possible, 
// OR better, update MonitorPage to import from ./types.

// Let's just remove the definition here and import it.


interface OpportunityCardProps {
    opportunity: Opportunity;
}

const statusColors: Record<string, string> = {
    SIGNAL: "bg-green-500/10 text-green-500 border-green-500/20",
    NEAR: "bg-yellow-500/10 text-yellow-500 border-yellow-500/20",
    NEUTRAL: "bg-gray-500/10 text-gray-500 border-gray-500/20",
    ERROR: "bg-red-500/10 text-red-500 border-red-500/20",
    HOLDING: "bg-blue-500/10 text-blue-500 border-blue-500/20",
    EXIT_NEAR: "bg-orange-500/10 text-orange-500 border-orange-500/20",
    EXIT_SIGNAL: "bg-red-600/10 text-red-600 border-red-600/20",
};

const getBorderColor = (status: string) => {
    switch (status) {
        case 'SIGNAL': return 'border-l-green-500';
        case 'NEAR': return 'border-l-yellow-500';
        case 'HOLDING': return 'border-l-blue-500';
        case 'EXIT_NEAR': return 'border-l-orange-500';
        case 'EXIT_SIGNAL': return 'border-l-red-600';
        default: return 'border-l-gray-500';
    }
};

export const OpportunityCard: React.FC<OpportunityCardProps> = ({ opportunity }) => {
    const { symbol, timeframe, name, status, message, last_price, details } = opportunity;

    const formattedPrice = new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
    }).format(last_price);

    const distance = details?.distance ? `${details.distance}%` : '-';

    return (
        <Card className={`border-l-4 ${getBorderColor(status)} hover:shadow-md transition-all`}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <div className="flex flex-col">
                    <CardTitle className="text-lg font-bold flex items-center gap-2">
                        {symbol} <span className="text-xs font-normal text-muted-foreground bg-secondary px-1.5 py-0.5 rounded">{timeframe}</span>
                    </CardTitle>
                    <span className="text-xs text-muted-foreground">{name || opportunity.template_name}</span>
                </div>
                <Badge variant="outline" className={`${statusColors[status]} uppercase text-xs font-bold`}>
                    {status}
                </Badge>
            </CardHeader>
            <CardContent>
                <div className="flex flex-col gap-3 mt-2">
                    <div className="flex justify-between items-center text-sm">
                        <span className="text-muted-foreground">Price:</span>
                        <span className="font-mono font-medium">{formattedPrice}</span>
                    </div>

                    <div className="flex justify-between items-center text-sm">
                        <span className="text-muted-foreground">Distance:</span>
                        <div className="flex items-center gap-1">
                            <Target className="w-3 h-3 text-muted-foreground" />
                            <span className={`font-mono font-medium ${status === 'SIGNAL' ? 'text-green-500' : status === 'NEAR' ? 'text-yellow-500' : ''}`}>
                                {distance}
                            </span>
                        </div>
                    </div>

                    <div className="p-2 bg-secondary/50 rounded-md text-xs border border-border/50">
                        <div className="flex items-start gap-2">
                            <Activity className="w-3 h-3 mt-0.5 text-primary" />
                            <span className="italic">{message}</span>
                        </div>
                    </div>
                </div>
            </CardContent>
        </Card>
    );
};
