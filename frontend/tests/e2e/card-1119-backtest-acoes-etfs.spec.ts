import { expect, test, type Page } from '@playwright/test'
import { mockAssetCatalog } from './helpers/assetCatalogMock'
import { coverageCatalog } from './helpers/history1118'

/**
 * Card #1119 (tarefa 7.5): backtest de ação e ETF com a API simulada, a 1440 e a 390 px.
 * Resultado (NVDA 1d long, SPY 1h short, BTC/USDT 4h), Combo, Otimização e a recusa do lote.
 * O protótipo aprovado (frontend/public/prototypes/card-1119-backtest-acoes-etfs/) é a spec de UI:
 * os textos abaixo são os dele.
 */

const ADMIN_USER = {
  id: 'discovery-admin',
  email: 'alan@example.com',
  name: 'Alan Silva',
  isAdmin: true,
  mustChangePassword: false,
}
const TEMPLATES = [{ name: 'ema_rsi', display_name: 'EMA + RSI', description: 'x', is_readonly: true }]
const DESKTOP = { width: 1440, height: 900 }
const PHONE = { width: 390, height: 844 }

const pageErrors = new WeakMap<Page, string[]>()
test.beforeEach(({ page }) => {
  const errors: string[] = []
  pageErrors.set(page, errors)
  page.on('pageerror', (error) => errors.push(error.message))
})
test.afterEach(({ page }) => {
  expect(pageErrors.get(page) ?? [], 'sem erro de página não tratado').toEqual([])
})

function json(body: unknown, status = 200) {
  return { status, contentType: 'application/json', body: JSON.stringify(body) }
}

const fitsHorizontally = (page: Page) =>
  page.evaluate(() => document.documentElement.scrollWidth <= document.documentElement.clientWidth)

// --------------------------------------------------------------------------- resultado

const EQUITY_CONVENTIONS = {
  fee: 0.001,
  fee_confirmed: true,
  slippage: 0.0002,
  calendar: { kind: 'nyse_regular_session', timezone: 'America/New_York', years: 'calendar_days_365', sessions_per_year: 252 },
  fraction: { simulated: true, confirms_account: false },
  short: null,
  gap_exit: { enabled: true, stops_with_gap: 1 },
  adjusted_prices: true,
}

const PROVENANCE = { adjustment: 'adjusted', version_label: '3', snapshot_id: 'snap-1', kept_until: '2026-11-22T12:00:00Z' }

function candles(startIso: string, count: number, stepMs: number, base: number) {
  const start = new Date(startIso).getTime()
  return Array.from({ length: count }, (_, i) => ({
    timestamp_utc: new Date(start + i * stepMs).toISOString(),
    open: base + i * 0.2,
    high: base + i * 0.2 + 1.5,
    low: base + i * 0.2 - 1.5,
    close: base + i * 0.2 + 0.4,
    volume: 1000,
  }))
}

const metrics = { total_trades: 2, win_rate: 0.5, total_return: 0.08, avg_profit: 0.04, sharpe_ratio: 0.9, max_drawdown: 0.05 }

function nvdaResult(overrides: Record<string, unknown> = {}) {
  return {
    template_name: 'ema_rsi',
    symbol: 'NVDA',
    timeframe: '1d',
    start_date: null,
    end_date: null,
    period_type: 'all',
    execution_mode: 'fast_1d',
    asset: { symbol: 'NVDA', asset_id: 'binance:equity:EQ_NVDA', asset_class: 'stock', name: 'NVIDIA Corporation Common Stock', currency: 'USD' },
    data_provenance: PROVENANCE,
    execution: {
      precision_requested: 'intrabar',
      precision_effective: 'candle',
      timeframe: '1d',
      intraday_missing: [{ from: '2014-11-11', to: '2026-05-18' }],
      intraday_reason: 'coverage',
      gap_stops: 1,
      window: { requested: { start: null, end: null }, covered: { start: '2014-11-11T05:00:00+00:00', end: '2026-10-22T04:00:00+00:00', candles: 2990 } },
      collection: null,
    },
    conventions: EQUITY_CONVENTIONS,
    parameters: { direction: 'long', stop_loss: 0.05 },
    metrics,
    trades: [
      { entry_time: '2026-02-02T05:00:00+00:00', entry_price: 191.3, exit_time: '2026-02-20T05:00:00+00:00', exit_price: 204.1, profit: 0.0669, type: 'long', signal_type: 'Close entry(s) order...' },
      {
        entry_time: '2026-02-23T05:00:00+00:00',
        entry_price: 191.3,
        exit_time: '2026-02-26T05:00:00+00:00',
        exit_price: 172.1,
        stop_price: 181.74,
        gap_pct: 0.053,
        profit: -0.1006,
        type: 'long',
        exit_reason: 'stop_loss_gap',
        signal_type: 'Stop com gap',
      },
    ],
    indicator_data: {},
    candles: candles('2026-02-01T05:00:00Z', 30, 86_400_000, 190),
    ...overrides,
  }
}

