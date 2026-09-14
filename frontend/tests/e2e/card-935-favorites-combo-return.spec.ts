import { expect, test, type Locator, type Page } from '@playwright/test'

const AUTH_USER = {
  id: 'admin-user',
  email: 'admin@example.com',
  name: 'Alan Silva',
  isAdmin: true,
  mustChangePassword: false,
}

const CANDLES = Array.from({ length: 40 }, (_, index) => {
  const open = 100 + index * 0.4
  const close = open + (index % 2 === 0 ? 0.8 : -0.3)
  return {
    timestamp_utc: new Date(Date.UTC(2026, 0, index + 1)).toISOString(),
    open,
    high: Math.max(open, close) + 1,
    low: Math.min(open, close) - 1,
    close,
    volume: 900 + index * 10,
  }
})

const SOL_TRADES = Array.from({ length: 32 }, (_, index) => ({
  entry_time: `2024-03-${String((index % 28) + 1).padStart(2, '0')}T00:00:00Z`,
  entry_price: 80 + index,
  exit_time: `2024-03-${String((index % 28) + 1).padStart(2, '0')}T12:00:00Z`,
  exit_price: index < 10 ? 70 : 90 + index,
  profit: index < 10 ? -0.05 : 0.08,
  type: 'long',
}))

const ETH_TRADES = Array.from({ length: 18 }, (_, index) => ({
  entry_time: `2025-02-${String((index % 28) + 1).padStart(2, '0')}T00:00:00Z`,
  entry_price: 3000 + index,
  exit_time: `2025-02-${String((index % 28) + 1).padStart(2, '0')}T12:00:00Z`,
  exit_price: 3100 + index,
  profit: 0.02,
  type: 'long',
}))

const SOL_METRICS = {
  sharpe_ratio: 0.45,
  win_rate: 0.6875,
  total_return: 985.9156,
  total_return_pct: 98591.56,
  max_drawdown: 0.1415,
  total_trades: 32,
  avg_profit: 30.81,
  profit_factor: 2.1,
}

const ETH_METRICS = {
  sharpe_ratio: 1.12,
  win_rate: 0.611,
  total_return: 0.35,
  total_return_pct: 35,
  max_drawdown: 0.08,
  total_trades: 18,
  avg_profit: 0.0194,
}

const CONTRACT_METRICS = {
  sharpe_ratio: 0.31,
  win_rate: 0.467,
  total_return: 169.51,
  total_return_pct: 16951,
  max_drawdown: 0.165,
  total_trades: 30,
}

const FAVORITES = [
  {
    id: 935,
    name: 'SOL Médias Confirmada',
    symbol: 'SOL/USDT',
    timeframe: '1d',
    strategy_name: 'multi_ma_crossover',
    strategy_display_name: 'Médias Móveis: Tendência Confirmada',
    parameters: { direction: 'long', ema_short: 9, sma_medium: 21 },
    metrics: {
      ...SOL_METRICS,
      trades: SOL_TRADES,
      trades_history_cached: true,
      analysis_candles: CANDLES,
      analysis_indicator_data: {},
      analysis_execution_mode: 'favorite_cache',
    },
    notes: 'combo-saved',
    created_at: '2026-09-13T00:00:00Z',
    tier: 3,
    notify_telegram: false,
    start_date: '2020-01-01',
    end_date: '2026-09-01',
  },
  {
    id: 36,
    name: 'ETH +35%',
    symbol: 'ETH/USDT',
    timeframe: '1d',
    strategy_name: 'multi_ma_crossover',
    strategy_display_name: 'Médias: Virada Inicial',
    parameters: { direction: 'long' },
    metrics: {
      ...ETH_METRICS,
      trades: ETH_TRADES,
      trades_history_cached: true,
      analysis_candles: CANDLES,
      analysis_indicator_data: {},
      analysis_execution_mode: 'favorite_cache',
    },
    notes: 'combo-saved small compound',
    created_at: '2026-09-10T00:00:00Z',
    tier: 1,
    notify_telegram: false,
  },
  {
    id: 193,
    name: 'ALPHA Descoberta',
    symbol: 'ALPHA/USDT',
    timeframe: '1d',
    strategy_name: 'bollinger_breakout',
    strategy_display_name: 'Bandas: expansão',
    parameters: { direction: 'long' },
    metrics: {
      origin_type: 'discovery_sweep',
      metrics_snapshot: CONTRACT_METRICS,
      trades: [],
      trades_history_cached: true,
      analysis_candles: CANDLES,
    },
    notes: 'descoberta com retorno visível',
    created_at: '2026-09-11T00:00:00Z',
    tier: 2,
    notify_telegram: false,
    start_date: '2020-10-10',
    end_date: '2024-02-01',
  },
  {
    id: 897,
    name: 'BTC sem métricas',
    symbol: 'BTC/USDT',
    timeframe: '1d',
    strategy_name: 'ema_rsi',
    strategy_display_name: 'EMA RSI',
    parameters: { direction: 'long' },
    metrics: { origin_type: 'discovery_sweep' },
    notes: 'métrica ausente permanece #897',
    created_at: '2026-09-09T00:00:00Z',
    tier: 3,
    notify_telegram: false,
  },
]

