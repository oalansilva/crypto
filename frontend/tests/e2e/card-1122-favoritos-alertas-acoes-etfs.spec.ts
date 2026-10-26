import { expect, test, type Page, type Route } from '@playwright/test'

/**
 * Card #1122 (tarefa 6.3): alertas por favorito em cripto, ação e ETF, com a API simulada.
 * Segue o protótipo aprovado (frontend/public/prototypes/card-1122-favoritos-alertas-acoes-etfs/):
 * Monitor (linha compacta, estado do mercado, "Alerta", fonte antiga, faixa da transição),
 * Favoritos ("Alertar" do dono a 1440/1280/1024 e no celular, fora da carteira, vitrine),
 * Resultado (salvar NVDA, foco preso, Esc, duplicata e sucesso) e Perfil.
 */

const USER = { id: 'card-1122', email: 'bia@example.com', name: 'Bia', isAdmin: false, mustChangePassword: false }
const DESKTOP = { width: 1440, height: 900 }
const PHONE = { width: 390, height: 844 }

const BINANCE = {
  data_source: 'binance_equity',
  session: 'regular_ny',
  adjustment: 'split',
  label_short: 'Binance Ações · NY · split',
  label_compact: 'Binance · NY · split',
  label_long: 'Binance Ações · pregão regular de NY · ajustado por split',
}
const STOOQ = {
  data_source: 'stooq',
  session: 'eod',
  adjustment: 'legacy',
  label_short: 'Stooq · fonte antiga · diário',
  label_compact: 'Stooq · antiga · diário',
  label_long: 'Stooq · fonte antiga · diário',
}
const CRYPTO = {
  data_source: 'ccxt',
  session: '24x7',
  adjustment: 'none',
  label_short: 'Binance Spot · 24/7',
  label_compact: 'Binance Spot · 24/7',
  label_long: 'Binance Spot · 24/7',
}

const WEEKEND = { state: 'closed', reason: 'weekend', next_open: '2026-10-26T13:30:00+00:00', timezone: 'America/New_York' }
const HOLIDAY = { state: 'closed', reason: 'holiday', next_open: '2026-11-27T14:30:00+00:00', timezone: 'America/New_York' }
const OPEN = { state: 'open', reason: 'session', closes_at: '2026-10-26T20:00:00+00:00', timezone: 'America/New_York' }
const NVDA_STALE = {
  state: 'stale',
  reason: 'delay',
  last_candle: '2026-10-23T04:00:00+00:00',
  expected_candle: '2026-10-26T04:00:00+00:00',
  stale_since: '2026-10-27T11:05:00',
}
const BTC_STALE = {
  state: 'stale',
  reason: 'delay',
  last_candle: '2026-10-23T00:00:00+00:00',
  expected_candle: '2026-10-24T00:00:00+00:00',
  stale_since: '2026-10-25T11:05:00',
}

const base = {
  template_name: 'multi_ma_crossover',
  strategy_display_name: 'Médias Móveis: Tendência em Virada',
  strategy_description: 'Cruzamento de médias a favor da tendência, com stop de 5%.',
  notes: '',
  parameters: { direction: 'long' },
  details: {},
  signal_history: [],
  timestamp: '2026-10-23T04:00:00+00:00',
  indicator_values_candle_time: '2026-10-23T04:00:00+00:00',
}

type Opp = Record<string, unknown>