function spyResult() {
  return {
    template_name: 'ema_rsi',
    symbol: 'SPY',
    timeframe: '1h',
    start_date: '2026-08-01',
    end_date: '2026-10-22',
    period_type: 'custom',
    execution_mode: 'deep_15m',
    direction: 'short',
    asset: { symbol: 'SPY', asset_id: 'binance:equity:EQ_SPY', asset_class: 'etf', name: 'State Street SPDR S&P 500 ETF Trust', currency: 'USD' },
    data_provenance: PROVENANCE,
    execution: {
      precision_requested: 'intrabar',
      precision_effective: 'intrabar_15m',
      timeframe: '1h',
      intraday_missing: [],
      intraday_reason: null,
      gap_stops: 1,
      window: { requested: { start: '2026-08-01', end: '2026-10-22' }, covered: { start: '2026-08-03T13:30:00+00:00', end: '2026-10-22T19:30:00+00:00', candles: 512 } },
      collection: null,
    },
    conventions: { ...EQUITY_CONVENTIONS, slippage: 0.0003, short: { simulated: true, confirms_account: false } },
    parameters: { direction: 'short', stop_loss: 0.02 },
    metrics,
    trades: [
      {
        entry_time: '2026-08-26T14:30:00+00:00',
        entry_price: 658.8,
        exit_time: '2026-08-27T13:30:00+00:00',
        exit_price: 676.1,
        stop_price: 672.04,
        profit: -0.0275,
        type: 'short',
        exit_reason: 'stop_loss_gap',
        signal_type: 'Stop com gap',
      },
    ],
    indicator_data: {},
    candles: candles('2026-08-26T13:30:00Z', 20, 3_600_000, 660),
  }
}

function btcResult() {
  return {
    template_name: 'ema_rsi',
    symbol: 'BTC/USDT',
    timeframe: '4h',
    start_date: '2024-01-01',
    end_date: '2024-12-31',
    period_type: 'custom',
    execution_mode: 'fast_1d',
    asset: { symbol: 'BTC/USDT', asset_id: 'binance:spot:BTC/USDT', asset_class: 'crypto', name: 'BTC', currency: 'USDT' },
    data_provenance: { version_label: '12', snapshot_id: 'snap-btc' },
    execution: {
      precision_requested: 'intrabar',
      precision_effective: 'candle',
      timeframe: '4h',
      intraday_missing: [{ from: '2024-08-01', to: '2024-08-20' }],
      intraday_reason: 'coverage',
      gap_stops: 1,
      window: { requested: { start: '2024-01-01', end: '2024-12-31' }, covered: { start: '2024-01-01T00:00:00+00:00', end: '2024-12-31T20:00:00+00:00', candles: 2196 } },
    },
    conventions: { fee: 0.00075, fee_confirmed: true, slippage: 0.0002, fraction: null, short: null, gap_exit: { enabled: true, stops_with_gap: 1 }, adjusted_prices: false },
    parameters: { direction: 'long', stop_loss: 0.03 },
    metrics,
    trades: [
      { entry_time: '2024-03-01T00:00:00+00:00', entry_price: 62000, exit_time: '2024-03-08T00:00:00+00:00', exit_price: 66000, profit: 0.0627, type: 'long', signal_type: 'Close entry(s) order...' },
      {
        entry_time: '2024-03-10T00:00:00+00:00',
        entry_price: 70000,
        exit_time: '2024-03-12T04:00:00+00:00',
        exit_price: 65500,
        stop_price: 67900,
        profit: -0.0645,
        type: 'long',
        exit_reason: 'stop_loss_gap',
        signal_type: 'Stop com gap',
      },
    ],
    indicator_data: {},
    candles: candles('2024-03-01T00:00:00Z', 30, 14_400_000, 64000),
  }
}

async function openResult(page: Page, result: unknown, isOptimization = true, viewport = DESKTOP) {
  await page.setViewportSize(viewport)
  await page.addInitScript((user) => {
    localStorage.setItem('auth_access_token', 'admin-token')
    localStorage.setItem('auth_refresh_token', 'admin-refresh')
    localStorage.setItem('auth_user', JSON.stringify(user))
    localStorage.setItem('cripto-farol-onboarding-dismissed', '1')
  }, ADMIN_USER)
  await page.route('**/api/**', (route) => route.fulfill(json({})))
  await page.route('**/api/auth/me', (route) => route.fulfill(json(ADMIN_USER)))
  await page.goto('/combo/results')
  await page.evaluate(
    ({ result, isOptimization }) => {
      history.replaceState({ usr: { result, isOptimization, returnTo: '/combo/configure' }, key: 'card-1119', idx: 0 }, '', location.href)
    },
    { result, isOptimization },
  )
  await page.reload()
  await expect(page.getByTestId('result-data-execution')).toBeVisible()
}

