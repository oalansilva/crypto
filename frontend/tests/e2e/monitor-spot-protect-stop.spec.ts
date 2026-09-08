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
  let deleteCalls = 0

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
            managed_by_app: placed,
            source: placed ? 'app' : null,
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
        deleteCalls += 1
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
  // Card 861: remover exige confirmação — nenhum DELETE antes de confirmar
  await page.getByTestId('spot-protect-remove').click()
  await expect(page.getByTestId('spot-protect-remove-confirm')).toBeVisible()
  await expect(page.getByTestId('spot-protect-remove-confirm')).toContainText(/criada no app \(Farol\)/)
  expect(deleteCalls).toBe(0)
  await page.getByTestId('spot-protect-remove-confirm-yes').click()
  await expect(page.getByTestId('spot-protect-place')).toBeVisible({ timeout: 10_000 })
  expect(deleteCalls).toBe(1)
})

test('Venda travada pela stop: remover no fluxo e revender sem vender junto', async ({ page }) => {
  await mockAuthenticatedSession(page)

  let stopRemoved = false
  let previewCalls = 0
  let deleteCalls = 0
  let orderCalls = 0

  const btcOpportunity = {
    id: 21,
    symbol: 'BTC/USDT',
    asset_type: 'cryptomoeda',
    timeframe: '1d',
    direction: 'long',
    template_name: 'ema',
    name: 'BTC Long',
    notes: '',
    tier: 1,
    is_holding: true,
    distance_to_next_status: 1,
    next_status_label: 'exit',
    status: 'HOLDING',
    last_price: 100000,
    timestamp: '2026-01-01T00:00:00Z',
    entry_price: 95000,
    stop_price: 90000,
    distance_to_stop_pct: 10,
    parameters: { stop_loss: 0.1, direction: 'long' },
    signal_history: [],
    details: {},
  }

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
      await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify([btcOpportunity]) })
      return
    }
    if (url.includes('/api/monitor/spot-market-orders/eligibility')) {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ items: [{ symbol: 'BTC/USDT', eligible: true, reason: null }] }),
      })
      return
    }
    if (url.includes('/api/monitor/spot-market-orders/preview')) {
      previewCalls += 1
      if (previewCalls === 1) {
        await route.fulfill({
          status: 400,
          contentType: 'application/json',
          body: JSON.stringify({
            detail: {
              code: 'BINANCE_VALIDATION_ERROR',
              message: 'Quantidade abaixo do mínimo permitido pela Binance',
            },
          }),
        })
        return
      }
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          preview_token: 'preview-test-1',
          idempotency_key: 'idem-test-1',
          symbol: 'BTCUSDT',
          side: 'SELL',
          requested_quote_amount: null,
          base_balance: 0.5,
          calculated_base_quantity: 0.5,
          residual_quantity: 0,
          estimated_base_quantity: null,
          estimated_quote_amount: 50000,
          warning: 'Preço indicativo.',
        }),
      })
      return
    }
    if (url.includes('/api/monitor/spot-market-orders') && method === 'POST') {
      orderCalls += 1
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ state: 'filled' }),
      })
      return
    }
    if (url.includes('/api/monitor/spot-stop-order')) {
      if (method === 'GET') {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: stopRemoved
            ? JSON.stringify({ protected: false, symbol: 'BTCUSDT' })
            : JSON.stringify({
              protected: true,
              symbol: 'BTCUSDT',
              client_order_id: 'cfstop_test',
              managed_by_app: true,
              source: 'app',
              order: { order_id: 2, stop_price: 90000, limit_price: 89910, quantity: 0.5, status: 'NEW' },
            }),
        })
        return
      }
      if (method === 'DELETE') {
        deleteCalls += 1
        stopRemoved = true
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({ protected: false, symbol: 'BTCUSDT' }),
        })
        return
      }
    }

    await route.fulfill({ status: 200, contentType: 'application/json', body: '{}' })
  })

  await page.goto('/monitor')
  await page.locator('[data-testid="open-spot-trade-btc-usdt"]:visible').first().click()
  await page.getByRole('tab', { name: /Vender/ }).click()
  await page.getByTestId('spot-continue-order').click()

  // Venda trava pela stop: bloco próprio no fluxo
  await expect(page.getByTestId('spot-sell-stop-blocked')).toBeVisible({ timeout: 15_000 })
  await page.getByTestId('spot-sell-stop-remove').click()
  await expect(page.getByTestId('spot-sell-stop-remove-confirm')).toBeVisible()
  await expect(page.getByTestId('spot-sell-stop-remove-confirm')).toContainText(/criada no app \(Farol\)/)
  expect(deleteCalls).toBe(0)

  // Confirmar remove a stop e NÃO vende (prova por execução)
  await page.getByTestId('spot-sell-stop-confirm-yes').click()
  await expect(page.getByTestId('spot-sell-stop-removed')).toBeVisible({ timeout: 10_000 })
  expect(deleteCalls).toBe(1)
  expect(orderCalls).toBe(0)

  // Nova prévia recomeça o fluxo normal de venda
  await page.getByTestId('spot-repreview-order').click()
  await page.getByTestId('spot-continue-order').click()
  await expect(page.getByTestId('spot-confirm-order')).toBeVisible({ timeout: 10_000 })
  expect(orderCalls).toBe(0)
})

test('Proteção Spot: stop externo Binance bloqueia Proteger e oferece Remover', async ({ page }) => {
  await mockAuthenticatedSession(page)

  await page.route('**/api/**', async (route) => {
    const url = route.request().url()
    if (url.includes('/api/auth/me')) {
      await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(AUTH_USER) })
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
            stop_price: 1682.28,
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
          ],
        }),
      })
      return
    }
    if (url.includes('/api/monitor/spot-stop-order')) {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          protected: true,
          symbol: 'ETHUSDT',
          client_order_id: 'web_f8fe890af06c488c99f0dfe2f12f1a96',
          managed_by_app: false,
          source: 'external',
          order: {
            order_id: 48768780964,
            stop_price: 1682.28,
            limit_price: 1682.28,
            quantity: 0.0519,
            status: 'NEW',
          },
        }),
      })
      return
    }
    await route.fulfill({ status: 200, contentType: 'application/json', body: '{}' })
  })

  await page.goto('/monitor')
  await page.getByRole('button', { name: /Abrir Gráfico ETH\/USDT/i }).first().click()
  await expect(page.getByTestId('spot-protect-stop-panel')).toBeVisible({ timeout: 15_000 })
  await expect(page.getByTestId('spot-protect-summary')).toContainText(/1,?682\.28/)
  await expect(page.getByTestId('spot-protect-external-note')).toBeVisible()
  await expect(page.getByTestId('spot-protect-remove')).toBeVisible()
  await expect(page.getByTestId('spot-protect-place')).toHaveCount(0)
})
