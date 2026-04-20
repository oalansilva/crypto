export type MonitorAssetType = 'crypto' | 'stock';

export interface OpportunitySignalHistoryItem {
    timestamp: string;
    signal: 1 | -1;
    type: 'entry' | 'exit';
    reason?: string | null;
    price?: number | null;
}

export interface Opportunity {
    id: number;
    symbol: string;
    asset_type?: string | null;
    timeframe: string;
    template_name: string;
    name: string;
    notes?: string;
    tier?: number | null;  // 1=Core, 2=Complementares, 3=Outros
    parameters?: Record<string, unknown>;  // Parâmetros da estratégia (ema_short, sma_long, stop_loss, etc.)
    // Simplified model
    is_holding: boolean;
    distance_to_next_status: number | null;
    next_status_label: 'entry' | 'exit' | 're-entry' | 'confirmation';
    // Legacy fields (for backward compatibility)
    status?: string;
    badge?: string;
    message?: string;
    last_price: number;
    timestamp: string;
    details?: any;
    /** Valores dos indicadores usados no cálculo da distância (último candle fechado) */
    indicator_values?: Record<string, number>;
    /** Data/hora do candle usado (ISO) para conferir com TradingView */
    indicator_values_candle_time?: string | null;
    /** Histórico recente de sinais confirmados da estratégia */
    signal_history?: OpportunitySignalHistoryItem[];

    /** Optional risk info */
    entry_price?: number | null;
    stop_price?: number | null;
    distance_to_stop_pct?: number | null;
}

export type MonitorCardMode = 'price' | 'strategy';
export type MonitorPriceTimeframe = '15m' | '1h' | '4h' | '1d';

export type MonitorTheme = 'dark-green' | 'black';

export interface MonitorPreference {
    in_portfolio: boolean;
    card_mode: MonitorCardMode;
    price_timeframe: MonitorPriceTimeframe;
    theme?: MonitorTheme;
}

const normalizeMonitorAssetType = (assetType: string | null | undefined): MonitorAssetType | null => {
    const normalized = String(assetType || '').trim().toLowerCase();
    if (normalized === 'crypto' || normalized === 'cryptomoeda' || normalized === 'criptomoeda') {
        return 'crypto';
    }
    if (normalized === 'stock' || normalized === 'stocks' || normalized === 'acao' || normalized === 'acoes') {
        return 'stock';
    }
    return null;
};

export const getOpportunityAssetType = (opportunity: Pick<Opportunity, 'asset_type' | 'symbol'>): MonitorAssetType => {
    const explicitType = normalizeMonitorAssetType(opportunity.asset_type);
    if (explicitType) {
        return explicitType;
    }
    return String(opportunity.symbol || '').includes('/') ? 'crypto' : 'stock';
};

export const getOpportunityBaseAsset = (opportunity: Pick<Opportunity, 'symbol'> | string): string => {
    const rawSymbol = typeof opportunity === 'string' ? opportunity : opportunity.symbol;
    const normalized = String(rawSymbol || '').trim().toUpperCase();
    if (!normalized) {
        return '';
    }
    return normalized.split('/')[0]?.trim() || normalized;
};

export const isDerivedPortfolioRuleActive = (
    opportunity: Pick<Opportunity, 'asset_type' | 'symbol'>,
    binanceConfigured: boolean,
): boolean => {
    return binanceConfigured && getOpportunityAssetType(opportunity) === 'crypto';
};
