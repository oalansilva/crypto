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
    templates: ['bollinger_breakout'],
    symbols: ['BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'ALPHA/USDT', 'ARPA/USDT', 'ADA/USDT'],
    timeframes: ['1d'],
    directions: ['long'],
  },
  raw_total: 16,
  exclusions: {},
  excluded_count: 0,
  valid_total: 16,
  limits: { max_total: 1000 },
  errors: {},
  expires_at: '2026-09-11T13:00:00Z',
  snapshot_token: 'snapshot-token-896',
  snapshot_hash: '896abcdef896abcdef896abcdef896abcdef896abcdef896abcdef896abcdef',
  period_type: 'all',
  start_date: '2017-01-01',
  end_date: '2026-09-08',
}

const ACTIVE = {
  sweep_id: 'c896nogo',
  state: 'running',
  total: 16,
  succeeded: 12,
  failed: 1,
  skipped: 1,
  insufficient_sample: 0,
  processed: 14,
  terminal_reason: null,
  terminal_code: null,
  draft_key: 'draft-896',
  snapshot: SNAPSHOT,
  updated_at: '2026-09-11T12:00:00Z',
}

const TEMPLATES = [
  {
    name: 'bollinger_breakout',
    display_name: 'Bandas: expansão',
    description: 'Opera a expansão da faixa com bandas.',
    is_readonly: true,
  },
]

function row(partial: Record<string, unknown>) {
  return {
    template_id: 'bollinger_breakout',
    display_name: 'Bandas: expansão',
    description: 'Opera a expansão da faixa com bandas.',
    timeframe: '1d',
    direction: 'long',
    parameters: {},
    cagr: null,
    benchmark_cagr: null,
    delta_cagr_vs_bh: null,
    sharpe_ratio: null,
    profit_factor: null,
    win_rate: null,
    coverage: 0.97,
    eligibility_reason: null,
    dedup_state: 'unique',
    dedup_reference: null,
    start_at: '2017-01-01T00:00:00Z',
    end_at: '2026-09-08T00:00:00Z',
    candle_source: 'ccxt',
    candle_version: null,
    expected_candles: 3500,
    observed_valid_candles: 3400,
    fees_slippage: { fees: 0.001, slippage: 0.0005 },
    oos_verdict: null,
    ...partial,
  }
}

