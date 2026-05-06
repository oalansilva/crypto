import { expect, test } from '@playwright/test'

const AUTH_USER = {
  id: 'test-user',
  email: 'test@example.com',
  name: 'Test User',
  isAdmin: false,
}

async function mockAuthenticatedSession(page: any) {
  await page.addInitScript((user) => {
    window.localStorage.setItem('auth_access_token', 'test-access-token')
    window.localStorage.setItem('auth_refresh_token', 'test-refresh-token')
    window.localStorage.setItem('auth_user', JSON.stringify(user))
  }, AUTH_USER)
}

const FAVORITES_PAYLOAD = [
  {
    id: 1,
    name: 'BTC Core',
    symbol: 'BTC/USDT',
    timeframe: '1d',
    strategy_name: 'ema_rsi',
    parameters: {},
    metrics: {},
    created_at: '2025-01-01T00:00:00Z',
    tier: 1,
  },
  {
    id: 2,
    name: 'AAPL Core',
    symbol: 'AAPL',
    timeframe: '1d',
    strategy_name: 'ema_rsi',
    parameters: {},
    metrics: {},
    created_at: '2025-01-01T00:00:00Z',
    tier: 1,
  },
]

const OPPORTUNITIES_PAYLOAD = [
  {
    id: 1,
    symbol: 'BTC/USDT',
    timeframe: '1d',
    template_name: 'ema_rsi',
    name: 'BTC Core',
    notes: '',
    tier: 1,
    parameters: {},
    is_holding: true,
    distance_to_next_status: 0.5,
    next_status_label: 'exit',
    status: 'HOLDING',
    message: 'Holding position',
    last_price: 50000,
    timestamp: '2025-01-01T00:00:00Z',
    details: {},
  },
  {
    id: 2,
    symbol: 'AAPL',
    timeframe: '1d',
    template_name: 'ema_rsi',
    name: 'AAPL Core',
    notes: '',
    tier: 1,
    parameters: {},
    is_holding: false,
    distance_to_next_status: 0.6,
    next_status_label: 'entry',
    status: 'WAIT',
    message: 'Waiting for entry',
    last_price: 200,
    timestamp: '2025-01-01T00:00:00Z',
    details: {},
  },
]

async function setupApiMocks(page: any) {
  await mockAuthenticatedSession(page)

  const preferences: Record<string, any> = {
    __global__: { in_portfolio: false, card_mode: 'price', price_timeframe: '1d', theme: 'dark-green' },
    'BTC/USDT': { in_portfolio: true, card_mode: 'price', price_timeframe: '1d', theme: 'dark-green' },
    AAPL: { in_portfolio: true, card_mode: 'price', price_timeframe: '1d', theme: 'dark-green' },
  }

  await page.route('**/*', (route: any) => {
    const url = new URL(route.request().url())
    if (url.hostname === '127.0.0.1' || url.hostname === 'localhost') {
      return route.continue()
    }
    return route.abort('blockedbyclient')
  })

  await page.route('**/api/favorites/', (route: any) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(FAVORITES_PAYLOAD),
    })
  )

  await page.route('**/api/opportunities/**', (route: any) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(OPPORTUNITIES_PAYLOAD),
    })
  )

  await page.route('**/api/auth/me', (route: any) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(AUTH_USER),
    })
  )

  await page.route('**/api/monitor/preferences', (route: any) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(preferences),
    })
  )

  await page.route('**/api/monitor/preferences/*', (route: any) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ in_portfolio: true, card_mode: 'price', price_timeframe: '1d', theme: 'dark-green' }),
    })
  )

  await page.route('**/api/user/binance-credentials', (route: any) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ configured: false, api_key_masked: null }),
    })
  )

  await page.route('**/api/market/candles**', (route: any) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ candles: [] }),
    })
  )
}

test('monitor hides stock opportunities in crypto-only MVP', async ({ page }) => {
  await setupApiMocks(page)
  await page.goto('/monitor')

  await expect(page.getByTestId('monitor-row-btc-usdt')).toBeVisible()
  await expect(page.getByText('AAPL', { exact: true })).toHaveCount(0)
  await expect(page.getByTestId('monitor-filter-asset-type')).toHaveCount(0)
})
