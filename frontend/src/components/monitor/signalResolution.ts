import type { Opportunity } from './types';
import type { MarkerSignalType } from '@/lib/tradeMarkers';

export type MonitorSignalKind = 'hold' | 'exit';

type MarkerDirection = 'aboveBar' | 'belowBar';
type MarkerShape = 'arrowDown' | 'arrowUp';

export interface MonitorSignalVisual {
    readonly badgeText: string;
    readonly badgeClass: string;
    readonly borderClass: string;
    readonly cardBgClass: string;
    readonly titleClass: string;
    readonly markerLabel: 'Compra' | 'Venda';
    readonly distanceLabel: 'compra' | 'venda';
    readonly markerPosition: MarkerDirection;
    readonly markerShape: MarkerShape;
    readonly markerColor: string;
    readonly statusClass: 'info' | 'warning' | 'danger';
}

export interface ResolvedMonitorSignal {
    readonly section: MonitorSignalKind;
    readonly isUncertain: boolean;
    readonly statusMessage: string;
    readonly freshnessReason: string | null;
    readonly strategyTimeframe: string | null;
    readonly displayTimeframe: string | null;
    readonly referenceCandleTime: string | null;
    readonly latestCandleTime: string | null;
    readonly visual: MonitorSignalVisual;
}

export interface ResolveOpportunitySignalContext {
    readonly selectedTimeframe?: string | null;
    readonly latestCandleTime?: string | null;
    readonly latestSignalTime?: string | null;
    readonly latestSignalType?: 'entry' | 'exit' | null;
    readonly latestVisibleMarkerType?: MarkerSignalType | null;
    readonly requireCurrentCandleMatch?: boolean;
    readonly hasVisibleActiveEntry?: boolean | null;
}

const TIMEFRAME_TO_MS: Record<string, number> = {
    '15m': 15 * 60 * 1000,
    '1h': 60 * 60 * 1000,
    '4h': 4 * 60 * 60 * 1000,
    '1d': 24 * 60 * 60 * 1000,
};

const VISUAL_BY_KIND: Record<MonitorSignalKind, MonitorSignalVisual> = {
    hold: {
        badgeText: 'Compra',
        badgeClass: 'bg-green-600 text-white border-green-600 font-bold shadow-md',
        borderClass: 'border-l-green-600 border-l-4',
        cardBgClass: 'bg-green-50 dark:bg-green-900/40 border-green-400 dark:border-green-600',
        titleClass: 'text-green-700 dark:text-green-300',
        markerLabel: 'Compra',
        distanceLabel: 'venda',
        markerPosition: 'belowBar',
        markerShape: 'arrowUp',
        markerColor: '#3fb950',
        statusClass: 'info',
    },
    exit: {
        badgeText: 'Venda',
        badgeClass: 'bg-sky-600 text-white border-sky-600 font-bold shadow-md',
        borderClass: 'border-l-sky-600 border-l-4',
        cardBgClass: 'bg-sky-50 dark:bg-sky-900/30 border-sky-300 dark:border-sky-700',
        titleClass: 'text-sky-700 dark:text-sky-300',
        markerLabel: 'Venda',
        distanceLabel: 'compra',
        markerPosition: 'aboveBar',
        markerShape: 'arrowDown',
        markerColor: '#0284c7',
        statusClass: 'info',
    },
};

const normalizeDirection = (opportunity: Opportunity): 'long' | 'short' => {
    const raw = String((opportunity as any).direction ?? opportunity.parameters?.direction ?? 'long').trim().toLowerCase();
    return raw === 'short' ? 'short' : 'long';
};

const resolveVisual = (section: MonitorSignalKind, direction: 'long' | 'short'): MonitorSignalVisual => {
    if (direction === 'long') return VISUAL_BY_KIND[section];
    if (section === 'hold') {
        return {
            badgeText: 'Venda',
            badgeClass: 'bg-red-600 text-white border-red-600 font-bold shadow-md',
            borderClass: 'border-l-red-600 border-l-4',
            cardBgClass: 'bg-red-50 dark:bg-red-900/30 border-red-300 dark:border-red-700',
            titleClass: 'text-red-700 dark:text-red-300',
            markerLabel: 'Venda',
            distanceLabel: 'compra',
            markerPosition: 'aboveBar',
            markerShape: 'arrowDown',
            markerColor: '#f6465d',
            statusClass: 'info',
        };
    }
    return {
        badgeText: 'Compra',
        badgeClass: 'bg-green-600 text-white border-green-600 font-bold shadow-md',
        borderClass: 'border-l-green-600 border-l-4',
        cardBgClass: 'bg-green-50 dark:bg-green-900/40 border-green-400 dark:border-green-600',
        titleClass: 'text-green-700 dark:text-green-300',
        markerLabel: 'Compra',
        distanceLabel: 'venda',
        markerPosition: 'belowBar',
        markerShape: 'arrowUp',
        markerColor: '#0ecb81',
        statusClass: 'info',
    };
};

