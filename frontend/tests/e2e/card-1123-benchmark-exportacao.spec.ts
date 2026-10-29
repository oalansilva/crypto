/**
 * Card #1123 — comparação com referência escolhida e planilhas com contexto (funcional, API simulada).
 *
 * Segue o protótipo aprovado (`frontend/public/prototypes/card-1123-benchmark-exportacao/`): seção
 * "Comparação com referência" em `/combo/results` (rodada nova e análise do favorito), seletor modal,
 * "Ref." e exportação em `/favorites`, "Exportar planilha", faixa "Coluna extra" e coluna "Contra <ativo>"
 * no Decidir. A 1440 px e a 390 px (toque). Os números vêm do servidor simulado; nada é calculado no navegador.
 */
import { expect, test, type Page, type Route } from '@playwright/test'
import { readFileSync } from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
import * as XLSXLIB from 'xlsx'
import { covered, mockAssetCatalog, onDemand, tf, type MockAsset } from './helpers/assetCatalogMock'
import { installDiscoveryMulticlassMocks } from './helpers/discoveryMulticlassMock'

const ADMIN = { id: 'card-1123', email: 'alan@example.com', name: 'Alan', isAdmin: true, mustChangePassword: false }
const DESKTOP = { width: 1440, height: 900 }
const PHONE = { width: 390, height: 844 }
const VIEWPORTS = [
  { name: '1440', size: DESKTOP, touch: false },
  { name: '390', size: PHONE, touch: true },
] as const

