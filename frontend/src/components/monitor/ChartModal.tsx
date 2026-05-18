import React from 'react';
import { Minus, Plus, RotateCcw } from 'lucide-react';
import {
    ColorType,
    CrosshairMode,
    LineStyle,
    type IChartApi,
    type LogicalRange,
    type Time,
    type UTCTimestamp,
    createChart,
} from 'lightweight-charts';

import type { MarketCandle } from './MiniCandlesChart';
import {
    getOpportunityAssetType,
    getStrategyDisplayName,
    isProtectedStrategy,
    type Opportunity,
    type OpportunitySignalHistoryItem,
} from './types';
import { CHART_TIMEFRAMES, fetchMarketCandles, toChartTimeframe, type ChartTimeframe } from './chartData';
import { hasExitedOpportunity, resolveOpportunitySignal } from './signalResolution';

interface ChartModalProps {
    symbol: string;
    opportunity: Opportunity;
    initialCandles: MarketCandle[];
    initialTimeframe: ChartTimeframe;
    onClose: () => void;
}

type TimeframePickerSource = 'algorithmic' | 'manual';
type TimeframePickerItem = {
    value: ChartTimeframe;
    label: string;
    source: TimeframePickerSource;
};

type TooltipSnapshot = {
    candle: MarketCandle;
};
const LOGICAL_RANGE_PADDING = 8;
const MIN_VISIBLE_BARS = 12;
const ZOOM_STEP_FACTOR = 0.75;

const PRICE_FORMATTER = new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 2,
    maximumFractionDigits: 8,
});

function toUtcTimestamp(value: string): UTCTimestamp {
    return Math.floor(new Date(value).getTime() / 1000) as UTCTimestamp;
}

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

function getVisibleBarCount(range: LogicalRange | null) {
    if (!range) {
        return null;
    }
    return Math.max(1, Math.round(range.to - range.from));
}

function clampLogicalRange(center: number, span: number, candleCount: number): LogicalRange {
    const minFrom = -LOGICAL_RANGE_PADDING;
    const maxTo = Math.max(candleCount - 1, 0) + LOGICAL_RANGE_PADDING;
    const maxSpan = Math.max(MIN_VISIBLE_BARS, maxTo - minFrom);
    const nextSpan = Math.max(1, Math.min(span, maxSpan));

    let from = center - nextSpan / 2;
    let to = center + nextSpan / 2;

    if (from < minFrom) {
        const shift = minFrom - from;
        from += shift;
        to += shift;
    }

    if (to > maxTo) {
        const shift = to - maxTo;
        from -= shift;
        to -= shift;
    }

    return {
        from: Math.max(from, minFrom) as LogicalRange['from'],
        to: Math.min(to, maxTo) as LogicalRange['to'],
    };
}

function formatSignalReason(value?: string | null) {
    const normalized = String(value || '').trim().toLowerCase();
    if (!normalized) {
        return '-';
    }
    if (normalized === 'entry') {
        return 'Compra';
    }
    if (normalized === 'exit') {
        return 'Venda';
    }
    if (normalized === 'exit_logic') {
        return 'Regra de venda';
    }
    if (normalized === 'stop_loss') {
        return 'Stop loss';
    }
    return normalized.replace(/_/g, ' ');
}

function getSignalHistoryLabel(item: OpportunitySignalHistoryItem) {
    return item.type === 'entry' ? 'Compra' : 'Venda';
}

