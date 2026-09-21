import { expect, test, type Page } from '@playwright/test'

const AUTH_USER = {
  id: 'card-994-user',
  email: 'card994@example.com',
  name: 'Card 994',
  isAdmin: true,
  mustChangePassword: false,
}

const FAVORITES = [
  {
    id: 1,
    name: 'BTC Trend',
    symbol: 'BTC/USDT',
    timeframe: '4h',
    strategy_name: 'multi_ma_crossover',
    strategy_display_name: 'Médias Móveis: Tendência em Virada',
    parameters: {},
    metrics: {},
    created_at: '2026-09-19T00:00:00Z',
    tier: 1,
  },
  {
    id: 2,
    name: 'ETH Trend',
    symbol: 'ETH/USDT',
    timeframe: '1d',
    strategy_name: 'macd',
    strategy_display_name: 'MACD: Mudança de Ritmo',
    parameters: {},
    metrics: {},
    created_at: '2026-09-19T00:00:00Z',
    tier: 2,
  },
]

const OPPORTUNITIES = [
  {
    id: 1,
    symbol: 'BTC/USDT',
    asset_type: 'crypto',
    timeframe: '4h',
    template_name: 'multi_ma_crossover',
    strategy_display_name: 'Médias Móveis: Tendência em Virada',
    name: 'BTC Trend',
    notes: '',
    tier: 1,
    parameters: { direction: 'long' },
    is_holding: true,
    distance_to_next_status: 1.8,
    next_status_label: 'exit',
    status: 'HOLDING',
    message: 'Em posição',
    last_price: 64215.4,
    timestamp: '2026-09-19T12:00:00Z',
    indicator_values_candle_time: '2026-09-19T12:00:00Z',
    distance_to_stop_pct: 4.2,
    details: {},
  },
  {
    id: 2,
    symbol: 'ETH/USDT',
    asset_type: 'crypto',
    timeframe: '1d',
    template_name: 'macd',
    strategy_display_name: 'MACD: Mudança de Ritmo',
    name: 'ETH Trend',
    notes: '',
    tier: 2,
    parameters: { direction: 'long' },
    is_holding: false,
    distance_to_next_status: 0.9,
    next_status_label: 're-entry',
    status: 'EXITED',
    message: 'Saída confirmada',
    last_price: 3412.5,
    timestamp: '2026-09-19T12:00:00Z',
    indicator_values_candle_time: '2026-09-19T00:00:00Z',
    distance_to_stop_pct: 2.1,
    details: {},
  },
]

function buildCandles() {
  return [
    { timestamp_utc: '2026-09-18T00:00:00Z', open: 100, high: 102, low: 99, close: 101, volume: 1000 },
    { timestamp_utc: '2026-09-18T04:00:00Z', open: 101, high: 103, low: 100, close: 102, volume: 1100 },
    { timestamp_utc: '2026-09-18T08:00:00Z', open: 102, high: 104, low: 101, close: 103, volume: 1200 },
  ]
}

async function mockAuthenticatedSession(page: Page) {
  await page.addInitScript((user) => {
    window.localStorage.setItem('auth_access_token', 'test-access-token')
    window.localStorage.setItem('auth_refresh_token', 'test-refresh-token')
    window.localStorage.setItem('auth_user', JSON.stringify(user))
    window.localStorage.setItem('cripto-farol-onboarding-dismissed', '1')
  }, AUTH_USER)
}

