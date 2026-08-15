import { expect, test, type Page } from '@playwright/test'

const ADMIN_USER = {
  id: 'discovery-admin',
  email: 'alan@example.com',
  name: 'Alan Silva',
  isAdmin: true,
  mustChangePassword: false,
}

const PREFLIGHT = {
  axes: {
    templates: ['multi_ma_crossover', 'bollinger_breakout', 'ema_rsi_reversal'],
    symbols: ['BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'BNB/USDT'],
    timeframes: ['4h', '1d'],
    directions: ['long', 'short'],
  },
  raw_total: 48,
  exclusions: {
    'bollinger_breakout|BNB/USDT|1d': { reasons: ['cobertura de candles insuficiente'] },
  },
  excluded_count: 2,
  valid_total: 46,
  limits: { max_total: 1000 },
  errors: {},
  expires_at: '2026-08-15T13:00:00Z',
  snapshot_token: 'snapshot-token-469',
  snapshot_hash: '30422146abcdef30422146abcdef30422146abcdef30422146abcdef30422146',
}

const HISTORY_SWEEP = {
  sweep_id: 'SW-2026-0814-07',
  state: 'completed',
  total: 46,
  succeeded: 44,
  failed: 2,
  skipped: 0,
  processed: 46,
  terminal_reason: null,
  terminal_code: null,
  snapshot: PREFLIGHT,
}

const TEMPLATES = [
  { name: 'multi_ma_crossover', description: 'Médias: tendência', is_readonly: true },
  { name: 'bollinger_breakout', description: 'Bandas: expansão', is_readonly: true },
  { name: 'ema_rsi_reversal', description: 'EMA + RSI', is_readonly: true },
  { name: 'dual_momentum', description: 'ROC duplo', is_readonly: true },
]

const SYMBOLS = [
  'BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'BNB/USDT', 'ADA/USDT', 'XRP/USDT',
  'AVAX/USDT', 'LINK/USDT', 'DOT/USDT', 'ATOM/USDT', 'LTC/USDT', 'DOGE/USDT',
  'UNI/USDT', 'AAVE/USDT', 'NEAR/USDT', 'FIL/USDT',
]

const NAMES = [
  'EMA + RSI · retomada', 'Bandas · impulso', 'Bandas · expansão', 'ROC duplo · aceleração',
  'EMA + RSI · proteção', 'Médias · tendência', 'ROC · defesa', 'Médias · confirmação',
  'Bandas · retorno', 'EMA + RSI · continuação', 'ROC · reversão', 'Médias · baixa amostra',
]

const RESULTS = NAMES.map((name, index) => {
  const lowSample = index === 11
  const duplicate = index === 5
  const symbol = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'BNB/USDT'][index % 4]
  const direction = index % 3 === 0 ? 'short' : 'long'
  return {
    rank: lowSample ? null : index + 1,
    result_id: `RS-${1048 + index}`,
    sweep_id: HISTORY_SWEEP.sweep_id,
    template_id: name,
    symbol,
    timeframe: index % 2 === 0 ? '1d' : '4h',
    direction,
    parameters: index % 2 === 0 ? { ema: 55, rsi: 18 } : { period: 20, deviation: 2.2 },
    calmar_ratio: lowSample ? 3.2 : 2.84 - index * 0.19,
    cagr: 0.384 - index * 0.018,
    benchmark_cagr: 0.205,
    delta_cagr_vs_bh: 17.9 - index * 2.1,
    max_drawdown: 0.135 + index * 0.006,
    sharpe_ratio: 1.62 - index * 0.06,
    profit_factor: 1.91 - index * 0.05,
    win_rate: 0.568 - index * 0.008,
    trades_count: lowSample ? 18 : 44 + index * 3,
    coverage: lowSample ? 0.82 : 0.98 - index * 0.003,
    eligibility: lowSample ? 'low_sample' : 'eligible',
    eligibility_reason: lowSample ? 'mínimo 30 trades e 90% cobertura' : null,
    dedup_state: duplicate ? 'duplicate_favorite' : 'unique',
    dedup_reference: duplicate ? 'ETH Trend D1' : null,
    start_at: '2024-08-14T00:00:00Z',
    end_at: '2026-08-14T00:00:00Z',
    candle_source: 'Binance',
    candle_version: '3',
    expected_candles: 4392,
    observed_valid_candles: 4380,
    fees_slippage: { fees: 0.001, slippage: 0.0005 },
  }
})

const BROWSER_ERRORS = new WeakMap<Page, string[]>()

test.beforeEach(async ({ page }) => {
  const errors: string[] = []
  BROWSER_ERRORS.set(page, errors)
  page.on('console', (message) => {
    if (message.type() === 'error') errors.push(`console: ${message.text()}`)
  })
  page.on('pageerror', (error) => errors.push(`pageerror: ${error.message}`))
})

test.afterEach(async ({ page }) => {
  expect(BROWSER_ERRORS.get(page) ?? []).toEqual([])
})

