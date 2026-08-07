import {
    StrategyChartSurface,
    type StrategyChartCandle,
    type StrategyChartConfigurationItem,
    type StrategyChartMarker,
} from './charts/StrategyChartSurface'
import { normalizeStrategyTransparency, type StrategyTransparency } from '../lib/strategyTransparency'

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
    const transparency = normalizeStrategyTransparency(strategyTransparency)
    const configurationItems: StrategyChartConfigurationItem[] = transparency
        ? transparency.indicators.map((indicator) => ({
                label: indicator.label,
                color: indicator.color,
            }))
        : []

    return (
        <StrategyChartSurface
            candles={candles}
            markers={markers}
            strategyName={strategyName}
            symbol={symbol}
            timeframe={timeframe}
            viewportResetKey={`${symbol || ''}|${timeframe || ''}`}
            strategyTransparency={strategyTransparency}
            configurationItems={configurationItems}
            rootTestId="monitor-aligned-result-chart"
            chartTestId="result-main-chart"
            shellTestId="result-chart-shell"
            zoomTestIdPrefix="result-chart"
            visibleBarsTestId="result-chart-visible-bars"
            markerCount={markers?.length ?? 0}
            showTransparencyDetails={false}
        />
    )
}
