import { expect, test, type Page } from '@playwright/test'

const ADMIN_USER = {
  id: 'discovery-admin',
  email: 'alan@example.com',
  name: 'Alan Silva',
  isAdmin: true,
  mustChangePassword: false,
}

const SNAPSHOT = {
  axes: {
    templates: ['multi_ma_crossover'],
    symbols: ['BTC/USDT'],
    timeframes: ['1d'],
    directions: ['long'],
  },
  raw_total: 1,
  exclusions: {},
  excluded_count: 0,
  valid_total: 1,
  limits: { max_total: 1000 },
  errors: {},
  expires_at: '2026-09-16T20:00:00Z',
  snapshot_token: 'snapshot-token-954',
  snapshot_hash: '954abcdef954abcdef954abcdef954abcdef954abcdef954abcdef954abcdef',
  period_type: 'all',
  start_date: '2017-01-01',
  end_date: '2026-09-16',
}

const ACTIVE_ID = '00e9a4d28e114099bc18fc85d5500df3'
const HISTORY_ID = 'cc5e54036a814b0491fc3ec54cb51d22'
const CANDIDATE_ID = 'RS-263BF9A075'

const TEMPLATES = [
  {
    name: 'multi_ma_crossover',
    display_name: 'Médias Móveis: Tendência em Virada',
    description: 'Cruzamento de médias para swing.',
    is_readonly: true,
  },
]

function row(partial: Record<string, unknown>) {
  return {
    template_id: 'multi_ma_crossover',
    display_name: 'Médias Móveis: Tendência em Virada',
    description: 'Cruzamento de médias para swing.',
    timeframe: '1d',
    direction: 'long',
    parameters: { ema_short: 9 },
    cagr: 0.013,
    benchmark_cagr: null,
    delta_cagr_vs_bh: null,
    sharpe_ratio: 0.42,
    profit_factor: 1.1,
    win_rate: 0.48,
    coverage: 1,
    eligibility: 'eligible',
    eligibility_reason: null,
    dedup_state: 'already_promoted',
    dedup_reference: null,
    start_at: '2017-01-01T00:00:00Z',
    end_at: '2026-09-16T00:00:00Z',
    candle_source: 'ccxt',
    candle_version: null,
    expected_candles: 3500,
    observed_valid_candles: 3400,
    fees_slippage: { fees: 0.001, slippage: 0.0005 },
    oos_verdict: { status: 'NO-GO', reasons: ['Sharpe abaixo do limiar'] },
    ...partial,
  }
}

const CANDIDATE_ROW = row({
  rank: 1,
  result_id: CANDIDATE_ID,
  symbol: 'BTC/USDT',
  calmar_ratio: 0.19,
  max_drawdown: 0.085,
  trades_count: 30,
})

async function installMocks(page: Page) {
  let sweepPolls = 0
  let partialPolls = 0

  const runningStale = {
    sweep_id: ACTIVE_ID,
    state: 'running',
    total: 1,
    succeeded: 0,
    failed: 0,
    skipped: 0,
    insufficient_sample: 0,
    processed: 0,
    terminal_reason: null,
    terminal_code: null,
    draft_key: 'draft-954',
    snapshot: SNAPSHOT,
    updated_at: '2026-09-16T17:38:00Z',
  }

  const runningFresh = {
    ...runningStale,
    succeeded: 1,
    processed: 1,
    updated_at: '2026-09-16T17:39:00Z',
  }

  const completed = {
    ...runningFresh,
    state: 'completed',
    updated_at: '2026-09-16T17:39:20Z',
    terminal_reason: 'done',
    terminal_code: null,
  }

  const historyRun = {
    sweep_id: HISTORY_ID,
    state: 'completed',
    total: 12,
    succeeded: 12,
    processed: 12,
    label: 'RS-C100CF418A',
    updated_at: '2026-09-16T12:00:00Z',
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
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ symbols: ['BTC/USDT'] }),
    }),
  )
  await page.route('**/api/combos/discovery/sweeps/preflight', (route) =>
    route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(SNAPSHOT) }),
  )
  await page.route('**/api/combos/discovery/sweeps/active', (route) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ sweeps: [runningStale] }),
    }),
  )
  await page.route('**/api/combos/discovery/sweeps/history', (route) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ sweeps: [historyRun] }),
    }),
  )
  await page.route(`**/api/combos/discovery/sweeps/${HISTORY_ID}`, (route) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        ...historyRun,
        failed: 0,
        skipped: 0,
        snapshot: SNAPSHOT,
      }),
    }),
  )
  await page.route(`**/api/combos/discovery/sweeps/${ACTIVE_ID}`, (route) => {
    sweepPolls += 1
    const body = sweepPolls >= 3 ? completed : runningFresh
    return route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(body) })
  })
  await page.route('**/api/combos/discovery/sweeps/*/leaderboard?*', (route) => {
    const url = new URL(route.request().url())
    const exclude = url.searchParams.get('exclude_eligibility')
    const sweepMatch = url.pathname.match(/\/sweeps\/([^/]+)\/leaderboard/)
    const sweepId = sweepMatch?.[1] ?? ''
    if (exclude === 'insufficient_sample' && sweepId === ACTIVE_ID) {
      partialPolls += 1
      const results = partialPolls >= 2 ? [CANDIDATE_ROW] : []
      return route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ results, total: results.length, unfiltered_total: results.length, offset: 0, limit: 5 }),
      })
    }
    const results = sweepId === ACTIVE_ID ? [CANDIDATE_ROW] : []
    return route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        results,
        total: results.length,
        unfiltered_total: results.length,
        offset: 0,
        limit: 10,
      }),
    })
  })
}

