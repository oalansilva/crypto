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
  },
  {
    id: 2,
    name: 'BTC Momentum',
    symbol: 'BTC/USDT',
    timeframe: '4h',
    strategy_name: 'ema_rsi',
    parameters: {},
    metrics: {},
    created_at: '2025-01-01T00:00:00Z',
  },
]

function buildCandles() {
  return [
    { timestamp_utc: '2025-01-01T00:00:00Z', open: 100, high: 102, low: 99, close: 101, volume: 1000 },
    { timestamp_utc: '2025-01-01T01:00:00Z', open: 101, high: 103, low: 100, close: 102, volume: 1100 },
    { timestamp_utc: '2025-01-01T02:00:00Z', open: 102, high: 104, low: 101, close: 103, volume: 1200 },
  ]
}

async function setupApiMocks(page: any) {
  const requestedTimeframes: string[] = []

  await page.route('**/*', (route: any) => {
    const url = new URL(route.request().url())
    if (url.hostname === '127.0.0.1' || url.hostname === 'localhost') {
      return route.continue()
    }
    return route.abort('blockedbyclient')
  })

  await page.route('**/api/opportunities/**', (route: any) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify([]),
    })
  )

  await page.route('**/api/favorites/', (route: any) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(FAVORITES_PAYLOAD),
    })
  )

  await page.route('**/api/market/candles**', (route: any) => {
    const url = new URL(route.request().url())
    requestedTimeframes.push(url.searchParams.get('timeframe') || '')
    return route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        symbol: url.searchParams.get('symbol'),
        timeframe: url.searchParams.get('timeframe'),
        asset_type: 'crypto',
        data_source: 'ccxt',
        candles: buildCandles(),
        count: 3,
        limit: 300,
      }),
    })
  })

  return {
    requestedTimeframes,
  }
}

test.use({ viewport: { width: 390, height: 844 } })

test('monitor shows status and dashboard tabs and loads favorites in dashboard', async ({ page }) => {
  await setupApiMocks(page)
  await page.goto('/monitor')

  await expect(page.getByRole('tab', { name: 'Status' })).toBeVisible()
  await expect(page.getByRole('tab', { name: 'Dashboard' })).toBeVisible()

  await page.getByRole('tab', { name: 'Dashboard' }).click()
  await expect(page.getByTestId('monitor-dashboard-tab')).toBeVisible()
  await expect(page.getByTestId('dashboard-symbol-list')).toContainText('NVDA')
  await expect(page.getByTestId('dashboard-symbol-list')).toContainText('BTC/USDT')
})

test('monitor dashboard selects symbol and renders chart container', async ({ page }) => {
  await setupApiMocks(page)
  await page.goto('/monitor')
  await page.getByRole('tab', { name: 'Dashboard' }).click()

  await page.getByRole('button', { name: /BTC\/USDT/i }).click()
  await expect(page.getByTestId('market-candles-chart')).toBeVisible()
})

test('monitor dashboard timeframe switching updates request and state', async ({ page }) => {
  const mocks = await setupApiMocks(page)
  await page.goto('/monitor')
  await page.getByRole('tab', { name: 'Dashboard' }).click()

  await expect(page.getByTestId('timeframe-1h')).toHaveAttribute('aria-pressed', 'true')
  await page.getByTestId('timeframe-4h').click()
  await expect(page.getByTestId('timeframe-4h')).toHaveAttribute('aria-pressed', 'true')

  await expect.poll(() => mocks.requestedTimeframes.includes('4h')).toBe(true)
})
