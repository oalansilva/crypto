import { expect, test, type Page } from '@playwright/test'

/**
 * Card #1120 (tarefa 5.5): Favoritos como lista única de cripto, ação e ETF, a 1440 e a 390 px.
 * Os cinco favoritos são os do protótipo aprovado (frontend/public/prototypes/card-1120-lote-multiclasse/
 * index.html): NVDA e SPY do lote 7f3c2a91 com precisão diária, BTC/USDT do lote com intrabar, ETH/USDT
 * antigo (sem execução) e SOL/USDT em 4h.
 */

const AUTH_USER = { id: 'card-1120', email: 'alan@example.com', name: 'Alan', isAdmin: true, mustChangePassword: false }
const DESKTOP = { width: 1440, height: 900 }
const PHONE = { width: 390, height: 844 }
const LOTE = '7f3c2a91'

const pageErrors = new WeakMap<Page, string[]>()
test.beforeEach(({ page }) => {
  const errors: string[] = []
  pageErrors.set(page, errors)
  page.on('pageerror', (error) => errors.push(error.message))
})
test.afterEach(({ page }) => {
  expect(pageErrors.get(page) ?? [], 'sem erro de página não tratado').toEqual([])
})

const INTRABAR = {
  precision_requested: 'intrabar',
  precision_effective: 'intrabar_15m',
  timeframe: '1d',
  window: { covered: { start: '2017-08-17T00:00:00Z', end: '2026-10-24T00:00:00Z', candles: 3400 } },
}
const DAILY = (first: string, from: string) => ({
  precision_requested: 'intrabar',
  precision_effective: 'candle',
  intraday_reason: 'coverage',
  intraday_missing: [{ from, to: '2026-05-18' }],
  timeframe: '1d',
  window: { covered: { start: first, end: '2026-10-23T04:00:00Z', candles: 3000 } },
})
const EQUITY_CONVENTIONS = {
  fee: 0.001,
  fee_confirmed: false,
  slippage: 0.0002,
  calendar: { kind: 'nyse_regular_session', timezone: 'America/New_York', sessions_per_year: 252 },
  fraction: { simulated: true, confirms_account: false },
  gap_exit: { enabled: true, stops_with_gap: 0 },
  adjusted_prices: true,
}

