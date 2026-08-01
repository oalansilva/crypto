import { expect, test } from '@playwright/test'

async function setupAuth(page: any) {
  await page.addInitScript(() => {
    const user = {
      id: 'admin-user',
      email: 'admin@example.com',
      name: 'Admin User',
      isAdmin: true,
    }
    window.localStorage.setItem('auth_access_token', 'test-access-token')
    window.localStorage.setItem('auth_refresh_token', 'test-refresh-token')
    window.localStorage.setItem('auth_user', JSON.stringify(user))
  })
  await page.route('**/api/auth/me', (route: any) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        id: 'admin-user',
        email: 'admin@example.com',
        name: 'Admin User',
        isAdmin: true,
      }),
    })
  )
  await page.route('**/api/opportunities/?tier=*', (route: any) =>
    route.fulfill({ status: 200, contentType: 'application/json', body: '[]' })
  )
  await page.route('**/api/monitor/preferences', (route: any) =>
    route.fulfill({ status: 200, contentType: 'application/json', body: '{}' })
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

test('legacy /kanban redirects to /monitor without board UI', async ({ page }) => {
  await setupAuth(page)
  await page.goto('/kanban')
  await expect(page).toHaveURL(/\/monitor$/)
  await expect(page.getByTestId('monitor-status-tab')).toBeVisible()
  await expect(page.getByRole('heading', { name: 'Kanban', exact: true })).toHaveCount(0)
})
