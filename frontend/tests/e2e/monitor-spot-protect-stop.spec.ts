import { expect, test, type Page } from '@playwright/test'

const AUTH_USER = {
  id: 'spot-protect-user',
  email: 'spot.protect@example.com',
  name: 'Spot Protect',
  isAdmin: false,
  mustChangePassword: false,
}

async function mockAuthenticatedSession(page: Page) {
  await page.addInitScript((user) => {
    window.localStorage.setItem('auth_access_token', 'test-access-token')
    window.localStorage.setItem('auth_refresh_token', 'test-refresh-token')
    window.localStorage.setItem('auth_user', JSON.stringify(user))
  }, AUTH_USER)
}

test('Proteção Spot: place e remove stop-limit no gráfico long HOLD', async ({ page }) => {
  await mockAuthenticatedSession(page)

  let placed = false

  await page.route('**/api/**', async (route) => {
    const url = route.request().url()
    const method = route.request().method()

    if (url.includes('/api/auth/me')) {
      await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(AUTH_USER) })
      return
    }
    if (url.includes('/api/user/binance-credentials')) {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ configured: true, api_key_masked: 'ABCD****WXYZ' }),
      })
      return
    }
    if (url.includes('/api/monitor/preferences')) {
      await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({}) })
      return
    }
    if (url.includes('/api/favorites')) {
      await route.fulfill({ status: 200, contentType: 'application/json', body: '[]' })
      return
    }
    if (url.includes('/api/opportunities')) {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify([
          {
            id: 11,
            symbol: 'ETH/USDT',
            asset_type: 'cryptomoeda',
            timeframe: '1d',
            direction: 'long',
            template_name: 'ema',
            name: 'ETH Long',
            notes: '',
            tier: 1,
            is_holding: true,
            distance_to_next_status: 1,
            next_status_label: 'exit',
            status: 'HOLDING',
            last_price: 2000,
            timestamp: '2026-01-01T00:00:00Z',
            entry_price: 2100,
            stop_price: 2000,
            distance_to_stop_pct: 5,
            parameters: { stop_loss: 0.05, direction: 'long' },
            signal_history: [],
            details: {},
          },
        ]),
      })
      return
    }
    if (url.includes('/api/market/candles')) {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          candles: [
            { timestamp_utc: '2026-01-01T00:00:00Z', open: 2000, high: 2010, low: 1990, close: 2005, volume: 1 },
            { timestamp_utc: '2026-01-02T00:00:00Z', open: 2005, high: 2020, low: 2000, close: 2010, volume: 1 },
          ],
        }),
      })
      return
    }
    if (url.includes('/api/monitor/spot-stop-order')) {
      if (method === 'GET') {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            protected: placed,
            symbol: 'ETHUSDT',
            client_order_id: 'cfstop_test',
            order: placed
              ? { order_id: 1, stop_price: 2000, limit_price: 1998, quantity: 1.5, status: 'NEW' }
              : null,
          }),
        })
        return
      }
      if (method === 'POST') {
        placed = true
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            protected: true,
            symbol: 'ETHUSDT',
            quantity: 1.5,
            stop_price: 2000,
            limit_price: 1998,
            order_id: 1,
          }),
        })
        return
      }
      if (method === 'DELETE') {
        placed = false
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({ protected: false, symbol: 'ETHUSDT' }),
        })
        return
      }
    }

    await route.fulfill({ status: 200, contentType: 'application/json', body: '{}' })
  })

  await page.goto('/monitor')
  await expect(page.getByRole('button', { name: /Abrir Gráfico ETH\/USDT/i }).first()).toBeVisible({
    timeout: 20_000,
  })
  await page.getByRole('button', { name: /Abrir Gráfico ETH\/USDT/i }).first().click()

  const panel = page.getByTestId('spot-protect-stop-panel')
  await expect(panel).toBeVisible({ timeout: 15_000 })
  await expect(page.getByTestId('spot-protect-place')).toBeVisible()
  await page.getByTestId('spot-protect-place').click()
  await expect(page.getByTestId('spot-protect-confirm')).toBeVisible()
  await page.getByTestId('spot-protect-confirm-yes').click()
  await expect(page.getByTestId('spot-protect-remove')).toBeVisible({ timeout: 10_000 })
  await page.getByTestId('spot-protect-remove').click()
  await expect(page.getByTestId('spot-protect-place')).toBeVisible({ timeout: 10_000 })
})
