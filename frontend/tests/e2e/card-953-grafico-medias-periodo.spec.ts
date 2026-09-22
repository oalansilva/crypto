import { expect, test, type Page } from '@playwright/test'

const WHOLE_MARKET_START = '2017-08-17T00:00:00.000Z'
const FAVORITE_START = '2024-09-16T00:00:00.000Z'
const FAVORITE_END = '2026-09-16T00:00:00.000Z'

function buildDailyCandles(untilIso: string, startIso = FAVORITE_START) {
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

const FAVORITE_CANDLES = buildDailyCandles(FAVORITE_END).slice(0, 250)
const FAVORITE_LAST = FAVORITE_CANDLES.at(-1)!.timestamp_utc.slice(0, 10)
const WHOLE_MARKET_CANDLES = [
  ...buildDailyCandles(FAVORITE_START, WHOLE_MARKET_START).slice(0, 1),
  ...FAVORITE_CANDLES,
]

function recentOnlyMaSeries(candles: typeof FAVORITE_CANDLES, period: number) {
  const recent = candles.slice(-30)
  return recent.map((candle, index) => ({
    timestamp_utc: candle.timestamp_utc,
    value: candle.close - period + index,
  }))
}

const transparencyTwoYearFavorite = {
  status: 'available',
  timeframe: '1d',
  display_name: 'Virada de Tendência',
  indicators: [
    {
      key: 'sma_fast',
      type: 'sma',
      label: 'SMA 9',
      panel: 'price',
      color: '#f6465d',
      parameters: { length: 9 },
      series_status: 'available',
      series: recentOnlyMaSeries(FAVORITE_CANDLES, 9),
    },
    {
      key: 'sma_slow',
      type: 'sma',
      label: 'SMA 21',
      panel: 'price',
      color: '#3b82f6',
      parameters: { length: 21 },
      series_status: 'available',
      series: recentOnlyMaSeries(FAVORITE_CANDLES, 21),
    },
  ],
}

const ANALYSIS_RESULT = {
  template_name: 'trend_reversal',
  symbol: 'BTC/USDT',
  timeframe: '1d',
  parameters: { direction: 'long' },
  metrics: { total_trades: 16, win_rate: 0.5, total_return: 0.1, avg_profit: 0.05 },
  trades: Array.from({ length: 16 }, (_, index) => ({
    entry_time: FAVORITE_CANDLES[10 + index * 12].timestamp_utc,
    entry_price: 45_000,
    exit_time: FAVORITE_CANDLES[11 + index * 12].timestamp_utc,
    exit_price: 46_000,
    profit: 0.02,
    type: 'long',
  })),
  indicator_data: {},
  candles: FAVORITE_CANDLES,
  strategy_transparency: transparencyTwoYearFavorite,
  direction: 'long',
}

async function seedMonitorChartModal(page: Page) {
  await page.addInitScript(() => {
    window.localStorage.setItem('auth_access_token', 'test-access-token')
    window.localStorage.setItem('auth_refresh_token', 'test-refresh-token')
    window.localStorage.setItem('auth_user', JSON.stringify({
      id: 'card-953-user',
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
    const url = new URL(route.request().url())
    if (url.pathname.endsWith('/trades')) {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          trades: ANALYSIS_RESULT.trades,
          metrics: ANALYSIS_RESULT.metrics,
          candles: ANALYSIS_RESULT.candles,
          indicator_data: ANALYSIS_RESULT.indicator_data,
          strategy_transparency: ANALYSIS_RESULT.strategy_transparency,
        }),
      })
      return
    }
    await route.fulfill({ status: 200, contentType: 'application/json', body: '[]' })
  })

  await page.route('**/api/auth/me', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        id: 'card-953-user',
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
    const fullHistory = url.searchParams.get('full_history') === 'true'
    const candles = fullHistory ? WHOLE_MARKET_CANDLES : FAVORITE_CANDLES.slice(-300)
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
        id: 953,
        symbol: 'BTC/USDT',
        timeframe: '1d',
        template_name: 'trend_reversal',
        strategy_display_name: 'Virada de Tendência',
        strategy_description: 'Card 953 monitor',
        strategy_transparency: transparencyTwoYearFavorite,
        is_strategy_protected: false,
        name: 'BTC Monitor 953',
        notes: '',
        tier: 1,
        parameters: { direction: 'long' },
        is_holding: true,
        distance_to_next_status: 0.5,
        next_status_label: 'exit',
        status: 'HOLDING',
        message: 'Posição ativa',
        last_price: 95_000,
        timestamp: FAVORITE_END,
        indicator_values_candle_time: FAVORITE_LAST,
        signal_history: [],
        details: {},
      }]),
    })
  })

  await page.goto('/monitor')
  const viewport = page.viewportSize()
  if (viewport && viewport.width < 768) {
    await page.getByTestId('monitor-card-btc-usdt').getByRole('button', { name: 'Abrir Gráfico' }).click()
  } else {
    await page.getByRole('button', { name: /Abrir Gráfico BTC\/USDT/i }).first().click()
  }
  await expect(page.getByTestId('chart-modal')).toBeVisible()
}

