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
    name: 'BTC Trend',
    symbol: 'BTC/USDT',
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
    name: 'BTC Trend',
    notes: '',
    tier: 1,
    parameters: { ema_short: 9, ema_long: 21 },
    is_holding: true,
    distance_to_next_status: 0.5,
    next_status_label: 'exit',
    status: 'HOLDING',
    message: 'Holding position',
    last_price: 1000,
    timestamp: '2025-01-01T00:00:00Z',
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

  await page.route('**/api/auth/me', (route: any) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(AUTH_USER),
    })
  )

  await page.route('**/api/favorites/', (route: any) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(FAVORITES_PAYLOAD),
    })
  )

  await page.route('**/api/favorites/5/trades', (route: any) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        trades: [
          {
            entry_time: '2099-04-10T00:00:00Z',
            entry_price: 70210.15,
            exit_time: '2099-04-13T00:00:00Z',
            exit_price: 72150.42,
            profit: 0.0276,
            type: 'long',
            signal_type: 'Regra de venda',
          },
        ],
        metrics: {
          total_trades: 1,
          win_rate: 1,
          total_return: 0.0276,
          avg_profit: 0.0276,
        },
      }),
    })
  )

  await page.route('**/api/opportunities/**', (route: any) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(OPPORTUNITIES_PAYLOAD),
    })
  )

  await page.route('**/api/monitor/preferences', (route: any) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        __global__: { in_portfolio: false, card_mode: 'price', price_timeframe: '1d', theme: 'dark-green' },
        'BTC/USDT': { in_portfolio: true, card_mode: 'price', price_timeframe: '1d', theme: 'dark-green' },
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

  await page.route('**/api/favorites/2/trades', (route: any) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        favorite_id: 2,
        trades: [
          {
            entry_time: '2026-05-09T00:00:00+00:00',
            entry_price: 0.0927,
            exit_time: '2026-05-20T00:00:00+00:00',
            exit_price: 0.08877,
            profit: -0.04383015327501139,
            type: 'long',
          },
        ],
        metrics: { total_trades: 1 },
        candles: [
          { timestamp_utc: '2026-05-09T00:00:00Z', open: 0.0927, high: 0.094, low: 0.091, close: 0.0932, volume: 1000 },
          { timestamp_utc: '2026-05-19T00:00:00Z', open: 0.089, high: 0.09, low: 0.088, close: 0.08877, volume: 1000 },
          { timestamp_utc: '2026-05-20T00:00:00Z', open: 0.08877, high: 0.0895, low: 0.0875, close: 0.08812, volume: 1000 },
        ],
        indicator_data: {},
        regenerated: false,
        execution_mode: 'deep_15m',
      }),
    })
  )

  await page.route('**/api/market/candles**', (route: any) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        candles: [
          { timestamp_utc: '2025-01-01T00:00:00Z', open: 100, high: 102, low: 99, close: 101, volume: 1000 },
          { timestamp_utc: '2025-01-01T01:00:00Z', open: 101, high: 103, low: 100, close: 102, volume: 1100 },
        ],
      }),
    })
  )
}

test.use({ viewport: { width: 390, height: 844 } })

test('monitor mobile uses single cards view without horizontal overflow', async ({ page }) => {
  await setupApiMocks(page)
  await page.goto('/monitor')

  await expect(page.getByTestId('monitor-card-btc-usdt')).toBeVisible()
  await expect(page.locator('.mobile-cards').first()).toBeVisible()
  await expect(page.getByTestId('timeframe-toggle-btc-usdt-1d')).toHaveAttribute('aria-pressed', 'true')
  await expect(page.getByTestId('timeframe-toggle-btc-usdt-15m')).toBeEnabled()
  await expect(page.getByTestId('timeframe-toggle-btc-usdt-1h')).toBeEnabled()
  await expect(page.getByTestId('timeframe-toggle-btc-usdt-4h')).toBeEnabled()
  const viewportFits = await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth + 1)
  expect(viewportFits).toBe(true)
})

