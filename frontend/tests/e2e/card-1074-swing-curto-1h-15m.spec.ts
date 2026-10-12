import { expect, test, type Page } from '@playwright/test'

const ADMIN_USER = {
  id: 'discovery-admin-1074',
  email: 'alan@example.com',
  name: 'Alan Silva',
  isAdmin: true,
  mustChangePassword: false,
}

const SNAPSHOT = {
  axes: {
    templates: ['multi_ma_crossover'],
    symbols: ['BTC/USDT'],
    timeframes: ['1d'],
    directions: ['long'],
  },
  raw_total: 1,
  exclusions: {},
  excluded_count: 0,
  valid_total: 1,
  limits: { max_total: 1000 },
  errors: {},
  expires_at: '2026-10-02T13:00:00Z',
  snapshot_token: 'snapshot-token-1074',
  snapshot_hash: '1074abcdef1074abcdef1074abcdef1074abcdef1074abcdef1074abcdef1074abcd',
  period_type: 'all',
  start_date: '2017-01-01',
  end_date: '2026-10-02',
}

const TEMPLATES = [
  {
    name: 'multi_ma_crossover',
    display_name: 'Médias Móveis: Cruzamento',
    description: 'Cruzamento de médias móveis.',
    is_readonly: true,
  },
  {
    name: 'donchian_volume_breakout',
    display_name: 'Canal Donchian + volume',
    description: 'Donchian com volume.',
    is_readonly: true,
  },
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
      body: JSON.stringify({ symbols: ['BTC/USDT', 'ETH/USDT'] }),
    }),
  )
  await page.route('**/api/combos/discovery/sweeps/preflight', (route) =>
    route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(SNAPSHOT) }),
  )
  await page.route('**/api/combos/discovery/sweeps/active', (route) =>
    route.fulfill({ status: 404, contentType: 'application/json', body: '{}' }),
  )
}

test.describe('card-1074 discovery swing 1h 15m', () => {
  test.beforeEach(async ({ page }) => {
    await installMocks(page)
    await page.goto('/combo/discovery')
  })

  test('Montar landmarks, timeframes e nota de custo', async ({ page }) => {
    await expect(page.getByRole('heading', { name: 'Descoberta de estratégias swing' })).toBeVisible()
    await expect(
      page.getByText('Compare templates em 4h, 1h, 15m e 1d.', { exact: false }),
    ).toBeVisible()

    await expect(page.getByRole('heading', { name: 'Preflight' })).toBeVisible()
    await expect(page.getByRole('heading', { name: 'Rascunho de varredura' })).toBeVisible()

    await expect(page.getByTestId('timeframe-15m')).toBeVisible()
    await expect(page.getByTestId('timeframe-1h')).toBeVisible()
    await expect(page.getByTestId('timeframe-4h')).toBeVisible()
    await expect(page.getByTestId('timeframe-1d')).toBeVisible()

    await expect(page.getByTestId('cost-note')).toContainText('taxa 0,075%')
    await expect(page.getByTestId('cost-note')).toContainText('slippage do timeframe')
  })
})
