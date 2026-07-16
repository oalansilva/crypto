import React from 'react';
import { createPortal } from 'react-dom';

import type { MarketCandle } from './MiniCandlesChart';
import { API_BASE_URL } from '../../lib/apiBase';
import { authFetch } from '@/lib/authFetch';
import { formatStrategyParameterLabel, formatStrategyParameterValue } from '@/lib/strategyParameters';
import { buildTradeMarkers, collapseSameCandleOppositeMarkers, getLatestMarkerSignalType, sameDisplayedCandle } from '@/lib/tradeMarkers';
import {
    StrategyChartSurface,
    toStrategyChartTimestamp,
    type StrategyChartMarker,
    type StrategyChartPriceLine,
    type StrategyChartConfigurationItem,
    type StrategyChartSnapshot,
    type StrategyChartSummaryItem,
} from '../charts/StrategyChartSurface';
import {
    StrategyTradesTable,
    type StrategyTrade,
    type StrategyTradeMetrics,
} from '../charts/StrategyTradesTable';
import {
    getOpportunityAssetType,
    getStrategyDisplayName,
    isProtectedStrategy,
    type Opportunity,
    type OpportunitySignalHistoryItem,
} from './types';
import { CHART_TIMEFRAMES, fetchMarketCandles, toChartTimeframe, type ChartTimeframe } from './chartData';
import { hasExitedOpportunity, resolveOpportunitySignal } from './signalResolution';
import { mergeStrategyTransparencySeries } from '@/lib/strategyTransparency';

interface ChartModalProps {
    symbol: string;
    opportunity: Opportunity;
    initialCandles: MarketCandle[];
    initialTimeframe: ChartTimeframe;
    viewMode: 'chart' | 'trades';
    onClose: () => void;
}

type TimeframePickerSource = 'algorithmic' | 'manual';
type TimeframePickerItem = {
    value: ChartTimeframe;
    label: string;
    source: TimeframePickerSource;
};

const PRICE_FORMATTER = new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 2,
    maximumFractionDigits: 8,
});

function formatPrice(value?: number | null) {
    if (value === null || value === undefined || Number.isNaN(value)) {
        return '-';
    }
    return PRICE_FORMATTER.format(value);
}

function formatPercent(value?: number | null) {
    if (value === null || value === undefined || Number.isNaN(value)) {
        return '-';
    }
    return `${value >= 0 ? '+' : ''}${value.toFixed(2)}%`;
}

function formatTimestamp(value?: string | null) {
    if (!value) {
        return '-';
    }

    return new Intl.DateTimeFormat('en-US', {
        month: 'short',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        timeZone: 'UTC',
    }).format(new Date(value));
}

function normalizeDirection(value?: string | null) {
    return String(value || 'long').trim().toLowerCase() === 'short' ? 'short' : 'long';
}

function actionLabelsForDirection(direction?: string | null) {
    const isShort = normalizeDirection(direction) === 'short';
    return {
        entry: isShort ? 'Venda' : 'Compra',
        exit: isShort ? 'Compra' : 'Venda',
        entrySignal: isShort ? 'Vender' : 'Comprar',
        exitRule: isShort ? 'Regra de compra/cobertura' : 'Regra de venda',
    };
}

function formatSignalReason(value?: string | null, direction?: string | null) {
    const normalized = String(value || '').trim().toLowerCase();
    const labels = actionLabelsForDirection(direction);
    if (!normalized) {
        return '-';
    }
    if (normalized === 'entry') {
        return labels.entry;
    }
    if (normalized === 'exit') {
        return labels.exit;
    }
    if (normalized === 'exit_logic') {
        return labels.exitRule;
    }
    if (normalized === 'stop_loss') {
        return 'Stop loss';
    }
    return normalized.replace(/_/g, ' ');
}

function getSignalHistoryLabel(item: OpportunitySignalHistoryItem, direction?: string | null) {
    const labels = actionLabelsForDirection(direction);
    return item.type === 'entry' ? labels.entry : labels.exit;
}

function getSignalHistoryMarker(item: OpportunitySignalHistoryItem, direction?: string | null) {
    const isEntry = item.type === 'entry';
    const isShort = normalizeDirection(direction) === 'short';
    const isStop = !isEntry && String(item.reason || '').trim().toLowerCase() === 'stop_loss';
    const isBuyVisual = (isEntry && !isShort) || (!isEntry && isShort);
    return {
        position: isBuyVisual ? 'belowBar' : 'aboveBar',
        shape: isBuyVisual ? 'arrowUp' : 'arrowDown',
        color: isStop ? '#f85149' : (isBuyVisual ? '#3fb950' : '#f6465d'),
        text: getSignalHistoryLabel(item, direction),
        signalType: item.type,
    } as const;
}

