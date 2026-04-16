import type { Opportunity } from './types';

export type MonitorSignalKind = 'holding' | 'stoppedOut' | 'exited' | 'missedEntry' | 'waiting';

type MarkerDirection = 'aboveBar' | 'belowBar';
type MarkerShape = 'arrowDown' | 'arrowUp';

export interface MonitorSignalVisual {
    readonly badgeText: string;
    readonly badgeClass: string;
    readonly borderClass: string;
    readonly cardBgClass: string;
    readonly titleClass: string;
    readonly markerLabel: 'ENTRY' | 'EXIT' | 'WAIT';
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
    readonly requireCurrentCandleMatch?: boolean;
}

const TIMEFRAME_TO_MS: Record<string, number> = {
    '15m': 15 * 60 * 1000,
    '1h': 60 * 60 * 1000,
    '4h': 4 * 60 * 60 * 1000,
    '1d': 24 * 60 * 60 * 1000,
};

const VISUAL_BY_KIND: Record<MonitorSignalKind, MonitorSignalVisual> = {
    holding: {
        badgeText: 'HOLD',
        badgeClass: 'bg-green-600 text-white border-green-600 font-bold shadow-md',
        borderClass: 'border-l-green-600 border-l-4',
        cardBgClass: 'bg-green-50 dark:bg-green-900/40 border-green-400 dark:border-green-600',
        titleClass: 'text-green-700 dark:text-green-300',
        markerLabel: 'EXIT',
        markerPosition: 'aboveBar',
        markerShape: 'arrowDown',
        markerColor: '#0ea5e9',
        statusClass: 'info',
    },
    exited: {
        badgeText: 'EXITED',
        badgeClass: 'bg-sky-600 text-white border-sky-600 font-bold shadow-md',
        borderClass: 'border-l-sky-600 border-l-4',
        cardBgClass: 'bg-sky-50 dark:bg-sky-900/30 border-sky-300 dark:border-sky-700',
        titleClass: 'text-sky-700 dark:text-sky-300',
        markerLabel: 'EXIT',
        markerPosition: 'aboveBar',
        markerShape: 'arrowDown',
        markerColor: '#0284c7',
        statusClass: 'info',
    },
    stoppedOut: {
        badgeText: 'STOPPED OUT',
        badgeClass: 'bg-red-600 text-white border-red-600 font-bold shadow-md',
        borderClass: 'border-l-red-600 border-l-4',
        cardBgClass: 'bg-red-50 dark:bg-red-900/40 border-red-400 dark:border-red-600',
        titleClass: 'text-red-700 dark:text-red-300',
        markerLabel: 'ENTRY',
        markerPosition: 'belowBar',
        markerShape: 'arrowUp',
        markerColor: '#dc2626',
        statusClass: 'danger',
    },
    missedEntry: {
        badgeText: 'MISSED',
        badgeClass: 'bg-yellow-500 text-white border-yellow-500 font-bold shadow-md',
        borderClass: 'border-l-yellow-500 border-l-4',
        cardBgClass: 'bg-yellow-50 dark:bg-yellow-900/40 border-yellow-400 dark:border-yellow-600',
        titleClass: 'text-yellow-700 dark:text-yellow-300',
        markerLabel: 'ENTRY',
        markerPosition: 'belowBar',
        markerShape: 'arrowUp',
        markerColor: '#f59e0b',
        statusClass: 'warning',
    },
    waiting: {
        badgeText: 'WAIT',
        badgeClass: 'bg-slate-200 text-slate-600 border-slate-300',
        borderClass: 'border-l-slate-300 border-l-4',
        cardBgClass: 'bg-[var(--monitor-card)] border-[var(--monitor-border)]',
        titleClass: 'text-[var(--monitor-text)]',
        markerLabel: 'WAIT',
        markerPosition: 'belowBar',
        markerShape: 'arrowUp',
        markerColor: '#2dd4bf',
        statusClass: 'warning',
    },
};

const asStatus = (rawStatus: unknown): string => String(rawStatus || '').trim().toUpperCase();
const normalizeTimeframe = (timeframe: string | null | undefined): string => String(timeframe || '').trim().toLowerCase();

