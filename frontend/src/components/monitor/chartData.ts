import type { MarketCandle } from './MiniCandlesChart';
import { apiUrl } from '@/lib/apiBase';
import { authFetch } from '@/lib/authFetch';

export type ChartTimeframe = '15m' | '1h' | '4h' | '1d';

export const CHART_TIMEFRAMES: ChartTimeframe[] = ['15m', '1h', '4h', '1d'];

const SUPPORTED_CHART_TIMEFRAMES = new Set<ChartTimeframe>(CHART_TIMEFRAMES);

export function toChartTimeframe(value?: string | null): ChartTimeframe {
    const normalized = String(value || '').trim().toLowerCase();
    if (SUPPORTED_CHART_TIMEFRAMES.has(normalized as ChartTimeframe)) {
        return normalized as ChartTimeframe;
    }
    return '1d';
}

export async function fetchMarketCandles(
    symbol: string,
    timeframe: ChartTimeframe,
    signal?: AbortSignal,
    limit = 300,
    fullHistory = false,
): Promise<MarketCandle[]> {
    const url = apiUrl('/market/candles');
    url.searchParams.set('symbol', symbol);
    url.searchParams.set('timeframe', timeframe);
    url.searchParams.set('limit', String(limit));
    if (fullHistory) {
        url.searchParams.set('full_history', 'true');
    }

    const response = await authFetch(url.toString(), { signal });
    const payload = await response.json();
    if (!response.ok) {
        throw new Error(String(payload?.detail || `Falha ao carregar candles (${response.status})`));
    }

    return Array.isArray(payload?.candles) ? payload.candles : [];
}

/**
 * Card #1122: série de ação/ETF da Binance pelo histórico (`/api/market/history`), no tempo do
 * favorito. A cripto segue em `/api/market/candles`.
 */
export async function fetchEquityHistoryCandles(
    symbol: string,
    timeframe: ChartTimeframe,
    signal?: AbortSignal,
    limit = 300,
): Promise<MarketCandle[]> {
    const url = apiUrl('/market/history');
    url.searchParams.set('symbol', symbol);
    url.searchParams.set('timeframe', timeframe);
    url.searchParams.set('limit', String(limit));

    const response = await authFetch(url.toString(), { signal });
    const payload = await response.json();
    if (!response.ok) {
        const detail = payload?.detail;
        const message = typeof detail === 'string' ? detail : detail?.message;
        throw new Error(String(message || `Falha ao carregar candles (${response.status})`));
    }
    return Array.isArray(payload?.candles) ? payload.candles : [];
}

export async function fetchOpportunityCandles(
    opportunity: { symbol: string; asset_class?: string | null },
    timeframe: ChartTimeframe,
    signal?: AbortSignal,
    limit = 300,
): Promise<MarketCandle[]> {
    const equity = !String(opportunity.symbol || '').includes('/')
        || ['stock', 'etf'].includes(String(opportunity.asset_class || '').toLowerCase());
    return equity
        ? fetchEquityHistoryCandles(opportunity.symbol, timeframe, signal, limit)
        : fetchMarketCandles(opportunity.symbol, timeframe, signal, limit);
}