test.describe('resultado de ação e ETF', () => {
  test('NVDA 1d a 1440 px: identidade, precisão diária com o trecho, 8 fatos, convenções e lista em USD', async ({ page }) => {
    await openResult(page, nvdaResult())
    await expect(page.getByTestId('result-asset-class')).toHaveText('Ação')
    await expect(page.getByTestId('result-provenance')).toHaveText('Binance Ações · pregão regular de Nova York · ajustado por split · USD')
    await expect(page.getByTestId('result-precision-title')).toHaveText('Precisão diária')
    await expect(page.getByTestId('result-precision')).toHaveAttribute('role', 'note')
    await expect(page.getByTestId('result-precision-text')).toContainText('O intradiário de 15m faltou de 11 nov. 2014 a 18 mai. 2026.')
    await expect(page.getByTestId('result-precision-text')).toContainText('o stop foi simulado no candle diário em toda a janela')
    // desktop: tudo aberto, sem botão e sem a linha de Avisos
    await expect(page.getByTestId('result-data-toggle')).toBeHidden()
    await expect(page.getByTestId('result-alerts')).toBeHidden()
    await expect(page.getByTestId('result-facts').locator('[data-fact]')).toHaveCount(8)
    for (const label of ['Ativo', 'Fonte e sessão', 'Ajuste e moeda', 'Tempo gráfico', 'Janela pedida', 'Janela coberta', 'Amostra', 'Precisão']) {
      await expect(page.getByTestId('result-facts')).toContainText(label)
    }
    await expect(page.locator('[data-fact="requested"]')).toContainText('Todo o histórico')
    await expect(page.locator('[data-fact="timeframe"]')).toContainText('1d nativo')
    await expect(page.locator('[data-fact="sample"]')).toContainText('Versão 3')
    await expect(page.locator('[data-fact="sample"]')).toContainText('vale o prazo de 30 dias')
    const conventions = page.getByTestId('result-conventions')
    for (const key of ['gap', 'costs', 'fraction', 'calendar', 'annualization', 'adjusted']) {
      await expect(conventions.locator(`[data-convention="${key}"]`)).toBeVisible()
    }
    await expect(conventions.locator('[data-convention="adjusted"]')).toContainText('Preços ajustados')
    await expect(conventions.locator('[data-convention="costs"]')).toContainText('Taxa de 0,1% por lado, confirmada na Binance Ações.')
    await expect(conventions.locator('[data-convention="fraction"]')).toContainText('Isso não confirma que a sua conta na Binance compra fração.')
    await expect(conventions.locator('[data-convention="annualization"]')).toContainText('Sharpe e Sortino por operação, sem anualização')
    await expect(conventions.locator('[data-convention="gap"]')).toContainText('1 saída com gap (26 fev. 2026: stop 181,74, abertura 172,10)')
    // quatro colunas de fatos a 1440 px
    const columns = await page.getByTestId('result-facts').evaluate((el) => getComputedStyle(el).gridTemplateColumns.split(' ').length)
    expect(columns).toBe(4)
    // lista: USD em todas as colunas de dinheiro, só a data no 1d, "Stop com gap" com stop e abertura
    const table = page.getByTestId('result-trades')
    await expect(table).toContainText('USD')
    await expect(table).not.toContainText('USDT')
    await expect(table).not.toContainText('EDT')
    await expect(table).not.toContainText('EST')
    await expect(table).toContainText('Stop com gap')
    await expect(table).toContainText('stop 181.74 · abriu 172.10')
    expect(await fitsHorizontally(page)).toBe(true)
  })

  test('NVDA a 390 px: recolhido com precisão e avisos; um toque abre; Enter e Espaço alternam', async ({ page }) => {
    await openResult(page, nvdaResult({ conventions: { ...EQUITY_CONVENTIONS, fee: 0.00075, fee_confirmed: false } }), true, PHONE)
    const toggle = page.getByTestId('result-data-toggle')
    await expect(toggle).toBeVisible()
    await expect(toggle).toHaveAttribute('aria-expanded', 'false')
    await expect(toggle).toContainText('Fatos e convenções desta execução')
    await expect(toggle).toContainText('8 fatos · 6 convenções')
    const box = await toggle.boundingBox()
    expect(box!.height).toBeGreaterThanOrEqual(44)
    await expect(page.getByTestId('result-precision-title')).toBeVisible()
    await expect(page.getByTestId('result-alerts')).toContainText('Avisos: 1 saída com gap · taxa assumida · posição com fração')
    await expect(page.getByTestId('result-facts')).toBeHidden()
    await expect(page.getByTestId('result-conventions')).toBeHidden()
    expect(await fitsHorizontally(page)).toBe(true)

    await toggle.click()
    await expect(toggle).toHaveAttribute('aria-expanded', 'true')
    await expect(page.getByTestId('result-facts')).toBeVisible()
    await expect(page.getByTestId('result-conventions')).toContainText('Preços ajustados')
    const columns = await page.getByTestId('result-facts').evaluate((el) => getComputedStyle(el).gridTemplateColumns.split(' ').length)
    expect(columns).toBe(1)
    expect(await fitsHorizontally(page)).toBe(true)

    await toggle.focus()
    await page.keyboard.press('Space')
    await expect(toggle).toHaveAttribute('aria-expanded', 'false')
    await expect(toggle).toBeFocused()
    await page.keyboard.press('Enter')
    await expect(toggle).toHaveAttribute('aria-expanded', 'true')
    await expect(toggle).toBeFocused()
  })

  test('a 1024 px os fatos ficam em 2 colunas', async ({ page }) => {
    await openResult(page, nvdaResult(), true, { width: 1024, height: 800 })
    const columns = await page.getByTestId('result-facts').evaluate((el) => getComputedStyle(el).gridTemplateColumns.split(' ').length)
    expect(columns).toBe(2)
    expect(await fitsHorizontally(page)).toBe(true)
  })

  test('card #1122: favoritar ação abre o modal com a identidade (a recusa do #1119 saiu)', async ({ page }) => {
    await openResult(page, nvdaResult())
    const save = page.getByTestId('save-favorite-button')
    await expect(save).toBeVisible()
    await expect(save).not.toHaveAttribute('aria-disabled', /.*/)
    await expect(page.locator('#favorite-refused-why')).toHaveCount(0)
    const box = await save.boundingBox()
    expect(box!.height).toBeGreaterThanOrEqual(44)
    await save.click()
    const dialog = page.getByRole('dialog', { name: 'Salvar nos Favoritos' })
    await expect(dialog).toBeVisible()
    await expect(dialog.getByTestId('favorite-identity')).toContainText('NVDA · Ação · USD')
    await page.keyboard.press('Escape')
    await expect(dialog).toHaveCount(0)
    await expect(save).toBeFocused()
  })

  test('coleta que parou no meio: nota âmbar "Janela coberta menor que a pedida"', async ({ page }) => {
    const base = nvdaResult()
    await openResult(page, {
      ...base,
      period_type: 'custom',
      start_date: '2014-11-11',
      end_date: '2026-10-22',
      execution: {
        ...(base.execution as object),
        window: { requested: { start: '2014-11-11', end: '2026-10-22' }, covered: { start: '2014-11-11T05:00:00+00:00', end: '2026-10-02T04:00:00+00:00', candles: 2970 } },
        collection: {
          status: 'partial',
          kind: 'tail',
          series: '1d',
          symbol: 'NVDA',
          reason: 'limite de requisições da Binance',
          stopped_after: '2026-10-02T04:00:00+00:00',
          covered: { start: '2014-11-11T05:00:00+00:00', end: '2026-10-02T04:00:00+00:00' },
          requested: { start: '2014-11-11', end: '2026-10-22' },
          left_out: [{ from: '2026-10-05', to: '2026-10-22' }],
        },
      },
    })
    const note = page.getByTestId('result-coverage')
    await expect(note).toHaveAttribute('role', 'note')
    await expect(note).toContainText('Janela coberta menor que a pedida')
    await expect(note).toContainText('A coleta do 1d de NVDA parou depois de guardar até 02 out. 2026')
    await expect(page.locator('[data-fact="covered"]')).toContainText('Coleta parou em 02 out. 2026')
  })

  test('intrabar desligado e erro de leitura: estados da faixa de precisão', async ({ page }) => {
    const base = nvdaResult()
    await openResult(page, {
      ...base,
      execution: { ...(base.execution as object), precision_requested: 'daily', intraday_reason: null, intraday_missing: [] },
    })
    await expect(page.getByTestId('result-precision-title')).toHaveText('Precisão diária, escolhida')
    await expect(page.getByTestId('result-precision')).toHaveAttribute('data-tone', 'info')
    await page.goto('/')
    await openResult(page, {
      ...base,
      execution: { ...(base.execution as object), intraday_reason: 'read_error', intraday_missing: [{ from: '2026-01-02', to: '2026-10-22' }] },
    })
    await expect(page.getByTestId('result-precision')).toHaveAttribute('data-tone', 'warn')
    await expect(page.getByTestId('result-precision-text')).toContainText('Não foi possível ler o intradiário')
  })

  test('resultado antigo sem execution não mostra o bloco', async ({ page }) => {
    await page.setViewportSize(DESKTOP)
    await page.addInitScript((user) => {
      localStorage.setItem('auth_access_token', 'admin-token')
      localStorage.setItem('auth_user', JSON.stringify(user))
      localStorage.setItem('cripto-farol-onboarding-dismissed', '1')
    }, ADMIN_USER)
    await page.route('**/api/**', (route) => route.fulfill(json({})))
    await page.goto('/combo/results')
    const { execution: _e, conventions: _c, asset: _a, data_provenance: _p, ...legacy } = btcResult() as Record<string, unknown>
    await page.evaluate((result) => {
      history.replaceState({ usr: { result, isOptimization: true }, key: 'k', idx: 0 }, '', location.href)
    }, legacy)
    await page.reload()
    await expect(page.getByTestId('result-trades')).toBeVisible()
    await expect(page.getByTestId('result-data-execution')).toHaveCount(0)
    await expect(page.getByTestId('result-asset-class')).toHaveCount(0)
    // sem classe o favorito segue vivo, como antes
    await expect(page.getByTestId('save-favorite-button')).not.toHaveAttribute('aria-disabled', 'true')
  })

  test('SPY 1h short: hora de Nova York na lista, short simulado, preços ajustados e intrabar 15m', async ({ page }) => {
    await openResult(page, spyResult())
    await expect(page.getByTestId('result-asset-class')).toHaveText('ETF')
    await expect(page.getByTestId('result-precision-title')).toHaveText('Precisão intrabar 15m')
    await expect(page.getByTestId('result-precision')).toHaveAttribute('data-tone', 'info')
    await expect(page.locator('[data-fact="timeframe"]')).toContainText('1h montado do 5m')
    await expect(page.locator('[data-convention="short"]')).toContainText('não indica que a sua conta na Binance pode vender a descoberto')
    await expect(page.locator('[data-convention="adjusted"]')).toContainText('Preços ajustados')
    await expect(page.locator('[data-convention="annualization"]')).toContainText('Sharpe e Sortino por operação, sem anualização')
    await expect(page.locator('[data-convention="gap"]')).toContainText('27 ago. 2026, abertura do pregão: stop 672,04, abertura 676,10')
    const table = page.getByTestId('result-trades')
    await expect(table).toContainText('Data e hora (Nova York)')
    await expect(table).toContainText('09:30 EDT')
    await expect(table).toContainText('10:30 EDT')
    await expect(table).toContainText('Aug 27, 2026')
    await expect(table).toContainText('stop 672.04 · abriu 676.10')
    await expect(table).not.toContainText('USDT')
    // Card #1122: ação/ETF salvam nos Favoritos (o botão não é mais recusado).
    await expect(page.getByTestId('save-favorite-button')).not.toHaveAttribute('aria-disabled', 'true')
    expect(await fitsHorizontally(page)).toBe(true)
  })

  test('SPY 1h a 390 px: cartão móvel com hora e fuso de Nova York', async ({ page }) => {
    await openResult(page, spyResult(), true, PHONE)
    const card = page.getByTestId('trade-gap-card')
    await expect(card).toContainText('Stop com gap · stop 672.04, abriu 676.10')
    await expect(page.getByTestId('result-trades')).toContainText('Horário de Nova York (EDT)')
    await expect(page.getByTestId('result-trades')).toContainText('Aug 26, 2026, 10:30 → Aug 27, 2026, 09:30')
    expect(await fitsHorizontally(page)).toBe(true)
  })

  test('BTC/USDT 4h (regressão cripto): lista em USDT, "candle de 4h", sem fração e favorito vivo', async ({ page }) => {
    await openResult(page, btcResult())
    await expect(page.getByTestId('result-asset-class')).toHaveText('Cripto')
    await expect(page.getByTestId('result-provenance')).toHaveText('Binance Spot · 24/7 · ajuste não se aplica · USDT')
    await expect(page.getByTestId('result-precision-title')).toHaveText('Precisão do candle de 4h')
    await expect(page.locator('[data-fact="precision"]')).toContainText('Candle de 4h')
    await expect(page.getByTestId('result-data-execution')).not.toContainText('diária')
    await expect(page.locator('[data-convention="fraction"]')).toHaveCount(0)
    await expect(page.locator('[data-convention="adjusted"]')).toHaveCount(0)
    const table = page.getByTestId('result-trades')
    await expect(table).toContainText('USDT')
    await expect(table).not.toContainText(/\d USD\b/)
    await expect(table).not.toContainText('EDT')
    await expect(table).toContainText('stop 67900.00 · abriu 65500.00'.replace('67900.00', '67,900.00').replace('65500.00', '65,500.00'))
    // cripto não ganha hora de Nova York
    await expect(table).not.toContainText('Nova York')
    const save = page.getByTestId('save-favorite-button')
    await expect(save).not.toHaveAttribute('aria-disabled', 'true')
    await save.click()
    await expect(page.getByRole('heading', { name: 'Salvar nos Favoritos' })).toBeVisible()
  })
})

