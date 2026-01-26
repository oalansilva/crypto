import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { Target, Activity } from "lucide-react";

import type { Opportunity } from './types';

interface OpportunityCardProps {
    opportunity: Opportunity;
}

const getDistanceColor = (distance: number | null | undefined): string => {
    if (distance === null || distance === undefined) return 'text-gray-600 dark:text-gray-400';
    if (distance < 0.5) return 'text-green-600 dark:text-green-400 font-bold';
    if (distance < 1.0) return 'text-yellow-600 dark:text-yellow-400 font-bold';
    return 'text-gray-600 dark:text-gray-400';
};

export const OpportunityCard: React.FC<OpportunityCardProps> = ({ opportunity }) => {
    const { 
        symbol, 
        timeframe, 
        name, 
        is_holding, 
        distance_to_next_status, 
        next_status_label,
        last_price 
    } = opportunity;

    const formattedPrice = new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 2,
        maximumFractionDigits: 8,
    }).format(last_price);

    const distance = distance_to_next_status;
    const distanceStr = distance !== null && distance !== undefined 
        ? `${distance.toFixed(2)}%` 
        : '-';
    const distanceColor = getDistanceColor(distance);
    
    // Show progress bar if distance is less than 1%
    const showProgress = distance !== null && distance !== undefined && distance < 1.0;
    const progressPercent = showProgress 
        ? Math.max(0, Math.min(100, (1 - distance) * 100)) 
        : 0;

    // Check for special statuses from backend
    const status = opportunity.status || (is_holding ? 'HOLD' : 'WAIT');
    const isStoppedOut = status === 'STOPPED_OUT';
    const isMissedEntry = status === 'MISSED_ENTRY';
    
    // Status badge: HOLD (green), STOPPED_OUT (red/orange), MISSED_ENTRY (yellow), or WAIT (gray)
    let statusBadge = 'WAIT';
    let badgeColor = "bg-slate-200 text-slate-600 border-slate-300";
    let borderColor = 'border-l-slate-300 border-l-4';
    let cardBgColor = 'bg-white dark:bg-slate-800 border-slate-200 dark:border-slate-700';
    let holdingIndicator = '';
    
    if (is_holding) {
        statusBadge = 'HOLD';
        badgeColor = "bg-green-600 text-white border-green-600 font-bold shadow-md";
        borderColor = 'border-l-green-600 border-l-4';
        cardBgColor = 'bg-green-50 dark:bg-green-900/40 border-green-400 dark:border-green-600';
        holdingIndicator = 'ring-2 ring-green-400 shadow-lg shadow-green-500/30';
    } else if (isStoppedOut) {
        statusBadge = 'STOPPED OUT';
        badgeColor = "bg-red-600 text-white border-red-600 font-bold shadow-md";
        borderColor = 'border-l-red-600 border-l-4';
        cardBgColor = 'bg-red-50 dark:bg-red-900/40 border-red-400 dark:border-red-600';
        holdingIndicator = 'ring-2 ring-red-400 shadow-lg shadow-red-500/30';
    } else if (isMissedEntry) {
        statusBadge = 'MISSED';
        badgeColor = "bg-yellow-500 text-white border-yellow-500 font-bold shadow-md";
        borderColor = 'border-l-yellow-500 border-l-4';
        cardBgColor = 'bg-yellow-50 dark:bg-yellow-900/40 border-yellow-400 dark:border-yellow-600';
        holdingIndicator = 'ring-2 ring-yellow-400 shadow-lg shadow-yellow-500/30';
    }

    // Message: Use backend message if available, otherwise generate from distance
    const statusMessage = opportunity.message || (
        distance !== null && distance !== undefined
            ? `${distance.toFixed(2)}% to ${next_status_label}`
            : `Waiting for ${next_status_label} signal`
    );

    return (
        <Card 
            className={`${borderColor} ${cardBgColor} ${holdingIndicator} hover:shadow-lg transition-all hover:scale-[1.02] relative`}
            style={is_holding ? { 
                backgroundColor: 'rgb(220, 252, 231)', // green-100
                borderLeftWidth: '4px',
                borderLeftColor: 'rgb(22, 163, 74)', // green-600
            } : isStoppedOut ? {
                backgroundColor: 'rgb(254, 242, 242)', // red-50
                borderLeftWidth: '4px',
                borderLeftColor: 'rgb(220, 38, 38)', // red-600
            } : isMissedEntry ? {
                backgroundColor: 'rgb(254, 252, 232)', // yellow-50
                borderLeftWidth: '4px',
                borderLeftColor: 'rgb(234, 179, 8)', // yellow-500
            } : {
                backgroundColor: 'rgb(255, 255, 255)', // branco para WAIT
                borderLeftWidth: '4px',
                borderLeftColor: 'rgb(203, 213, 225)', // slate-300 para WAIT
            }}
        >
            {/* Visual indicator dot for special statuses */}
            {is_holding && (
                <div 
                    className="absolute top-3 right-3 w-3 h-3 bg-green-500 rounded-full animate-pulse shadow-lg shadow-green-500/70 ring-2 ring-green-400"
                    style={{ backgroundColor: 'rgb(34, 197, 94)' }}
                ></div>
            )}
            {isStoppedOut && (
                <div 
                    className="absolute top-3 right-3 w-3 h-3 bg-red-500 rounded-full animate-pulse shadow-lg shadow-red-500/70 ring-2 ring-red-400"
                    style={{ backgroundColor: 'rgb(239, 68, 68)' }}
                ></div>
            )}
            {isMissedEntry && (
                <div 
                    className="absolute top-3 right-3 w-3 h-3 bg-yellow-500 rounded-full animate-pulse shadow-lg shadow-yellow-500/70 ring-2 ring-yellow-400"
                    style={{ backgroundColor: 'rgb(234, 179, 8)' }}
                ></div>
            )}
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <div className="flex flex-col">
                    <CardTitle className={`text-xl font-bold flex items-center gap-2 ${
                        is_holding ? 'text-green-700 dark:text-green-300' : 
                        isStoppedOut ? 'text-red-700 dark:text-red-300' : 
                        isMissedEntry ? 'text-yellow-700 dark:text-yellow-300' : 
                        'text-gray-900 dark:text-gray-100'
                    }`}>
                        {symbol} <span className="text-sm font-normal text-gray-600 dark:text-gray-400 bg-gray-100 dark:bg-gray-700 px-2 py-1 rounded">{timeframe}</span>
                    </CardTitle>
                    <span className="text-sm text-gray-700 dark:text-gray-300 truncate max-w-[200px] font-medium">
                        {name || opportunity.template_name}
                    </span>
                </div>
                <Badge variant="outline" className={`${badgeColor} uppercase text-sm font-bold shadow-sm px-3 py-1`}>
                    {statusBadge}
                </Badge>
            </CardHeader>
            <CardContent>
                <div className="flex flex-col gap-4 mt-2">
                    <div className="flex justify-between items-center">
                        <span className="text-base font-semibold text-gray-700 dark:text-gray-300">Price:</span>
                        <span className="font-mono font-bold text-lg text-gray-900 dark:text-gray-100">{formattedPrice}</span>
                    </div>

                    <div className="flex flex-col gap-2">
                        <div className="flex justify-between items-center">
                            <span className="text-base font-semibold text-gray-700 dark:text-gray-300">Distance:</span>
                            <div className="flex items-center gap-2">
                                <Target className="w-4 h-4 text-gray-600 dark:text-gray-400" />
                                <span className={`font-mono font-bold text-lg ${distanceColor}`}>
                                    {distanceStr}
                                </span>
                            </div>
                        </div>
                        
                        {/* Progress bar when close to signal (< 1%) */}
                        {showProgress && (
                            <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2 overflow-hidden">
                                <div 
                                    className={`h-full transition-all ${
                                        is_holding ? 'bg-orange-500' : 'bg-yellow-500'
                                    }`}
                                    style={{ width: `${progressPercent}%` }}
                                />
                            </div>
                        )}
                    </div>

                    <div className="p-3 bg-gray-100 dark:bg-gray-800 rounded-md text-sm border border-gray-300 dark:border-gray-600">
                        <div className="flex items-start gap-2">
                            <Activity className="w-4 h-4 mt-0.5 text-blue-600 dark:text-blue-400 flex-shrink-0" />
                            <span className="font-medium text-gray-800 dark:text-gray-200 break-words">{statusMessage}</span>
                        </div>
                    </div>
                </div>
            </CardContent>
        </Card>
    );
};
