export interface Opportunity {
    id: number;
    symbol: string;
    timeframe: string;
    template_name: string;
    name: string;
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
