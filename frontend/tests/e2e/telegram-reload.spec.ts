import { expect, test, type Page } from '@playwright/test'

const AUTH_USER = {
  id: 'telegram-reload-user',
  email: 'o.alan.silva@gmail.com',
  name: 'Alan Silva',
  isAdmin: false,
  mustChangePassword: false,
}

async function blockExternalNetwork(page: Page) {
  await page.route('**/*', (route) => {
    const url = new URL(route.request().url())
    if (url.hostname === '127.0.0.1' || url.hostname === 'localhost') {
      return route.continue()
    }
    return route.abort('blockedbyclient')
  })
}

async function setAuthenticatedSession(page: Page) {
  await page.addInitScript((user) => {
    window.localStorage.setItem('auth_access_token', 'e2e-token')
    window.localStorage.setItem('auth_refresh_token', 'e2e-refresh-token')
    window.localStorage.setItem('auth_user', JSON.stringify(user))
  }, AUTH_USER)
}

async function installTelegramReloadMocks(page: Page, overrides?: { telegramAlertsEnabled?: boolean }) {
  await blockExternalNetwork(page)
  await setAuthenticatedSession(page)

  await page.route('**/api/auth/me', (route) =>
    route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(AUTH_USER) }),
  )
  await page.route('**/api/users/me', (route) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        id: AUTH_USER.id,
        email: AUTH_USER.email,
        name: AUTH_USER.name,
        createdAt: '2025-01-01T00:00:00Z',
        lastLogin: '2025-01-15T12:00:00Z',
      }),
    }),
  )
  await page.route('**/api/users/me/telegram-settings', (route) => {
    return route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        telegramUsername: 'oalansilva',
        telegramAlertsEnabled: overrides?.telegramAlertsEnabled ?? true,
        linked: true,
        linkedAt: '2026-08-27T00:50:58.000Z',
        usernameMismatch: false,
        botUsername: 'Criptofarol_bot',
        hasPendingLinkToken: false,
      }),
    })
  })
  // minimal mocks for monitor/profile to avoid 500s
  await page.route('**/api/monitor/preferences', (route) =>
    route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({}) }),
  )
  await page.route('**/api/user/binance-credentials', (route) =>
    route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ configured: false }) }),
  )
  await page.route('**/api/**', (route) => {
    // fallback for other api calls (opportunities etc) — return empty ok to let profile render
    if (route.request().url().includes('/api/users/me/telegram-settings')) return route.fallback()
    return route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({}) })
  })
}

test.describe('card-749 telegram reload', () => {
  test('profile reload with linked:true shows Vinculado and toggle on', async ({ page }) => {
    await installTelegramReloadMocks(page, { telegramAlertsEnabled: true })
    await page.goto('/profile')
    const form = page.getByTestId('telegram-alerts-form')
    await expect(form).toBeVisible({ timeout: 10_000 })
    await expect(form.getByText('Status: Vinculado')).toBeVisible()
    await expect(page.getByTestId('telegram-alerts-enabled')).toBeChecked()
    await expect(form.getByText(/Vinculado em/)).toBeVisible()
    await expect(form.getByText('Bot: @Criptofarol_bot')).toBeVisible()

    await page.reload()
    await expect(form).toBeVisible()
    await expect(form.getByText('Status: Vinculado')).toBeVisible()
    await expect(page.getByTestId('telegram-alerts-enabled')).toBeChecked()
  })

  test('profile reload preserves Vinculado without extra interaction (no Save click)', async ({ page }) => {
    await installTelegramReloadMocks(page, { telegramAlertsEnabled: false })
    await page.goto('/profile')
    const form = page.getByTestId('telegram-alerts-form')
    await expect(form.getByText('Status: Vinculado')).toBeVisible()
    await expect(page.getByTestId('telegram-alerts-enabled')).not.toBeChecked()

    await page.reload()
    await expect(form).toBeVisible()
    await expect(form.getByText('Status: Vinculado')).toBeVisible()
    await expect(page.getByTestId('telegram-alerts-enabled')).not.toBeChecked()
  })

  test('monitor and profile share same telegramAlertsEnabled flag', async ({ page }) => {
    // mock PATCH to echo back toggled value
    await installTelegramReloadMocks(page, { telegramAlertsEnabled: true })
    let currentEnabled = true
    await page.route('**/api/users/me/telegram-settings', async (route) => {
      if (route.request().method() === 'PATCH') {
        const body = route.request().postDataJSON() as { telegramAlertsEnabled?: boolean }
        if (typeof body?.telegramAlertsEnabled === 'boolean') currentEnabled = body.telegramAlertsEnabled
        return route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            telegramUsername: 'oalansilva',
            telegramAlertsEnabled: currentEnabled,
            linked: true,
            linkedAt: '2026-08-27T00:50:58.000Z',
            usernameMismatch: false,
            botUsername: 'Criptofarol_bot',
            hasPendingLinkToken: false,
          }),
        })
      }
      return route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          telegramUsername: 'oalansilva',
          telegramAlertsEnabled: currentEnabled,
          linked: true,
          linkedAt: '2026-08-27T00:50:58.000Z',
          usernameMismatch: false,
          botUsername: 'Criptofarol_bot',
          hasPendingLinkToken: false,
        }),
      })
    })

    await page.goto('/profile')
    await expect(page.getByTestId('telegram-alerts-form')).toBeVisible()
    await expect(page.getByTestId('telegram-alerts-enabled')).toBeChecked()

    await page.goto('/monitor')
    const toggle = page.getByTestId('monitor-telegram-alerts-toggle')
    await expect(toggle).toBeVisible()
    await expect(toggle).toHaveText('Telegram: on')

    // toggle off in monitor
    await toggle.click()
    await expect(toggle).toHaveText('Telegram: off')

    // back to profile → should be off now
    await page.goto('/profile')
    await expect(page.getByTestId('telegram-alerts-form')).toBeVisible()
    await expect(page.getByTestId('telegram-alerts-enabled')).not.toBeChecked()
  })
})