function opportunities(overrides: { nvda?: Opp; spy?: Opp; legacy?: Opp; btc?: Opp; qqq?: Opp | null } = {}): Opp[] {
  const rows: Opp[] = [
    {
      ...base,
      id: 1,
      symbol: 'BTC/USDT',
      asset_type: 'crypto',
      asset_class: 'crypto',
      currency: 'USDT',
      configuration: CRYPTO,
      timeframe: '1d',
      name: 'BTC',
      tier: 1,
      is_holding: true,
      status: 'HOLD',
      distance_to_next_status: 3.1,
      next_status_label: 'exit',
      last_price: 67000,
      notify_telegram: true,
      timestamp: new Date().toISOString(),
      indicator_values_candle_time: new Date(Date.now() - 86_400_000).toISOString(),
      market_state: { state: 'open', reason: '24x7' },
      ...overrides.btc,
    },
    {
      ...base,
      id: 21,
      symbol: 'NVDA',
      asset_type: 'stock',
      asset_class: 'stock',
      currency: 'USD',
      configuration: BINANCE,
      timeframe: '1d',
      name: 'NVDA Binance',
      tier: 2,
      is_holding: true,
      status: 'HOLD',
      distance_to_next_status: 2.1,
      next_status_label: 'exit',
      last_price: 186.1,
      entry_price: 182.4,
      stop_price: 173.28,
      distance_to_stop_pct: 6.89,
      notify_telegram: true,
      market_state: OPEN,
      ...overrides.nvda,
    },
    {
      ...base,
      id: 22,
      symbol: 'SPY',
      asset_type: 'stock',
      asset_class: 'etf',
      currency: 'USD',
      configuration: BINANCE,
      timeframe: '1d',
      name: 'SPY',
      tier: 3,
      is_holding: true,
      status: 'HOLD',
      distance_to_next_status: 1.4,
      next_status_label: 'exit',
      last_price: 512.3,
      notify_telegram: true,
      market_state: OPEN,
      ...overrides.spy,
    },
    {
      ...base,
      id: 23,
      symbol: 'NVDA',
      asset_type: 'stock',
      asset_class: 'stock',
      currency: 'USD',
      configuration: STOOQ,
      parameters: { direction: 'long', data_source: 'stooq' },
      timeframe: '1d',
      name: 'NVDA Stooq',
      tier: 3,
      is_holding: false,
      status: 'EXIT',
      distance_to_next_status: 0.9,
      next_status_label: 'entry',
      last_price: 182.31,
      notify_telegram: false,
      market_state: OPEN,
      ...overrides.legacy,
    },
  ]
  if (overrides.qqq !== null && overrides.qqq !== undefined) {
    rows.push({
      ...base,
      id: 24,
      symbol: 'QQQ',
      asset_type: 'stock',
      asset_class: 'etf',
      currency: 'USD',
      configuration: BINANCE,
      timeframe: '1d',
      name: 'QQQ',
      tier: 3,
      is_holding: false,
      status: 'EXIT',
      raw_analysis_status: 'INSUFFICIENT',
      distance_to_next_status: null,
      next_status_label: 'entry',
      last_price: 490,
      notify_telegram: false,
      market_state: { state: 'insufficient', reason: 'insufficient', available: 40, required: 200 },
      ...overrides.qqq,
    })
  }
  return rows
}

const PREFERENCES = {
  __global__: { in_portfolio: false, card_mode: 'price', price_timeframe: '1d', theme: 'dark-green' },
  'BTC/USDT': { in_portfolio: true, card_mode: 'price', price_timeframe: '1d', theme: 'dark-green' },
  NVDA: { in_portfolio: true, card_mode: 'price', price_timeframe: '1d', theme: 'dark-green' },
  SPY: { in_portfolio: true, card_mode: 'price', price_timeframe: '1d', theme: 'dark-green' },
}

const json = (body: unknown, status = 200) => ({ status, contentType: 'application/json', body: JSON.stringify(body) })

async function login(page: Page) {
  await page.addInitScript((user) => {
    localStorage.setItem('auth_access_token', 'tok')
    localStorage.setItem('auth_refresh_token', 'ref')
    localStorage.setItem('auth_user', JSON.stringify(user))
    localStorage.setItem('cripto-farol-onboarding-dismissed', '1')
  }, USER)
}

const pageErrors = new WeakMap<Page, string[]>()
test.beforeEach(({ page }) => {
  const errors: string[] = []
  pageErrors.set(page, errors)
  page.on('pageerror', (error) => errors.push(error.message))
})
test.afterEach(({ page }) => {
  expect(pageErrors.get(page) ?? [], 'sem erro de página não tratado').toEqual([])
})

// Leitura no sábado, 24 out. 2026, 11:05 BRT (o protótipo usa as mesmas datas).
const SATURDAY = new Date('2026-10-24T14:05:00Z')

async function mockMonitor(
  page: Page,
  rows: Opp[],
  origin: { show_banner: boolean; received_catalog_alerts: boolean; catalog_until: string | null } = {
    show_banner: false,
    received_catalog_alerts: false,
    catalog_until: null,
  },
) {
  await login(page)
  await page.clock.setFixedTime(SATURDAY)
  const requests: string[] = []
  await page.route('**/api/**', async (route: Route) => {
    const url = route.request().url()
    requests.push(url)
    if (url.includes('/api/auth/me')) return route.fulfill(json(USER))
    if (url.includes('/api/opportunities/alert-origin')) return route.fulfill(json(origin))
    if (url.includes('/api/opportunities')) return route.fulfill(json(rows))
    if (/\/api\/favorites\/?(\?|$)/.test(url)) return route.fulfill(json([{ id: 21, symbol: 'NVDA' }]))
    if (/\/api\/monitor\/preferences\/?$/.test(url)) return route.fulfill(json(PREFERENCES))
    if (url.includes('/api/user/binance-credentials')) return route.fulfill(json({ configured: false }))
    if (url.includes('/api/users/me/telegram-settings')) return route.fulfill(json({ telegramAlertsEnabled: true }))
    if (url.includes('/api/market/history')) {
      const start = Date.parse('2026-09-01T04:00:00Z')
      const candles = Array.from({ length: 30 }, (_, i) => ({
        timestamp_utc: new Date(start + i * 86_400_000).toISOString(),
        open: 180 + i,
        high: 182 + i,
        low: 178 + i,
        close: 181 + i,
        volume: 1000,
      }))
      return route.fulfill(json({ candles, count: candles.length }))
    }
    return route.fulfill(json({}))
  })
  return { requests }
}

