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

  await page.route('**/api/user/binance-credentials', (route: any) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ configured: false, api_key_masked: null }),
    })
  )
}

test('external balances page loads and shows balances', async ({ page }) => {
  await setupApiMocks(page)
  await page.goto('/external/balances')

  await expect(page.getByRole('heading', { name: 'Carteira', exact: true })).toBeVisible()

  await expect(page.getByText('Total USD')).toBeVisible()
  await expect(page.getByText('PnL parcial')).toBeVisible()
  await expect(page.getByText('Locked only')).toHaveCount(0)
  await expect(page.getByText('Locked USD')).toHaveCount(0)
  await expect(page.getByRole('button', { name: 'Locked' })).toHaveCount(0)
  await expect(page.getByText('Locked', { exact: true })).toHaveCount(0)

  // Rows present
  await expect(page.getByRole('row', { name: /HBAR.*896\.103/ })).toBeVisible()
  await expect(page.getByRole('row', { name: /USDC.*0\.455/ })).toBeVisible()

  // Values render/formatted in the desktop table row.
  const hbarRow = page.getByRole('row', { name: /HBAR.*896\.103/ })
  await expect(hbarRow.getByText('$89.61')).toBeVisible()
  await expect(hbarRow.getByText('$0.08')).toBeVisible()
  await expect(hbarRow.getByText('+$17.92')).toBeVisible()
  await expect(hbarRow.getByText('+25.00%')).toBeVisible()
})

test('wallet credentials form asks for Binance API credentials, not login credentials', async ({ page }) => {
  await setupApiMocks(page)

  await page.goto('/external/balances')

  const apiKey = page.getByLabel('Binance API Key read-only')
  const apiSecret = page.getByLabel('Binance API Secret read-only')

  await expect(page.getByText('O Cripto Farol não solicita e-mail nem senha da Binance.')).toBeVisible()
  await expect(apiKey).toHaveAttribute('placeholder', 'API Key read-only da Binance')
  await expect(apiKey).toHaveAttribute('autocomplete', 'off')
  await expect(apiKey).toHaveAttribute('data-lpignore', 'true')
  await expect(apiSecret).toHaveAttribute('placeholder', 'API Secret da chave read-only')
  await expect(apiSecret).toHaveAttribute('autocomplete', 'new-password')
  await expect(apiSecret).toHaveAttribute('data-lpignore', 'true')

  await apiKey.fill('alan@example.com')
  await apiSecret.fill('senha-da-binance')
  await page.getByRole('button', { name: /Salvar credenciais/ }).click()

  await expect(page.getByText('Este campo não aceita e-mail.')).toBeVisible()
})
