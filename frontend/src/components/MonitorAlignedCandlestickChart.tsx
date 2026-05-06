import React from 'react'
import { CandlestickChart, Minus, Plus, RotateCcw } from 'lucide-react'
import {
    ColorType,
    CrosshairMode,
    type IChartApi,
    type LineData,
    type LogicalRange,
    type Time,
    type UTCTimestamp,
    createChart,
} from 'lightweight-charts'

interface Candle {
    timestamp_utc: string
    open: number
    high: number
    low: number
    close: number
    volume: number
}

interface Marker {
    time: number | string
    position: 'aboveBar' | 'belowBar'
    color: string
    shape: 'arrowUp' | 'arrowDown' | 'circle' | 'square'
    text: string
}

interface Snapshot {
    candle: Candle
    emaShort?: number
    smaMedium?: number
    smaLong?: number
}

interface MonitorAlignedCandlestickChartProps {
    candles: Candle[]
    markers?: Marker[]
    parameters?: Record<string, any>
    strategyName: string
    symbol?: string
    timeframe?: string
}

const LOGICAL_RANGE_PADDING = 8
const MIN_VISIBLE_BARS = 12
const ZOOM_STEP_FACTOR = 0.75

function toUtcTimestamp(value: string | number): UTCTimestamp {
    if (typeof value === 'number') return value as UTCTimestamp
    return Math.floor(new Date(value).getTime() / 1000) as UTCTimestamp
}

function getVisibleBarCount(range: LogicalRange | null) {
    if (!range) return null
    return Math.max(1, Math.round(range.to - range.from))
}

function clampLogicalRange(center: number, span: number, candleCount: number): LogicalRange {
    const padding = Math.min(LOGICAL_RANGE_PADDING, Math.max(2, Math.floor(candleCount / 4)))
    const minFrom = -padding
    const maxTo = Math.max(candleCount - 1 + padding, 0)
    let from = center - span / 2
    let to = center + span / 2

    if (from < minFrom) {
        to += minFrom - from
        from = minFrom
    }
    if (to > maxTo) {
        from -= to - maxTo
        to = maxTo
    }

    return {
        from: Math.max(minFrom, from) as LogicalRange['from'],
        to: Math.min(maxTo, to) as LogicalRange['to'],
    }
}

function getNumericParameter(parameters: Record<string, any> | undefined, names: string[], fallback: number) {
    for (const name of names) {
        const value = Number(parameters?.[name])
        if (Number.isFinite(value) && value > 0) return value
    }
    return fallback
}

function calculateSma(candles: Candle[], period: number): LineData<Time>[] {
    const data: LineData<Time>[] = []
    let rollingSum = 0
    candles.forEach((candle, index) => {
        rollingSum += candle.close
        if (index >= period) rollingSum -= candles[index - period].close
        if (index >= period - 1) {
            data.push({
                time: toUtcTimestamp(candle.timestamp_utc),
                value: rollingSum / period,
            })
        }
    })
    return data
}

function calculateEma(candles: Candle[], period: number): LineData<Time>[] {
    if (candles.length < period) return []
    const multiplier = 2 / (period + 1)
    let ema = candles.slice(0, period).reduce((sum, candle) => sum + candle.close, 0) / period
    const data: LineData<Time>[] = [{
        time: toUtcTimestamp(candles[period - 1].timestamp_utc),
        value: ema,
    }]

    for (let index = period; index < candles.length; index += 1) {
        ema = (candles[index].close - ema) * multiplier + ema
        data.push({
            time: toUtcTimestamp(candles[index].timestamp_utc),
            value: ema,
        })
    }
    return data
}

function formatPrice(value?: number | null) {
    if (value === null || value === undefined || Number.isNaN(value)) return '-'
    return value.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 8 })
}

function formatVolume(value?: number | null) {
    if (value === null || value === undefined || Number.isNaN(value)) return '-'
    return value.toLocaleString('en-US', { maximumFractionDigits: 2 })
}

