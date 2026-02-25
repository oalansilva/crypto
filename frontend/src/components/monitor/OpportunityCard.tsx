import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { Target, Activity, Settings, Star, BarChart3 } from "lucide-react";
import { API_BASE_URL, apiUrl } from '../../lib/apiBase';
import { MiniCandlesChart, type MarketCandle } from './MiniCandlesChart';

import type { Opportunity, MonitorCardMode, MonitorPreference } from './types';

interface OpportunityCardProps {
    opportunity: Opportunity;
    preference: MonitorPreference;
    isSavingPreference: boolean;
    onToggleInPortfolio: (symbol: string, nextValue: boolean) => void;
    onToggleCardMode: (symbol: string, nextMode: MonitorCardMode) => void;
}

const getDistanceColor = (distance: number | null | undefined): string => {
    if (distance === null || distance === undefined) return 'text-gray-600 dark:text-gray-400';
    if (distance < 0.5) return 'text-green-600 dark:text-green-400 font-bold';
    if (distance < 1.0) return 'text-yellow-600 dark:text-yellow-400 font-bold';
    return 'text-gray-600 dark:text-gray-400';
};

const getTierStyles = (tier: number | null | undefined) => {
    switch (tier) {
        case 1:
            return { dot: 'bg-green-500', border: 'rgb(34, 197, 94)', label: 'Tier 1', ring: 'ring-green-400' };
        case 2:
            return { dot: 'bg-amber-500', border: 'rgb(245, 158, 11)', label: 'Tier 2', ring: 'ring-amber-400' };
        case 3:
            return { dot: 'bg-red-500', border: 'rgb(239, 68, 68)', label: 'Tier 3', ring: 'ring-red-400' };
        default:
            return null;
    }
};

const symbolKey = (symbol: string): string => symbol.replace(/[^a-zA-Z0-9]+/g, '-').toLowerCase();

