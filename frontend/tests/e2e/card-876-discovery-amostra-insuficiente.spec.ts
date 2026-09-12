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
    symbols: ['BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'BNB/USDT', 'XRP/USDT', 'ADA/USDT', 'BLZ/USDT'],
    timeframes: ['1d'],
    directions: ['long'],
  },
  raw_total: 24,
  exclusions: {},
  excluded_count: 0,
  valid_total: 24,
  limits: { max_total: 1000 },
  errors: {},
  expires_at: '2026-09-09T13:00:00Z',
  snapshot_token: 'snapshot-token-876',
  snapshot_hash: '876abcdef876abcdef876abcdef876abcdef876abcdef876abcdef876abcdef',
  period_type: 'all',
  start_date: '2017-01-01',
  end_date: '2026-09-08',
}

const ACTIVE = {
  sweep_id: 'c876a01e',
  state: 'running',
  total: 24,
  succeeded: 12,
  failed: 1,
  skipped: 1,
  insufficient_sample: 4,
  processed: 18,
  terminal_reason: null,
  terminal_code: null,
  draft_key: 'draft-876',
  snapshot: SNAPSHOT,
  updated_at: '2026-09-09T12:00:00Z',
}

const TEMPLATES = [
  { name: 'bollinger_breakout', display_name: 'Bandas: expansão', description: 'Opera a expansão da faixa com bandas.', is_readonly: true },
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
    ...partial,
  }
}

const RESULTS = [
  row({
    rank: 1, result_id: 'RS-876-01', symbol: 'BTC/USDT',
    calmar_ratio: 2.84, max_drawdown: 0.154, trades_count: 45, coverage: 0.97,
    eligibility: 'eligible',
  }),
  row({
    rank: 2, result_id: 'RS-876-02', symbol: 'ETH/USDT',
    calmar_ratio: 2.31, max_drawdown: 0.135, trades_count: 44, coverage: 0.95,
    eligibility: 'eligible',
  }),
  row({
    rank: 3, result_id: 'RS-876-SOL', symbol: 'SOL/USDT',
    calmar_ratio: 1.92, max_drawdown: 0.181, trades_count: 41, coverage: 0.96,
    eligibility: 'eligible',
  }),
  row({
    rank: 4, result_id: 'RS-876-BNB', symbol: 'BNB/USDT',
    calmar_ratio: 1.71, max_drawdown: 0.162, trades_count: 38, coverage: 0.94,
    eligibility: 'eligible',
  }),
  row({
    rank: 5, result_id: 'RS-876-XRP', symbol: 'XRP/USDT',
    calmar_ratio: 1.44, max_drawdown: 0.19, trades_count: 36, coverage: 0.93,
    eligibility: 'eligible',
  }),
  row({
    rank: null, result_id: 'RS-876-03', symbol: 'ADA/USDT',
    calmar_ratio: 3.2, max_drawdown: 0.159, trades_count: 18, coverage: 0.82,
    eligibility: 'low_sample', eligibility_reason: 'mínimo 30 trades e 90% cobertura',
  }),
  row({
    rank: null, result_id: 'RS-876-INS', symbol: 'BLZ/USDT',
    calmar_ratio: null, max_drawdown: null, trades_count: null, coverage: null,
    eligibility: 'insufficient_sample', eligibility_reason: 'treino 18 < mínimo 30',
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
  await page.route('**/api/combos/discovery/sweeps/c876a01e', (route) =>
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
  test(`card 876 — ${viewport.name} fórmula, Decidir e parciais vs proto`, async ({ page }) => {
    await page.setViewportSize({ width: viewport.width, height: viewport.height })
    await installMocks(page)
    await page.goto('/combo/discovery')

    await expect(page.getByRole('heading', { name: 'Descoberta de estratégias swing' })).toBeVisible()
    await expect(page.getByTestId('discovery-modes')).toBeVisible()
    await expect(page.getByTestId('counter-invariant')).toHaveText(
      '18 processadas = 12 sucesso + 1 falha + 1 ignoradas + 4 amostra insuficiente',
    )
    await expect(page.getByText('Limites: 8 global · 1 por sweep · fila justa')).toBeVisible()

    const partials = page.getByTestId('partials-table')
    await expect(partials).toBeVisible()
    await expect(partials.getByText('Amostra insuficiente')).toHaveCount(0)
    await expect(partials.getByText('BLZ/USDT')).toHaveCount(0)

    await page.getByRole('tab', { name: 'Montar' }).click()
    await expect(page.getByRole('heading', { name: 'Preflight' })).toBeVisible()
    await expect(page.getByRole('heading', { name: 'Rascunho de varredura' })).toBeVisible()

    await page.getByRole('tab', { name: 'Decidir' }).click()
    const insufficient = page.getByTestId('row-insufficient')
    await expect(insufficient).toBeVisible()
    await expect(insufficient.getByTestId('seal-insufficient')).toHaveText('Amostra insuficiente')
    await expect(insufficient.getByText('Baixa amostra')).toHaveCount(0)
    await expect(insufficient.getByText('—')).toBeVisible()
    await expect(insufficient.locator('td.na')).toHaveCount(6)
    await expect(insufficient.getByRole('button', { name: 'Promover' })).toHaveCount(0)
    await expect(insufficient.getByRole('button', { name: /Excluir/ })).toBeVisible()

    const lowSample = page.locator('[data-eligibility="low_sample"]')
    await expect(lowSample.getByText('Baixa amostra').first()).toBeVisible()
    await expect(lowSample.getByTestId('promote-RS-876-03')).toBeDisabled()
    await expect(lowSample.getByTestId('promote-RS-876-03')).toHaveText('Baixa amostra')

    await expect(page.getByTestId('promote-RS-876-01')).toBeEnabled()
    await expect(page.getByTestId('promote-RS-876-01')).toHaveText('Promover')
  })
}