test('monitor card keeps strategy timeframe visible when chart timeframe differs', async ({ page }) => {
  await mockAuthenticatedSession(page)

  await page.route('**/*', (route: any) => {
    const url = new URL(route.request().url())
    if (url.hostname === '127.0.0.1' || url.hostname === 'localhost') {
      return route.continue()
    }
    return route.abort('blockedbyclient')
  })

  await page.route('**/api/auth/me', (route: any) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(AUTH_USER),
    })
  )

  await page.route('**/api/favorites/', (route: any) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify([
        {
          id: 2,
          name: 'BTC Trend',
          symbol: 'BTC/USDT',
          timeframe: '1d',
          strategy_name: 'multi_ma_crossover',
          parameters: {},
          metrics: {},
          created_at: '2025-01-01T00:00:00Z',
          tier: 1,
        },
      ]),
    })
  )

  await page.route('**/api/opportunities/**', (route: any) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify([
        {
          id: 2,
          symbol: 'BTC/USDT',
          timeframe: '1d',
          template_name: 'multi_ma_crossover',
          name: 'BTC Trend',
          notes: '',
          tier: 1,
          parameters: { ema_short: 18, sma_medium: 20, sma_long: 35 },
          is_holding: true,
          distance_to_next_status: 0.5,
          next_status_label: 'exit',
          status: 'HOLDING',
          message: 'Holding position',
          last_price: 67915.02,
          timestamp: '2025-01-01T00:00:00Z',
          details: {},
        },
      ]),
    })
  )

  await page.route('**/api/monitor/preferences', (route: any) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        __global__: { in_portfolio: false, card_mode: 'price', price_timeframe: '1d', theme: 'dark-green' },
        'BTC/USDT': { in_portfolio: true, card_mode: 'price', price_timeframe: '1h', theme: 'dark-green' },
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
          { timestamp_utc: '2025-01-01T00:00:00Z', open: 100, high: 102, low: 99, close: 101, volume: 1000 },
          { timestamp_utc: '2025-01-01T01:00:00Z', open: 101, high: 103, low: 100, close: 102, volume: 1100 },
        ],
      }),
    })
  )

  await page.goto('/monitor')

  const card = page.getByTestId('monitor-card-btc-usdt')
  await expect(card).toBeVisible()
  await expect(card.getByTitle('Strategy timeframe')).toHaveText('1d')
  await expect(card.getByTitle('Price chart timeframe')).toHaveText('chart 1h')
})

test('monitor renders exited strategies separately from stopped out ones', async ({ page }) => {
  await mockAuthenticatedSession(page)

  await page.route('**/*', (route: any) => {
    const url = new URL(route.request().url())
    if (url.hostname === '127.0.0.1' || url.hostname === 'localhost') {
      return route.continue()
    }
    return route.abort('blockedbyclient')
  })

  await page.route('**/api/auth/me', (route: any) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(AUTH_USER),
    })
  )

  await page.route('**/api/favorites/', (route: any) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify([
        {
          id: 3,
          name: 'BTC Venda',
          symbol: 'BTC/USDT',
          timeframe: '1d',
          strategy_name: 'multi_ma_crossover',
          parameters: {},
          metrics: {},
          created_at: '2025-01-01T00:00:00Z',
          tier: 1,
        },
      ]),
    })
  )

  await page.route('**/api/opportunities/**', (route: any) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify([
        {
          id: 3,
          symbol: 'BTC/USDT',
          timeframe: '1d',
          template_name: 'multi_ma_crossover',
          name: 'BTC Venda',
          notes: '',
          tier: 1,
          parameters: { ema_short: 18, sma_medium: 20, sma_long: 35 },
          is_holding: false,
          distance_to_next_status: 0.38,
          next_status_label: 'entry',
          status: 'EXITED',
          message: 'Saida confirmada pela regra de exit. Aguardando reentrada.',
          last_price: 67915.02,
          timestamp: '2025-01-01T00:00:00Z',
          details: {},
        },
      ]),
    })
  )

  await page.route('**/api/monitor/preferences', (route: any) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        __global__: { in_portfolio: false, card_mode: 'price', price_timeframe: '1d', theme: 'dark-green' },
        'BTC/USDT': { in_portfolio: true, card_mode: 'strategy', price_timeframe: '1d', theme: 'dark-green' },
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

  await page.goto('/monitor')

  await expect(page.getByText('Estado Venda')).toBeVisible()
  await expect(page.getByTestId('monitor-card-btc-usdt').getByText(/^Venda$/)).toBeVisible()
})

