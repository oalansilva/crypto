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
    symbols: ['ALPHA/USDT', 'ARPA/USDT', 'ETH/USDT', 'ADA/USDT'],
    timeframes: ['1d'],
    directions: ['long'],
  },
  raw_total: 8,
  exclusions: {},
  excluded_count: 0,
  valid_total: 8,
  limits: { max_total: 1000 },
  errors: {},
  expires_at: '2026-09-12T13:00:00Z',
  snapshot_token: 'snapshot-token-944',
  snapshot_hash: '944abcdef944abcdef944abcdef944abcdef944abcdef944abcdef944abcdef',
  period_type: 'all',
  start_date: '2017-01-01',
  end_date: '2026-09-08',
}

const ACTIVE = {
  sweep_id: 'c944names',
  state: 'running',
  total: 697,
  succeeded: 292,
  failed: 0,
  skipped: 0,
  insufficient_sample: 17,
  processed: 309,
  terminal_reason: null,
  terminal_code: null,
  draft_key: 'draft-944',
  snapshot: SNAPSHOT,
  updated_at: '2026-09-12T12:00:00Z',
}

const TEMPLATES = [
  {
    name: 'multi_ma_crossover',
    display_name: 'Médias Móveis: Tendência em Virada 1',
    description: 'Compara médias de velocidades diferentes.',
    is_readonly: true,
  },
]

const VISIBLE_HEADERS = [
  'Sharpe',
  'Trades',
  'Win%',
  'Return',
  'Max DD',
  'Calmar',
  'CAGR anualizado',
] as const

function row(partial: Record<string, unknown>) {
  return {
    template_id: 'multi_ma_crossover',
    display_name: 'Médias Móveis: Tendência em Virada 1',
    description: 'Compara médias de velocidades diferentes.',
    timeframe: '1d',
    direction: 'long',
    parameters: { ema_short: 8 },
    benchmark_cagr: 0.084,
    delta_cagr_vs_bh: -0.047,
    profit_factor: 1.12,
    eligibility_reason: null,
    dedup_state: 'unique',
    dedup_reference: null,
    start_at: '2020-10-09T00:00:00Z',
    end_at: '2024-01-31T00:00:00Z',
    candle_source: 'ccxt',
    candle_version: null,
    expected_candles: 1209,
    observed_valid_candles: 1210,
    fees_slippage: { fees: 0.001, slippage: 0.001 },
    oos_verdict: { status: 'NO-GO' },
    ...partial,
  }
}

const PARTIAL_TOP5 = [
  row({
    rank: 1,
    result_id: 'RS-B109ED2C80',
    symbol: 'ALPHA/USDT',
    calmar_ratio: 22.53,
    max_drawdown: 0.165,
    trades_count: 30,
    coverage: 1,
    sharpe_ratio: 0.31,
    win_rate: 0.467,
    cagr: 0.037,
    total_return: 0.128,
    total_return_pct: 12.8,
    eligibility: 'eligible',
  }),
  row({
    rank: 2,
    result_id: 'RS-944-02',
    symbol: 'ARPA/USDT',
    calmar_ratio: 19.03,
    max_drawdown: 0.085,
    trades_count: 30,
    coverage: 1,
    sharpe_ratio: 0.59,
    win_rate: 0.633,
    cagr: 0.016,
    total_return: 0.054,
    total_return_pct: 5.4,
    eligibility: 'eligible',
  }),
  row({
    rank: 3,
    result_id: 'RS-944-03',
    symbol: 'CFX/USDT',
    calmar_ratio: 16.9,
    max_drawdown: 0.075,
    trades_count: 40,
    coverage: 1,
    sharpe_ratio: 0.36,
    win_rate: 0.175,
    cagr: 0.013,
    total_return: 0.044,
    total_return_pct: 4.4,
    eligibility: 'eligible',
  }),
  row({
    rank: 4,
    result_id: 'RS-944-04',
    symbol: 'CRV/USDT',
    calmar_ratio: 13.78,
    max_drawdown: 0.075,
    trades_count: 46,
    coverage: 1,
    sharpe_ratio: 0.41,
    win_rate: 0.489,
    cagr: 0.011,
    total_return: 0.037,
    total_return_pct: 3.7,
    eligibility: 'eligible',
  }),
  row({
    rank: 5,
    result_id: 'RS-944-ETH',
    symbol: 'ETH/USDT',
    calmar_ratio: 12.93,
    max_drawdown: 0.108,
    trades_count: 60,
    coverage: 1,
    sharpe_ratio: 0.88,
    win_rate: 0.491,
    cagr: 0.01,
    eligibility: 'eligible',
  }),
]

