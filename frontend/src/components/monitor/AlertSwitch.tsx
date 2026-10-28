import React from 'react';
import { Bell, BellOff } from 'lucide-react';
import { getStrategyDisplayName, type Opportunity } from './types';
import { getConfiguration, isEquityOpportunity, isLegacySource, opportunityRowKey } from './marketState';

/**
 * Card #1122 (Design d2, decisão 18): interruptor "Alerta" por estratégia no Monitor.
 * Ligado por padrão; grava `notify_telegram` do favorito. Sino (ligado) ou sino cortado com borda
 * tracejada (desligado), sempre com texto: nunca só cor.
 */

export type AlertSwitchVariant = 'row' | 'compact' | 'card' | 'detail';

export const ALERT_SWITCH_TITLE = 'Ligar ou desligar o alerta desta estratégia no Telegram';
export const ALERT_SWITCH_ERROR = 'Não foi possível mudar o alerta. Tente de novo.';

/** Configuração curta do nome acessível: "Binance Ações" ou "Stooq fonte antiga" (cripto: nada). */
const configurationName = (opportunity: Opportunity): string | null => {
    if (!isEquityOpportunity(opportunity)) return null;
    if (isLegacySource(opportunity)) return 'Stooq fonte antiga';
    const label = getConfiguration(opportunity)?.label_short;
    const source = String(label || '').split(' · ')[0].trim();
    return source || 'Binance Ações';
};

/** "NVDA 1d" (o nome curto do status da página). */
export const alertStrategyName = (opportunity: Opportunity): string => (
    `${opportunity.symbol} ${opportunity.timeframe || ''}`.trim()
);

/** "Alerta no Telegram · NVDA 1d · Médias Móveis: Tendência em Virada · Binance Ações". */
export const alertSwitchLabel = (opportunity: Opportunity): string => {
    const parts = ['Alerta no Telegram', alertStrategyName(opportunity), getStrategyDisplayName(opportunity)];
    const configuration = configurationName(opportunity);
    if (configuration) parts.push(configuration);
    return parts.filter(Boolean).join(' · ');
};

export const alertSwitchStatus = (opportunity: Opportunity, on: boolean): string => (
    on
        ? `Alerta de ${alertStrategyName(opportunity)} ligado: entrada e saída saem no Telegram.`
        : `Alerta de ${alertStrategyName(opportunity)} desligado: nada sai no Telegram para esta estratégia.`
);

/** Estratégia própria com estrela: a que tem o interruptor (a vitrine nunca tem). */
export const hasAlertSwitch = (opportunity: Pick<Opportunity, 'is_curated_fallback' | 'tier'>): boolean => (
    opportunity.is_curated_fallback !== true && [1, 2, 3].includes(Number(opportunity.tier))
);

interface AlertSwitchProps {
    opportunity: Opportunity;
    variant: AlertSwitchVariant;
    onToggle: (opportunity: Opportunity) => void;
}

const CLASS_BY_VARIANT: Record<AlertSwitchVariant, string> = {
    row: 'row-action alert-switch',
    compact: 'row-action alert-switch alert-switch-compact',
    card: 'btn ghost alert-switch alert-switch-card',
    detail: 'btn ghost alert-switch alert-switch-card',
};

export const AlertSwitch: React.FC<AlertSwitchProps> = ({ opportunity, variant, onToggle }) => {
    const on = opportunity.notify_telegram !== false;
    const key = opportunityRowKey(opportunity);
    const withColon = variant === 'card' || variant === 'detail';
    return (
        <button
            type="button"
            className={CLASS_BY_VARIANT[variant]}
            role="switch"
            aria-checked={on}
            aria-label={alertSwitchLabel(opportunity)}
            title={ALERT_SWITCH_TITLE}
            data-testid={`monitor-alert-${variant}-${key}`}
            onClick={(event) => {
                // O clique não abre nem fecha a linha.
                event.stopPropagation();
                onToggle(opportunity);
            }}
        >
            {on ? (
                <Bell className="alert-switch-icon" aria-hidden="true" />
            ) : (
                <BellOff className="alert-switch-icon" aria-hidden="true" />
            )}
            <span>{withColon ? 'Alerta:' : 'Alerta'}</span>
            <span className="alert-switch-state" aria-hidden="true">{on ? 'ligado' : 'desligado'}</span>
        </button>
    );
};

/** Linha do catálogo (vitrine): sem controle. */
export const CatalogNoAlert: React.FC<{ testId?: string }> = ({ testId }) => (
    <span className="alert-switch-none" data-testid={testId}>Catálogo · sem alerta</span>
);
