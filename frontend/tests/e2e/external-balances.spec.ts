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
          { asset: 'HBAR', free: 0.103, locked: 896, total: 896.103 },
          { asset: 'USDC', free: 0.455, locked: 0, total: 0.455 },
        ],
      }),
    })
  )
}

test('external balances page loads and shows balances', async ({ page }) => {
  await setupApiMocks(page)
  await page.goto('/external/balances')

  await expect(page.getByText('External Balances')).toBeVisible()
  await expect(page.getByText('HBAR', { exact: true })).toBeVisible()
  await expect(page.getByText('USDC', { exact: true })).toBeVisible()
})
