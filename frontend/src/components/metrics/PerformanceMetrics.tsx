import React from 'react';
import { TrendingUp } from 'lucide-react';
import { MetricCard } from './MetricCard';
import { MetricSection } from './MetricSection';

interface PerformanceMetricsProps {
    metrics: {
        total_return_pct?: number;
        cagr?: number;
        monthly_return_avg?: number;
    };
    benchmark?: {
        return_pct?: number;
        cagr?: number;
    };
}

export const PerformanceMetrics: React.FC<PerformanceMetricsProps> = ({ metrics, benchmark }) => {
    const getStatus = (value: number | undefined, benchmarkValue: number | undefined) => {
        if (value === undefined) return 'neutral';
        if (benchmarkValue === undefined) return value > 0 ? 'good' : 'bad';
        return value > benchmarkValue ? 'good' : value > benchmarkValue * 0.9 ? 'warning' : 'bad';
    };

    return (
        <MetricSection
            title="Performance"
            icon={<TrendingUp className="w-5 h-5 text-blue-400" />}
            defaultExpanded={true}
        >
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <MetricCard
                    label="Retorno Total"
                    value={metrics.total_return_pct ?? 0}
                    format="percentage"
                    status={getStatus(metrics.total_return_pct, benchmark?.return_pct)}
                    subtitle={benchmark ? `B&H: ${((benchmark.return_pct ?? 0) * 100).toFixed(2)}%` : undefined}
                    tooltip="Retorno total da estratégia no período testado"
                />

                <MetricCard
                    label="CAGR"
                    value={metrics.cagr ?? 0}
                    format="percentage"
                    status={getStatus(metrics.cagr, benchmark?.cagr)}
                    subtitle={benchmark ? `B&H: ${((benchmark.cagr ?? 0) * 100).toFixed(2)}%` : undefined}
                    tooltip="Compound Annual Growth Rate - permite comparação justa entre períodos diferentes"
                />

                <MetricCard
                    label="Retorno Médio Mensal"
                    value={metrics.monthly_return_avg ?? 0}
                    format="percentage"
                    status={(metrics.monthly_return_avg ?? 0) > 0 ? 'good' : 'bad'}
                    tooltip="Retorno médio mensal - indica consistência da estratégia"
                />
            </div>

            {benchmark && (
                <div className="mt-4 p-3 bg-blue-900/20 border border-blue-500/30 rounded">
                    <p className="text-sm text-gray-300">
                        <span className="font-semibold text-blue-300">Alpha: </span>
                        {metrics.cagr && benchmark.cagr
                            ? `${((metrics.cagr - benchmark.cagr) * 100).toFixed(2)}%`
                            : 'N/A'
                        } (excesso de retorno vs Buy & Hold)
                    </p>
                </div>
            )}
        </MetricSection>
    );
};
