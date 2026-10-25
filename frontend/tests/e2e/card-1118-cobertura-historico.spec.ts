import { expect, test, type Page } from '@playwright/test'
import { EQUITY_NOTE, mockAssetCatalog, type CatalogMock } from './helpers/assetCatalogMock'
import { coverageCatalog } from './helpers/history1118'

/**
 * Card #1118 (6.4): cobertura do histórico no seletor de ativos (Descoberta, Combo e Otimização) e estado
 * da amostra no Decidir, a 1440 e 390 px, com a API simulada. O protótipo aprovado é a spec de layout:
 * frontend/public/prototypes/card-1118-historico-binance/ (dados do protótipo = amostra).
 */

const ADMIN_USER = {
  id: 'discovery-admin-1118',
  email: 'alan@example.com',
  name: 'Alan Silva',
  isAdmin: true,
  mustChangePassword: false,
}

const TEMPLATES = [
  { name: 'multi_ma_crossover', display_name: 'Médias: tendência', description: 'x', is_readonly: true },
  { name: 'ema_rsi', display_name: 'EMA + RSI', description: 'x', is_readonly: true },
]

// Os horários de atualização usam o fuso do navegador: Brasília, como no protótipo aprovado.
test.use({ timezoneId: 'America/Sao_Paulo', locale: 'pt-BR' })

const pageErrors = new WeakMap<Page, string[]>()
test.beforeEach(({ page }) => {
  const errors: string[] = []
  pageErrors.set(page, errors)
  page.on('pageerror', (error) => errors.push(error.message))
})
test.afterEach(({ page }) => {
  expect(pageErrors.get(page) ?? [], 'sem erro de página não tratado').toEqual([])
})

const json = (body: unknown, status = 200) => ({ status, contentType: 'application/json', body: JSON.stringify(body) })

// --- Mocks -------------------------------------------------------------------------------------------

async function baseMocks(page: Page): Promise<CatalogMock> {
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
  await page.route('**/api/combos/templates/ema_rsi/metadata', (route) =>
    route.fulfill(json({ indicators: [{ type: 'ema', alias: 'ema', params: { length: 21 } }] })),
  )
  return mockAssetCatalog(page, { assets: coverageCatalog() })
}

/** Qualquer pedido à consulta de histórico ou ao gráfico é registrado: o seletor nunca deve fazê-lo. */
async function watchCollection(page: Page): Promise<string[]> {
  const calls: string[] = []
  await page.route('**/api/market/history**', (route) => {
    calls.push(route.request().url())
    return route.fulfill(json({}))
  })
  await page.route('**/api/market/candles**', (route) => {
    calls.push(route.request().url())
    return route.fulfill(json({}))
  })
  return calls
}

async function discoveryMocks(page: Page) {
  const mock = await baseMocks(page)
  const preflight: Array<{ symbols: string[] }> = []
  await page.route('**/api/combos/discovery/sweeps/active', (route) => route.fulfill(json({ sweeps: [] })))
  await page.route('**/api/combos/discovery/sweeps/history', (route) => route.fulfill(json({ sweeps: [] })))
  await page.route('**/api/combos/discovery/sweeps/preflight', async (route) => {
    const body = JSON.parse(route.request().postData() || '{}')
    preflight.push(body)
    const symbols: string[] = body.symbols ?? []
    const bySymbol = new Map(mock.assets.map((a) => [a.symbol, a]))
    const crypto = symbols.filter((s) => bySymbol.get(s)?.asset_class === 'crypto' && bySymbol.get(s)?.state === 'tradable')
    const per = (body.templates?.length ?? 1) * (body.timeframes?.length ?? 1) * (body.directions?.length ?? 1)
    await route.fulfill(
      json({
        axes: { templates: body.templates, symbols, timeframes: body.timeframes, directions: body.directions },
        raw_total: symbols.length * per,
        exclusions: {},
        excluded_assets: symbols
          .filter((s) => !crypto.includes(s))
          .map((s) => ({
            symbol: s,
            asset_class: bySymbol.get(s)?.asset_class,
            state: 'tradable',
            kind: 'class',
            reason: 'ação e ETF por enquanto rodam no Combo e na Otimização (1 ativo ou lote); a Descoberta vem depois',
            combinations: per,
          })),
        excluded_count: (symbols.length - crypto.length) * per,
        valid_total: crypto.length * per,
        limits: { max_total: 1000 },
        errors: crypto.length ? {} : { symbols: 'Nenhuma combinação válida: ação e ETF por enquanto rodam no Combo e na Otimização (1 ativo ou lote); a Descoberta vem depois.' },
        expires_at: '2026-10-24T00:00:00Z',
        snapshot_token: 'tok',
        snapshot_hash: 'hash1118',
        period_type: 'all',
      }),
    )
  })
  return { mock, preflight }
}

