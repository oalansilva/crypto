import type { MarketState, Opportunity, OpportunityConfiguration } from './types';

/**
 * Card #1122: identidade de configuração, estado do mercado e atraso real das linhas do Monitor.
 * Horários em BRT, com NY entre parênteses para ação e ETF.
 */

export type MarketTone = 'open' | 'closed' | 'stale' | 'insufficient';

export interface MarketStateView {
    readonly tone: MarketTone;
    /** Texto curto da linha (sob a pílula de Status). */
    readonly short: string;
    /** Texto completo (cartão, `title` da linha). */
    readonly full: string;
    /** "Sinal em espera" / "Sem sinal" (curto na linha, completo no cartão). */
    readonly holdShort: string | null;
    readonly holdFull: string | null;
}

const BRT = 'America/Sao_Paulo';
const NY = 'America/New_York';
const WEEKDAYS = ['dom.', 'seg.', 'ter.', 'qua.', 'qui.', 'sex.', 'sáb.'];
const MONTHS = ['jan.', 'fev.', 'mar.', 'abr.', 'mai.', 'jun.', 'jul.', 'ago.', 'set.', 'out.', 'nov.', 'dez.'];
const CLASS_LABEL: Record<string, string> = { crypto: 'Cripto', stock: 'Ação', etf: 'ETF' };

export const LEGACY_UNAVAILABLE_REASON = 'Fonte antiga: gráfico e trades depois da migração para a Binance.';

export const getAssetClass = (opportunity: Pick<Opportunity, 'asset_class' | 'symbol'>): 'crypto' | 'stock' | 'etf' => {
    const raw = String(opportunity.asset_class || '').trim().toLowerCase();
    if (raw === 'crypto' || raw === 'stock' || raw === 'etf') return raw;
    return String(opportunity.symbol || '').includes('/') ? 'crypto' : 'stock';
};

export const isEquityOpportunity = (opportunity: Pick<Opportunity, 'asset_class' | 'symbol'>): boolean => (
    getAssetClass(opportunity) !== 'crypto'
);

export const getConfiguration = (opportunity: Pick<Opportunity, 'configuration'>): OpportunityConfiguration | null => (
    opportunity.configuration && typeof opportunity.configuration === 'object' ? opportunity.configuration : null
);

/** Favorito da fonte antiga (Stooq): gráfico e trades indisponíveis até a migração (#1126). */
export const isLegacySource = (opportunity: Pick<Opportunity, 'configuration' | 'parameters'>): boolean => {
    const source = getConfiguration(opportunity)?.data_source ?? opportunity.parameters?.data_source;
    return String(source || '').toLowerCase() === 'stooq';
};

/** Chave estável das linhas (dois NVDA de fontes diferentes não colidem). */
export const opportunityRowKey = (
    opportunity: Pick<Opportunity, 'symbol' | 'asset_class' | 'configuration' | 'parameters'>,
): string => {
    const base = String(opportunity.symbol || '').replace(/[^a-zA-Z0-9]+/g, '-').toLowerCase();
    return isEquityOpportunity(opportunity) && isLegacySource(opportunity) ? `${base}-legacy` : base;
};

/** "Ação · USD · Binance · NY · split" (fonte antiga: "Ação · USD · Stooq · antiga · diário"). */
export const assetIdentityShort = (opportunity: Opportunity): string | null => {
    if (!isEquityOpportunity(opportunity)) return null;
    const configuration = getConfiguration(opportunity);
    const label = configuration?.label_compact || configuration?.label_short || 'Binance · NY · split';
    return `${CLASS_LABEL[getAssetClass(opportunity)]} · ${opportunity.currency || 'USD'} · ${label}`;
};

/** "Ação · USD · Binance Ações · pregão regular de NY · ajustado por split". */
export const assetIdentityLong = (opportunity: Opportunity): string | null => {
    if (!isEquityOpportunity(opportunity)) return null;
    const configuration = getConfiguration(opportunity);
    const label = configuration?.label_long || configuration?.label_short || 'Binance Ações · pregão regular de NY · ajustado por split';
    return `${CLASS_LABEL[getAssetClass(opportunity)]} · ${opportunity.currency || 'USD'} · ${label}`;
};

const parts = (date: Date, timeZone: string) => {
    const formatter = new Intl.DateTimeFormat('en-US', {
        timeZone,
        year: 'numeric',
        month: 'numeric',
        day: 'numeric',
        weekday: 'short',
        hour: '2-digit',
        minute: '2-digit',
        hourCycle: 'h23',
    });
    const map: Record<string, string> = {};
    for (const part of formatter.formatToParts(date)) map[part.type] = part.value;
    const weekdayIndex = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].indexOf(map.weekday);
    return {
        year: Number(map.year),
        month: Number(map.month),
        day: Number(map.day),
        weekday: weekdayIndex,
        time: `${map.hour}:${map.minute}`,
    };
};

