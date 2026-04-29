import { expect, test } from '@playwright/test'

const AUTH_USER = {
  id: 'test-user',
  email: 'test@example.com',
  name: 'Test User',
  isAdmin: false,
}

const NOW = new Date().toISOString()

async function mockAuthenticatedSession(page: any) {
  await page.addInitScript((user) => {
    window.localStorage.setItem('auth_access_token', 'test-access-token')
    window.localStorage.setItem('auth_refresh_token', 'test-refresh-token')
    window.localStorage.setItem('auth_user', JSON.stringify(user))
  }, AUTH_USER)
}

const OPPORTUNITIES_PAYLOAD = [
  {
    id: 1,
    symbol: 'BTC/USDT',
    timeframe: '1d',
    template_name: 'ema_rsi',
    name: 'BTC Hold',
    notes: '',
    tier: 1,
    parameters: { ema_short: 9, ema_long: 21 },
    is_holding: true,
    distance_to_next_status: 0.4,
    next_status_label: 'exit',
    indicator_values_candle_time: NOW,
    status: 'HOLDING',
    message: 'Posição ativa monitorada.',
    last_price: 50000,
    timestamp: NOW,
    details: {},
  },
  {
    id: 2,
    symbol: 'ETH/USDT',
    timeframe: '1h',
    template_name: 'ema_rsi',
    name: 'ETH Wait',
    notes: '',
    tier: 1,
    parameters: { ema_short: 9, ema_long: 21 },
    is_holding: false,
    distance_to_next_status: 0.7,
    next_status_label: 'entry',
    indicator_values_candle_time: NOW,
    status: 'WAIT',
    message: 'Aguardando condição de entrada.',
    last_price: 3000,
    timestamp: NOW,
    details: {},
  },
  {
    id: 3,
    symbol: 'AAPL',
    timeframe: '1d',
    template_name: 'ema_rsi',
    name: 'AAPL Exit',
    notes: '',
    tier: 2,
    parameters: { ema_short: 9, ema_long: 21 },
    is_holding: false,
    distance_to_next_status: 1.2,
    next_status_label: 're-entry',
    indicator_values_candle_time: NOW,
    status: 'EXITED',
    message: 'Condição de saída registrada.',
    last_price: 200,
    timestamp: NOW,
    details: {},
  },
]

async function setupApiMocks(page: any) {
  await mockAuthenticatedSession(page)

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
      body: JSON.stringify([
        { id: 1, name: 'BTC Hold', symbol: 'BTC/USDT', timeframe: '4h', strategy_name: 'ema_rsi', parameters: {}, metrics: {}, created_at: '2025-01-01T00:00:00Z', tier: 1 },
        { id: 2, name: 'ETH Wait', symbol: 'ETH/USDT', timeframe: '1h', strategy_name: 'ema_rsi', parameters: {}, metrics: {}, created_at: '2025-01-01T00:00:00Z', tier: 1 },
        { id: 3, name: 'AAPL Exit', symbol: 'AAPL', timeframe: '1d', strategy_name: 'ema_rsi', parameters: {}, metrics: {}, created_at: '2025-01-01T00:00:00Z', tier: 2 },
      ]),
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
        body: JSON.stringify({
          __global__: { in_portfolio: false, card_mode: 'price', price_timeframe: '1d', theme: 'dark-green' },
        'BTC/USDT': { in_portfolio: true, card_mode: 'price', price_timeframe: '1d', theme: 'dark-green' },
        'ETH/USDT': { in_portfolio: true, card_mode: 'price', price_timeframe: '1d', theme: 'dark-green' },
        'AAPL': { in_portfolio: true, card_mode: 'price', price_timeframe: '1d', theme: 'dark-green' },
      }),
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
      body: JSON.stringify({
        candles: [
          { timestamp_utc: NOW, open: 100, high: 102, low: 99, close: 101, volume: 1000 },
          { timestamp_utc: NOW, open: 101, high: 103, low: 100, close: 102, volume: 1100 },
        ],
      }),
    })
  )
}

test('issue 70: monitor standardizes states to HOLD, WAIT and EXIT', async ({ page }) => {
  await setupApiMocks(page)
  await page.goto('/monitor')

  await expect(page.getByText('Estado HOLD')).toBeVisible()
  await expect(page.getByText('Estado WAIT')).toBeVisible()
  await expect(page.getByText('Estado EXIT')).toBeVisible()

  const holdCard = page.getByTestId('monitor-card-btc-usdt')
  const waitCard = page.getByTestId('monitor-card-eth-usdt')
  const exitCard = page.getByTestId('monitor-card-aapl')

  await expect(holdCard.getByText(/^HOLD$/)).toBeVisible()
  await expect(waitCard.getByText(/^WAIT$/)).toBeVisible()
  await expect(exitCard.getByText(/^EXIT$/)).toBeVisible()
})
