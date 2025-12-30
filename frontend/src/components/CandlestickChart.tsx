import { useEffect, useRef } from 'react'
import { CandlestickChart as ChartIcon } from 'lucide-react'
import { createChart, ColorType } from 'lightweight-charts'

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

interface Indicator {
    name: string
    data: { time: number | string; value: number }[]
    color?: string
}

interface CandlestickChartProps {
    candles: Candle[]
    markers?: Marker[]
    indicators?: Indicator[]
    strategyName: string
    color: string
}

export function CandlestickChart({ candles, markers, indicators, strategyName, color }: CandlestickChartProps) {
    const chartContainerRef = useRef<HTMLDivElement>(null)

    useEffect(() => {
        if (!chartContainerRef.current || !candles || candles.length === 0) return

        const chart = createChart(chartContainerRef.current, {
            layout: {
                background: { type: ColorType.Solid, color: 'transparent' },
                textColor: '#94a3b8',
            },
            grid: {
                vertLines: { color: 'rgba(255, 255, 255, 0.05)' },
                horzLines: { color: 'rgba(255, 255, 255, 0.05)' },
            },
            crosshair: {
                mode: 1,
            },
            rightPriceScale: {
                borderColor: 'rgba(255, 255, 255, 0.1)',
            },
            timeScale: {
                borderColor: 'rgba(255, 255, 255, 0.1)',
                timeVisible: true,
                secondsVisible: false,
            },
            width: chartContainerRef.current.clientWidth,
            height: 350,
        })

        const candlestickSeries = chart.addCandlestickSeries({
            upColor: '#10b981',
            downColor: '#ef4444',
            borderUpColor: '#10b981',
            borderDownColor: '#ef4444',
            wickUpColor: '#10b981',
            wickDownColor: '#ef4444',
        })

        // Transform candle data
        const candleData = candles.map(candle => ({
            time: (new Date(candle.timestamp_utc).getTime() / 1000) as any,
            open: candle.open,
            high: candle.high,
            low: candle.low,
            close: candle.close,
        }))

        candlestickSeries.setData(candleData)

        // Add markers if available
        if (markers && markers.length > 0) {
            candlestickSeries.setMarkers(markers.map(m => ({
                ...m,
                time: (typeof m.time === 'number' ? m.time : (new Date(m.time).getTime() / 1000)) as any
            })))
        }

        // Check for oscillators (RSI) to adjust layout
        const hasOscillator = indicators?.some(i => i.name.includes('RSI'))

        // Configure main price scale margins
        chart.priceScale('right').applyOptions({
            scaleMargins: {
                top: 0.1, // Leave space for title
                bottom: hasOscillator ? 0.30 : 0.1, // Leave space for oscillator if present
            },
        })

        // Add indicators lines
        if (indicators && indicators.length > 0) {
            const indicatorColors = ['#fbbf24', '#3b82f6', '#8b5cf6', '#ec4899'] // Amber, Blue, Violet, Pink

            indicators.forEach((ind, index) => {
                const isOscillator = ind.name.includes('RSI')

                const lineSeries = chart.addLineSeries({
                    color: ind.color || indicatorColors[index % indicatorColors.length],
                    lineWidth: 2,
                    title: ind.name,
                    priceScaleId: isOscillator ? 'oscillator' : 'right', // Separate scale for indicators like RSI
                })

                if (isOscillator) {
                    chart.priceScale('oscillator').applyOptions({
                        scaleMargins: {
                            top: 0.75, // Position at bottom 25%
                            bottom: 0,
                        },
                    })
                }

                // Ensure time is correct format
                const lineData = ind.data.map(d => ({
                    time: (typeof d.time === 'number' ? d.time : (new Date(d.time).getTime() / 1000)) as any,
                    value: d.value
                }))

                lineSeries.setData(lineData)
            })
        }

        // Fit content
        chart.timeScale().fitContent()

        // Handle resize
        const handleResize = () => {
            if (chartContainerRef.current) {
                chart.applyOptions({
                    width: chartContainerRef.current.clientWidth,
                })
            }
        }

        window.addEventListener('resize', handleResize)

        return () => {
            window.removeEventListener('resize', handleResize)
            chart.remove()
        }
    }, [candles, markers, indicators])

    return (
        <div className="glass-strong rounded-2xl p-6 border border-white/10 mb-8">
            <div className="flex items-center gap-3 mb-4">
                <div
                    className="p-2.5 rounded-xl"
                    style={{ backgroundColor: `${color}20` }}
                >
                    <ChartIcon className="w-6 h-6" style={{ color }} />
                </div>
                <div>
                    <h2 className="text-2xl font-bold text-white">{strategyName} - Price Action</h2>
                    <p className="text-sm text-gray-400">Candlestick chart with entry/exit markers</p>
                </div>
            </div>

            {/* Indicator Legend */}
            {indicators && indicators.length > 0 && (
                <div className="flex items-center gap-4 mb-4 p-3 glass rounded-xl border border-white/5">
                    <span className="text-sm text-gray-400 font-semibold">Indicadores:</span>
                    {indicators.map((ind, index) => (
                        <div key={index} className="flex items-center gap-2">
                            <div
                                className="w-3 h-3 rounded-sm"
                                style={{ backgroundColor: ind.color || '#ff9800' }}
                            />
                            <span className="text-sm font-medium text-white">{ind.name}</span>
                        </div>
                    ))}
                </div>
            )}

            <div ref={chartContainerRef} className="w-full" />
        </div>
    )
}