const search = async (page: Page, text: string) => {
  await page.getByTestId('asset-search').fill(text)
  await expect(page.getByTestId('asset-results')).toBeVisible()
}
const row = (page: Page, symbol: string) => page.locator(`.ap-row[data-asset="${symbol}"]`)
const hist = (page: Page, symbol: string) => row(page, symbol).locator('.ap-fact.hist')
const covButton = (page: Page, symbol: string) => row(page, symbol).getByRole('button', { name: /^Cobertura/ })
const covPanel = (page: Page, symbol: string) => page.getByTestId(`asset-coverage-${symbol}`)
const noHorizontalScroll = (page: Page) =>
  page.evaluate(() => document.documentElement.scrollWidth <= document.documentElement.clientWidth)

const VIEWPORTS = [
  { name: '1440', width: 1440, height: 900 },
  { name: '390', width: 390, height: 844 },
] as const

// --- Fato de histórico em cada estado ------------------------------------------------------------------

for (const viewport of VIEWPORTS) {
  test.describe(`fato de histórico no seletor a ${viewport.name} px`, () => {
    test.beforeEach(async ({ page }) => {
      await page.setViewportSize({ width: viewport.width, height: viewport.height })
    })

    test('cada estado diz o que há, sem "Histórico não coletado"', async ({ page }) => {
      await discoveryMocks(page)
      await page.goto('/combo/discovery')
      await expect(page.getByTestId('asset-picker')).toBeVisible()

      await search(page, 'btc')
      await expect(hist(page, 'BTC/USDT')).toHaveText(/^Histórico desde 17 ago\. 2017 · 4 timeframes · sem lacunas · atualizado 22 out\.(?: 2026)?, \d{2}:\d{2}$/)

      await search(page, 'nvda')
      await expect(hist(page, 'NVDA')).toHaveText(
        /^1d desde 11 nov\. 2014 · 5m e 15m desde 19 mai\. 2026 · sem lacunas · atualizado 22 out\.(?: 2026)?, \d{2}:\d{2}$/,
      )

      await search(page, 'spy')
      await expect(hist(page, 'SPY')).toContainText('1 lacuna')
      await expect(hist(page, 'SPY')).not.toContainText('2 lacunas')

      await search(page, 'qqq')
      await expect(hist(page, 'QQQ')).toHaveText('Coletando histórico · 1d, página 2 · pedido às 18:06')

      await search(page, 'voo')
      await expect(hist(page, 'VOO')).toHaveText(
        'Coleta falhou 22 out., 18:06 · limite de requisições da Binance · já coletado: 1d desde 05 jan. 2023',
      )
      await expect(hist(page, 'VOO')).not.toContainText('488006')

      await search(page, 'ibit')
      await expect(hist(page, 'IBIT')).toHaveText(
        /^Parcial: pedido desde 22 out\. 2021; a Binance tem desde 11 jan\. 2024 · atualizado 21 out\.(?: 2026)?, \d{2}:\d{2}$/,
      )

      await search(page, 'aapl')
      await expect(hist(page, 'AAPL')).toHaveText('Histórico sob demanda · a coleta começa quando as análises aceitarem ações')
      await expect(covButton(page, 'AAPL')).toHaveCount(0)

      await search(page, 'sol')
      await expect(hist(page, 'SOL/USDT')).toHaveText('Histórico sob demanda · coletado quando uma análise pedir')

      await search(page, 'waves')
      await expect(hist(page, 'WAVES/USDT')).toHaveText('Histórico 01 jan. 2018 – 31 mai. 2024 · sem atualização: ativo suspenso')

      await search(page, '')
      await expect(page.getByTestId('asset-picker')).not.toContainText('Histórico não coletado')
      expect(await noHorizontalScroll(page), 'sem rolagem horizontal').toBe(true)
    })

    test('linha é <div> com <label for> e o botão Cobertura fica fora do label', async ({ page }) => {
      await discoveryMocks(page)
      await page.goto('/combo/discovery')
      await search(page, 'nvda')
      const nvda = row(page, 'NVDA')
      expect(await nvda.evaluate((el) => el.tagName)).toBe('DIV')
      const label = nvda.locator('label.ap-id')
      await expect(label).toHaveAttribute('for', /.+/)
      await expect(label.locator('button')).toHaveCount(0)
      const button = covButton(page, 'NVDA')
      await expect(button).toHaveAttribute('aria-expanded', 'false')
      await expect(button).toHaveAttribute('aria-controls', /.+/)
      expect(await button.evaluate((el) => !!el.closest('label'))).toBe(false)
      const box = await button.boundingBox()
      expect(box?.height ?? 0).toBeGreaterThanOrEqual(24)
      expect(box?.width ?? 0).toBeGreaterThanOrEqual(24)
    })

    test('clicar no nome e na linha seleciona; clicar em Cobertura não marca nem desmarca', async ({ page }) => {
      await discoveryMocks(page)
      await page.goto('/combo/discovery')
      await search(page, 'nvda')
      await row(page, 'NVDA').locator('label.ap-id').click()
      await expect(row(page, 'NVDA').locator('input')).toBeChecked()
      await expect(page.getByTestId('asset-count')).toContainText('1 selecionado')
      await covButton(page, 'NVDA').click()
      await expect(row(page, 'NVDA').locator('input')).toBeChecked()
      await covButton(page, 'NVDA').click()
      await expect(row(page, 'NVDA').locator('input')).toBeChecked()
      await row(page, 'NVDA').locator('label.ap-id').click()
      await expect(row(page, 'NVDA').locator('input')).not.toBeChecked()
      await search(page, 'spy')
      await covButton(page, 'SPY').click()
      await expect(covPanel(page, 'SPY')).toBeVisible()
      await expect(row(page, 'SPY').locator('input')).not.toBeChecked()
      await expect(page.getByTestId('asset-count')).toContainText('0 selecionados')
    })
  })
}