// --------------------------------------------------------------------------- Combo e Otimização

async function selectionMocks(page: Page) {
  await page.addInitScript((user) => {
    localStorage.setItem('auth_access_token', 'admin-token')
    localStorage.setItem('auth_refresh_token', 'admin-refresh')
    localStorage.setItem('auth_user', JSON.stringify(user))
    localStorage.setItem('cripto-farol-onboarding-dismissed', '1')
  }, ADMIN_USER)
  await page.route('**/api/**', (route) => route.fulfill(json({})))
  await page.route('**/api/auth/me', (route) => route.fulfill(json(ADMIN_USER)))
  await page.route('**/api/combos/templates', (route) => route.fulfill(json({ prebuilt: TEMPLATES, examples: [], custom: [] })))
  await page.route('**/api/combos/meta/ema_rsi', (route) =>
    route.fulfill(
      json({
        name: 'ema_rsi',
        description: 'EMA + RSI',
        indicators: [{ type: 'ema', alias: 'ema', params: { length: 21 } }],
        entry_logic: 'close > ema',
        exit_logic: 'close < ema',
        stop_loss: 0.02,
        optimization_schema: { ema_length: { min: 5, max: 20, step: 1 } },
      }),
    ),
  )
  await page.route('**/api/combos/templates/ema_rsi/metadata', (route) => route.fulfill(json({ indicators: [{ type: 'ema', alias: 'ema', params: { length: 21 } }] })))
  const catalog = await mockAssetCatalog(page, { assets: coverageCatalog() })
  const posts: Array<{ url: string; body: any }> = []
  let exists = 0
  await page.route('**/api/favorites/exists**', (route) => {
    exists += 1
    return route.fulfill(json({ exists: false }))
  })
  await page.route('**/api/combos/backtest/batch', async (route) => {
    posts.push({ url: 'batch', body: JSON.parse(route.request().postData() || '{}') })
    await route.fulfill(json({ job_id: 'job-1119' }))
  })
  await page.route('**/api/combos/backtest/batch/job-1119', (route) =>
    route.fulfill(json({ job_id: 'job-1119', status: 'running', processed: 0, total: 1, succeeded: 0, failed: 0, skipped: 0, errors: [], started_at: null, elapsed_sec: 0, estimated_remaining_sec: null, current_symbol: 'BTC/USDT' })),
  )
  return { catalog, posts, existsCalls: () => exists }
}

