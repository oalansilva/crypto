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
    name: 'NVDA Trend',
    symbol: 'NVDA',
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
    symbol: 'NVDA',
    timeframe: '1d',
    template_name: 'ema_rsi',
    name: 'NVDA Trend',
    notes: '',
    tier: 1,
    parameters: { ema_short: 9, ema_long: 21 },
    is_holding: false,
    distance_to_next_status: 0.5,
    next_status_label: 'entry',
    status: 'WAIT',
    message: 'Waiting for entry',
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
        NVDA: { in_portfolio: true, card_mode: 'price', price_timeframe: '1d', theme: 'dark-green' },
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
}

test.use({ viewport: { width: 390, height: 844 } })

test('monitor mobile uses single cards view and stock timeframe buttons are constrained to 1d', async ({ page }) => {
  await setupApiMocks(page)
  await page.goto('/monitor')

  await expect(page.getByTestId('monitor-card-nvda')).toBeVisible()
  await expect(page.getByTestId('timeframe-toggle-nvda-1d')).toHaveAttribute('aria-pressed', 'true')
  await expect(page.getByTestId('timeframe-toggle-nvda-15m')).toBeDisabled()
  await expect(page.getByTestId('timeframe-toggle-nvda-1h')).toBeDisabled()
  await expect(page.getByTestId('timeframe-toggle-nvda-4h')).toBeDisabled()
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
          is_holding: false,
          distance_to_next_status: 0.5,
          next_status_label: 'entry',
          status: 'WAIT',
          message: 'Waiting for entry',
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
          name: 'BTC Exit',
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
          name: 'BTC Exit',
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

  await expect(page.getByText('Estado EXIT')).toBeVisible()
  await expect(page.getByTestId('monitor-card-btc-usdt').getByText(/^EXIT$/)).toBeVisible()
})

test('monitor keeps mismatched exit signals in WAIT state with explicit context', async ({ page }) => {
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
          indicator_values_candle_time: '2026-04-15T00:00:00+00:00',
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
  await expect(card.getByText('WAIT', { exact: true })).toBeVisible()
  await expect(card).toContainText('Estado em revisão: decisão não confirmada pelo contexto atual.')
  await expect(card).toContainText('EXIT bloqueado: timeframe da estratégia não corresponde ao timeframe exibido.')
  await expect(card.getByText('Estado: WAIT')).toBeVisible()
  await expect(card.getByText('strategy tf: 1d')).toBeVisible()
  await expect(card.getByText('display tf: 1h')).toBeVisible()

  await card.click()

  const dialog = page.getByRole('dialog')
  await expect(dialog).toBeVisible()
  await dialog.getByRole('button', { name: 'Compacto' }).click()
  await expect(page.getByTestId('chart-modal-signal-badge')).toHaveText('WAIT')
  await expect(dialog.getByText('Resolved state')).toBeVisible()
  await expect(dialog).toContainText('1d')
  await expect(dialog).toContainText('1h')
  await expect(dialog).toContainText('Estado em revisão: decisão não confirmada pelo contexto atual.')
  await expect(dialog).toContainText('EXIT bloqueado: candle de referência não corresponde ao último candle exibido.')
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
          indicator_values_candle_time: '2026-04-15T00:00:00+00:00',
          is_holding: true,
          distance_to_next_status: 0.88,
          next_status_label: 'exit',
          status: 'HOLDING',
          message: 'Em Hold. Distância para saída: 0.88%',
          last_price: 74924,
          timestamp: '2026-04-16T00:00:00Z',
          signal_history: [
            { timestamp: '2026-04-10T00:00:00+00:00', signal: 1, type: 'entry', reason: 'entry', price: 70210.15 },
            { timestamp: '2026-04-13T00:00:00+00:00', signal: -1, type: 'exit', reason: 'exit_logic', price: 72150.42 },
            { timestamp: '2026-04-15T00:00:00+00:00', signal: 1, type: 'entry', reason: 'entry', price: 73980.37 },
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
          { timestamp_utc: '2026-04-09T00:00:00Z', open: 69500, high: 70400, low: 69000, close: 70100, volume: 82.413 },
          { timestamp_utc: '2026-04-10T00:00:00Z', open: 70210.15, high: 71000, low: 70050, close: 70880, volume: 91.127 },
          { timestamp_utc: '2026-04-11T00:00:00Z', open: 70880, high: 71510, low: 70520, close: 71210, volume: 94.321 },
          { timestamp_utc: '2026-04-12T00:00:00Z', open: 71210, high: 72300, low: 71050, close: 72020, volume: 99.654 },
          { timestamp_utc: '2026-04-13T00:00:00Z', open: 72150.42, high: 72440, low: 71500, close: 71720, volume: 103.552 },
          { timestamp_utc: '2026-04-14T00:00:00Z', open: 71720, high: 74120, low: 71610, close: 73910, volume: 108.117 },
          { timestamp_utc: '2026-04-15T00:00:00Z', open: 73980.37, high: 74980, low: 73800, close: 74809.99, volume: 112.613 },
        ],
      }),
    })
  )

  await page.goto('/monitor')

  const card = page.getByTestId('monitor-card-btc-usdt')
  await expect(card).toBeVisible()
  await card.click()

  const dialog = page.getByRole('dialog')
  await expect(dialog).toBeVisible()
  await dialog.getByRole('button', { name: 'Compacto' }).click()
  await expect(dialog.getByText('Signal History')).toBeVisible()
  await expect(dialog.getByTestId('chart-modal-signal-history')).toBeVisible()
  await expect(dialog.getByTestId('chart-modal-signal-history-item-0')).toContainText('ENTRY')
  await expect(dialog.getByTestId('chart-modal-signal-history-item-1')).toContainText('EXIT')
  await expect(dialog.getByText('Markers aligned with chart timeframe.')).toBeVisible()
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
          parameters: { direction: 'long', ema_short: 9, sma_medium: 21, sma_long: 50, rsi_period: 14 },
          indicator_values: {
            ema_9: 73210.5,
            sma_21: 72654.8,
            sma_50: 71892.3,
            rsi_14: 58.4,
            close: 73420.2,
          },
          indicator_values_candle_time: '2026-04-20T00:00:00+00:00',
          is_holding: false,
          distance_to_next_status: 0.44,
          next_status_label: 'entry',
          status: 'WAIT',
          message: 'Waiting for entry',
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
  await card.click()

  const dialog = page.getByRole('dialog')
  await expect(dialog).toBeVisible()
  await expect(page.getByTestId('chart-zoom-in')).toBeVisible()
  await expect(page.getByTestId('chart-zoom-out')).toBeVisible()
  await expect(page.getByTestId('chart-zoom-reset')).toBeVisible()
  await expect(dialog.getByText('Mouse wheel: zoom')).toBeVisible()

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