const base = {
  strategy_name: 'multi_ma_crossover',
  strategy_display_name: 'Médias: tendência',
  strategy_description: 'Cruzamento de médias a favor da tendência, com stop de 5%.',
  parameters: { direction: 'long', stop_loss: 0.05 },
  notify_telegram: true,
  start_date: null,
  end_date: null,
  auto_refresh_status: 'SUCCESS',
  auto_refresh_completed_at: '2026-10-24T12:12:00Z',
}
const FAVORITES = [
  {
    ...base,
    id: 104,
    name: 'multi_ma_crossover - NVDA 1d (batch)',
    symbol: 'NVDA',
    timeframe: '1d',
    tier: null,
    notes: `gerado em lote (${LOTE})`,
    created_at: '2026-10-24T21:40:00Z',
    auto_refresh_status: null,
    asset: { symbol: 'NVDA', asset_class: 'stock', currency: 'USD', name: 'NVIDIA' },
    metrics: {
      total_return: 12.845, total_trades: 29, sharpe_ratio: 1.67, win_rate: 0.52, max_drawdown: 0.31, avg_atr: 4.871,
      batch_id: `${LOTE}-0000-4000-8000-000000000001`,
      execution: DAILY('2014-11-11T05:00:00Z', '2014-11-11'),
      conventions: EQUITY_CONVENTIONS,
    },
  },
  {
    ...base,
    id: 101,
    name: 'multi_ma_crossover - BTC/USDT 1d (batch)',
    symbol: 'BTC/USDT',
    timeframe: '1d',
    tier: 3,
    notes: `gerado em lote (${LOTE})`,
    created_at: '2026-10-24T21:41:00Z',
    asset: { symbol: 'BTC/USDT', asset_class: 'crypto', currency: 'USDT', name: 'BTC' },
    metrics: {
      total_return: 4.126, total_trades: 38, sharpe_ratio: 1.42, win_rate: 0.5, max_drawdown: 0.25, avg_atr: 1834.2,
      batch_id: `${LOTE}-0000-4000-8000-000000000001`,
      execution: INTRABAR,
      conventions: { fee: 0.00075, calendar: { kind: '24x7' } },
    },
  },
  {
    ...base,
    id: 102,
    name: 'multi_ma_crossover - ETH/USDT 1d (batch)',
    symbol: 'ETH/USDT',
    timeframe: '1d',
    tier: 2,
    notes: null,
    created_at: '2026-09-01T10:00:00Z',
    asset: { symbol: 'ETH/USDT', asset_class: 'crypto', currency: 'USDT', name: 'ETH' },
    metrics: { total_return: 2.683, total_trades: 41, sharpe_ratio: 1.11, win_rate: 0.48, max_drawdown: 0.3, avg_atr: 120.5 },
  },
  {
    ...base,
    id: 105,
    name: 'multi_ma_crossover - SPY 1d (batch)',
    symbol: 'SPY',
    timeframe: '1d',
    tier: null,
    notes: `gerado em lote (${LOTE})`,
    created_at: '2026-10-24T21:42:00Z',
    auto_refresh_status: null,
    asset: { symbol: 'SPY', asset_class: 'etf', currency: 'USD', name: 'SPDR S&P 500' },
    metrics: {
      total_return: 0.612, total_trades: 22, sharpe_ratio: 0.74, win_rate: 0.55, max_drawdown: 0.2, avg_atr: 3.12,
      batch_id: `${LOTE}-0000-4000-8000-000000000001`,
      execution: DAILY('2015-01-02T05:00:00Z', '2015-01-02'),
      conventions: { ...EQUITY_CONVENTIONS, fee_confirmed: true },
    },
  },
  {
    ...base,
    id: 103,
    name: 'multi_ma_crossover - SOL/USDT 4h (batch)',
    symbol: 'SOL/USDT',
    timeframe: '4h',
    tier: null,
    notes: null,
    created_at: '2026-09-02T10:00:00Z',
    asset: { symbol: 'SOL/USDT', asset_class: 'crypto', currency: 'USDT', name: 'SOL' },
    metrics: {
      total_return: 0.974, total_trades: 64, sharpe_ratio: 0.86, win_rate: 0.46, max_drawdown: 0.4, avg_atr: 2.2,
      execution: { ...INTRABAR, timeframe: '4h', window: { covered: { start: '2020-08-11T00:00:00Z', end: '2026-10-24T00:00:00Z', candles: 9000 } } },
      conventions: { fee: 0.00075, calendar: { kind: '24x7' } },
    },
  },
]

async function mockFavorites(page: Page) {
  await page.addInitScript((user) => {
    localStorage.setItem('auth_access_token', 'tok')
    localStorage.setItem('auth_refresh_token', 'ref')
    localStorage.setItem('auth_user', JSON.stringify(user))
    localStorage.setItem('cripto-farol-onboarding-dismissed', '1')
  }, AUTH_USER)
  const patches: Array<{ id: string; body: unknown }> = []
  await page.route('**/api/**', async (route) => {
    const url = route.request().url()
    const method = route.request().method()
    const ok = (body: unknown) => route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(body) })
    if (url.includes('/api/auth/me')) return ok(AUTH_USER)
    if (method === 'PATCH' && /\/api\/favorites\/\d+/.test(url)) {
      patches.push({ id: url.split('/').pop()!, body: JSON.parse(route.request().postData() || '{}') })
      return ok({ ...FAVORITES[1], tier: 1 })
    }
    if (/\/api\/favorites\/?(\?|$)/.test(url)) return ok(FAVORITES)
    if (url.includes('/api/opportunities')) return ok([])
    return ok({})
  })
  return { patches }
}

const fits = (page: Page) => page.evaluate(() => document.documentElement.scrollWidth <= document.documentElement.clientWidth)
const row = (page: Page, id: number) => page.getByTestId(`favorite-${id}`)
const card = (page: Page, id: number) => page.getByTestId(`favorite-${id}-mobile`)

