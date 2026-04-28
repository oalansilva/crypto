import fs from 'node:fs'
import path from 'node:path'
import { expect, test } from '@playwright/test'

async function blockExternalNetwork(page: any) {
  await page.route('**/*', (route: any) => {
    const url = new URL(route.request().url())
    if (url.hostname === '127.0.0.1' || url.hostname === 'localhost') {
      return route.continue()
    }
    return route.abort('blockedbyclient')
  })
}

async function mockMonitorApi(page: any) {
  await page.route('**/api/opportunities/?tier=*', (route: any) => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify([]),
    })
  })

  await page.route('**/api/monitor/preferences', (route: any) => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({}),
    })
  })

  await page.route('**/api/user/binance-credentials', (route: any) => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ configured: false, api_key_masked: null }),
    })
  })

  await page.route('**/api/external/binance/spot/balances**', (route: any) => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ balances: [], total_usd: 0, as_of: '2026-04-28T00:00:00Z' }),
    })
  })
}

async function mockLoginSuccess(page: any) {
  await page.route('**/api/auth/login', (route: any) => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        accessToken: 'test-access-token',
        refreshToken: 'test-refresh-token',
        id: 'test-user',
        email: 'test@example.com',
        name: 'Test User',
        isAdmin: false,
      }),
    })
  })
}

test('raiz autenticada deve abrir no Monitor', async ({ page }) => {
  const evidenceDir = path.resolve(process.cwd(), '..', 'qa_artifacts', 'playwright', 'issue-68')
  fs.mkdirSync(evidenceDir, { recursive: true })

  await blockExternalNetwork(page)
  await mockMonitorApi(page)

  await page.goto('/')

  await expect(page).toHaveURL('/monitor')
  await expect(page.getByTestId('monitor-status-tab')).toBeVisible()
  await page.screenshot({ path: path.join(evidenceDir, '01-root-to-monitor.png'), fullPage: true })
})

test('login deve redirecionar para /monitor', async ({ page }) => {
  const evidenceDir = path.resolve(process.cwd(), '..', 'qa_artifacts', 'playwright', 'issue-68')
  fs.mkdirSync(evidenceDir, { recursive: true })

  await blockExternalNetwork(page)
  await mockMonitorApi(page)
  await mockLoginSuccess(page)

  await page.route('**/api/auth/me', (route: any) => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ id: 'test-user', email: 'test@example.com', name: 'Test User', isAdmin: false }),
    })
  })

  await page.goto('/login')
  await page.getByPlaceholder('seu@email.com').fill('test@example.com')
  await page.getByPlaceholder('••••••••').first().fill('12345678')
  await page.locator('form').getByRole('button', { name: 'Entrar' }).click()

  await expect(page).toHaveURL('/monitor')
  await expect(page.getByTestId('monitor-status-tab')).toBeVisible()
  await page.screenshot({ path: path.join(evidenceDir, '02-login-to-monitor.png'), fullPage: true })
})