function optimizeResponse(symbol: string, timeframe: string) {
  const base = nvdaResult()
  return {
    job_id: 'o1119',
    template_name: 'ema_rsi',
    symbol,
    timeframe,
    stages: [{ stage_num: 1, stage_name: 'Fase 1', values: [1, 2] }],
    best_parameters: { ema_length: 10 },
    best_metrics: { total_return: 0.08, win_rate: 0.5, sharpe_ratio: 0.9, total_trades: 2 },
    execution_mode: 'fast_1d',
    asset: { ...(base.asset as object), symbol },
    data_provenance: PROVENANCE,
    execution: {
      ...(base.execution as object),
      timeframe,
      intraday_missing: [{ from: '2024-01-02', to: '2024-01-31' }],
      window: { requested: { start: '2024-01-01', end: '2024-01-31' }, covered: { start: '2024-01-02T05:00:00+00:00', end: '2024-01-31T05:00:00+00:00', candles: 21 } },
    },
    conventions: EQUITY_CONVENTIONS,
    trades: [],
    metrics,
    parameters: { direction: 'long' },
    indicator_data: {},
    candles: [],
  }
}

const row = (page: Page, symbol: string) => page.locator(`.ap-row[data-asset="${symbol}"]`)
const chip = (page: Page, symbol: string) => page.locator(`.ap-chip[data-asset="${symbol}"]`)
async function pick(page: Page, symbol: string) {
  await page.getByTestId('asset-search').fill(symbol)
  await expect(page.getByTestId('asset-results')).toBeVisible()
  await row(page, symbol).locator('input').check()
}

