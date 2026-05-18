import {
    StrategyChartSurface,
    type StrategyChartCandle,
    type StrategyChartMarker,
} from './charts/StrategyChartSurface'

interface MonitorAlignedCandlestickChartProps {
    candles: StrategyChartCandle[]
    markers?: StrategyChartMarker[]
    strategyName: string
    symbol?: string
    timeframe?: string
}

export function MonitorAlignedCandlestickChart({
    candles,
    markers,
    strategyName,
    symbol,
    timeframe,
}: MonitorAlignedCandlestickChartProps) {
    return (
        <StrategyChartSurface
            candles={candles}
            markers={markers}
            strategyName={strategyName}
            symbol={symbol}
            timeframe={timeframe}
            rootTestId="monitor-aligned-result-chart"
            chartTestId="result-main-chart"
            shellTestId="result-chart-shell"
            zoomTestIdPrefix="result-chart"
            visibleBarsTestId="result-chart-visible-bars"
            markerCount={markers?.length ?? 0}
        />
    )
}