export const OpportunityCard: React.FC<OpportunityCardProps> = ({
    opportunity,
    preference,
    isSavingPreference,
    onToggleInPortfolio,
    onToggleCardMode,
}) => {
    const {
        symbol,
        timeframe,
        name,
        is_holding,
        distance_to_next_status,
        next_status_label,
        last_price,
    } = opportunity;

    const isPriceMode = preference.card_mode === 'price';

    const [isEditingNotes, setIsEditingNotes] = React.useState(false);
    const [notesValue, setNotesValue] = React.useState(opportunity.notes || '');
    const [isSavingNotes, setIsSavingNotes] = React.useState(false);

    const [candles, setCandles] = React.useState<MarketCandle[]>([]);
    const [candlesLoading, setCandlesLoading] = React.useState(false);
    const [candlesError, setCandlesError] = React.useState<string | null>(null);

    React.useEffect(() => {
        setNotesValue(opportunity.notes || '');
    }, [opportunity.notes]);

    React.useEffect(() => {
        if (!isPriceMode) {
            setCandlesError(null);
            return;
        }

        const controller = new AbortController();
        const run = async () => {
            setCandlesLoading(true);
            setCandlesError(null);
            try {
                const effectiveTf = symbol.includes('/') ? timeframe : '1d';
                const url = apiUrl('/market/candles');
                url.searchParams.set('symbol', symbol);
                url.searchParams.set('timeframe', effectiveTf);
                url.searchParams.set('limit', '120');

                const response = await fetch(url.toString(), { signal: controller.signal });
                const payload = await response.json();
                if (!response.ok) {
                    throw new Error(String(payload?.detail || `Failed to load candles (${response.status})`));
                }

                const rows = Array.isArray(payload?.candles) ? payload.candles : [];
                setCandles(rows);
            } catch (error) {
                if (!controller.signal.aborted) {
                    setCandles([]);
                    setCandlesError(error instanceof Error ? error.message : 'Failed to load candles');
                }
            } finally {
                if (!controller.signal.aborted) {
                    setCandlesLoading(false);
                }
            }
        };

        run();
        return () => controller.abort();
    }, [isPriceMode, symbol, timeframe]);

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

    const showProgress = distance !== null && distance !== undefined && distance < 1.0;
    const progressPercent = showProgress
        ? Math.max(0, Math.min(100, (1 - distance) * 100))
        : 0;

    const status = opportunity.status || (is_holding ? 'HOLD' : 'WAIT');
    const isStoppedOut = status === 'STOPPED_OUT';
    const isMissedEntry = status === 'MISSED_ENTRY';
    const isWait = !is_holding && !isStoppedOut && !isMissedEntry;
    const tierStyles = getTierStyles(opportunity.tier);

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
    } else if (isWait && tierStyles) {
        borderColor = 'border-l-4';
        cardBgColor = tierStyles.dot === 'bg-green-500' ? 'bg-green-50/50 dark:bg-green-900/20 border-green-200 dark:border-green-800' :
                      tierStyles.dot === 'bg-amber-500' ? 'bg-amber-50/50 dark:bg-amber-900/20 border-amber-200 dark:border-amber-800' :
                      'bg-red-50/50 dark:bg-red-900/20 border-red-200 dark:border-red-800';
    }

    const statusMessage = opportunity.message || (
        distance !== null && distance !== undefined
            ? `${distance.toFixed(2)}% to ${next_status_label}`
            : `Waiting for ${next_status_label} signal`
    );

    const cardStyle = is_holding ? {
        backgroundColor: 'rgb(220, 252, 231)',
        borderLeftWidth: '4px',
        borderLeftColor: 'rgb(22, 163, 74)',
    } : isStoppedOut ? {
        backgroundColor: 'rgb(254, 242, 242)',
        borderLeftWidth: '4px',
        borderLeftColor: 'rgb(220, 38, 38)',
    } : isMissedEntry ? {
        backgroundColor: 'rgb(254, 252, 232)',
        borderLeftWidth: '4px',
        borderLeftColor: 'rgb(234, 179, 8)',
    } : isWait && tierStyles ? {
        backgroundColor: tierStyles.dot === 'bg-green-500' ? 'rgb(240, 253, 244)' : tierStyles.dot === 'bg-amber-500' ? 'rgb(255, 251, 235)' : 'rgb(254, 242, 242)',
        borderLeftWidth: '4px',
        borderLeftColor: tierStyles.border,
    } : {
        backgroundColor: 'rgb(255, 255, 255)',
        borderLeftWidth: '4px',
        borderLeftColor: 'rgb(203, 213, 225)',
    };

    const symbolTestKey = symbolKey(symbol);

    return (
        <Card
            className={`${borderColor} ${cardBgColor} ${holdingIndicator} hover:shadow-lg transition-all hover:scale-[1.02] relative`}
            style={cardStyle}
            data-testid={`monitor-card-${symbolTestKey}`}
        >
            <CardHeader className="flex flex-row items-start justify-between space-y-0 pb-2 gap-2">
                <div className="flex flex-col min-w-0">
                    <CardTitle className={`text-xl font-bold flex items-center gap-2 ${
                        is_holding ? 'text-green-700 dark:text-green-300' :
                        isStoppedOut ? 'text-red-700 dark:text-red-300' :
                        isMissedEntry ? 'text-yellow-700 dark:text-yellow-300' :
                        'text-gray-900 dark:text-gray-100'
                    }`}>
                        {tierStyles && (
                            <span className={`w-2 h-2 rounded-full ${tierStyles.dot} ring-1 ${tierStyles.ring} flex-shrink-0`} title={tierStyles.label} />
                        )}
                        <span className="truncate">{symbol}</span>
                        <span className="text-sm font-normal text-gray-600 dark:text-gray-400 bg-gray-100 dark:bg-gray-700 px-2 py-1 rounded">{timeframe}</span>
                    </CardTitle>
                    <span className="text-sm text-gray-700 dark:text-gray-300 truncate max-w-[220px] font-medium">
                        {name || opportunity.template_name}
                    </span>
                </div>

                <div className="flex flex-col items-end gap-2">
                    <Badge variant="outline" className={`${badgeColor} uppercase text-sm font-bold shadow-sm px-3 py-1`}>
                        {statusBadge}
                    </Badge>
                    <div className="flex items-center gap-1">
                        <button
                            type="button"
                            className={`rounded-md border px-2 py-1 text-xs flex items-center gap-1 ${preference.in_portfolio ? 'border-amber-500 text-amber-600 bg-amber-50' : 'border-slate-300 text-slate-600 bg-white'}`}
                            onClick={() => onToggleInPortfolio(symbol, !preference.in_portfolio)}
                            disabled={isSavingPreference}
                            data-testid={`portfolio-toggle-${symbolTestKey}`}
                            title={preference.in_portfolio ? 'Remove from In Portfolio' : 'Add to In Portfolio'}
                        >
                            <Star className={`w-3 h-3 ${preference.in_portfolio ? 'fill-current' : ''}`} />
                            <span className="hidden sm:inline">Portfolio</span>
                        </button>

                        <button
                            type="button"
                            className="rounded-md border border-slate-300 px-2 py-1 text-xs flex items-center gap-1 bg-white text-slate-700"
                            onClick={() => onToggleCardMode(symbol, isPriceMode ? 'strategy' : 'price')}
                            disabled={isSavingPreference}
                            data-testid={`mode-toggle-${symbolTestKey}`}
                            title={isPriceMode ? 'Switch to strategy mode' : 'Switch to price mode'}
                        >
                            <BarChart3 className="w-3 h-3" />
                            <span data-testid={`mode-label-${symbolTestKey}`}>{isPriceMode ? 'Price' : 'Strategy'}</span>
                        </button>
                    </div>
                </div>
            </CardHeader>

            <CardContent>
                {isPriceMode ? (
                    <div className="space-y-3">
                        <div className="flex justify-between items-center">
                            <span className="text-base font-semibold text-gray-700 dark:text-gray-300">Price:</span>
                            <span className="font-mono font-bold text-lg text-gray-900 dark:text-gray-100">{formattedPrice}</span>
                        </div>
                        <div className="p-2 bg-gray-100 dark:bg-gray-800 rounded-md text-xs border border-gray-300 dark:border-gray-600">
                            {candlesLoading ? 'Loading candles...' : null}
                            {candlesError ? <span className="text-red-600 dark:text-red-300">{candlesError}</span> : null}
                            {!candlesLoading && !candlesError && candles.length === 0 ? <span>No candle data.</span> : null}
                            {!candlesLoading && !candlesError && candles.length > 0 ? <MiniCandlesChart candles={candles} /> : null}
                        </div>
                    </div>
                ) : (
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

                            {is_holding && opportunity.distance_to_stop_pct !== null && opportunity.distance_to_stop_pct !== undefined ? (
                                <div className="rounded-md border border-red-200 dark:border-red-800 bg-red-50/60 dark:bg-red-900/20 p-2">
                                    <div className="flex justify-between items-center">
                                        <span className="text-sm font-semibold text-gray-700 dark:text-gray-300">Stop risk:</span>
                                        <span className="font-mono font-bold text-sm text-red-700 dark:text-red-300">
                                            {opportunity.distance_to_stop_pct.toFixed(2)}%
                                        </span>
                                    </div>
                                    <div className="mt-1 flex flex-wrap gap-x-3 gap-y-1 text-[11px] font-mono text-gray-700 dark:text-gray-300">
                                        {opportunity.entry_price !== null && opportunity.entry_price !== undefined ? (
                                            <span>entry: ${opportunity.entry_price.toFixed(8)}</span>
                                        ) : null}
                                        {opportunity.stop_price !== null && opportunity.stop_price !== undefined ? (
                                            <span>stop: ${opportunity.stop_price.toFixed(8)}</span>
                                        ) : null}
                                    </div>
                                </div>
                            ) : null}

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

                        {opportunity.parameters && Object.keys(opportunity.parameters).length > 0 && (
                            <div className="p-3 bg-gray-100 dark:bg-gray-800 rounded-md text-sm border border-gray-300 dark:border-gray-600">
                                <div className="flex items-center gap-2 mb-1">
                                    <Settings className="w-4 h-4 text-violet-600 dark:text-violet-400 flex-shrink-0" />
                                    <span className="text-xs font-semibold uppercase tracking-wide text-gray-500 dark:text-gray-400">
                                        Parameters
                                    </span>
                                </div>
                                <p className="font-mono text-xs text-gray-700 dark:text-gray-300 break-words">
                                    {Object.entries(opportunity.parameters)
                                        .map(([k, v]) => `${k}=${v}`)
                                        .join(' ')}
                                </p>
                            </div>
                        )}

                        {opportunity.indicator_values && Object.keys(opportunity.indicator_values).length > 0 && (
                            <div className="p-3 bg-blue-50 dark:bg-blue-900/20 rounded-md text-sm border border-blue-200 dark:border-blue-800">
                                <div className="flex items-center gap-2 mb-1">
                                    <Target className="w-4 h-4 text-blue-600 dark:text-blue-400 flex-shrink-0" />
                                    <span className="text-xs font-semibold uppercase tracking-wide text-blue-600 dark:text-blue-400">
                                        Indicator Values
                                    </span>
                                </div>
                                <p className="font-mono text-xs text-gray-700 dark:text-gray-300 break-words">
                                    {Object.entries(opportunity.indicator_values)
                                        .map(([k, v]) => `${k}=${typeof v === 'number' ? v.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) : v}`)
                                        .join(' · ')}
                                </p>
                            </div>
                        )}

                        <div className="p-3 bg-slate-50 dark:bg-slate-800/80 rounded-md text-sm border border-slate-200 dark:border-slate-600">
                            <div className="flex items-center justify-between gap-2">
                                <span className="text-xs font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-400">
                                    Notes
                                </span>
                                {!isEditingNotes && (
                                    <button
                                        type="button"
                                        className="text-xs text-blue-600 dark:text-blue-400 hover:underline"
                                        onClick={() => setIsEditingNotes(true)}
                                    >
                                        Edit
                                    </button>
                                )}
                            </div>

                            {isEditingNotes ? (
                                <div className="mt-2 space-y-2">
                                    <textarea
                                        className="w-full min-h-[60px] text-xs rounded border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-900 px-2 py-1 text-slate-800 dark:text-slate-100 focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
                                        value={notesValue}
                                        onChange={(e) => setNotesValue(e.target.value)}
                                        placeholder="Add notes for this strategy..."
                                    />
                                    <div className="flex justify-end gap-2">
                                        <button
                                            type="button"
                                            className="px-2 py-1 text-xs rounded border border-slate-300 text-slate-600 hover:bg-slate-100 dark:border-slate-600 dark:text-slate-300 dark:hover:bg-slate-700"
                                            onClick={() => {
                                                setNotesValue(opportunity.notes || '');
                                                setIsEditingNotes(false);
                                            }}
                                            disabled={isSavingNotes}
                                        >
                                            Cancel
                                        </button>
                                        <button
                                            type="button"
                                            className="px-2 py-1 text-xs rounded bg-blue-600 text-white hover:bg-blue-700 disabled:opacity-60 disabled:cursor-not-allowed"
                                            onClick={async () => {
                                                try {
                                                    setIsSavingNotes(true);
                                                    const res = await fetch(`${API_BASE_URL}/favorites/${opportunity.id}`, {
                                                        method: 'PATCH',
                                                        headers: { 'Content-Type': 'application/json' },
                                                        body: JSON.stringify({ notes: notesValue }),
                                                    });
                                                    if (!res.ok) {
                                                        alert('Error saving notes.');
                                                        return;
                                                    }
                                                    setIsEditingNotes(false);
                                                } catch (err) {
                                                    console.error('Error saving notes:', err);
                                                    alert('Error saving notes.');
                                                } finally {
                                                    setIsSavingNotes(false);
                                                }
                                            }}
                                            disabled={isSavingNotes}
                                        >
                                            {isSavingNotes ? 'Saving...' : 'Save'}
                                        </button>
                                    </div>
                                </div>
                            ) : (
                                <p className="mt-1 font-medium text-slate-700 dark:text-slate-200 break-words text-xs whitespace-pre-wrap">
                                    {notesValue || 'No notes.'}
                                </p>
                            )}
                        </div>
                    </div>
                )}
            </CardContent>
        </Card>
    );
};
