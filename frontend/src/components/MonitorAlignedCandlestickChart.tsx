import {
    StrategyChartSurface,
    type StrategyChartCandle,
    type StrategyChartMarker,
} from './charts/StrategyChartSurface'
import type { StrategyTransparency } from '../lib/strategyTransparency'

interface MonitorAlignedCandlestickChartProps {
    candles: StrategyChartCandle[]
    markers?: StrategyChartMarker[]
    strategyName: string
    symbol?: string
    timeframe?: string
    strategyTransparency?: StrategyTransparency | Record<string, unknown> | null
}

export function MonitorAlignedCandlestickChart({
    candles,
    markers,
    strategyName,
    symbol,
    timeframe,
    strategyTransparency,
}: MonitorAlignedCandlestickChartProps) {
    return (
        <StrategyChartSurface
            candles={candles}
            markers={markers}
            strategyName={strategyName}
            symbol={symbol}
            timeframe={timeframe}
            strategyTransparency={strategyTransparency}
            rootTestId="monitor-aligned-result-chart"
            chartTestId="result-main-chart"
            shellTestId="result-chart-shell"
            zoomTestIdPrefix="result-chart"
            visibleBarsTestId="result-chart-visible-bars"
            markerCount={markers?.length ?? 0}
        />
    )
}