export function MonitorAlignedCandlestickChart({
    candles,
    markers,
    parameters,
    strategyName,
    symbol,
    timeframe,
}: MonitorAlignedCandlestickChartProps) {
    const chartRef = React.useRef<HTMLDivElement>(null)
    const chartApiRef = React.useRef<IChartApi | null>(null)
    const [visibleBarCount, setVisibleBarCount] = React.useState<number | null>(null)
    const [tooltip, setTooltip] = React.useState<Snapshot | null>(null)

    const sortedCandles = React.useMemo(
        () => [...candles].sort((left, right) => Date.parse(left.timestamp_utc) - Date.parse(right.timestamp_utc)),
        [candles],
    )
    const periods = React.useMemo(() => ({
        emaShort: getNumericParameter(parameters, ['ema_short', 'emaShort', 'sma_short', 'smaShort'], 9),
        smaMedium: getNumericParameter(parameters, ['sma_medium', 'smaMedium', 'ema_medium', 'emaMedium'], 21),
        smaLong: getNumericParameter(parameters, ['sma_long', 'smaLong', 'ema_long', 'emaLong'], 50),
    }), [parameters])
    const candlestickData = React.useMemo(() => sortedCandles.map((candle) => ({
        time: toUtcTimestamp(candle.timestamp_utc),
        open: candle.open,
        high: candle.high,
        low: candle.low,
        close: candle.close,
    })), [sortedCandles])
    const volumeData = React.useMemo(() => sortedCandles.map((candle) => ({
        time: toUtcTimestamp(candle.timestamp_utc),
        value: candle.volume,
        color: candle.close >= candle.open ? 'rgba(14, 203, 129, 0.45)' : 'rgba(246, 70, 93, 0.45)',
    })), [sortedCandles])
    const emaShortData = React.useMemo(() => calculateEma(sortedCandles, periods.emaShort), [periods.emaShort, sortedCandles])
    const smaMediumData = React.useMemo(() => calculateSma(sortedCandles, periods.smaMedium), [periods.smaMedium, sortedCandles])
    const smaLongData = React.useMemo(() => calculateSma(sortedCandles, periods.smaLong), [periods.smaLong, sortedCandles])
    const tooltipData = React.useMemo(() => {
        const emaShortMap = new Map<number, number>()
        const smaMediumMap = new Map<number, number>()
        const smaLongMap = new Map<number, number>()
        emaShortData.forEach((point) => typeof point.time === 'number' && emaShortMap.set(point.time, point.value))
        smaMediumData.forEach((point) => typeof point.time === 'number' && smaMediumMap.set(point.time, point.value))
        smaLongData.forEach((point) => typeof point.time === 'number' && smaLongMap.set(point.time, point.value))
        return new Map<number, Snapshot>(
            sortedCandles.map((candle) => {
                const time = toUtcTimestamp(candle.timestamp_utc)
                return [time, {
                    candle,
                    emaShort: emaShortMap.get(time),
                    smaMedium: smaMediumMap.get(time),
                    smaLong: smaLongMap.get(time),
                }]
            }),
        )
    }, [emaShortData, smaMediumData, smaLongData, sortedCandles])
    const latestSnapshot = React.useMemo(() => {
        const latest = sortedCandles[sortedCandles.length - 1]
        return latest ? tooltipData.get(toUtcTimestamp(latest.timestamp_utc)) ?? null : null
    }, [sortedCandles, tooltipData])
    const displaySnapshot = tooltip ?? latestSnapshot

    const syncVisibleBars = React.useCallback((range: LogicalRange | null) => {
        setVisibleBarCount(getVisibleBarCount(range))
    }, [])

    const applyZoom = React.useCallback((direction: 'in' | 'out') => {
        const chart = chartApiRef.current
        if (!chart || candlestickData.length === 0) return
        const currentRange = chart.timeScale().getVisibleLogicalRange()
        const currentSpan = currentRange
            ? Math.max(1, currentRange.to - currentRange.from)
            : Math.max(candlestickData.length, MIN_VISIBLE_BARS)
        const zoomMultiplier = direction === 'in' ? ZOOM_STEP_FACTOR : 1 / ZOOM_STEP_FACTOR
        const nextSpan = direction === 'in'
            ? Math.max(MIN_VISIBLE_BARS, currentSpan * zoomMultiplier)
            : Math.min(candlestickData.length + LOGICAL_RANGE_PADDING * 2, currentSpan * zoomMultiplier)
        const center = currentRange
            ? (currentRange.from + currentRange.to) / 2
            : Math.max(candlestickData.length - 1, 0) / 2
        const nextRange = clampLogicalRange(center, nextSpan, candlestickData.length)
        chart.timeScale().setVisibleLogicalRange(nextRange)
        syncVisibleBars(nextRange)
    }, [candlestickData.length, syncVisibleBars])

    const resetZoom = React.useCallback(() => {
        const chart = chartApiRef.current
        if (!chart) return
        chart.timeScale().fitContent()
        syncVisibleBars(chart.timeScale().getVisibleLogicalRange())
    }, [syncVisibleBars])

    const handleWheel = (event: React.WheelEvent<HTMLDivElement>) => {
        if (candlestickData.length === 0 || Math.abs(event.deltaY) < 3) return
        event.preventDefault()
        applyZoom(event.deltaY < 0 ? 'in' : 'out')
    }

    React.useEffect(() => {
        if (!chartRef.current || candlestickData.length === 0) return undefined

        const chart = createChart(chartRef.current, {
            autoSize: true,
            layout: {
                background: { type: ColorType.Solid, color: '#0b0e11' },
                textColor: '#929aa5',
            },
            grid: {
                vertLines: { color: 'rgba(43, 49, 57, 0.6)' },
                horzLines: { color: 'rgba(43, 49, 57, 0.6)' },
            },
            crosshair: {
                mode: CrosshairMode.Normal,
                vertLine: { color: 'rgba(252, 213, 53, 0.35)', labelBackgroundColor: '#1e2329' },
                horzLine: { color: 'rgba(252, 213, 53, 0.35)', labelBackgroundColor: '#1e2329' },
            },
            rightPriceScale: {
                borderColor: '#2b3139',
                scaleMargins: { top: 0.08, bottom: 0.28 },
            },
            timeScale: {
                borderColor: '#2b3139',
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
        })
        chartApiRef.current = chart

        const candleSeries = chart.addCandlestickSeries({
            upColor: '#0ecb81',
            downColor: '#f6465d',
            borderUpColor: '#0ecb81',
            borderDownColor: '#f6465d',
            wickUpColor: '#0ecb81',
            wickDownColor: '#f6465d',
            priceLineVisible: false,
        })
        const volumeSeries = chart.addHistogramSeries({
            priceScaleId: '',
            priceFormat: { type: 'volume' },
            priceLineVisible: false,
            lastValueVisible: false,
        })
        volumeSeries.priceScale().applyOptions({ scaleMargins: { top: 0.78, bottom: 0 } })
        const emaShortSeries = chart.addLineSeries({
            color: '#fcd535',
            lineWidth: 2,
            priceLineVisible: false,
            lastValueVisible: false,
        })
        const smaMediumSeries = chart.addLineSeries({
            color: '#2dbdb6',
            lineWidth: 2,
            priceLineVisible: false,
            lastValueVisible: false,
        })
        const smaLongSeries = chart.addLineSeries({
            color: '#3b82f6',
            lineWidth: 2,
            priceLineVisible: false,
            lastValueVisible: false,
        })

        candleSeries.setData(candlestickData)
        candleSeries.setMarkers((markers || []).map((marker) => ({
            ...marker,
            time: toUtcTimestamp(marker.time),
        })) as any)
        volumeSeries.setData(volumeData)
        emaShortSeries.setData(emaShortData)
        smaMediumSeries.setData(smaMediumData)
        smaLongSeries.setData(smaLongData)

        chart.timeScale().fitContent()
        const onVisibleRangeChange = (range: LogicalRange | null) => syncVisibleBars(range)
        chart.timeScale().subscribeVisibleLogicalRangeChange(onVisibleRangeChange)
        onVisibleRangeChange(chart.timeScale().getVisibleLogicalRange())

        const onCrosshairMove = (param: { time?: Time }) => {
            if (typeof param.time !== 'number') {
                setTooltip(null)
                return
            }
            setTooltip(tooltipData.get(param.time) ?? null)
        }
        chart.subscribeCrosshairMove(onCrosshairMove)

        return () => {
            chart.unsubscribeCrosshairMove(onCrosshairMove)
            chart.timeScale().unsubscribeVisibleLogicalRangeChange(onVisibleRangeChange)
            if (chartApiRef.current === chart) chartApiRef.current = null
            chart.remove()
        }
    }, [candlestickData, emaShortData, markers, smaLongData, smaMediumData, syncVisibleBars, tooltipData, volumeData])

    return (
        <section className="rounded-lg border border-[#2b3139] bg-[#0b0e11] text-[#eaecef]" data-testid="monitor-aligned-result-chart">
            <header className="flex flex-wrap items-center justify-between gap-3 border-b border-[#2b3139] px-5 py-4">
                <div className="flex min-w-0 items-center gap-3">
                    <div className="rounded-md border border-[#fcd535]/35 bg-[#fcd535]/10 p-2">
                        <CandlestickChart className="h-5 w-5 text-[#fcd535]" />
                    </div>
                    <div className="min-w-0">
                        <h2 className="truncate text-lg font-semibold text-[#eaecef]">
                            {strategyName} - Price Action
                        </h2>
                        <p className="text-sm text-[#929aa5]">
                            {[symbol, timeframe, `${candlestickData.length} candles`].filter(Boolean).join(' • ')}
                        </p>
                    </div>
                </div>

                <div className="flex flex-wrap items-center gap-2" aria-label="Chart zoom controls">
                    <button
                        type="button"
                        className="inline-flex h-9 items-center gap-1 rounded-md border border-[#2b3139] bg-[#1e2329] px-3 text-sm font-semibold text-[#eaecef] transition hover:border-[#fcd535] disabled:opacity-50"
                        onClick={() => applyZoom('out')}
                        disabled={candlestickData.length === 0}
                        aria-label="Zoom out chart"
                        data-testid="result-chart-zoom-out"
                    >
                        <Minus className="h-4 w-4" />
                        Out
                    </button>
                    <button
                        type="button"
                        className="inline-flex h-9 items-center gap-1 rounded-md border border-[#fcd535]/65 bg-[#fcd535] px-3 text-sm font-semibold text-[#181a20] transition hover:bg-[#f0b90b] disabled:opacity-50"
                        onClick={() => applyZoom('in')}
                        disabled={candlestickData.length === 0}
                        aria-label="Zoom in chart"
                        data-testid="result-chart-zoom-in"
                    >
                        <Plus className="h-4 w-4" />
                        In
                    </button>
                    <button
                        type="button"
                        className="inline-flex h-9 items-center gap-1 rounded-md border border-[#2b3139] bg-[#1e2329] px-3 text-sm font-semibold text-[#eaecef] transition hover:border-[#fcd535] disabled:opacity-50"
                        onClick={resetZoom}
                        disabled={candlestickData.length === 0}
                        aria-label="Reset chart zoom"
                        data-testid="result-chart-zoom-reset"
                    >
                        <RotateCcw className="h-4 w-4" />
                        Reset
                    </button>
                    <span className="rounded-md border border-[#2b3139] bg-[#1e2329] px-2.5 py-1 text-xs font-medium text-[#929aa5]" data-testid="result-chart-visible-bars">
                        {visibleBarCount ?? 0} candles
                    </span>
                </div>
            </header>

            <div className="grid gap-3 p-3 xl:grid-cols-[minmax(0,1fr)_260px]">
                <div
                    className="relative min-h-[420px] rounded-lg border border-[#2b3139] bg-[#0b0e11] p-2"
                    onWheel={handleWheel}
                    data-testid="result-chart-shell"
                >
                    <div ref={chartRef} className="h-[420px] w-full md:h-[520px]" data-testid="result-main-chart" />
                    <div className="pointer-events-none absolute left-4 top-4 rounded-md border border-[#fcd535]/25 bg-[#0b0e11]/90 px-3 py-1 text-[11px] font-medium text-[#fcd535]">
                        Scroll to zoom
                    </div>
                </div>

                <aside className="rounded-lg border border-[#2b3139] bg-[#1e2329] p-4">
                    <p className="mb-3 text-xs font-semibold uppercase text-[#929aa5]">Candle</p>
                    <dl className="grid grid-cols-2 gap-3 text-sm xl:grid-cols-1">
                        <div>
                            <dt className="text-[#707a8a]">Close</dt>
                            <dd className="font-mono font-semibold text-[#eaecef]">{formatPrice(displaySnapshot?.candle.close)}</dd>
                        </div>
                        <div>
                            <dt className="text-[#707a8a]">High / Low</dt>
                            <dd className="font-mono text-[#eaecef]">
                                {formatPrice(displaySnapshot?.candle.high)} / {formatPrice(displaySnapshot?.candle.low)}
                            </dd>
                        </div>
                        <div>
                            <dt className="text-[#707a8a]">Volume</dt>
                            <dd className="font-mono text-[#eaecef]">{formatVolume(displaySnapshot?.candle.volume)}</dd>
                        </div>
                    </dl>

                    <div className="mt-5 space-y-2 text-sm">
                        <p className="text-xs font-semibold uppercase text-[#929aa5]">Overlays</p>
                        <div className="flex items-center justify-between gap-2">
                            <span className="text-[#fcd535]">EMA {periods.emaShort}</span>
                            <span className="font-mono text-[#eaecef]">{formatPrice(displaySnapshot?.emaShort)}</span>
                        </div>
                        <div className="flex items-center justify-between gap-2">
                            <span className="text-[#2dbdb6]">SMA {periods.smaMedium}</span>
                            <span className="font-mono text-[#eaecef]">{formatPrice(displaySnapshot?.smaMedium)}</span>
                        </div>
                        <div className="flex items-center justify-between gap-2">
                            <span className="text-[#3b82f6]">SMA {periods.smaLong}</span>
                            <span className="font-mono text-[#eaecef]">{formatPrice(displaySnapshot?.smaLong)}</span>
                        </div>
                    </div>
                </aside>
            </div>
        </section>
    )
}
