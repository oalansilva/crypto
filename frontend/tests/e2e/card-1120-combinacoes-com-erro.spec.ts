import { expect, test, type Page } from '@playwright/test'
import { mockAssetCatalog } from './helpers/assetCatalogMock'
import { coverageCatalog } from './helpers/history1118'
import { INTRABAR, buildJob, installLoteApi, simItem } from './helpers/lote1120'

/**
 * Card #1120 (segunda entrada pós-T18): combinação com erro é pulada e contada, com a API simulada, a 1440 e a 390 px.
 * Tela de 1 ativo (resultado do Combo e Otimização): o aviso "Combinações puladas" só aparece quando a resposta
 * traz `combination_errors`. Painel do lote: o item gravado mostra "N combinações com erro: <motivo>" no detalhe.
 */

const ADMIN_USER = {
  id: 'discovery-admin',
  email: 'alan@example.com',
  name: 'Alan Silva',
  isAdmin: true,
  mustChangePassword: false,
}
const TEMPLATES = [{ name: 'ema_rsi', display_name: 'Médias: tendência', description: 'x', is_readonly: true }]
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

const json = (body: unknown, status = 200) => ({ status, contentType: 'application/json', body: JSON.stringify(body) })
const fitsHorizontally = (page: Page) =>
  page.evaluate(() => document.documentElement.scrollWidth <= document.documentElement.clientWidth)

const REASON = 'a regra usa coluna que a combinação não tem (RSI_14)'
const COMBINATION_ERRORS = {
  failed: 132,
  executed: 200,
  reasons: [{ reason: REASON, count: 132 }],
  message: `132 combinações com erro: ${REASON} (x132)`,
}

const metrics = { total_trades: 2, win_rate: 0.5, total_return: 0.08, avg_profit: 0.04, sharpe_ratio: 0.9, max_drawdown: 0.05 }
const PROVENANCE = { adjustment: 'adjusted', version_label: '3', snapshot_id: 'snap-1', kept_until: '2026-11-22T12:00:00Z' }
const EQUITY_CONVENTIONS = {
  fee: 0.001,
  fee_confirmed: true,
  slippage: 0.0002,
  calendar: { kind: 'nyse_regular_session', timezone: 'America/New_York', years: 'calendar_days_365', sessions_per_year: 252 },
  fraction: { simulated: true, confirms_account: false },
  short: null,
  gap_exit: { enabled: true, stops_with_gap: 0 },
  adjusted_prices: true,
}
const EXECUTION = {
  precision_requested: 'intrabar',
  precision_effective: 'intrabar_15m',
  timeframe: '1d',
  intraday_missing: [],
  intraday_reason: null,
  gap_stops: 0,
  window: { requested: { start: '2024-01-01', end: '2024-01-31' }, covered: { start: '2024-01-02T05:00:00+00:00', end: '2024-01-31T05:00:00+00:00', candles: 21 } },
  collection: null,
}

function candles(count: number) {
  const start = new Date('2024-01-02T05:00:00Z').getTime()
  return Array.from({ length: count }, (_, i) => ({
    timestamp_utc: new Date(start + i * 86_400_000).toISOString(),
    open: 190 + i * 0.2,
    high: 191.5 + i * 0.2,
    low: 188.5 + i * 0.2,
    close: 190.4 + i * 0.2,
    volume: 1000,
  }))
}

function singleResult(extra: Record<string, unknown> = {}) {
  return {
    template_name: 'ema_rsi',
    symbol: 'NVDA',
    timeframe: '1d',
    start_date: '2024-01-01',
    end_date: '2024-01-31',
    period_type: 'custom',
    execution_mode: 'fast_1d',
    asset: { symbol: 'NVDA', asset_id: 'binance:equity:EQ_NVDA', asset_class: 'stock', name: 'NVIDIA Corporation Common Stock', currency: 'USD' },
    data_provenance: PROVENANCE,
    execution: EXECUTION,
    conventions: EQUITY_CONVENTIONS,
    parameters: { direction: 'long', stop_loss: 0.05 },
    metrics,
    trades: [{ entry_time: '2024-01-04T05:00:00+00:00', entry_price: 191.3, exit_time: '2024-01-18T05:00:00+00:00', exit_price: 204.1, profit: 0.0669, type: 'long', signal_type: 'Close entry(s) order...' }],
    indicator_data: {},
    candles: candles(21),
    ...extra,
  }
}

