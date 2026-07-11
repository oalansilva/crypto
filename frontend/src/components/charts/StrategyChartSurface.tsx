import React from 'react'
import { CandlestickChart, Minus, Plus, RotateCcw } from 'lucide-react'
import {
    ColorType,
    CrosshairMode,
    LineStyle,
    type IChartApi,
    type IPriceLine,
    type ISeriesApi,
    type LogicalRange,
    type Time,
    type UTCTimestamp,
    createChart,
} from 'lightweight-charts'
import {
    buildIndicatorValueIndex,
    normalizeStrategyTransparency,
    transparencyMatchesTimeframe,
    type StrategyTransparency,
    type StrategyTransparencyIndicator,
} from '../../lib/strategyTransparency'

export interface StrategyChartCandle {
    timestamp_utc: string
    open: number
    high: number
    low: number
    close: number
    volume: number
}

export interface StrategyChartMarker {
    time: number | string
    position: 'aboveBar' | 'belowBar'
    color: string
    shape: 'arrowUp' | 'arrowDown' | 'circle' | 'square'
    text: string
    signalType?: 'entry' | 'exit'
}

export interface StrategyChartPriceLine {
    price: number
    color: string
    title: string
    lineStyle?: LineStyle
}

export interface StrategyChartSummaryItem {
    label: string
    value: React.ReactNode
    tone?: 'default' | 'primary' | 'success' | 'danger' | 'muted'
}

export interface StrategyChartConfigurationItem {
    label: string
    color?: string
}

export interface StrategyChartSnapshot {
    candle: StrategyChartCandle
    indicatorValues: Record<string, number | null>
}

interface StrategyChartSurfaceProps {
    candles: StrategyChartCandle[]
    markers?: StrategyChartMarker[]
    priceLines?: StrategyChartPriceLine[]
    strategyName: string
    symbol?: string
    timeframe?: string
    strategyTransparency?: StrategyTransparency | Record<string, unknown> | null
    title?: React.ReactNode
    subtitle?: React.ReactNode
    headerMeta?: React.ReactNode
    configurationItems?: StrategyChartConfigurationItem[]
    headerActions?: React.ReactNode
    toolbarLeading?: React.ReactNode
    summaryItems?: StrategyChartSummaryItem[]
    sideContent?: React.ReactNode | ((snapshot: StrategyChartSnapshot | null) => React.ReactNode)
    showSideContent?: boolean
    belowContent?: React.ReactNode
    footerContent?: React.ReactNode
    loading?: boolean
    error?: string | null
    markerCount?: number
    currentMarkerLabel?: string
    rootTestId: string
    chartTestId: string
    shellTestId: string
    zoomTestIdPrefix: string
    visibleBarsTestId: string
    summaryTestId?: string
    heightClassName?: string
    gridClassName?: string
    sideClassName?: string
    className?: string
}

const LOGICAL_RANGE_PADDING = 8
const MIN_VISIBLE_BARS = 12
const ZOOM_STEP_FACTOR = 0.75
const DEFAULT_VISIBLE_BARS = 180

type IndicatorPanelRuntime = {
    chart: IChartApi
    series: Map<string, ISeriesApi<'Line'> | ISeriesApi<'Histogram'>>
}

export function toStrategyChartTimestamp(value: string | number): UTCTimestamp {
    if (typeof value === 'number') return value as UTCTimestamp
    return Math.floor(new Date(value).getTime() / 1000) as UTCTimestamp
}

function normalizeMarkers(markers: StrategyChartMarker[] | undefined) {
    return (markers || [])
        .map((marker, index) => ({
            marker: {
                ...marker,
                time: toStrategyChartTimestamp(marker.time),
            },
            index,
        }))
        .filter(({ marker }) => Number.isFinite(marker.time))
        .sort((left, right) => {
            const timeDelta = left.marker.time - right.marker.time
            return timeDelta === 0 ? left.index - right.index : timeDelta
        })
        .map(({ marker }) => marker)
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

function getDefaultLogicalRange(candleCount: number): LogicalRange | null {
    if (candleCount <= DEFAULT_VISIBLE_BARS) return null
    return {
        from: candleCount - DEFAULT_VISIBLE_BARS,
        to: candleCount,
    } as LogicalRange
}

function formatPrice(value?: number | null) {
    if (value === null || value === undefined || Number.isNaN(value)) return '-'
    return value.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 8 })
}

function formatVolume(value?: number | null) {
    if (value === null || value === undefined || Number.isNaN(value)) return '-'
    return value.toLocaleString('en-US', { maximumFractionDigits: 2 })
}