function getActiveEntrySignal(history?: OpportunitySignalHistoryItem[]): OpportunitySignalHistoryItem | null {
    const sortedHistory = [...(history || [])].sort(
        (left, right) => Date.parse(left.timestamp) - Date.parse(right.timestamp),
    );
    let activeEntry: OpportunitySignalHistoryItem | null = null;

    sortedHistory.forEach((item) => {
        if (item.type === 'entry') {
            activeEntry = item;
        } else if (item.type === 'exit') {
            activeEntry = null;
        }
    });

    return activeEntry;
}

function getLatestSignal(history?: OpportunitySignalHistoryItem[]): OpportunitySignalHistoryItem | null {
    const sortedHistory = [...(history || [])].sort(
        (left, right) => Date.parse(left.timestamp) - Date.parse(right.timestamp),
    );
    return sortedHistory.length > 0 ? sortedHistory[sortedHistory.length - 1] : null;
}

function getCandleTimestampKey(candle: MarketCandle): string {
    const parsed = Date.parse(String(candle.timestamp_utc || ''));
    return Number.isFinite(parsed) ? new Date(parsed).toISOString() : String(candle.timestamp_utc || '');
}

function mergeAnalysisCandles(currentCandles: MarketCandle[], analysisCandles: MarketCandle[]): MarketCandle[] {
    if (analysisCandles.length === 0) {
        return currentCandles;
    }
    if (currentCandles.length === 0) {
        return analysisCandles;
    }

    const byTimestamp = new Map<string, MarketCandle>();
    analysisCandles.forEach((candle) => {
        const key = getCandleTimestampKey(candle);
        if (key) {
            byTimestamp.set(key, candle);
        }
    });
    currentCandles.forEach((candle) => {
        const key = getCandleTimestampKey(candle);
        if (key) {
            byTimestamp.set(key, candle);
        }
    });

    return Array.from(byTimestamp.values()).sort((left, right) => (
        Date.parse(getCandleTimestampKey(left)) - Date.parse(getCandleTimestampKey(right))
    ));
}

function buildTradesFromSignalHistory(
    history: OpportunitySignalHistoryItem[] | undefined,
    direction: string,
    includeActiveTrade: boolean,
    currentStateExplanation?: StrategyTrade['current_state_explanation'],
): StrategyTrade[] {
    const sortedHistory = [...(history || [])].sort(
        (left, right) => Date.parse(left.timestamp) - Date.parse(right.timestamp),
    );
    const isShort = direction.toLowerCase() === 'short';
    const trades: StrategyTrade[] = [];
    let activeEntry: OpportunitySignalHistoryItem | null = null;

    sortedHistory.forEach((item) => {
        if (item.type === 'entry') {
            activeEntry = item;
            return;
        }
        if (!activeEntry || item.type !== 'exit') {
            return;
        }

        const entryPrice = Number(activeEntry.price || 0);
        const exitPrice = Number(item.price || 0);
        const profit = entryPrice > 0
            ? (isShort ? (entryPrice - exitPrice) / entryPrice : (exitPrice - entryPrice) / entryPrice)
            : 0;

        trades.push({
            entry_time: activeEntry.timestamp,
            entry_price: entryPrice,
            exit_time: item.timestamp,
            exit_price: exitPrice,
            profit,
            type: isShort ? 'short' : 'long',
            entry_signal_type: isShort ? 'Vender' : 'Comprar',
            signal_type: formatSignalReason(item.reason, direction),
            entry_explanation: activeEntry.explanation,
            exit_explanation: item.explanation,
        });
        activeEntry = null;
    });

    if (activeEntry && includeActiveTrade) {
        trades.push({
            entry_time: activeEntry.timestamp,
            entry_price: Number(activeEntry.price || 0),
            type: isShort ? 'short' : 'long',
            entry_signal_type: isShort ? 'Vender' : 'Comprar',
            entry_explanation: activeEntry.explanation,
            current_state_explanation: currentStateExplanation,
        });
    }

    return trades;
}

function markerTimesMatch(left: StrategyChartMarker['time'], right: StrategyChartMarker['time']): boolean {
    const leftTime = toStrategyChartTimestamp(left);
    const rightTime = toStrategyChartTimestamp(right);
    return Number.isFinite(leftTime) && Number.isFinite(rightTime) && leftTime === rightTime;
}

function hasEquivalentMarker(markers: StrategyChartMarker[], marker: StrategyChartMarker): boolean {
    return markers.some((existing) => (
        markerTimesMatch(existing.time, marker.time)
        && existing.shape === marker.shape
        && existing.position === marker.position
    ));
}

