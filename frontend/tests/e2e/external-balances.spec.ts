import { expect, test } from '@playwright/test'

async function setupApiMocks(page: any) {
  await page.route('**/*', (route: any) => {
    const url = new URL(route.request().url())
    if (url.hostname === '127.0.0.1' || url.hostname === 'localhost') {
      return route.continue()
    }
    return route.abort('blockedbyclient')
  })

  await page.route('**/api/external/binance/spot/balances', (route: any) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        balances: [
          { asset: 'HBAR', free: 0.103, locked: 896, total: 896.103, price_usdt: 0.1, value_usd: 89.61, avg_cost_usdt: 0.08, pnl_usd: 17.92, pnl_pct: 25.0 },
          { asset: 'USDC', free: 0.455, locked: 0, total: 0.455, price_usdt: 1, value_usd: 0.455, avg_cost_usdt: 1.0, pnl_usd: 0.0, pnl_pct: 0.0 },
        ],
        total_usd: 90.065,
      }),
    })
  )
}

test('external balances page loads and shows balances', async ({ page }) => {
  await setupApiMocks(page)
  await page.goto('/external/balances')

  await expect(page.getByRole('heading', { name: 'Carteira' })).toBeVisible()

  // Column headers (regression: PnL columns present)
  await expect(page.getByText('Avg Cost (USDT)')).toBeVisible()
  await expect(page.getByText('PnL (USD)')).toBeVisible()
  await expect(page.getByText('PnL (%)')).toBeVisible()

  // Rows present
  await expect(page.getByText('HBAR', { exact: true })).toBeVisible()
  await expect(page.getByText('USDC', { exact: true })).toBeVisible()

  // Values render/formatted
  await expect(page.getByText('89.61')).toBeVisible() // HBAR value_usd (toFixed(2))
  await expect(page.getByText('0.08')).toBeVisible() // HBAR avg_cost_usdt
  await expect(page.getByText('17.92')).toBeVisible() // HBAR pnl_usd (toFixed(2))
  await expect(page.getByText('25.00')).toBeVisible() // HBAR pnl_pct (toFixed(2))
})