const fits = (page: Page) => page.evaluate(() => document.documentElement.scrollWidth <= document.documentElement.clientWidth)

test.describe('Monitor com ação e ETF', () => {
  test('1440 px: linha compacta com identidade, estado sob a pílula, Alerta, carteira e fonte antiga indisponível', async ({ page }) => {
    await page.setViewportSize(DESKTOP)
    const { requests } = await mockMonitor(page, opportunities({ nvda: { market_state: WEEKEND }, spy: { market_state: WEEKEND }, legacy: { market_state: WEEKEND } }))
    await page.goto('/monitor')
    const nvda = page.getByTestId('monitor-row-nvda')
    await expect(nvda).toBeVisible()
    await expect(page.getByTestId('monitor-row-identity-nvda')).toHaveText('Ação · USD · Binance · NY · split')
    await expect(page.getByTestId('monitor-row-identity-nvda')).toHaveAttribute(
      'title',
      'Ação · USD · Binance Ações · pregão regular de NY · ajustado por split',
    )
    await expect(page.getByTestId('monitor-row-identity-spy')).toHaveText('ETF · USD · Binance · NY · split')
    await expect(page.getByTestId('monitor-row-identity-nvda-legacy')).toHaveText('Ação · USD · Stooq · antiga · diário')
    const state = page.getByTestId('monitor-row-market-nvda')
    await expect(state).toHaveAttribute('data-tone', 'closed')
    await expect(state).toHaveText('Fechado · fim de semana · abre seg. 10:30 (09:30 NY)')
    await expect(state).toHaveAttribute('title', 'Mercado fechado · fim de semana · abre seg., 26 out., 10:30 (09:30 em NY)')
    await expect(state.locator('svg')).toHaveCount(1) // ícone + texto, nunca só cor
    // BTC/USDT sem estado de mercado
    await expect(page.getByTestId('monitor-row-market-btc-usdt')).toHaveCount(0)
    // tag "Alerta" só no marcado; a fonte antiga sem a marca fica sem
    await expect(page.getByTestId('monitor-row-alert-nvda')).toHaveText('Alerta')
    await expect(page.getByTestId('monitor-row-alert-btc-usdt')).toBeVisible()
    await expect(page.getByTestId('monitor-row-alert-nvda-legacy')).toHaveCount(0)
    // "Em carteira" conta ativos distintos (as duas NVDA contam uma vez)
    await expect(page.locator('.kpi').filter({ hasText: 'Em carteira' }).locator('.kpi-val')).toHaveText('3')
    // ação/ETF sem "Operar"
    await expect(nvda.getByRole('button', { name: /Operar/ })).toHaveCount(0)

    // fonte antiga: os dois botões visíveis e indisponíveis, com o motivo em texto
    const legacy = page.getByTestId('monitor-row-nvda-legacy')
    const chart = legacy.getByRole('button', { name: 'Abrir Gráfico NVDA (indisponível)' })
    const trades = legacy.getByRole('button', { name: 'Ver Trades NVDA (indisponível)' })
    await expect(chart).toHaveAttribute('aria-disabled', 'true')
    await expect(trades).toHaveAttribute('aria-disabled', 'true')
    await expect(chart).toHaveAttribute('title', 'Fonte antiga: gráfico e trades depois da migração para a Binance.')
    await expect(legacy.locator('.legacy-unavailable-why')).toHaveText('Fonte antiga: gráfico e trades depois da migração para a Binance.')
    await chart.click({ force: true })
    expect(requests.some((url) => url.includes('/api/market/'))).toBe(false)

    // gráfico de ação/ETF Binance pela série do favorito, no tempo dele
    await nvda.getByRole('button', { name: 'Abrir Gráfico NVDA' }).click()
    await expect.poll(() => requests.find((url) => url.includes('/api/market/history'))).toContain('timeframe=1d')
    expect(requests.some((url) => url.includes('/api/market/candles') && url.includes('NVDA'))).toBe(false)
    await page.keyboard.press('Escape')

    // detalhe da fonte antiga: o do próprio favorito ("Risco residual")
    await legacy.getByRole('button', { name: 'Expandir' }).click()
    const detail = page.locator('tr.detail-row').filter({ has: page.getByTestId('monitor-card-nvda-legacy') })
    await expect(detail).toContainText('Risco residual')
    await expect(detail).toContainText('configuração Ação · USD · Stooq · fonte antiga · diário')
    await expect(detail.getByRole('button', { name: 'Ver Trades NVDA (indisponível)' })).toHaveAttribute('aria-disabled', 'true')
    await expect(detail.locator('.legacy-unavailable-why')).toBeVisible()
    // detalhe de NVDA Binance: configuração longa e o texto da carteira
    await nvda.getByRole('button', { name: 'Expandir' }).click()
    const nvdaDetail = page.locator('tr.detail-row').filter({ has: page.getByTestId('monitor-card-nvda') })
    await expect(nvdaDetail).toContainText('Ação/ETF na carteira recebe entrada e saída no Telegram.')
    await expect(nvdaDetail.getByRole('button', { name: /Operar/ })).toHaveCount(0)

    // altura da linha compacta perto da linha de cripto
    const btcHeight = (await page.getByTestId('monitor-row-btc-usdt').boundingBox())!.height
    const nvdaHeight = (await nvda.boundingBox())!.height
    expect(nvdaHeight).toBeLessThanOrEqual(btcHeight * 1.35)
    expect(await fits(page)).toBe(true)
  })

  test('pregão aberto, feriado, atraso de ação e de cripto e dado insuficiente', async ({ page }) => {
    await page.setViewportSize(DESKTOP)
    await mockMonitor(page, opportunities({ spy: { market_state: HOLIDAY }, nvda: { market_state: NVDA_STALE }, btc: { market_state: BTC_STALE }, qqq: {} }))
    await page.goto('/monitor')
    await expect(page.getByTestId('monitor-row-market-nvda-legacy')).toHaveText('Aberto · fecha 17:00 (16:00 NY)')
    await expect(page.getByTestId('monitor-row-market-nvda-legacy')).toHaveAttribute('data-tone', 'open')
    await expect(page.getByTestId('monitor-row-market-spy')).toHaveText('Fechado · feriado em NY · abre sex. 11:30 (09:30 NY)')
    const nvda = page.getByTestId('monitor-row-market-nvda')
    await expect(nvda).toHaveAttribute('data-tone', 'stale')
    await expect(nvda).toHaveText('Dados atrasados · falta seg. 26/10')
    await expect(page.getByTestId('monitor-row-market-nvda-hold')).toHaveText('Sinal em espera')
    // cripto atrasada pelo servidor: "Dados atrasados" no lugar de "Sem candle válido/atual"
    await expect(page.getByTestId('monitor-row-market-btc-usdt')).toHaveText('Dados atrasados · falta sáb. 24/10')
    await page.getByTestId('monitor-row-btc-usdt').getByRole('button', { name: 'Expandir' }).click()
    const btcDetail = page.locator('tr.detail-row').filter({ has: page.getByTestId('monitor-card-btc-usdt') })
    await expect(btcDetail).toContainText('Dados atrasados · último candle sex., 23 out.; esperado sáb., 24 out.')
    await expect(btcDetail).not.toContainText('Sem candle válido/atual')
    // QQQ: "Sem leitura" na Saída, com a contagem e "Sem sinal"
    const qqq = page.getByTestId('monitor-row-qqq')
    await expect(page.getByTestId('monitor-section-exit').getByTestId('monitor-row-qqq')).toBeVisible()
    await expect(page.getByTestId('monitor-row-signal-qqq')).toHaveText('Sem leitura')
    await expect(page.getByTestId('monitor-row-market-qqq')).toHaveText('Dados insuficientes · 40 de 200 candles')
    await expect(page.getByTestId('monitor-row-market-qqq-hold')).toHaveText('Sem sinal')
    await expect(qqq).toBeVisible()
  })

  test('faixa da transição com a frase datada só para quem recebia pelo catálogo', async ({ page }) => {
    await page.setViewportSize(DESKTOP)
    await mockMonitor(page, opportunities(), { show_banner: true, received_catalog_alerts: true, catalog_until: '2026-10-26' })
    await page.goto('/monitor')
    const banner = page.getByTestId('monitor-alert-origin-banner')
    await expect(banner).toHaveAttribute('role', 'status')
    await expect(banner).toContainText('Os alertas do Telegram agora vêm dos seus favoritos marcados "Alertar". Você ainda não marcou nenhum.')
    await expect(page.getByTestId('monitor-alert-origin-dated')).toHaveText(
      ' Até 26/10 você recebia os alertas do catálogo do Cripto Farol; agora cada pessoa escolhe os próprios.',
    )
    const link = banner.getByRole('link', { name: 'Marcar em Favoritos' })
    expect((await link.boundingBox())!.height).toBeGreaterThanOrEqual(44)
    await expect(link).toHaveAttribute('href', '/favorites')
  })

  test('faixa sem a frase com data para quem nunca recebeu', async ({ page }) => {
    await page.setViewportSize(DESKTOP)
    await mockMonitor(page, opportunities(), { show_banner: true, received_catalog_alerts: false, catalog_until: null })
    await page.goto('/monitor')
    await expect(page.getByTestId('monitor-alert-origin-banner')).toBeVisible()
    await expect(page.getByTestId('monitor-alert-origin-dated')).toHaveCount(0)
  })

  test('390 px: cartão com identidade, Alerta e estado completo; fonte antiga com o motivo; sem rolagem', async ({ page }) => {
    await page.setViewportSize(PHONE)
    await mockMonitor(page, opportunities({ nvda: { market_state: NVDA_STALE }, legacy: { market_state: WEEKEND } }))
    await page.goto('/monitor')
    const card = page.locator('.mobile-card').filter({ has: page.getByTestId('monitor-card-nvda') })
    await expect(card.getByTestId('monitor-card-meta-nvda')).toContainText('Ação · USD · Binance · NY · split')
    await expect(card.getByTestId('monitor-card-meta-nvda')).toContainText('Alerta')
    await expect(card.getByTestId('monitor-card-market-nvda')).toHaveText('Dados atrasados · último candle sex., 23 out.; esperado seg., 26 out.')
    await expect(card.getByTestId('monitor-card-market-nvda-hold')).toHaveText('Sinal em espera até o dado normalizar')
    const legacy = page.locator('.mobile-card').filter({ has: page.getByTestId('monitor-card-nvda-legacy') })
    await expect(legacy.getByTestId('monitor-card-market-nvda-legacy')).toHaveText(
      'Mercado fechado · fim de semana · abre seg., 26 out., 10:30 (09:30 em NY)',
    )
    await expect(legacy.getByRole('button', { name: 'Ver Trades NVDA (indisponível)' })).toHaveAttribute('aria-disabled', 'true')
    await expect(legacy.locator('.legacy-unavailable-why')).toHaveText('Fonte antiga: gráfico e trades depois da migração para a Binance.')
    await expect(card).toContainText('Ação/ETF na carteira recebe entrada e saída no Telegram.')
    expect(await fits(page)).toBe(true)
  })
})

