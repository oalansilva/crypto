import { expect, test, type Page } from '@playwright/test'

const AUTH_USER = {
  id: 'card-1001-user',
  email: 'card1001@example.com',
  name: 'Card 1001',
  isAdmin: true,
  mustChangePassword: false,
}

const BTC_OPPORTUNITY = {
  id: 1001,
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
  last_price: 65000,
  timestamp: '2026-09-21T00:00:00Z',
  entry_price: 62000,
  stop_price: 61000,
  distance_to_stop_pct: 6.1,
  parameters: {},
  signal_history: [],
  details: {},
}

type ScalpState = 'off' | 'on' | 'kill' | 'nokey'

function statusBody(state: ScalpState) {
  const map = {
    off: {
      state: 'off',
      has_spot_key: true,
      jev_available: true,
      t_quote: '100',
      clip_quote: '10',
      inventory_btc: '0',
      calibration: null,
      pnl_quote: '0',
      status_text: 'Desligado — não envia ordem deste scalp. Inventário e P&L ficam visíveis.',
      kill_banner: false,
      inventory_clipped: false,
    },
    on: {
      state: 'on',
      has_spot_key: true,
      jev_available: true,
      t_quote: '100',
      clip_quote: '10',
      inventory_btc: '0.0012',
      calibration: { hits: 4, signals: 9, last_latency_s: 2 },
      pnl_quote: '-0.42',
      status_text:
        'Ligado — o primeiro ciclo (livro + Jev a tempo) pode enviar post-only sem confirmar cada ordem. Operar continua ao lado.',
      kill_banner: false,
      inventory_clipped: false,
    },
    kill: {
      state: 'kill',
      has_spot_key: true,
      jev_available: true,
      t_quote: '100',
      clip_quote: '10',
      inventory_btc: '0',
      calibration: { hits: 4, signals: 11, last_latency_s: 2 },
      pnl_quote: '-2',
      status_text: 'Parado por kill — sem envio. Inventário e P&L ficam visíveis. Religar é o interruptor.',
      kill_banner: true,
      inventory_clipped: false,
    },
    nokey: {
      state: 'nokey',
      has_spot_key: false,
      jev_available: false,
      t_quote: '0',
      clip_quote: '10',
      inventory_btc: '0',
      calibration: null,
      pnl_quote: '0',
      status_text: 'Sem chave Spot em Meu Perfil — não envia. Configure a chave Spot (a mesma do Operar).',
      kill_banner: false,
      inventory_clipped: false,
    },
  } as const
  return map[state]
}

async function mockAuthenticatedSession(page: Page) {
  await page.addInitScript((user) => {
    window.localStorage.setItem('auth_access_token', 'test-access-token')
    window.localStorage.setItem('auth_refresh_token', 'test-refresh-token')
    window.localStorage.setItem('auth_user', JSON.stringify(user))
    window.localStorage.setItem('cripto-farol-onboarding-dismissed', '1')
  }, AUTH_USER)
}

async function mockMonitorWithScalp(page: Page, initial: ScalpState = 'off') {
  let scalp = statusBody(initial)
  await page.route('**/api/**', async (route) => {
    const url = route.request().url()
    const method = route.request().method()
    if (url.includes('/api/auth/refresh')) {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          accessToken: 'test-access-token',
          refreshToken: 'test-refresh-token',
          id: AUTH_USER.id,
          userId: AUTH_USER.id,
          email: AUTH_USER.email,
          name: AUTH_USER.name,
          isAdmin: AUTH_USER.isAdmin,
          mustChangePassword: AUTH_USER.mustChangePassword,
          expiresIn: 3600,
        }),
      })
      return
    }
    if (url.includes('/api/auth/me')) {
      await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(AUTH_USER) })
      return
    }
    if (url.includes('/api/scalp/switch') && method === 'POST') {
      const body = route.request().postDataJSON() as { enabled?: boolean }
      scalp = statusBody(body?.enabled ? 'on' : 'off')
      await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(scalp) })
      return
    }
    if (url.includes('/api/scalp/status')) {
      await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(scalp) })
      return
    }
    if (url.includes('/api/favorites')) {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify([{
          id: 1001,
          name: 'BTC Long',
          symbol: 'BTC/USDT',
          timeframe: '1d',
          strategy_name: 'ema',
          parameters: { direction: 'long' },
          metrics: {},
          created_at: '2026-01-01T00:00:00Z',
          tier: 1,
        }]),
      })
      return
    }
    if (url.includes('/api/opportunities')) {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify([BTC_OPPORTUNITY]),
      })
      return
    }
    if (url.includes('/api/monitor/preferences')) {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          'BTC/USDT': { in_portfolio: true, card_mode: 'price', price_timeframe: '1d', theme: 'black' },
        }),
      })
      return
    }
    if (url.includes('/api/user/binance-credentials')) {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ configured: initial !== 'nokey', api_key_masked: initial === 'nokey' ? null : 'abcd****efgh' }),
      })
      return
    }
    if (url.includes('/api/external/binance/spot/balances')) {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          balances: [
            { asset: 'BTC', total: 0.02, free: 0.02 },
            { asset: 'USDT', total: 500, free: 500 },
          ],
          total_usd: 1800,
          as_of: '2026-09-21T00:00:00Z',
        }),
      })
      return
    }
    if (url.includes('/api/monitor/spot-market-orders/eligibility')) {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ items: [{ symbol: 'BTCUSDT', eligible: true, reason: null }] }),
      })
      return
    }
    if (url.includes('/api/users/me/telegram-settings')) {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ telegramAlertsEnabled: false }),
      })
      return
    }
    await route.fulfill({ status: 200, contentType: 'application/json', body: '{}' })
  })
}

