/**
 * API simulada da Descoberta multiclasse (card #1121), com os números do protótipo aprovado
 * (`frontend/public/prototypes/card-1121-descoberta-acoes-etfs/`). Usada pelo E2E funcional e pelo visual.
 */
import type { Page, Route } from '@playwright/test'
import { mockAssetCatalog } from './assetCatalogMock'

export const ADMIN_USER = {
  id: 'discovery-admin',
  email: 'alan@example.com',
  name: 'Alan Silva',
  isAdmin: true,
  mustChangePassword: false,
}

export const SWEEP_ID = 'c1121mix'

const TEMPLATES = [
  { name: 'multi_ma_crossover', display_name: 'Médias Móveis: Cruzamento', description: 'Cruzamento de médias móveis com filtro de tendência.', is_readonly: true },
  { name: 'ema_rsi', display_name: 'EMA + RSI', description: 'Combina média exponencial e RSI.', is_readonly: true },
]

const BY_CLASS = {
  crypto: { assets: 1, combinations: 1, currency: 'USDT' },
  stock: { assets: 1, combinations: 1, currency: 'USD' },
  etf: { assets: 1, combinations: 1, currency: 'USD' },
}

export const PREFLIGHT_MIXED = {
  axes: { templates: ['multi_ma_crossover'], symbols: ['BTC/USDT', 'NVDA', 'SPY'], timeframes: ['1d'], directions: ['long'] },
  raw_total: 3,
  exclusions: {},
  excluded_assets: [],
  excluded_count: 0,
  valid_total: 3,
  limits: { max_total: 1000 },
  errors: {},
  expires_at: '2026-10-26T13:00:00Z',
  snapshot_token: 'tok-1121',
  snapshot_hash: '1121aaaa1121aaaa1121aaaa1121aaaa1121aaaa1121aaaa1121aaaa1121aaaa',
  period_type: 'all',
  start_date: null,
  end_date: null,
  by_class: BY_CLASS,
  asset_classes: { 'BTC/USDT': 'crypto', NVDA: 'stock', SPY: 'etf' },
  collection: {
    count: 1,
    of: 3,
    assets: [{ symbol: 'SPY', asset_class: 'etf', series: ['1d', '5m do intrabar'] }],
    stored: ['BTC/USDT', 'NVDA'],
  },
  precision_forecast: {
    daily: [
      { symbol: 'NVDA', timeframe: '1d', from: '2003-01-02', to: '2025-12-31', from_label: '2 jan. 2003', to_label: '31 dez. 2025', five_from: '2026-01-02', five_from_label: '2 jan. 2026' },
    ],
    no_candles: [],
    unknown: ['SPY'],
  },
  survivorship: { catalog_as_of: '2026-10-26T12:00:00Z', window: { start: '2003-01-02', start_label: '2 jan. 2003', end: null, end_label: null } },
}

export const PREFLIGHT_LIMIT = {
  ...PREFLIGHT_MIXED,
  axes: { ...PREFLIGHT_MIXED.axes, symbols: ['BTC/USDT', 'NVDA', 'SPY'] },
  raw_total: 2433,
  valid_total: 2433,
  by_class: {
    crypto: { assets: 1, combinations: 1, currency: 'USDT' },
    stock: { assets: 2431, combinations: 2431, currency: 'USD' },
    etf: { assets: 1, combinations: 1, currency: 'USD' },
  },
  errors: {
    total:
      '2.433 combinações válidas passam do limite de 1.000: 2.433 ativos (1 cripto · 2.431 ações · 1 ETF). Estreite a seleção: menos ativos, menos templates ou menos timeframes. Nenhuma varredura foi criada.',
  },
  collection: null,
  precision_forecast: null,
}