// ---------------------------------------------------------------- Favoritos

const favBase = {
  strategy_name: 'multi_ma_crossover',
  strategy_display_name: 'Médias Móveis: Tendência em Virada',
  parameters: { direction: 'long', stop_loss: 0.05 },
  start_date: null,
  end_date: null,
  created_at: '2026-10-24T21:40:00Z',
  notes: null,
  auto_refresh_status: 'SUCCESS',
  auto_refresh_completed_at: '2026-10-24T11:12:00Z',
}

function favorites(spyNotify = true, catalog = false) {
  return [
    {
      ...favBase,
      id: 101,
      name: 'BTC',
      symbol: 'BTC/USDT',
      timeframe: '1d',
      tier: 1,
      notify_telegram: true,
      configuration: CRYPTO,
      is_curated_fallback: catalog,
      asset: { symbol: 'BTC/USDT', asset_class: 'crypto', currency: 'USDT' },
      metrics: { total_trades: 10 },
    },
    {
      ...favBase,
      id: 104,
      name: 'NVDA',
      symbol: 'NVDA',
      timeframe: '1d',
      tier: 2,
      notify_telegram: true,
      configuration: BINANCE,
      is_curated_fallback: catalog,
      asset: { symbol: 'NVDA', asset_class: 'stock', currency: 'USD' },
      metrics: { total_trades: 20, analysis_last_session: '2026-10-23' },
    },
    {
      ...favBase,
      id: 106,
      name: 'NVDA antiga',
      symbol: 'NVDA',
      timeframe: '1d',
      tier: 3,
      notify_telegram: false,
      configuration: STOOQ,
      is_curated_fallback: catalog,
      parameters: { direction: 'long', data_source: 'stooq' },
      asset: { symbol: 'NVDA', asset_class: 'stock', currency: 'USD' },
      metrics: { total_trades: 18 },
      auto_refresh_status: 'INSUFFICIENT',
      auto_refresh_error: '40 de 200 candles',
    },
    {
      ...favBase,
      id: 105,
      name: 'SPY',
      symbol: 'SPY',
      timeframe: '1d',
      tier: 3,
      notify_telegram: spyNotify,
      configuration: BINANCE,
      is_curated_fallback: catalog,
      asset: { symbol: 'SPY', asset_class: 'etf', currency: 'USD' },
      metrics: { total_trades: 22, analysis_last_session: '2026-10-23' },
    },
  ]
}

