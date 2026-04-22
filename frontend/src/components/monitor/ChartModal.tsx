import React from 'react';
import { Minus, Plus, RotateCcw } from 'lucide-react';
import {
    ColorType,
    CrosshairMode,
    LineStyle,
    type IChartApi,
    type LineData,
    type LogicalRange,
    type Time,
    type UTCTimestamp,
    createChart,
} from 'lightweight-charts';

import type { MarketCandle } from './MiniCandlesChart';
import { getOpportunityAssetType, type Opportunity, type OpportunitySignalHistoryItem } from './types';
import { CHART_TIMEFRAMES, fetchMarketCandles, toChartTimeframe, type ChartTimeframe } from './chartData';
import { resolveOpportunitySignal } from './signalResolution';

interface ChartModalProps {
    symbol: string;
    opportunity: Opportunity;
    initialCandles: MarketCandle[];
    initialTimeframe: ChartTimeframe;
    onClose: () => void;
}

type IndicatorKey = 'emaShort' | 'smaMedium' | 'smaLong';
type TimeframePickerSource = 'algorithmic' | 'manual';
type TimeframePickerItem = {
    value: ChartTimeframe;
    label: string;
    source: TimeframePickerSource;
};

interface IndicatorState {
    emaShort: boolean;
    smaMedium: boolean;
    smaLong: boolean;
}

interface TooltipSnapshot {
    candle: MarketCandle;
    emaShort?: number;
    smaMedium?: number;
    smaLong?: number;
}

const DEFAULT_INDICATORS: IndicatorState = {
    emaShort: true,
    smaMedium: true,
    smaLong: true,
};
const LOGICAL_RANGE_PADDING = 8;
const MIN_VISIBLE_BARS = 12;
const ZOOM_STEP_FACTOR = 0.75;
const MA_COLORS = ['#FF5252', '#FF9800', '#1565C0'] as const;
type MAIndicatorKey = 'emaShort' | 'smaMedium' | 'smaLong';
type MAColorByIndicator = Record<MAIndicatorKey, string>;

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

function formatIndicator(value?: number | null) {
    if (value === null || value === undefined || Number.isNaN(value)) {
        return '-';
    }
    return value.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 4 });
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
        return 'Entry';
    }
    if (normalized === 'exit_logic') {
        return 'Exit rule';
    }
    if (normalized === 'stop_loss') {
        return 'Stop loss';
    }
    return normalized.replace(/_/g, ' ');
}