async function authMocks(page: Page) {
  await page.addInitScript((user) => {
    localStorage.setItem('auth_access_token', 'admin-token')
    localStorage.setItem('auth_refresh_token', 'admin-refresh')
    localStorage.setItem('auth_user', JSON.stringify(user))
    localStorage.setItem('cripto-farol-onboarding-dismissed', '1')
  }, ADMIN_USER)
  await page.route('**/api/**', (route) => route.fulfill(json({})))
  await page.route('**/api/auth/me', (route) => route.fulfill(json(ADMIN_USER)))
}

async function templateMocks(page: Page) {
  await page.route('**/api/combos/templates', (route) => route.fulfill(json({ prebuilt: TEMPLATES, examples: [], custom: [] })))
  await page.route('**/api/combos/meta/ema_rsi', (route) =>
    route.fulfill(
      json({
        name: 'ema_rsi',
        display_name: 'Médias: tendência',
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
  await mockAssetCatalog(page, { assets: coverageCatalog() })
}

async function openResult(page: Page, result: unknown) {
  await authMocks(page)
  await page.goto('/combo/results')
  await page.evaluate(
    ({ result }) => {
      history.replaceState({ usr: { result, isOptimization: true, returnTo: '/combo/configure' }, key: 'card-1120', idx: 0 }, '', location.href)
    },
    { result },
  )
  await page.reload()
  await expect(page.getByTestId('result-data-execution')).toBeVisible()
}

async function optimizeMocks(page: Page, response: unknown) {
  await authMocks(page)
  await templateMocks(page)
  await page.route('**/api/combos/optimize', (route) => route.fulfill(json(response)))
}

function optimizeResponse(extra: Record<string, unknown> = {}) {
  const base = singleResult()
  return {
    job_id: 'o1120',
    template_name: 'ema_rsi',
    symbol: 'NVDA',
    timeframe: '1d',
    stages: [{ stage_num: 1, stage_name: 'Fase 1', values: [1, 2] }],
    best_parameters: { ema_length: 10 },
    best_metrics: { total_return: 0.08, win_rate: 0.5, sharpe_ratio: 0.9, total_trades: 2 },
    execution_mode: 'fast_1d',
    asset: base.asset,
    data_provenance: PROVENANCE,
    execution: EXECUTION,
    conventions: EQUITY_CONVENTIONS,
    trades: [],
    metrics,
    parameters: { direction: 'long' },
    indicator_data: {},
    candles: [],
    ...extra,
  }
}

// ------------------------------------------------------------------------------------------ resultado

test.describe('Resultado de 1 ativo: combinações puladas', () => {
  for (const viewport of [DESKTOP, PHONE]) {
    test(`com combination_errors: o aviso mostra a contagem e o motivo agrupado (${viewport.width} px)`, async ({ page }) => {
      await page.setViewportSize(viewport)
      await openResult(page, singleResult({ combination_errors: COMBINATION_ERRORS }))
      const notice = page.getByTestId('result-combination-errors')
      await expect(notice).toHaveCount(1)
      await expect(notice).toBeVisible()
      await expect(notice).toHaveAttribute('role', 'note')
      await expect(notice.locator('strong')).toHaveText('Combinações puladas')
      await expect(notice).toContainText('132 combinações com erro')
      await expect(notice).toContainText(`${REASON} (x132)`)
      await expect(notice).toContainText('O resultado vem das combinações que funcionaram.')
      expect(await fitsHorizontally(page)).toBe(true)
    })

    test(`sem a mensagem pronta, o aviso monta a contagem e o motivo a partir de reasons (${viewport.width} px)`, async ({ page }) => {
      await page.setViewportSize(viewport)
      const { message: _message, ...withoutMessage } = COMBINATION_ERRORS
      await openResult(page, singleResult({ combination_errors: withoutMessage }))
      await expect(page.getByTestId('result-combination-errors')).toContainText(`132 combinações com erro: ${REASON} (x132)`)
    })

    test(`sem combination_errors: o aviso não aparece (${viewport.width} px)`, async ({ page }) => {
      await page.setViewportSize(viewport)
      await openResult(page, singleResult())
      await expect(page.getByTestId('result-combination-errors')).toHaveCount(0)
      await expect(page.getByText('Combinações puladas')).toHaveCount(0)
    })

    test(`com combination_errors de failed 0: o aviso não aparece (${viewport.width} px)`, async ({ page }) => {
      await page.setViewportSize(viewport)
      await openResult(page, singleResult({ combination_errors: { failed: 0, executed: 200, reasons: [] } }))
      await expect(page.getByTestId('result-combination-errors')).toHaveCount(0)
    })
  }
})

// ------------------------------------------------------------------------------------------ Otimização

test.describe('Otimização com 1 ativo: combinações puladas', () => {
  for (const viewport of [DESKTOP, PHONE]) {
    test(`a resposta com combination_errors mostra o aviso ao lado de "Dados e execução" (${viewport.width} px)`, async ({ page }) => {
      await page.setViewportSize(viewport)
      await optimizeMocks(page, optimizeResponse({ combination_errors: COMBINATION_ERRORS }))
      await page.goto('/combo/optimize?template=ema_rsi&symbol=NVDA')
      await page.locator('select').filter({ has: page.locator('option[value="1m"]') }).first().selectOption('1d')
      await page.getByTestId('run-optimization').click()
      await expect(page.getByText('Optimization Complete')).toBeVisible()
      await expect(page.getByTestId('result-data-execution')).toBeVisible()
      const notice = page.getByTestId('result-combination-errors')
      await expect(notice).toHaveCount(1)
      await expect(notice).toContainText('Combinações puladas')
      await expect(notice).toContainText('132 combinações com erro')
      await expect(notice).toContainText(`${REASON} (x132)`)
      expect(await fitsHorizontally(page)).toBe(true)
    })

    test(`a resposta sem combination_errors não mostra o aviso (${viewport.width} px)`, async ({ page }) => {
      await page.setViewportSize(viewport)
      await optimizeMocks(page, optimizeResponse())
      await page.goto('/combo/optimize?template=ema_rsi&symbol=NVDA')
      await page.locator('select').filter({ has: page.locator('option[value="1m"]') }).first().selectOption('1d')
      await page.getByTestId('run-optimization').click()
      await expect(page.getByText('Optimization Complete')).toBeVisible()
      await expect(page.getByTestId('result-data-execution')).toBeVisible()
      await expect(page.getByTestId('result-combination-errors')).toHaveCount(0)
    })
  }
})

// ------------------------------------------------------------------------------------------ lote

test.describe('Painel do lote: combinações com erro no detalhe do item', () => {
  for (const viewport of [DESKTOP, PHONE]) {
    test(`item gravado com reason mostra "N combinações com erro: <motivo>"; item sem erro não mostra (${viewport.width} px)`, async ({ page }) => {
      await page.setViewportSize(viewport)
      await authMocks(page)
      await templateMocks(page)
      const sim = await installLoteApi(page)
      const note = `132 combinações com erro: ${REASON} (x132)`
      sim.setJob(
        buildJob(
          [
            simItem(0, 'BTC/USDT', 'success', { execution: INTRABAR, favorite_id: 101, reason: note }),
            simItem(1, 'ETH/USDT', 'success', { execution: INTRABAR, favorite_id: 102 }),
          ],
          'completed',
          { elapsed_sec: 61, succeeded: 2 },
        ),
      )
      // concluído não aparece em /active: abre o lote como se tivesse acabado de terminar
      sim.job!.status = 'running'
      await page.goto('/combo/configure?template=ema_rsi')
      sim.job!.status = 'completed'
      await expect(page.getByTestId('batch-status')).toHaveText('Concluído', { timeout: 10_000 })
      const withErrors = page.locator('.lote-row[data-asset="BTC/USDT"]')
      const clean = page.locator('.lote-row[data-asset="ETH/USDT"]')
      await expect(withErrors).toContainText('Favorito gravado')
      await expect(withErrors).toContainText(note)
      await expect(clean).toContainText('Favorito gravado')
      await expect(clean).not.toContainText('combinações com erro')
      expect(await fitsHorizontally(page)).toBe(true)
    })
  }
})
