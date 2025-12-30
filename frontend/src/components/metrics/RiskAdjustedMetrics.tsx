import React from 'react';
import { Activity } from 'lucide-react';
import { MetricCard } from './MetricCard';
import { MetricSection } from './MetricSection';

interface RiskAdjustedMetricsProps {
    metrics: {
        sharpe_ratio?: number;
        sortino_ratio?: number;
        calmar_ratio?: number;
    };
}

export const RiskAdjustedMetrics: React.FC<RiskAdjustedMetricsProps> = ({ metrics }) => {
    const getRatioStatus = (value: number | undefined, goodThreshold: number, excellentThreshold: number) => {
        if (value === undefined) return 'neutral';
        if (value >= excellentThreshold) return 'good';
        if (value >= goodThreshold) return 'warning';
        return 'bad';
    };

    return (
        <MetricSection
            title="Retorno Ajustado ao Risco"
            icon={<Activity className="w-5 h-5 text-purple-400" />}
        >
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <MetricCard
                    label="Sharpe Ratio"
                    value={metrics.sharpe_ratio ?? 0}
                    format="ratio"
                    status={getRatioStatus(metrics.sharpe_ratio, 1.0, 2.0)}
                    tooltip="Retorno por unidade de risco total. ≥1.0 = bom, ≥2.0 = excelente"
                />

                <MetricCard
                    label="Sortino Ratio"
                    value={metrics.sortino_ratio ?? 0}
                    format="ratio"
                    status={getRatioStatus(metrics.sortino_ratio, 1.3, 2.0)}
                    tooltip="Penaliza apenas volatilidade negativa (downside). Melhor que Sharpe para estratégias assimétricas"
                />

                <MetricCard
                    label="Calmar Ratio ⭐"
                    value={metrics.calmar_ratio ?? 0}
                    format="ratio"
                    status={getRatioStatus(metrics.calmar_ratio, 1.0, 1.5)}
                    tooltip="CAGR / Max DD. Excelente para swing trading. ≥1.0 = bom, ≥1.5 = excelente"
                />
            </div>

            <div className="mt-4 p-3 bg-purple-900/20 border border-purple-500/30 rounded">
                <p className="text-xs text-gray-400">
                    <span className="font-semibold text-purple-300">Dica:</span> Calmar Ratio é especialmente útil para crypto swing trading pois considera o drawdown máximo em vez da volatilidade total.
                </p>
            </div>
        </MetricSection>
    );
};