const asStatus = (rawStatus: unknown): string => String(rawStatus || '').trim().toUpperCase();
const normalizeTimeframe = (timeframe: string | null | undefined): string => String(timeframe || '').trim().toLowerCase();
const normalizeNextStatus = (nextStatusLabel: string | null | undefined): string => {
    const normalized = String(nextStatusLabel || '').trim().toLowerCase();
    if (normalized === 'entry') return 'entrada';
    if (normalized === 're-entry') return 'reentrada';
    if (normalized === 'confirmation') return 'confirmação';
    if (normalized === 'exit') return 'saída';
    return 'próxima decisão';
};

const toPublicSignalMessage = (message: string, direction: 'long' | 'short'): string => {
    const entry = direction === 'short' ? 'Venda' : 'Compra';
    const exit = direction === 'short' ? 'Compra' : 'Venda';
    return message
        .replace(/\bEXIT\b/g, exit)
        .replace(/\bHOLD\b/g, entry)
        .replace(/\bExit\b/g, exit)
        .replace(/\bHold\b/g, entry)
        .replace(/\bexit\b/g, exit.toLowerCase())
        .replace(/\bhold\b/g, entry.toLowerCase())
        .replace(/entry/g, 'entrada')
        .replace(/buy/g, 'compra')
        .replace(/sell/g, 'venda');
};

const toMsByTimeframe = (timeframe: string | null | undefined): number => {
    return TIMEFRAME_TO_MS[normalizeTimeframe(timeframe) || '1d'] ?? TIMEFRAME_TO_MS['1d'];
};

const isExplicitExitStatus = (rawStatus: string): boolean => (
    rawStatus === 'EXIT'
    || rawStatus === 'EXIT_SIGNAL'
    || rawStatus === 'EXIT_NEAR'
    || rawStatus === 'EXITED'
    || rawStatus === 'STOPPED_OUT'
    || rawStatus === 'MISSED_ENTRY'
    || rawStatus === 'MISSED'
);

const isStale = (referenceTime: string | null | undefined, timeframe: string | undefined): boolean => {
    if (!referenceTime) return false;
    const candleTime = Date.parse(referenceTime);
    if (Number.isNaN(candleTime)) return false;

    const maxAge = toMsByTimeframe(timeframe) * 3;
    return Date.now() - candleTime > maxAge;
};

const hasSameCandleReference = (
    referenceTime: string | null | undefined,
    latestCandleTime: string | null | undefined,
): boolean => {
    if (!referenceTime || !latestCandleTime) return false;

    const referenceMs = Date.parse(referenceTime);
    const latestMs = Date.parse(latestCandleTime);
    if (Number.isNaN(referenceMs) || Number.isNaN(latestMs)) return false;

    return referenceMs === latestMs;
};

