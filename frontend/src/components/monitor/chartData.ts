import type { MarketCandle } from './MiniCandlesChart';
import { apiUrl } from '@/lib/apiBase';
import { authFetch } from '@/lib/authFetch';

export type ChartTimeframe = '1d';

export const CHART_TIMEFRAMES: ChartTimeframe[] = ['1d'];

export function toChartTimeframe(value?: string | null): ChartTimeframe {
    void value;
    return '1d';
}

export async function fetchMarketCandles(
    symbol: string,
    timeframe: ChartTimeframe,
    signal?: AbortSignal,
    limit = 300,
): Promise<MarketCandle[]> {
    const url = apiUrl('/market/candles');
    url.searchParams.set('symbol', symbol);
    url.searchParams.set('timeframe', timeframe);
    url.searchParams.set('limit', String(limit));

    const response = await authFetch(url.toString(), { signal });
    const payload = await response.json();
    if (!response.ok) {
        throw new Error(String(payload?.detail || `Falha ao carregar candles (${response.status})`));
    }

    return Array.isArray(payload?.candles) ? payload.candles : [];
}