const DAILY_NVDA = {
  precision_requested: 'intrabar',
  precision_effective: 'candle',
  timeframe: '1d',
  intraday_reason: 'coverage',
  intraday_missing: [{ from: '2003-01-02', to: '2025-12-31' }],
  window: { covered: { start: '2003-01-02T05:00:00+00:00', end: '2026-10-23T04:00:00+00:00', candles: 5990 } },
}
const INTRABAR_BTC = {
  precision_requested: 'intrabar',
  precision_effective: 'intrabar_15m',
  timeframe: '1d',
  intraday_missing: [],
  window: { covered: { start: '2017-08-17T00:00:00+00:00', end: '2026-10-25T00:00:00+00:00', candles: 3357 } },
}
const EQUITY_CONVENTIONS = { fee: 0.001, adjusted_prices: true, calendar: { kind: 'nyse_regular_session', sessions_per_year: 252 } }
const CRYPTO_CONVENTIONS = { fee: 0.00075, calendar: { kind: '24x7' } }

function row(over: Record<string, unknown>) {
  return {
    sweep_id: SWEEP_ID,
    template_id: 'multi_ma_crossover',
    display_name: 'Médias Móveis: Cruzamento',
    description: 'Cruzamento de médias móveis com filtro de tendência.',
    timeframe: '1d',
    direction: 'long',
    parameters: { fast: 21, slow: 89 },
    benchmark_cagr: 0.12,
    delta_cagr_vs_bh: 6.3,
    profit_factor: 1.7,
    eligibility: 'eligible',
    eligibility_reason: null,
    dedup_state: 'unique',
    dedup_reference: null,
    candle_source: 'Binance Spot',
    candle_version: '1',
    expected_candles: 3357,
    observed_valid_candles: 3357,
    start_at: '2017-08-17T00:00:00Z',
    end_at: '2026-10-25T00:00:00Z',
    fees_slippage: { fees: 0.00075, slippage: 0.0002, fee_pct: 0.00075, slippage_pct: 0.0002 },
    sample: { state: 'kept', retain_until: '2026-11-25T00:00:00Z' },
    ...over,
  }
}

export const RESULTS = [
  row({
    rank: 1,
    result_id: 'RS-BTC1121A1',
    symbol: 'BTC/USDT',
    calmar_ratio: 2.14,
    cagr: 0.45,
    max_drawdown: 0.21,
    sharpe_ratio: 1.12,
    win_rate: 0.52,
    trades_count: 48,
    coverage: 0.97,
    total_return: 30,
    oos_verdict: { status: 'GO', reasons: [] },
    asset: { symbol: 'BTC/USDT', asset_class: 'crypto', currency: 'USDT' },
    execution: INTRABAR_BTC,
    conventions: CRYPTO_CONVENTIONS,
    provenance: { data_source: 'Binance Spot', asset_class: 'crypto', session: '24x7', adjustment: 'na', timeframe_origin: 'native' },
    snapshot_id: '3f9a0c21aa00bb11cc22dd33ee44ff55',
  }),
  row({
    rank: 2,
    result_id: 'RS-NVDA1121B2',
    symbol: 'NVDA',
    calmar_ratio: 1.08,
    cagr: 0.183,
    max_drawdown: 0.17,
    sharpe_ratio: 0.94,
    win_rate: 0.49,
    trades_count: 61,
    coverage: 1,
    total_return: 54,
    start_at: '2003-01-02T05:00:00Z',
    end_at: '2026-10-23T04:00:00Z',
    fees_slippage: { fees: 0.001, slippage: 0.0002, fee_pct: 0.001, slippage_pct: 0.0002 },
    oos_verdict: { status: 'GO', reasons: [] },
    asset: { symbol: 'NVDA', asset_class: 'stock', currency: 'USD' },
    execution: DAILY_NVDA,
    conventions: EQUITY_CONVENTIONS,
    provenance: { data_source: 'Binance Ações', asset_class: 'stock', session: 'rth', adjustment: 'adjusted', timeframe_origin: 'native' },
    snapshot_id: '8b41d7e2aa00bb11cc22dd33ee44ff55',
  }),
  row({
    rank: 3,
    result_id: 'RS-SPY1121C3',
    symbol: 'SPY',
    calmar_ratio: 0.42,
    cagr: 0.046,
    max_drawdown: 0.14,
    sharpe_ratio: 0.31,
    win_rate: 0.46,
    trades_count: 37,
    coverage: 1,
    total_return: 1.4,
    start_at: '2003-01-02T05:00:00Z',
    end_at: '2026-10-23T04:00:00Z',
    fees_slippage: { fees: 0.001, slippage: 0.0002, fee_pct: 0.001, slippage_pct: 0.0002 },
    oos_verdict: { status: 'NO-GO', reasons: ['Treino: Sharpe abaixo do mínimo.'] },
    asset: { symbol: 'SPY', asset_class: 'etf', currency: 'USD' },
    execution: DAILY_NVDA,
    conventions: EQUITY_CONVENTIONS,
    provenance: { data_source: 'Binance Ações', asset_class: 'etf', session: 'rth', adjustment: 'adjusted', timeframe_origin: 'native' },
    snapshot_id: 'c07e5a19aa00bb11cc22dd33ee44ff55',
  }),
]