const LEADERBOARD = [
  ...PARTIAL_TOP5,
  row({
    rank: null,
    result_id: 'RS-944-INS',
    symbol: 'ADA/USDT',
    calmar_ratio: 4.2,
    max_drawdown: 0.1,
    trades_count: 12,
    coverage: 0.4,
    sharpe_ratio: 0.2,
    win_rate: 0.5,
    cagr: 0.09,
    total_return: 0.22,
    total_return_pct: 22,
    eligibility: 'insufficient_sample',
    eligibility_reason: 'treino 18 < mínimo 30',
    oos_verdict: null,
  }),
]

async function installMocks(page: Page) {
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
      body: JSON.stringify({ symbols: SNAPSHOT.axes.symbols }),
    }),
  )
  await page.route('**/api/combos/discovery/sweeps/preflight', (route) =>
    route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(SNAPSHOT) }),
  )
  await page.route('**/api/combos/discovery/sweeps/active', (route) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ sweeps: [ACTIVE] }),
    }),
  )
  await page.route('**/api/combos/discovery/sweeps/history', (route) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ sweeps: [] }),
    }),
  )
  await page.route('**/api/combos/discovery/sweeps/c944names', (route) =>
    route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(ACTIVE) }),
  )
  await page.route('**/api/combos/discovery/sweeps/*/leaderboard?*', (route) => {
    const url = new URL(route.request().url())
    const exclude = url.searchParams.get('exclude_eligibility')
    const offset = Number(url.searchParams.get('offset') || 0)
    const limit = Number(url.searchParams.get('limit') || 10)
    const matched = LEADERBOARD.filter((item) => item.eligibility !== exclude)
    return route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        results: matched.slice(offset, offset + limit),
        total: matched.length,
        unfiltered_total: LEADERBOARD.length,
        offset,
        limit,
      }),
    })
  })
}

async function visibleMetricHeaders(table: ReturnType<Page['getByTestId']>) {
  return table.locator('thead th').evaluateAll((nodes) =>
    nodes.slice(2, -1).map((th) => {
      const labeled = th.querySelector('span:not(.th-hint)')
      const text = labeled?.textContent || th.textContent || ''
      return text.replace(/\s+/g, ' ').trim()
    }),
  )
}

const VIEWPORTS = [
  { name: 'desktop', width: 1440, height: 900 },
  { name: 'mobile', width: 390, height: 844 },
] as const

