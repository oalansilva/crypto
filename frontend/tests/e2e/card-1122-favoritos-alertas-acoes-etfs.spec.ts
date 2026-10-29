import { expect, test, type Browser, type Page, type Route } from '@playwright/test'

/**
 * Card #1122: alertas das estratégias que cada pessoa acompanha no Monitor, em cripto, ação e ETF, com a
 * API simulada. Regra de 27/10/2026 (Design d2, tarefa 8.11), como no protótipo aprovado
 * (frontend/public/prototypes/card-1122-favoritos-alertas-acoes-etfs/):
 * - Monitor: interruptor "Alerta" por estratégia na linha (1280 px ou mais), na célula Status (1024 a
 *   1279 px), no cartão (390) e no detalhe; vitrine com "Catálogo · sem alerta" e a faixa nova; sem a tag
 *   "Alerta"; ajuda da carteira só no detalhe; frase da ajuda do Monitor; atraso por outro tempo gráfico;
 *   admin abre em "Em portfólio" sem aviso;
 * - Favoritos sem "Alertar", legenda "No Monitor"/"Fora do Monitor", resumo "Acompanhar", estrelas de 44 px
 *   no celular, status das estrelas e vitrine;
 * - textos do Resultado e do Perfil (a Descoberta fica no spec do #1121).
 * O que não mudou desde o Design anterior (linha compacta, estado do mercado, fonte antiga) segue coberto.
 */

const USER = { id: 'card-1122', email: 'bia@example.com', name: 'Bia', isAdmin: false, mustChangePassword: false }
const ADMIN = { ...USER, id: 'card-1122-admin', email: 'alan@example.com', name: 'Alan', isAdmin: true }
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
// NVDA 1d em espera por causa do 15m (o candle 1d de sexta chegou; falta o 15m das 14:30 BRT).
const NVDA_STALE_15M = {
  state: 'stale',
  reason: 'delay',
  last_candle: '2026-10-23T04:00:00+00:00',
  expected_candle: '2026-10-23T04:00:00+00:00',
  stale_timeframe: '15m',
  stale_detail: {
    timeframe: '15m',
    last_candle: '2026-10-26T17:15:00+00:00',
    expected_candle: '2026-10-26T17:30:00+00:00',
  },
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
      notify_telegram: true,
      market_state: { state: 'insufficient', reason: 'insufficient', available: 40, required: 200 },
      ...overrides.qqq,
    })
  }
  return rows
}

const catalogRows = (): Opp[] =>
  opportunities().slice(0, 2).map((row) => ({ ...row, is_curated_fallback: true, notify_telegram: false }))

const PREFERENCES = {
  __global__: { in_portfolio: false, card_mode: 'price', price_timeframe: '1d', theme: 'dark-green' },
  'BTC/USDT': { in_portfolio: true, card_mode: 'price', price_timeframe: '1d', theme: 'dark-green' },
  NVDA: { in_portfolio: true, card_mode: 'price', price_timeframe: '1d', theme: 'dark-green' },
  SPY: { in_portfolio: true, card_mode: 'price', price_timeframe: '1d', theme: 'dark-green' },
}

const json = (body: unknown, status = 200) => ({ status, contentType: 'application/json', body: JSON.stringify(body) })

