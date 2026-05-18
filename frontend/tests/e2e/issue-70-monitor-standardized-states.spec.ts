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
    symbol: 'ETH/USDT',
    timeframe: '1d',
    template_name: 'ema_rsi',
    name: 'ETH Compra',
    notes: '',
    tier: 1,
    parameters: { ema_short: 9, ema_long: 21 },
    is_holding: true,
    distance_to_next_status: 0.4,
    next_status_label: 'exit',
    indicator_values_candle_time: NOW,
    status: 'HOLD',
    message: 'Posição ativa monitorada.',
    last_price: 50000,
    timestamp: NOW,
    details: {},
  },
  {
    id: 122,
    symbol: 'BTC/USDT',
    timeframe: '1d',
    template_name: 'multi_ma_crossoverV2',
    name: 'multi_ma_crossoverV2 - BTC/USDT 1d (batch)',
    notes: '',
    tier: 1,
    parameters: { ema_short: 9, ema_long: 21 },
    is_holding: false,
    distance_to_next_status: 0.7,
    next_status_label: 'entry',
    indicator_values_candle_time: NOW,
    status: 'EXIT',
    message: 'Venda/fora de posicao. Aguardando proxima compra.',
    last_price: 76599,
    timestamp: NOW,
    details: {},
  },
  {
    id: 200,
    symbol: 'BTC/USDT',
    timeframe: '1d',
    template_name: 'quant_btc_1d_roc_ema_momentum_guard_long_v3',
    name: 'Quant BTC 1D ROC+EMA Momentum Guard Long v3',
    notes: '',
    tier: 1,
    parameters: { ema_short: 9, ema_long: 21 },
    is_holding: false,
    distance_to_next_status: 1.2,
    next_status_label: 're-entry',
    indicator_values_candle_time: NOW,
    status: 'EXIT',
    message: 'Venda/fora de posicao. Aguardando proxima compra.',
    last_price: 76599,
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
        { id: 1, name: 'ETH Compra', symbol: 'ETH/USDT', timeframe: '1d', strategy_name: 'ema_rsi', parameters: {}, metrics: {}, created_at: '2025-01-01T00:00:00Z', tier: 1 },
        { id: 122, name: 'multi_ma_crossoverV2 - BTC/USDT 1d (batch)', symbol: 'BTC/USDT', timeframe: '1d', strategy_name: 'multi_ma_crossoverV2', parameters: {}, metrics: {}, created_at: '2025-01-01T00:00:00Z', tier: 1 },
        { id: 200, name: 'Quant BTC 1D ROC+EMA Momentum Guard Long v3', symbol: 'BTC/USDT', timeframe: '1d', strategy_name: 'quant_btc_1d_roc_ema_momentum_guard_long_v3', parameters: {}, metrics: {}, created_at: '2025-01-01T00:00:00Z', tier: 1 },
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
        'XRP/USDT': { in_portfolio: true, card_mode: 'price', price_timeframe: '1d', theme: 'dark-green' },
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

test('monitor shows only Compra and Venda and keeps same-symbol starred strategies visible', async ({ page }) => {
  await setupApiMocks(page)
  await page.goto('/monitor')

  await expect(page.getByText('Estado Compra')).toBeVisible()
  await expect(page.getByText('Estado Espera')).toHaveCount(0)
  await expect(page.getByText('Estado Venda')).toBeVisible()

  await expect(page.getByTestId('monitor-row-btc-usdt')).toHaveCount(2)
  await expect(page.locator('[data-testid="monitor-row-btc-usdt"]', { hasText: 'multi_ma_crossoverV2' })).toBeVisible()
  await expect(page.locator('[data-testid="monitor-row-btc-usdt"]', { hasText: 'quant_btc_1d_roc_ema_momentum_guard_long_v3' })).toBeVisible()

  await page.getByTestId('monitor-row-eth-usdt').click()
  await page.locator('[data-testid="monitor-row-btc-usdt"]', { hasText: 'multi_ma_crossoverV2' }).click()

  await expect(page.getByTestId('monitor-card-eth-usdt').locator('.status-pill.hold').first()).toHaveText('Compra')
  await expect(page.getByTestId('monitor-card-btc-usdt').first().locator('.status-pill.exit').first()).toHaveText('Venda')
})
