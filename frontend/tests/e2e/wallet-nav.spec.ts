import { expect, test } from '@playwright/test'
import fs from 'node:fs'
import path from 'node:path'

async function setupApiMocks(page: any) {
  // Block all external network; allow local dev server.
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
          {
            asset: 'HBAR',
            free: 0.103,
            locked: 896,
            total: 896.103,
            price_usdt: 0.1,
            value_usd: 89.61,
            avg_cost_usdt: 0.08,
            pnl_usd: 17.92,
            pnl_pct: 25.0,
          },
          {
            asset: 'USDC',
            free: 0.455,
            locked: 0,
            total: 0.455,
            price_usdt: 1,
            value_usd: 0.455,
            avg_cost_usdt: 1.0,
            pnl_usd: 0.0,
            pnl_pct: 0.0,
          },
        ],
        total_usd: 90.065,
      }),
    })
  )
}

test('menu: Carteira -> loads and shows balances (with screenshots)', async ({ page }, testInfo) => {
  await setupApiMocks(page)

  // Save evidence outside Playwright's ephemeral output so it can be linked from tracking.
  const evidenceDir = path.resolve(process.cwd(), '..', 'qa_artifacts', 'playwright', 'wallet')
  fs.mkdirSync(evidenceDir, { recursive: true })

  await page.goto('/')
  await expect(page.getByRole('navigation', { name: 'Navegação principal' })).toBeVisible()

  await page.screenshot({ path: path.join(evidenceDir, '01-home.png'), fullPage: true })

  await page
    .getByRole('navigation', { name: 'Navegação principal' })
    .getByRole('link', { name: 'Carteira', exact: true })
    .click()
  await expect(page).toHaveURL(/\/external\/balances/)

  await expect(page.getByRole('heading', { name: 'Carteira' })).toBeVisible()

  // Wait for wallet rows using locators scoped to the balances section so
  // strict mode doesn't collide with duplicated asset labels elsewhere.
  const balancesSection = page.locator('div').filter({
    has: page.getByRole('heading', { name: 'Balances', exact: true }),
  }).first()

  await expect(
    balancesSection.locator('div').filter({
      has: page.getByText('HBAR', { exact: true }),
      hasText: '896.103',
    }).first()
  ).toBeVisible()
  await expect(
    balancesSection.locator('div').filter({
      has: page.getByText('USDC', { exact: true }),
      hasText: '0.455',
    }).first()
  ).toBeVisible()

  // Total should be formatted with 2 decimals (JS float rounding can yield 90.06 for 90.065)
  await expect(page.getByText(/90\.0(6|7)/)).toBeVisible()

  await page.screenshot({ path: path.join(evidenceDir, '02-wallet-loaded.png'), fullPage: true })
})