async function login(page: Page, user: typeof USER = USER) {
  await page.addInitScript((user) => {
    localStorage.setItem('auth_access_token', 'tok')
    localStorage.setItem('auth_refresh_token', 'ref')
    localStorage.setItem('auth_user', JSON.stringify(user))
    localStorage.setItem('cripto-farol-onboarding-dismissed', '1')
  }, user)
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
// Segunda, 26 out. 2026, 15:00 BRT (cenário "Atraso no 15m" do protótipo).
const MONDAY_15H = new Date('2026-10-26T18:00:00Z')

type Origin = { show_banner: boolean; received_catalog_alerts: boolean; catalog_until: string | null }
const NO_BANNER: Origin = { show_banner: false, received_catalog_alerts: false, catalog_until: null }

async function mockMonitor(
  page: Page,
  rows: Opp[],
  options: {
    origin?: Origin
    user?: typeof USER
    preferences?: Record<string, unknown>
    now?: Date
    patchStatus?: number
  } = {},
) {
  const user = options.user ?? USER
  await login(page, user)
  await page.clock.setFixedTime(options.now ?? SATURDAY)
  const requests: string[] = []
  const patches: Array<{ id: string; body: Record<string, unknown> }> = []
  const state = { patchStatus: options.patchStatus ?? 200 }
  await page.route('**/api/**', async (route: Route) => {
    const url = route.request().url()
    const method = route.request().method()
    requests.push(url)
    if (url.includes('/api/auth/me')) return route.fulfill(json(user))
    if (method === 'PATCH' && /\/api\/favorites\/\d+/.test(url)) {
      patches.push({ id: url.split('/').pop()!, body: JSON.parse(route.request().postData() || '{}') })
      return route.fulfill(json({ detail: 'erro' }, state.patchStatus))
    }
    if (url.includes('/api/opportunities/alert-origin')) return route.fulfill(json(options.origin ?? NO_BANNER))
    if (url.includes('/api/opportunities')) return route.fulfill(json(rows))
    if (/\/api\/favorites\/?(\?|$)/.test(url)) return route.fulfill(json([{ id: 21, symbol: 'NVDA' }]))
    if (/\/api\/monitor\/preferences\/?$/.test(url)) return route.fulfill(json(options.preferences ?? PREFERENCES))
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
  return { requests, patches, state }
}

const fits = (page: Page) => page.evaluate(() => document.documentElement.scrollWidth <= document.documentElement.clientWidth)
const NVDA_ALERT_NAME = 'Alerta no Telegram · NVDA 1d · Médias Móveis: Tendência em Virada · Binance Ações'
const LEGACY_ALERT_NAME = 'Alerta no Telegram · NVDA 1d · Médias Móveis: Tendência em Virada · Stooq fonte antiga'
const BTC_ALERT_NAME = 'Alerta no Telegram · BTC/USDT 1d · Médias Móveis: Tendência em Virada'
const MONITOR_HELP =
  'Toda estratégia aqui manda alerta no Telegram, com ou sem o ativo na carteira; para parar de receber, desligue o "Alerta" da linha.'
const WALLET_HELP = 'Entrada e saída saem com ou sem o ativo na carteira. Desligado, nada sai no Telegram para esta estratégia.'

test.describe('Monitor: ação, ETF e o interruptor "Alerta"', () => {
  test('1440 px: linha compacta, estado sob a pílula, fonte antiga indisponível e sem a tag "Alerta"', async ({ page }) => {
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
    await expect(page.getByTestId('monitor-row-market-btc-usdt')).toHaveCount(0)
    // d2: a tag "Alerta" sai das Tags (o estado fica no interruptor)
    await expect(page.locator('[data-testid^="monitor-row-alert-"]')).toHaveCount(0)
    await expect(nvda.locator('.col-tags')).not.toContainText('Alerta')
    // "Em carteira" conta ativos distintos (as duas NVDA contam uma vez)
    await expect(page.locator('.kpi').filter({ hasText: 'Em carteira' }).locator('.kpi-val')).toHaveText('3')
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

    const btcHeight = (await page.getByTestId('monitor-row-btc-usdt').boundingBox())!.height
    const nvdaHeight = (await nvda.boundingBox())!.height
    expect(nvdaHeight).toBeLessThanOrEqual(btcHeight * 1.35)
    expect(await fits(page)).toBe(true)
  })

  test('1440 px: interruptor na célula de ações, nome acessível, sem abrir a linha, detalhe sincronizado e ajuda', async ({ page }) => {
    await page.setViewportSize(DESKTOP)
    const { patches } = await mockMonitor(page, opportunities())
    await page.goto('/monitor')
    await expect(page.getByTestId('monitor-help-alert')).toHaveText(` ${MONITOR_HELP}`)
    const row = page.getByTestId('monitor-row-nvda')
    const toggle = row.getByRole('switch', { name: NVDA_ALERT_NAME })
    await expect(toggle).toBeVisible()
    await expect(toggle).toHaveAttribute('aria-checked', 'true')
    await expect(toggle).toHaveText('Alertaligado')
    await expect(toggle.locator('.alert-switch-state')).toHaveAttribute('aria-hidden', 'true')
    // primeiro botão da célula de ações, antes de "Abrir Gráfico"
    await expect(row.locator('.actions-cell .row-actions > *').first()).toHaveAttribute('role', 'switch')
    // a 1440 px o da célula Status fica escondido: um interruptor por largura
    await expect(page.getByTestId('monitor-alert-compact-nvda')).toBeHidden()
    // duas linhas de NVDA: nomes distintos pela configuração; a fonte antiga desligada
    const legacy = page.getByTestId('monitor-row-nvda-legacy').getByRole('switch', { name: LEGACY_ALERT_NAME })
    await expect(legacy).toHaveAttribute('aria-checked', 'false')
    await expect(legacy).toHaveText('Alertadesligado')
    await expect(page.getByTestId('monitor-row-btc-usdt').getByRole('switch', { name: BTC_ALERT_NAME })).toBeVisible()

    // desligar: grava, anuncia e não abre a linha
    await toggle.click()
    await expect.poll(() => patches).toEqual([{ id: '21', body: { notify_telegram: false } }])
    await expect(toggle).toHaveAttribute('aria-checked', 'false')
    await expect(toggle).toHaveText('Alertadesligado')
    await expect(row).toHaveAttribute('aria-expanded', 'false')
    await expect(page.getByTestId('monitor-alert-status')).toHaveText(
      'Alerta de NVDA 1d desligado: nada sai no Telegram para esta estratégia.',
    )
    await expect(page.getByTestId('monitor-alert-status')).toHaveAttribute('role', 'status')

    // o detalhe abre com o estado atual; religar no detalhe religa a linha
    await row.getByRole('button', { name: 'Expandir' }).click()
    const detail = page.locator('tr.detail-row').filter({ has: page.getByTestId('monitor-card-nvda') })
    const detailToggle = detail.getByRole('switch', { name: NVDA_ALERT_NAME })
    await expect(detailToggle).toHaveAttribute('aria-checked', 'false')
    await expect(detailToggle).toHaveText('Alerta:desligado')
    await expect(detail.getByTestId('monitor-alert-help-nvda')).toHaveText(WALLET_HELP)
    await expect(detail).not.toContainText('Ação/ETF na carteira recebe entrada e saída no Telegram.')
    await expect(detail.getByTestId('monitor-card-meta-nvda')).not.toContainText('Alerta')
    await detailToggle.click()
    await expect.poll(() => patches.length).toBe(2)
    expect(patches[1]).toEqual({ id: '21', body: { notify_telegram: true } })
    await expect(toggle).toHaveAttribute('aria-checked', 'true')
    await expect(detailToggle).toHaveAttribute('aria-checked', 'true')
    // desligar na linha desliga o detalhe aberto
    await toggle.click()
    await expect(detailToggle).toHaveAttribute('aria-checked', 'false')
    await expect(row).toHaveAttribute('aria-expanded', 'true')
    expect(await fits(page)).toBe(true)
  })

  test('erro ao gravar: o interruptor volta e o status diz "Tente de novo"', async ({ page }) => {
    await page.setViewportSize(DESKTOP)
    const { patches } = await mockMonitor(page, opportunities(), { patchStatus: 500 })
    await page.goto('/monitor')
    const toggle = page.getByTestId('monitor-row-nvda').getByRole('switch', { name: NVDA_ALERT_NAME })
    await toggle.click()
    await expect.poll(() => patches.length).toBe(1)
    await expect(page.getByTestId('monitor-alert-status')).toHaveText('Não foi possível mudar o alerta. Tente de novo.')
    await expect(toggle).toHaveAttribute('aria-checked', 'true')
  })

  for (const width of [1280, 1024]) {
    test(`${width} px: um interruptor por linha, dentro da área visível`, async ({ page }) => {
      await page.setViewportSize({ width, height: 800 })
      const { patches } = await mockMonitor(page, opportunities())
      await page.goto('/monitor')
      const rowSwitch = page.getByTestId('monitor-alert-row-nvda')
      const compact = page.getByTestId('monitor-alert-compact-nvda')
      const shown = width >= 1280 ? rowSwitch : compact
      const hidden = width >= 1280 ? compact : rowSwitch
      await expect(shown).toBeVisible()
      await expect(hidden).toBeHidden()
      await expect(shown).toHaveAccessibleName(NVDA_ALERT_NAME)
      const box = (await shown.boundingBox())!
      const board = (await page.locator('.monitor-main').boundingBox())!
      expect(box.x + box.width, 'interruptor dentro da área do Monitor').toBeLessThanOrEqual(board.x + board.width + 1)
      if (width < 1280) {
        // na célula Status, abaixo da pílula e do estado do mercado
        const status = page.getByTestId('monitor-row-nvda').locator('td').nth(2)
        await expect(status.getByRole('switch')).toHaveCount(1)
        const pill = (await page.getByTestId('monitor-row-signal-nvda').boundingBox())!
        expect(box.y).toBeGreaterThan(pill.y)
      }
      await shown.click()
      await expect.poll(() => patches).toEqual([{ id: '21', body: { notify_telegram: false } }])
      await expect(shown).toHaveAttribute('aria-checked', 'false')
      await expect(page.getByTestId('monitor-row-nvda')).toHaveAttribute('aria-expanded', 'false')
    })
  }

  test('célula de ações: botões da mesma largura, rótulo em uma linha; coluna única abaixo de 1600 e 2 × 2 a partir de 1600', async ({ page }) => {
    for (const viewport of [{ width: 1440, height: 900 }, { width: 1600, height: 900 }]) {
      await page.setViewportSize(viewport)
      await mockMonitor(page, opportunities(), { user: ADMIN })
      await page.goto('/monitor')
      await page.getByTestId('monitor-filter-all').click()
      const buttons = page.getByTestId('monitor-row-btc-usdt').locator('.actions-cell .row-actions > *')
      await expect(buttons).toHaveCount(4)
      const boxes = await buttons.evaluateAll((els) =>
        els.map((el) => {
          const r = el.getBoundingClientRect()
          return { x: Math.round(r.x), y: Math.round(r.y), w: Math.round(r.width), h: Math.round(r.height) }
        }),
      )
      const columns = [...new Set(boxes.map((b) => b.x))]
      expect(columns.length, `colunas a ${viewport.width} px: ${JSON.stringify(boxes)}`).toBe(viewport.width >= 1600 ? 2 : 1)
      for (const x of columns) {
        const widths = boxes.filter((b) => b.x === x).map((b) => b.w)
        expect(Math.max(...widths) - Math.min(...widths), `mesma largura na coluna ${x}`).toBeLessThanOrEqual(1)
      }
      // rótulo em uma linha (altura de um botão de 1 linha)
      for (const b of boxes) expect(b.h).toBeLessThanOrEqual(32)
      expect(await fits(page)).toBe(true)
      await page.unrouteAll({ behavior: 'ignoreErrors' })
    }
  })

  test('390 px: cartão com "Alerta: ligado" de 44 px, sem a ajuda da carteira; fonte antiga com o motivo', async ({ page }) => {
    await page.setViewportSize(PHONE)
    const { patches } = await mockMonitor(page, opportunities({ nvda: { market_state: NVDA_STALE }, legacy: { market_state: WEEKEND } }))
    await page.goto('/monitor')
    await expect(page.getByTestId('monitor-help-alert')).toBeVisible()
    const card = page.locator('.mobile-card').filter({ has: page.getByTestId('monitor-card-nvda') })
    const toggle = card.getByRole('switch', { name: NVDA_ALERT_NAME })
    await expect(toggle).toHaveText('Alerta:ligado')
    expect((await toggle.boundingBox())!.height).toBeGreaterThanOrEqual(44)
    await expect(card.getByTestId('monitor-card-meta-nvda')).toContainText('Ação · USD · Binance · NY · split')
    await expect(card.getByTestId('monitor-card-meta-nvda')).not.toContainText('Alerta')
    await expect(card.getByTestId('monitor-card-market-nvda')).toHaveText('Dados atrasados · último candle sex., 23 out.; esperado seg., 26 out.')
    await expect(card.getByTestId('monitor-card-market-nvda-hold')).toHaveText('Sinal em espera até o dado normalizar')
    // o cartão não repete a ajuda da carteira (ela está na ajuda do Monitor)
    await expect(card).not.toContainText(WALLET_HELP)
    await expect(card).not.toContainText('Ação/ETF na carteira recebe entrada e saída no Telegram.')
    const legacy = page.locator('.mobile-card').filter({ has: page.getByTestId('monitor-card-nvda-legacy') })
    await expect(legacy.getByRole('switch', { name: LEGACY_ALERT_NAME })).toHaveText('Alerta:desligado')
    await expect(legacy.getByRole('button', { name: 'Ver Trades NVDA (indisponível)' })).toHaveAttribute('aria-disabled', 'true')
    await expect(legacy.locator('.legacy-unavailable-why')).toHaveText('Fonte antiga: gráfico e trades depois da migração para a Binance.')
    // NVDA atrasada: só o sinal fica em espera; os campos de risco seguem com o valor
    const risk = card.getByTestId('monitor-risk-block-nvda')
    await expect(risk).not.toContainText('indisponível — dado não confiável')
    await expect(risk).toContainText('$173.28')
    await expect(card.getByTestId('monitor-detail-configuration-nvda')).toHaveCount(0)
    await toggle.click()
    await expect.poll(() => patches).toEqual([{ id: '21', body: { notify_telegram: false } }])
    await expect(toggle).toHaveText('Alerta:desligado')
    expect(await fits(page)).toBe(true)
    // altura do cartão de NVDA atrasada contra o protótipo (cenário "Dados atrasados")
    const proto = await (await page.context().browser()!.newContext({ viewport: PHONE })).newPage()
    await proto.goto('/prototypes/card-1122-favoritos-alertas-acoes-etfs/index.html')
    await proto.locator('[data-set-scenario="delay"]').first().click()
    const protoCard = proto.locator('[data-m22-view="own"] .mobile-card').filter({ has: proto.locator('[data-testid="monitor-card-nvda"]') })
    const protoHeight = (await protoCard.first().boundingBox())!.height
    const height = (await card.boundingBox())!.height
    expect(Math.abs(height - protoHeight), `altura do cartão de NVDA: protótipo ${protoHeight} x ${height}`).toBeLessThanOrEqual(30)
  })

  test('390 px: cripto atrasada segue como hoje (risco indisponível e o estado na linha "alerta")', async ({ page }) => {
    await page.setViewportSize(PHONE)
    await mockMonitor(page, opportunities({ btc: { market_state: BTC_STALE, entry_price: 64000, stop_price: 60800, distance_to_stop_pct: 9.2 } }))
    await page.goto('/monitor')
    const card = page.locator('.mobile-card').filter({ has: page.getByTestId('monitor-card-btc-usdt') })
    await expect(card.getByTestId('monitor-risk-block-btc-usdt')).toContainText('indisponível — dado não confiável')
    await expect(card.getByTestId('monitor-detail-strategy-identity-btc-usdt')).toContainText('alerta Dados atrasados')
  })

  test('pregão aberto, feriado, atraso de ação e de cripto e dado insuficiente', async ({ page }) => {
    await page.setViewportSize(DESKTOP)
    await mockMonitor(page, opportunities({ spy: { market_state: HOLIDAY }, nvda: { market_state: NVDA_STALE }, btc: { market_state: BTC_STALE }, qqq: {} }))
    await page.goto('/monitor')
    await expect(page.getByTestId('monitor-row-market-nvda-legacy')).toHaveText('Aberto · fecha 17:00 (16:00 NY)')
    await expect(page.getByTestId('monitor-row-market-spy')).toHaveText('Fechado · feriado em NY · abre sex. 11:30 (09:30 NY)')
    const nvda = page.getByTestId('monitor-row-market-nvda')
    await expect(nvda).toHaveAttribute('data-tone', 'stale')
    await expect(nvda).toHaveText('Dados atrasados · falta seg. 26/10')
    await expect(page.getByTestId('monitor-row-market-nvda-hold')).toHaveText('Sinal em espera')
    await expect(page.getByTestId('monitor-row-market-btc-usdt')).toHaveText('Dados atrasados · falta sáb. 24/10')
    await page.getByTestId('monitor-row-btc-usdt').getByRole('button', { name: 'Expandir' }).click()
    const btcDetail = page.locator('tr.detail-row').filter({ has: page.getByTestId('monitor-card-btc-usdt') })
    await expect(btcDetail).toContainText('Dados atrasados · último candle sex., 23 out.; esperado sáb., 24 out.')
    await expect(btcDetail).not.toContainText('Sem candle válido/atual')
    await expect(page.getByTestId('monitor-section-exit').getByTestId('monitor-row-qqq')).toBeVisible()
    await expect(page.getByTestId('monitor-row-signal-qqq')).toHaveText('Sem leitura')
    await expect(page.getByTestId('monitor-row-market-qqq')).toHaveText('Dados insuficientes · 40 de 200 candles')
    await expect(page.getByTestId('monitor-row-market-qqq-hold')).toHaveText('Sem sinal')
  })

  test('atraso no 15m: a linha 1d diz "no 15m · falta 14:30" e o cartão o último e o esperado do 15m', async ({ page }) => {
    await page.setViewportSize(DESKTOP)
    await mockMonitor(page, opportunities({ nvda: { market_state: NVDA_STALE_15M } }), { now: MONDAY_15H })
    await page.goto('/monitor')
    const state = page.getByTestId('monitor-row-market-nvda')
    await expect(state).toHaveAttribute('data-tone', 'stale')
    await expect(state).toHaveText('Dados atrasados no 15m · falta 14:30')
    await expect(state).toHaveAttribute('title', 'Dados atrasados no 15m · último 14:15; esperado 14:30')
    await expect(state).not.toContainText('26/10')
    await expect(page.getByTestId('monitor-row-market-nvda-hold')).toHaveText('Sinal em espera')
    await page.getByTestId('monitor-row-nvda').getByRole('button', { name: 'Expandir' }).click()
    const detail = page.locator('tr.detail-row').filter({ has: page.getByTestId('monitor-card-nvda') })
    await expect(detail.getByTestId('monitor-card-market-nvda')).toHaveText('Dados atrasados no 15m · último 14:15; esperado 14:30')
    await page.setViewportSize(PHONE)
    const card = page.locator('.mobile-card').filter({ has: page.getByTestId('monitor-card-nvda') })
    await expect(card.getByTestId('monitor-card-market-nvda')).toHaveText('Dados atrasados no 15m · último 14:15; esperado 14:30')
  })

  test('admin abre em "Em portfólio" sem aviso; "Todos" mostra a estratégia fora da carteira com o interruptor', async ({ page }) => {
    await page.setViewportSize(DESKTOP)
    const outside = { ...PREFERENCES, NVDA: { in_portfolio: false, card_mode: 'price', price_timeframe: '1d', theme: 'dark-green' } }
    await mockMonitor(page, opportunities(), { user: ADMIN, preferences: outside })
    await page.goto('/monitor')
    await expect(page.getByTestId('monitor-filter-in-portfolio')).toHaveClass(/on/)
    await expect(page.getByTestId('monitor-row-btc-usdt')).toBeVisible()
    await expect(page.getByTestId('monitor-row-nvda')).toHaveCount(0)
    await expect(page.getByText(/fora da carteira com alerta/i)).toHaveCount(0)
    await expect(page.getByText('Ver todos')).toHaveCount(0)
    await page.getByTestId('monitor-filter-all').click()
    await expect(page.getByTestId('monitor-row-nvda').getByRole('switch', { name: NVDA_ALERT_NAME })).toHaveAttribute('aria-checked', 'true')
  })

  test('vitrine: "Catálogo · sem alerta", faixa nova com a frase datada e sem a ajuda do alerta', async ({ page }) => {
    await page.setViewportSize(DESKTOP)
    await mockMonitor(page, catalogRows(), { origin: { show_banner: true, received_catalog_alerts: true, catalog_until: '2026-10-26' } })
    await page.goto('/monitor')
    const banner = page.getByTestId('monitor-alert-origin-banner')
    await expect(banner).toHaveAttribute('role', 'status')
    await expect(banner.locator('strong')).toHaveText('Estas estratégias são o catálogo do Cripto Farol: só exibição, sem alerta no Telegram.')
    await expect(banner).toContainText(
      'Os alertas vêm das estratégias que você acompanha no Monitor. Dê pelo menos 1 estrela a uma estratégia sua em Favoritos (ou salve lá um resultado do Combo): ela entra aqui com o alerta ligado.',
    )
    await expect(page.getByTestId('monitor-alert-origin-dated')).toHaveText(
      ' Até 26/10 você recebia os alertas do catálogo; agora cada pessoa recebe os das próprias estratégias.',
    )
    await expect(banner).not.toContainText('Você ainda não marcou nenhum')
    // ícone de informação, não o sino
    await expect(banner.locator('svg.lucide-info')).toHaveCount(1)
    await expect(banner.locator('svg.lucide-bell')).toHaveCount(0)
    const link = banner.getByRole('link', { name: 'Ir para Favoritos' })
    expect((await link.boundingBox())!.height).toBeGreaterThanOrEqual(44)
    await expect(link).toHaveAttribute('href', '/favorites')
    const none = page.getByTestId('monitor-alert-catalog-row-btc-usdt')
    await expect(none).toHaveText('Catálogo · sem alerta')
    expect(await none.evaluate((el) => getComputedStyle(el).fontSize)).toBe('12px')
    await expect(page.getByRole('switch')).toHaveCount(0)
    await expect(page.getByTestId('monitor-help-alert')).toHaveCount(0)
    await page.setViewportSize(PHONE)
    const card = page.locator('.mobile-card').filter({ has: page.getByTestId('monitor-card-btc-usdt') })
    await expect(card.getByTestId('monitor-alert-catalog-card-btc-usdt')).toHaveText('Catálogo · sem alerta')
    expect(await fits(page)).toBe(true)
  })

  test('vitrine sem a frase com data para quem nunca recebeu', async ({ page }) => {
    await page.setViewportSize(DESKTOP)
    await mockMonitor(page, catalogRows(), { origin: { show_banner: true, received_catalog_alerts: false, catalog_until: null } })
    await page.goto('/monitor')
    await expect(page.getByTestId('monitor-alert-origin-banner')).toBeVisible()
    await expect(page.getByTestId('monitor-alert-origin-dated')).toHaveCount(0)
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

function favorites(catalog = false) {
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
      id: 107,
      name: 'multi_ma_crossover - QQQ 1d (batch)',
      symbol: 'QQQ',
      timeframe: '1d',
      tier: null,
      notify_telegram: true,
      configuration: BINANCE,
      notes: 'gerado em lote (b41d7e20)',
      is_curated_fallback: catalog,
      asset: { symbol: 'QQQ', asset_class: 'etf', currency: 'USD' },
      metrics: { total_trades: 25, analysis_last_session: '2026-10-23' },
    },
  ]
}

async function mockFavorites(
  page: Page,
  rows: Array<Record<string, unknown>> = favorites(),
  user: typeof USER = USER,
  { failPatch = false }: { failPatch?: boolean } = {},
) {
  await login(page, user)
  const patches: Array<{ id: string; body: Record<string, unknown> }> = []
  let current = rows
  await page.route('**/api/**', async (route: Route) => {
    const url = route.request().url()
    const method = route.request().method()
    if (url.includes('/api/auth/me')) return route.fulfill(json(user))
    if (method === 'PATCH' && /\/api\/favorites\/\d+/.test(url)) {
      const id = url.split('/').pop()!
      const body = JSON.parse(route.request().postData() || '{}')
      patches.push({ id, body })
      if (failPatch) return route.fulfill({ status: 500, contentType: 'application/json', body: '{"detail":"boom"}' })
      current = current.map((row) => (String(row.id) === id ? { ...row, ...body } : row))
      return route.fulfill(json(current.find((row) => String(row.id) === id)))
    }
    if (/\/api\/favorites\/?(\?|$)/.test(url)) return route.fulfill(json(current))
    if (/\/api\/monitor\/preferences\/?$/.test(url)) {
      return route.fulfill(json({ NVDA: { in_portfolio: true }, SPY: { in_portfolio: false } }))
    }
    if (url.includes('/api/opportunities')) return route.fulfill(json([]))
    return route.fulfill(json({}))
  })
  return { patches }
}

const favRow = (page: Page, id: number) => page.getByTestId(`favorite-${id}`)
const STAR_HELP =
  'Com pelo menos 1 estrela, a estratégia entra no Monitor e manda alerta no Telegram, ligado por padrão (desligue no Monitor). Sem estrela, fica só aqui; lote e Descoberta salvam sem estrela.'

async function expectNoAlertar(page: Page) {
  await expect(page.getByText(/Alertar/)).toHaveCount(0)
  await expect(page.locator('.telegram-col')).toHaveCount(0)
  await expect(page.locator('[data-testid^="alertar-"]')).toHaveCount(0)
  await expect(page.getByText(/Fora da carteira/)).toHaveCount(0)
}

test.describe('Favoritos: a estrela é a porta do Monitor', () => {
  test('1440 px: sem "Alertar", ajuda, legenda, resumo "Acompanhar" e o status da primeira e da última estrela', async ({ page }) => {
    await page.setViewportSize(DESKTOP)
    const { patches } = await mockFavorites(page)
    await page.goto('/favorites')
    await expect(favRow(page, 104)).toBeVisible()
    await expectNoAlertar(page)
    await expect(page.getByTestId('fav-monitor-help')).toHaveText(STAR_HELP)
    await expect(page.locator('.tier-card-watch .tier-card-helper')).toHaveText('No Monitor, com alerta ligado')
    await expect(page.getByText('Monitorar quando fizer sentido')).toHaveCount(0)
    await expect(page.locator('.tier-card-high .tier-card-helper')).toHaveText('Prioridade intermediária')
    await expect(page.locator('.tier-card-top .tier-card-helper')).toHaveText('Fila principal do Monitor')
    await expect(page.getByTestId('fav-monitor-legend-row-104')).toHaveText('No Monitor')
    await expect(page.getByTestId('fav-monitor-legend-row-107')).toHaveText('Fora do Monitor')
    // status de ação/ETF com o último pregão; série curta em "Aguardando dados"
    await expect(favRow(page, 104).getByTestId('fav-refresh-status')).toHaveText('Backtest atualizado: 24/10, 08:12 · último pregão 23/10')
    await expect(favRow(page, 106).getByTestId('fav-refresh-status')).toHaveText('Aguardando dados: 40 de 200 candles')
    // estrelas com aria-label
    const qqqStars = favRow(page, 107).locator('.stars-cell button')
    await expect(qqqStars.nth(0)).toHaveAttribute('aria-label', '1 estrela')
    await expect(qqqStars.nth(2)).toHaveAttribute('aria-label', '3 estrelas')
    // primeira estrela em QQQ (lote, sem estrela)
    await qqqStars.nth(0).click()
    await expect.poll(() => patches).toEqual([{ id: '107', body: { tier: 3 } }])
    await expect(page.getByTestId('fav-star-status')).toHaveText('QQQ 1d entrou no Monitor com o alerta ligado.')
    await expect(page.getByTestId('fav-star-status')).toHaveAttribute('role', 'status')
    await expect(page.getByTestId('fav-monitor-legend-row-107')).toHaveText('No Monitor · alerta ligado')
    // subir para 2 estrelas não mexe no alerta
    await favRow(page, 107).locator('.stars-cell button').nth(1).click()
    await expect.poll(() => patches.length).toBe(2)
    await expect(page.getByTestId('fav-star-status')).toHaveText('QQQ 1d: 2 estrelas; o alerta no Monitor fica como estava.')
    // tirar a última estrela
    await favRow(page, 107).locator('.stars-cell button').nth(1).click()
    await expect.poll(() => patches.length).toBe(3)
    expect(patches[2]).toEqual({ id: '107', body: { tier: null } })
    await expect(page.getByTestId('fav-star-status')).toHaveText('QQQ 1d saiu do Monitor e não manda mais alerta.')
    await expect(page.getByTestId('fav-monitor-legend-row-107')).toHaveText('Fora do Monitor')
    expect(await fits(page)).toBe(true)
  })

  test('PATCH das estrelas falha: o status anuncia o erro, não a entrada no Monitor', async ({ page }) => {
    await page.setViewportSize(DESKTOP)
    const { patches } = await mockFavorites(page, favorites(), USER, { failPatch: true })
    await page.goto('/favorites')
    await expect(favRow(page, 107)).toBeVisible()
    await favRow(page, 107).locator('.stars-cell button').nth(0).click()
    await expect.poll(() => patches).toEqual([{ id: '107', body: { tier: 3 } }])
    const status = page.getByTestId('fav-star-status')
    await expect(status).toHaveAttribute('role', 'status')
    await expect(status).toHaveText('Não foi possível salvar as estrelas de QQQ 1d. Tente de novo.')
    await expect(status).not.toContainText('entrou no Monitor')
    await expect(page.getByTestId('fav-monitor-legend-row-107')).toHaveText('Fora do Monitor')
  })

  for (const viewport of [{ width: 1280, height: 800 }, { width: 1024, height: 768 }]) {
    test(`${viewport.width} px: sem "Alertar" (nem coluna nem sino na célula Ações) e com a legenda`, async ({ page }) => {
      await page.setViewportSize(viewport)
      await mockFavorites(page)
      await page.goto('/favorites')
      await expect(favRow(page, 104)).toBeVisible()
      await expectNoAlertar(page)
      await expect(favRow(page, 104).locator('.fav-row-actions .lucide-bell')).toHaveCount(0)
      await expect(page.getByTestId('fav-monitor-legend-row-104')).toBeVisible()
      expect(await fits(page)).toBe(true)
    })
  }

  test('390 px: estrelas de 44 px, legenda perto da estrela e sem "Alertar: on/off"', async ({ page }) => {
    await page.setViewportSize(PHONE)
    const { patches } = await mockFavorites(page)
    await page.goto('/favorites')
    const card = page.getByTestId('favorite-107-mobile')
    await expect(card).toBeVisible()
    await expectNoAlertar(page)
    const stars = card.locator('.fav-mobile-stars button')
    await expect(stars).toHaveCount(3)
    for (let i = 0; i < 3; i += 1) {
      const box = (await stars.nth(i).boundingBox())!
      expect(box.width).toBeGreaterThanOrEqual(44)
      expect(box.height).toBeGreaterThanOrEqual(44)
    }
    await expect(stars.nth(0)).toHaveAttribute('aria-label', '1 estrela')
    const legend = page.getByTestId('fav-monitor-legend-card-107')
    await expect(legend).toHaveText('Fora do Monitor')
    await stars.nth(0).click()
    await expect.poll(() => patches).toEqual([{ id: '107', body: { tier: 3 } }])
    await expect(legend).toHaveText('No Monitor · alerta ligado')
    const legendBox = (await legend.boundingBox())!
    const starBox = (await stars.nth(0).boundingBox())!
    expect(Math.abs(legendBox.y - starBox.y), 'legenda a menos de 80 px da estrela').toBeLessThan(80)
    expect(await fits(page)).toBe(true)
  })

  test('vitrine do catálogo: faixa nova (só Combo), sem legenda, sem ajuda e sem "Alertar"', async ({ page }) => {
    await page.setViewportSize(DESKTOP)
    await mockFavorites(page, favorites(true))
    await page.goto('/favorites')
    const banner = page.getByTestId('favorites-catalog-banner')
    await expect(banner).toHaveAttribute('role', 'status')
    await expect(banner).toHaveText(
      'Estas estratégias são o catálogo do Cripto Farol e não mandam alerta. Os alertas do Telegram vêm das estratégias que você acompanha no Monitor: salve um resultado do Combo nos Favoritos e dê pelo menos 1 estrela aqui.',
    )
    await expect(banner).not.toContainText('Descoberta')
    await expect(banner).not.toContainText('lote')
    await expectNoAlertar(page)
    await expect(page.locator('[data-testid^="fav-monitor-legend-"]')).toHaveCount(0)
    await expect(page.getByTestId('fav-monitor-help')).toHaveCount(0)
    await expect(page.getByTestId('fav-star-status')).toHaveText('')
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
  test('modal com identidade e a nota nova, foco preso, Esc em qualquer foco, duplicata e sucesso com "Ver em Favoritos"', async ({ page }) => {
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
      'O favorito entra sem estrela, só em Favoritos. Dê pelo menos 1 estrela lá para acompanhar no Monitor e receber os sinais no Telegram; o alerta já vem ligado e você desliga no Monitor.',
    )
    await expect(dialog).not.toContainText('Alertar')
    await expect(dialog).not.toContainText('No portfólio')
    for (let i = 0; i < 12; i += 1) {
      await page.keyboard.press('Tab')
      expect(await dialog.evaluate((el) => el.contains(document.activeElement))).toBe(true)
    }
    for (let i = 0; i < 3; i += 1) {
      await page.keyboard.press('Shift+Tab')
      expect(await dialog.evaluate((el) => el.contains(document.activeElement))).toBe(true)
    }
    await page.evaluate(() => (document.activeElement as HTMLElement | null)?.blur())
    await page.keyboard.press('Escape')
    await expect(dialog).toHaveCount(0)
    await expect(save).toBeFocused()

    await save.click()
    await dialog.getByRole('button', { name: 'Salvar', exact: true }).click()
    await expect(dialog.getByTestId('favorite-duplicate')).toHaveText(
      'Já está nos favoritos com esta configuração (fonte, sessão e ajuste). Nada foi salvo.',
    )
    await expect(dialog.getByTestId('favorite-duplicate')).toHaveAttribute('role', 'alert')
    expect(posts[0].parameters.data_source).toBe('binance_equity')
    expect(posts[0].metrics.analysis_asset.asset_class).toBe('stock')
    await page.keyboard.press('Escape')
    await expect(save).toBeFocused()

    status.current = 200
    await save.click()
    await dialog.getByRole('button', { name: 'Salvar', exact: true }).click()
    const link = dialog.getByTestId('favorite-saved-link')
    await expect(link).toBeFocused()
    await expect(link).toHaveText('Ver em Favoritos')
    expect((await link.boundingBox())!.height).toBeGreaterThanOrEqual(44)
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
    page.getByText(
      'Receba DMs individuais quando mudar a leitura de uma estratégia sua que está no Monitor (cripto, ação ou ETF), com ou sem o ativo na carteira. Desligue por estratégia no Monitor. Mercado fechado e feriado aparecem só no Monitor.',
    ),
  ).toBeVisible()
  await expect(page.getByText(/Alertar/)).toHaveCount(0)
})

// ---------------------------------------------------------------- contra o protótipo do #1122 (8.12)

const PROTO_1122 = '/prototypes/card-1122-favoritos-alertas-acoes-etfs'

type Box = { x: number; y: number; width: number; height: number }

const boxOf = async (page: Page, selector: string): Promise<Box> => {
  const box = await page.locator(selector).first().boundingBox()
  expect(box, `caixa de ${selector}`).not.toBeNull()
  return box!
}

/** Os sete favoritos de `favorites.html` (d2), na ordem do protótipo. */
function prototypeFavorites() {
  const daily = (first: string) => ({
    precision_requested: 'intrabar',
    precision_effective: 'candle',
    intraday_reason: 'coverage',
    intraday_missing: [{ from: first.slice(0, 10), to: '2026-01-01' }],
    timeframe: '1d',
    window: { covered: { start: first, end: '2026-10-23T04:00:00Z' } },
  })
  const intrabar = (timeframe: string) => ({
    precision_requested: 'intrabar',
    precision_effective: 'intrabar_15m',
    timeframe,
    window: { covered: { start: '2017-08-17T00:00:00Z', end: '2026-10-24T00:00:00Z' } },
  })
  const conventions = (feeConfirmed: boolean) => ({
    fee_confirmed: feeConfirmed,
    fraction: { simulated: true },
    adjusted_prices: true,
    calendar: { sessions_per_year: 252 },
  })
  const batch = { batch_id: '7f3c2a91-0000-4000-8000-000000000001' }
  const row = (id: number, symbol: string, cls: string, currency: string, extra: Record<string, unknown>) => ({
    ...favBase,
    id,
    symbol,
    timeframe: '1d',
    strategy_description: 'Cruzamento de médias a favor da tendência, com stop de 5%.',
    asset: { symbol, asset_class: cls, currency },
    ...extra,
  })
  return [
    row(104, 'NVDA', 'stock', 'USD', {
      name: 'multi_ma_crossover - NVDA 1d (batch)',
      tier: 2,
      notify_telegram: true,
      configuration: BINANCE,
      notes: 'gerado em lote (7f3c2a91)',
      metrics: { total_return: 12.845, total_trades: 29, sharpe_ratio: 1.67, win_rate: 0.52, max_drawdown: 0.31, avg_atr: 4.87, analysis_last_session: '2026-10-23', ...batch, execution: daily('2014-11-11T05:00:00Z'), conventions: conventions(false) },
    }),
    row(106, 'NVDA', 'stock', 'USD', {
      name: 'NVDA antigo',
      tier: 1,
      notify_telegram: true,
      configuration: STOOQ,
      parameters: { direction: 'long', stop_loss: 0.05, data_source: 'stooq' },
      metrics: { total_return: 9.402, total_trades: 31, sharpe_ratio: 1.38, win_rate: 0.5, max_drawdown: 0.34, avg_atr: 4.51, analysis_last_session: '2026-10-23', execution: { precision_requested: 'candle', precision_effective: 'candle', timeframe: '1d', window: { covered: { start: '2010-01-04T05:00:00Z', end: '2026-10-23T04:00:00Z' } } } },
    }),
    row(108, 'AAPL', 'stock', 'USD', {
      name: 'Descoberta AAPL',
      tier: null,
      notify_telegram: true,
      configuration: BINANCE,
      metrics: { total_return: 3.21, total_trades: 27, sharpe_ratio: 1.02, win_rate: 0.51, max_drawdown: 0.27, avg_atr: 3.9, analysis_last_session: '2026-10-23', execution: daily('2014-11-11T05:00:00Z'), conventions: conventions(false) },
    }),
    row(101, 'BTC/USDT', 'crypto', 'USDT', {
      name: 'BTC Trend',
      tier: 3,
      notify_telegram: true,
      configuration: CRYPTO,
      metrics: { total_return: 4.126, total_trades: 38, sharpe_ratio: 1.42, win_rate: 0.5, max_drawdown: 0.25, avg_atr: 1834.2, execution: intrabar('1d') },
    }),
    row(107, 'QQQ', 'etf', 'USD', {
      name: 'multi_ma_crossover - QQQ 1d (batch)',
      tier: null,
      notify_telegram: true,
      configuration: BINANCE,
      notes: 'gerado em lote (b41d7e20)',
      created_at: '2026-10-27T21:40:00Z',
      metrics: { total_return: 1.904, total_trades: 25, sharpe_ratio: 0.95, win_rate: 0.52, max_drawdown: 0.22, avg_atr: 7.8, analysis_last_session: '2026-10-23', batch_id: 'b41d7e20-0000-4000-8000-000000000002', execution: daily('2015-01-02T05:00:00Z'), conventions: conventions(true) },
    }),
    row(102, 'ETH/USDT', 'crypto', 'USDT', {
      name: 'ETH Ritmo',
      tier: 2,
      timeframe: '4h',
      notify_telegram: false,
      configuration: CRYPTO,
      strategy_name: 'macd_crossover',
      strategy_display_name: 'MACD: Mudança de Ritmo',
      strategy_description: 'Entrada quando o MACD cruza a linha de sinal com histograma positivo.',
      metrics: { total_return: 2.683, total_trades: 41, sharpe_ratio: 1.11, win_rate: 0.48, max_drawdown: 0.3, avg_atr: 120.5, execution: intrabar('4h') },
    }),
    row(105, 'SPY', 'etf', 'USD', {
      name: 'multi_ma_crossover - SPY 1d (batch)',
      tier: 1,
      notify_telegram: true,
      configuration: BINANCE,
      notes: 'gerado em lote (7f3c2a91)',
      metrics: { total_return: 0.612, total_trades: 22, sharpe_ratio: 0.74, win_rate: 0.55, max_drawdown: 0.2, avg_atr: 3.12, analysis_last_session: '2026-10-23', ...batch, execution: daily('2015-01-02T05:00:00Z'), conventions: conventions(true) },
    }),
  ]
}

const headerColumns = (page: Page) =>
  page.locator('table.fav-strategies thead th').evaluateAll((els) =>
    els.map((el) => ({
      key: `${el.className.split(' ')[0]}:${(el.textContent || '').trim()}`,
      shown: getComputedStyle(el).display !== 'none',
      w: Math.round(el.getBoundingClientRect().width),
    })),
  )

async function pages(browser: Browser, viewport: { width: number; height: number }) {
  const protoPage = await (await browser.newContext({ viewport })).newPage()
  const productPage = await (await browser.newContext({ viewport })).newPage()
  return { protoPage, productPage }
}

for (const viewport of [
  { width: 1440, height: 900 },
  { width: 1280, height: 800 },
  { width: 1024, height: 768 },
]) {
  test(`Favoritos a ${viewport.width} px: mesa sem "Alertar", colunas, linhas e legenda como no protótipo do #1122`, async ({ browser }, testInfo) => {
    const { protoPage, productPage } = await pages(browser, viewport)
    await productPage.clock.setFixedTime(new Date('2026-10-24T21:40:00Z'))
    // o protótipo mostra a visão do admin (coluna "Sel" da comparação), dono dos sete favoritos
    await mockFavorites(productPage, prototypeFavorites(), { ...USER, isAdmin: true })
    await protoPage.goto(`${PROTO_1122}/favorites.html`)
    await productPage.goto('/favorites')
    await expect(productPage.getByTestId('favorite-104')).toBeVisible()
    const log: Array<Record<string, unknown>> = []

    const protoCols = await headerColumns(protoPage)
    const productCols = await headerColumns(productPage)
    log.push({ name: 'colunas', proto: protoCols, product: productCols })
    expect(productCols.map((c) => `${c.key}:${c.shown}`)).toEqual(protoCols.map((c) => `${c.key}:${c.shown}`))
    expect(productCols.some((c) => c.key.includes('Alertar'))).toBe(false)
    for (let i = 0; i < protoCols.length; i += 1) {
      expect.soft(Math.abs(productCols[i].w - protoCols[i].w), `coluna ${protoCols[i].key}: ${protoCols[i].w} x ${productCols[i].w}`).toBeLessThanOrEqual(4)
    }

    const protoTable = await boxOf(protoPage, 'table.fav-strategies')
    const productTable = await boxOf(productPage, 'table.fav-strategies')
    log.push({ name: 'mesa', proto: protoTable, product: productTable })
    expect.soft(Math.abs(productTable.width - protoTable.width), `mesa: largura ${protoTable.width} x ${productTable.width}`).toBeLessThanOrEqual(4)
    expect.soft(Math.abs(productTable.x - protoTable.x), `mesa: x ${protoTable.x} x ${productTable.x}`).toBeLessThanOrEqual(4)

    const order = (page: Page) =>
      page.locator('table.fav-strategies tbody tr[data-favorite-id]').evaluateAll((els) => els.map((el) => el.getAttribute('data-favorite-id')))
    expect(await order(productPage)).toEqual(await order(protoPage))
    // Altura da linha sem os textos que o produto escreve diferente do protótipo de propósito (o status
    // da atualização quebra em vez de cortar a 1024 px; a precisão da fonte antiga é "Deep Backtest
    // desligado" no produto).
    const rowHeight = (page: Page, sel: string, skip: string[]) =>
      page.locator(sel).evaluate((row, skipped) => {
        const full = row.getBoundingClientRect().height
        const rest = skipped.reduce((h, q) => h - (row.querySelector(q)?.getBoundingClientRect().height ?? 0), full)
        return { full, rest }
      }, skip)
    for (const id of [104, 106, 108, 101, 107, 102, 105]) {
      const sel = `table.fav-strategies tbody tr[data-favorite-id="${id}"]`
      const skip = [
        // o status da atualização: o produto escreve "· último pregão 23/10" e quebra em vez de cortar
        '.fav-refresh-status',
        ...(id === 106 ? ['[data-testid="fav-precision"]'] : []),
      ]
      const a = await rowHeight(protoPage, sel, skip)
      const b = await rowHeight(productPage, sel, skip)
      log.push({ name: `linha ${id}`, proto: a, product: b, skip })
      expect.soft(Math.abs(b.rest - a.rest), `altura da linha ${id} (sem ${skip.join(', ') || 'nada'}): ${a.rest} x ${b.rest}`).toBeLessThanOrEqual(6)
      // legenda "No Monitor"/"Fora do Monitor" sob as estrelas, com o mesmo texto e a mesma caixa
      const la = await boxOf(protoPage, `${sel} .stars-cell .m22-legend`)
      const lb = await boxOf(productPage, `${sel} .stars-cell .fav-monitor-legend`)
      log.push({ name: `legenda ${id}`, proto: la, product: lb })
      expect(norm(await productPage.locator(`${sel} .stars-cell .fav-monitor-legend`).textContent())).toBe(
        norm(await protoPage.locator(`${sel} .stars-cell .m22-legend`).textContent()),
      )
      const rowA = await boxOf(protoPage, `${sel} .stars-cell [aria-label="Prioridade por estrelas"]`)
      const rowB = await boxOf(productPage, `${sel} .stars-cell [aria-label="Prioridade por estrelas"]`)
      expect.soft(Math.abs((lb.y - rowB.y) - (la.y - rowA.y)), `legenda ${id}: y sob as estrelas ${la.y - rowA.y} x ${lb.y - rowB.y}`).toBeLessThanOrEqual(4)
      expect.soft(Math.abs(lb.height - la.height), `legenda ${id}: altura ${la.height} x ${lb.height}`).toBeLessThanOrEqual(3)
    }
    for (const p of [protoPage, productPage]) {
      expect(await fits(p)).toBe(true)
    }
    await testInfo.attach(`comparacao-favoritos-1122-${viewport.width}.json`, { body: JSON.stringify(log, null, 2), contentType: 'application/json' })
  })
}

const norm = (value: string | null) => (value || '').replace(/\s+/g, ' ').trim()

/**
 * Monitor contra `index.html` (d2) em "Todos": a mesa, a célula de ações com o interruptor (mesma
 * largura por coluna; coluna única abaixo de 1600 px e 2 × 2 a partir de 1600 px) e o interruptor.
 */
function prototypeMonitorRows(): Opp[] {
  const rows = opportunities()
  const nvda = rows.find((r) => r.id === 21)!
  const legacy = rows.find((r) => r.id === 23)!
  return [
    rows[0],
    { ...rows[0], id: 2, symbol: 'SOL/USDT', name: 'SOL', tier: 1 },
    { ...nvda },
    rows.find((r) => r.id === 22)!,
    {
      ...rows[0],
      id: 3,
      symbol: 'ETH/USDT',
      name: 'ETH',
      timeframe: '4h',
      tier: 2,
      status: 'EXIT',
      is_holding: false,
      notify_telegram: false,
      template_name: 'macd_crossover',
      strategy_display_name: 'MACD: Mudança de Ritmo',
    },
    { ...legacy, notify_telegram: true },
  ]
}

for (const viewport of [
  { width: 1440, height: 900 },
  { width: 1280, height: 800 },
  { width: 1024, height: 768 },
  { width: 1600, height: 900 },
  { width: 1920, height: 1000 },
]) {
  test(`Monitor a ${viewport.width} px: mesa, célula de ações e interruptor como no protótipo do #1122`, async ({ browser }, testInfo) => {
    const { protoPage, productPage } = await pages(browser, viewport)
    await mockMonitor(productPage, prototypeMonitorRows(), { user: ADMIN })
    await protoPage.goto(`${PROTO_1122}/index.html`)
    await productPage.goto('/monitor')
    for (const p of [protoPage, productPage]) {
      await p.locator('[data-testid="monitor-filter-all"]').first().click()
    }
    await expect(productPage.getByTestId('monitor-row-nvda')).toBeVisible()
    const log: Array<Record<string, unknown>> = []
    const protoRoot = '[data-m22-view="own"] '
    const tableA = await boxOf(protoPage, `${protoRoot}table.signals`)
    const tableB = await boxOf(productPage, 'table.signals')
    const monitorColumns = (page: Page, root: string) =>
      page.locator(`${root}table.signals`).first().locator('thead th').evaluateAll((els) =>
        els.map((el) => `${(el.textContent || '').trim() || el.className}:${Math.round(el.getBoundingClientRect().width)}`),
      )
    log.push({
      name: 'mesa',
      proto: { ...tableA, columns: await monitorColumns(protoPage, protoRoot) },
      product: { ...tableB, columns: await monitorColumns(productPage, '') },
    })
    // A mesa acompanha o conteúdo de amostra (preços e nomes diferem do protótipo em poucos px por
    // coluna); a célula de ações, que o interruptor e o ajuste de Alan mudam, fica com ±6 px abaixo.
    expect.soft(Math.abs(tableB.width - tableA.width), `mesa: largura ${tableA.width} x ${tableB.width}`).toBeLessThanOrEqual(12)
    const shape = (page: Page, sel: string) =>
      page.locator(sel).first().evaluate((cell) => {
        const kids = Array.from(cell.querySelectorAll('.row-actions > *')).filter((el) => (el as HTMLElement).offsetParent !== null)
        const boxes = kids.map((el) => el.getBoundingClientRect())
        return {
          columns: new Set(boxes.map((b) => Math.round(b.x))).size,
          widths: boxes.map((b) => Math.round(b.width)),
          heights: boxes.map((b) => Math.round(b.height)),
          cell: Math.round(cell.getBoundingClientRect().width),
        }
      })
    const sa = await shape(protoPage, `${protoRoot}tr[data-testid="monitor-row-btc-usdt"] td.actions-cell`)
    const sb = await shape(productPage, 'tr[data-testid="monitor-row-btc-usdt"] td.actions-cell')
    log.push({ name: 'ações BTC/USDT', proto: sa, product: sb })
    expect(sb.columns, `colunas da célula de ações: ${sa.columns} x ${sb.columns}`).toBe(sa.columns)
    expect.soft(Math.abs(sb.cell - sa.cell), `célula de ações: ${sa.cell} x ${sb.cell}`).toBeLessThanOrEqual(6)
    for (let i = 0; i < Math.min(sa.heights.length, sb.heights.length); i += 1) {
      expect.soft(Math.abs(sb.heights[i] - sa.heights[i]), `altura do botão ${i}`).toBeLessThanOrEqual(2)
    }
    const visibleSwitch = async (page: Page, root: string) => {
      const all = page.locator(`${root}tr[data-testid="monitor-row-nvda"] [role="switch"]`)
      const n = await all.count()
      for (let i = 0; i < n; i += 1) if (await all.nth(i).isVisible()) return all.nth(i)
      throw new Error('nenhum interruptor visível')
    }
    const swA = await visibleSwitch(protoPage, protoRoot)
    const swB = await visibleSwitch(productPage, '')
    const ba = (await swA.boundingBox())!
    const bb = (await swB.boundingBox())!
    log.push({ name: 'interruptor NVDA', proto: ba, product: bb })
    expect(await swB.getAttribute('aria-label')).toBe(await swA.getAttribute('aria-label'))
    expect(norm(await swB.textContent())).toBe(norm(await swA.textContent()))
    expect.soft(Math.abs(bb.height - ba.height), `interruptor: altura ${ba.height} x ${bb.height}`).toBeLessThanOrEqual(2)
    expect.soft(Math.abs(bb.width - ba.width), `interruptor: largura ${ba.width} x ${bb.width}`).toBeLessThanOrEqual(6)
    for (const p of [protoPage, productPage]) {
      expect(await fits(p)).toBe(true)
    }
    await testInfo.attach(`comparacao-monitor-1122-${viewport.width}.json`, { body: JSON.stringify(log, null, 2), contentType: 'application/json' })
  })
}