// --- Tabela de cobertura -----------------------------------------------------------------------------------

for (const viewport of VIEWPORTS) {
  test.describe(`tabela de cobertura a ${viewport.name} px`, () => {
    test.beforeEach(async ({ page }) => {
      await page.setViewportSize({ width: viewport.width, height: viewport.height })
    })

    test('NVDA: 1d, 5m e 15m "montado do 5m" com selo derivado e a linha de fonte, sessão e ajuste', async ({ page }) => {
      await discoveryMocks(page)
      await page.goto('/combo/discovery')
      await search(page, 'nvda')
      await covButton(page, 'NVDA').click()
      const panel = covPanel(page, 'NVDA')
      await expect(panel).toBeVisible()
      await expect(covButton(page, 'NVDA')).toHaveAttribute('aria-expanded', 'true')
      await expect(panel.locator('.ap-cov-note')).toHaveText(`${EQUITY_NOTE}. Mercado fechado não conta como lacuna.`)
      await expect(panel.locator('[data-timeframe]')).toHaveCount(3)
      const fifteen = panel.locator('[data-timeframe="15m"]')
      await expect(fifteen).toContainText('montado do 5m')
      await expect(fifteen.locator('.ap-cov-derived')).toHaveText('derivado')
      await expect(panel.locator('[data-timeframe="1d"]')).toContainText('11 nov. 2014 – 22 out. 2026')
      await expect(panel.locator('[data-timeframe="1d"]')).toContainText('nativo')
      await expect(panel.locator('[data-timeframe="5m"]')).toContainText('sem lacunas')
      await expect(panel.getByText(/^Atualizado \(.+\)$/).first()).toBeVisible()
      expect(await noHorizontalScroll(page), 'sem rolagem horizontal').toBe(true)
    })

    test('SPY pelo teclado: lacuna no horário de Nova York, 15m herdada, SPY fora da seleção, Esc devolve o foco', async ({ page }) => {
      await discoveryMocks(page)
      await page.goto('/combo/discovery')
      await search(page, 'spy')
      const button = covButton(page, 'SPY')
      await button.focus()
      await page.keyboard.press('Enter')
      const panel = covPanel(page, 'SPY')
      await expect(panel).toBeVisible()
      await expect(row(page, 'SPY').locator('input')).not.toBeChecked()
      await expect(panel.locator('[data-timeframe="5m"]')).toContainText(
        '1 lacuna: 14 out. 2026, 10:05–10:40, horário de Nova York (8 candles que a Binance não tem)',
      )
      await expect(panel.locator('[data-timeframe="15m"]')).toContainText(
        'herdada do 5m: 14 out. 2026, 10:00–10:45, horário de Nova York (bloco incompleto; não soma no resumo)',
      )
      await expect(panel.locator('[data-timeframe="15m"]')).toContainText('montado do 5m')
      // A lacuna herdada não soma: a linha continua em "1 lacuna".
      await expect(hist(page, 'SPY')).toContainText('· 1 lacuna ·')

      // Esc com o foco no botão fecha e devolve o foco.
      await page.keyboard.press('Escape')
      await expect(panel).toHaveCount(0)
      await expect(button).toHaveAttribute('aria-expanded', 'false')
      await expect(button).toBeFocused()

      // Space alterna; Esc com o foco dentro da tabela também fecha e devolve o foco ao botão.
      await page.keyboard.press('Space')
      await expect(covPanel(page, 'SPY')).toBeVisible()
      await covPanel(page, 'SPY').focus()
      await page.keyboard.press('Escape')
      await expect(covPanel(page, 'SPY')).toHaveCount(0)
      await expect(button).toBeFocused()
      await expect(row(page, 'SPY').locator('input')).not.toBeChecked()
      await expect(page.getByTestId('asset-count')).toContainText('0 selecionados')
    })

    test('QQQ em coleta, VOO em falha e IBIT parcial explicam na tabela', async ({ page }) => {
      await discoveryMocks(page)
      await page.goto('/combo/discovery')
      await search(page, 'qqq')
      await covButton(page, 'QQQ').click()
      await expect(covPanel(page, 'QQQ').locator('[data-timeframe="1d"]')).toContainText('até agora: 05 jan. 2023 – 22 out. 2026')
      await expect(covPanel(page, 'QQQ').locator('[data-timeframe="1d"]')).toContainText('em coleta')
      await search(page, 'voo')
      await covButton(page, 'VOO').click()
      await expect(covPanel(page, 'VOO').locator('[data-timeframe="1d"]')).toContainText(
        'incompleto: faltam os candles antes de 05 jan. 2023; a coleta continua do ponto em que parou no próximo pedido',
      )
      await search(page, 'ibit')
      await covButton(page, 'IBIT').click()
      await expect(covPanel(page, 'IBIT').locator('[data-timeframe="1d"]')).toContainText(
        'insuficiente para o último pedido (desde 22 out. 2021): a Binance não tem candles antes de 11 jan. 2024',
      )
      expect(await noHorizontalScroll(page), 'sem rolagem horizontal').toBe(true)
    })
  })
}