const OPPORTUNITIES = [
  {
    id: 935,
    symbol: 'SOL/USDT',
    asset_type: 'crypto',
    timeframe: '1d',
    template_name: 'multi_ma_crossover',
    strategy_display_name: 'Médias Móveis: Tendência Confirmada',
    name: 'SOL Médias Confirmada',
    notes: '',
    tier: 3,
    parameters: { direction: 'long' },
    is_holding: false,
    distance_to_next_status: 13.38,
    next_status_label: 'entry',
    status: 'WAIT',
    message: 'Aguardando compra',
    last_price: 105.39,
    timestamp: '2026-09-13T00:00:00Z',
    details: {},
    distance_to_stop_pct: 35.21,
  },
  {
    id: 36,
    symbol: 'ETH/USDT',
    asset_type: 'crypto',
    timeframe: '1d',
    template_name: 'multi_ma_crossover',
    strategy_display_name: 'Médias: Virada Inicial',
    name: 'ETH +35%',
    notes: '',
    tier: 1,
    parameters: { direction: 'long' },
    is_holding: false,
    distance_to_next_status: 4.2,
    next_status_label: 'entry',
    status: 'WAIT',
    message: 'Aguardando compra',
    last_price: 3412,
    timestamp: '2026-09-13T00:00:00Z',
    details: {},
    distance_to_stop_pct: 9.1,
  },
]

async function mockAuth(page: Page) {
  await page.addInitScript((user) => {
    window.localStorage.setItem('auth_access_token', 'test-access-token')
    window.localStorage.setItem('auth_refresh_token', 'test-refresh-token')
    window.localStorage.setItem('auth_user', JSON.stringify(user))
  }, AUTH_USER)
}

async function dismissOnboarding(page: Page) {
  const dismiss = page.getByRole('button', { name: 'Dispensar' })
  if (await dismiss.isVisible().catch(() => false)) {
    await dismiss.click()
  }
}

async function mockAppApis(page: Page) {
  await mockAuth(page)

  await page.route('**/*', (route) => {
    const url = new URL(route.request().url())
    if (url.hostname === '127.0.0.1' || url.hostname === 'localhost') {
      return route.continue()
    }
    return route.abort('blockedbyclient')
  })

  await page.route(/\/api\/auth\/me$/, (route) =>
    route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(AUTH_USER) }),
  )

  await page.route(/\/api\/favorites\/?$/, (route) =>
    route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(FAVORITES) }),
  )

  await page.route(/\/api\/favorites\/(\d+)\/trades$/, (route) => {
    const favoriteId = Number(new URL(route.request().url()).pathname.match(/\/favorites\/(\d+)\/trades$/)?.[1] ?? 935)
    const favorite = FAVORITES.find((item) => item.id === favoriteId) ?? FAVORITES[0]
    const metrics = favorite.metrics || {}
    const trades = Array.isArray(metrics.trades) ? metrics.trades : []
    return route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        favorite_id: favoriteId,
        trades,
        metrics,
        metrics_match: true,
        metrics_deltas: {},
        candles: CANDLES,
        indicator_data: {},
        execution_mode: 'favorite_cache',
      }),
    })
  })

  await page.route(/\/api\/opportunities\/?(?:\?.*)?$/, (route) =>
    route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(OPPORTUNITIES) }),
  )

  await page.route(/\/api\/market\/candles(?:\?.*)?$/, (route) =>
    route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ candles: CANDLES }) }),
  )

  await page.route(/\/api\/monitor\/preferences/, (route) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        __global__: { in_portfolio: false, card_mode: 'strategy', price_timeframe: '1d', theme: 'dark-green' },
        'SOL/USDT': { in_portfolio: true, card_mode: 'strategy', price_timeframe: '1d', theme: 'dark-green' },
        'ETH/USDT': { in_portfolio: true, card_mode: 'strategy', price_timeframe: '1d', theme: 'dark-green' },
      }),
    }),
  )

  await page.route(/\/api\/user\/binance-credentials$/, (route) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ configured: false, api_key_masked: null }),
    }),
  )
}

async function expectLargeCompound(locator: Locator) {
  await expect(locator).toBeVisible()
  await expect(locator).toContainText(/98\.?591/)
  await expect(locator).not.toHaveText(/^\s*\+?985[.,]\d{2}%\s*$/)
}

