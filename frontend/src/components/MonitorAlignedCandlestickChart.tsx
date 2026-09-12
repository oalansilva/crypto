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
    tradeListCount?: number
    strategyName: string
    symbol?: string
    timeframe?: string
    strategyTransparency?: StrategyTransparency | Record<string, unknown> | null
}

export function MonitorAlignedCandlestickChart({
    candles,
    markers,
    tradeListCount,
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
            toolbarLeading={typeof tradeListCount === 'number' ? (
                <span
                    className="rounded-md border border-[#0ecb81]/35 bg-[#0ecb81]/10 px-2.5 py-1 text-xs font-semibold text-[#0ecb81]"
                    data-testid="history-pair"
                >
                    {`Lista ${tradeListCount} · Setas ${markers?.length ?? 0} (entrada+saída) · 1:1`}
                </span>
            ) : undefined}
            rootTestId="monitor-aligned-result-chart"
            chartTestId="result-main-chart"
            shellTestId="result-chart-shell"
            zoomTestIdPrefix="result-chart"
            visibleBarsTestId="result-chart-visible-bars"
            markerCount={markers?.length ?? 0}
            listCount={tradeListCount}
            showTransparencyDetails={false}
        />
    )
}
