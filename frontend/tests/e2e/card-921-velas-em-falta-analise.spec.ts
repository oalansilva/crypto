import { expect, test, type Page } from '@playwright/test'

const STALE_LAST = '2026-08-15T00:00:00.000Z'
const MARKET_LAST = '2026-09-12T00:00:00.000Z'

function buildDailyCandles(untilIso: string, startIso = '2026-01-01T00:00:00.000Z') {
  const start = Date.parse(startIso)
  const end = Date.parse(untilIso)
  const step = 86_400_000
  const count = Math.floor((end - start) / step) + 1
  return Array.from({ length: count }, (_, index) => {
    const timestamp = start + index * step
    const open = 40_000 + index * 50
    const close = open + (index % 2 === 0 ? 80 : -40)
    return {
      timestamp_utc: new Date(timestamp).toISOString(),
      open,
      high: Math.max(open, close) + 120,
      low: Math.min(open, close) - 120,
      close,
      volume: 5000 + index,
    }
  })
}

const STALE_CANDLES = buildDailyCandles(STALE_LAST)
const MARKET_CANDLES = buildDailyCandles(MARKET_LAST)

const transparencyWithFutureMa = {
  status: 'available',
  timeframe: '1d',
  display_name: 'Médias Móveis',
  indicators: [{
    key: 'short',
    type: 'ema',
    label: 'EMA curta',
    panel: 'price',
    color: '#f6465d',
    parameters: { length: 16 },
    participation: ['entry'],
    references: [],
    series_status: 'available',
    series: MARKET_CANDLES.map((candle, index) => ({
      timestamp_utc: candle.timestamp_utc,
      value: 39_000 + index * 40,
    })),
  }],
}

const ANALYSIS_RESULT = {
  template_name: 'multi_ma_crossover',
  symbol: 'BTC/USDT',
  timeframe: '1d',
  parameters: { direction: 'long' },
  metrics: { total_trades: 2, win_rate: 0.5, total_return: 0.1, avg_profit: 0.05 },
  trades: [
    {
      entry_time: STALE_CANDLES.at(-5)!.timestamp_utc,
      entry_price: 42_000,
      exit_time: STALE_CANDLES.at(-2)!.timestamp_utc,
      exit_price: 43_000,
      profit: 0.02,
      type: 'long',
    },
  ],
  indicator_data: {},
  candles: STALE_CANDLES,
  strategy_transparency: transparencyWithFutureMa,
  direction: 'long',
}

async function seedComboResults(page: Page) {
  await page.addInitScript(() => {
    window.localStorage.setItem('auth_access_token', 'test-access-token')
    window.localStorage.setItem('auth_refresh_token', 'test-refresh-token')
    window.localStorage.setItem('auth_user', JSON.stringify({
      id: 'card-921-user',
      email: 'trader@example.com',
      name: 'Trader',
      isAdmin: false,
    }))
  })

  await page.route('**/api/market/candles**', async (route) => {
    const url = new URL(route.request().url())
    const fullHistory = url.searchParams.get('full_history') === 'true'
    const candles = fullHistory ? MARKET_CANDLES : STALE_CANDLES.slice(-300)
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ candles, canonical_candles: true }),
    })
  })

  await page.goto('/combo/results')
  await page.evaluate((result) => {
    history.replaceState(
      { usr: { result, returnTo: '/favorites' }, key: 'card-921', idx: 0 },
      '',
      location.href,
    )
  }, ANALYSIS_RESULT)
  await page.reload()
  await expect(page.locator('.combo-page')).toBeVisible()
}

async function assertAlignedChart(page: Page) {
  const chart = page.getByTestId('monitor-aligned-result-chart')
  await expect(chart).toBeVisible()
  await expect.poll(async () => chart.getAttribute('data-ma-ahead'), { timeout: 15_000 }).toBe('0')
  await expect.poll(async () => chart.getAttribute('data-last-candle-timestamp'), { timeout: 15_000 }).toContain('2026-09-12')
  const lastMa = await chart.getAttribute('data-last-ma-timestamp')
  const lastCandle = await chart.getAttribute('data-last-candle-timestamp')
  expect(lastMa?.slice(0, 10)).toBe(lastCandle?.slice(0, 10))
}