async function installMocks(page: Page) {
  let activeState = 'running'
  const captured = {
    sweepIdempotencyKey: '',
    promotionIdempotencyKey: '',
  }

  await page.addInitScript((user) => {
    localStorage.setItem('auth_access_token', 'discovery-admin-token')
    localStorage.setItem('auth_refresh_token', 'discovery-admin-refresh')
    localStorage.setItem('auth_user', JSON.stringify(user))
    localStorage.setItem('cripto-farol-onboarding-dismissed', '1')
  }, ADMIN_USER)

  await page.route('**/api/**', (route) =>
    route.fulfill({ status: 200, contentType: 'application/json', body: '{}' }),
  )
  await page.route('**/api/auth/me', (route) =>
    route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(ADMIN_USER) }),
  )
  await page.route('**/api/combos/templates', (route) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ prebuilt: TEMPLATES, examples: [], custom: [] }),
    }),
  )
  await page.route('**/api/exchanges/binance/symbols', (route) =>
    route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ symbols: SYMBOLS }) }),
  )
  await page.route('**/api/combos/discovery/sweeps/preflight', (route) =>
    route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(PREFLIGHT) }),
  )
  await page.route('**/api/combos/discovery/sweeps/history', (route) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        sweeps: [{
          sweep_id: HISTORY_SWEEP.sweep_id,
          state: HISTORY_SWEEP.state,
          total: 46,
          processed: 46,
          succeeded: 44,
          failed: 2,
          skipped: 0,
          snapshot_hash: PREFLIGHT.snapshot_hash,
          created_at: '2026-08-14T14:42:00Z',
        }],
      }),
    }),
  )
  await page.route('**/api/combos/discovery/sweeps/SW-2026-0814-07', (route) =>
    route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(HISTORY_SWEEP) }),
  )
  await page.route('**/api/combos/discovery/sweeps/SW-ACTIVE-469', (route) =>
    {
      const responseState = activeState
      const terminal = responseState === 'cancelled'
      if (responseState === 'cancelling') activeState = 'cancelled'
      return route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        ...HISTORY_SWEEP,
        sweep_id: 'SW-ACTIVE-469',
        state: responseState,
        total: 46,
        processed: terminal ? 46 : 13,
        succeeded: 12,
        failed: 1,
        skipped: terminal ? 33 : 0,
      }),
      })
    },
  )
  await page.route('**/api/combos/discovery/sweeps', async (route) => {
    if (route.request().method() !== 'POST') return route.fallback()
    captured.sweepIdempotencyKey = route.request().postDataJSON().idempotency_key
    return route.fulfill({
      status: 201,
      contentType: 'application/json',
      body: JSON.stringify({ sweep_id: 'SW-ACTIVE-469', state: 'running', total: 46 }),
    })
  })
  await page.route('**/api/combos/discovery/sweeps/SW-ACTIVE-469/pause', (route) => {
    activeState = 'paused'
    return route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ state: 'paused' }) })
  })
  await page.route('**/api/combos/discovery/sweeps/SW-ACTIVE-469/resume', (route) => {
    activeState = 'running'
    return route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ state: 'running' }) })
  })
  await page.route('**/api/combos/discovery/sweeps/SW-ACTIVE-469/cancel', (route) => {
    activeState = 'cancelling'
    return route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ state: 'cancelling' }) })
  })
  await page.route('**/api/combos/discovery/sweeps/*/leaderboard?*', (route) => {
    const url = new URL(route.request().url())
    const symbol = url.searchParams.get('symbol')
    const timeframe = url.searchParams.get('timeframe')
    const direction = url.searchParams.get('direction')
    const offset = Number(url.searchParams.get('offset') || 0)
    const limit = Number(url.searchParams.get('limit') || 10)
    const matched = RESULTS.filter((row) =>
      (!symbol || row.symbol === symbol) &&
      (!timeframe || row.timeframe === timeframe) &&
      (!direction || row.direction === direction),
    )
    return route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        results: matched.slice(offset, offset + limit),
        total: matched.length,
        unfiltered_total: RESULTS.length,
        offset,
        limit,
      }),
    })
  })
  await page.route('**/api/combos/discovery/results/*/promote', (route) => {
    captured.promotionIdempotencyKey = route.request().postDataJSON().idempotency_key
    return route.fulfill({
      status: 201,
      contentType: 'application/json',
      body: JSON.stringify({ favorite_id: 'FT-469', result_id: 'RS-1048' }),
    })
  })

  return captured
}

async function openDiscovery(page: Page) {
  const captured = await installMocks(page)
  await page.goto('/combo/discovery')
  await expect(page.getByRole('heading', { name: 'Descoberta de estratégias swing' })).toBeVisible()
  await expect(page.getByTestId('planned-total')).toHaveText('46')
  await expect(page.getByRole('heading', { name: 'Leaderboard · Calmar' })).toBeVisible()
  await expect(page.getByTestId('result-count')).toContainText('12 de 12 candidatos')
  await expect(page.getByRole('columnheader', { name: 'Buy and Hold', exact: true })).toHaveCount(1)
  await expect(page.getByRole('columnheader', { name: 'Delta versus Buy and Hold', exact: true })).toHaveCount(1)
  await expect(page.getByRole('columnheader', { name: 'Maximum Drawdown', exact: true })).toHaveCount(1)
  await expect(page.getByRole('columnheader', { name: 'Profit Factor', exact: true })).toHaveCount(1)
  await expect(page.getByLabel('Tabela rolável de candidatos')).toHaveAttribute('tabindex', '0')
  await expect(page.getByTestId('critical-state')).toBeVisible()
  return captured
}