const BTC_DONE = {
  symbol: 'BTC/USDT', asset_class: 'crypto', currency: 'USDT', done: 1, total: 1, state: 'done', max_attempts: 3,
  outcomes: { succeeded: 1, daily: 0, insufficient: 0, failed: 0, skipped: 0 },
  details: [{ timeframe: '1d', outcome: 'succeeded', precision: { kind: 'intrabar_15m', missing: [] }, period: { start_label: '17 ago. 2017', end_label: '25 out. 2026' } }],
}
const NVDA_DONE = {
  symbol: 'NVDA', asset_class: 'stock', currency: 'USD', done: 1, total: 1, state: 'done_daily', max_attempts: 3,
  outcomes: { succeeded: 1, daily: 1, insufficient: 0, failed: 0, skipped: 0 },
  details: [{ timeframe: '1d', outcome: 'succeeded', precision: { kind: 'daily', missing: [{ from: '2003-01-02', to: '2025-12-31' }] }, period: { start_label: '2 jan. 2003', end_label: '23 out. 2026' } }],
}
export const ASSETS_COLLECTING = [
  BTC_DONE,
  { symbol: 'NVDA', asset_class: 'stock', currency: 'USD', done: 0, total: 1, state: 'collecting', stage: '1d', series: '1d', role: 'candles', page: 3, pages: 6, attempt: 1, max_attempts: 3 },
  { symbol: 'SPY', asset_class: 'etf', currency: 'USD', done: 0, total: 1, state: 'queued', max_attempts: 3 },
]
export const ASSETS_FAILED = [
  BTC_DONE,
  NVDA_DONE,
  {
    symbol: 'SPY', asset_class: 'etf', currency: 'USD', done: 1, total: 1, state: 'failed', max_attempts: 3,
    reason: 'a Binance não respondeu ao histórico de SPY nas 3 tentativas',
    outcomes: { succeeded: 0, daily: 0, insufficient: 0, failed: 1, skipped: 0 },
    details: [{ timeframe: '1d', outcome: 'failed', reason: 'a Binance não respondeu ao histórico de SPY nas 3 tentativas' }],
  },
]
export const ASSETS_DONE = [
  BTC_DONE,
  NVDA_DONE,
  { ...NVDA_DONE, symbol: 'SPY', asset_class: 'etf' },
]

export interface DiscoveryMockState {
  preflight: Record<string, unknown>
  sweepState: string
  assets: Record<string, unknown>[]
  history: Array<Record<string, unknown>>
  active: boolean
  results: Record<string, unknown>[]
  promoted: string[]
}

const json = (route: Route, body: unknown, status = 200) =>
  route.fulfill({ status, contentType: 'application/json', body: JSON.stringify(body) })

export function sweepPayload(state: DiscoveryMockState) {
  const counts = { succeeded: 0, failed: 0, skipped: 0, insufficient_sample: 0 }
  for (const asset of state.assets as Array<{ outcomes?: Record<string, number> }>) {
    counts.succeeded += asset.outcomes?.succeeded ?? 0
    counts.failed += asset.outcomes?.failed ?? 0
    counts.skipped += asset.outcomes?.skipped ?? 0
    counts.insufficient_sample += asset.outcomes?.insufficient ?? 0
  }
  const processed = counts.succeeded + counts.failed + counts.skipped + counts.insufficient_sample
  return {
    sweep_id: SWEEP_ID,
    state: state.sweepState,
    total: 3,
    ...counts,
    processed,
    terminal_reason: null,
    terminal_code: null,
    draft_key: 'draft-1121',
    snapshot: PREFLIGHT_MIXED,
    updated_at: '2026-10-26T12:00:00Z',
    assets: state.assets,
  }
}

