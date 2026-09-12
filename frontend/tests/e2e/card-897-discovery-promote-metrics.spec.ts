import { expect, test, type Page } from '@playwright/test'

const AUTH_USER = {
  id: 'admin-user',
  email: 'admin@example.com',
  name: 'Alan Silva',
  isAdmin: true,
  mustChangePassword: false,
}

const SNAPSHOT_193 = {
  sharpe_ratio: 0.31,
  win_rate: 0.467,
  total_return: 169.51,
  total_return_pct: 16951,
  max_drawdown: 0.165,
  total_trades: 30,
  profit_factor: 1.42,
}

const CURRENT_TRADES = Array.from({ length: 12 }, (_, index) => ({
  entry_time: `2026-01-${String(index + 1).padStart(2, '0')}T00:00:00Z`,
  entry_price: 100,
  exit_time: `2026-01-${String(index + 1).padStart(2, '0')}T12:00:00Z`,
  exit_price: index === 0 ? 86.08 : 101,
  profit: index === 0 ? -0.1392 : 0.01,
  type: 'long',
}))

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

const FAVORITES = [
  {
    id: 193,
    name: 'ALPHA Descoberta',
    symbol: 'ALPHA/USDT',
    timeframe: '1d',
    strategy_name: 'bollinger_breakout',
    strategy_display_name: 'Bandas: expansão',
    strategy_description: 'Bandas: expansão · promovido da Descoberta.',
    parameters: { direction: 'long' },
    metrics: {
      origin_type: 'discovery_sweep',
      sweep_id: 'sw-193',
      result_id: 'RS-B109ED2C80',
      strategy_identity_key: 'id-193',
      evidence_fingerprint: 'fp-193',
      metrics_snapshot: SNAPSHOT_193,
      promoted_at: '2026-09-11T00:00:00Z',
    },
    notes: 'descoberta',
    created_at: '2026-09-11T00:00:00Z',
    tier: 3,
    notify_telegram: true,
    start_date: '2020-10-10',
    end_date: '2024-02-01',
    period_type: 'all',
  },
  {
    id: 9,
    name: 'BTC Combo',
    symbol: 'BTC/USDT',
    timeframe: '1d',
    strategy_name: 'multi_ma_crossover',
    strategy_display_name: 'Médias: Virada Inicial',
    parameters: { direction: 'long', ema_short: 9, sma_medium: 21 },
    metrics: {
      sharpe_ratio: 0.5,
      win_rate: 0.583,
      total_return: 199.27,
      total_return_pct: 19927,
      max_drawdown: 0.122,
      total_trades: 72,
      profit_factor: 1.9,
    },
    notes: 'combo-saved',
    created_at: '2026-09-10T00:00:00Z',
    tier: 1,
    notify_telegram: true,
    start_date: '2022-01-01',
    end_date: '2026-01-01',
    period_type: 'all',
  },
]

async function mockAuth(page: Page) {
  await page.addInitScript((user) => {
    window.localStorage.setItem('auth_access_token', 'test-access-token')
    window.localStorage.setItem('auth_refresh_token', 'test-refresh-token')
    window.localStorage.setItem('auth_user', JSON.stringify(user))
  }, AUTH_USER)
}

