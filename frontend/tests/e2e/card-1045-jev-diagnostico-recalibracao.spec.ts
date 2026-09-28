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
    closed_day: '2026-09-27',
    shown_on: '2026-09-28',
    lead: 'Um aviso por dia, só depois que o dia fecha. Este é o de 28 de setembro de 2026. Hoje não há outro.',
    when: '28 set 2026, sobre o dia 27 que já fechou',
    data_ok:
      '267 de 300 janelas históricas têm preço entre 23 setembro 2026 13:26 a 27 setembro 2026 21:47 UTC. A fronteira entre mercado calmo e agitado está ausente; os dois regimes continuam bloqueados. A comparação também está bloqueada: o modelo e a origem da confiança não foram identificados em 1 de 1 janelas elegíveis. São janelas históricas avaliadas, não trades executados.',
    period: '23 setembro 2026 13:26 a 27 setembro 2026 21:47 UTC',
    until: 'só as janelas que já tinham terminado à meia-noite UTC',
    confidence_now: 'Mercado calmo não entra. Mercado agitado não entra. Versão 12.',
    regime_boundary_bp: null,
    regime_boundary_status: 'absent',
    viability_status: 'indeterminate',
    barrier_measurement: {
      candidate_count: 24,
      measured_candidates: 0,
      indeterminate_candidates: 24,
      no_hit_candidates: 0,
    },
    decision: 'não mudei a confiança',
    verb: 'bloquear',
    sample:
      '1 janela histórica independente com preço passou pelos filtros depois da escolha; ainda não chega às 200 necessárias. Motivo: a fronteira entre mercado calmo e agitado está ausente; as barreiras ainda não foram resolvidas. São janelas avaliadas, não trades executados.',
    target_stop:
      'Com a taxa, o alvo precisaria ser atingido em cerca de 76 de cada 100 janelas; sem a taxa, em cerca de 44. No alvo e stop atuais: 0 alvos, 0 stops e 0 saídas pelo prazo. Em 267 janelas históricas as barreiras não tiveram resolução suficiente. Ainda não dá para concluir se a estratégia se paga.',
    signal: 'não ganhou da escolha aleatória na mesma proporção de compras.',
    side: 'Em 97 de 100 janelas o sinal indicou compra. Acertar o lado ficou em 49 em 100, igual a comprar e segurar (50 em 100).',
    reason:
      'Não mudei nada. A fronteira entre mercado calmo e agitado está ausente, então os dois regimes continuam bloqueados. A amostra e as barreiras ainda não podem ser comparadas; isso não mostra prejuízo. A confiança fica como está. Alvo, stop e o prazo do scalp não mudam.',
    calibration_note:
      'O ajuste automático está ligado ao processamento dos diagnósticos, mas as entradas continuam bloqueadas nos regimes calmo e agitado. Isso não liga o scalp nem envia ordens.',
    can_revert: true,
    history: [
      {
        date: '2026-09-26',
        label: '26 set 2026',
        verb: 'bloquear',
        text: 'Não mudei. Só havia 1 janela histórica elegível, abaixo de 200.',
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

async function dismissMonitorRefreshToast(page: Page) {
  const toast = page.getByRole('status').filter({ hasText: 'estratégias analisadas' })
  await expect(toast).toBeVisible()
  await toast.getByRole('button', { name: 'Fechar notificação' }).click()
  await expect(toast).toHaveCount(0)
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
    await expect(page.getByTestId('scalp-fee')).toHaveText('10 bp')
    await expect(diagnosis.getByText(/267 de 300 janelas históricas/)).toBeVisible()
    await expect(diagnosis.getByText(/fronteira entre mercado calmo e agitado está ausente/).first()).toBeVisible()
    await expect(diagnosis.getByText(/barreiras não tiveram resolução suficiente/).first()).toBeVisible()
    await expect(diagnosis.getByText(/ainda não dá para concluir se a estratégia se paga/i)).toBeVisible()
    expect(text).not.toMatch(/scalp não se paga/i)
    await expect(diagnosis.getByText(/modelo e a origem da confiança não foram identificados/)).toBeVisible()
    await expect(diagnosis.getByText(/não trades executados/).first()).toBeVisible()
    await expect(diagnosis.getByText(/1 janela histórica independente com preço/)).toBeVisible()
    await expect(diagnosis.getByText(/ligado ao processamento dos diagnósticos/)).toBeVisible()
    await page.getByTestId('scalp-calibration-pause').click()
    await expect(page.getByTestId('scalp-module')).toHaveAttribute('data-state', 'off')
    await expect(page.getByTestId('scalp-switch')).toHaveText('Desligado')
  })

  test('shows the API rate and labels the BNB setting without reapplying a discount', async ({ page }) => {
    await mockAuthenticatedSession(page)
    await mockMonitor(page, scalpBody({ fee_bp: '10', bnb_fee_active: true, hurdle_bp: '20.1' }))
    await page.goto('/monitor')
    await expect(page.getByTestId('scalp-fee')).toHaveText(
      '10 bp (BNB habilitado; desconto não aplicado)',
    )
    await expect(page.getByTestId('scalp-hurdle')).toHaveText('20,1 bp')
  })

  test('diagnosis panel keeps the approved desktop hierarchy', async ({ page }) => {
    await mockAuthenticatedSession(page)
    await mockMonitor(page, scalpBody())
    await page.goto('/monitor')
    await dismissMonitorRefreshToast(page)
    await expect(page.getByTestId('scalp-diagnosis')).toHaveScreenshot(
      'card-1045-diagnosis-desktop.png',
    )
  })

  test('diagnosis panel keeps the approved hierarchy on mobile', async ({ page }) => {
    await page.setViewportSize({ width: 390, height: 2400 })
    await mockAuthenticatedSession(page)
    await mockMonitor(page, scalpBody())
    await page.goto('/monitor')
    await dismissMonitorRefreshToast(page)
    await expect(page.getByTestId('scalp-diagnosis')).toHaveScreenshot(
      'card-1045-diagnosis-mobile.png',
    )
  })
})