test.describe('Combo com ação e ETF', () => {
  for (const viewport of [DESKTOP, PHONE]) {
    test(`1 ação: roda o backtest de 1 ativo, abre o resultado sem salvar e sem checar favoritos (${viewport.width} px)`, async ({ page }) => {
      await page.setViewportSize(viewport)
      const { posts, existsCalls } = await selectionMocks(page)
      let release!: () => void
      const gate = new Promise<void>((resolve) => (release = resolve))
      await page.route('**/api/combos/optimize', async (route) => {
        posts.push({ url: 'optimize', body: JSON.parse(route.request().postData() || '{}') })
        await gate
        await route.fulfill(json({ ...optimizeResponse('NVDA', '1h'), start_date: null }))
      })
      await page.goto('/combo/configure?template=ema_rsi')
      await pick(page, 'NVDA')
      await chip(page, 'BTC/USDT').getByRole('button').click()
      await expect(page.getByTestId('combo-run-copy')).toHaveText(
        '1 ação (NVDA): otimiza e abre o resultado; para acompanhar, salve nos Favoritos por lá.',
      )
      await expect(page.getByTestId('combo-market-data')).toHaveText('Binance Ações · pregão regular de Nova York · ajustado por split')
      // contraste AA da caixa Market Data (texto novo): --text-tertiary sobre o fundo da caixa
      const contrast = await page.getByTestId('combo-market-data').evaluate((el) => {
        const parse = (c: string) => (c.match(/[\d.]+/g) ?? []).slice(0, 3).map(Number)
        const lum = ([r, g, b]: number[]) => {
          const f = (v: number) => {
            const s = v / 255
            return s <= 0.03928 ? s / 12.92 : ((s + 0.055) / 1.055) ** 2.4
          }
          return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b)
        }
        let bg = el as HTMLElement | null
        let bgc = 'rgba(0, 0, 0, 0)'
        while (bg) {
          const c = getComputedStyle(bg).backgroundColor
          if (c && !/rgba\(0, 0, 0, 0\)|transparent/.test(c)) {
            bgc = c
            break
          }
          bg = bg.parentElement
        }
        if (bgc === 'rgba(0, 0, 0, 0)') bgc = 'rgb(11, 14, 17)'
        const a = lum(parse(getComputedStyle(el).color))
        const b = lum(parse(bgc))
        return (Math.max(a, b) + 0.05) / (Math.min(a, b) + 0.05)
      })
      expect(contrast).toBeGreaterThanOrEqual(4.5)
      const timeframe = page.locator('select').filter({ has: page.locator('option[value="1m"]') }).first()
      await expect(timeframe.locator('option[value="1m"]')).toBeDisabled()
      await expect(timeframe.locator('option[value="5m"]')).toBeDisabled()
      await expect(timeframe.locator('option[value="1m"]')).toHaveText('1 minute (só cripto)')
      await expect(page.getByTestId('combo-timeframe-hint')).toContainText('15m, 1h, 4h ou 1d, montados no pregão regular de Nova York')
      await expect(page.getByTestId('combo-deep-hint')).toBeVisible()
      await expect(page.getByTestId('asset-class-note')).toContainText('1 ação ou ETF sozinha abre o resultado, sem salvar.')
      await timeframe.selectOption('1h')

      await page.getByTestId('combo-run').click()
      const collecting = page.getByTestId('run-collecting')
      await expect(collecting).toHaveAttribute('role', 'status')
      await expect(collecting).toContainText('Coletando histórico de NVDA para a janela pedida (1h, montado do 5m) antes de otimizar…')
      await expect(collecting).toContainText('Na primeira execução de um ativo isso pode levar alguns segundos.')
      release()
      await expect(page).toHaveURL(/\/combo\/results/)
      expect(posts.map((p) => p.url)).toEqual(['optimize'])
      expect(posts[0].body.run_scope).toBe('single')
      expect(posts[0].body.symbol).toBe('NVDA')
      expect(existsCalls()).toBe(0)
      await expect(page.getByTestId('result-asset-class')).toHaveText('Ação')
      // Card #1122: o resultado de 1 ação oferece "Salvar nos Favoritos" (sem salvar sozinho).
      await expect(page.getByTestId('save-favorite-button')).not.toHaveAttribute('aria-disabled', 'true')
      expect(await fitsHorizontally(page)).toBe(true)
    })
  }

  test('NVDA + BTC/USDT é um lote de 2 ativos: 1m/5m seguem escolhíveis, com "(só cripto)", e o Market Data é por ativo', async ({ page }) => {
    const { posts } = await selectionMocks(page)
    await page.goto('/combo/configure?template=ema_rsi')
    await pick(page, 'NVDA')
    await expect(page.getByTestId('combo-run-copy')).toContainText('Lote de 2 ativos (1 cripto, 1 ação): otimiza cada um com esta configuração')
    const timeframe = page.locator('select').filter({ has: page.locator('option[value="1m"]') }).first()
    await expect(timeframe.locator('option[value="1m"]')).toBeEnabled()
    await expect(timeframe.locator('option[value="5m"]')).toBeEnabled()
    await expect(timeframe.locator('option[value="1m"]')).toHaveText('1 minute (só cripto)')
    await expect(page.getByTestId('combo-market-data')).toHaveText('Por ativo: CCXT (cripto) · Binance Ações (ação e ETF)')
    expect(posts).toEqual([])
  })

  test('só ações e ETFs (NVDA + SPY) em 1d é um lote de 2; em 5m nada roda e a tela explica', async ({ page }) => {
    const { posts } = await selectionMocks(page)
    await page.goto('/combo/configure?template=ema_rsi')
    await pick(page, 'NVDA')
    await pick(page, 'SPY')
    const timeframe = page.locator('select').filter({ has: page.locator('option[value="1m"]') }).first()
    await timeframe.selectOption('5m') // com a cripto na seleção o 5m é escolhível
    await chip(page, 'BTC/USDT').getByRole('button').click()
    await expect(page.getByTestId('combo-run-copy')).toContainText(
      'Nada será executado: NVDA (Ação), SPY (ETF) — ação e ETF não rodam em 5m; para incluí-los, use 15m, 1h, 4h ou 1d.',
    )
    await page.getByTestId('combo-run').click()
    const warning = page.getByTestId('run-warning')
    await expect(warning).toContainText('Ação e ETF não rodam em 5m')
    await expect(warning).toContainText('Nada foi executado. A seleção foi mantida.')
    await timeframe.selectOption('1d')
    await expect(page.getByTestId('combo-run-copy')).toContainText('Lote de 2 ativos (1 ação, 1 ETF)')
    expect(posts).toEqual([])
  })

  test('5m escolhido com a cripto, que sai: o valor fica em 5m e a tela avisa antes de rodar', async ({ page }) => {
    const { posts } = await selectionMocks(page)
    await page.goto('/combo/configure?template=ema_rsi')
    await pick(page, 'NVDA')
    const timeframe = page.locator('select').filter({ has: page.locator('option[value="1m"]') }).first()
    await timeframe.selectOption('5m')
    await chip(page, 'BTC/USDT').getByRole('button').click()
    await expect(timeframe).toHaveValue('5m')
    await expect(page.getByTestId('combo-run-copy')).toContainText('Nada será executado: NVDA (Ação) não roda em 5m. Escolha 15m, 1h, 4h ou 1d.')
    await page.getByTestId('combo-run').click()
    await expect(page.getByTestId('run-warning')).toHaveAttribute('role', 'status')
    await expect(page.getByTestId('run-warning')).toContainText('Escolha 15m, 1h, 4h ou 1d')
    expect(posts).toEqual([])
    await timeframe.selectOption('1h')
    await expect(page.getByTestId('combo-run-copy')).toContainText('1 ação (NVDA): otimiza e abre o resultado')
  })

  test('coleta sem nada guardado: alerta "Histórico de NVDA indisponível agora", sem resultado vazio', async ({ page }) => {
    await selectionMocks(page)
    await page.route('**/api/combos/optimize', (route) =>
      route.fulfill(
        json(
          {
            detail: {
              code: 'history_unavailable',
              message: 'Histórico de NVDA indisponível agora: limite de requisições da Binance. Tente de novo em alguns minutos.',
              symbol: 'NVDA',
              reason: 'limite de requisições da Binance',
              error_code: 'binance_rate_limited',
            },
          },
          422,
        ),
      ),
    )
    await page.goto('/combo/configure?template=ema_rsi')
    await pick(page, 'NVDA')
    await chip(page, 'BTC/USDT').getByRole('button').click()
    await page.getByTestId('combo-run').click()
    const warning = page.getByTestId('run-warning')
    await expect(warning).toContainText('Histórico de NVDA indisponível agora')
    await expect(warning).toContainText('Limite de requisições da Binance')
    await expect(page).toHaveURL(/\/combo\/configure/)
    await expect(page.getByTestId('run-collecting')).toHaveCount(0)
  })

  test('cripto sozinha segue como hoje: salva em favoritos e abre favoritos', async ({ page }) => {
    const { posts, existsCalls } = await selectionMocks(page)
    await page.route('**/api/combos/optimize', async (route) => {
      posts.push({ url: 'optimize', body: JSON.parse(route.request().postData() || '{}') })
      await route.fulfill(json({ ...optimizeResponse('BTC/USDT', '1d'), execution: undefined }))
    })
    await page.goto('/combo/configure?template=ema_rsi')
    await expect(page.getByTestId('combo-run-copy')).toHaveText('1 ativo selecionado: otimiza, salva em favoritos e abre a página de favoritos.')
    await expect(page.getByTestId('combo-market-data')).toHaveText('CCXT (crypto exchange data)')
    await page.getByTestId('combo-run').click()
    await expect.poll(() => posts.length).toBe(1)
    expect(existsCalls()).toBe(1)
    expect(posts[0].body.run_scope).toBe('single')
    expect(posts[0].body.symbol).toBe('BTC/USDT')
  })
})

