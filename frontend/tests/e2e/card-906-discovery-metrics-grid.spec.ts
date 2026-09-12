import { expect, test, type Page } from '@playwright/test'

const ADMIN_USER = {
  id: 'discovery-admin',
  email: 'alan@example.com',
  name: 'Alan Silva',
  isAdmin: true,
  mustChangePassword: false,
}

const SNAPSHOT = {
  axes: {
    templates: ['multi_ma_crossover'],
    symbols: ['ALPHA/USDT', 'ARPA/USDT', 'ETH/USDT', 'ADA/USDT'],
    timeframes: ['1d'],
    directions: ['long'],
  },
  raw_total: 8,
  exclusions: {},
  excluded_count: 0,
  valid_total: 8,
  limits: { max_total: 1000 },
  errors: {},
  expires_at: '2026-09-12T13:00:00Z',
  snapshot_token: 'snapshot-token-906',
  snapshot_hash: '906abcdef906abcdef906abcdef906abcdef906abcdef906abcdef906abcdef',
  period_type: 'all',
  start_date: '2017-01-01',
  end_date: '2026-09-08',
}

const ACTIVE = {
  sweep_id: 'c906grid',
  state: 'running',
  total: 697,
  succeeded: 234,
  failed: 0,
  skipped: 0,
  insufficient_sample: 14,
  processed: 248,
  terminal_reason: null,
  terminal_code: null,
  draft_key: 'draft-906',
  snapshot: SNAPSHOT,
  updated_at: '2026-09-12T12:00:00Z',
}

const TEMPLATES = [
  {
    name: 'multi_ma_crossover',
    display_name: 'Médias Móveis: Tendência em Virada 1',
    description: 'Compara médias de velocidades diferentes.',
    is_readonly: true,
  },
]

function row(partial: Record<string, unknown>) {
  return {
    template_id: 'multi_ma_crossover',
    display_name: 'Médias Móveis: Tendência em Virada 1',
    description: 'Compara médias de velocidades diferentes.',
    timeframe: '1d',
    direction: 'long',
    parameters: { ema_short: 8 },
    benchmark_cagr: 0.084,
    delta_cagr_vs_bh: 9.4,
    profit_factor: 1.12,
    eligibility_reason: null,
    dedup_state: 'unique',
    dedup_reference: null,
    start_at: '2020-10-09T00:00:00Z',
    end_at: '2024-01-31T00:00:00Z',
    candle_source: 'ccxt',
    candle_version: null,
    expected_candles: 1209,
    observed_valid_candles: 1210,
    fees_slippage: { fees: 0.001, slippage: 0.001 },
    oos_verdict: { status: 'NO-GO' },
    ...partial,
  }
}

const PARTIAL_TOP5 = [
  row({
    rank: 1,
    result_id: 'RS-C22EB0B811',
    symbol: 'ALPHA/USDT',
    calmar_ratio: 22.53,
    max_drawdown: 0.165,
    trades_count: 30,
    coverage: 1,
    sharpe_ratio: 0.31,
    win_rate: 0.467,
    cagr: 0.178,
    eligibility: 'eligible',
  }),
  row({
    rank: 2,
    result_id: 'RS-906-02',
    symbol: 'ARPA/USDT',
    calmar_ratio: 19.03,
    max_drawdown: 0.085,
    trades_count: 30,
    coverage: 1,
    sharpe_ratio: 0.46,
    win_rate: 0.548,
    cagr: 0.162,
    eligibility: 'eligible',
  }),
  row({
    rank: 3,
    result_id: 'RS-906-03',
    symbol: 'CFX/USDT',
    calmar_ratio: 16.9,
    max_drawdown: 0.075,
    trades_count: 40,
    coverage: 1,
    sharpe_ratio: 0.52,
    win_rate: 0.512,
    cagr: 0.127,
    eligibility: 'eligible',
  }),
  row({
    rank: 4,
    result_id: 'RS-906-04',
    symbol: 'CRV/USDT',
    calmar_ratio: 13.78,
    max_drawdown: 0.075,
    trades_count: 46,
    coverage: 1,
    sharpe_ratio: 0.41,
    win_rate: 0.489,
    cagr: 0.103,
    eligibility: 'eligible',
  }),
  row({
    rank: 5,
    result_id: 'RS-906-ETH',
    symbol: 'ETH/USDT',
    calmar_ratio: 1.195e27,
    max_drawdown: 0.108,
    trades_count: 60,
    coverage: 1,
    sharpe_ratio: 0.88,
    win_rate: 0.491,
    cagr: 0.14,
    eligibility: 'eligible',
  }),
]

const LEADERBOARD = [
  ...PARTIAL_TOP5,
  row({
    rank: null,
    result_id: 'RS-906-INS',
    symbol: 'ADA/USDT',
    calmar_ratio: null,
    max_drawdown: null,
    trades_count: null,
    coverage: null,
    sharpe_ratio: null,
    win_rate: null,
    cagr: null,
    benchmark_cagr: null,
    delta_cagr_vs_bh: null,
    profit_factor: null,
    eligibility: 'insufficient_sample',
    eligibility_reason: 'treino 18 < mínimo 30',
    oos_verdict: null,
  }),
]

