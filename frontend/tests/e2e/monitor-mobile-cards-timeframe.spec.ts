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

async function setupApiMocks(page: any) {
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
      body: JSON.stringify({
        NVDA: { in_portfolio: true, card_mode: 'price', price_timeframe: '1d' },
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

test('monitor mobile uses single cards view and stock timeframe buttons are constrained to 1d', async ({ page }) => {
  await setupApiMocks(page)
  await page.goto('/monitor')

  await expect(page.getByTestId('monitor-card-nvda')).toBeVisible()
  await expect(page.getByTestId('timeframe-toggle-nvda-1d')).toHaveAttribute('aria-pressed', 'true')
  await expect(page.getByTestId('timeframe-toggle-nvda-15m')).toBeDisabled()
  await expect(page.getByTestId('timeframe-toggle-nvda-1h')).toBeDisabled()
  await expect(page.getByTestId('timeframe-toggle-nvda-4h')).toBeDisabled()
})