test.describe('Otimização com ação e ETF', () => {
  for (const viewport of [DESKTOP, PHONE]) {
    test(`1 ação em 1d: roda com run_scope single, período fixo visível e "Dados e execução" ao lado (${viewport.width} px)`, async ({ page }) => {
      await page.setViewportSize(viewport)
      const { posts } = await selectionMocks(page)
      await page.route('**/api/combos/optimize', async (route) => {
        posts.push({ url: 'optimize', body: JSON.parse(route.request().postData() || '{}') })
        await route.fulfill(json(optimizeResponse('NVDA', '1d')))
      })
      await page.goto('/combo/optimize?template=ema_rsi&symbol=NVDA')
      await expect(chip(page, 'NVDA')).toBeVisible()
      await expect(page.getByTestId('opt-period')).toHaveText('Período: 1 a 31 jan. 2024, fixo nesta tela.')
      const timeframe = page.locator('select').filter({ has: page.locator('option[value="1m"]') }).first()
      await timeframe.selectOption('1d')
      await expect(page.getByTestId('opt-run-copy')).toContainText('1 ação (NVDA): otimiza em 1d, de 1 a 31 jan. 2024, e mostra o resultado ao lado.')
      for (const tf of ['1m', '5m', '30m']) {
        await expect(timeframe.locator(`option[value="${tf}"]`)).toBeDisabled()
        await expect(timeframe.locator(`option[value="${tf}"]`)).toHaveText(`${tf} (só cripto)`)
      }
      await expect(page.getByTestId('opt-timeframe-hint')).toContainText('15m, 1h, 4h ou 1d no pregão regular de Nova York')
      await page.getByTestId('run-optimization').click()
      await expect(page.getByText('Optimization Complete')).toBeVisible()
      expect(posts[0].body).toMatchObject({ symbol: 'NVDA', timeframe: '1d', start_date: '2024-01-01', end_date: '2024-01-31', run_scope: 'single' })
      const block = page.getByTestId('result-data-execution')
      await expect(block).toBeVisible()
      await expect(page.getByTestId('result-provenance')).toHaveText('Binance Ações · pregão regular de Nova York · ajustado por split · USD')
      await expect(page.getByTestId('result-precision-title')).toHaveText('Precisão diária')
      await expect(page.getByTestId('result-precision-text')).toContainText('A Otimização pede precisão intrabar')
      await expect(page.getByTestId('result-precision-text')).toContainText('faltou de 02 jan. 2024 a 31 jan. 2024')
      await expect(page.locator('[data-fact="requested"]')).toContainText('Período fixo desta tela')
      // entre "Optimization Complete" e "Optimization Stages"
      const order = await page.evaluate(() => {
        const text = (s: string) => Array.from(document.querySelectorAll('h2,h3')).findIndex((h) => h.textContent?.includes(s))
        return [text('Optimization Complete'), text('Dados e execução'), text('Optimization Stages')]
      })
      expect(order[0]).toBeLessThan(order[1])
      expect(order[1]).toBeLessThan(order[2])
      if (viewport.width < 768) {
        await expect(page.getByTestId('result-data-toggle')).toHaveAttribute('aria-expanded', 'false')
      } else {
        await expect(page.getByTestId('result-data-toggle')).toBeHidden()
      }
      expect(await fitsHorizontally(page)).toBe(true)
    })
  }

  test('NVDA em 1h: o 5m começa em 19 mai. 2026 e não cobre jan. 2024; avisa antes de rodar e não roda', async ({ page }) => {
    const { posts } = await selectionMocks(page)
    await page.route('**/api/combos/optimize', async (route) => {
      posts.push({ url: 'optimize', body: JSON.parse(route.request().postData() || '{}') })
      await route.fulfill(json(optimizeResponse('NVDA', '1h')))
    })
    await page.goto('/combo/optimize?template=ema_rsi&symbol=NVDA')
    await expect(chip(page, 'NVDA')).toBeVisible()
    const timeframe = page.locator('select').filter({ has: page.locator('option[value="1m"]') }).first()
    await timeframe.selectOption('1h')
    await expect(page.getByTestId('opt-run-copy')).toContainText(
      'Nada será executado: o 5m de NVDA começa em 19 mai. 2026 e não cobre 1 a 31 jan. 2024, o período fixo desta tela. Use 1d aqui ou o Combo, que tem período.',
    )
    await page.getByTestId('run-optimization').click()
    await expect(page.getByTestId('run-warning')).toHaveAttribute('role', 'status')
    await expect(page.getByTestId('run-warning')).toContainText('NVDA não roda em 1h nesta tela')
    expect(posts).toEqual([])
    await timeframe.selectOption('1d')
    await expect(page.getByTestId('opt-run-copy')).toContainText('1 ação (NVDA): otimiza em 1d')
  })

  test('NVDA + BTC/USDT é um lote na Otimização; só ação e ETF em tempo que não serve: nada roda', async ({ page }) => {
    const { posts } = await selectionMocks(page)
    await page.goto('/combo/optimize?template=ema_rsi&timeframe=1d')
    await pick(page, 'NVDA')
    await expect(page.getByTestId('opt-run-copy')).toContainText('Lote de 2 ativos (1 cripto, 1 ação): otimiza cada um com esta configuração, no período fixo desta tela')
    const timeframe = page.locator('select').filter({ has: page.locator('option[value="1m"]') }).first()
    await expect(timeframe.locator('option[value="30m"]')).toBeEnabled()
    await timeframe.selectOption('30m')
    await chip(page, 'BTC/USDT').getByRole('button').click()
    await pick(page, 'SPY')
    await expect(page.getByTestId('opt-run-copy')).toContainText(
      'Nada será executado: NVDA (Ação), SPY (ETF) — ação e ETF não rodam em 30m; para incluí-los, use 1d aqui ou o Combo, que tem período.',
    )
    await page.getByTestId('run-optimization').click()
    await expect(page.getByTestId('run-warning')).toContainText('Ação e ETF não rodam em 30m')
    expect(posts).toEqual([])
  })

  test('cripto: o período fixo também aparece, e a Otimização de 1 par roda como hoje', async ({ page }) => {
    const { posts } = await selectionMocks(page)
    await page.route('**/api/combos/optimize', async (route) => {
      posts.push({ url: 'optimize', body: JSON.parse(route.request().postData() || '{}') })
      await route.fulfill(json({ ...optimizeResponse('BTC/USDT', '1d'), execution: undefined, asset: undefined, conventions: undefined }))
    })
    await page.goto('/combo/optimize?template=ema_rsi')
    await expect(page.getByTestId('opt-period')).toHaveText('Período: 1 a 31 jan. 2024, fixo nesta tela.')
    await expect(page.getByTestId('opt-run-copy')).toContainText('1 ativo: otimiza e mostra o resultado ao lado.')
    await page.getByTestId('run-optimization').click()
    await expect(page.getByText('Optimization Complete')).toBeVisible()
    await expect(page.getByTestId('result-data-execution')).toHaveCount(0)
  })
})
