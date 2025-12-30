import React from 'react';
import {
    GoNoGoIndicator,
    PerformanceMetrics,
    RiskMetrics,
    RiskAdjustedMetrics,
    TradeStatistics
} from '../metrics';

interface EnhancedMetricsDisplayProps {
    metrics: any; // Full metrics object from backend
}

export const EnhancedMetricsDisplay: React.FC<EnhancedMetricsDisplayProps> = ({ metrics }) => {
    // Check if we have enhanced metrics
    const hasEnhancedMetrics = metrics && (
        metrics.cagr !== undefined ||
        metrics.sortino_ratio !== undefined ||
        metrics.calmar_ratio !== undefined ||
        metrics.criteria_result !== undefined
    );

    if (!hasEnhancedMetrics) {
        return null; // Don't render if no enhanced metrics
    }

    return (
        <div className="space-y-6 mt-8">
            {/* GO/NO-GO Indicator */}
            {metrics.criteria_result && (
                <GoNoGoIndicator criteria={metrics.criteria_result} />
            )}

            {/* Performance Metrics */}
            <PerformanceMetrics
                metrics={{
                    total_return_pct: metrics.total_return_pct,
                    cagr: metrics.cagr,
                    monthly_return_avg: metrics.monthly_return_avg
                }}
                benchmark={metrics.benchmark}
            />

            {/* Risk Metrics */}
            <RiskMetrics
                metrics={{
                    max_drawdown: metrics.max_drawdown,
                    avg_drawdown: metrics.avg_drawdown,
                    max_dd_duration_days: metrics.max_dd_duration_days,
                    recovery_factor: metrics.recovery_factor
                }}
            />

            {/* Risk-Adjusted Metrics */}
            <RiskAdjustedMetrics
                metrics={{
                    sharpe_ratio: metrics.sharpe_ratio,
                    sortino_ratio: metrics.sortino_ratio,
                    calmar_ratio: metrics.calmar_ratio
                }}
            />

            {/* Trade Statistics */}
            <TradeStatistics
                metrics={{
                    total_trades: metrics.total_trades,
                    win_rate: metrics.win_rate,
                    profit_factor: metrics.profit_factor,
                    expectancy: metrics.expectancy,
                    max_consecutive_wins: metrics.max_consecutive_wins,
                    max_consecutive_losses: metrics.max_consecutive_losses,
                    trade_concentration_top_10_pct: metrics.trade_concentration_top_10_pct
                }}
            />
        </div>
    );
};
