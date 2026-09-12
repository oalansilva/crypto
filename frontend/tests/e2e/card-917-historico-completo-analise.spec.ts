import { expect, test, type Page } from '@playwright/test'

const CANDLE_COUNT = 3300

function buildDailyCandles(count: number) {
  const start = Date.UTC(2017, 7, 17)
  return Array.from({ length: count }, (_, index) => {
    const timestamp = start + index * 86_400_000
    const open = 4000 + index * 120
    const close = open + (index % 2 === 0 ? 180 : -90)
    return {
      timestamp_utc: new Date(timestamp).toISOString(),
      open,
      high: Math.max(open, close) + 220,
      low: Math.min(open, close) - 220,
      close,
      volume: 5000 + index * 12,
    }
  })
}

const ANALYSIS_TRADES = [
  {
    entry_time: '2017-10-05T00:00:00.000Z',
    entry_price: 4200,
    exit_time: '2017-11-01T00:00:00.000Z',
    exit_price: 6400,
    profit: 0.05,
    type: 'long',
  },
  {
    entry_time: '2025-06-01T00:00:00.000Z',
    entry_price: 68000,
    exit_time: '2025-07-01T00:00:00.000Z',
    exit_price: 71000,
    profit: 0.03,
    type: 'long',
  },
  {
    entry_time: '2025-12-01T00:00:00.000Z',
    entry_price: 90000,
    exit_time: '2026-01-05T00:00:00.000Z',
    exit_price: 93000,
    profit: 0.02,
    type: 'long',
  },
  {
    entry_time: '2026-05-10T00:00:00.000Z',
    entry_price: 95000,
    exit_time: '2026-07-10T00:00:00.000Z',
    exit_price: 99000,
    profit: 0.04,
    type: 'long',
  },
  {
    entry_time: '2026-07-20T00:00:00.000Z',
    entry_price: 100000,
    exit_time: '2026-08-01T00:00:00.000Z',
    exit_price: 102000,
    profit: 0.01,
    type: 'long',
  },
]

const SHORT_MONITOR_HISTORY = [
  {
    timestamp: '2026-05-10T00:00:00.000Z',
    signal: 1,
    type: 'entry',
    reason: 'entry',
    price: 95000,
  },
  {
    timestamp: '2026-07-10T00:00:00.000Z',
    signal: -1,
    type: 'exit',
    reason: 'exit_logic',
    price: 99000,
  },
]

const ANALYSIS_RESULT = {
  template_name: 'multi_ma_crossover',
  display_name: 'Médias Móveis: Tendência em Virada',
  symbol: 'BTC/USDT',
  timeframe: '1d',
  parameters: { direction: 'long' },
  metrics: {
    total_trades: ANALYSIS_TRADES.length,
    win_rate: 0.6,
    total_return: 0.5,
    avg_profit: 0.05,
    max_drawdown: 0.12,
  },
  trades: ANALYSIS_TRADES,
  signal_history: SHORT_MONITOR_HISTORY,
  indicator_data: {},
  candles: buildDailyCandles(CANDLE_COUNT),
  direction: 'long',
}

async function openComboResults(page: Page) {
  await page.addInitScript(() => {
    window.localStorage.setItem('auth_access_token', 'test-access-token')
    window.localStorage.setItem('auth_refresh_token', 'test-refresh-token')
    window.localStorage.setItem('auth_user', JSON.stringify({
      id: 'admin-user',
      email: 'admin@example.com',
      name: 'Admin User',
      isAdmin: true,
    }))
  })

  await page.goto('/combo/results')
  await page.evaluate((result) => {
    history.replaceState(
      { usr: { result, returnTo: '/favorites' }, key: 'card-917', idx: 0 },
      '',
      location.href,
    )
  }, ANALYSIS_RESULT)
  await page.reload()
  await expect(page.locator('.combo-page')).toBeVisible()
  await expect(page.getByTestId('combo-result-summary')).toBeVisible()
}

async function expectChartContract(page: Page) {
  const chart = page.getByTestId('monitor-aligned-result-chart')
  await expect(chart).toHaveAttribute('data-list-count', String(ANALYSIS_TRADES.length))
  await expect(chart).toHaveAttribute('data-marker-count', String(ANALYSIS_TRADES.length * 2))
  await expect(chart.getByTestId('history-pair')).toContainText('Lista 5 · Setas 10')
  await page.getByTestId('result-chart-zoom-reset').click()
  await expect.poll(async () => page.getByTestId('result-chart-visible-bars').textContent(), { timeout: 15_000 }).toMatch(/180 velas/)
  await expect.poll(async () => {
    const from = await chart.getAttribute('data-viewport-from')
    return from !== null && from >= '2026-01-05'
  }, { timeout: 15_000 }).toBe(true)
  await expect(chart).toHaveAttribute('data-marker-times', /2017-10-05/)
}

for (const viewport of [
  { name: 'desktop', width: 1440, height: 900 },
  { name: 'mobile', width: 390, height: 844 },
]) {
  test(`card 917 combo/results keeps full marker series (${viewport.name})`, async ({ page }) => {
    await page.setViewportSize({ width: viewport.width, height: viewport.height })
    await openComboResults(page)
    await expectChartContract(page)

    const chart = page.getByTestId('monitor-aligned-result-chart')
    const markerCountBefore = await chart.getAttribute('data-marker-count')
    const viewportFromBefore = await chart.getAttribute('data-viewport-from')
    expect(viewportFromBefore && viewportFromBefore >= '2026-01-05').toBeTruthy()

    for (let step = 0; step < 40; step += 1) {
      await page.getByTestId('result-chart-zoom-out').click()
    }

    const chartShell = page.getByTestId('result-chart-shell')
    const box = await chartShell.boundingBox()
    if (box) {
      await page.mouse.move(box.x + box.width * 0.2, box.y + box.height / 2)
      await page.mouse.down()
      await page.mouse.move(box.x + box.width * 0.85, box.y + box.height / 2, { steps: 12 })
      await page.mouse.up()
    }

    await expect.poll(async () => chart.getAttribute('data-viewport-from')).not.toBe(viewportFromBefore)
    const minZoomedBars = viewport.width < 500 ? 250 : 600
    await expect.poll(async () => {
      const visible = await page.getByTestId('result-chart-visible-bars').textContent()
      return visible !== null && Number.parseInt(visible, 10) > minZoomedBars
    }, { timeout: 15_000 }).toBe(true)
    await expect(chart).toHaveAttribute('data-marker-count', markerCountBefore ?? '')
    await expect(chart).toHaveAttribute('data-marker-times', /2017-10-05/)

    await page.getByTestId('result-chart-zoom-reset').click()
    await expect(page.getByTestId('result-chart-visible-bars')).toContainText('180 velas')
    await expect(chart).toHaveAttribute('data-marker-count', markerCountBefore ?? '')
    await expect(page.getByText('Lista de operações')).toBeVisible()
  })
}
