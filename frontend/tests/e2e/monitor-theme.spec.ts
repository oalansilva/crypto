import { expect, test } from '@playwright/test'

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

const sleep = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms))

async function setupApiMocks(page: any) {
  const preferences: Record<string, any> = {
    __global__: { in_portfolio: false, card_mode: 'price', price_timeframe: '1d', theme: 'dark-green' },
    NVDA: { in_portfolio: true, card_mode: 'price', price_timeframe: '1d', theme: 'dark-green' },
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

    await sleep(50)

    const current = preferences[symbol] || { in_portfolio: false, card_mode: 'price', price_timeframe: '1d' }
    const next = {
      in_portfolio: patch.in_portfolio ?? current.in_portfolio,
      card_mode: patch.card_mode ?? current.card_mode,
      price_timeframe: patch.price_timeframe ?? current.price_timeframe,
      theme: patch.theme ?? current.theme ?? 'dark-green',
    }
    preferences[symbol] = next

    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(next),
    })
  })

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

  return { preferences }
}

test('monitor defaults to dark-green theme (not black)', async ({ page }) => {
  await setupApiMocks(page)
  await page.goto('/monitor')

  const root = page.getByTestId('monitor-status-tab')
  await expect(root).toBeVisible()
  await expect(root).toHaveClass(/monitor-theme--dark-green/)
})

test('theme toggle persists across reload (via __global__ preference)', async ({ page }) => {
  await setupApiMocks(page)
  await page.goto('/monitor')

  const root = page.getByTestId('monitor-status-tab')
  await expect(root).toHaveClass(/monitor-theme--dark-green/)

  await page.getByTestId('monitor-theme-toggle').click()
  await expect(root).toHaveClass(/monitor-theme--black/)

  await page.reload()
  await expect(root).toHaveClass(/monitor-theme--black/)
})