test('monitor keeps backend exit in list and shows mismatched chart context', async ({ page }) => {
  await mockAuthenticatedSession(page)

  await page.route('**/*', (route: any) => {
    const url = new URL(route.request().url())
    if (url.hostname === '127.0.0.1' || url.hostname === 'localhost') {
      return route.continue()
    }
    return route.abort('blockedbyclient')
  })

  await page.route('**/api/auth/me', (route: any) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(AUTH_USER),
    })
  )

  await page.route('**/api/favorites/', (route: any) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify([
        {
          id: 4,
          name: 'BTC Trend',
          symbol: 'BTC/USDT',
          timeframe: '1d',
          strategy_name: 'multi_ma_crossover',
          parameters: {},
          metrics: {},
          created_at: '2026-04-15T00:00:00Z',
          tier: 1,
        },
      ]),
    })
  )

  await page.route('**/api/opportunities/**', (route: any) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify([
        {
          id: 4,
          symbol: 'BTC/USDT',
          timeframe: '1d',
          template_name: 'multi_ma_crossover',
          name: 'BTC Trend',
          notes: '',
          tier: 1,
          parameters: { direction: 'long', ema_short: 18, sma_medium: 20, sma_long: 35, stop_loss: 0.042 },
          indicator_values: {
            short: 71346.57,
            medium: 69796.7,
            long: 70294.6,
            open: 74131.55,
            close: 74809.99,
          },
          indicator_values_candle_time: '2099-04-15T00:00:00+00:00',
          is_holding: false,
          distance_to_next_status: 2.22,
          next_status_label: 'entry',
          status: 'EXIT_SIGNAL',
          message: '',
          last_price: 74924,
          timestamp: '2026-04-16T04:00:00Z',
          details: {},
        },
      ]),
    })
  )

  await page.route('**/api/monitor/preferences', (route: any) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        __global__: { in_portfolio: false, card_mode: 'strategy', price_timeframe: '1d', theme: 'dark-green' },
        'BTC/USDT': { in_portfolio: true, card_mode: 'strategy', price_timeframe: '1h', theme: 'dark-green' },
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
          { timestamp_utc: '2026-04-16T01:00:00Z', open: 74850, high: 74910, low: 74790, close: 74880, volume: 82.413 },
          { timestamp_utc: '2026-04-16T02:00:00Z', open: 74880, high: 74940, low: 74820, close: 74895, volume: 91.127 },
          { timestamp_utc: '2026-04-16T03:00:00Z', open: 74895, high: 75005, low: 74865, close: 74905, volume: 104.252 },
          { timestamp_utc: '2026-04-16T04:00:00Z', open: 74905, high: 75010, low: 74839, close: 74930.98, volume: 112.613 },
        ],
      }),
    })
  )

  await page.goto('/monitor')

  const card = page.getByTestId('monitor-card-btc-usdt')
  await expect(card).toBeVisible()
  await expect(card.getByText('Venda', { exact: true })).toBeVisible()
  await card.getByRole('button', { name: 'Abrir Gráfico' }).click()

  const dialog = page.getByRole('dialog')
  await expect(dialog).toBeVisible()
  await expect(dialog.getByRole('button', { name: 'Compacto' })).toHaveCount(0)
  await expect(dialog.getByRole('button', { name: 'Algorítmica', exact: true })).toHaveCount(0)
  await expect(dialog.getByTestId('chart-modal-main-chart')).toBeVisible()
  await expect(dialog.getByTestId('chart-modal-strategy-summary')).toHaveCount(0)
  await expect(dialog.getByTestId('chart-modal-signal-context')).toHaveCount(0)
  await expect(dialog.getByTestId('chart-modal-trades')).toHaveCount(0)
  await expect(dialog.getByText('Lista de trades')).toHaveCount(0)
  await expect(page.getByTestId('chart-modal-signal-badge')).toHaveText('Venda')
})

