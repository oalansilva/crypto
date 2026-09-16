import { expect, test, type Page } from '@playwright/test'

const ADMIN_USER = {
  id: 'discovery-admin',
  email: 'alan@example.com',
  name: 'Alan Silva',
  isAdmin: true,
  mustChangePassword: false,
}

const SWEEP_ID = 'af8fb5dee323462c98baa5c492f0fbfb'

const SNAPSHOT = {
  axes: {
    templates: ['multi_ma_crossover'],
    symbols: ['BTC/USDT', 'DOT/USDT', 'SOL/USDT'],
    timeframes: ['1d'],
    directions: ['long'],
  },
  raw_total: 3,
  exclusions: {},
  excluded_count: 0,
  valid_total: 3,
  limits: { max_total: 1000 },
  errors: {},
  expires_at: '2026-09-15T13:00:00Z',
  snapshot_token: 'snapshot-token-948',
  snapshot_hash: '948abcdef948abcdef948abcdef948abcdef948abcdef948abcdef948abcdef',
  period_type: 'all',
  start_date: '2017-01-01',
  end_date: '2026-09-08',
}

const RUNNING = {
  sweep_id: SWEEP_ID,
  state: 'running',
  total: 3,
  succeeded: 2,
  failed: 0,
  skipped: 0,
  insufficient_sample: 0,
  processed: 2,
  terminal_reason: null,
  terminal_code: null,
  draft_key: 'draft-948',
  snapshot: SNAPSHOT,
  updated_at: '2026-09-15T12:00:00Z',
}

const TEMPLATES = [
  {
    name: 'multi_ma_crossover',
    display_name: 'Médias Móveis: Tendência em Virada 1',
    description: 'Cruzamento de médias para swing.',
    is_readonly: true,
  },
]

function row(partial: Record<string, unknown>) {
  return {
    template_id: 'multi_ma_crossover',
    display_name: 'Médias Móveis: Tendência em Virada 1',
    description: 'Cruzamento de médias para swing.',
    timeframe: '1d',
    direction: 'long',
    parameters: { ema_short: 8 },
    cagr: 0.041,
    benchmark_cagr: null,
    delta_cagr_vs_bh: null,
    sharpe_ratio: 0.42,
    profit_factor: 1.1,
    win_rate: 0.48,
    coverage: 1,
    eligibility: 'eligible',
    eligibility_reason: null,
    start_at: '2017-01-01T00:00:00Z',
    end_at: '2026-09-08T00:00:00Z',
    candle_source: 'ccxt',
    candle_version: null,
    expected_candles: 3500,
    observed_valid_candles: 3400,
    fees_slippage: { fees: 0.001, slippage: 0.0005 },
    oos_verdict: { status: 'GO', reasons: [] },
    ...partial,
  }
}

const LEADERBOARD = [
  row({
    rank: 1,
    result_id: 'RS-E2FF8F9FEB',
    symbol: 'BTC/USDT',
    calmar_ratio: 0.19,
    max_drawdown: 0.141,
    trades_count: 84,
    dedup_state: 'unique',
    dedup_reference: null,
  }),
  row({
    rank: 2,
    result_id: 'RS-EA2A508DBD',
    symbol: 'DOT/USDT',
    calmar_ratio: 0.17,
    max_drawdown: 0.12,
    trades_count: 55,
    dedup_state: 'unique',
    dedup_reference: null,
  }),
  row({
    rank: 3,
    result_id: 'RS-LIVE-948',
    symbol: 'SOL/USDT',
    calmar_ratio: 0.15,
    max_drawdown: 0.1,
    trades_count: 40,
    dedup_state: 'duplicate_favorite',
    dedup_reference: '12',
    oos_verdict: { status: 'NO-GO', reasons: ['Sharpe abaixo do limiar'] },
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
    route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ sweeps: [RUNNING] }) }),
  )
  await page.route('**/api/combos/discovery/sweeps/history', (route) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ sweeps: [] }),
    }),
  )
  await page.route(`**/api/combos/discovery/sweeps/${SWEEP_ID}`, (route) =>
    route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(RUNNING) }),
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

for (const viewport of VIEWPORTS) {
  test(`card 948 — ${viewport.name} órfãos Promover vs proto`, async ({ page }) => {
    await page.setViewportSize({ width: viewport.width, height: viewport.height })
    await installMocks(page)
    await Promise.all([
      page.waitForResponse((res) => res.url().includes('/leaderboard') && res.status() === 200, {
        timeout: 15000,
      }),
      page.goto('/combo/discovery'),
    ])

    await expect(page.getByRole('heading', { name: 'Descoberta de estratégias swing' })).toBeVisible()
    const partials = page.getByTestId('partials-table')
    await expect(partials).toBeVisible()
    await expect(partials.locator('tbody tr')).toHaveCount(3)
    const partialOrphan = partials.locator('tbody tr').filter({ hasText: 'BTC/USDT' })
    await expect(partialOrphan.getByRole('button', { name: 'Promover' })).toBeVisible()
    await expect(partials.locator('tbody tr').filter({ hasText: 'SOL/USDT' }).getByText('Equivale ao favorito ativo 12')).toBeVisible()

    await page.getByRole('tab', { name: 'Decidir' }).click()
    const decidir = page.getByTestId('decidir-table')
    await expect(decidir).toBeVisible()

    const orphanDup = decidir.locator('tbody tr').filter({ hasText: 'RS-E2FF8F9FEB' })
    await expect(orphanDup).toBeVisible()
    await expect(orphanDup.getByRole('button', { name: 'Promover' })).toBeVisible()
    await expect(orphanDup.getByText('Já existe')).toHaveCount(0)
    await expect(orphanDup.getByText(/Equivale ao favorito ativo/)).toHaveCount(0)

    const orphanPromoted = decidir.locator('tbody tr').filter({ hasText: 'RS-EA2A508DBD' })
    await expect(orphanPromoted.getByRole('button', { name: 'Promover' })).toBeVisible()
    await expect(orphanPromoted.getByText('Favorito tier 3')).toHaveCount(0)

    const live = decidir.locator('tbody tr').filter({ hasText: 'RS-LIVE-948' })
    await expect(live.getByRole('button', { name: 'Já existe', disabled: true })).toBeVisible()
    await expect(live.getByText('Equivale ao favorito ativo 12')).toBeVisible()

    await page.getByRole('tab', { name: /Acompanhando/ }).click()
    await expect(partials.getByRole('button', { name: 'Promover' }).first()).toBeVisible()

    await page.getByRole('tab', { name: 'Montar' }).click()
    await expect(page.getByRole('heading', { name: 'Preflight' })).toBeVisible()
    await expect(page.getByRole('heading', { name: 'Rascunho de varredura' })).toBeVisible()
  })
}