async function installMocks(page: Page) {
  await page.addInitScript((user) => {
    localStorage.setItem('auth_access_token', 'discovery-admin-token')
    localStorage.setItem('auth_refresh_token', 'discovery-admin-refresh')
    localStorage.setItem('auth_user', JSON.stringify(user))
    localStorage.setItem('cripto-farol-onboarding-dismissed', '1')
  }, ADMIN_USER)

  await page.route('**/api/**', (route) =>
    route.fulfill({ status: 200, contentType: 'application/json', body: '{}' }),
  )
  await page.route('**/api/auth/me', (route) =>
    route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(ADMIN_USER) }),
  )
  await page.route('**/api/combos/templates', (route) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ prebuilt: TEMPLATES, examples: [], custom: [] }),
    }),
  )
  await page.route('**/api/exchanges/binance/symbols', (route) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ symbols: SNAPSHOT.axes.symbols }),
    }),
  )
  await page.route('**/api/combos/discovery/sweeps/preflight', (route) =>
    route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(SNAPSHOT) }),
  )
  await page.route('**/api/combos/discovery/sweeps/active', (route) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ sweeps: [ACTIVE] }),
    }),
  )
  await page.route('**/api/combos/discovery/sweeps/history', (route) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ sweeps: [] }),
    }),
  )
  await page.route('**/api/combos/discovery/sweeps/c906grid', (route) =>
    route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(ACTIVE) }),
  )
  await page.route('**/api/combos/discovery/sweeps/*/leaderboard?*', (route) => {
    const url = new URL(route.request().url())
    const exclude = url.searchParams.get('exclude_eligibility')
    const offset = Number(url.searchParams.get('offset') || 0)
    const limit = Number(url.searchParams.get('limit') || 10)
    const matched = LEADERBOARD.filter((item) => item.eligibility !== exclude)
    return route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        results: matched.slice(offset, offset + limit),
        total: matched.length,
        unfiltered_total: LEADERBOARD.length,
        offset,
        limit,
      }),
    })
  })
}

const VIEWPORTS = [
  { name: 'desktop', width: 1440, height: 900 },
  { name: 'mobile', width: 390, height: 844 },
] as const

const METRIC_HEADERS = [
  'Sharpe',
  'Win rate (taxa de acerto)',
  'Retorno (CAGR) anualizado da varredura',
] as const

for (const viewport of VIEWPORTS) {
  test(`card 906 — ${viewport.name} seis colunas Acompanhar/Decidir vs proto`, async ({ page }) => {
    await page.setViewportSize({ width: viewport.width, height: viewport.height })
    await installMocks(page)
    await page.goto('/combo/discovery')

    await expect(page.getByRole('heading', { name: 'Descoberta de estratégias swing' })).toBeVisible()

    const partials = page.getByTestId('partials-table')
    await expect(partials).toBeVisible()
    for (const name of METRIC_HEADERS) {
      await expect(partials.getByRole('columnheader', { name })).toBeVisible()
    }
    await expect(partials.getByTestId('partial-sharpe-1')).toHaveText('0,31')
    await expect(partials.locator('tr').filter({ hasText: 'ETH/USDT' }).getByTestId('partial-sharpe-na-RS-906-ETH')).toHaveText('N/A')

    await page.getByRole('tab', { name: 'Montar' }).click()
    await expect(page.getByRole('heading', { name: 'Preflight' })).toBeVisible()
    await expect(partials).toBeHidden()

    await page.getByRole('tab', { name: 'Decidir' }).click()
    const decidir = page.getByTestId('decidir-table')
    await expect(decidir).toBeVisible()
    for (const name of METRIC_HEADERS) {
      await expect(decidir.getByRole('columnheader', { name })).toBeVisible()
    }

    const sort = page.getByTestId('sort-filter')
    await expect(sort.locator('option')).toHaveText(['Calmar', 'CAGR vs B&H'])
    await expect(sort.locator('option')).toHaveCount(2)

    const insufficient = page.getByTestId('row-insufficient')
    await expect(insufficient).toBeVisible()
    await expect(insufficient.getByTestId('decidir-sharpe-na-RS-906-INS')).toHaveText('N/A')
    await expect(insufficient.getByTestId('decidir-win-na-RS-906-INS')).toHaveText('N/A')
    await expect(insufficient.getByTestId('decidir-cagr-na-RS-906-INS')).toHaveText('N/A')
    await expect(insufficient.locator('td.na')).toHaveCount(6)
    await expect(insufficient.getByRole('button', { name: 'Promover' })).toHaveCount(0)

    await page.getByTestId('expand-RS-C22EB0B811').click()
    const details = page.getByTestId('details-RS-C22EB0B811')
    await expect(details).toContainText('B&H')
    await expect(details).toContainText('PF')
    await expect(details).toContainText('janela')
    await expect(details).not.toContainText('Sharpe')
    await expect(details).not.toContainText('Win ')

    await expect(page.getByTestId('column-copy')).toContainText('CAGR na grelha')
    await expect(page.getByText('+47.916%')).toHaveCount(0)
  })
}