test('coleta em andamento anuncia só quando o progresso muda, não a cada filtro ou página', async ({ page }) => {
  await discoveryMocks(page)
  await page.goto('/combo/discovery')
  await search(page, 'qqq')
  const live = page.getByTestId('coverage-live')
  await expect(live).toHaveText('QQQ: Coletando histórico · 1d, página 2 · pedido às 18:06')
  // Trocar filtro e voltar não reescreve o texto anunciado enquanto o progresso é o mesmo.
  const mutations = await page.evaluate(
    () =>
      new Promise<number>((resolve) => {
        const node = document.querySelector('[data-testid="coverage-live"]')!
        let count = 0
        const observer = new MutationObserver((list) => {
          count += list.length
        })
        observer.observe(node, { childList: true, characterData: true, subtree: true })
        document.querySelector<HTMLButtonElement>('.ap-class[data-cls="etf"]')!.click()
        window.setTimeout(() => {
          document.querySelector<HTMLButtonElement>('.ap-class[data-cls="all"]')!.click()
          window.setTimeout(() => {
            observer.disconnect()
            resolve(count)
          }, 800)
        }, 800)
      }),
  )
  expect(mutations).toBeLessThanOrEqual(2)
})

// --- Nunca coleta por seleção ou por análise recusada -------------------------------------------------------

