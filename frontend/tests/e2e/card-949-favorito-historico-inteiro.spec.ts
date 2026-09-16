import { expect, test, type Page } from '@playwright/test'

const BASE = '/prototypes/card-949-favorito-historico-inteiro'

const viewports = [
  { name: 'desktop', width: 1440, height: 900 },
  { name: 'mobile', width: 390, height: 844 },
] as const

for (const viewport of viewports) {
  test.describe(`card-949 proto ${viewport.name}`, () => {
    test.use({ viewport: { width: viewport.width, height: viewport.height } })

    test('index — períodos BTC novo, legado e Combo 2 anos', async ({ page }) => {
      await page.goto(`${BASE}/`)
      await expect(page.getByRole('heading', { name: 'Estratégias favoritas' })).toBeVisible()
      if (viewport.name === 'desktop') {
        await expect(page.locator('table.fav-strategies')).toBeVisible()
      } else {
        await expect(page.locator("[data-testid='favorite-btc-new-mobile']")).toBeVisible()
      }

      const btcPeriod = page.locator("[data-testid='period-cell-btc-new'], [data-testid='period-btc-new'], [data-testid='period-btc-new-mobile']").first()
      const btcText = await btcPeriod.innerText()
      expect(btcText).toContain('17/08/2017 → 15/09/2026')
      expect(btcText).not.toContain('24/12/2023')

      const legacy = page.locator("[data-testid='period-cell-legacy'], [data-testid='period-legacy-mobile']").first()
      await expect(legacy).toContainText('17/08/2017 → 24/12/2023')

      const combo = page.locator("[data-testid='period-cell-combo-2y'], [data-testid='period-combo-2y-mobile']").first()
      const comboText = await combo.innerText()
      expect(comboText).toContain('15/09/2024 → 15/09/2026')
      expect(comboText).not.toContain('17/08/2017')
    })

    test('descoberta — grelha 70/30 e promover sem preview do completo', async ({ page }) => {
      await page.goto(`${BASE}/descoberta.html`)
      await expect(page.getByText('Descoberta de estratégias swing')).toBeVisible()
      await expect(page.locator('[data-testid="wf-portrait"]')).toContainText('17/08/2017 → 24/12/2023')

      const promote = page.locator("[data-testid='decidir-promote-RS-949-BTC']")
      await promote.click()
      const modal = page.locator('#promotion-modal')
      await expect(modal).toBeVisible()
      const modalText = await modal.innerText()
      expect(modalText).toContain('17/08/2017 → 24/12/2023')
      expect(modalText).not.toMatch(/preview.*15\/09\/2026/i)
    })

    test('analise — período completo sem título de treino', async ({ page }) => {
      await page.goto(`${BASE}/analise.html`)
      await expect(page.locator('.combo-page')).toBeVisible()
      await expect(page.getByText('Lista de operações')).toBeVisible()
      const body = await page.locator('body').innerText()
      expect(body).toContain('17/08/2017 → 15/09/2026')
      expect(body).not.toContain('janela de treino da Descoberta')
    })

    test('combo — 2 anos completos e salvar', async ({ page }) => {
      await page.goto(`${BASE}/combo.html`)
      await expect(page.getByTestId('save-favorite-button')).toBeVisible()
      const body = await page.locator('body').innerText()
      expect(body).toContain('15/09/2024 → 15/09/2026')
      expect(body).not.toContain('17/08/2017 → 15/09/2026')
      await page.getByTestId('save-favorite-button').click()
      await expect(page.locator('[data-testid="save-period"]')).toContainText('15/09/2024 → 15/09/2026')
    })
  })
}

const AUTH_USER = {
  id: 'admin-user',
  email: 'admin@example.com',
  name: 'Alan Silva',
  isAdmin: true,
  mustChangePassword: false,
}

const OPERATIONAL_FAVORITE = {
  id: 949,
  name: 'BTC operacional',
  symbol: 'BTC/USDT',
  timeframe: '1d',
  strategy_name: 'multi_ma_crossover',
  strategy_display_name: 'Médias Móveis: Tendência em Virada',
  strategy_description: 'Promovido com período operacional pós walk-forward.',
  parameters: { direction: 'long', ema_short: 9, sma_medium: 21, sma_long: 50 },
  metrics: {
    origin_type: 'discovery_sweep',
    sweep_id: 'sw-949',
    result_id: 'RS-949',
    operational_period_after_walk_forward: true,
    metrics_snapshot: { total_trades: 30, sharpe_ratio: 0.31 },
    total_trades: 71,
    sharpe_ratio: 0.38,
    total_return_pct: 210.4,
    trades: [
      {
        entry_time: '2026-01-01T00:00:00Z',
        entry_price: 90000,
        exit_time: '2026-02-01T00:00:00Z',
        exit_price: 95000,
        profit: 0.05,
        type: 'long',
      },
    ],
  },
  notes: 'card-949 live e2e',
  created_at: '2026-09-15T00:00:00Z',
  tier: 3,
  notify_telegram: true,
  start_date: '2017-08-17',
  end_date: '2026-09-15',
  period_type: 'all',
}

