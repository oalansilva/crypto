import React from 'react';
import { AlertTriangle, Circle, Clock, Hourglass } from 'lucide-react';
import type { MarketStateView } from './marketState';

interface MarketStateBadgeProps {
    view: MarketStateView;
    /** Linha da tabela: texto curto (o completo fica no `title`). Cartão: texto completo. */
    compact?: boolean;
    testId?: string;
}

const ICON_BY_TONE = {
    open: Circle,
    closed: Clock,
    stale: AlertTriangle,
    insufficient: Hourglass,
} as const;

/**
 * Card #1122: estado do mercado sob a pílula de Status, em quatro tons com ícone + texto
 * (aberto, fechado, dados atrasados, dados insuficientes). Nunca só cor.
 */
export const MarketStateBadge: React.FC<MarketStateBadgeProps> = ({ view, compact = false, testId }) => {
    const Icon = ICON_BY_TONE[view.tone];
    const hold = compact ? view.holdShort : view.holdFull;
    return (
        <>
            <div
                className="market-state"
                data-tone={view.tone}
                title={view.full}
                data-testid={testId}
            >
                <Icon className="market-state-icon" aria-hidden="true" />
                <span className="market-state-text">{compact ? view.short : view.full}</span>
            </div>
            {hold ? (
                <div
                    className="market-hold-note"
                    data-tone={view.tone}
                    data-testid={testId ? `${testId}-hold` : undefined}
                >
                    {hold}
                </div>
            ) : null}
        </>
    );
};