for (const viewport of VIEWPORTS) {
  test(`card 944 — ${viewport.name} nomes e ordem iguais a Favoritos vs proto`, async ({ page }) => {
    await page.setViewportSize({ width: viewport.width, height: viewport.height })
    await installMocks(page)
    await page.goto('/combo/discovery')

    await expect(page.getByRole('heading', { name: 'Descoberta de estratégias swing' })).toBeVisible()
    await expect(page.getByRole('tab', { name: /Acompanhando/ })).toHaveAttribute('aria-selected', 'true')

    const partials = page.getByTestId('partials-table')
    await expect(partials).toBeVisible()
    expect(await visibleMetricHeaders(partials)).toEqual([...VISIBLE_HEADERS])
    await expect(partials.getByRole('columnheader', { name: 'Trades/cobertura' })).toHaveCount(0)
    await expect(partials.getByRole('button', { name: '+ detalhes' })).toHaveCount(0)

    await expect(partials.getByTestId('partial-sharpe-1')).toHaveText('0,31')
    await expect(partials.getByTestId('partial-return-1')).toHaveText('+12,8%')
    await expect(partials.getByTestId('partial-return-1')).not.toHaveText('3,7%')
    const alphaPartial = partials.locator('tbody tr').filter({ hasText: 'ALPHA/USDT' })
    await expect(alphaPartial.locator('td[data-label="CAGR anualizado"]')).toHaveText('3,7%')
    await expect(alphaPartial.locator('td[data-label="Trades"]')).toContainText('30')
    await expect(alphaPartial.locator('td[data-label="Trades"]')).toContainText('100% velas')
    await expect(alphaPartial.locator('td[data-label="Win%"]')).toHaveText('46,7%')
    await expect(alphaPartial.locator('td[data-label="Max DD"]')).toHaveText('−16,5%')
    await expect(alphaPartial.locator('td[data-label="Calmar"]')).toHaveText('22,53')

    const ethPartial = partials.locator('tbody tr').filter({ hasText: 'ETH/USDT' })
    await expect(ethPartial.locator('td[data-label="Return"]')).toHaveText('N/A')
    await expect(ethPartial.locator('td[data-label="CAGR anualizado"]')).not.toHaveText('N/A')
    await expect(ethPartial.locator('td[data-label="CAGR anualizado"]')).not.toHaveText(
      await ethPartial.locator('td[data-label="Return"]').innerText(),
    )

    const partialLabels = await alphaPartial.locator('td[data-label]').evaluateAll((nodes) =>
      nodes.map((node) => node.getAttribute('data-label')),
    )
    expect(partialLabels).toEqual(['Rank', 'Candidato', ...VISIBLE_HEADERS, 'Ação'])
    await expect(alphaPartial.locator('td[data-label="Win rate"]')).toHaveCount(0)
    await expect(alphaPartial.locator('td[data-label="Maximum Drawdown"]')).toHaveCount(0)

    await page.getByRole('tab', { name: 'Montar' }).click()
    await expect(page.getByRole('heading', { name: 'Preflight' })).toBeVisible()
    await expect(page.getByRole('heading', { name: 'Rascunho de varredura' })).toBeVisible()
    await expect(page.getByTestId('partials-table')).toHaveCount(0)
    await expect(page.getByTestId('decidir-table')).toHaveCount(0)

    await page.getByRole('tab', { name: 'Decidir' }).click()
    const decidir = page.getByTestId('decidir-table')
    await expect(decidir).toBeVisible()
    expect(await visibleMetricHeaders(decidir)).toEqual([...VISIBLE_HEADERS])

    const sort = page.getByTestId('sort-filter')
    await expect(sort.locator('option')).toHaveText(['Calmar', 'CAGR vs B&H'])
    await expect(sort.locator('option')).toHaveCount(2)
    const sortLabels = await sort.locator('option').allTextContents()
    expect(sortLabels.join(' ')).not.toMatch(/Sharpe|Win%|Return|CAGR anualizado/)

    await expect(decidir.getByTestId('decidir-return-1')).toHaveText('+12,8%')
    await expect(decidir.getByTestId('decidir-cagr-1')).toHaveText('3,7%')
    await expect(decidir.getByTestId('decidir-return-1')).not.toHaveText(
      await decidir.getByTestId('decidir-cagr-1').innerText(),
    )
    await expect(page.getByText('+16.951%')).toHaveCount(0)
    await expect(page.getByText('+16951')).toHaveCount(0)

    const insufficient = page.getByTestId('row-insufficient')
    await expect(insufficient).toBeVisible()
    await expect(insufficient.getByTestId('seal-insufficient')).toHaveText('Amostra insuficiente')
    for (const label of VISIBLE_HEADERS) {
      await expect(insufficient.locator(`td[data-label="${label}"]`)).toHaveText('N/A')
    }
    await expect(insufficient.locator('td.na')).toHaveCount(7)
    await expect(insufficient.getByRole('button', { name: 'Promover' })).toHaveCount(0)

    await page.getByTestId('expand-RS-B109ED2C80').click()
    const details = page.getByTestId('details-RS-B109ED2C80')
    await expect(details).toContainText('B&H')
    await expect(details).toContainText('Δ')
    await expect(details).toContainText('PF')
    await expect(details).toContainText('janela')
    await expect(details).not.toContainText('Sharpe')
    await expect(details).not.toContainText('Win%')
    await expect(details).not.toContainText('Return')
    await expect(details).not.toContainText('CAGR anualizado')

    await expect(page.getByTestId('column-copy')).toContainText('Ordem igual a Favoritos')
    await expect(page.getByText('Trades/cobertura')).toHaveCount(0)

    const decidirLabels = await decidir.locator('tbody tr').first().locator('td[data-label]').evaluateAll((nodes) =>
      nodes.map((node) => node.getAttribute('data-label')),
    )
    expect(decidirLabels).toEqual(['Rank global', 'Candidato', ...VISIBLE_HEADERS, 'Ação'])
  })
}