const parseDate = (value: string | null | undefined): Date | null => {
    if (!value) return null;
    const date = new Date(value);
    return Number.isNaN(date.getTime()) ? null : date;
};

const sameDay = (a: ReturnType<typeof parts>, b: ReturnType<typeof parts>): boolean => (
    a.year === b.year && a.month === b.month && a.day === b.day
);

/** Dia do pregão de um candle 1d (Binance: meia-noite de NY; Stooq: meia-noite UTC). */
const sessionDay = (value: string | null | undefined) => {
    const date = parseDate(value);
    if (!date) return null;
    return parts(new Date(date.getTime() + 12 * 60 * 60 * 1000), NY);
};

const dayShort = (day: ReturnType<typeof parts>): string => (
    `${WEEKDAYS[day.weekday]} ${String(day.day).padStart(2, '0')}/${String(day.month).padStart(2, '0')}`
);

const dayLong = (day: ReturnType<typeof parts>): string => (
    `${WEEKDAYS[day.weekday]}, ${day.day} ${MONTHS[day.month - 1]}`
);

const candleLabel = (value: string | null | undefined, timeframe: string, equity: boolean, long: boolean): string => {
    const tf = String(timeframe || '1d').toLowerCase();
    if (tf === '1d') {
        const day = equity ? sessionDay(value) : (() => {
            const date = parseDate(value);
            return date ? parts(date, 'UTC') : null;
        })();
        if (!day) return '-';
        return long ? dayLong(day) : dayShort(day);
    }
    const date = parseDate(value);
    if (!date) return '-';
    const local = parts(date, BRT);
    return `${long ? dayLong(local) : dayShort(local)} ${local.time}`;
};

const openingLabel = (nextOpen: string | null | undefined, now: Date, long: boolean): string => {
    const date = parseDate(nextOpen);
    if (!date) return long ? 'próxima abertura indisponível' : 'abertura indisponível';
    const brt = parts(date, BRT);
    const ny = parts(date, NY);
    const today = parts(now, BRT);
    const nyNote = long ? `(${ny.time} em NY)` : `(${ny.time} NY)`;
    if (sameDay(brt, today)) {
        return long ? `abre hoje, ${brt.time} ${nyNote}` : `abre hoje ${brt.time} ${nyNote}`;
    }
    return long
        ? `abre ${WEEKDAYS[brt.weekday]}, ${brt.day} ${MONTHS[brt.month - 1]}, ${brt.time} ${nyNote}`
        : `abre ${WEEKDAYS[brt.weekday]} ${brt.time} ${nyNote}`;
};

const closingLabel = (closesAt: string | null | undefined, long: boolean): string => {
    const date = parseDate(closesAt);
    if (!date) return '';
    const brt = parts(date, BRT);
    const ny = parts(date, NY);
    return long ? ` · fecha ${brt.time} (${ny.time} em NY)` : ` · fecha ${brt.time} (${ny.time} NY)`;
};

const CLOSED_REASON: Record<string, { short: string; long: string }> = {
    weekend: { short: ' · fim de semana', long: ' · fim de semana' },
    holiday: { short: ' · feriado em NY', long: ' · feriado em Nova York' },
    after_hours: { short: '', long: ' · fora do pregão' },
    pre_open: { short: '', long: ' · fora do pregão' },
};

/** Horário de um candle intradiário da série atrasada: só a hora quando é do dia (BRT) de agora. */
const intradayLabel = (value: string | null | undefined, now: Date, long: boolean): string | null => {
    const date = parseDate(value);
    if (!date) return null;
    const local = parts(date, BRT);
    if (sameDay(local, parts(now, BRT))) return local.time;
    return `${long ? dayLong(local) : dayShort(local)} ${local.time}`;
};

/**
 * Card #1122 (residual P2 da w3): a linha está em espera por causa de outro tempo gráfico do mesmo
 * ativo (`stale_detail`). O texto diz o tempo gráfico e os horários da série atrasada, nunca
 * "falta" de um candle do próprio tempo gráfico que já chegou.
 */