async function setupMonitor(page: Page) {
  await mockAuthenticatedSession(page)
  const candleRequests: Array<{ symbol: string; timeframe: string; limit: string }> = []

  await page.route('**/*', (route) => {
    const url = new URL(route.request().url())
    if (url.hostname === '127.0.0.1' || url.hostname === 'localhost') {
      return route.continue()
    }
    return route.abort('blockedbyclient')
  })

  await page.route('**/api/**', async (route) => {
    const url = route.request().url()

    if (url.includes('/api/auth/me')) {
      await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(AUTH_USER) })
      return
    }

    if (url.match(/\/api\/favorites\/?(\?|$)/)) {
      await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(FAVORITES) })
      return
    }

    if (url.includes('/api/favorites/') && url.includes('/trades')) {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ trades: [], metrics: null, strategy_transparency: null }),
      })
      return
    }

    if (url.includes('/api/opportunities')) {
      await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(OPPORTUNITIES) })
      return
    }

    if (url.includes('/api/monitor/preferences')) {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          'BTC/USDT': { in_portfolio: true, card_mode: 'price', price_timeframe: '1d' },
          'ETH/USDT': { in_portfolio: true, card_mode: 'price', price_timeframe: '1d' },
        }),
      })
      return
    }

    if (url.includes('/api/monitor/spot-market-orders/eligibility')) {
      await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ items: [] }) })
      return
    }

    if (url.includes('/api/user/binance-credentials')) {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ configured: false, api_key_masked: null }),
      })
      return
    }

    if (url.includes('/api/users/me/telegram-settings')) {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ telegramAlertsEnabled: false }),
      })
      return
    }

    if (url.includes('/api/market/candles')) {
      const parsed = new URL(url)
      candleRequests.push({
        symbol: parsed.searchParams.get('symbol') || '',
        timeframe: parsed.searchParams.get('timeframe') || '',
        limit: parsed.searchParams.get('limit') || '',
      })
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ candles: buildCandles() }),
      })
      return
    }

    await route.fulfill({ status: 200, contentType: 'application/json', body: '{}' })
  })

  return { candleRequests }
}

function isMobile(width: number) {
  return width < 740
}

async function assertNoSecondTimeframe(page: Page) {
  await expect(page.getByText('Gráfico 1d')).toHaveCount(0)
  await expect(page.getByText('tf 1d')).toHaveCount(0)
  await expect(page.getByTitle('Timeframe do gráfico de preço')).toHaveCount(0)
  await expect(page.getByTestId('timeframe-toggle-btc-usdt-1d')).toHaveCount(0)
}

async function openBtcChart(page: Page, width: number, mode: 'chart' | 'trades' = 'chart') {
  const label = mode === 'trades' ? 'Ver Trades' : 'Abrir Gráfico'
  if (isMobile(width)) {
    const card = page.getByTestId('monitor-card-btc-usdt')
    await expect(card).toBeVisible()
    await card.getByRole('button', { name: label }).click()
    return
  }
  const row = page.getByTestId('monitor-row-btc-usdt')
  await expect(row).toBeVisible()
  await row.getByRole('button', { name: new RegExp(`^${label}`) }).click()
}

async function assertChartLockedToStrategy(page: Page) {
  const dialog = page.getByTestId('chart-modal')
  await expect(dialog).toBeVisible()
  await expect(page.getByTestId('chart-strategy-tf')).toContainText('Estratégia')
  await expect(page.getByTestId('chart-strategy-tf')).toContainText('4h')
  await expect(page.getByRole('group', { name: 'Selecionar timeframe do gráfico' })).toHaveCount(0)
  await expect(page.getByTestId('chart-timeframe-15m')).toHaveCount(0)
  await expect(page.getByTestId('chart-timeframe-1h')).toHaveCount(0)
  await expect(page.getByTestId('chart-timeframe-1d')).toHaveCount(0)
  await expect(page.getByTestId('chart-timeframe-4h')).toHaveCount(0)
  await expect(page.getByRole('button', { name: '15m' })).toHaveCount(0)
  await expect(page.getByRole('button', { name: '1h' })).toHaveCount(0)
  await expect(page.getByRole('button', { name: '1d' })).toHaveCount(0)
  await expect(page.getByRole('button', { name: 'Estratégia (4H)' })).toHaveCount(0)
  await expect(page.locator('[data-chart-tf]')).toHaveCount(0)
}