test('monitor keeps Compra in chart detail while showing holding context mismatch', async ({ page }) => {
  await mockAuthenticatedSession(page)

  await page.route('**/*', (route: any) => {
    const url = new URL(route.request().url())
    if (url.hostname === '127.0.0.1' || url.hostname === 'localhost') {
      return route.continue()
    }
    return route.abort('blockedbyclient')
  })

  await page.route('**/api/auth/me', (route: any) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(AUTH_USER),
    })
  )

  await page.route('**/api/favorites/', (route: any) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify([
        {
          id: 7,
          name: 'SOL Compra',
          symbol: 'SOL/USDT',
          timeframe: '1d',
          strategy_name: 'multi_ma_crossover',
          parameters: {},
          metrics: {},
          created_at: '2099-04-01T00:00:00Z',
          tier: 1,
        },
      ]),
    })
  )

  await page.route('**/api/opportunities/**', (route: any) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify([
        {
          id: 7,
          symbol: 'SOL/USDT',
          timeframe: '1d',
          template_name: 'multi_ma_crossover',
          name: 'SOL Compra',
          notes: '',
          tier: 1,
          parameters: { direction: 'long', ema_short: 18, sma_medium: 20, sma_long: 35, stop_loss: 0.042 },
          indicator_values_candle_time: '2099-04-16T00:00:00+00:00',
          is_holding: true,
          distance_to_next_status: 0.41,
          distance_to_stop_pct: 14.18,
          next_status_label: 'exit',
          status: 'HOLDING',
          message: 'Em Hold. Distância para saída: 0.41%',
          entry_price: 142.1,
          stop_price: 121.95,
          last_price: 151.24,
          timestamp: '2099-04-16T00:00:00Z',
          signal_history: [
            { timestamp: '2099-04-10T00:00:00+00:00', signal: 1, type: 'entry', reason: 'entry', price: 142.1 },
          ],
          details: {},
        },
      ]),
    })
  )

  await page.route('**/api/monitor/preferences', (route: any) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        __global__: { in_portfolio: false, card_mode: 'strategy', price_timeframe: '1d', theme: 'dark-green' },
        'SOL/USDT': { in_portfolio: true, card_mode: 'strategy', price_timeframe: '1d', theme: 'dark-green' },
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
          { timestamp_utc: '2099-04-14T00:00:00Z', open: 149, high: 152, low: 147, close: 151, volume: 1000 },
          { timestamp_utc: '2099-04-15T00:00:00Z', open: 151, high: 154, low: 150, close: 151.24, volume: 1000 },
        ],
      }),
    })
  )

  await page.goto('/monitor')

  const card = page.getByTestId('monitor-card-sol-usdt')
  await expect(card).toBeVisible()
  await expect(card.getByText('Compra', { exact: true })).toBeVisible()
  await card.getByRole('button', { name: 'Abrir Gráfico' }).click()

  const dialog = page.getByRole('dialog')
  await expect(dialog).toBeVisible()
  await expect(dialog.getByTestId('chart-modal-signal-badge')).toHaveText('Compra')
  await expect(dialog.getByTestId('chart-modal-main-chart-shell')).toHaveAttribute('data-current-marker', 'Compra')
  await expect(dialog.getByRole('button', { name: 'Compacto' })).toHaveCount(0)
  await expect(dialog.getByRole('button', { name: 'Algorítmica', exact: true })).toHaveCount(0)
  await expect(dialog.getByTestId('chart-modal-main-chart')).toBeVisible()
  await expect(dialog.getByTestId('chart-modal-signal-context')).toHaveCount(0)
  await expect(dialog.getByTestId('chart-modal-trades')).toHaveCount(0)
  await expect(dialog.getByRole('group', { name: 'Chart indicators' })).toHaveCount(0)
  await expect(dialog.getByText('Indicators')).toHaveCount(0)
  await expect(dialog.getByText(/EMA 9|SMA 21|SMA 50/)).toHaveCount(0)
})