const otherTimeframeDelay = (
    opportunity: Opportunity,
    now: Date,
): { short: string; full: string } | null => {
    const state = opportunity.market_state;
    const detail = state?.stale_detail;
    const timeframe = String(detail?.timeframe || state?.stale_timeframe || '').trim().toLowerCase();
    const own = String(opportunity.timeframe || '').trim().toLowerCase();
    if (!detail || !timeframe || timeframe === own) return null;
    const equity = isEquityOpportunity(opportunity);
    const daily = timeframe === '1d';
    const expectedShort = daily
        ? candleLabel(detail.expected_candle, timeframe, equity, false)
        : intradayLabel(detail.expected_candle, now, false) ?? '-';
    const expectedLong = daily
        ? candleLabel(detail.expected_candle, timeframe, equity, true)
        : intradayLabel(detail.expected_candle, now, true) ?? '-';
    const last = daily
        ? candleLabel(detail.last_candle, timeframe, equity, true)
        : intradayLabel(detail.last_candle, now, true);
    return {
        short: `Dados atrasados no ${timeframe} · falta ${expectedShort}`,
        full: last && last !== '-'
            ? `Dados atrasados no ${timeframe} · último ${last}; esperado ${expectedLong}`
            : `Dados atrasados no ${timeframe} · nenhum candle recebido; esperado ${expectedLong}`,
    };
};

/**
 * Estado do mercado da linha, em quatro tons (ícone + texto, nunca só cor).
 * A cripto só mostra estado quando o servidor diz que o dado está atrasado.
 */
export const marketStateView = (opportunity: Opportunity, now: Date = new Date()): MarketStateView | null => {
    const state: MarketState | null | undefined = opportunity.market_state;
    if (!state || typeof state !== 'object') return null;
    const equity = isEquityOpportunity(opportunity);
    const tone = String(state.state || '') as MarketTone;
    if (tone === 'stale') {
        const other = otherTimeframeDelay(opportunity, now);
        if (other) {
            return {
                tone,
                short: other.short,
                full: other.full,
                holdShort: 'Sinal em espera',
                holdFull: 'Sinal em espera até o dado normalizar',
            };
        }
        const expected = candleLabel(state.expected_candle, opportunity.timeframe, equity, false);
        const last = candleLabel(state.last_candle, opportunity.timeframe, equity, true);
        const expectedLong = candleLabel(state.expected_candle, opportunity.timeframe, equity, true);
        return {
            tone,
            short: `Dados atrasados · falta ${expected}`,
            full: state.last_candle
                ? `Dados atrasados · último candle ${last}; esperado ${expectedLong}`
                : `Dados atrasados · nenhum candle recebido; esperado ${expectedLong}`,
            holdShort: 'Sinal em espera',
            holdFull: 'Sinal em espera até o dado normalizar',
        };
    }
    if (tone === 'insufficient') {
        const text = `Dados insuficientes · ${state.available ?? 0} de ${state.required ?? 0} candles`;
        return {
            tone,
            short: text,
            full: text,
            holdShort: 'Sem sinal',
            holdFull: 'Sem sinal até completar o histórico',
        };
    }
    if (!equity) return null;
    if (tone === 'open') {
        return {
            tone,
            short: `Aberto${closingLabel(state.closes_at, false)}`,
            full: `Pregão aberto${closingLabel(state.closes_at, true)}`,
            holdShort: null,
            holdFull: null,
        };
    }
    if (tone === 'closed') {
        const reason = CLOSED_REASON[String(state.reason || '')] ?? { short: '', long: '' };
        return {
            tone,
            short: `Fechado${reason.short} · ${openingLabel(state.next_open, now, false)}`,
            full: `Mercado fechado${reason.long} · ${openingLabel(state.next_open, now, true)}`,
            holdShort: null,
            holdFull: null,
        };
    }
    return null;
};

/** Dado da linha atrasado: pelo servidor quando há `market_state`; senão, a regra "3 períodos". */
export const isOpportunityDataStale = (
    opportunity: Pick<Opportunity, 'market_state' | 'indicator_values_candle_time' | 'timeframe'>,
    now: number = Date.now(),
): boolean => {
    if (opportunity.market_state && typeof opportunity.market_state === 'object') {
        return opportunity.market_state.state === 'stale';
    }
    const ref = opportunity.indicator_values_candle_time;
    if (!ref) return false;
    const ms = Date.parse(ref);
    if (Number.isNaN(ms)) return false;
    const unit: Record<string, number> = {
        '15m': 15 * 60 * 1000,
        '1h': 60 * 60 * 1000,
        '4h': 4 * 60 * 60 * 1000,
        '1d': 24 * 60 * 60 * 1000,
    };
    const tf = String(opportunity.timeframe || '1d').trim().toLowerCase();
    return now - ms > (unit[tf] ?? unit['1d']) * 3;
};

export const isInsufficientData = (opportunity: Pick<Opportunity, 'market_state'>): boolean => (
    opportunity.market_state?.state === 'insufficient'
);
