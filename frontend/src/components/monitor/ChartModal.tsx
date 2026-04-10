import React from 'react';
import {
    ColorType,
    CrosshairMode,
    LineStyle,
    type IChartApi,
    type ISeriesApi,
    type LineData,
    type LogicalRange,
    type Time,
    type UTCTimestamp,
    createChart,
} from 'lightweight-charts';

import type { MarketCandle } from './MiniCandlesChart';
import type { Opportunity } from './types';
import { CHART_TIMEFRAMES, fetchMarketCandles, type ChartTimeframe } from './chartData';

interface ChartModalProps {
    symbol: string;
    opportunity: Opportunity;
    initialCandles: MarketCandle[];
    initialTimeframe: ChartTimeframe;
    onClose: () => void;
}

type IndicatorKey = 'sma9' | 'ema21' | 'rsi14';

interface IndicatorState {
    sma9: boolean;
    ema21: boolean;
    rsi14: boolean;
}

interface TooltipSnapshot {
    candle: MarketCandle;
    sma9?: number;
    ema21?: number;
    rsi14?: number;
}

const DEFAULT_INDICATORS: IndicatorState = {
    sma9: true,
    ema21: true,
    rsi14: true,
};

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

function calculateRsi(candles: MarketCandle[], period: number): LineData<Time>[] {
    if (candles.length <= period) {
        return [];
    }

    let gains = 0;
    let losses = 0;

    for (let index = 1; index <= period; index += 1) {
        const delta = candles[index].close - candles[index - 1].close;
        gains += Math.max(delta, 0);
        losses += Math.max(-delta, 0);
    }

    let avgGain = gains / period;
    let avgLoss = losses / period;
    const result: LineData<Time>[] = [];

    const firstRs = avgLoss === 0 ? 100 : avgGain / avgLoss;
    result.push({
        time: toUtcTimestamp(candles[period].timestamp_utc),
        value: 100 - 100 / (1 + firstRs),
    });

    for (let index = period + 1; index < candles.length; index += 1) {
        const delta = candles[index].close - candles[index - 1].close;
        const gain = Math.max(delta, 0);
        const loss = Math.max(-delta, 0);
        avgGain = ((avgGain * (period - 1)) + gain) / period;
        avgLoss = ((avgLoss * (period - 1)) + loss) / period;
        const rs = avgLoss === 0 ? 100 : avgGain / avgLoss;

        result.push({
            time: toUtcTimestamp(candles[index].timestamp_utc),
            value: 100 - 100 / (1 + rs),
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
    const [timeframe, setTimeframe] = React.useState<ChartTimeframe>(initialTimeframe);
    const [candles, setCandles] = React.useState<MarketCandle[]>(initialCandles);
    const [loading, setLoading] = React.useState(false);
    const [error, setError] = React.useState<string | null>(null);
    const [visibleIndicators, setVisibleIndicators] = React.useState<IndicatorState>(DEFAULT_INDICATORS);
    const [tooltip, setTooltip] = React.useState<TooltipSnapshot | null>(null);

    const cacheRef = React.useRef<Map<string, MarketCandle[]>>(new Map([
        [`${symbol}|${initialTimeframe}`, initialCandles],
    ]));
    const mainChartRef = React.useRef<HTMLDivElement>(null);
    const rsiChartRef = React.useRef<HTMLDivElement>(null);

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

    const sma9Data = React.useMemo(() => calculateSma(sortedCandles, 9), [sortedCandles]);
    const ema21Data = React.useMemo(() => calculateEma(sortedCandles, 21), [sortedCandles]);
    const rsi14Data = React.useMemo(() => calculateRsi(sortedCandles, 14), [sortedCandles]);

    const tooltipData = React.useMemo(() => {
        const smaMap = new Map<number, number>();
        const emaMap = new Map<number, number>();
        const rsiMap = new Map<number, number>();

        sma9Data.forEach((point) => {
            if (typeof point.time === 'number') {
                smaMap.set(point.time, point.value);
            }
        });
        ema21Data.forEach((point) => {
            if (typeof point.time === 'number') {
                emaMap.set(point.time, point.value);
            }
        });
        rsi14Data.forEach((point) => {
            if (typeof point.time === 'number') {
                rsiMap.set(point.time, point.value);
            }
        });

        return new Map<number, TooltipSnapshot>(
            sortedCandles.map((candle) => {
                const time = toUtcTimestamp(candle.timestamp_utc);
                return [
                    time,
                    {
                        candle,
                        sma9: smaMap.get(time),
                        ema21: emaMap.get(time),
                        rsi14: rsiMap.get(time),
                    },
                ];
            }),
        );
    }, [ema21Data, rsi14Data, sma9Data, sortedCandles]);

    const latestCandle = sortedCandles[sortedCandles.length - 1] ?? null;
    const latestSnapshot = React.useMemo(
        () => (latestCandle ? tooltipData.get(toUtcTimestamp(latestCandle.timestamp_utc)) ?? null : null),
        [latestCandle, tooltipData],
    );

    const displaySnapshot = tooltip ?? latestSnapshot;
    const signalLabel = opportunity.next_status_label === 'exit' ? 'EXIT' : 'ENTRY';

    const toggleIndicator = (key: IndicatorKey) => {
        setVisibleIndicators((current) => ({ ...current, [key]: !current[key] }));
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
    }, [symbol, timeframe]);

    React.useEffect(() => {
        if (!mainChartRef.current || !rsiChartRef.current || candlestickData.length === 0) {
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
            handleScroll: true,
            handleScale: true,
        });

        const rsiChart = createChart(rsiChartRef.current, {
            autoSize: true,
            layout: {
                background: { type: ColorType.Solid, color: '#0d1117' },
                textColor: '#8b949e',
            },
            grid: {
                vertLines: { color: 'rgba(48, 54, 61, 0.35)' },
                horzLines: { color: 'rgba(48, 54, 61, 0.35)' },
            },
            rightPriceScale: {
                borderColor: 'rgba(48, 54, 61, 0.85)',
                scaleMargins: { top: 0.15, bottom: 0.15 },
            },
            timeScale: {
                borderColor: 'rgba(48, 54, 61, 0.85)',
                timeVisible: true,
                secondsVisible: false,
            },
            crosshair: {
                mode: CrosshairMode.Normal,
                vertLine: { color: 'rgba(210, 153, 34, 0.35)', width: 1, labelBackgroundColor: '#161b22' },
                horzLine: { color: 'rgba(210, 153, 34, 0.35)', width: 1, labelBackgroundColor: '#161b22' },
            },
            handleScroll: true,
            handleScale: true,
        });

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

        const smaSeries = mainChart.addLineSeries({
            color: 'rgba(56, 139, 253, 0.72)',
            lineWidth: 2,
            visible: visibleIndicators.sma9,
            priceLineVisible: false,
            lastValueVisible: false,
        });

        const emaSeries = mainChart.addLineSeries({
            color: '#d29922',
            lineWidth: 2,
            visible: visibleIndicators.ema21,
            priceLineVisible: false,
            lastValueVisible: false,
        });

        const rsiSeries = rsiChart.addLineSeries({
            color: '#a371f7',
            lineWidth: 2,
            visible: visibleIndicators.rsi14,
            priceLineVisible: false,
        });

        const rsiUpper = rsiChart.addLineSeries({
            color: 'rgba(248, 81, 73, 0.4)',
            lineWidth: 1,
            lineStyle: LineStyle.Dashed,
            priceLineVisible: false,
            lastValueVisible: false,
        });
        const rsiLower = rsiChart.addLineSeries({
            color: 'rgba(34, 197, 94, 0.4)',
            lineWidth: 1,
            lineStyle: LineStyle.Dashed,
            priceLineVisible: false,
            lastValueVisible: false,
        });

        candleSeries.setData(candlestickData);
        candleSeries.setMarkers([
            {
                time: candlestickData[candlestickData.length - 1].time,
                position: opportunity.next_status_label === 'exit' ? 'aboveBar' : 'belowBar',
                color: opportunity.next_status_label === 'exit' ? '#f85149' : '#22c55e',
                shape: opportunity.next_status_label === 'exit' ? 'arrowDown' : 'arrowUp',
                text: signalLabel,
            },
        ]);
        volumeSeries.setData(volumeData);
        smaSeries.setData(sma9Data);
        emaSeries.setData(ema21Data);
        rsiSeries.setData(rsi14Data);

        if (rsi14Data.length > 0) {
            const firstRsiTime = rsi14Data[0].time;
            const lastRsiTime = rsi14Data[rsi14Data.length - 1].time;
            rsiUpper.setData([
                { time: firstRsiTime, value: 70 },
                { time: lastRsiTime, value: 70 },
            ]);
            rsiLower.setData([
                { time: firstRsiTime, value: 30 },
                { time: lastRsiTime, value: 30 },
            ]);
        }

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
        rsiChart.timeScale().fitContent();

        let syncing = false;
        const syncRange = (source: IChartApi, target: IChartApi) => {
            const handler = (range: LogicalRange | null) => {
                if (!range || syncing) {
                    return;
                }
                syncing = true;
                target.timeScale().setVisibleLogicalRange(range);
                syncing = false;
            };
            source.timeScale().subscribeVisibleLogicalRangeChange(handler);
            return handler;
        };

        const mainRangeHandler = syncRange(mainChart, rsiChart);
        const rsiRangeHandler = syncRange(rsiChart, mainChart);

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
            rsiChart.applyOptions({ width: rsiChartRef.current?.clientWidth ?? 0 });
        };
        window.addEventListener('resize', onResize);

        return () => {
            window.removeEventListener('resize', onResize);
            mainChart.unsubscribeCrosshairMove(onCrosshairMove);
            mainChart.timeScale().unsubscribeVisibleLogicalRangeChange(mainRangeHandler);
            rsiChart.timeScale().unsubscribeVisibleLogicalRangeChange(rsiRangeHandler);
            mainChart.remove();
            rsiChart.remove();
        };
    }, [
        candlestickData,
        opportunity.entry_price,
        opportunity.next_status_label,
        opportunity.stop_price,
        rsi14Data,
        signalLabel,
        sma9Data,
        tooltipData,
        visibleIndicators.ema21,
        visibleIndicators.rsi14,
        visibleIndicators.sma9,
        volumeData,
    ]);

    const sidebarIndicators = [
        {
            label: 'SMA 9',
            value: latestSnapshot?.sma9 ?? opportunity.indicator_values?.sma_9 ?? opportunity.indicator_values?.sma9,
            color: 'bg-[#388bfd]',
        },
        {
            label: 'EMA 21',
            value: latestSnapshot?.ema21 ?? opportunity.indicator_values?.ema_21 ?? opportunity.indicator_values?.ema21,
            color: 'bg-[#d29922]',
        },
        {
            label: 'RSI 14',
            value: latestSnapshot?.rsi14 ?? opportunity.indicator_values?.rsi_14 ?? opportunity.indicator_values?.rsi14,
            color: 'bg-[#a371f7]',
        },
    ];

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
                className="mx-auto flex h-full max-h-[860px] w-full max-w-[1440px] flex-col overflow-hidden rounded-2xl border border-[#30363d] bg-[#0d1117] shadow-[0_20px_60px_rgba(0,0,0,0.55)]"
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
                        className={`rounded-md px-2.5 py-1 text-xs font-semibold uppercase tracking-wide ${
                            opportunity.next_status_label === 'exit'
                                ? 'bg-[#d29922]/20 text-[#d29922]'
                                : 'bg-[#238636]/20 text-[#3fb950]'
                        }`}
                    >
                        {signalLabel}
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
                                {CHART_TIMEFRAMES.map((item) => {
                                    const active = item === timeframe;
                                    return (
                                        <button
                                            key={item}
                                            type="button"
                                            className={`rounded-md border px-3 py-1.5 text-sm font-medium transition ${
                                                active
                                                    ? 'border-[#388bfd] bg-[#388bfd]/20 text-[#e6edf3]'
                                                    : 'border-[#30363d] bg-[#161b22] text-[#8b949e] hover:text-[#e6edf3]'
                                            }`}
                                            onClick={() => setTimeframe(item)}
                                            aria-pressed={active}
                                            data-testid={`chart-timeframe-${item}`}
                                        >
                                            {item}
                                        </button>
                                    );
                                })}
                            </div>
                            <div className="ml-auto flex flex-wrap items-center gap-2" role="group" aria-label="Chart indicators">
                                {[
                                    { key: 'sma9', label: 'SMA 9', color: 'border-[#388bfd]/60 text-[#58a6ff]' },
                                    { key: 'ema21', label: 'EMA 21', color: 'border-[#d29922]/60 text-[#d29922]' },
                                    { key: 'rsi14', label: 'RSI 14', color: 'border-[#a371f7]/60 text-[#c297ff]' },
                                ].map((indicator) => {
                                    const active = visibleIndicators[indicator.key as IndicatorKey];
                                    return (
                                        <button
                                            key={indicator.key}
                                            type="button"
                                            className={`rounded-md border px-3 py-1.5 text-sm transition ${
                                                active
                                                    ? `${indicator.color} bg-white/5`
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

                        <div className="relative flex min-h-0 flex-1 flex-col gap-3 p-4">
                            {error ? (
                                <div className="rounded-xl border border-[#f85149]/40 bg-[#f85149]/10 px-4 py-3 text-sm text-[#ffb1ac]">
                                    {error}
                                </div>
                            ) : null}

                            <div className="grid gap-3 xl:grid-cols-[minmax(0,1fr)_280px]">
                                <div className="min-w-0 space-y-3">
                                    <div className="relative rounded-2xl border border-[#30363d] bg-[#0b1118] p-2">
                                        <div ref={mainChartRef} className="h-[420px] w-full" data-testid="chart-modal-main-chart" />
                                        {loading ? (
                                            <div className="absolute right-4 top-4 rounded-md bg-black/55 px-3 py-1.5 text-xs text-white">
                                                Loading timeframe...
                                            </div>
                                        ) : null}
                                    </div>
                                    <div className="rounded-2xl border border-[#30363d] bg-[#0b1118] p-2">
                                        <div ref={rsiChartRef} className="h-[140px] w-full" data-testid="chart-modal-rsi-chart" />
                                    </div>
                                </div>

                                <div className="rounded-2xl border border-[#30363d] bg-[#11161d] p-4 text-sm text-[#c9d1d9]">
                                    <div className="space-y-5">
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
                                                <p className="text-[11px] uppercase tracking-wide text-[#8b949e]">To {signalLabel.toLowerCase()}</p>
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
                                                            <span className={`h-2.5 w-2.5 rounded-full ${item.color}`} />
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
                            </div>
                        </div>

                        <footer className="border-t border-[#30363d] px-5 py-3">
                            <div className="flex flex-wrap items-center gap-3 text-xs text-[#8b949e]">
                                <span className="inline-flex items-center gap-2"><span className="h-2 w-2 rounded-full bg-[#388bfd]" /> Entry</span>
                                <span className="inline-flex items-center gap-2"><span className="h-2 w-2 rounded-full bg-[#f85149]" /> Stop</span>
                                <span className="inline-flex items-center gap-2"><span className="h-2 w-2 rounded-full bg-[#58a6ff]" /> SMA 9</span>
                                <span className="inline-flex items-center gap-2"><span className="h-2 w-2 rounded-full bg-[#d29922]" /> EMA 21</span>
                                <span className="inline-flex items-center gap-2"><span className="h-2 w-2 rounded-full bg-[#a371f7]" /> RSI 14</span>
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
