import type { MarketCandle } from './MiniCandlesChart';
import type { MonitorPriceTimeframe } from './types';
import { apiUrl } from '@/lib/apiBase';

export type ChartTimeframe = Exclude<MonitorPriceTimeframe, '15m'>;

export const CHART_TIMEFRAMES: ChartTimeframe[] = ['1h', '4h', '1d'];

export function toChartTimeframe(value?: string | null): ChartTimeframe {
    if (value === '4h' || value === '1d') {
        return value;
    }
    return '1h';
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

    const response = await fetch(url.toString(), { signal });
    const payload = await response.json();
    if (!response.ok) {
        throw new Error(String(payload?.detail || `Failed to load candles (${response.status})`));
    }

    return Array.isArray(payload?.candles) ? payload.candles : [];
}