test('monitor adds current sell marker when history only has prior entry', async ({ page }) => {
  await mockAuthenticatedSession(page)

  await page.route('**/*', (route: any) => {
    const url = new URL(route.request().url())
    if (url.hostname === '127.0.0.1' || url.hostname === 'localhost') {
      return route.continue()
    }
    return route.abort('blockedbyclient')
  })

  await page.route('**/api/auth/me', (route: any) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(AUTH_USER),
    })
  )

  await page.route('**/api/favorites/', (route: any) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify([
        {
          id: 2,
          name: 'HBAR Trend',
          symbol: 'HBAR/USDT',
          timeframe: '1d',
          strategy_name: 'multi_ma_crossover',
          parameters: {},
          metrics: {},
          created_at: '2026-04-15T00:00:00Z',
          tier: 1,
        },
      ]),
    })
  )

  await page.route('**/api/opportunities/**', (route: any) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify([
        {
          id: 2,
          symbol: 'HBAR/USDT',
          timeframe: '1d',
          template_name: 'multi_ma_crossover',
          name: 'HBAR Trend',
          notes: '',
          tier: 1,
          parameters: { direction: 'long', ema_short: 18, sma_medium: 20, sma_long: 35, stop_loss: 0.042 },
          indicator_values: {
            short: 0.08888,
            medium: 0.08911,
            long: 0.08889,
            open: 0.08771,
            close: 0.08773,
          },
          indicator_values_candle_time: '2026-05-19T00:00:00+00:00',
          is_holding: false,
          distance_to_next_status: 0,
          next_status_label: 'exit',
          status: 'EXIT',
          message: 'Venda/fora de posicao. Aguardando proxima compra.',
          last_price: 0.08877,
          timestamp: '2026-05-20T00:00:00Z',
          signal_history: [
            { timestamp: '2026-05-09T00:00:00+00:00', signal: 1, type: 'entry', reason: 'entry', price: 0.0927 },
          ],
          details: {},
        },
      ]),
    })
  )

  await page.route('**/api/monitor/preferences', (route: any) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        __global__: { in_portfolio: false, card_mode: 'strategy', price_timeframe: '1d', theme: 'dark-green' },
        'HBAR/USDT': { in_portfolio: true, card_mode: 'strategy', price_timeframe: '1d', theme: 'dark-green' },
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
          { timestamp_utc: '2026-05-09T00:00:00Z', open: 0.0927, high: 0.094, low: 0.091, close: 0.0932, volume: 1000 },
          { timestamp_utc: '2026-05-19T00:00:00Z', open: 0.089, high: 0.09, low: 0.088, close: 0.08877, volume: 1000 },
          { timestamp_utc: '2026-05-20T00:00:00Z', open: 0.08877, high: 0.0895, low: 0.0875, close: 0.08812, volume: 1000 },
        ],
      }),
    })
  )

  await page.goto('/monitor')

  const card = page.getByTestId('monitor-card-hbar-usdt')
  await expect(card).toBeVisible()
  await expect(card.getByText('Venda', { exact: true })).toBeVisible()
  await card.getByRole('button', { name: 'Abrir Gráfico' }).click()

  const dialog = page.getByRole('dialog')
  await expect(dialog).toBeVisible()
  await expect(dialog.getByRole('button', { name: 'Compacto' })).toHaveCount(0)
  await expect(dialog.getByRole('button', { name: 'Algorítmica', exact: true })).toHaveCount(0)
  await expect(dialog.getByTestId('chart-modal-main-chart')).toBeVisible()
  await expect(dialog.getByTestId('chart-modal-strategy-summary')).toHaveCount(0)
  await expect(page.getByTestId('chart-modal-signal-badge')).toHaveText('Venda')
  await expect(dialog.getByTestId('chart-modal-main-chart-shell')).toHaveAttribute('data-current-marker', 'Venda')
  await expect(dialog.getByTestId('chart-modal-surface')).toHaveAttribute('data-marker-count', '2')
})

