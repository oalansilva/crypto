import { expect, test } from '@playwright/test'

async function setupApiMocks(page: any) {
  await page.route('**/*', (route: any) => {
    const url = new URL(route.request().url())
    if (url.hostname === '127.0.0.1' || url.hostname === 'localhost') {
      return route.continue()
    }
    return route.abort('blockedbyclient')
  })

  await page.route('**/api/onchain/glassnode/BTC/supply-distribution**', async (route: any) => {
    const url = new URL(route.request().url())
    const window = url.searchParams.get('window') || '24h'
    const multiplier = window === '30d' ? 3 : window === '7d' ? 2 : 1

    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        asset: 'BTC',
        basis: 'entity',
        window,
        interval: '24h',
        since: 1777161600,
        until: 1777248000,
        cached: false,
        bands: [
          {
            id: 'shrimp',
            label: '< 1 BTC',
            min_btc: 0,
            max_btc: 1,
            latest: 1120000,
            previous: 1118000,
            change_abs: 2000 * multiplier,
            change_pct: 0.18 * multiplier,
            share_pct: 6.1,
          },
          {
            id: 'whales',
            label: '1k+ BTC',
            min_btc: 1000,
            max_btc: null,
            latest: 7420000,
            previous: 7400000,
            change_abs: 20000 * multiplier,
            change_pct: 0.27 * multiplier,
            share_pct: 40.2,
          },
        ],
        cohorts: {
          shrimps: { latest: 1120000, previous: 1118000, change_abs: 2000, change_pct: 0.18, share_pct: 6.1 },
          whales: { latest: 7420000, previous: 7400000, change_abs: 20000, change_pct: 0.27, share_pct: 40.2 },
          hodlers: { latest: 14800000, previous: 14750000, change_abs: 50000, change_pct: 0.34, share_pct: 74.8 },
        },
        whale_movement: {
          threshold_btc: 1000,
          change_abs: 20000 * multiplier,
          direction: 'accumulation',
          alert: true,
        },
        alerts: [{ type: 'whale-alert', threshold_btc: 1000, change_abs: 20000 * multiplier, direction: 'accumulation' }],
        sources: { glassnode: { metric: 'supply_distribution' } },
      }),
    })
  })
}

test('Supply distribution dashboard renders cohorts, bands, window filter, and whale alert', async ({ page }) => {
  await setupApiMocks(page)

  await page.goto('/supply-distribution')

  await expect(page.getByRole('heading', { name: 'Distribuição de supply' })).toBeVisible()
  await expect(page.getByRole('button', { name: '24h' })).toBeVisible()
  await expect(page.getByText('Shrimps')).toBeVisible()
  await expect(page.getByText('Whales')).toBeVisible()
  await expect(page.getByText('Hodlers')).toBeVisible()
  await expect(page.getByTestId('supply-band-shrimp')).toContainText('< 1 BTC')
  await expect(page.getByTestId('supply-band-whales')).toContainText('1k+ BTC')
  await expect(page.getByText('Whale alert')).toBeVisible()
  await expect(page.getByText('Ativo')).toBeVisible()

  await page.getByRole('button', { name: '7d' }).click()
  await expect(page.getByRole('button', { name: '7d' })).toHaveClass(/border-emerald/)
  await expect(page.getByText('40.000 BTC')).toBeVisible()

  await page
    .getByRole('navigation', { name: 'Navegação principal' })
    .getByRole('link', { name: 'Distribuição', exact: true })
    .click()
  await expect(page).toHaveURL(/\/supply-distribution/)
})