async function mockFavorites(page: Page, rows = favorites()) {
  await login(page)
  const patches: Array<{ id: string; body: Record<string, unknown> }> = []
  let current = rows
  await page.route('**/api/**', async (route: Route) => {
    const url = route.request().url()
    const method = route.request().method()
    if (url.includes('/api/auth/me')) return route.fulfill(json(USER))
    if (method === 'PATCH' && /\/api\/favorites\/\d+/.test(url)) {
      const id = url.split('/').pop()!
      const body = JSON.parse(route.request().postData() || '{}')
      patches.push({ id, body })
      current = current.map((row) => (String(row.id) === id ? { ...row, ...body } : row))
      return route.fulfill(json(current.find((row) => String(row.id) === id)))
    }
    if (/\/api\/favorites\/?(\?|$)/.test(url)) return route.fulfill(json(current))
    // SPY fora da carteira; NVDA dentro
    if (/\/api\/monitor\/preferences\/?$/.test(url)) {
      return route.fulfill(json({ NVDA: { in_portfolio: true }, SPY: { in_portfolio: false } }))
    }
    if (url.includes('/api/opportunities')) return route.fulfill(json([]))
    return route.fulfill(json({}))
  })
  return { patches }
}

const favRow = (page: Page, id: number) => page.getByTestId(`favorite-${id}`)