function getSignalHistoryMarker(item: OpportunitySignalHistoryItem) {
    const isEntry = item.type === 'entry';
    const isStop = !isEntry && String(item.reason || '').trim().toLowerCase() === 'stop_loss';
    return {
        position: isEntry ? 'belowBar' : 'aboveBar',
        shape: isEntry ? 'arrowUp' : 'arrowDown',
        color: isEntry ? '#3fb950' : (isStop ? '#f85149' : '#0284c7'),
        text: getSignalHistoryLabel(item),
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

export const ChartModal: React.FC<ChartModalProps> = ({
    symbol,
    opportunity,
    initialCandles,
    initialTimeframe,
    onClose,
}) => {
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
    const [tooltip, setTooltip] = React.useState<TooltipSnapshot | null>(null);
    const [visibleBarCount, setVisibleBarCount] = React.useState<number | null>(null);

    const cacheRef = React.useRef<Map<string, MarketCandle[]>>(new Map([
        [`${symbol}|${resolvedInitialTimeframe}`, initialCandles],
    ]));
    const mainChartRef = React.useRef<HTMLDivElement>(null);
    const mainChartApiRef = React.useRef<IChartApi | null>(null);
    const strategyProtected = isProtectedStrategy(opportunity);
    const strategyDisplayName = getStrategyDisplayName(opportunity);

    React.useEffect(() => {
        if (!supportedTimeframes.includes(timeframe)) {
            setTimeframe(supportedTimeframes[0] ?? resolvedInitialTimeframe);
        }
    }, [supportedTimeframes, timeframe, resolvedInitialTimeframe]);

    const sortedCandles = React.useMemo(
        () => [...candles].sort((left, right) => Date.parse(left.timestamp_utc) - Date.parse(right.timestamp_utc)),
        [candles],
    );
    const candlestickData = React.useMemo(() => (
        sortedCandles.map((candle) => ({
            time: toUtcTimestamp(candle.timestamp_utc),
            open: candle.open,
            high: candle.high,
            low: candle.low,
            close: candle.close,
        }))
    ), [sortedCandles]);

    const volumeData = React.useMemo(() => (
        sortedCandles.map((candle) => ({
            time: toUtcTimestamp(candle.timestamp_utc),
            value: candle.volume,
            color: candle.close >= candle.open ? 'rgba(34, 197, 94, 0.45)' : 'rgba(248, 81, 73, 0.45)',
        }))
    ), [sortedCandles]);
    const tooltipData = React.useMemo(() => (
        new Map<number, TooltipSnapshot>(
            sortedCandles.map((candle) => [toUtcTimestamp(candle.timestamp_utc), { candle }]),
        )
    ), [sortedCandles]);

    const latestCandle = sortedCandles[sortedCandles.length - 1] ?? null;
    const latestSnapshot = React.useMemo(
        () => (latestCandle ? tooltipData.get(toUtcTimestamp(latestCandle.timestamp_utc)) ?? null : null),
        [latestCandle, tooltipData],
    );
    const displaySnapshot = tooltip ?? latestSnapshot;
    const candleTimes = React.useMemo(
        () => new Set(candlestickData.map((point) => point.time)),
        [candlestickData],
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
        return candleTimes.has(toUtcTimestamp(activeEntrySignal.timestamp));
    }, [activeEntrySignal, canRenderSignalHistoryMarkers, candleTimes]);
    const resolvedSignal = React.useMemo(
        () => resolveOpportunitySignal(opportunity, {
            selectedTimeframe: timeframe,
            latestCandleTime: latestCandle?.timestamp_utc ?? null,
            latestSignalTime: latestSignal?.timestamp ?? null,
            latestSignalType: latestSignal?.type ?? null,
            requireCurrentCandleMatch: true,
            hasVisibleActiveEntry,
        }),
        [
            hasVisibleActiveEntry,
            latestCandle?.timestamp_utc,
            latestSignal?.timestamp,
            latestSignal?.type,
            opportunity,
            timeframe,
        ],
    );
    const showEntryStopRows = resolvedSignal.section !== 'exit' && !hasExitedOpportunity(opportunity);
    const signalLabel = resolvedSignal.visual.markerLabel;
    const historicalSignalMarkers = React.useMemo(() => {
        if (!canRenderSignalHistoryMarkers || sortedCandles.length === 0) {
            return [];
        }

        return (opportunity.signal_history || [])
            .map((item) => {
                const time = toUtcTimestamp(item.timestamp);
                if (!candleTimes.has(time)) {
                    return null;
                }
                return {
                    time,
                    ...getSignalHistoryMarker(item),
                };
            })
            .filter((item): item is NonNullable<typeof item> => item !== null);
    }, [canRenderSignalHistoryMarkers, candlestickData, opportunity.signal_history, sortedCandles.length]);
    const signalHistory = React.useMemo(
        () => [...(opportunity.signal_history || [])].sort(
            (left, right) => Date.parse(right.timestamp) - Date.parse(left.timestamp),
        ),
        [opportunity.signal_history],
    );

    const syncVisibleBars = (range: LogicalRange | null) => {
        setVisibleBarCount(getVisibleBarCount(range));
    };

    const applyZoom = (direction: 'in' | 'out') => {
        const mainChart = mainChartApiRef.current;
        if (!mainChart || candlestickData.length === 0) {
            return;
        }

        const currentRange = mainChart.timeScale().getVisibleLogicalRange();
        const currentSpan = currentRange
            ? Math.max(1, currentRange.to - currentRange.from)
            : Math.max(candlestickData.length, MIN_VISIBLE_BARS);
        const zoomMultiplier = direction === 'in' ? ZOOM_STEP_FACTOR : 1 / ZOOM_STEP_FACTOR;
        const nextSpan = direction === 'in'
            ? Math.max(MIN_VISIBLE_BARS, currentSpan * zoomMultiplier)
            : Math.min(candlestickData.length + (LOGICAL_RANGE_PADDING * 2), currentSpan * zoomMultiplier);
        const center = currentRange
            ? (currentRange.from + currentRange.to) / 2
            : (Math.max(candlestickData.length - 1, 0)) / 2;
        const nextRange = clampLogicalRange(center, nextSpan, candlestickData.length);

        mainChart.timeScale().setVisibleLogicalRange(nextRange);
        syncVisibleBars(nextRange);
    };

    const resetZoom = () => {
        const mainChart = mainChartApiRef.current;
        if (!mainChart) {
            return;
        }
        mainChart.timeScale().fitContent();
        syncVisibleBars(mainChart.timeScale().getVisibleLogicalRange());
    };

    const handleChartWheel = (event: React.WheelEvent<HTMLDivElement>) => {
        if (candlestickData.length === 0 || Math.abs(event.deltaY) < 3) {
            return;
        }
        event.preventDefault();
        applyZoom(event.deltaY < 0 ? 'in' : 'out');
    };

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
                    throw new Error('No candle data available for this timeframe.');
                }
                cacheRef.current.set(cacheKey, rows);
                setCandles(rows);
            } catch (fetchError) {
                if (!controller.signal.aborted) {
                    setError(fetchError instanceof Error ? fetchError.message : 'Failed to load chart data');
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
        if (!mainChartRef.current || candlestickData.length === 0) {
            return undefined;
        }

        const mainChart = createChart(mainChartRef.current, {
            autoSize: true,
            layout: {
                background: { type: ColorType.Solid, color: '#0d1117' },
                textColor: '#8b949e',
            },
            grid: {
                vertLines: { color: 'rgba(48, 54, 61, 0.45)' },
                horzLines: { color: 'rgba(48, 54, 61, 0.45)' },
            },
            crosshair: {
                mode: CrosshairMode.Normal,
                vertLine: { color: 'rgba(56, 139, 253, 0.35)', width: 1, labelBackgroundColor: '#161b22' },
                horzLine: { color: 'rgba(56, 139, 253, 0.35)', width: 1, labelBackgroundColor: '#161b22' },
            },
            rightPriceScale: {
                borderColor: 'rgba(48, 54, 61, 0.85)',
                scaleMargins: { top: 0.08, bottom: 0.28 },
            },
            timeScale: {
                borderColor: 'rgba(48, 54, 61, 0.85)',
                timeVisible: true,
                secondsVisible: false,
                rightOffset: 8,
            },
            handleScroll: {
                mouseWheel: true,
                pressedMouseMove: true,
                horzTouchDrag: true,
                vertTouchDrag: true,
            },
            handleScale: {
                mouseWheel: true,
                pinch: true,
                axisPressedMouseMove: true,
                axisDoubleClickReset: true,
            },
        });
        mainChartApiRef.current = mainChart;

        const candleSeries = mainChart.addCandlestickSeries({
            upColor: '#22c55e',
            downColor: '#f85149',
            borderUpColor: '#22c55e',
            borderDownColor: '#f85149',
            wickUpColor: '#22c55e',
            wickDownColor: '#f85149',
            priceLineVisible: false,
        });

        const volumeSeries = mainChart.addHistogramSeries({
            priceScaleId: '',
            priceFormat: { type: 'volume' },
            priceLineVisible: false,
            lastValueVisible: false,
        });
        volumeSeries.priceScale().applyOptions({ scaleMargins: { top: 0.78, bottom: 0 } });

        candleSeries.setData(candlestickData);
        candleSeries.setMarkers(
            historicalSignalMarkers.length > 0
                ? historicalSignalMarkers
                : [
                    {
                        time: candlestickData[candlestickData.length - 1].time,
                        position: resolvedSignal.visual.markerPosition,
                        color: resolvedSignal.visual.markerColor,
                        shape: resolvedSignal.visual.markerShape,
                        text: signalLabel,
                    },
                ],
        );
        volumeSeries.setData(volumeData);

        if (
            showEntryStopRows
            && opportunity.entry_price !== null
            && opportunity.entry_price !== undefined
        ) {
            candleSeries.createPriceLine({
                price: opportunity.entry_price,
                color: '#388bfd',
                lineWidth: 2,
                lineStyle: LineStyle.Dashed,
                axisLabelVisible: true,
                title: 'Compra',
            });
        }
        if (
            showEntryStopRows
            && opportunity.stop_price !== null
            && opportunity.stop_price !== undefined
        ) {
            candleSeries.createPriceLine({
                price: opportunity.stop_price,
                color: '#f85149',
                lineWidth: 2,
                lineStyle: LineStyle.Dashed,
                axisLabelVisible: true,
                title: 'STOP',
            });
        }

        mainChart.timeScale().fitContent();
        const onVisibleRangeChange = (range: LogicalRange | null) => {
            syncVisibleBars(range);
        };
        mainChart.timeScale().subscribeVisibleLogicalRangeChange(onVisibleRangeChange);
        onVisibleRangeChange(mainChart.timeScale().getVisibleLogicalRange());

        const onCrosshairMove = (param: { time?: Time }) => {
            if (typeof param.time !== 'number') {
                setTooltip(null);
                return;
            }
            setTooltip(tooltipData.get(param.time) ?? null);
        };
        mainChart.subscribeCrosshairMove(onCrosshairMove);

        const onResize = () => {
            mainChart.applyOptions({ width: mainChartRef.current?.clientWidth ?? 0 });
        };
        window.addEventListener('resize', onResize);

        return () => {
            window.removeEventListener('resize', onResize);
            mainChart.unsubscribeCrosshairMove(onCrosshairMove);
            mainChart.timeScale().unsubscribeVisibleLogicalRangeChange(onVisibleRangeChange);
            if (mainChartApiRef.current === mainChart) {
                mainChartApiRef.current = null;
            }
            mainChart.remove();
        };
    }, [
        candlestickData,
        historicalSignalMarkers,
        opportunity.entry_price,
        opportunity.stop_price,
        resolvedSignal.visual.markerColor,
        resolvedSignal.visual.markerPosition,
        resolvedSignal.visual.markerShape,
        signalLabel,
        tooltipData,
        showEntryStopRows,
        volumeData,
    ]);

    return (
        <div
            className="fixed inset-0 z-[1000] bg-[#010409]/88 px-3 py-4 sm:px-6"
            onClick={(event) => {
                if (event.target === event.currentTarget) {
                    onClose();
                }
            }}
            data-testid="chart-modal-backdrop"
        >
            <div
                className="mx-auto flex h-full max-h-[98vh] w-full max-w-[min(98vw,1680px)] flex-col overflow-hidden rounded-xl border border-[#263241] bg-[#0b1117] text-[#e6edf3] shadow-[0_30px_90px_rgba(0,0,0,0.62)]"
                role="dialog"
                aria-modal="true"
                aria-labelledby="chart-modal-title"
                data-testid="chart-modal"
            >
                <header className="border-b border-[#263241] bg-[linear-gradient(135deg,rgba(56,139,253,0.10),rgba(13,17,23,0.96)_58%)] px-4 py-4 sm:px-5">
                    <div className="flex flex-wrap items-start gap-4">
                        <div className="flex min-w-0 flex-1 items-start gap-3">
                            <div className="grid h-12 w-12 shrink-0 place-items-center rounded-xl border border-[#f7931a]/35 bg-[linear-gradient(135deg,#f7931a,#7c4a08)] font-mono text-xs font-bold text-white shadow-[0_12px_28px_rgba(247,147,26,0.18)]">
                                {symbol.split('/')[0]?.slice(0, 4) || symbol.slice(0, 4)}
                            </div>
                            <div className="min-w-0">
                                <div className="flex flex-wrap items-center gap-2">
                                    <h2 id="chart-modal-title" className="truncate text-xl font-semibold tracking-normal text-[#f0f6fc]">
                                        {symbol}
                                    </h2>
                                    <span
                                        className={`rounded-md px-2.5 py-1 text-xs font-semibold uppercase tracking-wide ${resolvedSignal.visual.badgeClass}`}
                                        data-testid="chart-modal-signal-badge"
                                    >
                                        {resolvedSignal.visual.badgeText}
                                    </span>
                                </div>
                                <p className="mt-1 text-sm text-[#9fb0c2]">
                                    {strategyDisplayName}
                                </p>
                                <div className="mt-2 flex flex-wrap items-center gap-2 text-xs text-[#8b949e]">
                                    <span className="rounded border border-[#30363d] bg-[#0d1117]/80 px-2 py-1 font-mono text-[#c9d1d9]">{timeframe.toUpperCase()}</span>
                                    <span>{candlestickData.length} candles</span>
                                    <span>candle ref {formatTimestamp(opportunity.indicator_values_candle_time)}</span>
                                </div>
                            </div>
                        </div>

                        <div className="rounded-xl border border-[#263241] bg-[#0d1117]/82 px-4 py-3 text-right">
                            <p className="text-[10px] font-semibold uppercase tracking-[0.16em] text-[#7d8b99]">Ultimo preco</p>
                            <p className="mt-1 font-mono text-xl font-semibold text-[#f0f6fc]">
                                {formatPrice(displaySnapshot?.candle.close ?? opportunity.last_price)}
                            </p>
                        </div>

                        <button
                            type="button"
                            className="grid h-10 w-10 place-items-center rounded-lg border border-[#30363d] bg-[#161b22] text-2xl leading-none text-[#8b949e] transition hover:bg-[#1f2937] hover:text-[#e6edf3]"
                            onClick={onClose}
                            aria-label="Close chart modal"
                            data-testid="chart-modal-close"
                        >
                            ×
                        </button>
                    </div>

                    <div className="mt-4 grid gap-2 md:grid-cols-4" data-testid="chart-modal-strategy-summary">
                        <div className="rounded-lg border border-[#263241] bg-[#0d1117]/78 p-3">
                            <p className="text-[10px] font-semibold uppercase tracking-[0.14em] text-[#7d8b99]">Candle</p>
                            <p className="mt-1 font-mono text-sm text-[#f0f6fc]">{formatTimestamp(displaySnapshot?.candle.timestamp_utc)}</p>
                        </div>
                        <div className="rounded-lg border border-[#263241] bg-[#0d1117]/78 p-3">
                            <p className="text-[10px] font-semibold uppercase tracking-[0.14em] text-[#7d8b99]">Ate {resolvedSignal.visual.distanceLabel}</p>
                            <p className={`mt-1 font-mono text-sm font-semibold ${
                                (opportunity.distance_to_next_status ?? 999) < 0.5 ? 'text-[#3fb950]' : 'text-[#f0f6fc]'
                            }`}>
                                {formatPercent(opportunity.distance_to_next_status)}
                            </p>
                        </div>
                        <div className="rounded-lg border border-[#263241] bg-[#0d1117]/78 p-3">
                            <p className="text-[10px] font-semibold uppercase tracking-[0.14em] text-[#7d8b99]">Risco</p>
                            <p className="mt-1 font-mono text-sm font-semibold text-[#f85149]">{formatPercent(opportunity.distance_to_stop_pct)}</p>
                        </div>
                        <div className="rounded-lg border border-[#263241] bg-[#0d1117]/78 p-3">
                            <p className="text-[10px] font-semibold uppercase tracking-[0.14em] text-[#7d8b99]">Historico</p>
                            <p className="mt-1 font-mono text-sm text-[#f0f6fc]">{signalHistory.length} sinais</p>
                        </div>
                    </div>
                </header>

                <div className="flex min-h-0 flex-1 flex-col">
                    <div className="flex flex-wrap items-center gap-2 border-b border-[#263241] bg-[#0d1117] px-4 py-3 sm:px-5">
                        <div className="flex flex-wrap items-center gap-2" role="group" aria-label="Chart timeframe selector">
                            {timeframeOptions.map((item) => {
                                const active = item.value === timeframe;
                                return (
                                    <button
                                        key={item.value}
                                        type="button"
                                        className={`rounded-md border px-3 py-1.5 text-sm font-medium transition ${
                                            active
                                                ? 'border-[#58a6ff] bg-[#1f6feb]/18 text-[#f0f6fc]'
                                                : 'border-[#263241] bg-[#111820] text-[#8b949e] hover:border-[#3d4d60] hover:text-[#f0f6fc]'
                                        }`}
                                        onClick={() => setTimeframe(item.value)}
                                        aria-pressed={active}
                                        title={item.source === 'algorithmic' ? 'Timeframe da estrategia' : 'Timeframe manual'}
                                        data-testid={`chart-timeframe-${item.value}`}
                                    >
                                        {item.label}
                                    </button>
                                );
                            })}
                        </div>

                        <div
                            className="ml-auto flex flex-wrap items-center gap-2 rounded-lg border border-[#263241] bg-[#111820] px-2 py-2"
                            role="group"
                            aria-label="Chart zoom controls"
                        >
                            <button
                                type="button"
                                className="inline-flex h-9 items-center gap-2 rounded-md border border-[#30363d] bg-[#161b22] px-3 text-sm font-semibold text-[#dbeafe] transition hover:border-[#58a6ff] disabled:cursor-not-allowed disabled:opacity-50"
                                onClick={() => applyZoom('out')}
                                disabled={candlestickData.length === 0}
                                aria-label="Zoom out chart"
                                data-testid="chart-zoom-out"
                            >
                                <Minus className="h-4 w-4" />
                                <span className="hidden sm:inline">Out</span>
                            </button>
                            <button
                                type="button"
                                className="inline-flex h-9 items-center gap-2 rounded-md border border-[#58a6ff]/70 bg-[#1f6feb] px-3 text-sm font-semibold text-white transition hover:bg-[#388bfd] disabled:cursor-not-allowed disabled:opacity-50"
                                onClick={() => applyZoom('in')}
                                disabled={candlestickData.length === 0}
                                aria-label="Zoom in chart"
                                data-testid="chart-zoom-in"
                            >
                                <Plus className="h-4 w-4" />
                                <span className="hidden sm:inline">In</span>
                            </button>
                            <button
                                type="button"
                                className="inline-flex h-9 items-center gap-2 rounded-md border border-[#30363d] bg-[#161b22] px-3 text-sm font-medium text-[#c9d1d9] transition hover:border-[#58a6ff] hover:text-[#e6edf3] disabled:cursor-not-allowed disabled:opacity-50"
                                onClick={resetZoom}
                                disabled={candlestickData.length === 0}
                                aria-label="Reset chart zoom"
                                data-testid="chart-zoom-reset"
                            >
                                <RotateCcw className="h-4 w-4" />
                                <span className="hidden sm:inline">Reset</span>
                            </button>
                            <span
                                className="rounded-md border border-[#30363d] bg-[#0d1117] px-2.5 py-1 text-xs font-medium text-[#c9d1d9]"
                                aria-live="polite"
                                data-testid="chart-visible-bars"
                            >
                                {visibleBarCount ?? 0} candles
                            </span>
                            <span className="text-[11px] text-[#8b949e]">
                                Mouse wheel: zoom
                            </span>
                        </div>
                    </div>

                    <div className="min-h-0 flex-1 overflow-auto p-3 sm:p-4">
                        {error ? (
                            <div className="mb-3 rounded-lg border border-[#f85149]/40 bg-[#f85149]/10 px-4 py-3 text-sm text-[#ffb1ac]">
                                {error}
                            </div>
                        ) : null}

                        <div className="grid min-h-full gap-3 xl:grid-cols-[minmax(0,1fr)_320px]">
                            <div
                                className="relative min-h-[420px] rounded-xl border border-[#263241] bg-[#06090f] p-2 shadow-[inset_0_0_0_1px_rgba(255,255,255,0.02)] sm:min-h-[560px]"
                                onWheel={handleChartWheel}
                                data-testid="chart-modal-main-chart-shell"
                                data-current-marker={signalLabel}
                            >
                                <div
                                    ref={mainChartRef}
                                    className="h-[420px] w-full sm:h-[560px] xl:h-full xl:min-h-[calc(100vh-330px)]"
                                    data-testid="chart-modal-main-chart"
                                />
                                <div className="pointer-events-none absolute left-4 top-4 rounded-full border border-[#58a6ff]/25 bg-[#0d1117]/86 px-3 py-1 text-[11px] font-medium text-[#c9e6ff]">
                                    Scroll to zoom
                                </div>
                                {loading ? (
                                    <div className="absolute right-4 top-4 rounded-md bg-black/60 px-3 py-1.5 text-xs text-white">
                                        Loading timeframe...
                                    </div>
                                ) : null}
                            </div>

                            <aside className="space-y-3 rounded-xl border border-[#263241] bg-[#0d1117] p-3 text-sm text-[#c9d1d9] xl:max-h-[calc(100vh-276px)] xl:overflow-auto">
                                <section>
                                    <p className="text-[10px] font-semibold uppercase tracking-[0.16em] text-[#7d8b99]">Contexto do sinal</p>
                                    <div
                                        className="mt-2 space-y-2 rounded-lg border border-[#263241] bg-[#111820] p-3"
                                        data-testid="chart-modal-signal-context"
                                    >
                                        <div className="flex justify-between gap-3">
                                            <span className="text-[#8b949e]">Sinal</span>
                                            <span className="font-mono text-[#f0f6fc]">{resolvedSignal.visual.badgeText}</span>
                                        </div>
                                        <div className="flex justify-between gap-3">
                                            <span className="text-[#8b949e]">Timeframe estrategia</span>
                                            <span className="font-mono text-[#f0f6fc]">{resolvedSignal.strategyTimeframe ?? '-'}</span>
                                        </div>
                                        <div className="flex justify-between gap-3">
                                            <span className="text-[#8b949e]">Timeframe exibido</span>
                                            <span className="font-mono text-[#f0f6fc]">{resolvedSignal.displayTimeframe ?? '-'}</span>
                                        </div>
                                        <div className="rounded-md border border-[#30363d] bg-[#0d1117] px-3 py-2 text-xs text-[#c9d1d9]">
                                            {resolvedSignal.statusMessage}
                                            {resolvedSignal.freshnessReason ? ` ${resolvedSignal.freshnessReason}` : ''}
                                        </div>
                                    </div>
                                </section>

                                <section>
                                    <p className="text-[10px] font-semibold uppercase tracking-[0.16em] text-[#7d8b99]">Candle</p>
                                    <div className="mt-2 grid grid-cols-2 gap-2 rounded-lg border border-[#263241] bg-[#111820] p-3">
                                        <div>
                                            <p className="text-[11px] uppercase tracking-wide text-[#8b949e]">Open</p>
                                            <p className="font-mono text-sm text-[#f0f6fc]">{formatPrice(displaySnapshot?.candle.open)}</p>
                                        </div>
                                        <div>
                                            <p className="text-[11px] uppercase tracking-wide text-[#8b949e]">Close</p>
                                            <p className="font-mono text-sm text-[#f0f6fc]">{formatPrice(displaySnapshot?.candle.close)}</p>
                                        </div>
                                        <div>
                                            <p className="text-[11px] uppercase tracking-wide text-[#8b949e]">High</p>
                                            <p className="font-mono text-sm text-[#f0f6fc]">{formatPrice(displaySnapshot?.candle.high)}</p>
                                        </div>
                                        <div>
                                            <p className="text-[11px] uppercase tracking-wide text-[#8b949e]">Low</p>
                                            <p className="font-mono text-sm text-[#f0f6fc]">{formatPrice(displaySnapshot?.candle.low)}</p>
                                        </div>
                                        <div className="col-span-2">
                                            <p className="text-[11px] uppercase tracking-wide text-[#8b949e]">Volume</p>
                                            <p className="font-mono text-sm text-[#f0f6fc]">
                                                {displaySnapshot?.candle.volume?.toLocaleString('en-US') ?? '-'}
                                            </p>
                                        </div>
                                    </div>
                                </section>

                                <section>
                                    <p className="text-[10px] font-semibold uppercase tracking-[0.16em] text-[#7d8b99]">Risco / Stop</p>
                                    <div className="mt-2 space-y-2 rounded-lg border border-[#263241] bg-[#111820] p-3">
                                        {showEntryStopRows ? (
                                            <>
                                                <div className="flex justify-between gap-3">
                                                    <span className="text-[#8b949e]">Compra</span>
                                                    <span className="font-mono text-[#f0f6fc]">{formatPrice(opportunity.entry_price)}</span>
                                                </div>
                                                <div className="flex justify-between gap-3">
                                                    <span className="text-[#8b949e]">Stop</span>
                                                    <span className="font-mono text-[#f85149]">{formatPrice(opportunity.stop_price)}</span>
                                                </div>
                                            </>
                                        ) : null}
                                        <div className="flex justify-between gap-3">
                                            <span className="text-[#8b949e]">Risco</span>
                                            <span className="font-mono text-[#f85149]">{formatPercent(opportunity.distance_to_stop_pct)}</span>
                                        </div>
                                    </div>
                                </section>

                                <section>
                                    <div className="flex items-center justify-between gap-3">
                                        <p className="text-[10px] font-semibold uppercase tracking-[0.16em] text-[#7d8b99]">Historico de sinais</p>
                                        <span className="text-[11px] text-[#8b949e]">
                                            {canRenderSignalHistoryMarkers ? 'Marcadores ativos' : 'Timeframe diferente'}
                                        </span>
                                    </div>
                                    <div className="mt-2 rounded-lg border border-[#263241] bg-[#111820] p-3">
                                        {signalHistory.length > 0 ? (
                                            <div className="space-y-2" data-testid="chart-modal-signal-history">
                                                {signalHistory.slice(0, 5).map((item, index) => {
                                                    const marker = getSignalHistoryMarker(item);
                                                    return (
                                                        <div
                                                            key={`${item.timestamp}-${item.type}-${index}`}
                                                            className="flex items-start justify-between gap-3 rounded-md border border-[#263241] bg-[#0d1117] px-3 py-2"
                                                            data-testid={`chart-modal-signal-history-item-${index}`}
                                                        >
                                                            <div className="space-y-1">
                                                                <div className="flex items-center gap-2">
                                                                    <span className="h-2.5 w-2.5 rounded-full" style={{ backgroundColor: marker.color }} />
                                                                    <span className="font-mono text-sm text-[#f0f6fc]">{getSignalHistoryLabel(item)}</span>
                                                                    <span className="text-xs text-[#8b949e]">{formatSignalReason(item.reason)}</span>
                                                                </div>
                                                                <p className="text-xs text-[#8b949e]">{formatTimestamp(item.timestamp)}</p>
                                                            </div>
                                                            <span className="font-mono text-sm text-[#f0f6fc]">{formatPrice(item.price)}</span>
                                                        </div>
                                                    );
                                                })}
                                            </div>
                                        ) : (
                                            <p className="text-[#8b949e]">Nenhum historico confirmado de compra/venda para esta estrategia.</p>
                                        )}
                                    </div>
                                </section>

                                <section>
                                    <p className="text-[10px] font-semibold uppercase tracking-[0.16em] text-[#7d8b99]">Parametros</p>
                                    <div className="mt-2 space-y-2 rounded-lg border border-[#263241] bg-[#111820] p-3">
                                        {strategyProtected ? (
                                            <p className="text-[#8b949e]">Parametros protegidos.</p>
                                        ) : opportunity.parameters && Object.keys(opportunity.parameters).length > 0 ? (
                                            Object.entries(opportunity.parameters).map(([key, value]) => (
                                                <div key={key} className="flex justify-between gap-3">
                                                    <span className="text-[#8b949e]">{key}</span>
                                                    <span className="font-mono text-[#f0f6fc]">{String(value)}</span>
                                                </div>
                                            ))
                                        ) : (
                                            <p className="text-[#8b949e]">Sem parametros disponiveis.</p>
                                        )}
                                    </div>
                                </section>

                                <section>
                                    <p className="text-[10px] font-semibold uppercase tracking-[0.16em] text-[#7d8b99]">Notas</p>
                                    <div className="mt-2 rounded-lg border border-[#263241] bg-[#111820] p-3">
                                        <p className="whitespace-pre-wrap text-sm text-[#c9d1d9]">
                                            {opportunity.notes?.trim() ? opportunity.notes : 'Sem notas para esta estrategia.'}
                                        </p>
                                    </div>
                                </section>
                            </aside>
                        </div>
                    </div>

                    <footer className="border-t border-[#263241] bg-[#0d1117] px-5 py-3">
                        <div className="flex flex-wrap items-center gap-3 text-xs text-[#8b949e]">
                            <span className="inline-flex items-center gap-2"><span className="h-2 w-2 rounded-full bg-[#388bfd]" /> Compra</span>
                            <span className="inline-flex items-center gap-2"><span className="h-2 w-2 rounded-full bg-[#f85149]" /> Stop</span>
                            <span className="inline-flex items-center gap-2"><span className="h-2 w-2 rounded-full bg-[#3fb950]" /> Entrada</span>
                            <span className="inline-flex items-center gap-2"><span className="h-2 w-2 rounded-full bg-[#f85149]" /> Venda</span>
                        </div>
                    </footer>
                </div>
            </div>
        </div>
    );
};