async function mockCard949LiveApi(page: Page) {
  await page.addInitScript((user) => {
    window.localStorage.setItem('auth_access_token', 'test-access-token')
    window.localStorage.setItem('auth_refresh_token', 'test-refresh-token')
    window.localStorage.setItem('auth_user', JSON.stringify(user))
  }, AUTH_USER)

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
        body: JSON.stringify([OPERATIONAL_FAVORITE]),
      })
    }
    return route.continue()
  })
}

for (const viewport of viewports) {
  test.describe(`card-949 live ${viewport.name}`, () => {
    test.use({ viewport: { width: viewport.width, height: viewport.height } })

    test('favorites — período operacional na app React', async ({ page }) => {
      await mockCard949LiveApi(page)
      await page.goto('/favorites')
      await expect(page.getByRole('heading', { name: 'Estratégias favoritas' })).toBeVisible()

      const favorite = page.getByTestId(viewport.name === 'mobile' ? 'favorite-949-mobile' : 'favorite-949')
      await expect(favorite).toBeVisible()
      if (viewport.name === 'desktop') {
        await expect(favorite).toContainText('17/08/2017')
        await expect(favorite).toContainText('15/09/2026')
        await expect(favorite).not.toContainText('24/12/2023')
      } else {
        await expect(favorite).toHaveAttribute('data-origin', 'discovery')
        await expect(favorite.locator('[data-metric="trades"]')).toContainText('71')
      }
    })

    test('combo/results — análise operacional sem label de treino', async ({ page }) => {
      await mockCard949LiveApi(page)
      await page.goto('/favorites')
      const openChart = viewport.name === 'mobile'
        ? page.getByTestId('favorite-949-mobile').getByRole('button', { name: 'Analisar' })
        : page.getByTestId('open-chart-949')
      await openChart.click()

      await expect(page).toHaveURL(/\/combo\/results/)
      await expect(page.getByTestId('combo-result-summary')).toBeVisible()
      await expect(page.getByTestId('summary-window-label')).toHaveCount(0)
      await expect(page.getByTestId('combo-result-title')).toBeVisible()
      await expect(page.locator('body')).not.toContainText('janela de treino da Descoberta')
    })

    test('combo/results — salvar favorito com gate walk-forward', async ({ page }) => {
      await page.addInitScript((user) => {
        window.localStorage.setItem('auth_access_token', 'test-access-token')
        window.localStorage.setItem('auth_refresh_token', 'test-refresh-token')
        window.localStorage.setItem('auth_user', JSON.stringify(user))
      }, AUTH_USER)

      const comboResult = {
        template_name: 'multi_ma_crossover',
        display_name: 'Médias Móveis: Tendência em Virada',
        symbol: 'BTC/USDT',
        timeframe: '1d',
        period_type: '2y',
        start_date: '2024-09-15',
        end_date: '2026-09-15',
        parameters: { direction: 'long', ema_short: 9, sma_medium: 21, sma_long: 50 },
        metrics: {
          total_trades: 42,
          win_rate: 0.55,
          total_return: 0.88,
          avg_profit: 0.02,
          sharpe_ratio: 0.62,
          max_drawdown: 0.1,
        },
        trades: [],
        indicator_data: {},
        candles: [],
        oos_verdict: { status: 'GO', reasons: ['ok'] },
        oos_metrics: { total_trades: 12, sharpe_ratio: 0.4 },
      }

      await page.goto('/combo/results')
      await page.evaluate(
        ({ result }) => {
          history.replaceState(
            { usr: { result, isOptimization: true, returnTo: '/combo' }, key: 'card-949-live', idx: 0 },
            '',
            location.href,
          )
        },
        { result: comboResult },
      )
      await page.reload()
      await expect(page.getByTestId('combo-result-oos-comparison')).toBeVisible()
      await page.getByTestId('save-favorite-button').click()
      await expect(page.getByTestId('oos-gate-block')).toContainText('GO no holdout')
      await expect(page.getByRole('heading', { name: 'Salvar nos Favoritos' })).toBeVisible()
    })
  })
}