test.describe('Favoritos: lista única', () => {
  test('cripto, ação e ETF na mesma tabela, com classe, moeda, precisão, convenções e período efetivo (1440 px)', async ({ page }) => {
    await page.setViewportSize(DESKTOP)
    await mockFavorites(page)
    await page.goto('/favorites')
    await expect(page.getByTestId('favorites-renewal-ok')).toBeVisible()
    for (const id of [104, 101, 102, 105, 103]) await expect(row(page, id)).toBeVisible()
    await expect(page.getByTestId('fav-count')).toHaveText('5 filtradas')

    // filtro Classe antes de Symbol, com contagens
    const classSelect = page.getByTestId('fav-class-filter')
    await expect(classSelect.locator('option')).toHaveText(['Todas (5)', 'Cripto (3)', 'Ações (1)', 'ETFs (1)'])
    const labels = await page.locator('.fav-filters label > span').allTextContents()
    expect(labels.slice(0, 3)).toEqual(['Classe', 'Symbol', 'Strategy'])
    // grade de 6 filtros a partir de 1100 px
    const columns = await page.locator('.fav-filters').evaluate((el) => getComputedStyle(el).gridTemplateColumns.split(' ').length)
    expect(columns).toBe(6)

    // NVDA: chip da classe e moeda (USD, nunca USDT), precisão diária com o trecho, convenções, período efetivo
    const nvda = row(page, 104)
    await expect(nvda.locator('.sym-cell .lote-cls')).toHaveText('Ação')
    await expect(nvda.locator('.sym-cell .lote-cur')).toHaveText('USD')
    await expect(nvda).not.toContainText('USDT')
    await expect(nvda.getByTestId('fav-precision')).toHaveText('Precisão diária · sem 15m de 11 nov. 2014 a 18 mai. 2026')
    await expect(nvda.getByTestId('fav-precision')).toHaveAttribute('data-tone', 'warn')
    await expect(nvda.getByTestId('fav-conventions')).toHaveText('Binance Ações · NY · split · 252/ano')
    await expect(nvda.getByTestId('fav-effective')).toHaveText('Período efetivo 11 nov. 2014 – 23 out. 2026')
    // Card #1122: o status da atualização diária substitui o "ainda não para ações e ETFs".
    await expect(nvda.getByTestId('fav-refresh-status')).toHaveText('Backtest aguardando atualização')
    await expect(nvda).not.toContainText('ainda não para ações e ETFs')
    await expect(nvda.locator('td.advanced-col').nth(3)).toHaveText('4.87 USD') // ATR na moeda
    // "Limitações e origem" atrás de um <details> fechado
    const more = nvda.getByTestId('fav-more-info')
    await expect(more.locator('summary')).toHaveText('Limitações e origem')
    expect(await more.evaluate((el) => (el as HTMLDetailsElement).open)).toBe(false)
    await expect(nvda.getByTestId('fav-conventions-full')).toBeHidden()
    await more.locator('summary').click()
    await expect(nvda.getByTestId('fav-conventions-full')).toHaveText('Convenções: Binance Ações · pregão regular de Nova York · ajustado por split · 252 pregões/ano')
    await expect(more).toContainText('Limitações: simulação com fração · taxa assumida · preços ajustados podem diferir do negociado')
    await expect(more).toContainText('Gerado em lote 7f3c2a91 · 24 out. 2026')
    // coluna Período: "Todo" + efetivo
    await expect(nvda.locator('td.period-col')).toContainText('Todo')
    await expect(nvda.locator('td.period-col .lote-eff')).toHaveText('efetivo 11 nov. 2014 – 23 out. 2026')

    // SPY: taxa confirmada, sem "taxa assumida"
    const spy = row(page, 105)
    await expect(spy.locator('.sym-cell .lote-cls')).toHaveText('ETF')
    await spy.getByTestId('fav-more-info').locator('summary').click()
    await expect(spy.getByTestId('fav-more-info')).not.toContainText('taxa assumida')

    // BTC/USDT do lote: USDT, intrabar, só "Origem"
    const btc = row(page, 101)
    await expect(btc.locator('.sym-cell .lote-cls')).toHaveText('Cripto')
    await expect(btc.locator('.sym-cell .lote-cur')).toHaveText('USDT')
    await expect(btc.getByTestId('fav-precision')).toHaveText('Precisão intrabar (15m)')
    await expect(btc.getByTestId('fav-conventions')).toHaveText('Binance Spot · 24/7 · 365 dias/ano')
    await expect(btc.getByTestId('fav-more-info').locator('summary')).toHaveText('Origem')
    await expect(btc.locator('td.advanced-col').nth(3)).toHaveText('1834.20 USDT')
    await expect(btc.getByTestId('fav-refresh-status')).toContainText('Backtest atualizado')

    // ETH/USDT antigo: diz quando os dados aparecem
    const eth = row(page, 102)
    await expect(eth.getByTestId('fav-precision')).toHaveText('Precisão e período efetivo: aparecem na próxima atualização diária')
    await expect(eth.getByTestId('fav-effective')).toHaveText('Período efetivo: na próxima atualização')
    await expect(eth.getByTestId('fav-more-info')).toHaveCount(0)

    // nome acessível: as células de símbolo e estratégia perdem o aria-label vivo
    expect(await nvda.locator('td.symbol-col').getAttribute('aria-label')).toBeNull()
    expect(await nvda.locator('td.strategy-cell').getAttribute('aria-label')).toBeNull()
    expect(await fits(page)).toBe(true)
  })

  test('card #1122: estrelas, "Alertar" e Revalidar de ação e ETF funcionam; o resumo e o filtro por estrelas contam todas as classes', async ({ page }) => {
    await page.setViewportSize(DESKTOP)
    const { patches } = await mockFavorites(page)
    await page.goto('/favorites')
    const nvda = row(page, 104)
    const stars = nvda.locator('.stars-cell button')
    await expect(stars).toHaveCount(3)
    for (let i = 0; i < 3; i += 1) await expect(stars.nth(i)).not.toHaveAttribute('aria-disabled', /.*/)
    await stars.nth(1).click()
    await expect.poll(() => patches.length).toBe(1)
    expect(patches[0]).toEqual({ id: '104', body: { tier: 2 } })
    const revalidate = nvda.getByRole('button', { name: 'Revalidar na janela recente' })
    await expect(revalidate).not.toHaveAttribute('aria-disabled', /.*/)
    await expect(page.getByTestId('fav-tier-note')).toHaveCount(0)

    // resumo e filtro com todas as classes (BTC tier 3, ETH tier 2; NVDA, SPY e SOL sem estrela)
    await expect(page.locator('.tier-card-watch .tier-card-count')).toHaveText('1')
    await expect(page.locator('.tier-card-high .tier-card-count')).toHaveText('1')
    const tierFilter = page.getByLabel('Filtro por tier')
    await expect(tierFilter.getByRole('button', { name: 'Todas 5' })).toBeVisible()
    await expect(tierFilter.getByRole('button', { name: 'Sem estrela 3' })).toBeVisible()
    await tierFilter.getByRole('button', { name: 'Sem estrela 3' }).click()
    await expect(page.getByTestId('fav-count')).toHaveText('3 filtradas')
    await expect(row(page, 104)).toBeVisible()
    await expect(row(page, 103)).toBeVisible()
  })

  test('filtro Classe, Ordenar, filtros com anel de foco e contagem e rodapé que seguem os filtros', async ({ page }) => {
    await page.setViewportSize(DESKTOP)
    await mockFavorites(page)
    await page.goto('/favorites')
    await page.getByTestId('fav-class-filter').selectOption('stock')
    await expect(page.getByTestId('fav-count')).toHaveText('1 filtradas')
    await expect(page.locator('.fav-footer')).toContainText('1 estratégias carregadas')
    await expect(row(page, 104)).toBeVisible()
    await expect(row(page, 101)).toHaveCount(0)
    await page.getByTestId('fav-class-filter').selectOption('etf')
    await expect(row(page, 105)).toBeVisible()
    await page.getByTestId('fav-class-filter').selectOption('crypto')
    await expect(page.getByTestId('fav-count')).toHaveText('3 filtradas')
    // classe + Symbol: NVDA com a classe Cripto não existe
    await page.getByLabel('Symbol').selectOption('NVDA')
    await expect(page.getByTestId('favorites-filter-empty').first()).toContainText('Nenhuma estratégia com estes filtros. Troque a classe ou limpe os filtros.')
    await page.getByLabel('Symbol').selectOption('ALL')
    await page.getByTestId('fav-class-filter').selectOption('all')
    // Ordenar vale para todas as classes juntas (Return decrescente: NVDA primeiro)
    await page.getByLabel('Ordenar').selectOption('return')
    const ids = await page.locator('table.fav-strategies tbody tr[data-favorite-id]').evaluateAll((rows) => rows.map((r) => r.getAttribute('data-favorite-id')))
    expect(ids).toEqual(['104', '101', '102', '103', '105'])
    // anel de foco do produto nos selects (o incumbente zera o outline)
    await page.getByTestId('fav-class-filter').focus()
    await page.keyboard.press('Shift+Tab')
    await page.keyboard.press('Tab')
    const outline = await page.getByTestId('fav-class-filter').evaluate((el) => getComputedStyle(el).outlineStyle)
    expect(outline).not.toBe('none')
  })

  test('?lote=<id8>: faixa com os favoritos do lote de todas as classes e "Mostrar todos" devolve o foco ao Classe', async ({ page }) => {
    await page.setViewportSize(DESKTOP)
    await mockFavorites(page)
    await page.goto(`/favorites?lote=${LOTE}`)
    const banner = page.getByTestId('fav-lote-filter')
    await expect(banner).toHaveAttribute('role', 'status')
    await expect(banner).toContainText('Mostrando só o lote 7f3c2a91 (24 out. 2026, 18:40): os favoritos gravados por ele, de todas as classes.')
    await expect(page.getByTestId('fav-count')).toHaveText('3 filtradas')
    for (const id of [104, 101, 105]) await expect(row(page, id)).toBeVisible()
    await expect(row(page, 102)).toHaveCount(0)
    const clear = banner.getByRole('button', { name: 'Mostrar todos os favoritos' })
    const box = await clear.boundingBox()
    expect(box!.height).toBeGreaterThanOrEqual(43.5)
    await clear.focus()
    await page.keyboard.press('Enter')
    await expect(banner).toHaveCount(0)
    await expect(page.getByTestId('fav-class-filter')).toBeFocused()
    await expect(page.getByTestId('fav-count')).toHaveText('5 filtradas')
    expect(new URL(page.url()).search).toBe('')
    const ring = await page.getByTestId('fav-class-filter').evaluate((el) => {
      const style = getComputedStyle(el)
      return { style: style.outlineStyle, width: parseFloat(style.outlineWidth) }
    })
    expect(ring.style).not.toBe('none')
    expect(ring.width).toBeGreaterThanOrEqual(2)
  })

  test('celular (390 px): cartões com classe, moeda, precisão e convenções, sem rolagem horizontal', async ({ page }) => {
    await page.setViewportSize(PHONE)
    await mockFavorites(page)
    await page.goto('/favorites')
    await expect(card(page, 104)).toBeVisible()
    const nvda = card(page, 104)
    await expect(nvda.locator('.lote-cardline .lote-cls')).toHaveText('Ação')
    await expect(nvda.locator('.lote-cardline .lote-cur')).toHaveText('USD')
    await expect(nvda.getByTestId('fav-precision')).toContainText('Precisão diária · sem 15m de 11 nov. 2014 a 18 mai. 2026')
    await expect(nvda.getByTestId('fav-conventions')).toHaveText('Binance Ações · NY · split · 252/ano')
    await expect(nvda.getByTestId('fav-effective')).toHaveText('Período efetivo 11 nov. 2014 – 23 out. 2026')
    await expect(nvda.getByTestId('fav-more-info').locator('summary')).toHaveText('Limitações e origem')
    // Card #1122: estrelas e Revalidar de ação/ETF ligados no cartão.
    await expect(nvda.locator('.fav-mobile-stars button[data-lote-off]')).toHaveCount(0)
    await expect(nvda.getByRole('button', { name: /Revalidar/ })).not.toHaveAttribute('aria-disabled', /.*/)
    expect(await fits(page)).toBe(true)
    // o cartão da cripto antiga diz quando os dados aparecem
    await expect(card(page, 102).getByTestId('fav-precision')).toHaveText('Precisão e período efetivo: aparecem na próxima atualização diária')
    // a classe filtra também os cartões
    await page.getByTestId('fav-class-filter').selectOption('etf')
    await expect(card(page, 105)).toBeVisible()
    await expect(card(page, 104)).toHaveCount(0)
    expect(await fits(page)).toBe(true)
  })
})