const json = (body: unknown, status = 200) => ({ status, contentType: 'application/json', body: JSON.stringify(body) })
const XLSX = { status: 200, contentType: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', body: 'PK' }

// Capturas para comparar com o protótipo (só com C1123_SHOTS definido; nada muda no teste).
async function shot(page: Page, name: string) {
  const dir = process.env.C1123_SHOTS
  if (dir) await page.screenshot({ path: `${dir}/${name}.png`, fullPage: true })
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

async function login(page: Page) {
  await page.addInitScript((user) => {
    localStorage.setItem('auth_access_token', 'tok')
    localStorage.setItem('auth_refresh_token', 'ref')
    localStorage.setItem('auth_user', JSON.stringify(user))
    localStorage.setItem('cripto-farol-onboarding-dismissed', '1')
  }, ADMIN)
}

// ---------------------------------------------------------------- catálogo da referência

function asset(cls: MockAsset['asset_class'], symbol: string, name: string, history: MockAsset['history'], state: MockAsset['state'] = 'tradable', reason: string | null = null): MockAsset {
  return {
    asset_id: cls === 'crypto' ? `binance:spot:${symbol}` : `binance:equity:EQ_${symbol}`,
    asset_class: cls,
    symbol,
    name,
    state,
    state_label: state === 'removed' ? 'Removido' : 'Negociável',
    state_reason: reason,
    info_note: null,
    removed_at: state === 'removed' ? '2024-06-17T00:00:00Z' : null,
    selectable: state === 'tradable',
    analysis_available: true,
    history,
  }
}

const since = (from: string, to = '2026-10-27T00:00:00Z') => covered([tf('1d', from, to)])
const CATALOG: MockAsset[] = [
  asset('crypto', 'BTC/USDT', 'Bitcoin', since('2017-08-17T00:00:00Z')),
  asset('crypto', 'ETH/USDT', 'Ethereum', since('2017-08-17T00:00:00Z')),
  asset('crypto', 'SOL/USDT', 'Solana', since('2020-08-11T00:00:00Z')),
  asset('crypto', 'PENGU/USDT', 'Pudgy Penguins', since('2024-12-17T00:00:00Z')),
  asset('crypto', 'WAVES/USDT', 'Waves', since('2019-01-01T00:00:00Z', '2024-06-17T00:00:00Z'), 'removed', 'Saiu da lista spot da Binance em 17 jun. 2024.'),
  asset('stock', 'NVDA', 'NVIDIA Corporation Common Stock', since('2003-01-02T05:00:00Z')),
  asset('stock', 'CRCL', 'Circle Internet Group', since('2025-06-05T04:00:00Z')),
  asset('etf', 'SPY', 'State Street SPDR S&P 500 ETF Trust', since('2003-01-02T05:00:00Z')),
  asset('etf', 'QQQ', 'Invesco QQQ Trust', onDemand()),
]

// ---------------------------------------------------------------- comparações gravadas (servidor simulado)

const SPY_REF = { kind: 'catalog', symbol: 'SPY', asset_class: 'etf', currency: 'USD', name: 'SPDR', return_kind: 'price_no_dividends', long_only: true }
const QQQ_REF = { ...SPY_REF, symbol: 'QQQ', name: 'Invesco QQQ' }
const BTC_OWN = { kind: 'own', symbol: 'BTC/USDT', asset_class: 'crypto', currency: 'USDT', name: 'BTC', return_kind: 'price', long_only: true }

function comparison(over: Record<string, unknown> = {}) {
  return {
    id: 'cmp-own',
    created_at: '2026-10-27T17:30:00Z',
    trigger: 'run',
    owner: { kind: 'result' },
    reference: BTC_OWN,
    strategy: { symbol: 'BTC/USDT', return: 63.5266, cagr: 1.0031, trades_in: 9, trades_out: 0, window: { start: '2019-01-01', end: '2024-12-31' } },
    reference_result: { return: 23.606, cagr: 0.7057, first_close: { date: '2019-01-01', price: 3800 }, last_close: { date: '2024-12-31', price: 93500 } },
    common_window: { start: '2019-01-01', end: '2024-12-31', days: 2191 },
    left_out: [],
    delta: { cagr_pp: 29.74 },
    currency_note: null,
    status: 'valid',
    reason: null,
    samples: { reference: { snapshot_id: 'snap-btc', version_label: '12' } },
    ...over,
  }
}

const SPY_CMP = comparison({
  id: 'cmp-spy',
  trigger: 'choice',
  created_at: '2026-10-27T17:32:00Z',
  reference: SPY_REF,
  strategy: { symbol: 'BTC/USDT', return: 63.5266, cagr: 1.0037, trades_in: 9, trades_out: 0 },
  reference_result: { return: 1.3426, cagr: 0.1525, first_close: { date: '2019-01-02', price: 250 }, last_close: { date: '2024-12-31', price: 585 } },
  common_window: { start: '2019-01-02', end: '2024-12-31', days: 2190 },
  left_out: [{ start: '2019-01-01', end: '2019-01-01', trades: 0, note: 'no_session' }],
  delta: { cagr_pp: 85.12 },
  currency_note: 'usdt_as_usd',
  samples: { reference: { snapshot_id: 'snap-spy', version_label: '5' } },
})
const QQQ_CMP = { ...SPY_CMP, id: 'cmp-qqq', reference: QQQ_REF, collected: true, delta: { cagr_pp: 78.3 } }
const insufficient = (symbol: string, cls: string, code: string, text: string) =>
  comparison({
    id: `cmp-${symbol}`,
    trigger: 'choice',
    reference: { kind: 'catalog', symbol, asset_class: cls, currency: cls === 'crypto' ? 'USDT' : 'USD', return_kind: cls === 'crypto' ? 'price' : 'price_no_dividends' },
    status: 'insufficient',
    reason: { code, text, short: text },
    reference_result: null,
    delta: null,
    common_window: code === 'short_overlap' ? { start: '2024-12-17', end: '2024-12-31', days: 14 } : null,
    strategy: { symbol: 'BTC/USDT', return: null, cagr: null, trades_in: null, trades_out: null },
    currency_note: cls === 'crypto' ? null : 'usdt_as_usd',
  })
const CRCL_CMP = insufficient('CRCL', 'stock', 'no_overlap', 'CRCL tem histórico desde 05/06/2025, depois do fim da estratégia (31/12/2024). Não há período comum.')
const PENGU_CMP = insufficient(
  'PENGU/USDT',
  'crypto',
  'short_overlap',
  'Período comum de 14 dias: o mínimo é 30. PENGU/USDT tem histórico desde 17/12/2024 e a estratégia termina em 31/12/2024.',
)

const BTC_RESULT = {
  template_name: 'multi_ma_crossover',
  display_name: 'Médias Móveis: Tendência em Virada',
  symbol: 'BTC/USDT',
  timeframe: '1d',
  start_date: '2019-01-01',
  end_date: '2024-12-31',
  period_type: null,
  direction: 'long',
  asset: { symbol: 'BTC/USDT', asset_id: 'binance:spot:BTC/USDT', asset_class: 'crypto', name: 'BTC', currency: 'USDT' },
  execution: {
    precision_requested: 'intrabar',
    precision_effective: 'intrabar_15m',
    timeframe: '1d',
    window: { requested: { start: '2019-01-01', end: '2024-12-31' }, covered: { start: '2019-01-01T00:00:00+00:00', end: '2024-12-31T00:00:00+00:00', candles: 2192 } },
  },
  conventions: { calendar: { kind: '24x7' } },
  parameters: { direction: 'long' },
  metrics: { total_return: 63.5266, win_rate: 0.66, total_trades: 9, max_drawdown: 0.3 },
  trades: [{ entry_time: '2019-02-01T00:00:00+00:00', entry_price: 3400, exit_time: '2024-12-20T00:00:00+00:00', exit_price: 219400, profit: 63.5266, type: 'long' }],
  indicator_data: {},
  candles: [],
  benchmark_comparison: comparison(),
}

async function openResult(page: Page, result: Record<string, unknown>, state: Record<string, unknown> = { isOptimization: true, returnTo: '/combo/configure' }) {
  await login(page)
  await mockAssetCatalog(page, { assets: CATALOG })
  const posts: Array<Record<string, any>> = []
  const exports: Array<{ body: Record<string, any>; auth: string | null }> = []
  const favorites: Array<Record<string, any>> = []
  const answers: Record<string, () => { status: number; body: unknown; delay?: number }> = {}
  await page.route(/\/api\/(auth\/me|favorites|benchmark-comparisons|combos\/export-trades|market\/candles)/, async (route: Route) => {
    const url = route.request().url()
    const method = route.request().method()
    if (url.includes('/api/auth/me')) return route.fulfill(json(ADMIN))
    if (method === 'POST' && url.includes('/api/benchmark-comparisons')) {
      const body = JSON.parse(route.request().postData() || '{}')
      posts.push(body)
      const key = String(body.reference_symbol ?? 'own')
      const answer = answers[key]?.() ?? { status: 201, body: comparison({ id: 'cmp-own-2', trigger: 'choice' }) }
      if (answer.delay) await new Promise((resolve) => setTimeout(resolve, answer.delay))
      return route.fulfill(json(answer.body, answer.status))
    }
    if (method === 'POST' && url.includes('/api/combos/export-trades')) {
      exports.push({ body: JSON.parse(route.request().postData() || '{}'), auth: route.request().headers()['authorization'] ?? null })
      return route.fulfill({ ...XLSX, headers: { 'Content-Disposition': 'attachment; filename="multi_ma_crossover_BTC_USDT_1d_trades.xlsx"' } })
    }
    if (method === 'POST' && /\/api\/favorites\/?$/.test(url)) {
      favorites.push(JSON.parse(route.request().postData() || '{}'))
      return route.fulfill(json({ id: 900, symbol: 'BTC/USDT' }))
    }
    return route.fulfill(json({ candles: [] }))
  })
  await page.goto('/combo/results')
  await page.evaluate(
    ({ result, state }) => {
      history.replaceState({ usr: { result, ...state }, key: 'card-1123', idx: 0 }, '', location.href)
    },
    { result, state },
  )
  await page.reload()
  return { posts, exports, favorites, answers }
}

const section = (page: Page) => page.getByTestId('benchmark-comparison')

for (const vp of VIEWPORTS) {
  test.describe(`Resultado a ${vp.name} px`, () => {
    test.use({ viewport: vp.size, hasTouch: vp.touch, isMobile: vp.touch })

    test('padrão do próprio ativo, seletor acessível, SPY com aviso de moeda, coleta de QQQ, insuficientes e falha', async ({ page }) => {
      const { posts, answers } = await openResult(page, BTC_RESULT)
      const block = section(page)
      await expect(block).toBeVisible()
      // Entre a análise e "Dados e execução".
      const order = await page.evaluate(() => {
        const ids = ['combo-result-summary', 'benchmark-comparison', 'result-data-execution']
        return ids.map((id) => document.querySelector(`[data-testid="${id}"]`)!.getBoundingClientRect().top)
      })
      expect(order[0]).toBeLessThan(order[1])
      expect(order[1]).toBeLessThan(order[2])
      await expect(block).toContainText('CAGR com dias corridos ÷ 365,25')
      await expect(page.getByTestId('benchmark-ref-name')).toHaveText('BTC/USDT (próprio ativo)')
      await expect(page.getByTestId('benchmark-s-ret')).toHaveText('+6352.66%')
      await expect(page.getByTestId('benchmark-delta')).toHaveText('+29.7 p.p.')
      await expect(page.getByTestId('benchmark-fx')).toHaveCount(0)
      await expect(page.getByTestId('benchmark-recorded')).toContainText('Gravada ao rodar, em 27/10/2026, 14:30.')
      await expect(page.getByTestId('benchmark-recorded')).toContainText('Ao salvar nos Favoritos, a referência vai junto.')

      // Seletor: foco na busca, Tab/Shift+Tab presos, filtros 44 px no toque, marcado desabilitado e avisos antes da escolha.
      const trigger = page.getByTestId('benchmark-switch')
      expect((await trigger.boundingBox())!.height).toBeGreaterThanOrEqual(44)
      await trigger.click()
      const dialog = page.getByRole('dialog', { name: 'Escolher referência' })
      await expect(dialog).toHaveAttribute('aria-modal', 'true')
      await expect(page.getByTestId('benchmark-search')).toBeFocused()
      await expect(dialog.getByTestId('benchmark-opt-SPY')).toBeVisible()
      for (let i = 0; i < 9; i += 1) {
        await page.keyboard.press('Tab')
        expect(await dialog.evaluate((el) => el.contains(document.activeElement))).toBe(true)
      }
      for (let i = 0; i < 4; i += 1) {
        await page.keyboard.press('Shift+Tab')
        expect(await dialog.evaluate((el) => el.contains(document.activeElement))).toBe(true)
      }
      const filter = dialog.getByTestId('benchmark-filter-crypto')
      expect((await filter.boundingBox())!.height).toBeGreaterThanOrEqual(vp.touch ? 44 : 36)
      await expect(dialog.getByTestId('benchmark-opt-own')).toContainText('Padrão')
      const waves = dialog.getByTestId('benchmark-opt-WAVES/USDT')
      await expect(waves.locator('input')).toBeDisabled()
      await expect(waves).toContainText('Removido')
      const why = await waves.locator('input').getAttribute('aria-describedby')
      await expect(page.locator(`[id="${why}"]`)).toHaveText('Saiu da lista spot da Binance em 17 jun. 2024. Não pode ser escolhido como referência.')
      await waves.locator('label').click({ force: true })
      await expect(dialog.getByTestId('benchmark-opt-own').locator('input')).toBeChecked()
      await expect(dialog.getByTestId('benchmark-opt-CRCL')).toContainText('Sem período comum com esta estratégia')
      await expect(dialog.getByTestId('benchmark-opt-PENGU/USDT')).toContainText('Só 14 dias em comum com esta estratégia')
      await expect(dialog.getByTestId('benchmark-opt-QQQ')).toContainText('Sem histórico guardado: coleta ao escolher')
      await shot(page, `results-dialog-${vp.name}`)
      await page.keyboard.press('Escape')
      await expect(dialog).toHaveCount(0)
      await expect(trigger).toBeFocused()

      // SPY: gravando sem número no DOM; depois período comum, feriado de NY e aviso com as duas moedas.
      answers.SPY = () => ({ status: 201, body: SPY_CMP, delay: 600 })
      await trigger.click()
      await dialog.getByTestId('benchmark-opt-SPY').locator('label').click()
      await dialog.getByTestId('benchmark-use').click()
      await expect(page.getByTestId('benchmark-live')).toContainText('Gravando a comparação com SPY…')
      await expect(block).toHaveAttribute('data-b23-state', 'collecting')
      expect(await block.innerText()).not.toMatch(/\d%|p\.p\./)
      await expect(block).toHaveAttribute('data-b23-state', 'valid')
      await expect(page.getByTestId('benchmark-ref-name')).toHaveText('SPY')
      await expect(page.getByTestId('benchmark-common')).toHaveText('02 jan. 2019 – 31 dez. 2024 · 2.190 dias')
      await expect(page.getByTestId('benchmark-left')).toHaveText('01 jan. 2019 (sem pregão em Nova York) · 0 trades')
      await expect(page.getByTestId('benchmark-price')).toContainText('Retorno de preço, sem dividendos')
      await expect(page.getByTestId('benchmark-fx')).toContainText('USDT tratado como USD, sem conversão.')
      await expect(page.getByTestId('benchmark-fx')).toContainText('BTC/USDT em USDT, SPY em USD')
      await expect(page.getByTestId('benchmark-recorded')).toContainText('Gravada neste resultado em 27/10/2026, 14:32.')
      await shot(page, `results-spy-${vp.name}`)
      expect(posts.at(-1)).toMatchObject({ owner: 'result', reference_symbol: 'SPY' })
      expect(posts.at(-1)!.context.symbol).toBe('BTC/USDT')
      expect(posts.at(-1)!.context.trades.length).toBe(1)

      // Recarregar mantém a escolha (history.state substituído).
      await page.reload()
      await expect(page.getByTestId('benchmark-ref-name')).toHaveText('SPY')

      // QQQ sem histórico: "Coletando…" e depois a comparação.
      answers.QQQ = () => ({ status: 201, body: QQQ_CMP, delay: 600 })
      await page.getByTestId('benchmark-switch').click()
      await page.getByTestId('benchmark-opt-QQQ').locator('label').click()
      await page.getByTestId('benchmark-use').click()
      await expect(page.getByTestId('benchmark-live')).toContainText('Coletando histórico de QQQ na Binance…')
      await expect(page.getByTestId('benchmark-ref-name')).toHaveText('QQQ')
      await expect(page.getByTestId('benchmark-recorded')).toContainText('QQQ versão 5 (coletada agora)')

      // CRCL: sem período comum, motivo e frase de apoio, sem número nem zero.
      answers.CRCL = () => ({ status: 201, body: CRCL_CMP })
      await page.getByTestId('benchmark-switch').click()
      await page.getByTestId('benchmark-opt-CRCL').locator('label').click()
      await page.getByTestId('benchmark-use').click()
      await expect(block).toHaveAttribute('data-b23-reason', 'no_overlap')
      await expect(page.getByTestId('benchmark-insufficient')).toContainText('Sem comparação')
      await expect(page.getByTestId('benchmark-insufficient-reason')).toHaveText(
        'CRCL tem histórico desde 05/06/2025, depois do fim da estratégia (31/12/2024). Não há período comum.',
      )
      await expect(page.getByTestId('benchmark-insufficient')).toContainText('Escolha outra referência com histórico no período da estratégia.')
      expect(await block.innerText()).not.toMatch(/%|0,00/)
      await expect(page.getByTestId('benchmark-fx')).toHaveCount(0)

      // PENGU/USDT: período comum curto, com a frase própria.
      answers['PENGU/USDT'] = () => ({ status: 201, body: PENGU_CMP })
      await page.getByTestId('benchmark-switch').click()
      await page.getByTestId('benchmark-opt-PENGU/USDT').locator('label').click()
      await page.getByTestId('benchmark-use').click()
      await expect(block).toHaveAttribute('data-b23-reason', 'short_overlap')
      await expect(page.getByTestId('benchmark-insufficient-reason')).toContainText('Período comum de 14 dias: o mínimo é 30.')
      await expect(page.getByTestId('benchmark-insufficient')).toContainText('Com poucos dias, anualizar exagera o CAGR.')
      expect(await block.innerText()).not.toMatch(/%|0,00/)

      // Falha na coleta: nada gravado, a anterior continua, alerta com "Tentar de novo" (44 px).
      answers.SPY = () => ({ status: 201, body: SPY_CMP })
      await page.getByTestId('benchmark-switch').click()
      await page.getByTestId('benchmark-opt-SPY').locator('label').click()
      await page.getByTestId('benchmark-use').click()
      await expect(page.getByTestId('benchmark-ref-name')).toHaveText('SPY')
      let failOnce = true
      answers.QQQ = () => {
        if (failOnce) {
          failOnce = false
          return { status: 422, body: { detail: { code: 'reference_collection_failed', message: 'Não foi possível coletar o histórico de QQQ na Binance (tempo esgotado).' } } }
        }
        return { status: 201, body: QQQ_CMP }
      }
      await page.getByTestId('benchmark-switch').click()
      await page.getByTestId('benchmark-opt-QQQ').locator('label').click()
      await page.getByTestId('benchmark-use').click()
      const failure = page.getByTestId('benchmark-failure')
      await expect(failure).toHaveAttribute('role', 'alert')
      await expect(failure).toContainText('Não foi possível coletar o histórico de QQQ na Binance (tempo esgotado). Nada foi gravado: a referência continua SPY.')
      await expect(page.getByTestId('benchmark-ref-name')).toHaveText('SPY')
      await expect(page.getByTestId('benchmark-delta')).toHaveText('+85.1 p.p.')
      const retry = failure.getByRole('button', { name: 'Tentar de novo' })
      expect((await retry.boundingBox())!.height).toBeGreaterThanOrEqual(44)
      await retry.click()
      await expect(page.getByTestId('benchmark-ref-name')).toHaveText('QQQ')
      await expect(page.getByTestId('benchmark-failure')).toHaveCount(0)
    })

    test('planilha de trades autenticada com contexto e salvar nos Favoritos leva a referência', async ({ page }) => {
      const { exports, favorites } = await openResult(page, { ...BTC_RESULT, benchmark_comparison: SPY_CMP })
      await page.getByRole('button', { name: 'Exportar para Excel' }).click()
      await expect(page.getByTestId('trades-export-status')).toHaveText(
        'Planilha baixada: multi_ma_crossover_BTC_USDT_1d_trades.xlsx · abas Trades, Contexto e Legenda · referência SPY.',
      )
      expect(exports[0].auth).toBe('Bearer tok')
      expect(exports[0].body.benchmark_comparison_id).toBe('cmp-spy')
      expect(exports[0].body.context.asset.asset_class).toBe('crypto')
      expect(exports[0].body.context.execution.window.covered.candles).toBe(2192)
      await page.getByTestId('save-favorite-button').click()
      await page.getByRole('dialog', { name: 'Salvar nos Favoritos' }).getByRole('button', { name: 'Salvar', exact: true }).click()
      await expect.poll(() => favorites.length).toBe(1)
      expect(favorites[0].benchmark_comparison_id).toBe('cmp-spy')
    })
  })
}

const NVDA_RESULT = {
  ...BTC_RESULT,
  symbol: 'NVDA',
  start_date: null,
  end_date: null,
  period_type: 'all',
  asset: { symbol: 'NVDA', asset_id: 'binance:equity:EQ_NVDA', asset_class: 'stock', name: 'NVIDIA', currency: 'USD' },
  execution: {
    precision_requested: 'intrabar',
    precision_effective: 'candle',
    timeframe: '1d',
    window: { requested: { start: null, end: null }, covered: { start: '2014-11-11T05:00:00+00:00', end: '2026-10-23T04:00:00+00:00', candles: 2994 } },
  },
  favorite_id: 104,
  favorite_name: 'NVDA Trend',
  benchmark_comparison: comparison({
    id: 'cmp-nvda-spy',
    trigger: 'choice',
    owner: { kind: 'favorite', favorite_id: 104 },
    created_at: '2026-10-27T12:14:00Z',
    reference: SPY_REF,
    strategy: { symbol: 'NVDA', return: 416.8254, cagr: 0.6572, trades_in: 12, trades_out: 0 },
    reference_result: { return: 2.2896, cagr: 0.1048, first_close: { date: '2014-11-11', price: 1 }, last_close: { date: '2026-10-23', price: 2 } },
    common_window: { start: '2014-11-11', end: '2026-10-23', days: 4364 },
    delta: { cagr_pp: 55.24 },
    currency_note: null,
    samples: { reference: { snapshot_id: 'snap-spy-fav', version_label: '5' } },
  }),
}

test.describe('Análise do favorito', () => {
  for (const vp of VIEWPORTS) {
    test(`${vp.name} px: NVDA x SPY gravada no favorito, troca grava no favorito e sem aviso de moeda`, async ({ page }) => {
      await page.setViewportSize(vp.size)
      const { posts, answers } = await openResult(page, NVDA_RESULT, { isOptimization: false, returnTo: '/favorites' })
      await expect(page.getByTestId('benchmark-comparison')).toHaveAttribute('data-b23-owner', 'favorite')
      await expect(page.getByTestId('benchmark-ref-name')).toHaveText('SPY')
      await expect(page.getByTestId('benchmark-fx')).toHaveCount(0)
      await expect(page.getByTestId('benchmark-recorded')).toContainText('Gravada no favorito NVDA Trend em 27/10/2026, 09:14.')
      await expect(page.getByTestId('benchmark-recorded')).toContainText('Refeita só quando o backtest do favorito é atualizado, com a mesma referência.')
      await expect(page.getByTestId('benchmark-recorded')).toContainText('SPY versão 5 (fixada pelo favorito)')
      answers['BTC/USDT'] = () => ({
        status: 201,
        body: comparison({
          id: 'cmp-nvda-btc',
          trigger: 'choice',
          owner: { kind: 'favorite', favorite_id: 104 },
          reference: { ...BTC_OWN, kind: 'catalog' },
          currency_note: 'usdt_as_usd',
          left_out: [{ start: '2014-11-11', end: '2017-08-16', trades: 2, note: 'no_reference' }],
        }),
      })
      await page.getByTestId('benchmark-switch').click()
      await page.getByTestId('benchmark-opt-BTC/USDT').locator('label').click()
      await page.getByTestId('benchmark-use').click()
      await expect(page.getByTestId('benchmark-fx')).toContainText('NVDA em USD, BTC/USDT em USDT')
      await expect(page.getByTestId('benchmark-left')).toHaveText('11 nov. 2014 – 16 ago. 2017 da estratégia · 2 trades fora')
      expect(posts.at(-1)).toEqual({ owner: 'favorite', favorite_id: 104, reference_symbol: 'BTC/USDT' })
      await page.reload()
      await expect(page.getByTestId('benchmark-ref-name')).toHaveText('BTC/USDT')
    })
  }

  test('favorito antigo: "Comparação não registrada" sem calcular ao abrir', async ({ page }) => {
    await page.setViewportSize(DESKTOP)
    const { posts } = await openResult(page, { ...NVDA_RESULT, benchmark_comparison: null }, { isOptimization: false, returnTo: '/favorites' })
    await expect(page.getByTestId('benchmark-unrecorded')).toContainText('Comparação não registrada para este favorito.')
    await expect(page.getByTestId('benchmark-unrecorded').getByRole('button', { name: 'Comparar com o próprio ativo' })).toBeVisible()
    await expect(page.getByTestId('benchmark-switch')).toBeVisible()
    expect(posts).toEqual([])
  })

  test('ETF contra o próprio ativo: retorno de preço, sem dividendos', async ({ page }) => {
    await page.setViewportSize(DESKTOP)
    await openResult(page, {
      ...NVDA_RESULT,
      symbol: 'SPY',
      asset: { symbol: 'SPY', asset_class: 'etf', currency: 'USD', name: 'SPDR' },
      favorite_id: null,
      benchmark_comparison: comparison({ reference: { ...SPY_REF, kind: 'own' }, currency_note: null }),
    }, { isOptimization: true, returnTo: '/combo/configure' })
    await expect(page.getByTestId('benchmark-ref-name')).toHaveText('SPY (próprio ativo)')
    await expect(page.getByTestId('benchmark-price')).toContainText('Retorno de preço, sem dividendos')
  })
})

// ---------------------------------------------------------------- Favoritos

const CRYPTO_CFG = { data_source: 'ccxt', session: '24x7', adjustment: 'none', label_short: 'Binance Spot · 24/7', label_compact: 'Binance Spot · 24/7', label_long: 'Binance Spot · 24/7' }
const EQ_CFG = { data_source: 'binance_equity', session: 'regular_ny', adjustment: 'split', label_short: 'Binance Ações · NY · split', label_compact: 'Binance · NY · split', label_long: 'Binance Ações · pregão regular de NY · ajustado por split' }
const favBase = {
  strategy_name: 'multi_ma_crossover',
  strategy_display_name: 'Médias Móveis: Tendência em Virada',
  parameters: { direction: 'long' },
  created_at: '2026-10-01T10:00:00Z',
  notify_telegram: false,
  is_strategy_protected: false,
}
const FAVORITES = [
  { ...favBase, id: 104, name: 'NVDA Trend', symbol: 'NVDA', timeframe: '1d', tier: 1, configuration: EQ_CFG, asset: { symbol: 'NVDA', asset_class: 'stock', currency: 'USD' }, metrics: { total_trades: 12 }, benchmark_comparison: { id: 'cmp-nvda-spy', status: 'valid', created_at: '2026-10-27T12:14:00Z', reference: { kind: 'catalog', symbol: 'SPY' } } },
  { ...favBase, id: 105, name: 'SPY Trend', symbol: 'SPY', timeframe: '1d', tier: 2, configuration: EQ_CFG, asset: { symbol: 'SPY', asset_class: 'etf', currency: 'USD' }, metrics: { total_trades: 8 }, benchmark_comparison: { id: 'cmp-spy-btc', status: 'valid', created_at: '2026-10-27T13:02:00Z', reference: { kind: 'catalog', symbol: 'BTC/USDT' } } },
  { ...favBase, id: 101, name: 'BTC Trend', symbol: 'BTC/USDT', timeframe: '1d', tier: 1, configuration: CRYPTO_CFG, asset: { symbol: 'BTC/USDT', asset_class: 'crypto', currency: 'USDT' }, metrics: { total_trades: 9 }, benchmark_comparison: { id: 'cmp-btc-own', status: 'valid', created_at: '2026-10-27T11:12:00Z', reference: { kind: 'own', symbol: 'BTC/USDT' } } },
  { ...favBase, id: 99, name: 'BTC antigo', symbol: 'BTC/USDT', timeframe: '4h', tier: 3, configuration: CRYPTO_CFG, asset: { symbol: 'BTC/USDT', asset_class: 'crypto', currency: 'USDT' }, metrics: { total_trades: 5 }, benchmark_comparison: null },
]

for (const vp of VIEWPORTS) {
  test(`Favoritos a ${vp.name} px: "Ref." só fora do padrão e planilha pelo servidor com a lista filtrada`, async ({ page }) => {
    await page.setViewportSize(vp.size)
    await login(page)
    const exportUrls: string[] = []
    await page.route('**/api/**', async (route: Route) => {
      const url = route.request().url()
      if (url.includes('/api/auth/me')) return route.fulfill(json(ADMIN))
      if (url.includes('/api/favorites/export')) {
        exportUrls.push(url)
        return route.fulfill({ ...XLSX, headers: { 'Content-Disposition': 'attachment; filename="Crypto_Backtest_Favorites_2026-10-27.xlsx"' } })
      }
      if (/\/api\/favorites\/?(\?|$)/.test(url)) return route.fulfill(json(FAVORITES))
      if (url.includes('/api/opportunities')) return route.fulfill(json([]))
      return route.fulfill(json({}))
    })
    await page.goto('/favorites')
    const refs = page.locator('[data-testid="fav-reference"]:visible')
    await expect(refs).toHaveCount(2)
    await expect(refs.nth(0)).toHaveText('Ref.: SPY · comparação gravada 27/10')
    await expect(refs.nth(1)).toHaveText('Ref.: BTC/USDT · comparação gravada 27/10')
    await shot(page, `favorites-${vp.name}`)
    await page.getByTestId('export-favorites').click()
    await expect(page.getByTestId('favorites-export-status')).toContainText('Planilha baixada: Crypto_Backtest_Favorites_2026-10-27.xlsx · 4 favoritos da lista filtrada · colunas de hoje + contexto')
    expect(decodeURIComponent(exportUrls[0])).toMatch(/ids=(\d+,){3}\d+$/)
  })
}

// ---------------------------------------------------------------- Decidir: coluna extra

const SWEEP = 'c1121mix'
function cand(rank: number | null, id: string, symbol: string, cls: string, start: string, end: string, extra: Record<string, unknown> = {}) {
  return {
    rank,
    result_id: id,
    sweep_id: SWEEP,
    template_id: 'multi_ma_crossover',
    display_name: 'Médias Móveis: Cruzamento',
    description: 'Cruzamento de médias móveis com filtro de tendência.',
    symbol,
    timeframe: '1d',
    direction: 'long',
    parameters: { fast: 21, slow: 89 },
    calmar_ratio: 2,
    cagr: 0.82,
    benchmark_cagr: 0.7,
    delta_cagr_vs_bh: 0.12,
    max_drawdown: 0.2,
    sharpe_ratio: 0.9,
    profit_factor: 1.7,
    win_rate: 0.52,
    trades_count: 40,
    coverage: 1,
    total_return: 30,
    eligibility: 'eligible',
    eligibility_reason: null,
    dedup_state: 'unique',
    dedup_reference: null,
    start_at: `${start}T00:00:00Z`,
    end_at: `${end}T00:00:00Z`,
    candle_source: 'Binance',
    candle_version: '1',
    expected_candles: 2000,
    observed_valid_candles: 2000,
    fees_slippage: { fees: 0.00075, slippage: 0.0002, fee_pct: 0.00075, slippage_pct: 0.0002 },
    sample: { state: 'kept', retain_until: '2026-11-25T00:00:00Z' },
    oos_verdict: { status: 'GO', reasons: [] },
    asset: { symbol, asset_class: cls, currency: cls === 'crypto' ? 'USDT' : 'USD' },
    ...extra,
  }
}
const CANDIDATES = [
  cand(1, 'RS-BTC1123A1', 'BTC/USDT', 'crypto', '2019-01-01', '2024-12-31'),
  cand(2, 'RS-NVDA1123B2', 'NVDA', 'stock', '2019-01-02', '2024-12-31'),
  cand(3, 'RS-SOL1123D4', 'SOL/USDT', 'crypto', '2020-08-11', '2024-12-31'),
  cand(4, 'RS-SPY1123C3', 'SPY', 'etf', '2019-01-02', '2024-12-31'),
  cand(null, 'RS-PENGU1123E5', 'PENGU/USDT', 'crypto', '2024-12-17', '2024-12-31', { eligibility: 'low_sample', eligibility_reason: 'baixa amostra' }),
]
const WINDOWS = CANDIDATES.map((c) => ({ result_id: c.result_id, symbol: c.symbol, start: c.start_at.slice(0, 10), end: c.end_at.slice(0, 10), sample: 'kept' }))

const validCell = (pp: number, refCagr: number, start: string, fx: boolean) => ({
  state: 'valid', id: 'x', delta_cagr_pp: pp, reference_cagr: refCagr, common_window: { start, end: '2024-12-31', days: 2000 }, currency_note: fx ? 'usdt_as_usd' : null,
})
const SPY_CELLS: Record<string, unknown> = {
  'RS-BTC1123A1': validCell(66.84, 0.1525, '2019-01-02', true),
  'RS-NVDA1123B2': validCell(49.8, 0.1525, '2019-01-02', false),
  'RS-SOL1123D4': validCell(81.2, 0.1525, '2020-08-11', true),
  'RS-SPY1123C3': validCell(-3.2, 0.1525, '2019-01-02', false),
  'RS-PENGU1123E5': { state: 'insufficient', reason_code: 'short_overlap', reason: 'Período comum de 14 dias: o mínimo é 30.' },
}
const QQQ_CELLS = { ...SPY_CELLS, 'RS-NVDA1123B2': validCell(43.0, 0.2204, '2019-01-02', false) }
const CRCL_CELLS = Object.fromEntries(CANDIDATES.map((c) => [c.result_id, { state: 'insufficient', reason_code: 'no_overlap', reason: 'Sem período comum com CRCL.' }]))

type Col = { id: string; reference: Record<string, unknown>; status: string; done: number; total: number; error?: string | null; active: boolean; created_at: string; completed_at: string | null; counts?: Record<string, unknown>; reference_version?: string }

async function openDecidir(page: Page, opts: { results?: typeof CANDIDATES; windows?: typeof WINDOWS } = {}) {
  const results = opts.results ?? CANDIDATES
  const windows = opts.windows ?? WINDOWS
  await installDiscoveryMulticlassMocks(page, {
    sweepState: 'completed',
    results,
    history: [{ sweep_id: SWEEP, state: 'completed', total: 5, processed: 5, succeeded: 5, failed: 0, skipped: 0, snapshot_hash: '1123', created_at: '2026-10-27T12:00:00Z' }],
  })
  await mockAssetCatalog(page, { assets: CATALOG })
  const state: { column: Col | null; pending: Col | null; cells: Record<string, unknown>; ticks: number; puts: Array<string | null>; failNext: Set<string>; exports: string[] } = {
    column: null,
    pending: null,
    cells: {},
    ticks: 0,
    puts: [],
    failNext: new Set(),
    exports: [],
  }
  const cellsFor = (symbol: string) => (symbol === 'SPY' ? SPY_CELLS : symbol === 'QQQ' ? QQQ_CELLS : CRCL_CELLS)
  const counts = (symbol: string) =>
    symbol === 'CRCL'
      ? { valid: 0, no_overlap: 5, computed: 5, total: 5, currency_note: false }
      : { valid: 4, short_overlap: 1, computed: 5, total: 5, currency_note: true }
  const make = (symbol: string, status: string, active: boolean): Col => ({
    id: `col-${symbol}`,
    reference: { symbol, asset_class: symbol === 'CRCL' ? 'stock' : 'etf', currency: 'USD', return_kind: 'price_no_dividends' },
    reference_version: '5',
    status,
    done: 0,
    total: 5,
    active,
    created_at: '2026-10-27T17:40:00Z',
    completed_at: null,
  })
  // Progresso simulado: cada consulta avança o estado (coleta → cálculo → concluída).
  const advance = () => {
    state.ticks += 1
    if (state.pending && state.pending.status === 'collecting') {
      const symbol = String(state.pending.reference.symbol)
      if (state.failNext.has(symbol)) {
        state.failNext.delete(symbol)
        state.pending = { ...state.pending, status: 'failed', error: `Não foi possível coletar o histórico de ${symbol} na Binance (tempo esgotado).` }
        return
      }
      state.column = { ...state.pending, status: 'computing', active: true }
      state.pending = null
      state.cells = {}
      return
    }
    if (state.column && state.column.status === 'computing') {
      const symbol = String(state.column.reference.symbol)
      state.column = { ...state.column, status: 'done', done: 5, completed_at: '2026-10-27T17:41:00Z', counts: counts(symbol) }
      state.cells = cellsFor(symbol)
    }
  }
  const snapshot = () => ({ column: state.column, pending: state.pending })
  await page.route('**/api/combos/discovery/sweeps/*/leaderboard?*', (route) => {
    const rows = results.map((c) => (state.column ? { ...c, reference_comparison: state.cells[c.result_id] ?? { state: 'pending' } } : c))
    return route.fulfill(json({ results: rows, total: rows.length, unfiltered_total: rows.length, class_counts: { all: 5, crypto: 3, stock: 1, etf: 1 }, offset: 0, limit: 12, reference_column: state.column || state.pending ? snapshot() : null }))
  })
  await page.route('**/api/combos/discovery/sweeps/*/leaderboard/export?*', (route) => {
    state.exports.push(route.request().url())
    return route.fulfill({
      ...XLSX,
      headers: { 'Content-Disposition': `attachment; filename="descoberta_${SWEEP}_ranking.xlsx"`, 'X-Export-Rows': '5', ...(state.column ? { 'X-Export-Extra': state.column.status === 'done' ? 'included' : 'computing' } : {}) },
    })
  })
  await page.route('**/api/combos/discovery/sweeps/*/reference-column/retry', (route) => {
    if (state.pending) state.pending = { ...state.pending, status: 'collecting', error: null }
    return route.fulfill(json(snapshot(), 202))
  })
  await page.route('**/api/combos/discovery/sweeps/*/reference-column', (route) => {
    const method = route.request().method()
    if (method === 'PUT') {
      const symbol = JSON.parse(route.request().postData() || '{}').reference_symbol ?? null
      state.puts.push(symbol)
      if (!symbol) {
        state.column = null
        state.pending = null
        state.cells = {}
        return route.fulfill(json({ column: null, pending: null }))
      }
      const stored = symbol !== 'QQQ'
      if (stored) {
        state.column = make(symbol, 'computing', true)
        state.cells = {}
      } else {
        state.pending = make(symbol, 'collecting', false)
      }
      return route.fulfill(json(snapshot(), 202))
    }
    advance()
    return route.fulfill(json({ ...snapshot(), candidates: windows, not_computed: 0, min_days: 30 }))
  })
  await page.goto('/combo/discovery')
  await page.getByRole('tab', { name: 'Decidir' }).click()
  return state
}

for (const vp of VIEWPORTS) {
  test.describe(`Decidir a ${vp.name} px`, () => {
    test.use({ viewport: vp.size, hasTouch: vp.touch, isMobile: vp.touch })

    test('coluna extra: seletor contado, SPY sem mudar a ordem, recarregar, QQQ com falha e retry, CRCL e Próprio ativo', async ({ page }) => {
      const state = await openDecidir(page)
      const table = page.getByTestId('decidir-table')
      await expect(table.locator('tr.result-row')).toHaveCount(5)
      const before = await table.locator('tr.result-row .rank-cell-value').allTextContents()
      expect(before).toEqual(['1', '2', '3', '4', '—'])
      await expect(page.getByTestId('ranking-reference')).toContainText('Referência do ranking: o próprio ativo (buy-and-hold, long-only). A ordem, o rank global e a elegibilidade não mudam com a coluna extra')
      const strip = page.getByTestId('discovery-extra-ref')
      await expect(page.getByTestId('extra-ref-name')).toHaveText('Nenhuma')
      await expect(strip).toContainText('Escolher uma referência guarda as amostras desta varredura enquanto a coluna existir.')
      await expect(page.getByTestId('extra-col-header')).toHaveCount(0)
      const trigger = page.getByTestId('discovery-ref-switch')
      await expect(trigger).toHaveText('Comparar com outra referência')
      expect((await trigger.boundingBox())!.height).toBeGreaterThanOrEqual(44)
      const exportBtn = page.getByTestId('export-ranking')
      expect((await exportBtn.boundingBox())!.height).toBeGreaterThanOrEqual(44)

      // Seletor com aviso contado sobre os candidatos (sem coletar).
      await trigger.click()
      const dialog = page.getByRole('dialog', { name: 'Escolher referência da coluna extra' })
      await expect(page.getByTestId('benchmark-search')).toBeFocused()
      await expect(dialog.getByTestId('benchmark-opt-own')).toContainText('Próprio ativo')
      await expect(dialog.getByTestId('benchmark-opt-own')).toContainText('Padrão')
      await expect(dialog.getByTestId('benchmark-opt-CRCL')).toContainText('Sem período comum com nenhum candidato desta varredura')
      await expect(dialog.getByTestId('benchmark-opt-SPY')).toContainText('1 candidato com período comum curto (PENGU/USDT)')
      await expect(dialog.getByTestId('benchmark-opt-WAVES/USDT').locator('input')).toBeDisabled()
      expect((await dialog.getByTestId('benchmark-filter-etf').boundingBox())!.height).toBeGreaterThanOrEqual(vp.touch ? 44 : 36)
      for (let i = 0; i < 8; i += 1) {
        await page.keyboard.press('Tab')
        expect(await dialog.evaluate((el) => el.contains(document.activeElement))).toBe(true)
      }
      await page.keyboard.press('Shift+Tab')
      expect(await dialog.evaluate((el) => el.contains(document.activeElement))).toBe(true)
      await page.keyboard.press('Escape')
      await expect(dialog).toHaveCount(0)
      await expect(trigger).toBeFocused()

      // SPY: "Calculando…" sem número; depois a coluna, com a mesma ordem e o mesmo rank.
      await trigger.click()
      await dialog.getByTestId('benchmark-opt-SPY').locator('label').click()
      await dialog.getByTestId('benchmark-use').click()
      // Calculando: célula sem número (nem no DOM) e progresso na faixa.
      await expect(page.getByTestId('extra-cell-RS-BTC1123A1')).toHaveAttribute('data-b23-xstate', 'busy')
      await expect(page.getByTestId('extra-cell-RS-BTC1123A1')).toHaveText('Calculando…')
      await expect(page.getByTestId('extra-ref-live')).toContainText('Calculando contra SPY: 0 de 5 candidatos…')
      expect(await table.locator('[data-testid^="extra-cell-"]').evaluateAll((cells) => cells.map((c) => c.textContent).join(' '))).not.toMatch(/%|p\.p\./)
      await expect(page.getByTestId('extra-cell-RS-BTC1123A1')).toContainText('+66,8 p.p.', { timeout: 10_000 })
      if (!vp.touch) {
        await expect(page.getByTestId('extra-col-header')).toContainText('Contra SPY')
        await expect(page.getByTestId('extra-col-header')).toContainText('Δ CAGR · período comum · não ordena')
      }
      await expect(page.getByTestId('extra-cell-RS-BTC1123A1')).toHaveAttribute('data-label', 'Contra SPY')
      await expect(page.getByTestId('extra-cell-RS-BTC1123A1')).toContainText('SPY +15,25% a.a.')
      await expect(page.getByTestId('extra-cell-RS-BTC1123A1')).toContainText('2 jan. 2019 – 31 dez. 2024')
      await expect(page.getByTestId('extra-cell-RS-BTC1123A1')).toContainText('USDT tratado como USD')
      await expect(page.getByTestId('extra-cell-RS-NVDA1123B2')).not.toContainText('USDT tratado como USD')
      await expect(page.getByTestId('extra-cell-RS-SPY1123C3')).toContainText('−3,2 p.p.')
      const pengu = page.getByTestId('extra-cell-RS-PENGU1123E5')
      await expect(pengu).toContainText('Sem comparação')
      await expect(pengu).toContainText('Período comum de 14 dias: o mínimo é 30.')
      expect(await pengu.innerText()).not.toMatch(/%|p\.p\.|0,00/)
      expect(await table.locator('tr.result-row .rank-cell-value').allTextContents()).toEqual(before)
      await expect(page.getByTestId('sort-filter').locator('option')).toHaveCount(2)
      await expect(page.getByTestId('extra-ref-name')).toHaveText('SPY')
      await expect(strip).toContainText('Retorno de preço, sem dividendos')
      await expect(strip).toContainText('A coluna não muda a ordem, o rank global nem a elegibilidade.')
      await expect(page.getByTestId('extra-ref-summary')).toHaveText('4 de 5 candidatos desta varredura com comparação; 1 sem comparação (período comum curto).')
      await expect(page.getByTestId('extra-ref-fx')).toContainText('USDT tratado como USD, sem conversão.')
      await expect(page.getByTestId('extra-ref-recorded')).toContainText('Gravada nesta varredura para você em 27/10/2026, 14:41.')
      await shot(page, `decidir-spy-${vp.name}`)
      await expect(page.locator('[data-testid^="sample-RS-"]').first()).toHaveText('amostra guardada pela coluna extra')

      // Planilha do ranking com as colunas (extra), todas as páginas e os filtros atuais.
      await exportBtn.click()
      await expect(page.getByTestId('export-ranking-status')).toHaveText(
        `Planilha baixada: descoberta_${SWEEP}_ranking.xlsx · 5 candidatos do recorte, todas as páginas, na ordem do ranking · abas Ranking e Legenda · colunas (extra) contra SPY.`,
      )
      expect(state.exports.at(-1)).toContain('metric=')

      // Recarregar mantém a coluna gravada, sem cálculo.
      await page.reload()
      await page.getByRole('tab', { name: 'Decidir' }).click()
      await expect(page.getByTestId('extra-cell-RS-BTC1123A1')).toContainText('+66,8 p.p.')
      await expect(page.getByTestId('extra-ref-live')).not.toContainText('Calculando')

      // QQQ sem histórico: coleta, falha sem gravar (a coluna continua SPY) e "Tentar de novo".
      state.failNext.add('QQQ')
      await page.getByTestId('discovery-ref-switch').click()
      await page.getByTestId('benchmark-opt-QQQ').locator('label').click()
      await page.getByTestId('benchmark-use').click()
      await expect(page.getByTestId('extra-ref-live')).toContainText('Coletando histórico de QQQ na Binance…')
      const failure = page.getByTestId('extra-ref-failure')
      await expect(failure).toContainText('Nada foi gravado: a coluna continua contra SPY.', { timeout: 10_000 })
      await expect(failure).toHaveAttribute('role', 'alert')
      await expect(page.getByTestId('extra-cell-RS-BTC1123A1')).toContainText('+66,8 p.p.')
      const retry = page.getByTestId('extra-ref-retry')
      expect((await retry.boundingBox())!.height).toBeGreaterThanOrEqual(44)
      await retry.click()
      await expect(page.getByTestId('extra-ref-name')).toHaveText('QQQ', { timeout: 10_000 })
      await expect(page.getByTestId('extra-cell-RS-NVDA1123B2')).toContainText('+43,0 p.p.', { timeout: 10_000 })
      expect(await table.locator('tr.result-row .rank-cell-value').allTextContents()).toEqual(before)

      // CRCL: sem período comum em todos, com o resumo explicando.
      await page.getByTestId('discovery-ref-switch').click()
      await page.getByTestId('benchmark-opt-CRCL').locator('label').click()
      await page.getByTestId('benchmark-use').click()
      await expect(page.getByTestId('extra-ref-summary')).toContainText('Nenhum candidato desta varredura tem período comum com CRCL', { timeout: 10_000 })
      for (const c of CANDIDATES) {
        const cell = page.getByTestId(`extra-cell-${c.result_id}`)
        await expect(cell).toContainText('Sem período comum com CRCL.')
        expect(await cell.innerText()).not.toMatch(/%|p\.p\./)
      }

      // Próprio ativo: a coluna some e a ordem segue igual.
      await page.getByTestId('discovery-ref-switch').click()
      await page.getByTestId('benchmark-opt-own').locator('label').click()
      await page.getByTestId('benchmark-use').click()
      await expect(page.getByTestId('extra-ref-name')).toHaveText('Nenhuma')
      await expect(page.locator('[data-testid^="extra-cell-"]')).toHaveCount(0)
      expect(state.puts.at(-1)).toBeNull()
      expect(await table.locator('tr.result-row .rank-cell-value').allTextContents()).toEqual(before)
    })
  })
}

test('Decidir: candidato com amostra vencida fica "Sem comparação" com aviso e "Sem amostra" sem número', async ({ page }) => {
  await page.setViewportSize(DESKTOP)
  const state = await openDecidir(page)
  state.column = {
    id: 'col-SPY', reference: { symbol: 'SPY', asset_class: 'etf', currency: 'USD' }, reference_version: '5', status: 'done', done: 5, total: 5, active: true,
    created_at: '2026-10-27T17:40:00Z', completed_at: '2026-10-27T17:41:00Z',
    counts: { valid: 3, short_overlap: 1, sample_expired: 1, computed: 5, total: 5, currency_note: true },
  }
  state.cells = {
    ...SPY_CELLS,
    'RS-SOL1123D4': { state: 'insufficient', reason_code: 'sample_expired', reason: 'Amostra do candidato vencida em 30/09/2026.' },
    'RS-SPY1123C3': { state: 'no_sample' },
  }
  await page.reload()
  await page.getByRole('tab', { name: 'Decidir' }).click()
  await expect(page.getByTestId('extra-cell-RS-SOL1123D4')).toContainText('Sem comparação')
  await expect(page.getByTestId('extra-cell-RS-SOL1123D4')).toContainText('Amostra do candidato vencida em 30/09/2026.')
  await expect(page.getByTestId('extra-cell-RS-SPY1123C3')).toHaveText('Sem amostra')
  await expect(page.getByTestId('extra-ref-summary')).toContainText('1 sem comparação (amostra vencida)')
  // Promoção com a coluna ativa: o favorito leva a comparação gravada da célula.
  await page.getByTestId('promote-RS-BTC1123A1').click()
  await expect(page.getByTestId('promotion-reference')).toContainText('Leva a comparação com SPY gravada')
})

// Retrabalho pós Não homologar: a cripto da Descoberta sem o histórico novo nunca guarda amostra. O
// BTC/USDT foi refeito pelo caminho antigo (velas do cache) com as mesmas métricas da varredura e
// compara; o SOL/USDT também é refazível (cache presente), mas os trades refeitos não batem com a
// varredura (trades, CAGR ou acerto) e a célula diz o motivo verdadeiro, nunca "vencida"; a linha de
// nenhum dos dois diz que a amostra está guardada pela coluna extra.
const NO_SAMPLE = new Set(['RS-BTC1123A1', 'RS-SOL1123D4'])
const LEGACY_CANDIDATES = CANDIDATES.map((c) =>
  NO_SAMPLE.has(c.result_id) ? { ...c, candle_source: 'ccxt', candle_version: '32bc697fc369', sample: { state: 'none', retain_until: null } } : c,
)
const LEGACY_WINDOWS = WINDOWS.map((w) =>
  NO_SAMPLE.has(w.result_id) ? { ...w, sample: 'legacy' } : w,
)
for (const vp of VIEWPORTS) {
  test(`Decidir a ${vp.name} px: cripto sem amostra compara pelo caminho antigo ou diz o motivo verdadeiro`, async ({ page }) => {
    await page.setViewportSize(vp.size)
    const state = await openDecidir(page, { results: LEGACY_CANDIDATES, windows: LEGACY_WINDOWS })
    // Antes da escolha: o refazível pelo caminho antigo não é aviso (a conferência é no cálculo).
    await page.getByTestId('discovery-ref-switch').click()
    const dialog = page.getByRole('dialog', { name: 'Escolher referência da coluna extra' })
    const spy = dialog.getByTestId('benchmark-opt-SPY')
    await expect(spy).not.toContainText('sem as velas da varredura')
    await expect(spy).toContainText('1 candidato com período comum curto (PENGU/USDT)')
    await expect(dialog).not.toContainText('vencida')
    await page.keyboard.press('Escape')
    state.column = {
      id: 'col-SPY', reference: { symbol: 'SPY', asset_class: 'etf', currency: 'USD', return_kind: 'price_no_dividends' }, reference_version: '5', status: 'done', done: 5, total: 5, active: true,
      created_at: '2026-10-27T17:40:00Z', completed_at: '2026-10-27T17:41:00Z',
      counts: { valid: 3, short_overlap: 1, sample_unavailable: 1, sample_expired: 0, computed: 5, total: 5, currency_note: true },
    }
    state.cells = {
      ...SPY_CELLS,
      'RS-SOL1123D4': { state: 'insufficient', reason_code: 'sample_unavailable', reason: 'Trades refeitos não batem com a varredura.', expired_at: null },
    }
    await page.reload()
    await page.getByRole('tab', { name: 'Decidir' }).click()
    const btc = page.getByTestId('extra-cell-RS-BTC1123A1')
    await expect(btc).toContainText('+66,8 p.p.')
    await expect(btc).toContainText('SPY +15,25% a.a.')
    await expect(btc).toContainText('2 jan. 2019 – 31 dez. 2024')
    const sol = page.getByTestId('extra-cell-RS-SOL1123D4')
    await expect(sol).toContainText('Sem comparação')
    await expect(sol).toContainText('Trades refeitos não batem com a varredura.')
    expect(await sol.innerText()).not.toMatch(/%|p\.p\.|vencida/)
    await expect(page.getByTestId('extra-ref-summary')).toHaveText(
      '3 de 5 candidatos desta varredura com comparação; 1 sem comparação (período comum curto); 1 sem comparação (sem os trades da varredura).',
    )
    // A linha do candidato sem amostra não diz que a amostra está guardada.
    await expect(page.getByTestId('sample-RS-BTC1123A1')).toHaveText('sem amostra guardada')
    await expect(page.getByTestId('sample-RS-SOL1123D4')).toHaveText('sem amostra guardada')
    await expect(page.getByTestId('sample-RS-NVDA1123B2')).toHaveText('amostra guardada pela coluna extra')
    await expect(page.getByTestId('decidir-table')).not.toContainText('vencida')
    await shot(page, `decidir-cripto-sem-amostra-${vp.name}`)
  })
}

// ---------------------------------------------------------------- 7.2: as três planilhas baixam com o contexto

/**
 * As planilhas servidas aqui saem do construtor real do servidor (`services/export_context.py`): os testes
 * do backend as regravam com `C1123_WRITE_FIXTURES=1` e conferem, a cada execução, que continuam iguais ao
 * que as rotas montam hoje. O E2E baixa pelo botão de cada tela e lê o arquivo baixado.
 */
const FIXTURES = path.resolve(path.dirname(fileURLToPath(import.meta.url)), 'fixtures/card-1123')
const CONTEXT_FIELDS = [
  'Classe', 'Moeda', 'Fonte', 'Sessão', 'Ajuste', 'Período pedido', 'Período efetivo', 'Modo de execução',
  'Versão da amostra', 'Referência', 'Tipo de retorno da referência', 'Período comum', 'Fora do período comum',
  'Retorno da estratégia no período comum', 'CAGR da estratégia no período comum', 'Retorno da referência',
  'CAGR da referência', 'Diferença de CAGR (p.p.)', 'Situação da comparação', 'Aviso de moeda',
  'Versão da amostra da referência', 'Comparação gravada em',
]
const workbookFile = (name: string) => ({ ...XLSX, body: readFileSync(path.join(FIXTURES, name)) })

async function download(page: Page, click: () => Promise<void>) {
  const [file] = await Promise.all([page.waitForEvent('download'), click()])
  const wb = XLSXLIB.read(readFileSync((await file.path())!), { type: 'buffer' })
  const rows = (sheet: string) => XLSXLIB.utils.sheet_to_json<unknown[]>(wb.Sheets[sheet], { header: 1, defval: '' }) as unknown[][]
  return { name: file.suggestedFilename(), sheets: wb.SheetNames, rows }
}

test('7.2: planilhas de trades, Favoritos e Descoberta baixam com o contexto completo', async ({ page }) => {
  await page.setViewportSize(DESKTOP)
  // Trades do resultado: abas Trades (+ Moeda), Contexto (22 campos) e Legenda.
  await login(page)
  await mockAssetCatalog(page, { assets: CATALOG })
  const resultRoutes = /\/api\/(auth\/me|combos\/export-trades|market\/candles)/
  await page.route(resultRoutes, (route) => {
    const url = route.request().url()
    if (url.includes('/api/auth/me')) return route.fulfill(json(ADMIN))
    if (url.includes('export-trades')) {
      return route.fulfill({ ...workbookFile('trades.xlsx'), headers: { 'Content-Disposition': 'attachment; filename="multi_ma_crossover_BTC_USDT_1d_trades.xlsx"' } })
    }
    return route.fulfill(json({ candles: [] }))
  })
  await page.goto('/combo/results')
  await page.evaluate((result) => {
    history.replaceState({ usr: { result, isOptimization: true, returnTo: '/combo/configure' }, key: 'c1123-72', idx: 0 }, '', location.href)
  }, { ...BTC_RESULT, benchmark_comparison: SPY_CMP })
  await page.reload()
  const trades = await download(page, () => page.getByRole('button', { name: 'Exportar para Excel' }).click())
  expect(trades.sheets).toEqual(['Trades', 'Contexto', 'Legenda'])
  expect(trades.rows('Trades')[0].at(-1)).toBe('Moeda')
  const context = trades.rows('Contexto')
  expect(context.slice(1).map((r) => r[0])).toEqual(CONTEXT_FIELDS)
  const ctx = Object.fromEntries(context.slice(1).map((r) => [r[0], r[1]]))
  expect(ctx['Referência']).toBe('SPY · ETF · USD')
  expect(ctx['Aviso de moeda']).toBe('USDT tratado como USD, sem conversão. A comparação é só em percentual.')
  expect(ctx['Período comum']).toBe('02/01/2019 – 31/12/2024 · 2.190 dias')
  await page.unroute(resultRoutes)

  // Favoritos: colunas de hoje + contexto; favorito antigo de cripto com "deduzido" e "não registrado".
  await page.route('**/api/**', (route) => {
    const url = route.request().url()
    if (url.includes('/api/auth/me')) return route.fulfill(json(ADMIN))
    if (url.includes('/api/favorites/export')) {
      return route.fulfill({ ...workbookFile('favoritos.xlsx'), headers: { 'Content-Disposition': 'attachment; filename="Crypto_Backtest_Favorites_2026-10-27.xlsx"' } })
    }
    if (/\/api\/favorites\/?(\?|$)/.test(url)) return route.fulfill(json(FAVORITES))
    if (url.includes('/api/opportunities')) return route.fulfill(json([]))
    return route.fulfill(json({}))
  })
  await page.goto('/favorites')
  const favs = await download(page, () => page.getByTestId('export-favorites').click())
  expect(favs.sheets).toEqual(['Favoritos', 'Legenda'])
  const favRows = favs.rows('Favoritos')
  const header = favRows[0] as string[]
  expect(header.slice(0, 2)).toEqual(['Name', 'Symbol'])
  expect(header.slice(-22)).toEqual(CONTEXT_FIELDS)
  const oldRow = favRows.find((r) => r[0] === 'BTC antigo')!
  const old = Object.fromEntries(header.map((h, i) => [h, oldRow[i]]))
  expect(old['Classe']).toBe('Cripto (deduzido)')
  expect(old['Moeda']).toBe('USDT (deduzido)')
  for (const field of ['Fonte', 'Sessão', 'Ajuste', 'Versão da amostra', 'Situação da comparação']) expect(old[field]).toBe('não registrado')
  expect(favs.rows('Legenda').map((r) => r[0])).toEqual(expect.arrayContaining(['Tela × planilha', 'Comparação refeita']))
  await page.unrouteAll({ behavior: 'ignoreErrors' })

  // Descoberta: referência do próprio ativo nos 22 campos e, com a coluna, as 13 "(extra)".
  const state = await openDecidir(page)
  state.column = {
    id: 'col-SPY', reference: { symbol: 'SPY', asset_class: 'etf', currency: 'USD' }, reference_version: '5', status: 'done', done: 5, total: 5,
    active: true, created_at: '2026-10-27T17:40:00Z', completed_at: '2026-10-27T17:41:00Z',
    counts: { valid: 4, short_overlap: 1, computed: 5, total: 5, currency_note: true },
  }
  state.cells = SPY_CELLS
  await page.route('**/api/combos/discovery/sweeps/*/leaderboard/export?*', (route) =>
    route.fulfill({ ...workbookFile('descoberta.xlsx'), headers: { 'Content-Disposition': `attachment; filename="descoberta_${SWEEP}_ranking.xlsx"`, 'X-Export-Rows': '6', 'X-Export-Extra': 'included' } }),
  )
  await page.reload()
  await page.getByRole('tab', { name: 'Decidir' }).click()
  const ranking = await download(page, () => page.getByTestId('export-ranking').click())
  expect(ranking.sheets).toEqual(['Ranking', 'Legenda'])
  const rankRows = ranking.rows('Ranking')
  const rh = rankRows[0] as string[]
  expect(rh.slice(18, 40)).toEqual(CONTEXT_FIELDS)
  expect(rh.slice(40)).toEqual(CONTEXT_FIELDS.slice(9).map((f) => `${f} (extra)`))
  const refIdx = rh.indexOf('Referência')
  expect(rankRows.slice(1).every((r) => r[refIdx] === 'Próprio ativo (buy-and-hold, long-only)')).toBe(true)
  expect(rankRows[1][rh.indexOf('Referência (extra)')]).toBe('SPY · ETF · USD')
  expect(ranking.rows('Legenda').map((r) => r[0])).toEqual(expect.arrayContaining(['(extra)', 'Retornos do ranking']))
})
