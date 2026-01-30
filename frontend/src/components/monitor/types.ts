export interface Opportunity {
    id: number;
    symbol: string;
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
}