async function seedComboResults(page: Page) {
  await page.addInitScript(() => {
    window.localStorage.setItem('auth_access_token', 'test-access-token')
    window.localStorage.setItem('auth_refresh_token', 'test-refresh-token')
    window.localStorage.setItem('auth_user', JSON.stringify({
      id: 'card-953-user',
      email: 'trader@example.com',
      name: 'Trader',
      isAdmin: false,
    }))
  })

  await page.route('**/api/market/candles**', async (route) => {
    const url = new URL(route.request().url())
    const fullHistory = url.searchParams.get('full_history') === 'true'
    const candles = fullHistory ? WHOLE_MARKET_CANDLES : FAVORITE_CANDLES.slice(-300)
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ candles, canonical_candles: true }),
    })
  })

  await page.goto('/combo/results')
  await page.evaluate((result) => {
    history.replaceState(
      { usr: { result, returnTo: '/favorites' }, key: 'card-953', idx: 0 },
      '',
      location.href,
    )
  }, ANALYSIS_RESULT)
  await page.reload()
  await expect(page.locator('.combo-page')).toBeVisible()
}

const viewports = [
  { name: 'desktop', width: 1440, height: 900 },
  { name: 'mobile', width: 390, height: 844 },
] as const

for (const viewport of viewports) {
  test.describe(`card-953 combo ${viewport.name}`, () => {
    test.use({ viewport: { width: viewport.width, height: viewport.height } })
    test.setTimeout(90_000)

    test('2 anos ≠ todo o mercado; zoom 180 com linha; Menos revela histórico; clip #921', async ({ page }) => {
      await seedComboResults(page)
      const chart = page.getByTestId('monitor-aligned-result-chart')
      await expect(chart).toBeVisible()
      await expect.poll(async () => chart.getAttribute('data-ma-ahead'), { timeout: 15_000 }).toBe('0')
      await expect(chart).toHaveAttribute('data-whole-market', '0')
      await expect(chart).toHaveAttribute('data-period-start', '2024-09-16')

      const visibleBars = page.getByTestId('result-chart-visible-bars')
      await expect.poll(async () => visibleBars.textContent(), { timeout: 15_000 }).toMatch(/180/)

      const minus = page.getByTestId('result-chart-zoom-out')
      await minus.click()
      await minus.click()
      await expect.poll(async () => visibleBars.textContent(), { timeout: 10_000 }).not.toMatch(/^180 /)

      await expect.poll(async () => {
        const linesOnOld = await chart.getAttribute('data-lines-on-old')
        if (linesOnOld === '1') return linesOnOld
        await minus.click()
        return chart.getAttribute('data-lines-on-old')
      }, { timeout: 30_000 }).toBe('1')
      await expect.poll(async () => chart.getAttribute('data-viewport-from')).toContain('2024-09-16')
      await expect.poll(async () => chart.getAttribute('data-last-candle-timestamp')).toContain(FAVORITE_LAST)
      const lastCandle = await chart.getAttribute('data-last-candle-timestamp')
      const lastMa = await chart.getAttribute('data-last-ma-timestamp')
      expect(lastMa?.slice(0, 10)).toBe(lastCandle?.slice(0, 10))

      await page.getByTestId('result-chart-zoom-reset').click()
      await expect.poll(async () => visibleBars.textContent(), { timeout: 10_000 }).toMatch(/180/)
      await expect(chart).toHaveAttribute('data-ma-ahead', '0')

      await expect(chart).toHaveAttribute('data-marker-count', '32')
      await expect(chart).toHaveAttribute('data-list-count', '16')
    })
  })
}

