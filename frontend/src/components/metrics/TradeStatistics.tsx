import React from 'react';
import { BarChart3 } from 'lucide-react';
import { MetricCard } from './MetricCard';
import { MetricSection } from './MetricSection';

interface TradeStatisticsProps {
    metrics: {
        total_trades?: number;
        win_rate?: number;
        profit_factor?: number;
        expectancy?: number;
        max_consecutive_wins?: number;
        max_consecutive_losses?: number;
        trade_concentration_top_10_pct?: number;
    };
}

export const TradeStatistics: React.FC<TradeStatisticsProps> = ({ metrics }) => {
    const getConcentrationStatus = (concentration: number | undefined) => {
        if (concentration === undefined) return 'neutral';
        if (concentration <= 0.40) return 'good';
        if (concentration <= 0.70) return 'warning';
        return 'bad';
    };

    return (
        <MetricSection
            title="Estatísticas de Trades"
            icon={<BarChart3 className="w-5 h-5 text-green-400" />}
        >
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-4">
                <MetricCard
                    label="Total de Trades"
                    value={metrics.total_trades ?? 0}
                    status={(metrics.total_trades ?? 0) >= 100 ? 'good' : (metrics.total_trades ?? 0) >= 50 ? 'warning' : 'bad'}
                    tooltip="Número total de trades. Mínimo recomendado: 100 para validação estatística"
                />

                <MetricCard
                    label="Win Rate"
                    value={metrics.win_rate ?? 0}
                    format="percentage"
                    status={(metrics.win_rate ?? 0) >= 0.55 ? 'good' : (metrics.win_rate ?? 0) >= 0.45 ? 'warning' : 'bad'}
                    tooltip="Percentual de trades vencedores"
                />

                <MetricCard
                    label="Profit Factor"
                    value={metrics.profit_factor ?? 0}
                    format="ratio"
                    status={(metrics.profit_factor ?? 0) >= 1.5 ? 'good' : (metrics.profit_factor ?? 0) >= 1.3 ? 'warning' : 'bad'}
                    tooltip="Lucro bruto / Perda bruta. Mínimo recomendado: 1.3"
                />

                <MetricCard
                    label="Expectancy"
                    value={metrics.expectancy ?? 0}
                    format="currency"
                    status={(metrics.expectancy ?? 0) > 0 ? 'good' : 'bad'}
                    tooltip="Expectativa de lucro por trade. Deve ser > 0"
                />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <MetricCard
                    label="Sequência Máx de Ganhos"
                    value={metrics.max_consecutive_wins ?? 0}
                    tooltip="Maior sequência de trades vencedores consecutivos"
                />

                <MetricCard
                    label="Sequência Máx de Perdas"
                    value={metrics.max_consecutive_losses ?? 0}
                    status={(metrics.max_consecutive_losses ?? 0) <= 5 ? 'good' : (metrics.max_consecutive_losses ?? 0) <= 10 ? 'warning' : 'bad'}
                    tooltip="Maior sequência de trades perdedores consecutivos - gestão de risco psicológico"
                />

                <MetricCard
                    label="Concentração (Top 10)"
                    value={metrics.trade_concentration_top_10_pct ?? 0}
                    format="percentage"
                    status={getConcentrationStatus(metrics.trade_concentration_top_10_pct)}
                    tooltip="% do lucro nos top 10 trades. >70% = estratégia não confiável"
                />
            </div>

            {metrics.trade_concentration_top_10_pct && metrics.trade_concentration_top_10_pct > 0.70 && (
                <div className="mt-4 p-3 bg-red-900/20 border border-red-500/30 rounded">
                    <p className="text-sm text-red-300">
                        ⚠ <span className="font-semibold">Alerta:</span> Lucro concentrado em poucos trades ({(metrics.trade_concentration_top_10_pct * 100).toFixed(0)}%). Estratégia pode não ser repetível.
                    </p>
                </div>
            )}
        </MetricSection>
    );
};