test('"Todos do filtro" em ETFs e Iniciar não pedem histórico nem gráfico', async ({ page }) => {
  const calls = await watchCollection(page)
  const { preflight } = await discoveryMocks(page)
  await page.goto('/combo/discovery')
  await page.getByTestId('inline-templates-search').fill('Médias')
  await page.locator('[role=group][aria-label="Templates (seleção inline)"] input[type=checkbox]').first().check()
  await page.locator('.ap-class[data-cls="etf"]').click()
  await expect(page.getByTestId('asset-select-all')).toContainText('Todos do filtro (')
  await page.getByTestId('asset-select-all').click()
  await expect(page.getByTestId('asset-confirm')).toBeVisible()
  await page.getByTestId('asset-confirm-ok').click()
  await expect(page.getByTestId('asset-count')).toContainText('ETF')
  // Só ETFs: o Preflight bloqueia e Iniciar fica desabilitado; nenhuma coleta é pedida.
  await expect(page.getByTestId('start-sweep')).toBeDisabled()
  await expect.poll(() => preflight.at(-1)?.symbols.length ?? 0).toBeGreaterThan(0)
  // Abrir a cobertura de uma linha com histórico também não coleta.
  await page.locator('.ap-cov-btn').first().click()
  expect(calls, 'nenhuma consulta de histórico ou de gráfico').toEqual([])
})

// --- Combo e Otimização -----------------------------------------------------------------------------------------

for (const viewport of VIEWPORTS) {
  for (const path of ['/combo/configure?template=ema_rsi', '/combo/optimize?template=ema_rsi']) {
    test(`cobertura em ${path.split('?')[0]} a ${viewport.name} px`, async ({ page }) => {
      await page.setViewportSize({ width: viewport.width, height: viewport.height })
      const calls = await watchCollection(page)
      await baseMocks(page)
      await page.route('**/api/favorites/exists**', (route) => route.fulfill(json({ exists: false })))
      await page.goto(path)
      await expect(page.getByTestId('asset-picker')).toBeVisible()
      await search(page, 'btc')
      await expect(hist(page, 'BTC/USDT')).toContainText('Histórico desde 17 ago. 2017 · 4 timeframes')
      await search(page, 'spy')
      await covButton(page, 'SPY').click()
      await expect(covPanel(page, 'SPY').locator('[data-timeframe="15m"]')).toContainText('herdada do 5m')
      await expect(row(page, 'SPY').locator('input')).not.toBeChecked()
      const panelBox = await covPanel(page, 'SPY').boundingBox()
      expect(panelBox).not.toBeNull()
      expect(panelBox!.x + panelBox!.width).toBeLessThanOrEqual(viewport.width + 1)
      expect(await noHorizontalScroll(page), 'sem rolagem horizontal com a tabela aberta').toBe(true)
      await search(page, 'nvda')
      await expect(hist(page, 'NVDA')).toContainText('1d desde 11 nov. 2014 · 5m e 15m desde 19 mai. 2026')
      expect(await noHorizontalScroll(page), 'sem rolagem horizontal').toBe(true)
      expect(calls).toEqual([])
    })
  }
}

// --- Decidir ---------------------------------------------------------------------------------------------------------

