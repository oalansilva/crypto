export type SignalType = 'BUY' | 'SELL' | 'HOLD'
export type RiskProfile = 'conservative' | 'moderate' | 'aggressive'

export type SignalIndicators = {
  RSI: number
  MACD: string
  BollingerBands: {
    upper: number
    middle: number
    lower: number
  }
}

export type Signal = {
  id: string
  asset: string
  type: SignalType
  confidence: number
  target_price: number
  stop_loss: number
  indicators: SignalIndicators
  created_at: string
  risk_profile: RiskProfile
  entry_price?: number | null
  current_price?: number | null
  pnl_percent?: number | null
  is_open_position?: boolean
}

export type SignalListResponse = {
  signals: Signal[]
  total: number
  cached_at: string | null
  is_stale: boolean
  available_assets: string[]
}

export type SignalFilterType = SignalType | 'ALL'

// --- Signal History types ---
export type SignalHistoryStatus = 'ativo' | 'disparado' | 'expirado' | 'cancelado'

export type SignalHistoryItem = {
  id: string
  asset: string
  type: SignalType
  confidence: number
  target_price: number
  stop_loss: number
  indicators: SignalIndicators | null
  created_at: string
  risk_profile: RiskProfile
  status: SignalHistoryStatus
  entry_price: number | null
  exit_price: number | null
  quantity: number | null
  pnl: number | null
  trigger_price: number | null
  updated_at: string | null
}

export type SignalHistoryResponse = {
  signals: SignalHistoryItem[]
  total: number
  limit: number
  offset: number
}

export type SignalStats = {
  total_signals: number
  win_rate: number
  avg_confidence: number
  expired_rate: number
  total_pnl: number
}
