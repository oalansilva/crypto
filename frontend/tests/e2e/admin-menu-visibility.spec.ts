import { expect, test } from '@playwright/test'

type TestUser = {
  id: string
  email: string
  name: string
  isAdmin: boolean
}

const adminOnlyLabels = ['Favoritos', 'Combo', 'Backtests', 'Histórico', 'Distribuicao', 'Backfill']

async function setupAuthenticatedUser(page: any, user: TestUser) {
  await page.addInitScript((authUser: TestUser) => {
    window.localStorage.setItem('auth_access_token', 'test-access-token')
    window.localStorage.setItem('auth_refresh_token', 'test-refresh-token')
    window.localStorage.setItem('auth_user', JSON.stringify(authUser))
  }, user)

  await page.route('**/*', (route: any) => {
    const url = new URL(route.request().url())
    if (url.hostname === '127.0.0.1' || url.hostname === 'localhost') {
      return route.continue()
    }
    return route.abort('blockedbyclient')
  })

  await page.route('**/api/auth/me', (route: any) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(user),
    })
  )

  await page.route('**/api/opportunities/?tier=*', (route: any) =>
    route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify([]) })
  )

  await page.route('**/api/monitor/preferences', (route: any) =>
    route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({}) })
  )

  await page.route('**/api/user/binance-credentials', (route: any) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ configured: false, api_key_masked: null }),
    })
  )

  await page.route('**/api/external/binance/spot/balances**', (route: any) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ balances: [], total_usd: 0, as_of: '2026-05-01T00:00:00Z' }),
    })
  )
}

test('common user does not see admin-only navigation entries', async ({ page }) => {
  await setupAuthenticatedUser(page, {
    id: 'common-user',
    email: 'common@example.com',
    name: 'Common User',
    isAdmin: false,
  })

  await page.goto('/monitor')

  const navigation = page.getByRole('navigation', { name: 'Navegacao principal' })
  await expect(navigation.getByRole('link', { name: 'Monitor', exact: true })).toBeVisible()

  for (const label of adminOnlyLabels) {
    await expect(navigation.getByRole('link', { name: label, exact: true })).toHaveCount(0)
  }
})

test('common user direct admin route redirects to monitor', async ({ page }) => {
  await setupAuthenticatedUser(page, {
    id: 'common-user',
    email: 'common@example.com',
    name: 'Common User',
    isAdmin: false,
  })

  await page.goto('/combo/select')

  await expect(page).toHaveURL(/\/monitor$/)
  await expect(page.getByTestId('monitor-status-tab')).toBeVisible()
})

test('admin user sees admin-only navigation entries', async ({ page }) => {
  await setupAuthenticatedUser(page, {
    id: 'admin-user',
    email: 'admin@example.com',
    name: 'Admin User',
    isAdmin: true,
  })

  await page.goto('/monitor')

  const navigation = page.getByRole('navigation', { name: 'Navegacao principal' })

  for (const label of adminOnlyLabels) {
    await expect(navigation.getByRole('link', { name: label, exact: true })).toBeVisible()
  }
})