const SNAPSHOT = {
  axes: { templates: ['multi_ma_crossover'], symbols: ['BTC/USDT', 'ETH/USDT'], timeframes: ['1d'], directions: ['long'] },
  raw_total: 2,
  exclusions: {},
  excluded_count: 0,
  valid_total: 2,
  limits: { max_total: 1000 },
  errors: {},
  expires_at: '2026-10-24T00:00:00Z',
  snapshot_token: 'snapshot-token-1118',
  snapshot_hash: '1118abcdef1118abcdef1118abcdef1118abcdef1118abcdef1118abcdef1118',
  period_type: 'all',
  start_date: '2024-09-21',
  end_date: '2026-09-20',
}

const ACTIVE = {
  sweep_id: 'c1118',
  state: 'running',
  total: 2,
  succeeded: 2,
  failed: 0,
  skipped: 0,
  insufficient_sample: 0,
  processed: 2,
  terminal_reason: null,
  terminal_code: null,
  draft_key: 'draft-1118',
  snapshot: SNAPSHOT,
  updated_at: '2026-10-22T12:00:00Z',
}

function result(symbol: string, id: string, rank: number, sample: { state: string; retain_until: string | null }, promoted = false) {
  return {
    template_id: 'multi_ma_crossover',
    display_name: 'Médias Móveis: Cruzamento',
    description: 'Cruzamento de médias móveis.',
    timeframe: '1d',
    direction: 'long',
    parameters: { fast: 9, slow: 21 },
    cagr: 0.12,
    benchmark_cagr: 0.08,
    delta_cagr_vs_bh: 4,
    sharpe_ratio: 0.5,
    profit_factor: 1.8,
    win_rate: 0.55,
    coverage: 1,
    eligibility: 'eligible',
    eligibility_reason: null,
    dedup_state: promoted ? 'already_promoted' : 'unique',
    dedup_reference: promoted ? '77' : null,
    start_at: '2024-09-21T00:00:00Z',
    end_at: '2026-09-20T00:00:00Z',
    candle_source: 'Binance Spot',
    candle_version: '7',
    expected_candles: 730,
    observed_valid_candles: 730,
    fees_slippage: { fees: 0.001, slippage: 0.0005 },
    oos_verdict: { status: 'GO', reasons: ['GO Descoberta: treino decente e Sharpe OOS > 0.'] },
    rank,
    result_id: id,
    symbol,
    calmar_ratio: 3.1,
    max_drawdown: 0.12,
    trades_count: 43,
    provenance: {
      data_source: 'Binance Spot',
      asset_class: 'crypto',
      session: '24x7',
      adjustment: 'na',
      timeframe_origin: 'native',
      data_version: 7,
    },
    snapshot_id: `snap-${id}`,
    sample,
  }
}

async function decidirMocks(page: Page, rows: ReturnType<typeof result>[]) {
  await baseMocks(page)
  await page.route('**/api/combos/discovery/sweeps/active', (route) => route.fulfill(json({ sweeps: [ACTIVE] })))
  await page.route('**/api/combos/discovery/sweeps/history', (route) => route.fulfill(json({ sweeps: [] })))
  await page.route('**/api/combos/discovery/sweeps/c1118', (route) => route.fulfill(json(ACTIVE)))
  await page.route('**/api/combos/discovery/sweeps/preflight', (route) => route.fulfill(json(SNAPSHOT)))
  await page.route('**/api/combos/discovery/sweeps/*/partials?*', (route) => route.fulfill(json({ results: rows, total: rows.length })))
  await page.route('**/api/combos/discovery/sweeps/*/leaderboard?*', (route) =>
    route.fulfill(json({ results: rows, total: rows.length, unfiltered_total: rows.length, offset: 0, limit: 10 })),
  )
}