async function assertBoardIntact(page: Page) {
  const width = page.viewportSize()?.width ?? 1280
  await expect(page.getByRole('button', { name: /Operar/ }).first()).toBeVisible()
  if (width > 740) {
    await expect(page.locator('table.signals').first()).toBeVisible()
    await expect(page.locator('table.signals th', { hasText: 'Status' }).first()).toBeVisible()
    await expect(page.locator('table.signals th', { hasText: 'Preço' }).first()).toBeVisible()
    await expect(page.locator('table.signals th', { hasText: 'Distância' }).first()).toBeVisible()
    await expect(page.locator('table.signals th', { hasText: 'Tags' }).first()).toBeAttached()
    await expect(page.locator('table.signals th', { hasText: 'Par / Estratégia' }).first()).toBeVisible()
  } else {
    await expect(page.locator('.mobile-cards .mobile-card').first()).toBeVisible()
    await expect(page.locator('table.signals').first()).toBeAttached()
  }
  const body = await page.locator('[data-testid="scalp-module"]').innerText()
  expect(body.toLowerCase()).not.toContain('estratégia lucrativa')
  expect(body.toLowerCase()).not.toContain('formador de mercado')
}

for (const viewport of [
  { name: 'desktop', width: 1280, height: 800 },
  { name: 'mobile', width: 390, height: 844 },
]) {
  test.describe(`card-1001 scalp panel ${viewport.name}`, () => {
    test.use({ viewport: { width: viewport.width, height: viewport.height } })

    test('default off, between page-sub and KPIs, board intact', async ({ page }) => {
      await mockAuthenticatedSession(page)
      await mockMonitorWithScalp(page, 'off')
      await page.goto('/monitor')
      const module = page.getByTestId('scalp-module')
      await expect(module).toBeVisible()
      await expect(module).toHaveAttribute('data-state', 'off')
      const sub = page.locator('.page-sub')
      const kpis = page.locator('.kpis')
      const boxModule = await module.boundingBox()
      const boxSub = await sub.boundingBox()
      const boxKpi = await kpis.boundingBox()
      expect(boxModule && boxSub && boxKpi).toBeTruthy()
      if (boxModule && boxSub && boxKpi) {
        expect(boxModule.y).toBeGreaterThan(boxSub.y)
        expect(boxModule.y).toBeLessThan(boxKpi.y)
      }
      await expect(page.getByTestId('scalp-switch')).toHaveAttribute('aria-checked', 'false')
      await expect(page.getByTestId('scalp-status')).toContainText('Desligado')
      await assertBoardIntact(page)
    })

    test('ligar and desligar', async ({ page }) => {
      await mockAuthenticatedSession(page)
      await mockMonitorWithScalp(page, 'off')
      await page.goto('/monitor')
      await page.getByTestId('scalp-switch').click()
      await expect(page.getByTestId('scalp-module')).toHaveAttribute('data-state', 'on')
      await expect(page.getByTestId('scalp-switch')).toHaveAttribute('aria-checked', 'true')
      await expect(page.getByTestId('scalp-status')).toContainText('Ligado')
      await expect(page.getByTestId('scalp-pnl')).toHaveClass(/neg/)
      await page.getByTestId('scalp-switch').click()
      await expect(page.getByTestId('scalp-module')).toHaveAttribute('data-state', 'off')
      await expect(page.getByTestId('scalp-switch')).toHaveAttribute('aria-checked', 'false')
    })

    test('parado por kill does not self-enable', async ({ page }) => {
      await mockAuthenticatedSession(page)
      await mockMonitorWithScalp(page, 'kill')
      await page.goto('/monitor')
      await expect(page.getByTestId('scalp-module')).toHaveAttribute('data-state', 'kill')
      await expect(page.getByTestId('scalp-kill')).toBeVisible()
      await expect(page.getByTestId('scalp-kill')).toContainText('Parado por kill')
      await expect(page.getByTestId('scalp-switch')).toHaveAttribute('aria-checked', 'false')
      await expect(page.getByTestId('scalp-switch')).toBeEnabled()
    })

    test('sem chave Spot disables switch and points to Meu Perfil', async ({ page }) => {
      await mockAuthenticatedSession(page)
      await mockMonitorWithScalp(page, 'nokey')
      await page.goto('/monitor')
      await expect(page.getByTestId('scalp-module')).toHaveAttribute('data-state', 'nokey')
      await expect(page.getByTestId('scalp-switch')).toBeDisabled()
      await expect(page.getByTestId('scalp-status')).toContainText('Meu Perfil')
      await expect(page.getByTestId('scalp-status').locator('a[href="/profile"]')).toBeVisible()
    })
  })
}

test('help copy admits optional scalp and drops absolute nao e bot', async ({ page }) => {
  await mockAuthenticatedSession(page)
  await page.route('**/api/**', async (route) => {
    await route.fulfill({ status: 200, contentType: 'application/json', body: '{}' })
  })
  await page.goto('/help')
  const grid = page.locator('.help-usage-grid')
  await expect(grid).toContainText('scalp')
  await expect(grid).not.toContainText('nao e bot')
  await expect(page.locator('.onboarding-guide')).toBeVisible()
})
