import { expect, test, type Page } from '@playwright/test'

const AUTH_USER = {
  id: 'card-1045-user',
  email: 'card1045@example.com',
  name: 'Card 1045',
  isAdmin: true,
  mustChangePassword: false,
}

const BTC_OPPORTUNITY = {
  id: 1045,
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
    closed_day: '2026-09-25',
    shown_on: '2026-09-26',
    lead: 'Um aviso por dia, só depois que o dia fecha. Este é o de 26 de setembro de 2026. Hoje não há outro.',
    when: '26 set 2026, sobre o dia 25 que já fechou',
    data_ok: 'servem para esta leitura',
    until: 'só o que já tinha fechado à meia-noite',
    confidence_now: 'mercado calmo só entra acima de 55%. Mercado agitado não entra. Versão 12.',
    decision: 'não mudei a confiança',
    verb: 'bloquear',
    sample: '67 operações, e não dá para compará-las. Para mudar alguma coisa preciso de cerca de 200.',
    target_stop:
      'para não perder com a taxa, teria de acertar cerca de 76 em 100. Sem a taxa, cerca de 44 em 100. O preço chegou no alvo em cerca de 30 em 100 das vezes em que bateu num dos lados.',
    signal: 'não ganhou nada além de ficar comprado.',
    side: '97 em 100 foram compra. Acertar o lado ficou em 49 em 100, igual a comprar e segurar (50 em 100).',
    reason:
      'Não mudei nada. Ainda só há 67 operações medidas à parte, abaixo de 200, e essa amostra não é comparável. Com este alvo e este stop o scalp não se paga. A confiança fica como está. Alvo, stop e o prazo do scalp não mudam.',
    can_revert: true,
    history: [
      {
        date: '2026-09-26',
        label: '26 set 2026',
        verb: 'bloquear',
        text: 'Não mudei. Só havia 67 operações, abaixo de 200.',
      },
    ],
  }
}

function scalpBody(overrides: Record<string, unknown> = {}) {
  return {
    state: 'off',
    has_spot_key: true,
    jev_available: true,
    book_available: true,
    horizon_s: 900,
    lookback_label: 'últimos 15 min',
    t_quote: '100',
    clip_quote: '10',
    inventory_btc: '0',
    calibration: null,
    pnl_quote: '0',
    status_text:
      'Desligado: não envia ordem deste scalp. Lookback últimos 15 min. Inventário e P&L ficam visíveis.',
    kill_banner: false,
    inventory_clipped: false,
    fee_bp: '10',
    bnb_fee_active: false,
    hurdle_bp: '20.1',
    exit_target_bp: '35',
    exit_stop_bp: '-28',
    position: null,
    stuck: false,
    calibration_paused: false,
    calibration_enabled: true,
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
  let live = { ...scalp }
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
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(AUTH_USER),
      })
      return
    }
    if (url.includes('/api/scalp/calibration') && method === 'POST') {
      const posted = route.request().postDataJSON() as { paused?: boolean; enabled?: boolean }
      const paused = posted.paused ?? posted.enabled === false
      live = { ...live, calibration_paused: paused, calibration_enabled: !paused, state: 'off' }
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(live),
      })
      return
    }
    if (url.includes('/api/scalp/switch') && method === 'POST') {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(live),
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
            id: 1045,
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

test.describe('card-1045 monitor diagnosis', () => {
  test('prototype keeps board landmarks and beginner diagnosis copy', async ({ page }) => {
    await page.goto('/prototypes/card-1045-jev-diagnostico-recalibracao/')
    await expect(page.locator('table.signals').first()).toBeVisible()
    const protoTable = page.locator('table.signals').first()
    for (const label of ['Status', 'Preço', 'Distância', 'Risco até stop', 'Tags', 'Operar', 'Par / Estratégia']) {
      await expect(protoTable.locator('th', { hasText: label }).first()).toBeVisible()
    }
    await expect(protoTable.locator('[data-landmark="7d"]').first()).toBeVisible()
    const diagnosis = page.getByTestId('scalp-diagnosis')
    await expect(diagnosis).toBeVisible()
    await expect(diagnosis.getByText('Como está o scalp')).toBeVisible()
    const text = await diagnosis.innerText()
    expect(text).not.toMatch(/break-even/i)
    expect(text).not.toMatch(/homogeneidade/i)
    expect(text).not.toMatch(/fasquia/i)
    expect(text).not.toMatch(/contribui[cç][aã]o preditiva/i)
    await expect(page.getByTestId('scalp-module')).toHaveAttribute('data-state', 'off')
    await expect(page.getByTestId('scalp-exit-target')).toHaveText('+35 bp')
    await expect(page.getByTestId('scalp-exit-stop')).toHaveText('−28 bp')
  })

  test('authenticated monitor shows diagnosis with scalp off and calibration does not arm the switch', async ({
    page,
  }) => {
    await mockAuthenticatedSession(page)
    await mockMonitor(page, scalpBody())
    await page.goto('/monitor')
    const module = page.getByTestId('scalp-module')
    await expect(module).toBeVisible()
    await expect(module).toHaveAttribute('data-state', 'off')
    await expect(page.locator('table.signals').first()).toBeVisible()
    const board = page.locator('table.signals').first()
    for (const label of ['Status', 'Preço', 'Distância', 'Risco até stop', 'Tags', 'Par / Estratégia']) {
      await expect(board.locator('th', { hasText: label }).first()).toBeVisible()
    }
    await expect(board.locator('[data-landmark="7d"]').first()).toBeVisible()
    await expect(board.getByText('Operar').first()).toBeVisible()
    const diagnosis = page.getByTestId('scalp-diagnosis')
    await expect(diagnosis).toBeVisible()
    await expect(diagnosis.getByText('Como está o scalp')).toBeVisible()
    const text = await diagnosis.innerText()
    expect(text).not.toMatch(/break-even/i)
    expect(text).not.toMatch(/homogeneidade/i)
    expect(text).not.toMatch(/fasquia/i)
    expect(text).not.toMatch(/contribui[cç][aã]o preditiva/i)
    await expect(page.getByTestId('scalp-switch')).toHaveText('Desligado')
    await page.getByTestId('scalp-calibration-pause').click()
    await expect(page.getByTestId('scalp-module')).toHaveAttribute('data-state', 'off')
    await expect(page.getByTestId('scalp-switch')).toHaveText('Desligado')
  })
})