const VIEWPORTS = [
  { name: 'desktop', width: 1440, height: 900 },
  { name: 'mobile', width: 390, height: 844 },
] as const

const PROTO_LANDMARKS = [
  'Descoberta de estratégias swing',
  'Preflight',
  'Rascunho de varredura',
] as const

for (const viewport of VIEWPORTS) {
  test(`card 954 — ${viewport.name} poll parciais e fecho Decidir desta vs proto`, async ({ page }) => {
    await page.setViewportSize({ width: viewport.width, height: viewport.height })
    await installMocks(page)
    await page.goto('/combo/discovery')

    for (const landmark of PROTO_LANDMARKS) {
      if (landmark === 'Preflight' || landmark === 'Rascunho de varredura') {
        await page.getByRole('tab', { name: 'Montar' }).click()
      }
      await expect(page.getByText(landmark, { exact: false }).first()).toBeVisible()
      if (landmark !== 'Descoberta de estratégias swing') {
        await page.getByRole('tab', { name: /Acompanhando/ }).click()
      }
    }

    await expect(page.getByTestId('mode-acomp')).toBeVisible()
    await expect(page.getByTestId('active-state-chip')).toHaveText('EM CURSO')

    await expect.poll(() => page.getByTestId('progress-count').innerText(), { timeout: 8000 }).toBe('1 de 1')

    await page.getByTestId('history-button').click()
    await page.getByTestId('run-selector').selectOption(HISTORY_ID)
    await expect(page.getByTestId('mode-decidir')).toBeVisible()
    await expect(page.getByTestId('leaderboard-meta')).toContainText(HISTORY_ID)
    await page.getByRole('tab', { name: /Acompanhando/ }).click()
    await expect(page.getByTestId('mode-acomp')).toBeVisible()
    await expect(page.getByTestId('sweep-progress')).toContainText(ACTIVE_ID)
    await expect(page.getByTestId('active-state-chip')).toHaveText('EM CURSO')
    await expect(page.getByTestId('partial-go-1')).toBeVisible()
    await expect(page.getByTestId('partials-table')).toContainText('BTC/USDT')
    await expect(page.getByText('Parciais ainda carregando')).toHaveCount(0)

    await expect.poll(async () => page.getByTestId('mode-decidir').isVisible(), { timeout: 10000 }).toBe(true)
    await expect(page.getByTestId('mode-acomp')).toHaveCount(0)
    await expect(page.getByTestId('leaderboard-meta')).toContainText(ACTIVE_ID)
    await expect(page.getByTestId('decidir-table')).toContainText(CANDIDATE_ID)
    await expect(page.getByTestId('decidir-table')).toContainText('Favorito tier 3')
    await expect(page.getByText('Acompanhar já concluída')).toHaveCount(0)
    await expect(page.getByTestId('active-state-chip')).toHaveCount(0)
  })
}