test.describe('Favoritos: "Alertar" do dono', () => {
  test('1440 px: coluna Alertar com aria-label desde a carga, estrelas e status de ação/ETF e o aviso fora da carteira', async ({ page }) => {
    await page.setViewportSize(DESKTOP)
    const { patches } = await mockFavorites(page)
    await page.goto('/favorites')
    await expect(page.locator('table.fav-strategies th.telegram-col')).toHaveText('Alertar')
    await expect(page.locator('table.fav-strategies th.telegram-col')).toBeVisible()
    await expect(page.getByTestId('alertar-column-101')).toHaveAttribute('aria-label', 'Alertar no Telegram: ligado')
    await expect(page.getByTestId('alertar-column-106')).toHaveAttribute('aria-label', 'Alertar no Telegram: desligado')
    await expect(page.getByTestId('alertar-column-106')).toHaveAttribute('aria-pressed', 'false')
    await expect(page.getByTestId('alertar-actions-104')).toBeHidden()
    // status de ação/ETF com o último pregão; série curta em "Aguardando dados"
    await expect(favRow(page, 104).getByTestId('fav-refresh-status')).toHaveText('Backtest atualizado: 24/10, 08:12 · último pregão 23/10')
    await expect(favRow(page, 106).getByTestId('fav-refresh-status')).toHaveText('Aguardando dados: 40 de 200 candles')
    await expect(favRow(page, 106).getByTestId('fav-conventions')).toHaveText('Stooq · fonte antiga · diário')
    // SPY com "Alertar" e fora da carteira: o aviso; NVDA na carteira: sem aviso
    const warning = favRow(page, 105).getByTestId('alertar-outside-portfolio-105')
    await expect(warning).toContainText('Fora da carteira: sem alerta.')
    await expect(warning.getByRole('link')).toHaveText('Marque o ativo como "No portfólio" no Monitor')
    await expect(favRow(page, 104).getByTestId('alertar-outside-portfolio-104')).toHaveCount(0)
    // resumo por estrelas com todas as classes, sem a nota "ainda não"
    await expect(page.locator('.tier-card-watch .tier-card-count')).toHaveText('2')
    await expect(page.locator('.tier-card-high .tier-card-count')).toHaveText('1')
    await expect(page.locator('.tier-card-top .tier-card-count')).toHaveText('1')
    await expect(page.getByText('ainda não para ações e ETFs')).toHaveCount(0)
    // desligar "Alertar" de SPY: PATCH do dono e o aviso some
    await page.getByTestId('alertar-column-105').click()
    await expect.poll(() => patches).toEqual([{ id: '105', body: { notify_telegram: false } }])
    await expect(page.getByTestId('alertar-column-105')).toHaveAttribute('aria-label', 'Alertar no Telegram: desligado')
    await expect(favRow(page, 105).getByTestId('alertar-outside-portfolio-105')).toHaveCount(0)
    // estrela de NVDA
    await favRow(page, 104).locator('.stars-cell button').nth(2).click()
    await expect.poll(() => patches.length).toBe(2)
    expect(await fits(page)).toBe(true)
  })

  test('1280 px mantém a coluna; 1024 px leva o sino para a célula Ações', async ({ page }) => {
    await page.setViewportSize({ width: 1280, height: 800 })
    const { patches } = await mockFavorites(page)
    await page.goto('/favorites')
    await expect(page.getByTestId('alertar-column-104')).toBeVisible()
    await expect(page.getByTestId('alertar-actions-104')).toBeHidden()
    await page.setViewportSize({ width: 1024, height: 768 })
    await expect(page.getByTestId('alertar-column-104')).toBeHidden()
    const bell = page.getByTestId('alertar-actions-104')
    await expect(bell).toBeVisible()
    await expect(bell).toHaveAttribute('aria-label', 'Alertar no Telegram: ligado')
    await bell.click()
    await expect.poll(() => patches).toEqual([{ id: '104', body: { notify_telegram: false } }])
    await expect(bell).toHaveAttribute('aria-pressed', 'false')
    expect(await fits(page)).toBe(true)
  })

  test('390 px: "Alertar: on/off" com alvo de 44 px', async ({ page }) => {
    await page.setViewportSize(PHONE)
    await mockFavorites(page)
    await page.goto('/favorites')
    const control = page.getByTestId('alertar-mobile-104')
    await expect(control).toHaveText('Alertar: on')
    await expect(control).toHaveAttribute('aria-label', 'Alertar no Telegram: ligado')
    const box = await control.boundingBox()
    expect(box!.height).toBeGreaterThanOrEqual(44)
    await expect(page.getByTestId('alertar-mobile-106')).toHaveText('Alertar: off')
    expect(await fits(page)).toBe(true)
  })

  test('vitrine do catálogo: faixa e nenhum controle "Alertar"', async ({ page }) => {
    await page.setViewportSize(DESKTOP)
    await mockFavorites(page, favorites(true, true))
    await page.goto('/favorites')
    const banner = page.getByTestId('favorites-catalog-banner')
    await expect(banner).toHaveAttribute('role', 'status')
    await expect(banner).toContainText('Estas estratégias são o catálogo do Cripto Farol e não mandam alerta.')
    await expect(page.getByTestId('alertar-column-104')).toHaveCount(0)
    await expect(favRow(page, 104).getByTestId('alertar-catalog-104')).toHaveText('Catálogo · não alerta')
  })
})