async function expectSmallCompound(locator: Locator) {
  await expect(locator).toBeVisible()
  await expect(locator).toContainText('+35')
  await expect(locator).not.toContainText('0.35%')
  await expect(locator).not.toContainText('3500')
}

async function expectSixteenThousand(locator: Locator) {
  await expect(locator).toBeVisible()
  await expect(locator).toContainText(/16\.?951/)
  await expect(locator).not.toHaveText(/^\s*\+?169[.,]51%?\s*$/)
}

const VIEWPORTS = [
  { name: 'desktop', width: 1280, height: 800 },
  { name: 'mobile', width: 390, height: 844 },
] as const

for (const viewport of VIEWPORTS) {
  test.describe(`card 935 ${viewport.name}`, () => {
    test.use({ viewport: { width: viewport.width, height: viewport.height } })

    test(`proto /favorites matches landmarks and canonical RETURN (${viewport.name})`, async ({ page }) => {
      await page.goto('/prototypes/card-935-favorites-combo-return/')
      await expect(page.getByRole('heading', { name: 'Estratégias favoritas' })).toBeVisible()
      await expect(page.locator('table.fav-strategies')).toBeAttached()
      if (viewport.name === 'desktop') {
        await expect(page.locator('table.fav-strategies th.symbol-col')).toHaveText('Symbol')
        await expect(page.locator('table.fav-strategies th.strategy-col')).toHaveText('Estratégia')
        await expect(page.locator('table.fav-strategies th.actions-col')).toHaveText('Ações')
      }

      const sol = page.getByTestId(viewport.name === 'mobile' ? 'favorite-sol-mobile' : 'favorite-sol-incident')
      await expect(sol).toBeVisible()
      await expectLargeCompound(sol.locator('[data-metric="return"]'))
      await expect(sol.locator('[data-metric="sharpe"]')).toContainText('0,45')
      await expect(sol.locator('[data-metric="trades"]')).toContainText('32')
      await expect(sol.locator('[data-metric="win"]')).toContainText('68,75%')
      await expect(sol.locator('[data-metric="maxdd"]')).toContainText('14,15%')

      const eth = page.getByTestId(viewport.name === 'mobile' ? 'favorite-small-mobile' : 'favorite-small-compound')
      await expectSmallCompound(eth.locator('[data-metric="return"]'))
    })

    test(`proto /combo/results extra keeps large compound (${viewport.name})`, async ({ page }) => {
      await page.goto('/prototypes/card-935-favorites-combo-return/analise.html')
      await expect(page.locator('.combo-page')).toBeVisible()
      await expect(page.getByRole('heading', { name: 'Médias Móveis: Tendência Confirmada' })).toBeVisible()
      await expectLargeCompound(page.getByTestId('combo-result-summary').locator('[data-metric="return"]'))
      await expect(page.getByTestId('combo-result-summary').locator('[data-metric="win"]')).toContainText('68,75%')
      await expect(page.getByTestId('combo-result-summary').locator('[data-metric="maxdd"]')).toContainText('14,15%')
      await expect(page.getByTestId('combo-result-summary').locator('[data-metric="trades"]')).toHaveText('32')
      await expect(page.getByRole('link', { name: 'Voltar aos favoritos' })).toBeVisible()
    })

    test(`proto /monitor Ver Trades shows the same compound (${viewport.name})`, async ({ page }) => {
      await page.goto('/prototypes/card-935-favorites-combo-return/monitor.html')
      await expect(page.locator('table.signals')).toBeAttached()
      await expect(page.getByRole('columnheader', { name: 'Status' })).toBeVisible()
      await expect(page.getByRole('columnheader', { name: 'Preço' })).toBeVisible()
      await expect(page.getByRole('columnheader', { name: 'Distância' })).toBeVisible()
      await expect(page.getByRole('columnheader', { name: 'Operar' })).toBeVisible()

      await page.getByRole('button', { name: 'Ver Trades SOL/USDT' }).click()
      const modal = page.getByTestId('chart-modal-trades')
      await expect(modal).toBeVisible()
      await expectLargeCompound(modal.locator('[data-metric="return"]'))
      await expect(modal.locator('[data-metric="win"]')).toContainText('68,75%')
      await expect(modal.locator('[data-metric="trades"]')).toHaveText('32')
      await expect(page.locator('body')).not.toContainText('985,85')

      await page.getByTestId('chart-modal-close').click()
      await page.getByRole('button', { name: 'Ver Trades ETH/USDT' }).click()
      await expectSmallCompound(page.getByTestId('chart-modal-trades').locator('[data-metric="return"]'))
    })

    test(`live /favorites + analysis + back keep the large compound (${viewport.name})`, async ({ page }) => {
      await mockAppApis(page)
      await page.goto('/favorites')
      await dismissOnboarding(page)
      await expect(page.getByRole('heading', { name: 'Estratégias favoritas' })).toBeVisible()
      await expect(page.locator('table.fav-strategies')).toBeAttached()

      const sol = page.getByTestId(viewport.name === 'mobile' ? 'favorite-935-mobile' : 'favorite-935')
      await expect(sol).toBeVisible()
      await expectLargeCompound(sol.locator('[data-metric="return"]'))
      await expect(sol.locator('[data-metric="sharpe"]')).toContainText('0.45')
      await expect(sol.locator('[data-metric="trades"]')).toContainText('32')
      if (viewport.name === 'desktop') {
        await expect(sol.locator('[data-metric="win"]')).toContainText('68.75%')
        await expect(sol.locator('[data-metric="maxdd"]')).toContainText('14.15%')
      }

      const eth = page.getByTestId(viewport.name === 'mobile' ? 'favorite-36-mobile' : 'favorite-36')
      await expectSmallCompound(eth.locator('[data-metric="return"]'))

      const discovery = page.getByTestId(viewport.name === 'mobile' ? 'favorite-193-mobile' : 'favorite-193')
      await expectSixteenThousand(discovery.locator('[data-metric="return"]'))

      const missing = page.getByTestId(viewport.name === 'mobile' ? 'favorite-897-mobile' : 'favorite-897')
      const missingReturn = (await missing.locator('[data-metric="return"]').innerText()).replace(/\s+/g, '')
      expect(missingReturn === '-' || missingReturn.endsWith('-')).toBeTruthy()
      expect(missingReturn).not.toMatch(/\d/)

      const openChart = viewport.name === 'mobile'
        ? page.getByTestId('favorite-935-mobile').getByRole('button', { name: 'Analisar' })
        : page.getByTestId('open-chart-935')
      await openChart.click()
      await expect(page).toHaveURL(/\/combo\/results/)
      const summary = page.getByTestId('combo-result-summary')
      await expectLargeCompound(summary.locator('[data-metric="return"]'))
      await expect(summary.locator('[data-metric="win"]')).toContainText('68.75%')
      await expect(summary.locator('[data-metric="maxdd"]')).toContainText('14.15%')
      await expect(summary.locator('[data-metric="trades"]')).toHaveText('32')
      await expect(page.locator('body')).not.toContainText('985.85%')

      await page.getByRole('button', { name: 'Voltar aos favoritos' }).click()
      await expect(page).toHaveURL(/\/favorites/)
      await expectLargeCompound(page.getByTestId(viewport.name === 'mobile' ? 'favorite-935-mobile' : 'favorite-935').locator('[data-metric="return"]'))
    })

    test(`live /monitor Ver Trades Retorno total matches the grade (${viewport.name})`, async ({ page }) => {
      await mockAppApis(page)
      await page.goto('/monitor')
      await dismissOnboarding(page)
      await expect(page.getByTestId('monitor-status-tab')).toBeVisible()
      await expect(page.locator('table.signals').first()).toBeAttached()

      if (viewport.name === 'desktop') {
        await expect(page.getByTestId('monitor-row-sol-usdt')).toBeVisible()
        await expect(page.getByRole('columnheader', { name: 'Status' }).first()).toBeVisible()
        await expect(page.getByRole('columnheader', { name: 'Preço' }).first()).toBeVisible()
        await expect(page.getByRole('columnheader', { name: 'Distância' }).first()).toBeVisible()
        await page.getByRole('button', { name: 'Ver Trades SOL/USDT' }).click()
      } else {
        await expect(page.getByTestId('monitor-card-sol-usdt')).toBeVisible()
        await page.getByTestId('monitor-card-sol-usdt').getByRole('button', { name: 'Ver Trades' }).click()
      }

      const trades = page.getByTestId('chart-modal-trades')
      await expect(trades).toBeVisible()
      await expectLargeCompound(trades.locator('[data-metric="return"]'))
      await expect(trades.locator('[data-metric="win"]')).toContainText('68.75%')
      await expect(trades.locator('[data-metric="trades"]')).toHaveText('32')
      await expect(page.locator('body')).not.toContainText('985.85%')

      await page.getByTestId('chart-modal-close').click()
      if (viewport.name === 'desktop') {
        await page.getByRole('button', { name: 'Ver Trades ETH/USDT' }).click()
      } else {
        await page.getByTestId('monitor-card-eth-usdt').getByRole('button', { name: 'Ver Trades' }).click()
      }
      await expectSmallCompound(page.getByTestId('chart-modal-trades').locator('[data-metric="return"]'))
    })
  })
}