test('monitor uses favorite trade markers without duplicating the current sell marker', async ({ page }) => {
  await mockAuthenticatedSession(page)

  await page.route('**/*', (route: any) => {
    const url = new URL(route.request().url())
    if (url.hostname === '127.0.0.1' || url.hostname === 'localhost') {
      return route.continue()
    }
    return route.abort('blockedbyclient')
  })

  await page.route('**/api/auth/me', (route: any) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(AUTH_USER),
    })
  )

  await page.route('**/api/favorites/', (route: any) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify([
        {
          id: 8,
          name: 'HBAR Trend',
          symbol: 'HBAR/USDT',
          timeframe: '1d',
          strategy_name: 'multi_ma_crossover',
          parameters: {},
          metrics: {},
          created_at: '2026-04-15T00:00:00Z',
          tier: 1,
        },
      ]),
    })
  )

  await page.route('**/api/opportunities/**', (route: any) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify([
        {
          id: 8,
          symbol: 'HBAR/USDT',
          timeframe: '1d',
          template_name: 'multi_ma_crossover',
          name: 'HBAR Trend',
          notes: '',
          tier: 1,
          parameters: { direction: 'long', ema_short: 18, sma_medium: 20, sma_long: 35, stop_loss: 0.042 },
          indicator_values_candle_time: '2026-05-20T00:00:00+00:00',
          is_holding: false,
          distance_to_next_status: 0,
          next_status_label: 'exit',
          status: 'EXIT',
          message: 'Venda/fora de posicao. Aguardando proxima compra.',
          last_price: 0.08877,
          timestamp: '2026-05-20T00:00:00Z',
          signal_history: [
            { timestamp: '2026-05-09T00:00:00+00:00', signal: 1, type: 'entry', reason: 'entry', price: 0.0927 },
          ],
          details: {},
        },
      ]),
    })
  )

  await page.route('**/api/favorites/8/trades', (route: any) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        favorite_id: 8,
        trades: [
          {
            entry_time: '2026-04-01T00:00:00+00:00',
            entry_price: 0.08,
            exit_time: '2026-04-10T00:00:00+00:00',
            exit_price: 0.09,
            profit: 0.125,
            type: 'long',
          },
          {
            entry_time: '2026-05-09T00:00:00+00:00',
            entry_price: 0.0927,
            exit_time: '2026-05-20T00:00:00+00:00',
            exit_price: 0.08877,
            profit: -0.0438,
            type: 'long',
          },
        ],
        metrics: { total_trades: 2 },
        candles: [
          { timestamp_utc: '2026-04-01T00:00:00Z', open: 0.08, high: 0.083, low: 0.079, close: 0.082, volume: 1000 },
          { timestamp_utc: '2026-04-10T00:00:00Z', open: 0.09, high: 0.094, low: 0.088, close: 0.091, volume: 1000 },
          { timestamp_utc: '2026-05-09T00:00:00Z', open: 0.0927, high: 0.094, low: 0.091, close: 0.0932, volume: 1000 },
          { timestamp_utc: '2026-05-20T00:00:00Z', open: 0.08877, high: 0.0895, low: 0.0875, close: 0.08812, volume: 1000 },
        ],
        indicator_data: {},
        regenerated: false,
        execution_mode: 'deep_15m',
      }),
    })
  )

  await page.route('**/api/monitor/preferences', (route: any) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        __global__: { in_portfolio: false, card_mode: 'strategy', price_timeframe: '1d', theme: 'dark-green' },
        'HBAR/USDT': { in_portfolio: true, card_mode: 'strategy', price_timeframe: '1d', theme: 'dark-green' },
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
          { timestamp_utc: '2026-05-20T00:00:00Z', open: 0.08877, high: 0.0895, low: 0.0875, close: 0.08812, volume: 1000 },
        ],
      }),
    })
  )

  await page.goto('/monitor')

  const card = page.getByTestId('monitor-card-hbar-usdt')
  await expect(card).toBeVisible()
  await card.getByRole('button', { name: 'Abrir Gráfico' }).click()

  const dialog = page.getByRole('dialog')
  await expect(dialog).toBeVisible()
  await expect(dialog.getByTestId('chart-modal-surface')).toHaveAttribute('data-marker-count', '4')
  await expect(dialog.getByTestId('chart-modal-surface')).toHaveAttribute('data-marker-labels', /COMPRA.*VENDA/);
  await expect(dialog.getByTestId('chart-modal-surface')).not.toHaveAttribute('data-marker-labels', /BUY|SELL|SHORT|COVER/);
  await expect(dialog.locator('header p').first()).toContainText('4 candles')
})