async function mockFavoritesApi(page: Page) {
  await mockAuth(page)
  let favorites = JSON.parse(JSON.stringify(FAVORITES))

  await page.route('**/*', (route) => {
    const url = new URL(route.request().url())
    if (url.hostname === '127.0.0.1' || url.hostname === 'localhost') {
      return route.continue()
    }
    return route.abort('blockedbyclient')
  })

  await page.route(/\/api\/favorites\/?$/, (route) => {
    if (route.request().method() === 'GET') {
      return route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(favorites),
      })
    }
    return route.continue()
  })

  await page.route(/.*\/api\/favorites\/(\d+)\/trades$/, (route) => {
    const url = new URL(route.request().url())
    const favoriteId = Number(url.pathname.match(/\/favorites\/(\d+)\/trades$/)?.[1] ?? 193)
    const favorite = favorites.find((item: { id: number }) => item.id === favoriteId)
    const isDiscovery = favorite?.metrics?.origin_type === 'discovery_sweep'
    const metrics = {
      ...(favorite?.metrics || {}),
      ...(isDiscovery ? SNAPSHOT_193 : {}),
      trades: isDiscovery ? CURRENT_TRADES : [],
      trades_history_cached: true,
      analysis_candles: CANDLES,
      analysis_indicator_data: {},
      analysis_execution_mode: 'fast_1d',
    }
    favorites = favorites.map((item: { id: number }) => (
      item.id === favoriteId ? { ...item, metrics } : item
    ))
    return route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        favorite_id: favoriteId,
        trades: metrics.trades,
        metrics,
        metrics_match: true,
        metrics_deltas: {},
        regenerated: true,
        candles: CANDLES,
        indicator_data: {},
        execution_mode: 'fast_1d',
      }),
    })
  })

  await page.route(/\/api\/market\/candles(?:\?.*)?$/, (route) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ candles: CANDLES }),
    }),
  )

  await page.route(/\/api\/opportunities\/?(?:\?.*)?$/, (route) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify([]),
    }),
  )
}

const VIEWPORTS = [
  { name: 'desktop', width: 1280, height: 800 },
  { name: 'mobile', width: 390, height: 844 },
] as const

