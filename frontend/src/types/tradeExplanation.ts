export type TradeExplanationStatus = 'available' | 'partial' | 'unavailable' | 'inconsistent'

export interface TradeEvidenceItem {
    key: string
    label: string
    value?: string | number | null
    timestamp_utc?: string | null
    state?: 'confirmed' | 'pending' | 'reference' | string | null
}

export interface TradeExplanation {
    status: TradeExplanationStatus
    direction?: 'long' | 'short' | string | null
    timeframe?: string | null
    action?: string | null
    trigger?: 'entry_rule' | 'exit_rule' | 'stop_loss' | 'take_profit' | 'open_position' | string | null
    summary?: string | null
    rule_summary?: string | null
    risk_summary?: string | null
    decision_candle_time?: string | null
    execution_time?: string | null
    execution_price?: number | null
    evidence?: TradeEvidenceItem[] | null
    unavailable_reason?: string | null
}