export async function installDiscoveryMulticlassMocks(page: Page, initial: Partial<DiscoveryMockState> = {}) {
  const state: DiscoveryMockState = {
    preflight: PREFLIGHT_MIXED,
    sweepState: 'running',
    assets: ASSETS_COLLECTING,
    history: [],
    active: false,
    results: RESULTS,
    promoted: [],
    ...initial,
  }
  await page.addInitScript((user) => {
    localStorage.setItem('auth_access_token', 'discovery-admin-token')
    localStorage.setItem('auth_refresh_token', 'discovery-admin-refresh')
    localStorage.setItem('auth_user', JSON.stringify(user))
    localStorage.setItem('cripto-farol-onboarding-dismissed', '1')
  }, ADMIN_USER)
  await page.route('**/api/**', (route) => json(route, {}))
  await page.route('**/api/auth/me', (route) => json(route, ADMIN_USER))
  await page.route('**/api/combos/templates', (route) => json(route, { prebuilt: TEMPLATES, examples: [], custom: [] }))
  await mockAssetCatalog(page)
  await page.route('**/api/combos/discovery/sweeps/preflight', (route) => json(route, state.preflight))
  await page.route('**/api/combos/discovery/sweeps/active', (route) =>
    json(route, { sweeps: state.active ? [sweepPayload(state)] : [] }),
  )
  await page.route('**/api/combos/discovery/sweeps/history', (route) => json(route, { sweeps: state.history }))
  await page.route('**/api/combos/discovery/sweeps', (route) => {
    if (route.request().method() !== 'POST') return route.fallback()
    state.active = true
    return json(route, { sweep_id: SWEEP_ID, state: 'running', total: 3, idempotency_key: 'draft-1121' }, 201)
  })
  await page.route(`**/api/combos/discovery/sweeps/${SWEEP_ID}`, (route) => json(route, sweepPayload(state)))
  await page.route(`**/api/combos/discovery/sweeps/${SWEEP_ID}/cancel`, (route) => {
    state.sweepState = 'cancelling'
    return json(route, { state: 'cancelling' })
  })
  await page.route('**/api/combos/discovery/sweeps/*/leaderboard?*', (route) => {
    const url = new URL(route.request().url())
    const cls = url.searchParams.get('asset_class')
    const exclude = url.searchParams.get('exclude_eligibility')
    const all = state.results.map((r) =>
      state.promoted.includes(String(r.result_id)) ? { ...r, dedup_state: 'already_promoted', dedup_reference: '901' } : r,
    ) as Array<Record<string, any>>
    const counts = { all: all.length, crypto: 0, stock: 0, etf: 0 } as Record<string, number>
    for (const r of all) counts[r.asset.asset_class] += 1
    const matched = all.filter(
      (r) => (!cls || r.asset.asset_class === cls) && (!exclude || r.eligibility !== exclude),
    )
    return json(route, {
      results: matched,
      total: matched.length,
      unfiltered_total: all.length,
      class_counts: counts,
      offset: 0,
      limit: 12,
    })
  })
  await page.route('**/api/combos/discovery/results/*/promote', (route) => {
    const id = route.request().url().split('/results/')[1].split('/')[0]
    state.promoted.push(id)
    return json(route, { favorite_id: '901', result_id: id }, 201)
  })
  return state
}

/** Seleção do card: 1 template, BTC/USDT, NVDA e SPY, 1d, Long, Todo o histórico. */
export async function buildMixedDraft(page: Page) {
  await page.getByTestId('inline-templates-search').fill('Médias')
  await page.locator('[role=group][aria-label="Templates (seleção inline)"] input[type=checkbox]').first().check()
  for (const symbol of ['BTC/USDT', 'NVDA', 'SPY']) {
    await page.getByTestId('asset-search').fill(symbol)
    await page.locator(`.ap-row[data-asset="${symbol}"] input`).check()
  }
  await page.getByTestId('sel-period').selectOption('all')
}