function getSignalHistoryLabel(item: OpportunitySignalHistoryItem) {
    return item.type === 'entry' ? 'ENTRY' : 'EXIT';
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

function getNumericParameter(parameters: Record<string, unknown> | undefined, keys: string[], fallback: number) {
    for (const key of keys) {
        const raw = parameters?.[key];
        const value = typeof raw === 'number' ? raw : Number(raw);
        if (Number.isFinite(value) && value > 0) {
            return value;
        }
    }
    return fallback;
}

function getIndicatorValue(values: Record<string, number> | undefined, keys: string[], fallback?: number | null) {
    for (const key of keys) {
        const value = values?.[key];
        if (value !== undefined && value !== null && !Number.isNaN(value)) {
            return value;
        }
    }
    return fallback ?? undefined;
}

function getMAColorsByPeriod(indicatorPeriods: { emaShort: number; smaMedium: number; smaLong: number }): MAColorByIndicator {
    const ordered = [
        { key: 'emaShort' as const, period: indicatorPeriods.emaShort, order: 0 },
        { key: 'smaMedium' as const, period: indicatorPeriods.smaMedium, order: 1 },
        { key: 'smaLong' as const, period: indicatorPeriods.smaLong, order: 2 },
    ].sort((a, b) => {
        if (a.period === b.period) {
            return a.order - b.order;
        }
        return a.period - b.period;
    });

    const map = {
        emaShort: MA_COLORS[2],
        smaMedium: MA_COLORS[2],
        smaLong: MA_COLORS[2],
    } as MAColorByIndicator;

    ordered.forEach((item, index) => {
        map[item.key] = MA_COLORS[index];
    });

    return map;
}

function calculateSma(candles: MarketCandle[], period: number): LineData<Time>[] {
    const result: LineData<Time>[] = [];
    let rollingSum = 0;

    candles.forEach((candle, index) => {
        rollingSum += candle.close;
        if (index >= period) {
            rollingSum -= candles[index - period].close;
        }
        if (index >= period - 1) {
            result.push({
                time: toUtcTimestamp(candle.timestamp_utc),
                value: rollingSum / period,
            });
        }
    });

    return result;
}

function calculateEma(candles: MarketCandle[], period: number): LineData<Time>[] {
    if (candles.length < period) {
        return [];
    }

    const multiplier = 2 / (period + 1);
    const result: LineData<Time>[] = [];
    let ema = candles.slice(0, period).reduce((sum, candle) => sum + candle.close, 0) / period;

    result.push({
        time: toUtcTimestamp(candles[period - 1].timestamp_utc),
        value: ema,
    });

    for (let index = period; index < candles.length; index += 1) {
        ema = (candles[index].close - ema) * multiplier + ema;
        result.push({
            time: toUtcTimestamp(candles[index].timestamp_utc),
            value: ema,
        });
    }

    return result;
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

        addOption(strategyTimeframe, `Algorítmica (${strategyTimeframe.toUpperCase()})`, 'algorithmic');
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
    const [visibleIndicators, setVisibleIndicators] = React.useState<IndicatorState>(DEFAULT_INDICATORS);
    const [tooltip, setTooltip] = React.useState<TooltipSnapshot | null>(null);
    const [visibleBarCount, setVisibleBarCount] = React.useState<number | null>(null);
    const [chartMode, setChartMode] = React.useState<'compact' | 'algorithmic'>('algorithmic');

    const cacheRef = React.useRef<Map<string, MarketCandle[]>>(new Map([
        [`${symbol}|${resolvedInitialTimeframe}`, initialCandles],
    ]));
    const mainChartRef = React.useRef<HTMLDivElement>(null);
    const mainChartApiRef = React.useRef<IChartApi | null>(null);

    React.useEffect(() => {
        if (!supportedTimeframes.includes(timeframe)) {
            setTimeframe(supportedTimeframes[0] ?? resolvedInitialTimeframe);
        }
    }, [supportedTimeframes, timeframe, resolvedInitialTimeframe]);

    const sortedCandles = React.useMemo(
        () => [...candles].sort((left, right) => Date.parse(left.timestamp_utc) - Date.parse(right.timestamp_utc)),
        [candles],
    );
    const indicatorPeriods = React.useMemo(() => ({
        emaShort: getNumericParameter(opportunity.parameters, ['ema_short', 'emaShort', 'sma_short', 'smaShort'], 9),
        smaMedium: getNumericParameter(opportunity.parameters, ['sma_medium', 'smaMedium', 'ema_medium', 'emaMedium'], 21),
        smaLong: getNumericParameter(opportunity.parameters, ['sma_long', 'smaLong', 'ema_long', 'emaLong'], 50),
    }), [opportunity.parameters]);
    const maColors = React.useMemo(() => getMAColorsByPeriod({
        emaShort: indicatorPeriods.emaShort,
        smaMedium: indicatorPeriods.smaMedium,
        smaLong: indicatorPeriods.smaLong,
    }), [indicatorPeriods.emaShort, indicatorPeriods.smaMedium, indicatorPeriods.smaLong]);
    const indicatorLabels = React.useMemo(() => ({
        emaShort: `EMA ${indicatorPeriods.emaShort}`,
        smaMedium: `SMA ${indicatorPeriods.smaMedium}`,
        smaLong: `SMA ${indicatorPeriods.smaLong}`,
    }), [indicatorPeriods]);

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

    const emaShortData = React.useMemo(
        () => calculateEma(sortedCandles, indicatorPeriods.emaShort),
        [indicatorPeriods.emaShort, sortedCandles],
    );
    const smaMediumData = React.useMemo(
        () => calculateSma(sortedCandles, indicatorPeriods.smaMedium),
        [indicatorPeriods.smaMedium, sortedCandles],
    );
    const smaLongData = React.useMemo(
        () => calculateSma(sortedCandles, indicatorPeriods.smaLong),
        [indicatorPeriods.smaLong, sortedCandles],
    );
    const tooltipData = React.useMemo(() => {
        const emaShortMap = new Map<number, number>();
        const smaMediumMap = new Map<number, number>();
        const smaLongMap = new Map<number, number>();

        emaShortData.forEach((point) => {
            if (typeof point.time === 'number') {
                emaShortMap.set(point.time, point.value);
            }
        });
        smaMediumData.forEach((point) => {
            if (typeof point.time === 'number') {
                smaMediumMap.set(point.time, point.value);
            }
        });
    smaLongData.forEach((point) => {
        if (typeof point.time === 'number') {
            smaLongMap.set(point.time, point.value);
        }
    });
    return new Map<number, TooltipSnapshot>(
            sortedCandles.map((candle) => {
                const time = toUtcTimestamp(candle.timestamp_utc);
                return [
                    time,
                    {
                        candle,
                        emaShort: emaShortMap.get(time),
                        smaMedium: smaMediumMap.get(time),
                        smaLong: smaLongMap.get(time),
                    },
                ];
            }),
        );
    }, [emaShortData, smaLongData, smaMediumData, sortedCandles]);

    const latestCandle = sortedCandles[sortedCandles.length - 1] ?? null;
    const latestSnapshot = React.useMemo(
        () => (latestCandle ? tooltipData.get(toUtcTimestamp(latestCandle.timestamp_utc)) ?? null : null),
        [latestCandle, tooltipData],
    );
    const isAlgorithmicChartMode = chartMode === 'algorithmic';

    const displaySnapshot = tooltip ?? latestSnapshot;
    const resolvedSignal = React.useMemo(
        () => resolveOpportunitySignal(opportunity, {
            selectedTimeframe: timeframe,
            latestCandleTime: latestCandle?.timestamp_utc ?? null,
            requireCurrentCandleMatch: true,
        }),
        [latestCandle?.timestamp_utc, opportunity, timeframe],
    );
    const signalLabel = resolvedSignal.visual.markerLabel;
    const canRenderSignalHistoryMarkers = React.useMemo(
        () => String(opportunity.timeframe || '').trim().toLowerCase() === timeframe,
        [opportunity.timeframe, timeframe],
    );
    const historicalSignalMarkers = React.useMemo(() => {
        if (!canRenderSignalHistoryMarkers || sortedCandles.length === 0) {
            return [];
        }

        const candleTimes = new Set(candlestickData.map((point) => point.time));
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

    const toggleIndicator = (key: IndicatorKey) => {
        setVisibleIndicators((current) => ({ ...current, [key]: !current[key] }));
    };

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

        const emaShortSeries = mainChart.addLineSeries({
            color: maColors.emaShort,
            lineWidth: 2,
            visible: visibleIndicators.emaShort,
            priceLineVisible: false,
            lastValueVisible: false,
        });

        const smaMediumSeries = mainChart.addLineSeries({
            color: maColors.smaMedium,
            lineWidth: 2,
            visible: visibleIndicators.smaMedium,
            priceLineVisible: false,
            lastValueVisible: false,
        });

        const smaLongSeries = mainChart.addLineSeries({
            color: maColors.smaLong,
            lineWidth: 2,
            visible: visibleIndicators.smaLong,
            priceLineVisible: false,
            lastValueVisible: false,
        });

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
        emaShortSeries.setData(emaShortData);
        smaMediumSeries.setData(smaMediumData);
        smaLongSeries.setData(smaLongData);

        if (opportunity.entry_price !== null && opportunity.entry_price !== undefined) {
            candleSeries.createPriceLine({
                price: opportunity.entry_price,
                color: '#388bfd',
                lineWidth: 2,
                lineStyle: LineStyle.Dashed,
                axisLabelVisible: true,
                title: 'ENTRY',
            });
        }
        if (opportunity.stop_price !== null && opportunity.stop_price !== undefined) {
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
        emaShortData,
        indicatorPeriods.emaShort,
        indicatorPeriods.smaLong,
        indicatorPeriods.smaMedium,
        maColors.emaShort,
        maColors.smaLong,
        maColors.smaMedium,
        historicalSignalMarkers,
        opportunity.entry_price,
        opportunity.stop_price,
        resolvedSignal.visual.markerColor,
        resolvedSignal.visual.markerPosition,
        resolvedSignal.visual.markerShape,
        signalLabel,
        smaLongData,
        smaMediumData,
        tooltipData,
        visibleIndicators.emaShort,
        visibleIndicators.smaLong,
        visibleIndicators.smaMedium,
        volumeData,
    ]);

    const sidebarIndicators = [
        {
            label: indicatorLabels.emaShort,
            value: getIndicatorValue(
                opportunity.indicator_values,
                [`ema_${indicatorPeriods.emaShort}`, `ema${indicatorPeriods.emaShort}`, 'ema_short', 'emaShort'],
                latestSnapshot?.emaShort,
            ),
            color: maColors.emaShort,
        },
        {
            label: indicatorLabels.smaMedium,
            value: getIndicatorValue(
                opportunity.indicator_values,
                [`sma_${indicatorPeriods.smaMedium}`, `sma${indicatorPeriods.smaMedium}`, 'sma_medium', 'smaMedium'],
                latestSnapshot?.smaMedium,
            ),
            color: maColors.smaMedium,
        },
        {
            label: indicatorLabels.smaLong,
            value: getIndicatorValue(
                opportunity.indicator_values,
                [`sma_${indicatorPeriods.smaLong}`, `sma${indicatorPeriods.smaLong}`, 'sma_long', 'smaLong'],
                latestSnapshot?.smaLong,
            ),
            color: maColors.smaLong,
        },
    ];

    const indicatorToggleStyles: Record<IndicatorKey, string> = React.useMemo(() => ({
        emaShort: maColors.emaShort,
        smaMedium: maColors.smaMedium,
        smaLong: maColors.smaLong,
    }), [maColors.emaShort, maColors.smaMedium, maColors.smaLong]);

    return (
        <div
            className="fixed inset-0 z-[1000] bg-[#010409]/85 px-4 py-6 sm:px-6"
            onClick={(event) => {
                if (event.target === event.currentTarget) {
                    onClose();
                }
            }}
            data-testid="chart-modal-backdrop"
        >
            <div
                className="mx-auto flex h-full max-h-[98vh] w-full max-w-[min(98vw,1680px)] flex-col overflow-hidden rounded-2xl border border-[#30363d] bg-[#0d1117] shadow-[0_20px_60px_rgba(0,0,0,0.55)]"
                role="dialog"
                aria-modal="true"
                aria-labelledby="chart-modal-title"
                data-testid="chart-modal"
            >
                <header className="flex flex-wrap items-center gap-3 border-b border-[#30363d] bg-[#161b22]/90 px-5 py-4">
                    <div className="min-w-0">
                        <h2 id="chart-modal-title" className="text-xl font-bold text-[#e6edf3]">{symbol}</h2>
                        <p className="text-xs text-[#8b949e]">
                            {opportunity.name || opportunity.template_name} • candle ref {formatTimestamp(opportunity.indicator_values_candle_time)}
                        </p>
                    </div>
                    <span className="rounded-md bg-[#388bfd]/20 px-2.5 py-1 text-xs font-semibold uppercase tracking-wide text-[#58a6ff]">
                        {timeframe}
                    </span>
                    <span
                        className={`rounded-md px-2.5 py-1 text-xs font-semibold uppercase tracking-wide ${resolvedSignal.visual.badgeClass}`}
                        data-testid="chart-modal-signal-badge"
                    >
                        {resolvedSignal.visual.badgeText}
                    </span>
                    <div className="ml-auto text-right">
                        <p className="text-xs uppercase tracking-wide text-[#8b949e]">Last price</p>
                        <p className="font-mono text-lg font-semibold text-[#e6edf3]">
                            {formatPrice(displaySnapshot?.candle.close ?? opportunity.last_price)}
                        </p>
                    </div>
                    <button
                        type="button"
                        className="rounded-md px-3 py-2 text-2xl leading-none text-[#8b949e] transition hover:bg-white/10 hover:text-[#e6edf3]"
                        onClick={onClose}
                        aria-label="Close chart modal"
                        data-testid="chart-modal-close"
                    >
                        ×
                    </button>
                </header>

                <div className="flex min-h-0 flex-1 flex-col lg:flex-row">
                    <div className="flex min-h-0 flex-1 flex-col border-b border-[#30363d] lg:border-b-0 lg:border-r">
                        <div className="flex flex-wrap items-center gap-2 border-b border-[#30363d] px-5 py-3">
                                <div className="flex items-center gap-2" role="group" aria-label="Chart timeframe selector">
                                    {timeframeOptions.map((item) => {
                                        const active = item.value === timeframe;
                                    return (
                                        <button
                                            key={item.value}
                                            type="button"
                                            className={`rounded-md border px-3 py-1.5 text-sm font-medium transition ${
                                                active
                                                    ? 'border-[#388bfd] bg-[#388bfd]/20 text-[#e6edf3]'
                                                    : 'border-[#30363d] bg-[#161b22] text-[#8b949e] hover:text-[#e6edf3]'
                                            }`}
                                            onClick={() => setTimeframe(item.value)}
                                            aria-pressed={active}
                                            title={item.source === 'algorithmic' ? 'Algorithmic timeframe' : 'Manual timeframe'}
                                            data-testid={`chart-timeframe-${item.value}`}
                                        >
                                            {item.label}
                                        </button>
                                    );
                                })}
                            </div>
                            <div
                                className="flex flex-wrap items-center gap-2 rounded-xl border border-[#1f6feb]/45 bg-[linear-gradient(135deg,rgba(31,111,235,0.18),rgba(9,105,218,0.06))] px-3 py-2 shadow-[0_10px_24px_rgba(9,105,218,0.18)]"
                                role="group"
                                aria-label="Chart zoom controls"
                            >
                                <span className="text-[11px] font-semibold uppercase tracking-[0.18em] text-[#79c0ff]">
                                    Zoom
                                </span>
                                <button
                                    type="button"
                                    className="inline-flex h-10 items-center gap-2 rounded-lg border border-[#4c8dff] bg-[#0f2747] px-3 text-sm font-semibold text-[#dbeafe] transition hover:border-[#79c0ff] hover:bg-[#16345b] disabled:cursor-not-allowed disabled:opacity-50"
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
                                    className="inline-flex h-10 items-center gap-2 rounded-lg border border-[#4c8dff] bg-[#0f2747] px-3 text-sm font-semibold text-[#dbeafe] transition hover:border-[#79c0ff] hover:bg-[#16345b] disabled:cursor-not-allowed disabled:opacity-50"
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
                                    className="inline-flex h-10 items-center gap-2 rounded-lg border border-[#335c8e] bg-[#111c2a] px-3 text-sm font-medium text-[#c9d1d9] transition hover:border-[#79c0ff] hover:text-[#e6edf3] disabled:cursor-not-allowed disabled:opacity-50"
                                    onClick={resetZoom}
                                    disabled={candlestickData.length === 0}
                                    aria-label="Reset chart zoom"
                                    data-testid="chart-zoom-reset"
                                >
                                    <RotateCcw className="h-4 w-4" />
                                    <span className="hidden sm:inline">Reset</span>
                                </button>
                                <span
                                    className="rounded-lg border border-white/10 bg-black/20 px-2.5 py-1 text-xs font-medium text-[#d0d7de]"
                                    aria-live="polite"
                                    data-testid="chart-visible-bars"
                                >
                                    {visibleBarCount ?? 0} candles
                                </span>
                                <span className="text-[11px] text-[#9fbad7]">
                                    Mouse wheel: zoom
                                </span>
                            </div>
                            <div className="flex flex-wrap items-center gap-2 rounded-xl border border-[#1f6feb]/45 bg-[linear-gradient(135deg,rgba(31,111,235,0.18),rgba(9,105,218,0.06))] px-3 py-2">
                                <span className="text-[11px] font-semibold uppercase tracking-[0.18em] text-[#79c0ff]">
                                    Layout
                                </span>
                                <button
                                    type="button"
                                    className={`inline-flex h-10 items-center gap-2 rounded-lg border px-3 text-sm font-semibold transition ${
                                        chartMode === 'compact'
                                            ? 'border-[#4c8dff] bg-[#0f2747] text-[#dbeafe]'
                                            : 'border-[#30363d] bg-[#0f2747]/55 text-[#8b949e]'
                                    }`}
                                    onClick={() => setChartMode('compact')}
                                >
                                    Compacto
                                </button>
                                <button
                                    type="button"
                                    className={`inline-flex h-10 items-center gap-2 rounded-lg border px-3 text-sm font-semibold transition ${
                                        chartMode === 'algorithmic'
                                            ? 'border-[#4c8dff] bg-[#0f2747] text-[#dbeafe]'
                                            : 'border-[#30363d] bg-[#0f2747]/55 text-[#8b949e]'
                                    }`}
                                    onClick={() => setChartMode('algorithmic')}
                                >
                                    Algorítmica
                                </button>
                            </div>
                            <div className="ml-auto flex flex-wrap items-center gap-2" role="group" aria-label="Chart indicators">
                                {[
                                    { key: 'emaShort', label: indicatorLabels.emaShort },
                                    { key: 'smaMedium', label: indicatorLabels.smaMedium },
                                    { key: 'smaLong', label: indicatorLabels.smaLong },
                                ].map((indicator) => {
                                    const active = visibleIndicators[indicator.key as IndicatorKey];
                                    return (
                                        <button
                                            key={indicator.key}
                                            type="button"
                                            style={active ? {
                                                borderColor: indicatorToggleStyles[indicator.key as IndicatorKey],
                                                color: indicatorToggleStyles[indicator.key as IndicatorKey],
                                            } : undefined}
                                            className={`rounded-md border px-3 py-1.5 text-sm transition ${
                                                active
                                                    ? 'bg-white/5'
                                                    : 'border-[#30363d] bg-[#161b22] text-[#8b949e]'
                                            }`}
                                            onClick={() => toggleIndicator(indicator.key as IndicatorKey)}
                                            aria-pressed={active}
                                            data-testid={`indicator-toggle-${indicator.key}`}
                                        >
                                            {indicator.label}
                                        </button>
                                    );
                                })}
                            </div>
                        </div>

                        <div className={`relative flex min-h-0 flex-1 flex-col gap-3 p-4 ${isAlgorithmicChartMode ? 'pb-5' : ''}`}>
                            {error ? (
                                <div className="rounded-xl border border-[#f85149]/40 bg-[#f85149]/10 px-4 py-3 text-sm text-[#ffb1ac]">
                                    {error}
                                </div>
                            ) : null}

                            <div className={`grid gap-3 ${isAlgorithmicChartMode ? 'grid-cols-1' : 'xl:grid-cols-[minmax(0,1fr)_280px]'}`}>
                                <div className="min-w-0 space-y-3">
                                    <div
                                        className={`relative rounded-2xl border border-[#30363d] bg-[#0b1118] p-2 ${isAlgorithmicChartMode ? 'min-h-0 flex-1' : ''}`}
                                        onWheel={handleChartWheel}
                                        data-testid="chart-modal-main-chart-shell"
                                    >
                                        <div
                                            ref={mainChartRef}
                                            className="w-full h-full"
                                            style={
                                                isAlgorithmicChartMode
                                                    ? { minHeight: '520px', height: 'min(82vh, calc(100vh - 250px))' }
                                                    : undefined
                                            }
                                            data-testid="chart-modal-main-chart"
                                        />
                                        <div className="pointer-events-none absolute left-4 top-4 rounded-full border border-[#79c0ff]/25 bg-[#0d1117]/86 px-3 py-1 text-[11px] font-medium text-[#c9e6ff]">
                                            Scroll to zoom
                                        </div>
                                        {loading ? (
                                            <div className="absolute right-4 top-4 rounded-md bg-black/55 px-3 py-1.5 text-xs text-white">
                                                Loading timeframe...
                                            </div>
                                        ) : null}
                                    </div>
                                </div>

                                {isAlgorithmicChartMode ? null : (
                                    <div className="rounded-2xl border border-[#30363d] bg-[#11161d] p-4 text-sm text-[#c9d1d9]">
                                        <div className="space-y-5">
                                            <section>
                                                <p className="text-xs font-semibold uppercase tracking-[0.16em] text-[#8b949e]">Signal Context</p>
                                                <div className="mt-2 space-y-2 rounded-xl border border-[#30363d] bg-[#0d1117] p-3">
                                                    <div className="flex justify-between gap-3">
                                                        <span className="text-[#8b949e]">Resolved state</span>
                                                        <span className="font-mono text-[#e6edf3]">{resolvedSignal.visual.badgeText}</span>
                                                    </div>
                                                    <div className="flex justify-between gap-3">
                                                        <span className="text-[#8b949e]">Strategy timeframe</span>
                                                        <span className="font-mono text-[#e6edf3]">{resolvedSignal.strategyTimeframe ?? '-'}</span>
                                                    </div>
                                                    <div className="flex justify-between gap-3">
                                                        <span className="text-[#8b949e]">Displayed timeframe</span>
                                                        <span className="font-mono text-[#e6edf3]">{resolvedSignal.displayTimeframe ?? '-'}</span>
                                                    </div>
                                                    <div className="flex justify-between gap-3">
                                                        <span className="text-[#8b949e]">Reference candle</span>
                                                        <span className="font-mono text-[#e6edf3]">{formatTimestamp(resolvedSignal.referenceCandleTime)}</span>
                                                    </div>
                                                    <div className="flex justify-between gap-3">
                                                        <span className="text-[#8b949e]">Latest displayed candle</span>
                                                        <span className="font-mono text-[#e6edf3]">{formatTimestamp(resolvedSignal.latestCandleTime)}</span>
                                                    </div>
                                                    <div className="rounded-lg border border-[#30363d] bg-[#11161d] px-3 py-2 text-xs text-[#c9d1d9]">
                                                        {resolvedSignal.statusMessage}
                                                        {resolvedSignal.freshnessReason ? ` ${resolvedSignal.freshnessReason}` : ''}
                                                    </div>
                                                </div>
                                            </section>

                                            <section>
                                                <p className="text-xs font-semibold uppercase tracking-[0.16em] text-[#8b949e]">Crosshair</p>
                                                <div className="mt-2 grid grid-cols-2 gap-2 rounded-xl border border-[#30363d] bg-[#0d1117] p-3">
                                                    <div>
                                                        <p className="text-[11px] uppercase tracking-wide text-[#8b949e]">Time</p>
                                                        <p className="font-mono text-sm text-[#e6edf3]">{formatTimestamp(displaySnapshot?.candle.timestamp_utc)}</p>
                                                    </div>
                                                    <div>
                                                        <p className="text-[11px] uppercase tracking-wide text-[#8b949e]">Volume</p>
                                                        <p className="font-mono text-sm text-[#e6edf3]">
                                                            {displaySnapshot?.candle.volume?.toLocaleString('en-US') ?? '-'}
                                                        </p>
                                                    </div>
                                                    <div>
                                                        <p className="text-[11px] uppercase tracking-wide text-[#8b949e]">Open</p>
                                                        <p className="font-mono text-sm text-[#e6edf3]">{formatPrice(displaySnapshot?.candle.open)}</p>
                                                    </div>
                                                    <div>
                                                        <p className="text-[11px] uppercase tracking-wide text-[#8b949e]">High</p>
                                                        <p className="font-mono text-sm text-[#e6edf3]">{formatPrice(displaySnapshot?.candle.high)}</p>
                                                    </div>
                                                    <div>
                                                        <p className="text-[11px] uppercase tracking-wide text-[#8b949e]">Low</p>
                                                        <p className="font-mono text-sm text-[#e6edf3]">{formatPrice(displaySnapshot?.candle.low)}</p>
                                                    </div>
                                                    <div>
                                                        <p className="text-[11px] uppercase tracking-wide text-[#8b949e]">Close</p>
                                                        <p className="font-mono text-sm text-[#e6edf3]">{formatPrice(displaySnapshot?.candle.close)}</p>
                                                    </div>
                                                </div>
                                            </section>

                                            <section>
                                                <p className="text-xs font-semibold uppercase tracking-[0.16em] text-[#8b949e]">Distance</p>
                                                <div className="mt-2 rounded-xl border border-[#30363d] bg-[#0d1117] p-3">
                                                    <p className="text-[11px] uppercase tracking-wide text-[#8b949e]">To {resolvedSignal.visual.markerLabel.toLowerCase()}</p>
                                                    <p className={`font-mono text-lg font-semibold ${
                                                        (opportunity.distance_to_next_status ?? 999) < 0.5 ? 'text-[#3fb950]' : 'text-[#e6edf3]'
                                                    }`}>
                                                        {formatPercent(opportunity.distance_to_next_status)}
                                                    </p>
                                                </div>
                                            </section>

                                            <section>
                                                <p className="text-xs font-semibold uppercase tracking-[0.16em] text-[#8b949e]">Risk / Stop</p>
                                                <div className="mt-2 space-y-2 rounded-xl border border-[#30363d] bg-[#0d1117] p-3">
                                                    <div className="flex justify-between gap-3">
                                                        <span className="text-[#8b949e]">Entry</span>
                                                        <span className="font-mono text-[#e6edf3]">{formatPrice(opportunity.entry_price)}</span>
                                                    </div>
                                                    <div className="flex justify-between gap-3">
                                                        <span className="text-[#8b949e]">Stop</span>
                                                        <span className="font-mono text-[#e6edf3]">{formatPrice(opportunity.stop_price)}</span>
                                                    </div>
                                                    <div className="flex justify-between gap-3">
                                                        <span className="text-[#8b949e]">Risk</span>
                                                        <span className="font-mono text-[#f85149]">{formatPercent(opportunity.distance_to_stop_pct)}</span>
                                                    </div>
                                                </div>
                                            </section>

                                            <section>
                                                <div className="flex items-center justify-between gap-3">
                                                    <p className="text-xs font-semibold uppercase tracking-[0.16em] text-[#8b949e]">Signal History</p>
                                                    <span className="text-[11px] text-[#8b949e]">
                                                        {canRenderSignalHistoryMarkers
                                                            ? 'Markers aligned with chart timeframe.'
                                                            : 'Markers hidden: chart timeframe differs from strategy timeframe.'}
                                                    </span>
                                                </div>
                                                <div className="mt-2 rounded-xl border border-[#30363d] bg-[#0d1117] p-3">
                                                    {signalHistory.length > 0 ? (
                                                        <div className="space-y-2" data-testid="chart-modal-signal-history">
                                                            {signalHistory.map((item, index) => {
                                                                const marker = getSignalHistoryMarker(item);
                                                                return (
                                                                    <div
                                                                        key={`${item.timestamp}-${item.type}-${index}`}
                                                                        className="flex items-start justify-between gap-3 rounded-lg border border-[#30363d] bg-[#11161d] px-3 py-2"
                                                                        data-testid={`chart-modal-signal-history-item-${index}`}
                                                                    >
                                                                        <div className="space-y-1">
                                                                            <div className="flex items-center gap-2">
                                                                                <span className="h-2.5 w-2.5 rounded-full" style={{ backgroundColor: marker.color }} />
                                                                                <span className="font-mono text-sm text-[#e6edf3]">{getSignalHistoryLabel(item)}</span>
                                                                                <span className="text-xs text-[#8b949e]">{formatSignalReason(item.reason)}</span>
                                                                            </div>
                                                                            <p className="text-xs text-[#8b949e]">{formatTimestamp(item.timestamp)}</p>
                                                                        </div>
                                                                        <span className="font-mono text-sm text-[#e6edf3]">{formatPrice(item.price)}</span>
                                                                    </div>
                                                                );
                                                            })}
                                                        </div>
                                                    ) : (
                                                        <p className="text-[#8b949e]">No confirmed entry/exit history available for this strategy.</p>
                                                    )}
                                                </div>
                                            </section>

                                            <section>
                                                <p className="text-xs font-semibold uppercase tracking-[0.16em] text-[#8b949e]">Parameters</p>
                                                <div className="mt-2 space-y-2 rounded-xl border border-[#30363d] bg-[#0d1117] p-3">
                                                    {opportunity.parameters && Object.keys(opportunity.parameters).length > 0 ? (
                                                        Object.entries(opportunity.parameters).map(([key, value]) => (
                                                            <div key={key} className="flex justify-between gap-3">
                                                                <span className="text-[#8b949e]">{key}</span>
                                                                <span className="font-mono text-[#e6edf3]">{String(value)}</span>
                                                            </div>
                                                        ))
                                                    ) : (
                                                        <p className="text-[#8b949e]">No parameters available.</p>
                                                    )}
                                                </div>
                                            </section>

                                            <section>
                                                <p className="text-xs font-semibold uppercase tracking-[0.16em] text-[#8b949e]">Indicators</p>
                                                <div className="mt-2 space-y-2 rounded-xl border border-[#30363d] bg-[#0d1117] p-3">
                                                    {sidebarIndicators.map((item) => (
                                                        <div key={item.label} className="flex items-center justify-between gap-3">
                                                            <div className="flex items-center gap-2">
                                                                <span className="h-2.5 w-2.5 rounded-full" style={{ backgroundColor: item.color }} />
                                                                <span className="text-[#8b949e]">{item.label}</span>
                                                            </div>
                                                            <span className="font-mono text-[#e6edf3]">{formatIndicator(item.value)}</span>
                                                        </div>
                                                    ))}
                                                </div>
                                            </section>

                                            <section>
                                                <p className="text-xs font-semibold uppercase tracking-[0.16em] text-[#8b949e]">Notes</p>
                                                <div className="mt-2 rounded-xl border border-[#30363d] bg-[#0d1117] p-3">
                                                    <p className="whitespace-pre-wrap text-sm text-[#c9d1d9]">
                                                        {opportunity.notes?.trim() ? opportunity.notes : 'No notes for this strategy.'}
                                                    </p>
                                                </div>
                                            </section>
                                        </div>
                                    </div>
                                )}
                            </div>
                        </div>

                        <footer className="border-t border-[#30363d] px-5 py-3">
                            <div className="flex flex-wrap items-center gap-3 text-xs text-[#8b949e]">
                                <span className="inline-flex items-center gap-2"><span className="h-2 w-2 rounded-full bg-[#388bfd]" /> Entry</span>
                                <span className="inline-flex items-center gap-2"><span className="h-2 w-2 rounded-full bg-[#f85149]" /> Stop</span>
                                <span className="inline-flex items-center gap-2"><span className="h-2 w-2 rounded-full" style={{ backgroundColor: maColors.emaShort }} /> {indicatorLabels.emaShort}</span>
                                <span className="inline-flex items-center gap-2"><span className="h-2 w-2 rounded-full" style={{ backgroundColor: maColors.smaMedium }} /> {indicatorLabels.smaMedium}</span>
                                <span className="inline-flex items-center gap-2"><span className="h-2 w-2 rounded-full" style={{ backgroundColor: maColors.smaLong }} /> {indicatorLabels.smaLong}</span>
                                <span className="inline-flex items-center gap-2"><span className="h-2 w-2 rounded-full bg-[#3fb950]" /> Buy</span>
                                <span className="inline-flex items-center gap-2"><span className="h-2 w-2 rounded-full bg-[#f85149]" /> Sell</span>
                            </div>
                        </footer>
                    </div>
                </div>
            </div>
        </div>
    );
};
