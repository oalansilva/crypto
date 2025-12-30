import React from 'react';
import { Shield } from 'lucide-react';
import { MetricCard } from './MetricCard';
import { MetricSection } from './MetricSection';

interface RiskMetricsProps {
    metrics: {
        max_drawdown?: number;
        avg_drawdown?: number;
        max_dd_duration_days?: number;
        recovery_factor?: number;
    };
}

export const RiskMetrics: React.FC<RiskMetricsProps> = ({ metrics }) => {
    const getDrawdownStatus = (dd: number | undefined) => {
        if (dd === undefined) return 'neutral';
        if (dd <= 0.20) return 'good';
        if (dd <= 0.35) return 'warning';
        return 'bad';
    };

    const getRecoveryStatus = (rf: number | undefined) => {
        if (rf === undefined) return 'neutral';
        if (rf >= 2.0) return 'good';
        if (rf >= 1.0) return 'warning';
        return 'bad';
    };

    return (
        <MetricSection
            title="Risco"
            icon={<Shield className="w-5 h-5 text-orange-400" />}
        >
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <MetricCard
                    label="Max Drawdown"
                    value={metrics.max_drawdown ?? 0}
                    format="percentage"
                    status={getDrawdownStatus(metrics.max_drawdown)}
                    tooltip="Maior queda do pico ao vale. Limite recomendado: ≤35% para crypto swing"
                />

                <MetricCard
                    label="Drawdown Médio"
                    value={metrics.avg_drawdown ?? 0}
                    format="percentage"
                    status={getDrawdownStatus(metrics.avg_drawdown)}
                    tooltip="Drawdown médio - indica frequência e magnitude típica das quedas"
                />

                <MetricCard
                    label="Tempo Máx em DD"
                    value={metrics.max_dd_duration_days ?? 0}
                    subtitle="dias"
                    status={(metrics.max_dd_duration_days ?? 0) > 60 ? 'bad' : (metrics.max_dd_duration_days ?? 0) > 30 ? 'warning' : 'good'}
                    tooltip="Tempo máximo em drawdown - impacto psicológico"
                />

                <MetricCard
                    label="Recovery Factor"
                    value={metrics.recovery_factor ?? 0}
                    format="ratio"
                    status={getRecoveryStatus(metrics.recovery_factor)}
                    tooltip="Retorno / Max DD. Valores >1.0 indicam boa recuperação"
                />
            </div>

            {metrics.max_drawdown && metrics.max_drawdown > 0.35 && (
                <div className="mt-4 p-3 bg-red-900/20 border border-red-500/30 rounded">
                    <p className="text-sm text-red-300">
                        ⚠ <span className="font-semibold">Alerta:</span> Max Drawdown acima do limite recomendado (35%)
                    </p>
                </div>
            )}
        </MetricSection>
    );
};