// ---------------------------------------------------------------- Resultado

const RESULT = {
  template_name: 'ema_rsi',
  symbol: 'NVDA',
  timeframe: '1d',
  start_date: null,
  end_date: null,
  period_type: 'all',
  asset: { symbol: 'NVDA', asset_id: 'binance:equity:EQ_NVDA', asset_class: 'stock', name: 'NVIDIA', currency: 'USD' },
  execution: {
    precision_requested: 'intrabar',
    precision_effective: 'candle',
    timeframe: '1d',
    window: { requested: { start: null, end: null }, covered: { start: '2014-11-11T05:00:00+00:00', end: '2026-10-22T04:00:00+00:00', candles: 2990 } },
  },
  conventions: { calendar: { kind: 'nyse_regular_session', sessions_per_year: 252 }, adjusted_prices: true },
  parameters: { direction: 'long', stop_loss: 0.05 },
  metrics: { total_return: 0.0669, total_return_pct: 6.69, win_rate: 1, total_trades: 1, sharpe_ratio: 0.9, max_drawdown: 0.05 },
  trades: [{ entry_time: '2026-02-02T05:00:00+00:00', entry_price: 191.3, exit_time: '2026-02-20T05:00:00+00:00', exit_price: 204.1, profit: 0.0669, type: 'long' }],
  indicator_data: {},
  candles: Array.from({ length: 30 }, (_, i) => ({
    timestamp_utc: new Date(Date.parse('2026-02-01T05:00:00Z') + i * 86_400_000).toISOString(),
    open: 190 + i,
    high: 192 + i,
    low: 188 + i,
    close: 191 + i,
    volume: 1000,
  })),
}

async function openResult(page: Page, saveStatus: { current: number }) {
  await login(page)
  const posts: Array<Record<string, any>> = []
  await page.route('**/api/**', async (route: Route) => {
    const url = route.request().url()
    if (url.includes('/api/auth/me')) return route.fulfill(json(USER))
    if (route.request().method() === 'POST' && /\/api\/favorites\/?$/.test(url)) {
      posts.push(JSON.parse(route.request().postData() || '{}'))
      if (saveStatus.current === 409) {
        return route.fulfill(json({ detail: 'Estratégia já existe nos favoritos com esta configuração' }, 409))
      }
      return route.fulfill(json({ id: 900, symbol: 'NVDA' }))
    }
    return route.fulfill(json({}))
  })
  await page.goto('/combo/results')
  await page.evaluate((result) => {
    history.replaceState({ usr: { result, isOptimization: true, returnTo: '/combo/configure' }, key: 'card-1122', idx: 0 }, '', location.href)
  }, RESULT)
  await page.reload()
  return { posts }
}