function summaryToneClass(tone?: StrategyChartSummaryItem['tone']) {
    if (tone === 'primary') return 'text-[#fcd535]'
    if (tone === 'success') return 'text-[#0ecb81]'
    if (tone === 'danger') return 'text-[#f6465d]'
    if (tone === 'muted') return 'text-[#929aa5]'
    return 'text-[#eaecef]'
}

export function StrategyChartSurface({
    candles,
    markers,
    priceLines,
    strategyName,
    symbol,
    timeframe,
    strategyTransparency,
    title,
    subtitle,
    headerMeta,
    configurationItems,
    headerActions,
    toolbarLeading,
    summaryItems,
    sideContent,
    showSideContent = true,
    belowContent,
    footerContent,
    loading,
    error,
    markerCount,
    currentMarkerLabel,
    rootTestId,
    chartTestId,
    shellTestId,
    zoomTestIdPrefix,
    visibleBarsTestId,
    summaryTestId,
    heightClassName = 'h-[420px] w-full md:h-[520px]',
    gridClassName = 'grid gap-3 p-3 xl:grid-cols-[minmax(0,1fr)_260px]',
    sideClassName = 'rounded-lg border border-[#2b3139] bg-[#1e2329] p-4',
    className = '',
}: StrategyChartSurfaceProps) {
    const shellRef = React.useRef<HTMLDivElement>(null)
    const chartRef = React.useRef<HTMLDivElement>(null)
    const chartApiRef = React.useRef<IChartApi | null>(null)
    const candleSeriesRef = React.useRef<ISeriesApi<'Candlestick'> | null>(null)
    const volumeSeriesRef = React.useRef<ISeriesApi<'Histogram'> | null>(null)
    const overlaySeriesRefs = React.useRef<Array<ISeriesApi<'Line'> | ISeriesApi<'Histogram'>>>([])
    const panelContainersRef = React.useRef<Map<string, HTMLDivElement>>(new Map())
    const panelRuntimesRef = React.useRef<Map<string, IndicatorPanelRuntime>>(new Map())
    const indicatorValueIndexRef = React.useRef<Map<string, Map<number, number>>>(new Map())
    const syncingCrosshairRef = React.useRef(false)
    const priceLineRefs = React.useRef<IPriceLine[]>([])
    const tooltipDataRef = React.useRef<Map<number, StrategyChartSnapshot>>(new Map())
    const [visibleBarCount, setVisibleBarCount] = React.useState<number | null>(null)
    const [tooltip, setTooltip] = React.useState<StrategyChartSnapshot | null>(null)

    const transparency = React.useMemo(
        () => normalizeStrategyTransparency(strategyTransparency),
        [strategyTransparency],
    )
    const timeframeMatches = React.useMemo(
        () => transparencyMatchesTimeframe(transparency, timeframe),
        [timeframe, transparency],
    )
    const activeIndicators = React.useMemo(
        () => timeframeMatches
            ? (transparency?.indicators ?? []).filter((indicator) => indicator.availability === 'available' && indicator.series.length > 0)
            : [],
        [timeframeMatches, transparency],
    )
    const lowerPanelGroups = React.useMemo(() => {
        const groups = new Map<string, StrategyTransparencyIndicator[]>()
        activeIndicators.forEach((indicator) => {
            if (indicator.panel === 'price' || indicator.panel === 'volume') return
            const group = groups.get(indicator.panel) ?? []
            group.push(indicator)
            groups.set(indicator.panel, group)
        })
        return [...groups.entries()]
    }, [activeIndicators])

    const indicatorValueIndex = React.useMemo(
        () => buildIndicatorValueIndex(transparency?.indicators ?? []),
        [transparency],
    )
    React.useEffect(() => {
        indicatorValueIndexRef.current = indicatorValueIndex
    }, [indicatorValueIndex])

    const sortedCandles = React.useMemo(
        () => [...candles].sort((left, right) => Date.parse(left.timestamp_utc) - Date.parse(right.timestamp_utc)),
        [candles],
    )
    const candlestickData = React.useMemo(() => sortedCandles.map((candle) => ({
        time: toStrategyChartTimestamp(candle.timestamp_utc),
        open: candle.open,
        high: candle.high,
        low: candle.low,
        close: candle.close,
    })), [sortedCandles])
    const volumeData = React.useMemo(() => sortedCandles.map((candle) => ({
        time: toStrategyChartTimestamp(candle.timestamp_utc),
        value: candle.volume,
        color: candle.close >= candle.open ? 'rgba(14, 203, 129, 0.45)' : 'rgba(246, 70, 93, 0.45)',
    })), [sortedCandles])
    const chartMarkers = React.useMemo(() => normalizeMarkers(markers), [markers])
    const tooltipData = React.useMemo(() => (
        new Map<number, StrategyChartSnapshot>(
            sortedCandles.map((candle) => {
                const time = toStrategyChartTimestamp(candle.timestamp_utc)
                const indicatorValues = Object.fromEntries(
                    (transparency?.indicators ?? []).map((indicator) => [
                        indicator.key,
                        timeframeMatches ? indicatorValueIndex.get(indicator.key)?.get(time) ?? null : null,
                    ]),
                )
                return [time, { candle, indicatorValues }]
            }),
        )
    ), [indicatorValueIndex, sortedCandles, timeframeMatches, transparency])
    const latestSnapshot = React.useMemo(() => {
        const latest = sortedCandles[sortedCandles.length - 1]
        return latest ? tooltipData.get(toStrategyChartTimestamp(latest.timestamp_utc)) ?? null : null
    }, [sortedCandles, tooltipData])
    const displaySnapshot = tooltip ?? latestSnapshot

    const syncVisibleBars = React.useCallback((range: LogicalRange | null) => {
        setVisibleBarCount(getVisibleBarCount(range))
    }, [])

    React.useEffect(() => {
        tooltipDataRef.current = tooltipData
    }, [tooltipData])

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
        const defaultRange = getDefaultLogicalRange(candlestickData.length)
        if (defaultRange) {
            chart.timeScale().setVisibleLogicalRange(defaultRange)
            syncVisibleBars(defaultRange)
            return
        }
        chart.timeScale().fitContent()
        syncVisibleBars(chart.timeScale().getVisibleLogicalRange())
    }, [candlestickData.length, syncVisibleBars])

    const handleWheelZoom = React.useCallback((deltaY: number) => {
        if (candlestickData.length === 0 || Math.abs(deltaY) < 3) return
        applyZoom(deltaY < 0 ? 'in' : 'out')
    }, [applyZoom, candlestickData.length])

    const handleWheel = (event: React.WheelEvent<HTMLDivElement>) => {
        if (candlestickData.length === 0 || Math.abs(event.deltaY) < 3) return
        event.preventDefault()
        event.stopPropagation()
        handleWheelZoom(event.deltaY)
    }

    React.useEffect(() => {
        const shell = shellRef.current
        if (!shell) return undefined

        const onWheel = (event: WheelEvent) => {
            if (candlestickData.length === 0 || Math.abs(event.deltaY) < 3) return
            event.preventDefault()
            event.stopPropagation()
            handleWheelZoom(event.deltaY)
        }

        shell.addEventListener('wheel', onWheel, { passive: false, capture: true })
        return () => shell.removeEventListener('wheel', onWheel, { capture: true } as AddEventListenerOptions)
    }, [candlestickData.length, handleWheelZoom])

    React.useEffect(() => {
        if (!chartRef.current) return undefined

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
        candleSeriesRef.current = candleSeries
        volumeSeriesRef.current = volumeSeries

        const onVisibleRangeChange = (range: LogicalRange | null) => {
            syncVisibleBars(range)
            if (!range) return
            panelRuntimesRef.current.forEach(({ chart: panelChart }) => {
                panelChart.timeScale().setVisibleLogicalRange(range)
            })
        }
        chart.timeScale().subscribeVisibleLogicalRangeChange(onVisibleRangeChange)

        const onCrosshairMove = (param: { time?: Time }) => {
            if (syncingCrosshairRef.current) return
            if (typeof param.time !== 'number') {
                setTooltip(null)
                panelRuntimesRef.current.forEach(({ chart: panelChart }) => panelChart.clearCrosshairPosition())
                return
            }
            setTooltip(tooltipDataRef.current.get(param.time) ?? null)
            syncingCrosshairRef.current = true
            panelRuntimesRef.current.forEach(({ chart: panelChart, series }) => {
                const firstEntry = [...series.entries()].find(([key]) => (
                    indicatorValueIndexRef.current.get(key)?.has(param.time as number)
                ))
                if (!firstEntry) {
                    panelChart.clearCrosshairPosition()
                    return
                }
                const value = indicatorValueIndexRef.current.get(firstEntry[0])?.get(param.time as number)
                if (value !== undefined) panelChart.setCrosshairPosition(value, param.time as UTCTimestamp, firstEntry[1])
            })
            syncingCrosshairRef.current = false
        }
        chart.subscribeCrosshairMove(onCrosshairMove)

        return () => {
            chart.unsubscribeCrosshairMove(onCrosshairMove)
            chart.timeScale().unsubscribeVisibleLogicalRangeChange(onVisibleRangeChange)
            priceLineRefs.current.forEach((line) => candleSeries.removePriceLine(line))
            priceLineRefs.current = []
            candleSeriesRef.current = null
            volumeSeriesRef.current = null
            if (chartApiRef.current === chart) chartApiRef.current = null
            chart.remove()
        }
    }, [syncVisibleBars])

    React.useEffect(() => {
        const chart = chartApiRef.current
        const candleSeries = candleSeriesRef.current
        const volumeSeries = volumeSeriesRef.current
        if (!chart || !candleSeries || !volumeSeries) return

        candleSeries.setData(candlestickData)
        volumeSeries.setData(volumeData)

        if (candlestickData.length === 0) {
            setTooltip(null)
            syncVisibleBars(null)
            return
        }

        const defaultRange = getDefaultLogicalRange(candlestickData.length)
        if (defaultRange) {
            chart.timeScale().setVisibleLogicalRange(defaultRange)
            syncVisibleBars(defaultRange)
            return
        }

        chart.timeScale().fitContent()
        syncVisibleBars(chart.timeScale().getVisibleLogicalRange())
    }, [candlestickData, syncVisibleBars, volumeData])

    React.useEffect(() => {
        const candleSeries = candleSeriesRef.current
        if (!candleSeries) return

        candleSeries.setMarkers(chartMarkers as any)
    }, [chartMarkers])

    React.useEffect(() => {
        const candleSeries = candleSeriesRef.current
        if (!candleSeries) return

        priceLineRefs.current.forEach((line) => candleSeries.removePriceLine(line))
        priceLineRefs.current = (priceLines || []).map((line) => (
            candleSeries.createPriceLine({
                price: line.price,
                color: line.color,
                lineWidth: 2,
                lineStyle: line.lineStyle ?? LineStyle.Dashed,
                axisLabelVisible: true,
                title: line.title,
            })
        ))
    }, [priceLines])

    React.useEffect(() => {
        const chart = chartApiRef.current
        if (!chart) return undefined

        overlaySeriesRefs.current.forEach((series) => {
            try { chart.removeSeries(series) } catch { /* chart already refreshed */ }
        })
        overlaySeriesRefs.current = []

        activeIndicators
            .filter((indicator) => indicator.panel === 'price' || indicator.panel === 'volume')
            .forEach((indicator) => {
                const isHistogram = indicator.type.includes('histogram')
                const series = isHistogram
                    ? chart.addHistogramSeries({
                        color: indicator.color,
                        priceScaleId: indicator.panel === 'volume' ? '' : 'right',
                        priceLineVisible: false,
                        lastValueVisible: true,
                    })
                    : chart.addLineSeries({
                        color: indicator.color,
                        lineWidth: 2,
                        priceScaleId: indicator.panel === 'volume' ? '' : 'right',
                        priceLineVisible: false,
                        lastValueVisible: true,
                        title: indicator.label,
                    })
                series.setData(indicator.series.map((point) => ({
                    time: toStrategyChartTimestamp(point.timestamp_utc),
                    value: point.value,
                    ...(isHistogram ? { color: indicator.color } : {}),
                })) as never)
                indicator.references.forEach((reference) => series.createPriceLine({
                    price: reference.value,
                    color: reference.color || indicator.color,
                    lineWidth: 1,
                    lineStyle: LineStyle.Dashed,
                    axisLabelVisible: true,
                    title: reference.label,
                }))
                overlaySeriesRefs.current.push(series)
            })

        return () => {
            overlaySeriesRefs.current.forEach((series) => {
                try { chart.removeSeries(series) } catch { /* chart already removed */ }
            })
            overlaySeriesRefs.current = []
        }
    }, [activeIndicators])

    React.useEffect(() => {
        panelRuntimesRef.current.forEach(({ chart }) => chart.remove())
        panelRuntimesRef.current.clear()

        lowerPanelGroups.forEach(([panel, indicators]) => {
            const container = panelContainersRef.current.get(panel)
            if (!container) return
            const panelChart = createChart(container, {
                autoSize: true,
                layout: { background: { type: ColorType.Solid, color: '#0b0e11' }, textColor: '#929aa5' },
                grid: {
                    vertLines: { color: 'rgba(43, 49, 57, 0.45)' },
                    horzLines: { color: 'rgba(43, 49, 57, 0.45)' },
                },
                crosshair: {
                    mode: CrosshairMode.Normal,
                    vertLine: { color: 'rgba(252, 213, 53, 0.35)', labelBackgroundColor: '#1e2329' },
                    horzLine: { color: 'rgba(252, 213, 53, 0.35)', labelBackgroundColor: '#1e2329' },
                },
                rightPriceScale: { borderColor: '#2b3139' },
                timeScale: {
                    borderColor: '#2b3139',
                    timeVisible: true,
                    secondsVisible: false,
                    rightOffset: 8,
                },
                handleScroll: false,
                handleScale: false,
            })
            const seriesByKey = new Map<string, ISeriesApi<'Line'> | ISeriesApi<'Histogram'>>()
            indicators.forEach((indicator) => {
                const isHistogram = indicator.type.includes('histogram')
                const series = isHistogram
                    ? panelChart.addHistogramSeries({
                        color: indicator.color,
                        priceLineVisible: false,
                        lastValueVisible: true,
                    })
                    : panelChart.addLineSeries({
                        color: indicator.color,
                        lineWidth: 2,
                        priceLineVisible: false,
                        lastValueVisible: true,
                        title: indicator.label,
                    })
                series.setData(indicator.series.map((point) => ({
                    time: toStrategyChartTimestamp(point.timestamp_utc),
                    value: point.value,
                    ...(isHistogram ? { color: indicator.color } : {}),
                })) as never)
                indicator.references.forEach((reference) => series.createPriceLine({
                    price: reference.value,
                    color: reference.color || indicator.color,
                    lineWidth: 1,
                    lineStyle: LineStyle.Dashed,
                    axisLabelVisible: true,
                    title: reference.label,
                }))
                seriesByKey.set(indicator.key, series)
            })
            const currentRange = chartApiRef.current?.timeScale().getVisibleLogicalRange()
            if (currentRange) panelChart.timeScale().setVisibleLogicalRange(currentRange)
            else panelChart.timeScale().fitContent()

            const onPanelCrosshairMove = (param: { time?: Time }) => {
                if (syncingCrosshairRef.current || typeof param.time !== 'number') return
                const snapshot = tooltipDataRef.current.get(param.time)
                setTooltip(snapshot ?? null)
                if (!snapshot || !candleSeriesRef.current || !chartApiRef.current) return
                syncingCrosshairRef.current = true
                chartApiRef.current.setCrosshairPosition(snapshot.candle.close, param.time, candleSeriesRef.current)
                syncingCrosshairRef.current = false
            }
            panelChart.subscribeCrosshairMove(onPanelCrosshairMove)
            panelRuntimesRef.current.set(panel, { chart: panelChart, series: seriesByKey })
        })

        return () => {
            panelRuntimesRef.current.forEach(({ chart }) => chart.remove())
            panelRuntimesRef.current.clear()
        }
    }, [lowerPanelGroups])

    const subtitleContent = subtitle ?? [symbol, timeframe, `${candlestickData.length} velas`].filter(Boolean).join(' • ')

    return (
        <section
            className={`overflow-hidden rounded-lg border border-[#2b3139] bg-[#0b0e11] text-[#eaecef] ${className}`}
            data-testid={rootTestId}
            data-marker-count={markerCount ?? markers?.length ?? 0}
            data-marker-labels={chartMarkers.map((marker) => marker.text).join('|')}
            data-last-candle-timestamp={sortedCandles.at(-1)?.timestamp_utc ?? ''}
        >
            <header className="border-b border-[#2b3139] bg-[#0b0e11] px-4 py-4 sm:px-5">
                <div className="flex flex-wrap items-start justify-between gap-3">
                    <div className="flex min-w-0 items-start gap-3">
                        <div className="grid h-10 w-10 shrink-0 place-items-center rounded-md border border-[#fcd535]/35 bg-[#fcd535]/10">
                            <CandlestickChart className="h-5 w-5 text-[#fcd535]" />
                        </div>
                        <div className="min-w-0">
                            <div className="flex flex-wrap items-center gap-2">
                                <h2 className="truncate text-lg font-semibold tracking-normal text-[#eaecef]">
                                    {title ?? `${strategyName} - Ação de preço`}
                                </h2>
                                {headerMeta}
                            </div>
                            <p className="mt-1 text-sm text-[#929aa5]">{subtitleContent}</p>
                            <div className="mt-2 flex flex-wrap gap-2" data-testid={`${rootTestId}-indicator-config`} aria-label="Configuração dos indicadores">
                                {configurationItems && configurationItems.length > 0 ? configurationItems.map((item, index) => (
                                    <span key={`${item.label}-${index}`} className="inline-flex items-center gap-1.5 rounded-md border border-[#2b3139] bg-[#1e2329] px-2.5 py-1 text-xs font-semibold text-[#eaecef]">
                                        {item.color ? <span className="h-2.5 w-2.5 rounded-full" style={{ backgroundColor: item.color }} aria-hidden="true" /> : null}
                                        {item.label}
                                    </span>
                                )) : (
                                    <span className="rounded-md border border-[#fcd535]/40 bg-[#fcd535]/10 px-2.5 py-1 text-xs text-[#eaecef]">
                                        Configuração dos indicadores indisponível
                                    </span>
                                )}
                            </div>
                        </div>
                    </div>
                    {headerActions}
                </div>

                {summaryItems && summaryItems.length > 0 ? (
                    <div className="mt-4 grid gap-2 md:grid-cols-4" data-testid={summaryTestId ?? `${rootTestId}-summary`}>
                        {summaryItems.map((item) => (
                            <div key={item.label} className="rounded-lg border border-[#2b3139] bg-[#1e2329]/78 p-3">
                                <p className="text-[10px] font-semibold uppercase tracking-normal text-[#707a8a]">{item.label}</p>
                                <div className={`mt-1 font-mono text-sm font-semibold ${summaryToneClass(item.tone)}`}>
                                    {item.value}
                                </div>
                            </div>
                        ))}
                    </div>
                ) : null}
            </header>

            <div className="flex flex-wrap items-center gap-2 border-b border-[#2b3139] bg-[#1e2329] px-4 py-3 sm:px-5">
                {toolbarLeading}
                <div className="ml-auto flex flex-wrap items-center gap-2" role="group" aria-label="Controles de zoom do grafico">
                    <button
                        type="button"
                        className="inline-flex h-11 items-center gap-1 rounded-md border border-[#2b3139] bg-[#0b0e11] px-3 text-sm font-semibold text-[#eaecef] transition hover:border-[#fcd535] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#3b82f6] disabled:cursor-not-allowed disabled:opacity-50"
                        onClick={() => applyZoom('out')}
                        disabled={candlestickData.length === 0}
                        aria-label="Reduzir zoom do grafico"
                        data-testid={`${zoomTestIdPrefix}-zoom-out`}
                    >
                        <Minus className="h-4 w-4" />
                        <span className="hidden sm:inline">Menos</span>
                    </button>
                    <button
                        type="button"
                        className="inline-flex h-11 items-center gap-1 rounded-md border border-[#fcd535]/65 bg-[#fcd535] px-3 text-sm font-semibold text-[#181a20] transition hover:bg-[#f0b90b] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#3b82f6] disabled:cursor-not-allowed disabled:opacity-50"
                        onClick={() => applyZoom('in')}
                        disabled={candlestickData.length === 0}
                        aria-label="Aumentar zoom do grafico"
                        data-testid={`${zoomTestIdPrefix}-zoom-in`}
                    >
                        <Plus className="h-4 w-4" />
                        <span className="hidden sm:inline">Mais</span>
                    </button>
                    <button
                        type="button"
                        className="inline-flex h-11 items-center gap-1 rounded-md border border-[#2b3139] bg-[#0b0e11] px-3 text-sm font-semibold text-[#eaecef] transition hover:border-[#fcd535] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#3b82f6] disabled:cursor-not-allowed disabled:opacity-50"
                        onClick={resetZoom}
                        disabled={candlestickData.length === 0}
                        aria-label="Redefinir zoom do grafico"
                        data-testid={`${zoomTestIdPrefix}-zoom-reset`}
                    >
                        <RotateCcw className="h-4 w-4" />
                        <span className="hidden sm:inline">Resetar</span>
                    </button>
                    <span
                        className="rounded-md border border-[#2b3139] bg-[#0b0e11] px-2.5 py-1 text-xs font-medium text-[#929aa5]"
                        aria-live="polite"
                        data-testid={visibleBarsTestId}
                    >
                        {visibleBarCount ?? 0} velas
                    </span>
                    <span className="text-[11px] text-[#929aa5]">
                        Roda do mouse: zoom
                    </span>
                </div>
            </div>

            {error ? (
                <div className="mx-3 mt-3 rounded-lg border border-[#f6465d]/40 bg-[#f6465d]/10 px-4 py-3 text-sm text-[#ffb1ac]">
                    {error}
                </div>
            ) : null}

            <div className={gridClassName}>
                <div
                    ref={shellRef}
                    className="relative min-h-[420px] rounded-lg border border-[#2b3139] bg-[#0b0e11] p-2"
                    onWheel={handleWheel}
                    data-testid={shellTestId}
                    data-current-marker={currentMarkerLabel}
                >
                    <div ref={chartRef} className={heightClassName} data-testid={chartTestId} />
                    {lowerPanelGroups.map(([panel, indicators]) => (
                        <section
                            key={panel}
                            className="mt-2 overflow-hidden rounded-lg border border-[#2b3139] bg-[#0b0e11]"
                            aria-labelledby={`${rootTestId}-${panel}-title`}
                            data-testid={`${rootTestId}-indicator-panel-${panel}`}
                        >
                            <h3
                                id={`${rootTestId}-${panel}-title`}
                                className="border-b border-[#2b3139] bg-[#1e2329] px-3 py-2 text-xs font-semibold uppercase text-[#eaecef]"
                            >
                                Painel {panel}: {indicators.map((indicator) => indicator.label).join(', ')}
                            </h3>
                            <div
                                ref={(node) => {
                                    if (node) panelContainersRef.current.set(panel, node)
                                    else panelContainersRef.current.delete(panel)
                                }}
                                className="h-[150px] w-full sm:h-[180px]"
                                aria-hidden="true"
                            />
                        </section>
                    ))}
                    <div className="pointer-events-none absolute left-4 top-4 rounded-md border border-[#fcd535]/25 bg-[#0b0e11]/90 px-3 py-1 text-[11px] font-medium text-[#fcd535]">
                        Role para dar zoom
                    </div>
                    {loading ? (
                        <div className="absolute right-4 top-4 rounded-md bg-black/60 px-3 py-1.5 text-xs text-white">
                            Carregando timeframe...
                        </div>
                    ) : null}

                    {transparency ? (
                        <section
                            className="mt-3 rounded-lg border border-[#2b3139] bg-[#1e2329] p-3 sm:p-4"
                            aria-labelledby={`${rootTestId}-strategy-transparency-title`}
                            data-testid={`${rootTestId}-strategy-transparency`}
                        >
                            <h3 id={`${rootTestId}-strategy-transparency-title`} className="text-sm font-semibold text-[#eaecef]">
                                {transparency.display_name || strategyName}
                            </h3>
                            {transparency.description ? <p className="mt-1 text-sm text-[#929aa5]">{transparency.description}</p> : null}

                            {!timeframeMatches ? (
                                <p className="mt-3 rounded-md border border-[#fcd535]/40 bg-[#fcd535]/10 px-3 py-2 text-sm text-[#eaecef]" role="status">
                                    Indicadores indisponíveis: o manifesto usa {transparency.timeframe.toUpperCase()} e o gráfico exibe {timeframe?.toUpperCase()}.
                                </p>
                            ) : transparency.status !== 'available' ? (
                                <p className="mt-3 rounded-md border border-[#fcd535]/40 bg-[#fcd535]/10 px-3 py-2 text-sm text-[#eaecef]" role="status">
                                    Indicadores indisponíveis{transparency.unavailable_reason ? `: ${transparency.unavailable_reason}` : '.'}
                                </p>
                            ) : null}

                            <ul className="mt-3 grid gap-2 md:grid-cols-2" aria-label="Legenda dos indicadores da estratégia">
                                {transparency.indicators.map((indicator) => {
                                    const value = timeframeMatches ? displaySnapshot?.indicatorValues[indicator.key] : null
                                    const isAvailable = timeframeMatches && indicator.availability === 'available' && indicator.series.length > 0
                                    return (
                                        <li
                                            key={indicator.key}
                                            className="rounded-md border border-[#2b3139] bg-[#0b0e11] p-3 text-sm"
                                            data-testid={`${rootTestId}-indicator-${indicator.key}`}
                                            data-indicator-color={indicator.color}
                                            data-series-points={indicator.series.length}
                                            data-series-last-timestamp={indicator.series.at(-1)?.timestamp_utc ?? ''}
                                        >
                                            <div className="flex items-start gap-2">
                                                <span className="mt-1 h-3 w-3 shrink-0 rounded-full border border-white/20" style={{ backgroundColor: indicator.color }} aria-hidden="true" />
                                                <div className="min-w-0">
                                                    <p className="font-semibold text-[#eaecef]">{indicator.label}</p>
                                                    {Object.keys(indicator.parameters).length > 0 ? (
                                                        <p className="text-xs text-[#929aa5]">
                                                            Configuração: {Object.entries(indicator.parameters).map(([key, value]) => `${key}=${String(value)}`).join(', ')}
                                                        </p>
                                                    ) : null}
                                                    <p className="text-xs text-[#929aa5]">
                                                        Painel {indicator.panel} • escala {indicator.scale} • valor {isAvailable && value !== null && value !== undefined ? formatPrice(value) : 'indisponível'}
                                                    </p>
                                                </div>
                                            </div>
                                            {indicator.function ? <p className="mt-2 text-xs text-[#929aa5]">Função: {indicator.function}</p> : null}
                                            {indicator.participation.length > 0 ? <p className="mt-1 text-xs text-[#929aa5]">Participação: {indicator.participation.join(', ')}</p> : null}
                                            {indicator.references.length > 0 ? (
                                                <p className="mt-1 text-xs text-[#929aa5]">
                                                    Referências: {indicator.references.map((reference) => `${reference.label} (${formatPrice(reference.value)})`).join(', ')}
                                                </p>
                                            ) : null}
                                            {!isAvailable ? (
                                                <p className="mt-2 text-xs text-[#fcd535]" role="status">
                                                    Série indisponível{indicator.unavailable_reason ? `: ${indicator.unavailable_reason}` : '.'}
                                                </p>
                                            ) : null}
                                        </li>
                                    )
                                })}
                            </ul>

                            {transparency.indicators.length === 0 ? (
                                <p className="mt-3 text-sm text-[#929aa5]">Nenhuma série de indicador disponível.</p>
                            ) : null}

                            {Object.keys(transparency.effective_parameters).length > 0 ? (
                                <dl className="mt-3 grid gap-2 text-xs sm:grid-cols-2" aria-label="Parâmetros efetivos da estratégia">
                                    {Object.entries(transparency.effective_parameters).map(([key, value]) => (
                                        <div key={key} className="flex justify-between gap-3 rounded-md bg-[#0b0e11] px-3 py-2">
                                            <dt className="text-[#929aa5]">{key.replace(/_/g, ' ')}</dt>
                                            <dd className="font-mono text-[#eaecef]">{String(value)}</dd>
                                        </div>
                                    ))}
                                </dl>
                            ) : null}

                            {transparency.logic_blocks.length > 0 ? (
                                <div className="mt-3">
                                    <h4 className="text-xs font-semibold uppercase text-[#929aa5]">Lógica funcional</h4>
                                    <ul className="mt-2 list-disc space-y-1 pl-5 text-sm text-[#eaecef]">
                                        {transparency.logic_blocks.map((block, index) => <li key={`${block}-${index}`}>{block}</li>)}
                                    </ul>
                                </div>
                            ) : null}
                        </section>
                    ) : null}
                </div>

                {showSideContent ? (
                    <aside className={sideClassName}>
                        {typeof sideContent === 'function' ? sideContent(displaySnapshot) : sideContent ?? (
                            <>
                                <p className="mb-3 text-xs font-semibold uppercase tracking-normal text-[#929aa5]">Candle</p>
                                <dl className="grid grid-cols-2 gap-3 text-sm xl:grid-cols-1">
                                    <div>
                                        <dt className="text-[#707a8a]">Fechamento</dt>
                                        <dd className="font-mono font-semibold text-[#eaecef]">{formatPrice(displaySnapshot?.candle.close)}</dd>
                                    </div>
                                    <div>
                                            <dt className="text-[#707a8a]">Máxima / Mínima</dt>
                                        <dd className="font-mono text-[#eaecef]">
                                            {formatPrice(displaySnapshot?.candle.high)} / {formatPrice(displaySnapshot?.candle.low)}
                                        </dd>
                                    </div>
                                    <div>
                                        <dt className="text-[#707a8a]">Volume</dt>
                                        <dd className="font-mono text-[#eaecef]">{formatVolume(displaySnapshot?.candle.volume)}</dd>
                                    </div>
                                </dl>
                            </>
                        )}
                    </aside>
                ) : null}
            </div>

            {belowContent ? (
                <div className="border-t border-[#2b3139] bg-[#0b0e11] p-3 sm:p-4">
                    {belowContent}
                </div>
            ) : null}

            {footerContent ? (
                <footer className="border-t border-[#2b3139] bg-[#1e2329] px-5 py-3">
                    {footerContent}
                </footer>
            ) : null}
        </section>
    )
}