test('monitor modal shows recent entry and exit history from the strategy payload', async ({ page }) => {
  await mockAuthenticatedSession(page)

  await page.route('**/*', (route: any) => {
    const url = new URL(route.request().url())
    if (url.hostname === '127.0.0.1' || url.hostname === 'localhost') {
      return route.continue()
    }
    return route.abort('blockedbyclient')
  })

  await page.route('**/api/auth/me', (route: any) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(AUTH_USER),
    })
  )

  await page.route('**/api/favorites/', (route: any) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify([
        {
          id: 5,
          name: 'BTC Trend History',
          symbol: 'BTC/USDT',
          timeframe: '1d',
          strategy_name: 'multi_ma_crossover',
          parameters: {},
          metrics: {},
          created_at: '2026-04-01T00:00:00Z',
          tier: 1,
        },
      ]),
    })
  )

  await page.route('**/api/opportunities/**', (route: any) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify([
        {
          id: 5,
          symbol: 'BTC/USDT',
          timeframe: '1d',
          template_name: 'multi_ma_crossover',
          name: 'BTC Trend History',
          notes: '',
          tier: 1,
          parameters: { direction: 'long', ema_short: 18, sma_medium: 20, sma_long: 35, stop_loss: 0.042 },
          indicator_values: {
            short: 71346.57,
            medium: 69796.7,
            long: 70294.6,
            open: 74131.55,
            close: 74809.99,
          },
          indicator_values_candle_time: '2099-04-15T00:00:00+00:00',
          is_holding: true,
          distance_to_next_status: 0.88,
          next_status_label: 'exit',
          status: 'HOLDING',
          message: 'Em Hold. Distância para saída: 0.88%',
          last_price: 74924,
          timestamp: '2099-04-16T00:00:00Z',
          signal_history: [
            { timestamp: '2099-04-10T00:00:00+00:00', signal: 1, type: 'entry', reason: 'entry', price: 70210.15 },
            { timestamp: '2099-04-13T00:00:00+00:00', signal: -1, type: 'exit', reason: 'exit_logic', price: 72150.42 },
            { timestamp: '2099-04-15T00:00:00+00:00', signal: 1, type: 'entry', reason: 'entry', price: 73980.37 },
          ],
          details: {},
        },
      ]),
    })
  )

  await page.route('**/api/monitor/preferences', (route: any) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        __global__: { in_portfolio: false, card_mode: 'strategy', price_timeframe: '1d', theme: 'dark-green' },
        'BTC/USDT': { in_portfolio: true, card_mode: 'strategy', price_timeframe: '1d', theme: 'dark-green' },
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
          { timestamp_utc: '2099-04-09T00:00:00Z', open: 69500, high: 70400, low: 69000, close: 70100, volume: 82.413 },
          { timestamp_utc: '2099-04-10T00:00:00Z', open: 70210.15, high: 71000, low: 70050, close: 70880, volume: 91.127 },
          { timestamp_utc: '2099-04-11T00:00:00Z', open: 70880, high: 71510, low: 70520, close: 71210, volume: 94.321 },
          { timestamp_utc: '2099-04-12T00:00:00Z', open: 71210, high: 72300, low: 71050, close: 72020, volume: 99.654 },
          { timestamp_utc: '2099-04-13T00:00:00Z', open: 72150.42, high: 72440, low: 71500, close: 71720, volume: 103.552 },
          { timestamp_utc: '2099-04-14T00:00:00Z', open: 71720, high: 74120, low: 71610, close: 73910, volume: 108.117 },
          { timestamp_utc: '2099-04-15T00:00:00Z', open: 73980.37, high: 74980, low: 73800, close: 74809.99, volume: 112.613 },
        ],
      }),
    })
  )

  await page.goto('/monitor')

  const card = page.getByTestId('monitor-card-btc-usdt')
  await expect(card).toBeVisible()
  await card.getByRole('button', { name: 'Ver Trades' }).click()

  const dialog = page.getByRole('dialog')
  await expect(dialog).toBeVisible()
  await expect(dialog.getByRole('button', { name: 'Compacto' })).toHaveCount(0)
  await expect(dialog.getByRole('button', { name: 'Algorítmica', exact: true })).toHaveCount(0)
  await expect(dialog.getByTestId('chart-modal-main-chart')).toBeVisible()
  await expect(dialog.getByTestId('chart-modal-signal-history')).toBeVisible()
  await expect(dialog.getByTestId('chart-modal-trades')).toBeVisible()
  await expect(dialog.getByText('Lista de trades')).toBeVisible()
  await expect(dialog.getByRole('columnheader', { name: 'Valor da posicao' })).toBeVisible()
  await expect(dialog.getByText('100.00 USD').first()).toBeVisible()
  await expect(dialog.getByText('Apr 10, 2099')).toBeVisible()
  await expect(dialog.getByText('Apr 13, 2099')).toBeVisible()
  await page.waitForTimeout(1500)
  await expect(dialog.getByTestId('chart-modal-main-chart')).toBeVisible()
  await expect(dialog.getByTestId('chart-modal-main-chart').locator('canvas').first()).toBeVisible()
  await expect(dialog.getByTestId('chart-modal-signal-badge')).toHaveText('Compra')
  await expect(dialog.getByTestId('chart-modal-main-chart-shell')).toHaveAttribute('data-current-marker', 'Compra')
})

