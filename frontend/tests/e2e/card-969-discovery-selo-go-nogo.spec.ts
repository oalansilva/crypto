import { expect, test, type Page } from '@playwright/test'

const ADMIN_USER = {
  id: 'discovery-admin-969',
  email: 'alan@example.com',
  name: 'Alan Silva',
  isAdmin: true,
  mustChangePassword: false,
}

const SNAPSHOT = {
  axes: {
    templates: ['multi_ma_crossover'],
    symbols: ['BTC/USDT', 'AGLD/USDT', 'DOGE/USDT', 'ADA/USDT', 'LINK/USDT'],
    timeframes: ['1d', '4h'],
    directions: ['long', 'short'],
  },
  raw_total: 8,
  exclusions: {},
  excluded_count: 0,
  valid_total: 8,
  limits: { max_total: 1000 },
  errors: {},
  expires_at: '2026-09-11T13:00:00Z',
  snapshot_token: 'snapshot-token-969',
  snapshot_hash: '969abcdef969abcdef969abcdef969abcdef969abcdef969abcdef969abcdef',
  period_type: 'all',
  start_date: '2017-01-01',
  end_date: '2026-09-08',
}

const ACTIVE = {
  sweep_id: 'c969gongo',
  state: 'running',
  total: 8,
  succeeded: 6,
  failed: 0,
  skipped: 0,
  insufficient_sample: 1,
  processed: 7,
  terminal_reason: null,
  terminal_code: null,
  draft_key: 'draft-969',
  snapshot: SNAPSHOT,
  updated_at: '2026-09-11T12:00:00Z',
}

const TEMPLATES = [
  {
    name: 'multi_ma_crossover',
    display_name: 'Médias Móveis: Cruzamento',
    description: 'Cruzamento de médias móveis.',
    is_readonly: true,
  },
]

function row(partial: Record<string, unknown>) {
  return {
    template_id: 'multi_ma_crossover',
    display_name: 'Médias Móveis: Cruzamento',
    description: 'Cruzamento de médias móveis.',
    timeframe: '1d',
    direction: 'long',
    parameters: {},
    cagr: 0.12,
    benchmark_cagr: 0.08,
    delta_cagr_vs_bh: 4,
    sharpe_ratio: 0.5,
    profit_factor: 1.8,
    win_rate: 0.55,
    coverage: 0.95,
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
    rank: 1,
    result_id: 'RS-E0E30719CC',
    symbol: 'BTC/USDT',
    calmar_ratio: 10.6,
    max_drawdown: 0.12,
    trades_count: 43,
    eligibility: 'eligible',
    oos_verdict: { status: 'GO', reasons: ['GO Descoberta: treino decente e Sharpe OOS > 0.'] },
  }),
  row({
    rank: 2,
    result_id: 'RS-AGLD-NOGO',
    symbol: 'AGLD/USDT',
    calmar_ratio: 1.1,
    max_drawdown: 0.18,
    trades_count: 38,
    eligibility: 'eligible',
    oos_verdict: {
      status: 'NO-GO',
      reasons: ['Holdout — Sharpe OOS −0,18 ≤ 0 (limiar > 0)'],
    },
  }),
  row({
    rank: 3,
    result_id: 'RS-DOGE-NOGO',
    symbol: 'DOGE/USDT',
    calmar_ratio: 0.42,
    max_drawdown: 0.22,
    trades_count: 40,
    eligibility: 'eligible',
    oos_verdict: {
      status: 'NO-GO',
      reasons: ['Treino — Calmar 0,42 < 1'],
    },
  }),
  row({
    rank: null,
    result_id: 'RS-ADA-LOW',
    symbol: 'ADA/USDT',
    calmar_ratio: 0.9,
    max_drawdown: 0.2,
    trades_count: 22,
    eligibility: 'low_sample',
    eligibility_reason: 'trades 22 < mínimo 30',
    oos_verdict: { status: 'NO-GO', reasons: ['legado combo'] },
  }),
  row({
    rank: null,
    result_id: 'RS-INSUF',
    symbol: 'LINK/USDT',
    direction: 'short',
    timeframe: '4h',
    calmar_ratio: null,
    eligibility: 'insufficient_sample',
    trades_count: null,
    coverage: null,
    oos_verdict: { status: 'NO-GO' },
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
    route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ sweeps: [] }) }),
  )
  await page.route('**/api/combos/discovery/sweeps/c969gongo', (route) =>
    route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(ACTIVE) }),
  )
  await page.route('**/api/combos/discovery/sweeps/*/partials?*', (route) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ results: RESULTS.slice(0, 3), total: 3 }),
    }),
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
  test(`card 969 — ${viewport.name} selo Discovery vs proto`, async ({ page }) => {
    await page.setViewportSize({ width: viewport.width, height: viewport.height })
    await installMocks(page)
    await page.goto('/combo/discovery')

    await expect(page.getByRole('heading', { name: 'Descoberta de estratégias swing' })).toBeVisible()
    await page.getByRole('tab', { name: 'Decidir' }).click()

    const goRow = page.locator('tr.result-row').filter({ has: page.getByText('RS-E0E30719CC') })
    await expect(goRow.getByTestId('seal-go')).toHaveText('GO')
    await expect(goRow.getByTestId('reason-holdout')).toHaveCount(0)

    const holdoutNogo = page.locator('tr.result-row').filter({ has: page.getByText('RS-AGLD-NOGO') })
    await expect(holdoutNogo.getByTestId('seal-nogo')).toBeVisible()
    await expect(holdoutNogo.getByTestId('reason-holdout')).toContainText('Holdout')
    await expect(page.getByTestId('promote-RS-AGLD-NOGO')).toBeEnabled()

    const treinoNogo = page.locator('tr.result-row').filter({ has: page.getByText('RS-DOGE-NOGO') })
    await expect(treinoNogo.getByTestId('reason-treino')).toContainText('Treino')

    const lowSample = page.locator('[data-eligibility="low_sample"]')
    await expect(lowSample.getByText('Baixa amostra').first()).toBeVisible()
    await expect(lowSample.getByText('NO-GO')).toHaveCount(0)
    await expect(page.getByTestId('promote-RS-ADA-LOW')).toBeDisabled()

    if (viewport.name === 'mobile') {
      const chip = goRow.getByTestId('seal-go')
      const box = await chip.boundingBox()
      expect(box?.width ?? 0).toBeGreaterThan(120)
    }

    await page.getByRole('tab', { name: 'Montar' }).click()
    await expect(page.getByRole('heading', { name: 'Preflight' })).toBeVisible()
    await expect(page.getByRole('heading', { name: 'Rascunho de varredura' })).toBeVisible()
  })
}