for (const viewport of VIEWPORTS) {
  test.describe(`Decidir a ${viewport.name} px`, () => {
    test.beforeEach(async ({ page }) => {
      await page.setViewportSize({ width: viewport.width, height: viewport.height })
    })

    test('amostra guardada: série na evidência, prazo e "favoritos guardam a amostra do último refresh"', async ({ page }) => {
      await decidirMocks(page, [
        result('BTC/USDT', 'r-btc-01', 1, { state: 'kept', retain_until: '2026-11-21T12:00:00Z' }, true),
        result('ETH/USDT', 'r-eth-02', 2, { state: 'kept', retain_until: '2026-11-21T12:00:00Z' }),
      ])
      await page.goto('/combo/discovery')
      await page.getByRole('tab', { name: 'Decidir' }).click()
      const evidence = page.getByTestId('sample-evidence')
      await expect(evidence).toHaveText('amostra guardada até 21 nov. 2026; favoritos guardam a amostra do último refresh')
      await expect(page.getByText(/730\/730 candles Binance Spot · 1d nativo · v7/)).toBeVisible()
      await expect(page.getByTestId('sample-r-btc-01')).toHaveText('amostra até 21 nov. 2026')
      await expect(page.getByTestId('sample-favorite-r-btc-01')).toHaveText('favorito: Favoritos guarda a amostra do último refresh')
      await expect(page.getByTestId('sample-favorite-r-eth-02')).toHaveCount(0)
      expect(await noHorizontalScroll(page), 'sem rolagem horizontal da página').toBe(true)
    })

    test('amostra vencida: "não reproduzível exatamente" na evidência e nos resultados, a 11 px', async ({ page }) => {
      await decidirMocks(page, [
        result('BTC/USDT', 'r-btc-01', 1, { state: 'expired', retain_until: '2026-11-21T12:00:00Z' }, true),
        result('ETH/USDT', 'r-eth-02', 2, { state: 'expired', retain_until: '2026-11-21T12:00:00Z' }),
      ])
      await page.goto('/combo/discovery')
      await page.getByRole('tab', { name: 'Decidir' }).click()
      const evidence = page.getByTestId('sample-evidence')
      await expect(evidence).toContainText('amostra expirada em 21 nov. 2026: não reproduzível exatamente')
      await expect(evidence).toContainText('favoritos guardam a amostra do último refresh')
      await expect(page.getByTestId('sample-r-btc-01')).toHaveText('não reproduzível exatamente')
      await expect(page.getByTestId('sample-r-eth-02')).toHaveText('não reproduzível exatamente')
      await expect(page.getByTestId('sample-favorite-r-btc-01')).toHaveText('favorito: Favoritos guarda a amostra do último refresh')
      for (const target of [evidence, page.getByTestId('sample-r-btc-01'), page.getByTestId('sample-r-eth-02')]) {
        expect(await target.evaluate((el) => getComputedStyle(el).fontSize)).toBe('11px')
      }
    })

    test('varredura antiga: sem amostra guardada, sem prometer reprodução', async ({ page }) => {
      await decidirMocks(page, [result('BTC/USDT', 'r-old-01', 1, { state: 'none', retain_until: null })])
      await page.goto('/combo/discovery')
      await page.getByRole('tab', { name: 'Decidir' }).click()
      await expect(page.getByTestId('sample-r-old-01')).toHaveText('sem amostra guardada')
      await expect(page.getByTestId('sample-evidence')).toContainText('sem amostra guardada')
    })
  })
}

test('cores de estado do delta vêm das variáveis do AssetPicker.css, não de literais novos', async ({ page }) => {
  await discoveryMocks(page)
  await page.goto('/combo/discovery')
  await search(page, 'ibit')
  const color = await hist(page, 'IBIT').evaluate((el) => getComputedStyle(el).color)
  expect(color).toBe('rgb(251, 191, 36)') // --ap-warn-text (#fbbf24)
  await search(page, 'qqq')
  expect(await hist(page, 'QQQ').evaluate((el) => getComputedStyle(el).color)).toBe('rgb(147, 197, 253)') // --ap-info-text
  await search(page, 'voo')
  expect(await hist(page, 'VOO').evaluate((el) => getComputedStyle(el).color)).toBe('rgb(255, 130, 148)') // --ap-danger-text
  expect(await hist(page, 'VOO').evaluate((el) => getComputedStyle(el).borderTopColor)).toBe('rgba(246, 70, 93, 0.45)')
  await search(page, 'ibit')
  expect(await hist(page, 'IBIT').evaluate((el) => getComputedStyle(el).borderTopColor)).toBe('rgba(245, 158, 11, 0.45)')
  await covButton(page, 'IBIT').click()
  expect(await covButton(page, 'IBIT').evaluate((el) => getComputedStyle(el).borderTopLeftRadius)).toBe('4px')
})