test('card 469 — fidelidade visual desktop/mobile', async ({ page }) => {
  await openDiscovery(page)
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= document.documentElement.clientWidth)).toBe(true)
  await expect(page).toHaveScreenshot('discovery-card-469.png', {
    animations: 'disabled',
    caret: 'hide',
    fullPage: true,
  })
})

test('card 469 — fluxo funcional do protótipo', async ({ page }) => {
  const captured = await openDiscovery(page)

  await expect(page.getByTestId('symbol-axis-status')).toContainText('cobertura de candles insuficiente')
  await page.getByTestId('critical-state').selectOption('over-limit')
  await expect(page.getByTestId('critical-panel')).toContainText('Limite excedido')
  await page.getByRole('button', { name: 'Reduzir escopo' }).click()
  await expect(page.getByLabel('Buscar template')).toBeFocused()
  await expect(page.getByTestId('critical-panel')).toContainText('Operação normal')

  const startBox = await page.getByTestId('start-sweep').boundingBox()
  expect(startBox?.height ?? 0).toBeGreaterThanOrEqual(44)

  await page.getByTestId('history-button').click()
  await expect(page.getByTestId('run-selector')).toHaveValue(HISTORY_SWEEP.sweep_id)

  await page.getByTestId('start-sweep').click()
  await expect(page.getByTestId('sweep-progress')).toBeVisible()
  await expect(page.getByTestId('progress-count')).toHaveText('13 de 46')
  await expect(page.getByTestId('active-state-chip')).toHaveText('RUNNING')
  await expect(page.getByTestId('leaderboard-meta')).toContainText(HISTORY_SWEEP.sweep_id)
  expect(captured.sweepIdempotencyKey).toHaveLength(64)
  expect(captured.sweepIdempotencyKey).toBe(`sweep-${PREFLIGHT.snapshot_hash}`.slice(0, 64))

  await page.getByTestId('pause-sweep').click()
  await expect(page.getByTestId('active-state-chip')).toHaveText('PAUSED')

  await page.getByTestId('cancel-sweep').click()
  await expect(page.getByRole('alertdialog')).toBeVisible()
  await page.getByTestId('confirm-cancel').click()
  await expect(page.getByTestId('active-state-chip')).toHaveText('CANCELLING')
  await expect(page.getByTestId('active-state-chip')).toHaveText('CANCELLED', { timeout: 5000 })
  await expect(page.locator('#progress-heading')).toBeFocused()

  await page.getByTestId('new-draft').click()
  await expect(page.locator('#draft-status')).toContainText('Editável')
  await expect(page.getByTestId('sweep-progress')).toBeVisible()

  await page.getByTestId('symbol-filter').selectOption('ETH/USDT')
  await expect(page.getByTestId('result-count')).toContainText('3 de 12 candidatos')
  await page.getByTestId('clear-filters').click()
  await expect(page.getByTestId('result-count')).toContainText('12 de 12 candidatos')
  await page.getByTestId('next-page').click()
  await expect(page.getByTestId('page-label')).toHaveText('Página 2 de 4')
  await expect(page.getByTestId('promote-RS-1053')).toBeDisabled()
  await expect(page.getByTestId('promote-RS-1053')).toHaveText('Já existe')
  await page.getByTestId('next-page').click()
  await page.getByTestId('next-page').click()
  await expect(page.getByTestId('page-label')).toHaveText('Página 4 de 4')
  await expect(page.getByTestId('promote-RS-1059')).toBeDisabled()
  await expect(page.getByTestId('promote-RS-1059')).toHaveText('Baixa amostra')
  await page.getByTestId('prev-page').click()
  await page.getByTestId('prev-page').click()
  await page.getByTestId('prev-page').click()

  await page.getByTestId('promote-RS-1048').click()
  await expect(page.getByRole('dialog', { name: 'Promover a favorito tier 3' })).toBeVisible()
  await expect(page.getByTestId('modal-result')).toHaveText('RS-1048')
  await expect(page.getByText('Tier 3 · observação')).toBeVisible()
  await page.keyboard.press('Escape')
  await expect(page.getByTestId('promote-RS-1048')).toBeFocused()
  await page.getByTestId('promote-RS-1048').click()
  await page.getByTestId('confirm-promotion').click()
  expect(captured.promotionIdempotencyKey).toBe('promote-RS-1048')
  expect(captured.promotionIdempotencyKey.length).toBeLessThanOrEqual(64)
  const promoted = page.locator('[data-promoted-result="RS-1048"]')
  await expect(promoted).toBeVisible()
  await expect(promoted).toBeFocused()
})