for (const project of [
  { name: 'desktop', width: 1440, height: 900 },
  { name: 'mobile', width: 390, height: 844 },
] as const) {
  test.describe(`card-994 ${project.name}`, () => {
    test.use({ viewport: { width: project.width, height: project.height } })

    test('BTC 4h shows 4h next to the pair without a second TF', async ({ page }) => {
      await setupMonitor(page)
      await page.goto('/monitor')

      if (isMobile(project.width)) {
        const card = page.getByTestId('monitor-card-btc-usdt')
        await expect(card).toBeVisible()
        await expect(card.getByTitle('Timeframe da estratégia')).toHaveText('4h')
      } else {
        await expect(page.getByTestId('monitor-row-btc-usdt')).toBeVisible()
        await expect(page.getByTestId('monitor-pair-tf-btc-usdt')).toHaveText('4h')
        await page.getByTestId('monitor-row-btc-usdt').click()
        const expanded = page.locator('[data-testid="monitor-card-btc-usdt"]:visible')
        await expect(expanded).toBeVisible()
        await expect(expanded.getByTitle('Timeframe da estratégia')).toHaveText('4h')
      }

      await assertNoSecondTimeframe(page)
    })

    test('timeframe filter lists Todos plus TFs present and filters rows', async ({ page }) => {
      await setupMonitor(page)
      await page.goto('/monitor')

      const filter = page.getByTestId('monitor-filter-timeframe')
      await expect(filter).toBeVisible()
      await expect(filter.locator('option')).toHaveText(['Timeframe: Todos', '4h', '1d'])

      const btc = isMobile(project.width)
        ? page.getByTestId('monitor-card-btc-usdt')
        : page.getByTestId('monitor-row-btc-usdt')
      const eth = isMobile(project.width)
        ? page.getByTestId('monitor-card-eth-usdt')
        : page.getByTestId('monitor-row-eth-usdt')

      await expect(btc).toBeVisible()
      await expect(eth).toBeVisible()

      await filter.selectOption('4h')
      await expect(btc).toBeVisible()
      await expect(eth).toHaveCount(0)

      await filter.selectOption('1d')
      await expect(eth).toBeVisible()
      await expect(btc).toHaveCount(0)

      await filter.selectOption('all')
      await expect(btc).toBeVisible()
      await expect(eth).toBeVisible()
    })

    test('Abrir gráfico and Ver Trades stay on the strategy TF without a selector', async ({ page }) => {
      const mocks = await setupMonitor(page)
      await page.goto('/monitor')

      await openBtcChart(page, project.width, 'chart')
      await assertChartLockedToStrategy(page)
      await expect.poll(() => mocks.candleRequests.some((item) => item.symbol === 'BTC/USDT' && item.timeframe === '4h')).toBe(true)
      await expect.poll(() => mocks.candleRequests.some((item) => item.symbol === 'BTC/USDT' && item.timeframe === '1d' && item.limit !== '14')).toBe(false)

      if (isMobile(project.width)) {
        await expect(page.getByTestId('monitor-card-btc-usdt').getByTitle('Timeframe da estratégia')).toHaveText('4h')
      } else {
        await expect(page.getByTestId('monitor-pair-tf-btc-usdt')).toHaveText('4h')
      }

      await page.getByTestId('chart-modal-close').click()
      await expect(page.getByTestId('chart-modal')).toHaveCount(0)

      await openBtcChart(page, project.width, 'trades')
      await assertChartLockedToStrategy(page)
    })

    if (!isMobile(project.width)) {
      test('minichart column stays named Gráfico and loads strategy TF candles', async ({ page }) => {
        const mocks = await setupMonitor(page)
        await page.goto('/monitor')

        await expect(page.locator('table.signals th.col-spark').first()).toHaveText('Gráfico')
        await expect(page.getByRole('columnheader', { name: 'Gráfico' }).first()).toBeVisible()
        await expect(page.getByRole('columnheader', { name: 'Status' }).first()).toBeVisible()
        await expect(page.getByRole('columnheader', { name: 'Preço' }).first()).toBeVisible()
        await expect(page.getByRole('columnheader', { name: 'Distância' }).first()).toBeVisible()
        await expect(page.getByRole('columnheader', { name: 'Par / Estratégia' }).first()).toBeVisible()

        await expect.poll(() =>
          mocks.candleRequests.some((item) => item.symbol === 'BTC/USDT' && item.timeframe === '4h' && item.limit === '14'),
        ).toBe(true)
        await expect.poll(() =>
          mocks.candleRequests.some((item) => item.symbol === 'ETH/USDT' && item.timeframe === '1d' && item.limit === '14'),
        ).toBe(true)

        await expect(page.getByRole('img', { name: 'Minigráfico BTC/USDT 4h' })).toBeVisible({ timeout: 10_000 })
        await expect(page.getByRole('img', { name: 'Minigráfico ETH/USDT 1d' })).toBeVisible({ timeout: 10_000 })
      })
    }
  })
}