for (const viewport of viewports) {
  test.describe(`card-953 monitor ${viewport.name}`, () => {
    test.use({ viewport: { width: viewport.width, height: viewport.height } })
    test.setTimeout(90_000)

    test('ChartModal — zoom 180, recorte 2 anos, Menos revela médias antigas', async ({ page }) => {
      await seedMonitorChartModal(page)
      const dialog = page.getByTestId('chart-modal')
      const chart = dialog.getByTestId('chart-modal-surface')
      await expect(chart).toBeVisible()
      await expect.poll(async () => chart.getAttribute('data-ma-ahead'), { timeout: 15_000 }).toBe('0')
      await expect(chart).toHaveAttribute('data-whole-market', '0')
      await expect(chart).toHaveAttribute('data-period-start', '2024-09-16')

      const visibleBars = page.getByTestId('chart-visible-bars')
      await expect.poll(async () => visibleBars.textContent(), { timeout: 15_000 }).toMatch(/180/)

      const minus = page.getByTestId('chart-zoom-out')
      await minus.click()
      await minus.click()
      await expect.poll(async () => visibleBars.textContent(), { timeout: 10_000 }).not.toMatch(/^180 /)

      await expect.poll(async () => {
        const linesOnOld = await chart.getAttribute('data-lines-on-old')
        if (linesOnOld === '1') return linesOnOld
        await minus.click()
        return chart.getAttribute('data-lines-on-old')
      }, { timeout: 30_000 }).toBe('1')
      await expect.poll(async () => chart.getAttribute('data-viewport-from')).toContain('2024-09-16')
      await expect.poll(async () => chart.getAttribute('data-last-candle-timestamp')).toContain(FAVORITE_LAST)
      const lastCandle = await chart.getAttribute('data-last-candle-timestamp')
      const lastMa = await chart.getAttribute('data-last-ma-timestamp')
      expect(lastMa?.slice(0, 10)).toBe(lastCandle?.slice(0, 10))

      await page.getByTestId('chart-zoom-reset').click()
      await expect.poll(async () => visibleBars.textContent(), { timeout: 10_000 }).toMatch(/180/)
      await expect(chart).toHaveAttribute('data-ma-ahead', '0')
    })
  })
}

for (const viewport of viewports) {
  test.describe(`card-953 proto ${viewport.name}`, () => {
    test.use({ viewport: { width: viewport.width, height: viewport.height } })

    test('index e monitor — recorte e painel MACD', async ({ page }) => {
      await page.goto('/prototypes/card-953-grafico-medias-periodo/')
      const chart = page.locator('[data-testid="monitor-aligned-result-chart"]')
      await expect(chart).toHaveAttribute('data-whole-market', '0')
      await expect(chart).toHaveAttribute('data-ma-ahead', '0')

      await page.goto('/prototypes/card-953-grafico-medias-periodo/monitor.html')
      await expect(page.locator('table.signals')).toBeVisible()
      await page.locator('table.signals tbody tr', { hasText: 'SOL' }).click()
      await expect(page.getByText(/Painel macd/i)).toBeVisible()
    })
  })
}
