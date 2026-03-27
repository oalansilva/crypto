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
}

export type SignalListResponse = {
  signals: Signal[]
  total: number
  cached_at: string | null
  is_stale: boolean
  available_assets: string[]
}

export type SignalFilterType = SignalType | 'ALL'