export const ChartModal: React.FC<ChartModalProps> = ({
    symbol,
    opportunity,
    initialCandles,
    initialTimeframe,
    viewMode,
    onClose,
}) => {
    const isTradesView = viewMode === 'trades';
    const isStockAsset = React.useMemo(
        () => getOpportunityAssetType(opportunity) === 'stock',
        [opportunity],
    );
    const strategyTimeframe = React.useMemo(
        () => toChartTimeframe(opportunity.timeframe),
        [opportunity.timeframe],
    );
    const timeframeOptions = React.useMemo(() => {
        const options: TimeframePickerItem[] = [];
        const addOption = (value: ChartTimeframe, label: string, source: TimeframePickerSource) => {
            if (!options.some((item) => item.value === value)) {
                options.push({ value, label, source });
            }
        };

        addOption(strategyTimeframe, `Estratégia (${strategyTimeframe.toUpperCase()})`, 'algorithmic');
        CHART_TIMEFRAMES.forEach((item) => {
            addOption(item, item, 'manual');
        });

        if (isStockAsset) {
            return options.filter((item) => item.value === '1d');
        }
        return options;
    }, [isStockAsset, strategyTimeframe]);
    const supportedTimeframes = React.useMemo(
        () => timeframeOptions.map((item) => item.value),
        [timeframeOptions],
    );
    const defaultRequestedTimeframe = isStockAsset ? '1d' : initialTimeframe;
    const resolvedInitialTimeframe = React.useMemo(() => (
        supportedTimeframes.includes(defaultRequestedTimeframe)
            ? defaultRequestedTimeframe
            : supportedTimeframes[0] ?? '1d'
    ), [defaultRequestedTimeframe, supportedTimeframes]);

    const [timeframe, setTimeframe] = React.useState<ChartTimeframe>(resolvedInitialTimeframe);
    const [candles, setCandles] = React.useState<MarketCandle[]>(initialCandles);
    const [loading, setLoading] = React.useState(false);
    const [error, setError] = React.useState<string | null>(null);
    const [analysisTrades, setAnalysisTrades] = React.useState<StrategyTrade[]>([]);
    const [analysisUsesSignalHistory, setAnalysisUsesSignalHistory] = React.useState(false);
    const [analysisMetrics, setAnalysisMetrics] = React.useState<StrategyTradeMetrics | null>(null);
    const [analysisStrategyTransparency, setAnalysisStrategyTransparency] = React.useState<Record<string, unknown> | null>(null);
    const [analysisCandles, setAnalysisCandles] = React.useState<MarketCandle[]>([]);
    const [analysisTradesLoading, setAnalysisTradesLoading] = React.useState(false);
    const [analysisTradesError, setAnalysisTradesError] = React.useState<string | null>(null);

    const cacheRef = React.useRef<Map<string, MarketCandle[]>>(new Map([
        [`${symbol}|${resolvedInitialTimeframe}`, initialCandles],
    ]));
    const strategyProtected = isProtectedStrategy(opportunity);
    const strategyDisplayName = getStrategyDisplayName(opportunity);
    const activeStrategyTransparency = React.useMemo(
        () => mergeStrategyTransparencySeries(
            analysisStrategyTransparency,
            opportunity.strategy_transparency,
        ),
        [analysisStrategyTransparency, opportunity.strategy_transparency],
    );
    const indicatorConfigurationItems = React.useMemo<StrategyChartConfigurationItem[]>(() => {
        if (!activeStrategyTransparency) return [];

        const indicatorItems = activeStrategyTransparency.indicators.map((indicator) => {
            const parameters = Object.entries(indicator.parameters);
            const configuration = parameters.length > 0
                ? parameters.map(([key, value]) => (
                    parameters.length === 1
                        ? formatStrategyParameterValue(key, value)
                        : `${formatStrategyParameterLabel(key)} ${formatStrategyParameterValue(key, value)}`
                )).join(' • ')
                : 'configuração padrão';
            return {
                label: `${indicator.label} ${configuration}`,
                color: indicator.color,
            };
        });
        const riskItems = Object.entries(activeStrategyTransparency.effective_parameters)
            .filter(([key]) => ['stop_loss', 'take_profit', 'direction'].includes(key))
            .map(([key, value]) => ({
                label: `${formatStrategyParameterLabel(key)} ${formatStrategyParameterValue(key, value)}`,
            }));
        return [...indicatorItems, ...riskItems];
    }, [activeStrategyTransparency]);
    const opportunityDirection = normalizeDirection(String(opportunity.direction ?? opportunity.parameters?.direction ?? 'long'));

    React.useEffect(() => {
        if (!supportedTimeframes.includes(timeframe)) {
            setTimeframe(supportedTimeframes[0] ?? resolvedInitialTimeframe);
        }
    }, [supportedTimeframes, timeframe, resolvedInitialTimeframe]);

    const mergedCandles = React.useMemo(
        () => timeframe === strategyTimeframe ? mergeAnalysisCandles(candles, analysisCandles) : candles,
        [analysisCandles, candles, strategyTimeframe, timeframe],
    );
    const sortedCandles = React.useMemo(
        () => [...mergedCandles].sort((left, right) => Date.parse(left.timestamp_utc) - Date.parse(right.timestamp_utc)),
        [mergedCandles],
    );
    const latestCandle = sortedCandles[sortedCandles.length - 1] ?? null;
    const candleTimes = React.useMemo(
        () => new Set(sortedCandles.map((candle) => toStrategyChartTimestamp(candle.timestamp_utc))),
        [sortedCandles],
    );
    const canRenderSignalHistoryMarkers = React.useMemo(
        () => String(opportunity.timeframe || '').trim().toLowerCase() === timeframe,
        [opportunity.timeframe, timeframe],
    );
    const activeEntrySignal = React.useMemo(
        () => getActiveEntrySignal(opportunity.signal_history),
        [opportunity.signal_history],
    );
    const latestSignal = React.useMemo(
        () => getLatestSignal(opportunity.signal_history),
        [opportunity.signal_history],
    );
    const hasVisibleActiveEntry = React.useMemo(() => {
        if (!activeEntrySignal) {
            return false;
        }
        if (!canRenderSignalHistoryMarkers) {
            return false;
        }
        return candleTimes.has(toStrategyChartTimestamp(activeEntrySignal.timestamp));
    }, [activeEntrySignal, canRenderSignalHistoryMarkers, candleTimes]);
    const historicalSignalMarkers = React.useMemo(() => {
        if (!canRenderSignalHistoryMarkers || sortedCandles.length === 0) {
            return [];
        }

        return (opportunity.signal_history || [])
            .map((item) => {
                const time = toStrategyChartTimestamp(item.timestamp);
                if (!candleTimes.has(time)) {
                    return null;
                }
                return {
                    time,
                    ...getSignalHistoryMarker(item, opportunityDirection),
                };
            })
            .filter((item): item is NonNullable<typeof item> => item !== null);
    }, [canRenderSignalHistoryMarkers, candleTimes, opportunity.signal_history, opportunityDirection, sortedCandles.length]);
    const signalHistory = React.useMemo(
        () => [...(opportunity.signal_history || [])].sort(
            (left, right) => Date.parse(right.timestamp) - Date.parse(left.timestamp),
        ),
        [opportunity.signal_history],
    );
    const signalHistoryTrades = React.useMemo(
        () => buildTradesFromSignalHistory(
            opportunity.signal_history,
            opportunityDirection,
            opportunity.is_holding,
            opportunity.trade_explanation,
        ),
        [opportunity.is_holding, opportunity.signal_history, opportunity.trade_explanation, opportunityDirection],
    );
    const tradeSignalMarkers = React.useMemo<StrategyChartMarker[]>(() => (
        canRenderSignalHistoryMarkers
            ? buildTradeMarkers(analysisTrades, { direction: opportunityDirection, timeframe })
                .filter((marker) => candleTimes.has(toStrategyChartTimestamp(marker.time)))
            : []
    ), [analysisTrades, canRenderSignalHistoryMarkers, candleTimes, opportunityDirection, timeframe]);
    const baseChartMarkers = React.useMemo<StrategyChartMarker[]>(
        () => analysisUsesSignalHistory
            ? historicalSignalMarkers as StrategyChartMarker[]
            : [...tradeSignalMarkers, ...historicalSignalMarkers as StrategyChartMarker[]],
        [analysisUsesSignalHistory, historicalSignalMarkers, tradeSignalMarkers],
    );
    const latestVisibleMarkerType = React.useMemo(
        () => getLatestMarkerSignalType(baseChartMarkers),
        [baseChartMarkers],
    );
    const resolvedSignal = React.useMemo(
        () => resolveOpportunitySignal(opportunity, {
            selectedTimeframe: timeframe,
            latestCandleTime: latestCandle?.timestamp_utc ?? null,
            latestSignalTime: latestSignal?.timestamp ?? null,
            latestSignalType: latestSignal?.type ?? null,
            latestVisibleMarkerType,
            requireCurrentCandleMatch: true,
            hasVisibleActiveEntry,
        }),
        [
            hasVisibleActiveEntry,
            latestCandle?.timestamp_utc,
            latestSignal?.timestamp,
            latestSignal?.type,
            latestVisibleMarkerType,
            opportunity,
            timeframe,
        ],
    );
    const showEntryStopRows = resolvedSignal.section !== 'exit' && !hasExitedOpportunity(opportunity);
    const signalLabel = resolvedSignal.visual.markerLabel;

    React.useEffect(() => {
        const onKeyDown = (event: KeyboardEvent) => {
            if (event.key === 'Escape') {
                onClose();
            }
        };

        const previousOverflow = document.body.style.overflow;
        document.body.style.overflow = 'hidden';
        window.addEventListener('keydown', onKeyDown);

        return () => {
            document.body.style.overflow = previousOverflow;
            window.removeEventListener('keydown', onKeyDown);
        };
    }, [onClose]);

    React.useEffect(() => {
        if (isStockAsset && timeframe !== '1d') {
            setTimeframe('1d');
            return;
        }

        if (!isStockAsset && !supportedTimeframes.includes(timeframe)) {
            setTimeframe(resolvedInitialTimeframe);
            return;
        }

        const cacheKey = `${symbol}|${timeframe}`;
        const cached = cacheRef.current.get(cacheKey);
        if (cached) {
            setCandles(cached);
            setError(null);
            return;
        }

        const controller = new AbortController();

        const run = async () => {
            setLoading(true);
            setError(null);
            try {
                const rows = await fetchMarketCandles(symbol, timeframe, controller.signal);
                if (rows.length === 0) {
                    throw new Error('Sem dados de candle para este timeframe.');
                }
                cacheRef.current.set(cacheKey, rows);
                setCandles(rows);
            } catch (fetchError) {
                if (!controller.signal.aborted) {
                    setError(fetchError instanceof Error ? fetchError.message : 'Falha ao carregar dados do gráfico');
                }
            } finally {
                if (!controller.signal.aborted) {
                    setLoading(false);
                }
            }
        };

        void run();

        return () => controller.abort();
    }, [symbol, timeframe, isStockAsset, supportedTimeframes, resolvedInitialTimeframe]);

    React.useEffect(() => {
        const controller = new AbortController();

        const run = async () => {
            setAnalysisTradesLoading(true);
            setAnalysisTradesError(null);
            try {
                const response = await authFetch(`${API_BASE_URL}/favorites/${opportunity.id}/trades`, {
                    signal: controller.signal,
                });
                const payload = await response.json().catch(() => ({}));
                if (!response.ok) {
                    throw new Error(String(payload?.detail || `Falha ao carregar trades do favorito (${response.status})`));
                }
                const payloadTrades = Array.isArray(payload?.trades) ? payload.trades : [];
                const payloadCandles = Array.isArray(payload?.candles) ? payload.candles : [];
                setAnalysisTrades(payloadTrades.length > 0 ? payloadTrades : signalHistoryTrades);
                setAnalysisUsesSignalHistory(payloadTrades.length === 0);
                setAnalysisCandles(payloadCandles);
                setAnalysisMetrics(payload?.metrics && typeof payload.metrics === 'object' ? payload.metrics : null);
                setAnalysisStrategyTransparency(
                    payload?.strategy_transparency && typeof payload.strategy_transparency === 'object'
                        ? payload.strategy_transparency
                        : null,
                );
            } catch {
                if (!controller.signal.aborted) {
                    setAnalysisTrades(signalHistoryTrades);
                    setAnalysisUsesSignalHistory(true);
                    setAnalysisCandles([]);
                    setAnalysisMetrics(null);
                    setAnalysisStrategyTransparency(null);
                    setAnalysisTradesError(signalHistoryTrades.length > 0 ? null : 'Trades do favorito indisponíveis.');
                }
            } finally {
                if (!controller.signal.aborted) {
                    setAnalysisTradesLoading(false);
                }
            }
        };

        void run();

        return () => controller.abort();
    }, [opportunity.id, signalHistoryTrades]);

    const fallbackMarker = React.useMemo<StrategyChartMarker[]>(() => (
        latestCandle ? [{
            time: toStrategyChartTimestamp(latestCandle.timestamp_utc),
            position: resolvedSignal.visual.markerPosition as StrategyChartMarker['position'],
            color: resolvedSignal.visual.markerColor,
            shape: resolvedSignal.visual.markerShape as StrategyChartMarker['shape'],
            text: signalLabel,
            signalType: resolvedSignal.section === 'hold' ? 'entry' : 'exit',
        }] : []
    ), [
        latestCandle?.timestamp_utc,
        resolvedSignal.visual.markerColor,
        resolvedSignal.visual.markerPosition,
        resolvedSignal.visual.markerShape,
        signalLabel,
    ]);
    const chartMarkers = React.useMemo<StrategyChartMarker[]>(() => {
        const resolvedMarkerType = resolvedSignal.section === 'hold' ? 'entry' : 'exit';
        const shouldAddFallbackMarker = latestVisibleMarkerType !== resolvedMarkerType;
        const fallbackCandidates = shouldAddFallbackMarker ? fallbackMarker : [];
        const mergedMarkers = baseChartMarkers.length > 0
            ? [
                ...baseChartMarkers,
                ...fallbackCandidates.filter((marker) => (
                    !hasEquivalentMarker(baseChartMarkers, marker)
                    && !baseChartMarkers.some((existing) => sameDisplayedCandle(existing.time, marker.time, timeframe))
                )),
            ]
            : fallbackCandidates;

        return collapseSameCandleOppositeMarkers(mergedMarkers, timeframe);
    }, [baseChartMarkers, fallbackMarker, latestVisibleMarkerType, resolvedSignal.section, timeframe]);
    const priceLines = React.useMemo<StrategyChartPriceLine[]>(() => [
        ...(showEntryStopRows && opportunity.entry_price !== null && opportunity.entry_price !== undefined
            ? [{ price: opportunity.entry_price, color: '#fcd535', title: opportunityDirection === 'short' ? 'Venda/Short' : 'Compra' }]
            : []),
        ...(showEntryStopRows && opportunity.stop_price !== null && opportunity.stop_price !== undefined
            ? [{ price: opportunity.stop_price, color: '#f6465d', title: 'STOP' }]
            : []),
    ], [opportunity.entry_price, opportunity.stop_price, opportunityDirection, showEntryStopRows]);
    const summaryItems: StrategyChartSummaryItem[] = [
        { label: 'Candle', value: formatTimestamp(latestCandle?.timestamp_utc) },
        {
            label: `Ate ${resolvedSignal.visual.distanceLabel}`,
            value: formatPercent(opportunity.distance_to_next_status),
            tone: (opportunity.distance_to_next_status ?? 999) < 0.5 ? 'success' : 'default',
        },
        { label: 'Risco', value: formatPercent(opportunity.distance_to_stop_pct), tone: 'danger' },
        { label: 'Histórico', value: `${signalHistory.length} sinais` },
    ];
    const timeframeToolbar = (
        <div className="flex flex-wrap items-center gap-2" role="group" aria-label="Selecionar timeframe do gráfico">
            {timeframeOptions.map((item) => {
                const active = item.value === timeframe;
                return (
                    <button
                        key={item.value}
                        type="button"
                        className={`min-h-11 rounded-md border px-3 py-2 text-sm font-medium transition focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#3b82f6] ${
                            active
                                ? 'border-[#fcd535] bg-[#fcd535]/16 text-[#eaecef]'
                                : 'border-[#2b3139] bg-[#0b0e11] text-[#929aa5] hover:border-[#fcd535] hover:text-[#eaecef]'
                        }`}
                        onClick={() => setTimeframe(item.value)}
                        aria-pressed={active}
                        title={item.source === 'algorithmic' ? 'Timeframe da estratégia' : 'Timeframe manual'}
                        data-testid={`chart-timeframe-${item.value}`}
                    >
                        {item.label}
                    </button>
                );
            })}
        </div>
    );
    const sideContent = (snapshot: StrategyChartSnapshot | null) => (
        <div className="space-y-3 text-sm text-[#eaecef]">
            <section>
                <p className="text-[10px] font-semibold uppercase tracking-normal text-[#929aa5]">Contexto do sinal</p>
                <div
                    className="mt-2 space-y-2 rounded-lg border border-[#2b3139] bg-[#0b0e11] p-3"
                    data-testid="chart-modal-signal-context"
                >
                    <div className="flex justify-between gap-3">
                        <span className="text-[#929aa5]">Sinal</span>
                        <span className="font-mono text-[#eaecef]">{resolvedSignal.visual.badgeText}</span>
                    </div>
                    <div className="flex justify-between gap-3">
                        <span className="text-[#929aa5]">Timeframe estrategia</span>
                        <span className="font-mono text-[#eaecef]">{resolvedSignal.strategyTimeframe ?? '-'}</span>
                    </div>
                    <div className="flex justify-between gap-3">
                        <span className="text-[#929aa5]">Timeframe exibido</span>
                        <span className="font-mono text-[#eaecef]">{resolvedSignal.displayTimeframe ?? '-'}</span>
                    </div>
                    <div className="rounded-md border border-[#2b3139] bg-[#1e2329] px-3 py-2 text-xs text-[#eaecef]">
                        {resolvedSignal.statusMessage}
                        {resolvedSignal.freshnessReason ? ` ${resolvedSignal.freshnessReason}` : ''}
                    </div>
                </div>
            </section>

            <section>
                <p className="text-[10px] font-semibold uppercase tracking-normal text-[#929aa5]">Candle</p>
                <div className="mt-2 grid grid-cols-2 gap-2 rounded-lg border border-[#2b3139] bg-[#0b0e11] p-3">
                    <div>
                        <p className="text-[11px] uppercase tracking-normal text-[#929aa5]">Abertura</p>
                        <p className="font-mono text-sm text-[#eaecef]">{formatPrice(snapshot?.candle.open)}</p>
                    </div>
                    <div>
                        <p className="text-[11px] uppercase tracking-normal text-[#929aa5]">Fechamento</p>
                        <p className="font-mono text-sm text-[#eaecef]">{formatPrice(snapshot?.candle.close)}</p>
                    </div>
                    <div>
                        <p className="text-[11px] uppercase tracking-normal text-[#929aa5]">Máxima</p>
                        <p className="font-mono text-sm text-[#eaecef]">{formatPrice(snapshot?.candle.high)}</p>
                    </div>
                    <div>
                        <p className="text-[11px] uppercase tracking-normal text-[#929aa5]">Mínima</p>
                        <p className="font-mono text-sm text-[#eaecef]">{formatPrice(snapshot?.candle.low)}</p>
                    </div>
                    <div className="col-span-2">
                        <p className="text-[11px] uppercase tracking-normal text-[#929aa5]">Volume</p>
                        <p className="font-mono text-sm text-[#eaecef]">
                            {snapshot?.candle.volume?.toLocaleString('en-US') ?? '-'}
                        </p>
                    </div>
                </div>
            </section>

            <section>
                <p className="text-[10px] font-semibold uppercase tracking-normal text-[#929aa5]">Risco / Stop</p>
                <div className="mt-2 space-y-2 rounded-lg border border-[#2b3139] bg-[#0b0e11] p-3">
                    {showEntryStopRows ? (
                        <>
                            <div className="flex justify-between gap-3">
                                <span className="text-[#929aa5]">Compra</span>
                                <span className="font-mono text-[#eaecef]">{formatPrice(opportunity.entry_price)}</span>
                            </div>
                            <div className="flex justify-between gap-3">
                                <span className="text-[#929aa5]">Stop</span>
                                <span className="font-mono text-[#f6465d]">{formatPrice(opportunity.stop_price)}</span>
                            </div>
                        </>
                    ) : null}
                    <div className="flex justify-between gap-3">
                        <span className="text-[#929aa5]">Risco</span>
                        <span className="font-mono text-[#f6465d]">{formatPercent(opportunity.distance_to_stop_pct)}</span>
                    </div>
                </div>
            </section>

            <section>
                <div className="flex items-center justify-between gap-3">
                    <p className="text-[10px] font-semibold uppercase tracking-normal text-[#929aa5]">Histórico de sinais</p>
                    <span className="text-[11px] text-[#929aa5]">
                        {canRenderSignalHistoryMarkers ? 'Marcadores ativos' : 'Timeframe diferente'}
                    </span>
                </div>
                <div className="mt-2 rounded-lg border border-[#2b3139] bg-[#0b0e11] p-3">
                    {signalHistory.length > 0 ? (
                        <div className="space-y-2" data-testid="chart-modal-signal-history">
                            {signalHistory.slice(0, 5).map((item, index) => {
                                const marker = getSignalHistoryMarker(item);
                                return (
                                    <div
                                        key={`${item.timestamp}-${item.type}-${index}`}
                                        className="flex items-start justify-between gap-3 rounded-md border border-[#2b3139] bg-[#1e2329] px-3 py-2"
                                        data-testid={`chart-modal-signal-history-item-${index}`}
                                    >
                                        <div className="space-y-1">
                                            <div className="flex items-center gap-2">
                                                <span className="h-2.5 w-2.5 rounded-full" style={{ backgroundColor: marker.color }} />
                                                <span className="font-mono text-sm text-[#eaecef]">{getSignalHistoryLabel(item)}</span>
                                                <span className="text-xs text-[#929aa5]">{formatSignalReason(item.reason)}</span>
                                            </div>
                                            <p className="text-xs text-[#929aa5]">{formatTimestamp(item.timestamp)}</p>
                                        </div>
                                        <span className="font-mono text-sm text-[#eaecef]">{formatPrice(item.price)}</span>
                                    </div>
                                );
                            })}
                        </div>
                    ) : (
                        <p className="text-[#929aa5]">Nenhum histórico confirmado de compra/venda para esta estratégia.</p>
                    )}
                </div>
            </section>

            <section>
                <p className="text-[10px] font-semibold uppercase tracking-normal text-[#929aa5]">Parâmetros</p>
                <div className="mt-2 space-y-2 rounded-lg border border-[#2b3139] bg-[#0b0e11] p-3" data-testid="chart-modal-parameters">
                    {activeStrategyTransparency && Object.keys(activeStrategyTransparency.effective_parameters).length > 0 ? (
                        Object.entries(activeStrategyTransparency.effective_parameters).map(([key, value]) => (
                            <div key={key} className="flex justify-between gap-3">
                                <span className="text-[#929aa5]">{formatStrategyParameterLabel(key)}</span>
                                <span className="font-mono text-[#eaecef]">{formatStrategyParameterValue(key, value)}</span>
                            </div>
                        ))
                    ) : !strategyProtected && opportunity.parameters && Object.keys(opportunity.parameters).length > 0 ? (
                        Object.entries(opportunity.parameters).map(([key, value]) => (
                            <div key={key} className="flex justify-between gap-3">
                                <span className="text-[#929aa5]">{formatStrategyParameterLabel(key)}</span>
                                <span className="font-mono text-[#eaecef]">{formatStrategyParameterValue(key, value)}</span>
                            </div>
                        ))
                    ) : (
                        <p className="text-[#929aa5]">Sem parâmetros disponíveis.</p>
                    )}
                </div>
            </section>

            <section>
                <p className="text-[10px] font-semibold uppercase tracking-normal text-[#929aa5]">Notas</p>
                <div className="mt-2 rounded-lg border border-[#2b3139] bg-[#0b0e11] p-3">
                    <p className="whitespace-pre-wrap text-sm text-[#eaecef]">
                        {opportunity.notes?.trim() ? opportunity.notes : 'Sem notas para esta estrategia.'}
                    </p>
                </div>
            </section>
        </div>
    );

    const modalContent = (
        <div
            className="fixed inset-0 z-[1000] bg-[#0b0e11]/88 px-3 py-4 sm:px-6"
            style={{ zIndex: 2147483647 }}
            onClick={(event) => {
                if (event.target === event.currentTarget) {
                    onClose();
                }
            }}
            data-testid="chart-modal-backdrop"
        >
            <div
                className="mx-auto flex h-full max-h-[98vh] w-full max-w-[min(98vw,1680px)] flex-col overflow-hidden rounded-lg border border-[#2b3139] bg-[#0b0e11] text-[#eaecef] shadow-[0_30px_90px_rgba(0,0,0,0.62)]"
                role="dialog"
                aria-modal="true"
                aria-labelledby="chart-modal-title"
                data-testid="chart-modal"
            >
                <StrategyChartSurface
                    candles={sortedCandles}
                    markers={chartMarkers}
                    priceLines={priceLines}
                    strategyName={strategyDisplayName}
                    symbol={symbol}
                    timeframe={timeframe.toUpperCase()}
                    strategyTransparency={activeStrategyTransparency}
                    title={<span id="chart-modal-title">{symbol}</span>}
                    subtitle={`${strategyDisplayName} • ${timeframe.toUpperCase()} • ${sortedCandles.length} velas • candle ref ${formatTimestamp(opportunity.indicator_values_candle_time)}`}
                    headerMeta={(
                        <span
                            className={`rounded-md px-2.5 py-1 text-xs font-semibold uppercase tracking-normal ${resolvedSignal.visual.badgeClass}`}
                            data-testid="chart-modal-signal-badge"
                        >
                            {resolvedSignal.visual.badgeText}
                        </span>
                    )}
                    configurationItems={indicatorConfigurationItems}
                    headerActions={(
                        <div className="flex items-start gap-3">
                            <div className="rounded-lg border border-[#2b3139] bg-[#1e2329] px-4 py-3 text-right">
                                <p className="text-[10px] font-semibold uppercase tracking-normal text-[#929aa5]">Ultimo preco</p>
                                <p className="mt-1 font-mono text-xl font-semibold text-[#eaecef]">
                                    {formatPrice(latestCandle?.close ?? opportunity.last_price)}
                                </p>
                            </div>
                            <button
                                type="button"
                                className="grid h-11 w-11 place-items-center rounded-lg border border-[#2b3139] bg-[#1e2329] text-2xl leading-none text-[#929aa5] transition hover:border-[#fcd535] hover:text-[#eaecef] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#3b82f6]"
                                onClick={onClose}
                                aria-label="Fechar modal do gráfico"
                                data-testid="chart-modal-close"
                            >
                                x
                            </button>
                        </div>
                    )}
                    toolbarLeading={timeframeToolbar}
                    summaryItems={isTradesView ? summaryItems : undefined}
                    summaryTestId="chart-modal-strategy-summary"
                    sideContent={isTradesView ? sideContent : undefined}
                    showSideContent={isTradesView}
                    belowContent={isTradesView ? (
                        <StrategyTradesTable
                            trades={analysisTrades}
                            candles={sortedCandles}
                            direction={opportunityDirection}
                            metrics={analysisMetrics}
                            loading={analysisTradesLoading}
                            error={analysisTradesError}
                            testId="chart-modal-trades"
                            strategyTransparency={activeStrategyTransparency}
                        />
                    ) : undefined}
                    footerContent={(
                        <div className="flex flex-wrap items-center gap-3 text-xs text-[#929aa5]">
                            <span className="inline-flex items-center gap-2"><span className="h-2 w-2 rounded-full bg-[#fcd535]" /> Compra</span>
                            <span className="inline-flex items-center gap-2"><span className="h-2 w-2 rounded-full bg-[#f6465d]" /> Stop</span>
                            <span className="inline-flex items-center gap-2"><span className="h-2 w-2 rounded-full bg-[#0ecb81]" /> Entrada</span>
                            <span className="inline-flex items-center gap-2"><span className="h-2 w-2 rounded-full bg-[#f6465d]" /> Venda</span>
                        </div>
                    )}
                    loading={loading}
                    error={error}
                    markerCount={chartMarkers.length}
                    currentMarkerLabel={signalLabel}
                    rootTestId="chart-modal-surface"
                    chartTestId="chart-modal-main-chart"
                    shellTestId="chart-modal-main-chart-shell"
                    zoomTestIdPrefix="chart"
                    visibleBarsTestId="chart-visible-bars"
                    heightClassName="h-[420px] w-full sm:h-[560px] xl:h-full xl:min-h-[calc(100vh-330px)]"
                    gridClassName="grid min-h-0 flex-1 gap-3 overflow-auto p-3 sm:p-4 xl:grid-cols-[minmax(0,1fr)_320px]"
                    sideClassName="rounded-lg border border-[#2b3139] bg-[#1e2329] p-3 xl:max-h-[calc(100vh-276px)] xl:overflow-auto"
                    className="flex min-h-0 flex-1 flex-col border-0"
                />
            </div>
        </div>
    );

    return createPortal(modalContent, document.body);
};
