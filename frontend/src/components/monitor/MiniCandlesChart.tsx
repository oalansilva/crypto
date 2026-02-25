import { useEffect, useRef } from 'react'
import { createChart, ColorType } from 'lightweight-charts'

export interface MarketCandle {
  timestamp_utc: string
  open: number
  high: number
  low: number
  close: number
  volume: number
}

interface MiniCandlesChartProps {
  candles: MarketCandle[]
}

export function MiniCandlesChart({ candles }: MiniCandlesChartProps) {
  const chartContainerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!chartContainerRef.current || candles.length === 0) return

    const chart = createChart(chartContainerRef.current, {
      layout: {
        background: { type: ColorType.Solid, color: 'transparent' },
        textColor: '#94a3b8',
      },
      grid: {
        vertLines: { color: 'rgba(255, 255, 255, 0.06)' },
        horzLines: { color: 'rgba(255, 255, 255, 0.06)' },
      },
      rightPriceScale: { borderColor: 'rgba(255, 255, 255, 0.12)' },
      timeScale: {
        borderColor: 'rgba(255, 255, 255, 0.12)',
        timeVisible: true,
        secondsVisible: false,
      },
      width: chartContainerRef.current.clientWidth,
      height: 280,
    })

    const series = chart.addCandlestickSeries({
      upColor: '#22c55e',
      downColor: '#ef4444',
      borderUpColor: '#22c55e',
      borderDownColor: '#ef4444',
      wickUpColor: '#22c55e',
      wickDownColor: '#ef4444',
    })

    const chartData = candles
      .map((c) => ({
        time: Math.floor(new Date(c.timestamp_utc).getTime() / 1000) as any,
        open: c.open,
        high: c.high,
        low: c.low,
        close: c.close,
      }))
      .sort((a, b) => a.time - b.time)

    series.setData(chartData)
    chart.timeScale().fitContent()

    const handleResize = () => {
      if (chartContainerRef.current) {
        chart.applyOptions({ width: chartContainerRef.current.clientWidth })
      }
    }
    window.addEventListener('resize', handleResize)
    return () => {
      window.removeEventListener('resize', handleResize)
      chart.remove()
    }
  }, [candles])

  return <div ref={chartContainerRef} className="w-full" data-testid="market-candles-chart" />
}
