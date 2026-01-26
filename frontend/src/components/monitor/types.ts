export interface Opportunity {
    id: number;
    symbol: string;
    timeframe: string;
    template_name: string;
    name: string;
    status: 'SIGNAL' | 'NEAR' | 'NEUTRAL' | 'ERROR';
    badge: 'success' | 'warning' | 'neutral' | 'destructive';
    message: string;
    last_price: number;
    timestamp: string;
    details: any;
}
