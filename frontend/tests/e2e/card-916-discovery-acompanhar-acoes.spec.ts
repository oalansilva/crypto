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
    symbols: ['ARPA/USDT', 'CFX/USDT', 'CRV/USDT', 'ETH/USDT', 'DOT/USDT'],
    timeframes: ['1d'],
    directions: ['long'],
  },
  raw_total: 5,
  exclusions: {},
  excluded_count: 0,
  valid_total: 5,
  limits: { max_total: 1000 },
  errors: {},
  expires_at: '2026-09-11T13:00:00Z',
  snapshot_token: 'snapshot-token-916',
  snapshot_hash: '916abcdef916abcdef916abcdef916abcdef916abcdef916abcdef916abcdef',
  period_type: 'all',
  start_date: '2017-01-01',
  end_date: '2026-09-08',
}

const ACTIVE = {
  sweep_id: '3d9bee8b4e4341eb8fcb0b60644a0579',
  state: 'running',
  total: 697,
  succeeded: 280,
  failed: 2,
  skipped: 0,
  insufficient_sample: 6,
  processed: 309,
  terminal_reason: null,
  terminal_code: null,
  draft_key: 'draft-916',
  snapshot: SNAPSHOT,
  updated_at: '2026-09-11T12:00:00Z',
}

const TEMPLATES = [
  {
    name: 'multi_ma_crossover',
    display_name: 'Médias Móveis: Tendência em Virada 1',
    description: 'Cruzamento de médias para swing.',
    is_readonly: true,
  },
]

function row(partial: Record<string, unknown>) {
  return {
    template_id: 'multi_ma_crossover',
    display_name: 'Médias Móveis: Tendência em Virada 1',
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
    eligibility_reason: null,
    dedup_state: 'unique',
    dedup_reference: null,
    start_at: '2017-01-01T00:00:00Z',
    end_at: '2026-09-08T00:00:00Z',
    candle_source: 'ccxt',
    candle_version: null,
    expected_candles: 3500,
    observed_valid_candles: 3400,
    fees_slippage: { fees: 0.001, slippage: 0.0005 },
    oos_verdict: { status: 'NO-GO', reasons: ['Sharpe abaixo do limiar'] },
    ...partial,
  }
}

function buildResults() {
  return [
    row({ rank: 1, result_id: 'RS-916-ARPA', symbol: 'ARPA/USDT', calmar_ratio: 0.19, max_drawdown: 0.085, trades_count: 30 }),
    row({ rank: 2, result_id: 'RS-916-CFX', symbol: 'CFX/USDT', calmar_ratio: 0.17, max_drawdown: 0.075, trades_count: 40 }),
    row({ rank: 3, result_id: 'RS-916-CRV', symbol: 'CRV/USDT', calmar_ratio: 0.15, max_drawdown: 0.075, trades_count: 46 }),
    row({ rank: 4, result_id: 'RS-916-ETH', symbol: 'ETH/USDT', calmar_ratio: 0.09, max_drawdown: 0.108, trades_count: 60 }),
    row({ rank: 5, result_id: 'RS-916-DOT', symbol: 'DOT/USDT', calmar_ratio: 0.1, max_drawdown: 0.092, trades_count: 38 }),
    row({
      rank: 6,
      result_id: 'RS-916-NEXT',
      symbol: 'ADA/USDT',
      calmar_ratio: 0.08,
      max_drawdown: 0.1,
      trades_count: 35,
    }),
  ]
}

async function installMocks(page: Page, opts?: { promoteReject?: boolean }) {
  let results = buildResults()
  const captured = { discarded: '', promoted: '' }

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
      body: JSON.stringify({ sweeps: [ACTIVE] }),
    }),
  )
  await page.route(`**/api/combos/discovery/sweeps/${ACTIVE.sweep_id}`, (route) =>
    route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(ACTIVE) }),
  )
  await page.route('**/api/combos/discovery/sweeps/*/leaderboard?*', (route) => {
    const url = new URL(route.request().url())
    const exclude = url.searchParams.get('exclude_eligibility')
    const offset = Number(url.searchParams.get('offset') || 0)
    const limit = Number(url.searchParams.get('limit') || 10)
    const matched = results.filter((item) => item.eligibility !== exclude)
    return route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        results: matched.slice(offset, offset + limit),
        total: matched.length,
        unfiltered_total: results.length,
        offset,
        limit,
      }),
    })
  })
  await page.route('**/api/combos/discovery/results/*/promote', (route) => {
    if (opts?.promoteReject) {
      return route.fulfill({
        status: 400,
        contentType: 'application/json',
        body: JSON.stringify({ detail: 'Não é possível promover com a varredura em execução' }),
      })
    }
    const id = route.request().url().split('/results/')[1]?.split('/')[0] ?? ''
    captured.promoted = id
    results = results.map((r) =>
      r.result_id === id ? { ...r, dedup_state: 'already_promoted', dedup_reference: 'FAV-916' } : r,
    )
    return route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ favorite_id: 'FAV-916' }),
    })
  })
  await page.route('**/api/combos/discovery/results/*/discard', (route) => {
    const id = route.request().url().split('/results/')[1]?.split('/')[0] ?? ''
    captured.discarded = id
    results = results.filter((r) => r.result_id !== id)
    return route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ ok: true }) })
  })

  return captured
}

