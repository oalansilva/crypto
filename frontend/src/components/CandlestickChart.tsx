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

        // Remove duplicates and sort by time
        const uniqueCandles = candleData.reduce((acc, candle) => {
            const existing = acc.find(c => c.time === candle.time)
            if (!existing) {
                acc.push(candle)
            }
            return acc
        }, [] as typeof candleData)

        const sortedCandles = uniqueCandles.sort((a, b) => a.time - b.time)

        candlestickSeries.setData(sortedCandles)

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

        // Indicators lines removed as per user request to keep chart clean
        // Only showing candles and order markers

        // Fit content with better spacing
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

            {/* Indicator Legend - Removed as lines are hidden */}

            <div ref={chartContainerRef} className="w-full" />
        </div>
    )
}
