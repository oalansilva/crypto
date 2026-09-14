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