const VIEWPORTS = [
  { name: 'desktop', width: 1440, height: 900 },
  { name: 'mobile', width: 390, height: 844 },
] as const

for (const viewport of VIEWPORTS) {
  test(`card 916 — ${viewport.name} parciais Promover/Excluir vs proto`, async ({ page }) => {
    await page.setViewportSize({ width: viewport.width, height: viewport.height })
    const captured = await installMocks(page)
    await page.goto('/combo/discovery')

    await expect(page.getByRole('heading', { name: 'Descoberta de estratégias swing' })).toBeVisible()
    await expect(page.getByRole('tab', { name: /Acompanhando/ })).toHaveAttribute('aria-selected', 'true')

    const partials = page.getByTestId('partials-table')
    await expect(partials).toBeVisible()
    await expect(partials.getByRole('columnheader', { name: 'Ação' })).toBeVisible()
    await expect(partials.locator('tbody tr')).toHaveCount(5)

    const cfxRow = partials.locator('tbody tr').filter({ hasText: 'CFX/USDT' })
    await expect(cfxRow).toHaveAttribute('data-verdict', 'NO-GO')
    await expect(cfxRow.getByTestId('seal-nogo')).toBeVisible()
    await expect(cfxRow.getByTestId('promote-RS-916-CFX')).toBeEnabled()
    await expect(cfxRow.getByTestId('discard-RS-916-CFX')).toBeVisible()

    await cfxRow.getByTestId('promote-RS-916-CFX').click()
    await expect(page.getByRole('dialog', { name: 'Promover a favorito tier 3' })).toBeVisible()
    await expect(page.getByText('Tier 3 · observação')).toBeVisible()
    await page.keyboard.press('Escape')
    await expect(cfxRow.getByTestId('promote-RS-916-CFX')).toBeFocused()
    await expect(page.getByTestId('progress-count')).toContainText('309 de 697')

    await cfxRow.getByTestId('promote-RS-916-CFX').click()
    await page.getByTestId('confirm-promotion').click()
    expect(captured.promoted).toBe('RS-916-CFX')
    await expect(cfxRow.locator('[data-promoted-result="RS-916-CFX"]')).toBeVisible()
    await expect(cfxRow.getByTestId('discard-RS-916-CFX')).toHaveCount(0)
    await expect(page.getByTestId('progress-count')).toContainText('309 de 697')

    await page.getByRole('tab', { name: 'Decidir' }).click()
    await expect(page.getByTestId('decidir-table')).toBeVisible()
    await expect(page.getByTestId('promote-RS-916-ARPA')).toBeVisible()
    const decidirCfx = page.locator('#panel-decidir tbody tr').filter({ hasText: 'RS-916-CFX' })
    await expect(decidirCfx.locator('[data-promoted-result="RS-916-CFX"]')).toBeVisible()

    await page.getByRole('tab', { name: /Acompanhando/ }).click()
    await partials.locator('tbody tr').filter({ hasText: 'ARPA/USDT' }).getByTestId('discard-RS-916-ARPA').click()
    await expect(page.getByRole('dialog', { name: 'Excluir resultado' })).toBeVisible()
    await page.getByTestId('confirm-discard').click()
    expect(captured.discarded).toBe('RS-916-ARPA')
    await expect(partials.locator('tbody tr').filter({ hasText: 'ARPA/USDT' })).toHaveCount(0)
    await expect(partials.locator('tbody tr')).toHaveCount(5)

    await page.getByRole('tab', { name: 'Decidir' }).click()
    await expect(page.locator('#panel-decidir tbody tr').filter({ hasText: 'RS-916-ARPA' })).toHaveCount(0)

    await page.getByRole('tab', { name: 'Montar' }).click()
    await expect(page.getByRole('heading', { name: 'Preflight' })).toBeVisible()
    await expect(page.getByRole('heading', { name: 'Rascunho de varredura' })).toBeVisible()
    await expect(page.getByTestId('partials-table')).toHaveCount(0)
  })
}

test('card 916 — POST recusado mostra erro visível', async ({ page }) => {
  await page.setViewportSize({ width: 1440, height: 900 })
  await installMocks(page, { promoteReject: true })
  await page.goto('/combo/discovery')
  const partials = page.getByTestId('partials-table')
  await partials.getByTestId('promote-RS-916-CFX').click()
  await page.getByTestId('confirm-promotion').click()
  await expect(page.getByText('Falha na promoção')).toBeVisible()
})