async function seedMonitorChart(page: Page) {
  await page.addInitScript(() => {
    window.localStorage.setItem('auth_access_token', 'test-access-token')
    window.localStorage.setItem('auth_refresh_token', 'test-refresh-token')
    window.localStorage.setItem('auth_user', JSON.stringify({
      id: 'card-921-user',
      email: 'trader@example.com',
      name: 'Trader',
      isAdmin: false,
    }))
  })

  await page.route('**/*', (route) => {
    const url = new URL(route.request().url())
    if (url.hostname === '127.0.0.1' || url.hostname === 'localhost') {
      return route.continue()
    }
    return route.abort('blockedbyclient')
  })

  await page.route('**/api/favorites/**', async (route) => {
    await route.fulfill({ status: 200, contentType: 'application/json', body: '[]' })
  })

  await page.route('**/api/auth/me', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        id: 'card-921-user',
        email: 'trader@example.com',
        name: 'Trader',
        isAdmin: false,
      }),
    })
  })

  await page.route('**/api/monitor/preferences', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        __global__: { in_portfolio: false, card_mode: 'price', price_timeframe: '1d', theme: 'dark-green' },
        'BTC/USDT': { in_portfolio: true, card_mode: 'price', price_timeframe: '1d', theme: 'dark-green' },
      }),
    })
  })

  await page.route('**/api/user/binance-credentials', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ configured: false, api_key_masked: null }),
    })
  })

  await page.route('**/api/market/candles**', async (route) => {
    const url = new URL(route.request().url())
    const timeframe = url.searchParams.get('timeframe') || '1d'
    const candles = buildDailyCandles(MARKET_LAST).map((candle) => ({ ...candle, timeframe }))
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ candles, canonical_candles: true }),
    })
  })

  await page.route('**/api/opportunities**', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify([{
        id: 921,
        symbol: 'BTC/USDT',
        timeframe: '1d',
        template_name: 'multi_ma_crossover',
        strategy_display_name: 'Médias Móveis',
        strategy_description: 'Teste card 921',
        strategy_transparency: transparencyWithFutureMa,
        is_strategy_protected: false,
        name: 'BTC Monitor',
        notes: '',
        tier: 1,
        parameters: {},
        is_holding: true,
        distance_to_next_status: 0.5,
        next_status_label: 'exit',
        status: 'HOLDING',
        message: 'Posição ativa',
        last_price: 95_000,
        timestamp: MARKET_LAST,
        indicator_values_candle_time: STALE_LAST,
        signal_history: [],
        details: {},
      }]),
    })
  })

  await page.goto('/monitor')
  const cardButton = page.getByTestId('monitor-card-btc-usdt').getByRole('button', { name: 'Abrir Gráfico' })
  if (await cardButton.count()) {
    await cardButton.click()
  } else {
    await page.getByRole('button', { name: /Abrir Gráfico BTC\/USDT/i }).first().click()
  }
  await expect(page.getByTestId('chart-modal')).toBeVisible()
}

async function assertMonitorAlignedChart(page: Page) {
  const dialog = page.getByTestId('chart-modal')
  const chart = dialog.getByTestId('chart-modal-surface')
  await expect(chart).toBeVisible()
  await expect.poll(async () => chart.getAttribute('data-ma-ahead'), { timeout: 15_000 }).toBe('0')
  for (const timeframe of ['15m', '1h', '4h', '1d']) {
    await dialog.getByTestId(`chart-timeframe-${timeframe}`).click()
    await expect.poll(async () => chart.getAttribute('data-ma-ahead'), { timeout: 15_000 }).toBe('0')
  }
}

test.describe('card-921 velas e médias alinhadas', () => {
  test('desktop /combo/results alinha média à última vela de mercado', async ({ page }) => {
    await page.setViewportSize({ width: 1440, height: 900 })
    await seedComboResults(page)
    await assertAlignedChart(page)
    await expect(page.getByTestId('result-chart-visible-bars')).toContainText('180 velas')
  })

  test('mobile /combo/results alinha média à última vela de mercado', async ({ page }) => {
    await page.setViewportSize({ width: 390, height: 844 })
    await seedComboResults(page)
    await assertAlignedChart(page)
  })

  test('desktop /monitor alinha média em 15m, 1h, 4h e 1d', async ({ page }) => {
    test.setTimeout(60_000)
    await page.setViewportSize({ width: 1440, height: 900 })
    await seedMonitorChart(page)
    await assertMonitorAlignedChart(page)
  })

  test('mobile /monitor alinha média em 15m, 1h, 4h e 1d', async ({ page }) => {
    test.setTimeout(60_000)
    await page.setViewportSize({ width: 390, height: 844 })
    await seedMonitorChart(page)
    await assertMonitorAlignedChart(page)
  })
})
