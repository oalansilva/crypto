import { expect, test, type Page } from '@playwright/test'

const AUTH_USER = {
  id: 'card-1006-user',
  email: 'card1006@example.com',
  name: 'Card 1006',
  isAdmin: true,
  mustChangePassword: false,
}

const BTC_OPPORTUNITY = {
  id: 1006,
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

function scalpHorizonBody(overrides: Record<string, unknown> = {}) {
  return {
    state: 'on',
    has_spot_key: true,
    jev_available: true,
    book_available: true,
    horizon_s: 900,
    lookback_label: 'últimos 15 min',
    t_quote: '100',
    clip_quote: '10',
    inventory_btc: '0.001',
    calibration: { hits: 4, signals: 9, last_latency_s: 2 },
    pnl_quote: '1.20',
    status_text:
      'Ligado: pergunta ao Jev com o toque fresco. Lookback últimos 15 min. Hurdle 20,1 bp com taxa 10 bp. Alvo 35 bp. Stop −28 bp depois do fill. Operar continua ao lado.',
    kill_banner: false,
    inventory_clipped: false,
    fee_bp: '10',
    bnb_fee_active: false,
    hurdle_bp: '20.1',
    exit_target_bp: '35',
    exit_stop_bp: '-28',
    position: {
      entry_quote: '64000',
      age_s: 120,
      target_bp: '35',
      stop_bp: '-28',
    },
    last_trade_bp: '12.5',
    last_trade_quote: '0.80',
    stuck: false,
    ...overrides,
  }
}

async function mockAuthenticatedSession(page: Page) {
  await page.addInitScript((user) => {
    window.localStorage.setItem('auth_access_token', 'test-access-token')
    window.localStorage.setItem('auth_refresh_token', 'test-refresh-token')
    window.localStorage.setItem('auth_user', JSON.stringify(user))
    window.localStorage.setItem('cripto-farol-onboarding-dismissed', '1')
  }, AUTH_USER)
}

async function mockMonitorWithScalpHorizon(page: Page, scalpBody: Record<string, unknown>) {
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
      await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(scalpBody) })
      return
    }
    if (url.includes('/api/scalp/status')) {
      await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(scalpBody) })
      return
    }
    if (url.includes('/api/favorites')) {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify([
          {
            id: 1006,
            name: 'BTC Long',
            symbol: 'BTC/USDT',
            timeframe: '1d',
            strategy_name: 'ema',
            parameters: { direction: 'long' },
            metrics: {},
            created_at: '2026-01-01T00:00:00Z',
            tier: 1,
          },
        ]),
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
        body: JSON.stringify({ configured: true, api_key_masked: 'abcd****efgh' }),
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

const viewports = [
  { name: 'desktop', width: 1280, height: 800 },
  { name: 'mobile', width: 390, height: 844 },
]

for (const vp of viewports) {
  test.describe(`card-1006 monitor ${vp.name}`, () => {
    test.use({ viewport: { width: vp.width, height: vp.height } })

    test('scalp module matches proto landmarks', async ({ page }) => {
      await page.goto('/prototypes/card-1006-scalp-jev-horizonte/')
      const module = page.getByTestId('scalp-module')
      await expect(module).toHaveAttribute('data-horizon-s', '900')
      await expect(page.getByTestId('scalp-horizon')).toHaveText('últimos 15 min')
      await expect(page.getByTestId('scalp-exit-target')).toHaveText('+35 bp')
      await expect(page.getByTestId('scalp-exit-stop')).toHaveText('−28 bp')
      await expect(page.locator('[data-testid="scalp-horizon-1"]')).toHaveCount(0)
      const body = await module.innerText()
      expect(body).not.toMatch(/1 vez \/ 15 min/i)
      expect(body).not.toMatch(/800\s*ms/i)
      expect(body).not.toMatch(/1[,.]5\s*s/i)
    })

    test('authenticated monitor shows lookback hurdle position and last trade', async ({ page }) => {
      await mockAuthenticatedSession(page)
      await mockMonitorWithScalpHorizon(page, scalpHorizonBody())
      await page.goto('/monitor')
      const module = page.getByTestId('scalp-module')
      await expect(module).toBeVisible()
      await expect(module).toHaveAttribute('data-horizon-s', '900')
      await expect(page.getByTestId('scalp-horizon')).toHaveText('últimos 15 min')
      await expect(page.getByTestId('scalp-hurdle')).toHaveText('20,1 bp')
      await expect(page.getByTestId('scalp-position')).toBeVisible()
      await expect(page.getByTestId('scalp-last-bp')).toHaveText('+12,5 bp')
      await expect(page.getByTestId('scalp-last-usd')).toContainText('US$')
      await expect(page.getByTestId('scalp-stuck')).toBeHidden()
      const body = await module.innerText()
      expect(body).not.toMatch(/1 vez \/ 15 min/i)
      expect(body).not.toMatch(/1[,.]5\s*s/i)
    })

    test('authenticated monitor shows stuck banner when API reports stuck', async ({ page }) => {
      await mockAuthenticatedSession(page)
      await mockMonitorWithScalpHorizon(
        page,
        scalpHorizonBody({
          stuck: true,
          status_text: 'Ligado com posição presa — sem saída automática a mercado.',
        }),
      )
      await page.goto('/monitor')
      await expect(page.getByTestId('scalp-stuck')).toBeVisible()
      await expect(page.getByTestId('scalp-stuck')).toContainText('posição presa')
    })
  })
}