for (const viewport of VIEWPORTS) {
  test.describe(`card 897 ${viewport.name}`, () => {
    test.use({ viewport: { width: viewport.width, height: viewport.height } })

    test(`proto /favorites matches landmarks and filled #193 (${viewport.name})`, async ({ page }) => {
      await page.goto('/prototypes/card-897-discovery-promote-metrics/')
      await expect(page.getByRole('heading', { name: 'Estratégias favoritas' })).toBeVisible()
      await expect(page.locator('table.fav-strategies')).toBeAttached()
      if (viewport.name === 'desktop') {
        await expect(page.locator('table.fav-strategies th.symbol-col')).toHaveText('Symbol')
        await expect(page.locator('table.fav-strategies th.strategy-col')).toHaveText('Estratégia')
        await expect(page.locator('table.fav-strategies th.actions-col')).toHaveText('Ações')
      }

      const discovery = page.getByTestId(viewport.name === 'mobile' ? 'favorite-193-mobile' : 'favorite-193')
      await expect(discovery).toBeVisible()
      await expect(discovery.locator('[data-metric="sharpe"]')).toContainText('0,31')
      await expect(discovery.locator('[data-metric="trades"]')).toContainText('30')
      await expect(discovery.locator('[data-metric="return"]')).toContainText('+16.951%')
      await expect(discovery.locator('[data-metric="win"]')).toContainText('46,7%')
      await expect(discovery.locator('[data-metric="maxdd"]')).toContainText('16,5%')

      const combo = page.getByTestId(viewport.name === 'mobile' ? 'favorite-combo-mobile' : 'favorite-combo')
      await expect(combo).toBeVisible()
      await expect(combo).toHaveAttribute('data-origin', 'combo')
    })

    test(`proto /combo/results extra has snapshot summary and window labels (${viewport.name})`, async ({ page }) => {
      await page.goto('/prototypes/card-897-discovery-promote-metrics/analise.html')
      await expect(page.getByTestId('summary-window-label')).toHaveText(
        'Resumo · janela de treino da Descoberta · 10/10/2020 → 01/02/2024',
      )
      await expect(page.getByTestId('trades-window-label')).toHaveText(
        'Lista de operações · velas atuais · 12 negócios — não é a janela da Descoberta',
      )
      await expect(page.locator('[data-metric="return"]')).toContainText('+16.951%')
      await expect(page.locator('[data-metric="win"]')).toContainText('46,7%')
      await expect(page.locator('[data-metric="maxdd"]')).toContainText('16,5%')
      await expect(page.locator('[data-metric="maxdd"]')).not.toContainText('Indisponível')
      await expect(page.locator('[data-metric="trades"]')).toHaveText('30')
    })

    test(`live /favorites fills discovery snapshot and keeps combo-saved (${viewport.name})`, async ({ page }) => {
      await mockFavoritesApi(page)
      await page.goto('/favorites')
      await expect(page.getByRole('heading', { name: 'Estratégias favoritas' })).toBeVisible()
      await expect(page.locator('table.fav-strategies')).toBeAttached()

      const discovery = page.getByTestId(viewport.name === 'mobile' ? 'favorite-193-mobile' : 'favorite-193')
      await expect(discovery).toBeVisible()
      await expect(discovery).toHaveAttribute('data-origin', 'discovery')
      await expect(discovery.locator('[data-metric="sharpe"]')).toContainText('0.31')
      await expect(discovery.locator('[data-metric="trades"]')).toContainText('30')
      await expect(discovery.locator('[data-metric="return"]')).toContainText('+16951.00%')
      await expect(discovery.locator('[data-metric="sharpe"]')).not.toHaveText('-')
      await expect(discovery.locator('[data-metric="trades"]')).not.toHaveText('0')
      if (viewport.name === 'desktop') {
        await expect(discovery.locator('[data-metric="win"]')).toContainText('46.70%')
        await expect(discovery.locator('[data-metric="maxdd"]')).toContainText('16.50%')
      }

      const combo = page.getByTestId(viewport.name === 'mobile' ? 'favorite-9-mobile' : 'favorite-9')
      await expect(combo).toBeVisible()
      await expect(combo).toHaveAttribute('data-origin', 'combo')
      await expect(combo.locator('[data-metric="sharpe"]')).toContainText('0.50')
      await expect(combo.locator('[data-metric="trades"]')).toContainText('72')
      await expect(combo.locator('[data-metric="return"]')).toContainText('+19927.00%')
    })

    test(`opening analysis keeps snapshot on grid and labels current-candle list (${viewport.name})`, async ({ page }) => {
      await mockFavoritesApi(page)
      await page.goto('/favorites')
      const openChart = viewport.name === 'mobile'
        ? page.getByTestId('favorite-193-mobile').getByRole('button', { name: 'Analisar' })
        : page.getByTestId('open-chart-193')
      await expect(openChart).toBeVisible()
      await openChart.click()

      await expect(page).toHaveURL(/\/combo\/results/)
      await expect(page.getByTestId('summary-window-label')).toHaveText(
        'Resumo · janela de treino da Descoberta · 10/10/2020 → 01/02/2024',
      )
      await expect(page.getByTestId('combo-result-summary').locator('[data-metric="return"]')).toContainText('16951')
      await expect(page.getByTestId('combo-result-summary').locator('[data-metric="win"]')).toContainText('46.7%')
      await expect(page.getByTestId('combo-result-summary').locator('[data-metric="maxdd"]')).toContainText('16.5%')
      await expect(page.getByTestId('combo-result-summary').locator('[data-metric="maxdd"]')).not.toContainText('Indisponível')
      await expect(page.getByTestId('combo-result-summary').locator('[data-metric="trades"]')).toHaveText('30')
      await expect(page.getByTestId('trades-window-label')).toHaveText(
        'Lista de operações · velas atuais · 12 negócios — não é a janela da Descoberta',
      )

      await page.getByRole('button', { name: 'Voltar aos favoritos' }).click()
      await expect(page).toHaveURL(/\/favorites/)
      const discovery = page.getByTestId(viewport.name === 'mobile' ? 'favorite-193-mobile' : 'favorite-193')
      await expect(discovery.locator('[data-metric="sharpe"]')).toContainText('0.31')
      await expect(discovery.locator('[data-metric="trades"]')).toContainText('30')
      await expect(discovery.locator('[data-metric="return"]')).toContainText('+16951.00%')
    })
  })
}