export const resolveOpportunitySignal = (
    opportunity: Opportunity,
    context: ResolveOpportunitySignalContext = {},
): ResolvedMonitorSignal => {
    const rawStatus = asStatus(opportunity.status);
    const isHolding = Boolean(opportunity.is_holding);
    const direction = normalizeDirection(opportunity);
    const selectedTimeframe = normalizeTimeframe(context.selectedTimeframe);
    const strategyTimeframe = normalizeTimeframe(opportunity.timeframe);
    const timeframeMismatch = Boolean(selectedTimeframe) && selectedTimeframe !== strategyTimeframe;
    const decisionReferenceTime = (
        rawStatus === 'EXIT_SIGNAL'
        && context.latestSignalType === 'exit'
        && context.latestSignalTime
    )
        ? context.latestSignalTime
        : opportunity.indicator_values_candle_time;
    const exitSignalMatchesChart = (
        rawStatus === 'EXIT_SIGNAL'
        && context.latestSignalType === 'exit'
        && hasSameCandleReference(decisionReferenceTime, context.latestCandleTime)
    );
    const uncertainty = exitSignalMatchesChart
        ? false
        : isStale(opportunity.indicator_values_candle_time, opportunity.timeframe);
    const candleMismatch = Boolean(context.requireCurrentCandleMatch) && !hasSameCandleReference(
        decisionReferenceTime,
        context.latestCandleTime,
    );
    const activeEntryMissingFromChart = Boolean(isHolding)
        && rawStatus !== 'EXIT_SIGNAL'
        && context.hasVisibleActiveEntry === false;

    let section: MonitorSignalKind = isHolding ? 'hold' : 'exit';
    let isUncertain = uncertainty || timeframeMismatch || candleMismatch || activeEntryMissingFromChart;
    const reasons: string[] = [];
    if (uncertainty) {
        reasons.push('Sem candle válido/atual para esta resolução.');
    }
    if (timeframeMismatch) {
        reasons.push('Venda bloqueada: timeframe da estratégia não corresponde ao timeframe exibido.');
    }
    if (candleMismatch) {
        reasons.push('Venda bloqueada: candle de referência não corresponde ao último candle exibido.');
    }
    if (activeEntryMissingFromChart) {
        reasons.push('Compra bloqueada: entrada ativa não aparece nos candles exibidos.');
    }

    if (rawStatus === 'EXIT' || rawStatus === 'EXIT_SIGNAL' || rawStatus === 'EXIT_NEAR') {
        section = 'exit';
    } else if (rawStatus === 'HOLDING' || rawStatus === 'HOLD') {
        section = isHolding || rawStatus === 'HOLD' ? 'hold' : 'exit';
        if (!isHolding) {
            isUncertain = true;
            reasons.push('Estado de decisão indica posição ativa, mas o sinal não confirma compra.');
        }
    } else if (rawStatus === 'EXITED' || rawStatus === 'STOPPED_OUT' || rawStatus === 'MISSED_ENTRY' || rawStatus === 'MISSED') {
        section = 'exit';
        if (isHolding) {
            isUncertain = true;
            reasons.push('Estado de saída inconsistente com posição aberta.');
        }
    } else if (rawStatus === 'BUY_SIGNAL') {
        section = 'hold';
    } else if (rawStatus === 'NEUTRAL' || rawStatus === 'BUY_NEAR') {
        section = isHolding ? 'hold' : 'exit';
    } else if (rawStatus) {
        section = isHolding ? 'hold' : 'exit';
        if (!isHolding) {
            isUncertain = true;
            reasons.push('Estado desconhecido, tratado como venda.');
        }
    }

    if (context.latestVisibleMarkerType === 'entry' && !isExplicitExitStatus(rawStatus)) {
        section = 'hold';
        isUncertain = false;
        reasons.length = 0;
    } else if (context.latestVisibleMarkerType === 'exit') {
        section = 'exit';
        isUncertain = false;
        reasons.length = 0;
    }

    const sectionVisual = resolveVisual(section, direction);
    const freshnessReason = reasons.length > 0 ? reasons.join(' ') : null;
    const fallbackStatusMessage = isUncertain
        ? 'Estado em revisão: decisão não confirmada pelo contexto atual.'
        : toPublicSignalMessage(
            opportunity.message || `Aguardando condição de ${normalizeNextStatus(opportunity.next_status_label)} para decisão.`,
            direction,
        );

    return {
        section,
        isUncertain,
        statusMessage: fallbackStatusMessage,
        freshnessReason,
        strategyTimeframe: strategyTimeframe || null,
        displayTimeframe: selectedTimeframe || strategyTimeframe || null,
        referenceCandleTime: decisionReferenceTime ?? null,
        latestCandleTime: context.latestCandleTime ?? null,
        visual: {
            ...sectionVisual,
        },
    };
};

export const hasExitedOpportunity = (opportunity: Opportunity): boolean => {
    const rawStatus = asStatus(opportunity.status);
    const isHolding = Boolean(opportunity.is_holding);

    return (
        rawStatus === 'EXIT'
        || rawStatus === 'EXIT_SIGNAL'
        || rawStatus === 'EXIT_NEAR'
        || (
            !isHolding
            && (
                rawStatus === 'EXITED'
                || rawStatus === 'STOPPED_OUT'
                || rawStatus === 'MISSED_ENTRY'
                || rawStatus === 'MISSED'
            )
        )
    );
};