const toMsByTimeframe = (timeframe: string | null | undefined): number => {
    return TIMEFRAME_TO_MS[normalizeTimeframe(timeframe) || '1d'] ?? TIMEFRAME_TO_MS['1d'];
};

const isStale = (referenceTime: string | null | undefined, timeframe: string | undefined): boolean => {
    if (!referenceTime) return true;
    const candleTime = Date.parse(referenceTime);
    if (Number.isNaN(candleTime)) return true;

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
    const uncertainty = isStale(opportunity.indicator_values_candle_time, opportunity.timeframe);
    const selectedTimeframe = normalizeTimeframe(context.selectedTimeframe);
    const strategyTimeframe = normalizeTimeframe(opportunity.timeframe);
    const timeframeMismatch = Boolean(selectedTimeframe) && selectedTimeframe !== strategyTimeframe;
    const candleMismatch = Boolean(context.requireCurrentCandleMatch) && !hasSameCandleReference(
        opportunity.indicator_values_candle_time,
        context.latestCandleTime,
    );

    let section: MonitorSignalKind = 'waiting';
    let isUncertain = uncertainty || timeframeMismatch || candleMismatch;
    const reasons: string[] = [];
    if (uncertainty) {
        reasons.push('Sem candle válido/atual para esta resolução.');
    }
    if (timeframeMismatch) {
        reasons.push('EXIT bloqueado: timeframe da estratégia não corresponde ao timeframe exibido.');
    }
    if (candleMismatch) {
        reasons.push('EXIT bloqueado: candle de referência não corresponde ao último candle exibido.');
    }

    if (rawStatus === 'HOLDING' || rawStatus === 'EXIT_NEAR' || rawStatus === 'EXIT_SIGNAL') {
        section = isHolding ? 'holding' : 'waiting';
        if (!isHolding) {
            isUncertain = true;
            reasons.push('Status indica saída em preparo com posição fechada.');
        }
    } else if (rawStatus === 'EXITED') {
        if (!isHolding) {
            section = 'exited';
        } else {
            section = 'waiting';
            isUncertain = true;
            reasons.push('Status de saída inconsistente com posição aberta.');
        }
    } else if (rawStatus === 'STOPPED_OUT') {
        section = 'stoppedOut';
    } else if (rawStatus === 'MISSED_ENTRY' || rawStatus === 'MISSED') {
        section = 'missedEntry';
    } else if (rawStatus === 'WAIT' || rawStatus === 'NEUTRAL' || rawStatus === 'BUY_NEAR' || rawStatus === 'BUY_SIGNAL') {
        section = 'waiting';
    } else if (rawStatus) {
        section = isHolding ? 'holding' : 'waiting';
        if (!isHolding) {
            isUncertain = true;
            reasons.push('Status desconhecido, tratado como estado de espera.');
        }
    }

    const visual = VISUAL_BY_KIND[section];
    const effectiveSection = isUncertain ? 'waiting' : section;
    const sectionVisual = VISUAL_BY_KIND[effectiveSection];
    const freshnessReason = reasons.length > 0 ? reasons.join(' ') : null;
    const fallbackStatusMessage = isUncertain
        ? 'SINAL INCONCLUSIVO: estado não confirmado.'
        : (opportunity.message || `Waiting for ${opportunity.next_status_label} signal`);

    return {
        section: effectiveSection,
        isUncertain,
        statusMessage: fallbackStatusMessage,
        freshnessReason,
        strategyTimeframe: strategyTimeframe || null,
        displayTimeframe: selectedTimeframe || strategyTimeframe || null,
        referenceCandleTime: opportunity.indicator_values_candle_time ?? null,
        latestCandleTime: context.latestCandleTime ?? null,
        visual: {
            ...sectionVisual,
            markerLabel: isUncertain
                ? sectionVisual.markerLabel
                : section === 'holding'
                    ? sectionVisual.markerLabel
                    : (rawStatus === 'EXIT_SIGNAL' || rawStatus === 'EXIT_NEAR' ? 'EXIT' : sectionVisual.markerLabel),
            markerColor: isUncertain ? '#8b949e' : sectionVisual.markerColor,
            markerShape: isUncertain ? 'arrowUp' : sectionVisual.markerShape,
            markerPosition: isUncertain ? 'belowBar' : sectionVisual.markerPosition,
        },
    };
};
