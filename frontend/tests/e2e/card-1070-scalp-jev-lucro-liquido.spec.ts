import { expect, test, type Page } from '@playwright/test'

const AUTH_USER = {
  id: 'card-1070-user',
  email: 'card1070@example.com',
  name: 'Card 1070',
  isAdmin: true,
  mustChangePassword: false,
}

const BTC_OPPORTUNITY = {
  id: 1070,
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
  timestamp: '2026-09-26T00:00:00Z',
  entry_price: 62000,
  stop_price: 61000,
  distance_to_stop_pct: 6.1,
  parameters: {},
  signal_history: [],
  details: {},
}

function diagnosisBody() {
  return {
    closed_day: '2026-09-28',
    shown_on: '2026-09-29',
    lead: 'Um aviso por dia, só depois que o dia fecha. Este é o de 29 de setembro de 2026. Hoje não há outro.',
    when: '29 set 2026, sobre o backtest que já fechou',
    data_ok: 'Os dados fecharam. A confiança não foi desligada.',
    period: '23 setembro 2026 13:26 a 27 setembro 2026 21:47 UTC',
    confidence_now: 'Mercado calmo entra. Mercado agitado entra. Versão 14.',
    decision: 'Apliquei',
    verb: 'aplicar',
    sample: 'mais de 200 janelas por recorte de mercado, no backtest.',
    backtest_sample:
      'Backtest: calmo: 220 janelas, IC 95% inferior 2 bp; agitado: 220 janelas, IC 95% inferior 1 bp. O conjunto pode ser promovido: lucro líquido médio com IC acima de zero.',
    geometry_bundle:
      'Conjunto aplicado: alvo 20 bp, stop −14 bp, prazo 60 min. Recorte de regime em 0.05 bp. Versão 14.',
    target_stop: 'versão aplicada: alvo +20, stop −14, prazo 60 min.',
    signal: 'o conjunto pagou no backtest.',
    side: '—',
    reason:
      'Apliquei. O backtest mostrou lucro líquido por trade, com intervalo de confiança acima de zero.',
    calibration_note: 'Ligar o ajuste automático não liga o scalp nem envia ordem.',
    can_revert: true,
    history: [],
  }
}

function scalpBody(overrides: Record<string, unknown> = {}) {
  return {
    state: 'on',
    has_spot_key: true,
    jev_available: true,
    book_available: true,
    horizon_s: 3600,
    lookback_label: 'últimos 60 min',
    t_quote: '100',
    clip_quote: '10',
    inventory_btc: '0',
    calibration: { hits: 0, signals: 25989, last_latency_s: 30 },
    pnl_quote: '-0.18',
    status_text:
      'Ligado: pergunta ao Jev com o toque fresco. Lookback últimos 60 min. Hurdle 15,1 bp com taxa 7,5 bp · desconto aplicado.',
    kill_banner: false,
    inventory_clipped: false,
    enabled: true,
    fee_bp: '7.5',
    bnb_fee_active: true,
    bnb_discount_applied: true,
    hurdle_bp: '15.1',
    exit_target_bp: '20',
    exit_stop_bp: '-14',
    last_trade_bp: '-12.4',
    last_trade_quote: '-0.18',
    position: null,
    stuck: false,
    calibration_paused: true,
    calibration_enabled: false,
    jev_diagnosis: diagnosisBody(),
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

async function mockMonitor(page: Page, scalp: Record<string, unknown>) {
  const live = { ...scalp }
  await page.route('**/api/**', async (route) => {
    const url = route.request().url()
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
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(AUTH_USER),
      })
      return
    }
    if (url.includes('/api/scalp/status')) {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(live),
      })
      return
    }
    if (url.includes('/api/favorites')) {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify([
          {
            id: 1070,
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
          as_of: '2026-09-26T00:00:00Z',
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

test.describe('card-1070 monitor scalp net return', () => {
  test('prototype keeps board landmarks fee discount and visible net loss', async ({ page }) => {
    await page.goto('/prototypes/card-1070-scalp-jev-lucro-liquido/')
    const board = page.locator('table.signals').first()
    await expect(board).toBeVisible()
    for (const label of ['Status', 'Preço', 'Distância', 'Risco até stop', 'Tags', 'Operar', 'Par / Estratégia']) {
      await expect(board.locator('th', { hasText: label }).first()).toBeVisible()
    }
    await expect(board.locator('[data-landmark="7d"]').first()).toBeVisible()
    await expect(page.getByTestId('scalp-fee')).toContainText('desconto aplicado')
    await expect(page.getByTestId('scalp-last-bp')).toContainText('−')
    await expect(page.getByTestId('scalp-last-usd')).toContainText('−US$')
    await expect(page.getByTestId('scalp-t')).toHaveText('US$ 100')
    await expect(page.getByText('≤ US$ 10').first()).toBeVisible()
    await expect(page.getByTestId('scalp-switch')).toBeVisible()
  })

  test('authenticated monitor shows discount fee negative net pnl and intact controls', async ({ page }) => {
    await mockAuthenticatedSession(page)
    await mockMonitor(page, scalpBody())
    await page.goto('/monitor')
    await expect(page.locator('table.signals').first()).toBeVisible()
    await expect(page.getByTestId('scalp-fee')).toHaveText('7,5 bp · desconto aplicado')
    await expect(page.getByTestId('scalp-last-bp')).toHaveText('-12,4 bp')
    await expect(page.getByTestId('scalp-last-usd')).toHaveText('−US$ 0,18')
    await expect(page.getByTestId('scalp-t')).toHaveText('US$ 100')
    await expect(page.getByText('≤ US$ 10').first()).toBeVisible()
    await expect(page.getByTestId('scalp-switch')).toHaveText('Ligado')
    await expect(page.getByTestId('scalp-diagnosis-backtest')).toContainText('Backtest:')
    await expect(page.getByTestId('scalp-diagnosis-bundle')).toContainText('Conjunto aplicado')
  })
})
