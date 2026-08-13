import { expect, test, type Page } from '@playwright/test'

const noGoResult = {
  template_name: 'Teste Walk Forward',
  symbol: 'BTC/USDT',
  timeframe: '1d',
  start_date: '2024-01-01',
  end_date: '2026-08-13',
  period_type: '2y',
  parameters: { direction: 'long' },
  metrics: {
    total_trades: 20,
    win_rate: 0.55,
    total_return: 0.2,
    avg_profit: 0.01,
    sharpe_ratio: 0.5,
    max_drawdown: 0.1,
  },
  trades: [],
  indicator_data: {},
  candles: [],
  oos_metrics: { total_trades: 10, sharpe_ratio: 0.3 },
  oos_proof: 'signed-oos-proof',
  oos_verdict: {
    status: 'NO-GO',
    reasons: ['Sharpe baixo'],
    split_train_ratio: 0.7,
  },
}

async function openResult(page: Page, isOptimization: boolean) {
  await page.goto('/combo/results')
  await page.evaluate(
    ({ result, isOptimization }) => {
      history.replaceState(
        { usr: { result, isOptimization, returnTo: isOptimization ? '/combo/configure' : '/favorites' }, key: 'card-470', idx: 0 },
        '',
        location.href,
      )
    },
    { result: noGoResult, isOptimization },
  )
  await page.reload()
  await expect(page.getByTestId('combo-result-oos-comparison')).toBeVisible()
}

test('NO-GO promotion is blocked for a common user on desktop and mobile', async ({ page }) => {
  for (const viewport of [{ width: 1440, height: 900 }, { width: 390, height: 844 }]) {
    await page.setViewportSize(viewport)
    await openResult(page, true)
    await page.getByTestId('save-favorite-button').click()

    await expect(page.getByRole('heading', { name: 'Salvar nos Favoritos' })).toBeVisible()
    await expect(page.getByTestId('oos-gate-block').getByText('Sharpe baixo')).toBeVisible()
    await expect(page.getByText(/override de admin/)).toHaveCount(0)
    await expect(page.getByRole('button', { name: 'Salvar', exact: true })).toBeDisabled()
  }
})

test('admin can explicitly override NO-GO and period metadata is preserved', async ({ page }) => {
  await page.addInitScript(() => {
    localStorage.setItem('auth_access_token', 'test-access-token')
    localStorage.setItem('auth_refresh_token', 'test-refresh-token')
    localStorage.setItem('auth_user', JSON.stringify({
      id: 'admin',
      email: 'admin@example.com',
      name: 'Admin',
      isAdmin: true,
      mustChangePassword: false,
    }))
  })
  await page.route('**/api/favorites', async route => {
    const payload = route.request().postDataJSON()
    expect(payload.override_oos).toBe(true)
    expect(payload.start_date).toBe(noGoResult.start_date)
    expect(payload.end_date).toBe(noGoResult.end_date)
    expect(payload.period_type).toBe(noGoResult.period_type)
    expect(payload.oos_proof).toBe(noGoResult.oos_proof)
    await route.fulfill({ status: 201, contentType: 'application/json', body: JSON.stringify({ id: 470 }) })
  })

  await openResult(page, true)
  await page.getByTestId('save-favorite-button').click()
  await page.getByText(/override de admin/).click()
  await expect(page.getByRole('button', { name: 'Salvar', exact: true })).toBeEnabled()
  await page.getByRole('button', { name: 'Salvar', exact: true }).click()
  await expect(page).toHaveURL(/\/favorites$/)
})

test('existing favorite analysis does not offer duplicate promotion', async ({ page }) => {
  await openResult(page, false)
  await expect(page.getByTestId('save-favorite-button')).toHaveCount(0)
})

test('admin revalidates an existing favorite and sees the non-destructive report', async ({ page }) => {
  await page.addInitScript(() => {
    localStorage.setItem('auth_access_token', 'test-access-token')
    localStorage.setItem('auth_refresh_token', 'test-refresh-token')
    localStorage.setItem('auth_user', JSON.stringify({
      id: 'admin',
      email: 'admin@example.com',
      name: 'Admin',
      isAdmin: true,
      mustChangePassword: false,
    }))
  })
  await page.route('**/api/favorites/', route => route.fulfill({
    status: 200,
    contentType: 'application/json',
    body: JSON.stringify([{
      id: 470,
      name: 'BTC Walk Forward',
      symbol: 'BTC/USDT',
      timeframe: '1d',
      strategy_name: 'ema_rsi',
      parameters: { direction: 'long' },
      metrics: { total_return: 0.2, total_trades: 20, win_rate: 0.55, sharpe_ratio: 0.5 },
      created_at: '2026-08-13T00:00:00Z',
      tier: 1,
      notify_telegram: true,
    }]),
  }))
  await page.route('**/api/favorites/470/revalidate', route => route.fulfill({
    status: 200,
    contentType: 'application/json',
    body: JSON.stringify({
      favorite_id: 470,
      symbol: 'BTC/USDT',
      timeframe: '1d',
      strategy_name: 'ema_rsi',
      verdict: 'NO-GO',
      window: { start: '2026-05-15', end: '2026-08-13' },
      revalidation: {
        best_metrics: { total_trades: 20, sharpe_ratio: 0.5 },
        oos_metrics: { total_trades: 5, sharpe_ratio: 0.2 },
        oos_verdict: { status: 'NO-GO', reasons: ['Poucos trades'] },
      },
    }),
  }))

  await page.goto('/favorites')
  await page.getByRole('button', { name: 'Revalidar na janela recente' }).click()
  const report = page.getByTestId('revalidation-report-modal')
  await expect(report).toBeVisible()
  await expect(report.getByText('BTC/USDT · 1d · 2026-05-15 a 2026-08-13')).toBeVisible()
  await expect(report.getByText('Poucos trades')).toBeVisible()
  await expect(report.getByText(/parâmetros e ativação permanecem inalterados/)).toBeVisible()
  await expect(report).toHaveAttribute('role', 'dialog')
  await page.keyboard.press('Escape')
  await expect(report).toHaveCount(0)
})