test.describe('Resultado: salvar ação nos Favoritos', () => {
  test('modal com identidade e nota, foco preso, Esc em qualquer foco, duplicata e sucesso com "Ver em Favoritos"', async ({ page }) => {
    await page.setViewportSize(DESKTOP)
    const status = { current: 409 }
    const { posts } = await openResult(page, status)
    const save = page.getByTestId('save-favorite-button')
    await expect(save).toBeVisible()
    await save.click()
    const dialog = page.getByRole('dialog', { name: 'Salvar nos Favoritos' })
    await expect(dialog).toHaveAttribute('aria-modal', 'true')
    await expect(dialog.getByTestId('favorite-identity')).toContainText('NVDA · Ação · USD')
    await expect(dialog.getByTestId('favorite-identity')).toContainText('Binance Ações · pregão regular de NY · ajustado por split · 1d · Long')
    await expect(dialog.getByTestId('favorite-alert-note')).toHaveText(
      'O favorito nasce sem alerta. Para receber os sinais no Telegram, marque "Alertar" em Favoritos e marque o ativo como "No portfólio" no Monitor.',
    )
    // foco preso: 12 Tab e 3 Shift+Tab não saem do modal
    for (let i = 0; i < 12; i += 1) {
      await page.keyboard.press('Tab')
      expect(await dialog.evaluate((el) => el.contains(document.activeElement))).toBe(true)
    }
    for (let i = 0; i < 3; i += 1) {
      await page.keyboard.press('Shift+Tab')
      expect(await dialog.evaluate((el) => el.contains(document.activeElement))).toBe(true)
    }
    // Esc com o foco fora do modal fecha e devolve o foco ao "Salvar nos Favoritos"
    await page.evaluate(() => (document.activeElement as HTMLElement | null)?.blur())
    await page.keyboard.press('Escape')
    await expect(dialog).toHaveCount(0)
    await expect(save).toBeFocused()

    // duplicata: texto no modal, nada salvo
    await save.click()
    await dialog.getByRole('button', { name: 'Salvar', exact: true }).click()
    await expect(dialog.getByTestId('favorite-duplicate')).toHaveText(
      'Já está nos favoritos com esta configuração (fonte, sessão e ajuste). Nada foi salvo.',
    )
    await expect(dialog.getByTestId('favorite-duplicate')).toHaveAttribute('role', 'alert')
    expect(posts[0].parameters.data_source).toBe('binance_equity')
    expect(posts[0].metrics.analysis_asset.asset_class).toBe('stock')
    expect(posts[0].metrics.analysis_conventions.adjusted_prices).toBe(true)
    await page.keyboard.press('Escape')
    await expect(save).toBeFocused()

    // sucesso: "Ver em Favoritos" (44 px) recebe o foco
    status.current = 200
    await save.click()
    await dialog.getByRole('button', { name: 'Salvar', exact: true }).click()
    const link = dialog.getByTestId('favorite-saved-link')
    await expect(link).toBeFocused()
    await expect(link).toHaveText('Ver em Favoritos')
    expect((await link.boundingBox())!.height).toBeGreaterThanOrEqual(44)
    await expect(dialog.getByTestId('favorite-saved')).toContainText('Salvo em Favoritos com a configuração Binance Ações.')
  })
})

// ---------------------------------------------------------------- Perfil

test('Perfil: a frase da origem dos alertas', async ({ page }) => {
  await page.setViewportSize(DESKTOP)
  await login(page)
  await page.route('**/api/**', async (route: Route) => {
    const url = route.request().url()
    if (url.includes('/api/auth/me')) return route.fulfill(json(USER))
    if (url.includes('/api/users/me/telegram-settings')) {
      return route.fulfill(json({ telegramAlertsEnabled: true, telegramUsername: 'bia', telegramLinked: true }))
    }
    return route.fulfill(json({}))
  })
  await page.goto('/profile')
  await expect(
    page.getByText('Receba DMs individuais quando mudar a leitura de um favorito seu marcado "Alertar" (cripto, ação ou ETF) com o ativo na sua carteira. Mercado fechado e feriado aparecem só no Monitor.'),
  ).toBeVisible()
})