test('monitor modal zoom controls adjust visible range without reloading candles', async ({ page }) => {
  await mockAuthenticatedSession(page)

  await page.route('**/*', (route: any) => {
    const url = new URL(route.request().url())
    if (url.hostname === '127.0.0.1' || url.hostname === 'localhost') {
      return route.continue()
    }
    return route.abort('blockedbyclient')
  })

  await page.route('**/api/auth/me', (route: any) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(AUTH_USER),
    })
  )

  await page.route('**/api/favorites/', (route: any) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify([
        {
          id: 6,
          name: 'BTC Zoom Test',
          symbol: 'BTC/USDT',
          timeframe: '1d',
          strategy_name: 'multi_ma_crossover',
          parameters: {},
          metrics: {},
          created_at: '2026-04-01T00:00:00Z',
          tier: 1,
        },
      ]),
    })
  )

  await page.route('**/api/opportunities/**', (route: any) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify([
        {
          id: 6,
          symbol: 'BTC/USDT',
          timeframe: '1d',
          template_name: 'multi_ma_crossover',
          name: 'BTC Zoom Test',
          notes: '',
          tier: 1,
          parameters: { direction: 'long', ema_short: 9, sma_medium: 21, sma_long: 50, stop_loss: 0.035, data_source: 'ccxt', rsi_period: 14 },
          indicator_values: {
            ema_9: 73210.5,
            sma_21: 72654.8,
            sma_50: 71892.3,
            rsi_14: 58.4,
            close: 73420.2,
          },
          indicator_values_candle_time: '2026-04-20T00:00:00+00:00',
          is_holding: true,
          distance_to_next_status: 0.44,
          next_status_label: 'exit',
          status: 'HOLDING',
          message: 'Holding position',
          last_price: 73420.2,
          timestamp: '2026-04-20T00:00:00Z',
          details: {},
        },
      ]),
    })
  )

  await page.route('**/api/monitor/preferences', (route: any) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        __global__: { in_portfolio: false, card_mode: 'strategy', price_timeframe: '1d', theme: 'dark-green' },
        'BTC/USDT': { in_portfolio: true, card_mode: 'strategy', price_timeframe: '1d', theme: 'dark-green' },
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

  const candles = Array.from({ length: 24 }, (_, index) => {
    const base = 70000 + (index * 120)
    return {
      timestamp_utc: new Date(Date.UTC(2026, 3, index + 1, 0, 0, 0)).toISOString(),
      open: base,
      high: base + 85,
      low: base - 75,
      close: base + ((index % 2 === 0) ? 40 : -35),
      volume: 100 + (index * 3.5),
    }
  })

  let candleRequestCount = 0
  await page.route('**/api/market/candles**', (route: any) => {
    candleRequestCount += 1
    return route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ candles }),
    })
  })

  await page.goto('/monitor')

  const card = page.getByTestId('monitor-card-btc-usdt')
  await expect(card).toBeVisible()
  await card.getByRole('button', { name: 'Ver Trades' }).click()

  const dialog = page.getByRole('dialog')
  await expect(dialog).toBeVisible()
  const parameters = dialog.locator('section').filter({ hasText: 'Parametros' }).last()
  await expect(parameters.getByText('Direção')).toBeVisible()
  await expect(parameters.getByText('Compra')).toBeVisible()
  await expect(parameters.getByText('EMA curta')).toBeVisible()
  await expect(parameters.getByText('SMA média')).toBeVisible()
  await expect(parameters.getByText('SMA longa')).toBeVisible()
  await expect(parameters.getByText('Stop de perda')).toBeVisible()
  await expect(parameters.getByText('3.50%')).toBeVisible()
  await expect(parameters.getByText('Fonte de dados')).toBeVisible()
  await expect(parameters.getByText('CCXT')).toBeVisible()
  await expect(parameters.getByText('direction')).toHaveCount(0)
  await expect(parameters.getByText('ema_short')).toHaveCount(0)
  await expect(parameters.getByText('sma_medium')).toHaveCount(0)
  await expect(parameters.getByText('sma_long')).toHaveCount(0)
  await expect(parameters.getByText('stop_loss')).toHaveCount(0)
  await expect(parameters.getByText('data_source')).toHaveCount(0)
  await expect(page.getByTestId('chart-zoom-in')).toBeVisible()
  await expect(page.getByTestId('chart-zoom-out')).toBeVisible()
  await expect(page.getByTestId('chart-zoom-reset')).toBeVisible()
  await expect(dialog.getByText('Roda do mouse: zoom')).toBeVisible()

  const visibleBars = page.getByTestId('chart-visible-bars')
  const readVisibleBars = async () => {
    const raw = (await visibleBars.textContent()) ?? '0'
    return Number.parseInt(raw, 10)
  }

  await expect.poll(readVisibleBars).toBeGreaterThan(0)
  const initialVisibleBars = await readVisibleBars()

  await page.getByTestId('chart-zoom-in').click()
  await expect.poll(readVisibleBars).toBeLessThan(initialVisibleBars)
  const zoomedInVisibleBars = await readVisibleBars()

  await page.getByTestId('chart-zoom-out').focus()
  await page.keyboard.press('Enter')
  await expect.poll(readVisibleBars).toBeGreaterThan(zoomedInVisibleBars)
  const zoomedOutVisibleBars = await readVisibleBars()

  await page.getByTestId('chart-modal-main-chart-shell').hover()
  await page.mouse.wheel(0, -600)
  await expect.poll(readVisibleBars).toBeLessThan(zoomedOutVisibleBars)

  expect(candleRequestCount).toBe(1)
})
