import { expect, test } from '@playwright/test'

const FAVORITES_PAYLOAD = [
  {
    id: 1,
    name: 'BTC Trend',
    symbol: 'BTC/USDT',
    timeframe: '4h',
    strategy_name: 'ema_rsi',
    parameters: {},
    metrics: {},
    created_at: '2025-01-01T00:00:00Z',
    tier: 1,
  },
  {
    id: 2,
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
    symbol: 'BTC/USDT',
    timeframe: '4h',
    template_name: 'ema_rsi',
    name: 'BTC Trend',
    notes: '',
    tier: 1,
    parameters: { ema_short: 9, ema_long: 21 },
    is_holding: false,
    distance_to_next_status: 0.3,
    next_status_label: 'entry',
    status: 'WAIT',
    message: 'Waiting for entry',
    last_price: 50000,
    timestamp: '2025-01-01T00:00:00Z',
    details: {},
  },
  {
    id: 2,
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

function buildCandles() {
  return [
    { timestamp_utc: '2025-01-01T00:00:00Z', open: 100, high: 102, low: 99, close: 101, volume: 1000 },
    { timestamp_utc: '2025-01-01T01:00:00Z', open: 101, high: 103, low: 100, close: 102, volume: 1100 },
    { timestamp_utc: '2025-01-01T02:00:00Z', open: 102, high: 104, low: 101, close: 103, volume: 1200 },
  ]
}

const sleep = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms))

async function setupApiMocks(
  page: any,
  options?: {
    candlesDelayMs?: number
    preferencePatchDelayMs?: number
  }
) {
  const requestedTimeframes: string[] = []
  const preferencePatches: Array<{ symbol: string; patch: any }> = []
  const preferences: Record<
    string,
    { in_portfolio: boolean; card_mode: 'price' | 'strategy'; price_timeframe: '15m' | '1h' | '4h' | '1d' }
  > = {
    'BTC/USDT': { in_portfolio: true, card_mode: 'price', price_timeframe: '1d' },
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

  await page.route('**/api/monitor/preferences', (route: any) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(preferences),
    })
  )

  await page.route('**/api/monitor/preferences/*', async (route: any) => {
    const url = new URL(route.request().url())
    const symbol = decodeURIComponent(url.pathname.split('/').pop() || '').trim()
    const patch = route.request().postDataJSON() || {}
    if (options?.preferencePatchDelayMs) {
      await sleep(options.preferencePatchDelayMs)
    }
    const current = preferences[symbol] || { in_portfolio: false, card_mode: 'price', price_timeframe: '1d' }
    const next = {
      in_portfolio: patch.in_portfolio ?? current.in_portfolio,
      card_mode: patch.card_mode ?? current.card_mode,
      price_timeframe: patch.price_timeframe ?? current.price_timeframe,
    }
    preferencePatches.push({ symbol, patch })
    preferences[symbol] = next

    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(next),
    })
  })

  await page.route('**/api/market/candles**', (route: any) =>
    {
      const url = new URL(route.request().url())
      requestedTimeframes.push(url.searchParams.get('timeframe') || '')
      return (async () => {
        if (options?.candlesDelayMs) {
          await sleep(options.candlesDelayMs)
        }
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            candles: buildCandles(),
          }),
        })
      })()
    }
  )

  return {
    requestedTimeframes,
    preferencePatches,
  }
}

test('defaults to In Portfolio and hides symbols without preference', async ({ page }) => {
  await setupApiMocks(page)
  await page.goto('/monitor')

  await expect(page.getByTestId('monitor-card-btc-usdt')).toBeVisible()
  await expect(page.getByTestId('monitor-card-nvda')).toHaveCount(0)
})

test('toggle in_portfolio persists across reload', async ({ page }) => {
  await setupApiMocks(page)
  await page.goto('/monitor')

  await page.getByTestId('monitor-filter-all').click()
  await expect(page.getByTestId('monitor-card-nvda')).toBeVisible()

  await page.getByTestId('portfolio-toggle-nvda').click()
  await page.getByTestId('monitor-filter-in-portfolio').click()
  await expect(page.getByTestId('monitor-card-nvda')).toBeVisible()

  await page.reload()
  await expect(page.getByTestId('monitor-card-nvda')).toBeVisible()
})

test('per-card mode toggle persists across reload', async ({ page }) => {
  await setupApiMocks(page)
  await page.goto('/monitor')

  await expect(page.getByTestId('mode-label-btc-usdt')).toHaveText('Price')
  await page.getByTestId('mode-toggle-btc-usdt').click()
  await expect(page.getByTestId('mode-label-btc-usdt')).toHaveText('Strategy')

  await page.reload()
  await expect(page.getByTestId('mode-label-btc-usdt')).toHaveText('Strategy')
})

test('per-card timeframe selection persists across reload', async ({ page }) => {
  const mocks = await setupApiMocks(page)
  await page.goto('/monitor')

  await expect(page.getByTestId('timeframe-toggle-btc-usdt-1d')).toHaveAttribute('aria-pressed', 'true')
  await page.getByTestId('timeframe-toggle-btc-usdt-4h').click()
  await expect(page.getByTestId('timeframe-toggle-btc-usdt-4h')).toHaveAttribute('aria-pressed', 'true')
  await expect.poll(() => mocks.requestedTimeframes.includes('4h')).toBe(true)

  await page.reload()
  await expect(page.getByTestId('timeframe-toggle-btc-usdt-4h')).toHaveAttribute('aria-pressed', 'true')
})

test('timeframe switch keeps non-chart controls interactive and shows localized chart loading', async ({ page }) => {
  const mocks = await setupApiMocks(page, { candlesDelayMs: 600, preferencePatchDelayMs: 500 })
  await page.goto('/monitor')

  await page.getByTestId('timeframe-toggle-btc-usdt-4h').click()
  await expect(page.getByTestId('timeframe-toggle-btc-usdt-4h')).toHaveAttribute('aria-pressed', 'true')
  await expect(page.getByTestId('candles-loading-btc-usdt')).toBeVisible()
  await expect(page.getByTestId('portfolio-toggle-btc-usdt')).toBeEnabled()

  await page.getByTestId('portfolio-toggle-btc-usdt').click()
  await expect
    .poll(() =>
      mocks.preferencePatches.some(
        (entry) => entry.symbol === 'BTC/USDT' && entry.patch && entry.patch.in_portfolio === false
      )
    )
    .toBe(true)

  await expect(page.getByTestId('candles-chart-area-btc-usdt')).toContainText('Loading chart...')
  await expect(page.locator('body')).not.toContainText('Loading candles...')
})
