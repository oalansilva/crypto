/** Coberturas de demonstração do card #1118 (as do protótipo aprovado, 22 out. 2026). */
import {
  EQUITY_NOTE,
  covered,
  defaultCatalog,
  tf,
  type MockAsset,
  type MockHistory,
} from './assetCatalogMock'

// --- Catálogo do protótipo (coberturas de 22 out. 2026) ---------------------------------------------

const UPDATED = '2026-10-22T21:12:00Z' // 18:12 em Brasília
const NY = 'America/New_York'

function equity(timeframes: ReturnType<typeof tf>[], extra: Partial<MockHistory> = {}): MockHistory {
  return covered(timeframes, { note: EQUITY_NOTE, calendar_timezone: NY, updated_at: UPDATED, ...extra })
}

export const NVDA = equity([
  tf('1d', '2014-11-11T05:00:00Z', '2026-10-22T04:00:00Z', { updated_at: UPDATED }),
  tf('5m', '2026-05-19T13:30:00Z', '2026-10-22T19:55:00Z', { updated_at: UPDATED }),
  tf('15m', '2026-05-19T13:30:00Z', '2026-10-22T19:45:00Z', { updated_at: UPDATED, origin: 'derived', derived_from: '5m' }),
])

export const SPY = equity([
  tf('1d', '2014-11-11T05:00:00Z', '2026-10-22T04:00:00Z', { updated_at: UPDATED }),
  tf('5m', '2026-07-01T13:30:00Z', '2026-10-22T19:55:00Z', {
    updated_at: UPDATED,
    gap_count: 1,
    gaps: [{ start: '2026-10-14T14:05:00Z', end: '2026-10-14T14:40:00Z', count: 8 }],
  }),
  tf('15m', '2026-07-01T13:30:00Z', '2026-10-22T19:45:00Z', {
    updated_at: UPDATED,
    origin: 'derived',
    derived_from: '5m',
    gap_count: 0,
    gaps: [
      { start: '2026-10-14T14:00:00Z', end: '2026-10-14T14:30:00Z', block_end: '2026-10-14T14:45:00Z', count: 4, inherited_from: '5m' },
    ],
  }),
])
// O resumo conta só as lacunas nativas (a do 15m é herdada do 5m).
SPY.gap_count = 1

export const QQQ_COLLECTING: MockHistory = {
  status: 'collecting',
  from: '2023-01-05T05:00:00Z',
  to: '2026-10-22T04:00:00Z',
  updated_at: UPDATED,
  gap_count: 0,
  note: EQUITY_NOTE,
  calendar_timezone: NY,
  collecting: { timeframe: '1d', page: 2, requested_at: '2026-10-22T21:06:00Z' },
  timeframes: [tf('1d', '2023-01-05T05:00:00Z', '2026-10-22T04:00:00Z', { updated_at: '2026-10-22T21:06:00Z', state: 'collecting' })],
}

export const VOO_FAILED: MockHistory = {
  status: 'failed',
  from: '2023-01-05T05:00:00Z',
  to: '2026-10-22T04:00:00Z',
  updated_at: '2026-10-22T21:06:00Z',
  gap_count: 0,
  note: EQUITY_NOTE,
  calendar_timezone: NY,
  error: { timeframe: '1d', code: 'binance_rate_limited', message: 'limite de requisições da Binance', at: '2026-10-22T21:06:00Z' },
  timeframes: [
    tf('1d', '2023-01-05T05:00:00Z', '2026-10-22T04:00:00Z', { updated_at: '2026-10-22T21:06:00Z', state: 'failed', incomplete: true }),
  ],
}

export const IBIT_PARTIAL: MockHistory = {
  status: 'partial',
  from: '2024-01-11T05:00:00Z',
  to: '2026-10-21T04:00:00Z',
  updated_at: '2026-10-21T13:30:00Z',
  gap_count: 0,
  note: EQUITY_NOTE,
  calendar_timezone: NY,
  partial: { timeframe: '1d', requested_since: '2021-10-22T04:00:00Z', starts_at: '2024-01-11T05:00:00Z', insufficient: true },
  timeframes: [
    tf('1d', '2024-01-11T05:00:00Z', '2026-10-21T04:00:00Z', {
      updated_at: '2026-10-21T13:30:00Z',
      insufficient: true,
      requested_since: '2021-10-22T04:00:00Z',
      starts_at: '2024-01-11T05:00:00Z',
    }),
  ],
}

export const WAVES_FROZEN: MockHistory = {
  ...covered([tf('1d', '2018-01-01T00:00:00Z', '2024-05-31T00:00:00Z', { updated_at: '2024-05-31T21:00:00Z' })]),
  status: 'frozen',
  updated_at: '2024-05-31T21:00:00Z',
}

export function coverageCatalog(): MockAsset[] {
  const base = defaultCatalog().map((asset) => ({ ...asset }))
  const byId = new Map(base.map((a) => [a.symbol, a]))
  byId.get('NVDA')!.history = NVDA
  byId.get('SPY')!.history = SPY
  byId.get('QQQ')!.history = QQQ_COLLECTING
  byId.get('WAVES/USDT')!.history = WAVES_FROZEN
  const extra = (symbol: string, name: string, history: MockHistory): MockAsset => ({
    ...byId.get('QQQ')!,
    asset_id: `binance:equity:EQ_${symbol}`,
    symbol,
    name,
    history,
  })
  return [...base, extra('VOO', 'Vanguard S&P 500 ETF', VOO_FAILED), extra('IBIT', 'iShares Bitcoin Trust ETF', IBIT_PARTIAL)]
}

