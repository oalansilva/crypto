import { expect, test } from '@playwright/test'

const AUTH_USER = {
  id: 'test-user',
  email: 'qa@test.com',
  name: 'QA User',
  isAdmin: false,
}

async function mockAuthenticatedSession(page: any) {
  await page.addInitScript((user) => {
    window.localStorage.setItem('auth_access_token', 'test-access-token')
    window.localStorage.setItem('auth_refresh_token', 'test-refresh-token')
    window.localStorage.setItem('auth_user', JSON.stringify(user))
  }, AUTH_USER)

  await page.route('**/api/auth/me', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(AUTH_USER),
    })
  })
}

test('card #92 requires a single consolidated signal per asset on /ai-dashboard', async ({ page }) => {
  await mockAuthenticatedSession(page)

  await page.route('**/api/ai/dashboard', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        generated_at: '2026-04-14T19:00:00.000Z',
        insights: [],
        fear_greed: { value: 64, label: 'Greed', tone: 'bullish' },
        indicators: [],
        recent_signals: [
          { id: 'btc-ai', asset: 'BTCUSDT', action: 'BUY', confidence: 84, reason: 'AI bullish' },
          { id: 'eth-ai', asset: 'ETHUSDT', action: 'HOLD', confidence: 61, reason: 'AI neutral' },
        ],
        stats: { hit_rate: 62, total_signals: 2, avg_confidence: 72 },
        news: [],
        section_errors: {},
      }),
    })
  })

  await page.goto('/ai-dashboard')

  await expect(page.getByText('AI Dashboard').first()).toBeVisible()

  // Acceptance criteria from card #92:
  // one consolidated signal per asset, with clear direction/strength and expandable source breakdown.
  await expect(page.getByText(/sinal consolidado/i)).toBeVisible()
  await expect(page.getByText(/força/i)).toBeVisible()

  const btc = page.getByText('BTCUSDT').first()
  await expect(btc).toBeVisible()

  await expect(page.getByText(/2\/3|3\/3|1\/3|0\/3/).first()).toBeVisible()

  await btc.click()

  await expect(page.getByText(/fontes do sinal/i)).toBeVisible()
  await expect(page.getByText(/\bAI\b/)).toBeVisible()
  await expect(page.getByText(/On-?chain/i)).toBeVisible()
  await expect(page.getByText(/\bSignals\b/i)).toBeVisible()
})
