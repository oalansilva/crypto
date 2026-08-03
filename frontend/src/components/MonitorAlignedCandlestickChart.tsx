import {
    StrategyChartSurface,
    type StrategyChartCandle,
    type StrategyChartConfigurationItem,
    type StrategyChartMarker,
} from './charts/StrategyChartSurface'
import { normalizeStrategyTransparency, type StrategyTransparency } from '../lib/strategyTransparency'
import { formatStrategyParameterLabel, formatStrategyParameterValue } from '../lib/strategyParameters'

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
        ? [
            ...transparency.indicators.map((indicator) => ({
                label: `${indicator.label}${Object.keys(indicator.parameters).length > 0
                    ? ` ${Object.entries(indicator.parameters)
                        .map(([key, value]) => `${formatStrategyParameterLabel(key)}=${formatStrategyParameterValue(key, value)}`)
                        .join(', ')}`
                    : ''}`,
                color: indicator.color,
            })),
            ...Object.entries(transparency.effective_parameters)
                .filter(([key]) => ['direction', 'stop_loss', 'take_profit'].includes(key))
                .map(([key, value]) => ({
                    label: `${formatStrategyParameterLabel(key)} ${formatStrategyParameterValue(key, value)}`,
                })),
        ]
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
        />
    )
}