const RESULTS = [
  row({
    rank: 1, result_id: 'RS-896-01', symbol: 'BTC/USDT',
    calmar_ratio: 1.2, max_drawdown: 0.148, trades_count: 42, coverage: 0.97,
    eligibility: 'eligible', oos_verdict: { status: 'GO' },
  }),
  row({
    rank: 2, result_id: 'RS-896-02', symbol: 'ETH/USDT',
    calmar_ratio: 0.94, max_drawdown: 0.135, trades_count: 44, coverage: 0.95,
    eligibility: 'eligible', oos_verdict: { status: 'GO' },
  }),
  row({
    rank: 3, result_id: 'RS-896-03', symbol: 'SOL/USDT',
    calmar_ratio: 0.81, max_drawdown: 0.181, trades_count: 41, coverage: 0.96,
    eligibility: 'eligible', oos_verdict: { status: 'GO' },
  }),
  row({
    rank: 4, result_id: 'RS-B109ED2C80', symbol: 'ALPHA/USDT',
    calmar_ratio: 22.0, max_drawdown: 0.165, trades_count: 30, coverage: 1,
    eligibility: 'eligible', oos_verdict: { status: 'NO-GO', reasons: ['Sharpe IS 0,31'] },
  }),
  row({
    rank: 5, result_id: 'RS-896-NA', symbol: 'ARPA/USDT',
    calmar_ratio: 1.195e27, max_drawdown: 0.092, trades_count: 31, coverage: 0.94,
    eligibility: 'eligible', oos_verdict: { status: 'NO-GO' },
  }),
  row({
    rank: null, result_id: 'RS-896-LS', symbol: 'ADA/USDT',
    calmar_ratio: 3.2, max_drawdown: 0.159, trades_count: 18, coverage: 0.82,
    eligibility: 'low_sample', eligibility_reason: 'mínimo 30 trades e 90% cobertura',
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
  await page.route('**/api/combos/discovery/sweeps/c896nogo', (route) =>
    route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(ACTIVE) }),
  )
  await page.route('**/api/combos/discovery/sweeps/*/leaderboard?*', (route) => {
    const url = new URL(route.request().url())
    const exclude = url.searchParams.get('exclude_eligibility')
    const offset = Number(url.searchParams.get('offset') || 0)
    const limit = Number(url.searchParams.get('limit') || 10)
    const matched = RESULTS.filter((item) => item.eligibility !== exclude)
    return route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        results: matched.slice(offset, offset + limit),
        total: matched.length,
        unfiltered_total: RESULTS.length,
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
  test(`card 896 — ${viewport.name} Calmar calendário, GO-first e selo vs proto`, async ({ page }) => {
    await page.setViewportSize({ width: viewport.width, height: viewport.height })
    await installMocks(page)
    await page.goto('/combo/discovery')

    await expect(page.getByRole('heading', { name: 'Descoberta de estratégias swing' })).toBeVisible()
    await expect(page.getByTestId('discovery-modes')).toBeVisible()

    const partials = page.getByTestId('partials-table')
    await expect(partials).toBeVisible()
    const firstPartial = partials.locator('tbody tr').first()
    await expect(firstPartial).toHaveAttribute('data-verdict', 'GO')
    await expect(firstPartial.getByTestId('seal-go')).toHaveText('GO')
    await expect(firstPartial.locator('td').nth(2)).toHaveText('1,20')
    await expect(partials.getByText('1.195.206')).toHaveCount(0)
    await expect(partials.getByText(/1e\+?27/i)).toHaveCount(0)

    const alphaPartial = page.getByTestId('partial-nogo')
    await expect(alphaPartial.getByTestId('seal-nogo')).toHaveText('NO-GO')
    await expect(alphaPartial.getByText('ALPHA/USDT')).toBeVisible()
    await expect(alphaPartial.locator('td').nth(2)).toHaveText('22,00')
    await expect(alphaPartial.getByText('30 · 100%')).toBeVisible()
    await expect(alphaPartial.getByText('Baixa amostra')).toHaveCount(0)
    await expect(alphaPartial.getByText('Amostra insuficiente')).toHaveCount(0)

    const naPartial = page.getByTestId('partial-na')
    await expect(naPartial.getByText('N/A')).toBeVisible()

    const partialVerdicts = await partials.locator('tbody tr').evaluateAll((rows) =>
      rows.map((row) => (row as HTMLElement).dataset.verdict || ''),
    )
    const lastGo = partialVerdicts.lastIndexOf('GO')
    const firstNogo = partialVerdicts.indexOf('NO-GO')
    expect(lastGo).toBeGreaterThanOrEqual(0)
    expect(firstNogo).toBeGreaterThan(lastGo)

    await page.getByRole('tab', { name: 'Montar' }).click()
    await expect(page.getByRole('heading', { name: 'Preflight' })).toBeVisible()
    await expect(page.getByRole('heading', { name: 'Rascunho de varredura' })).toBeVisible()

    await page.getByRole('tab', { name: 'Decidir' }).click()
    await expect(page.getByRole('columnheader', { name: 'Calmar (CAGR anual do calendário ÷ Max DD)' })).toBeVisible()
    await expect(page.getByRole('columnheader', { name: 'negócios / cobertura' })).toBeVisible()
    await expect(page.getByTestId('column-copy')).toContainText('não é taxa de acerto')

    const decidirRows = page.locator('#panel-decidir tbody tr.result-row')
    await expect(decidirRows.first()).toHaveAttribute('data-verdict', 'GO')
    await expect(decidirRows.first().locator('td').nth(2)).toHaveText('1,20')

    const nogo = page.getByTestId('row-nogo')
    await expect(nogo.getByTestId('seal-nogo')).toHaveText('NO-GO')
    await expect(nogo.getByText('22,00')).toBeVisible()
    await expect(nogo.getByText('30 · 100%')).toBeVisible()
    await expect(page.getByTestId('promote-RS-B109ED2C80')).toBeEnabled()
    await expect(page.getByTestId('promote-RS-B109ED2C80')).toHaveText('Promover')

    await expect(page.getByText('N/A').first()).toBeVisible()
    await expect(page.getByText('1.195')).toHaveCount(0)

    const lowSample = page.locator('[data-eligibility="low_sample"]')
    await expect(lowSample.getByText('Baixa amostra').first()).toBeVisible()
    await expect(lowSample.getByText('NO-GO')).toHaveCount(0)

    const box = await nogo.getByTestId('seal-nogo').boundingBox()
    expect(box).toBeTruthy()
    if (viewport.name === 'mobile') {
      expect(box!.width).toBeLessThan(viewport.width * 0.7)
    }
  })
}
