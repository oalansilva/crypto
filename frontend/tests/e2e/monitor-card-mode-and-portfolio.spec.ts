import { expect, test } from '@playwright/test'

const AUTH_USER = {
  id: 'test-user',
  email: 'test@example.com',
  name: 'Test User',
  isAdmin: false,
}

const ADMIN_USER = {
  ...AUTH_USER,
  isAdmin: true,
}

async function mockAuthenticatedSession(page: any, user = AUTH_USER) {
  await page.addInitScript((user) => {
    window.localStorage.setItem('auth_access_token', 'test-access-token')
    window.localStorage.setItem('auth_refresh_token', 'test-refresh-token')
    window.localStorage.setItem('auth_user', JSON.stringify(user))
  }, user)
}

const FAVORITES_PAYLOAD = [
  {
    id: 1,
    name: 'BTC Trend',
    symbol: 'BTC/USDT',
    timeframe: '4h',
    strategy_name: 'ema_rsi',
    parameters: {},
    metrics: {},
    created_at: '2025-01-01T00:00:00Z',
    tier: 1,
  },
  {
    id: 2,
    name: 'ETH Trend',
    symbol: 'ETH/USDT',
    timeframe: '1d',
    strategy_name: 'ema_rsi',
    parameters: {},
    metrics: {},
    created_at: '2025-01-01T00:00:00Z',
    tier: 2,
  },
]

const OPPORTUNITIES_PAYLOAD = [
  {
    id: 1,
    symbol: 'BTC/USDT',
    asset_type: 'cryptomoeda',
    timeframe: '4h',
    template_name: 'ema_rsi',
    name: 'BTC Trend',
    notes: '',
    tier: 1,
    parameters: { ema_short: 9, ema_long: 21 },
    is_holding: true,
    distance_to_next_status: 0.3,
    next_status_label: 'exit',
    status: 'HOLDING',
    message: 'Holding position',
    last_price: 50000,
    timestamp: '2025-01-01T00:00:00Z',
    details: {},
  },
  {
    id: 2,
    symbol: 'ETH/USDT',
    asset_type: 'cryptomoeda',
    timeframe: '1d',
    template_name: 'ema_rsi',
    name: 'ETH Trend',
    notes: '',
    tier: 2,
    parameters: { ema_short: 9, ema_long: 21 },
    is_holding: false,
    distance_to_next_status: 0.5,
    next_status_label: 're-entry',
    status: 'EXITED',
    message: 'Exit confirmed',
    last_price: 3000,
    timestamp: '2025-01-01T00:00:00Z',
    details: {},
  },
]

function buildCandles() {
  return [
    { timestamp_utc: '2025-01-01T00:00:00Z', open: 100, high: 102, low: 99, close: 101, volume: 1000 },
    { timestamp_utc: '2025-01-01T01:00:00Z', open: 101, high: 103, low: 100, close: 102, volume: 1100 },
    { timestamp_utc: '2025-01-01T02:00:00Z', open: 102, high: 104, low: 101, close: 103, volume: 1200 },
  ]
}

const sleep = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms))

async function setupApiMocks(
  page: any,
  options?: {
    binanceConfigured?: boolean
    candlesDelayMs?: number
    preferencePatchDelayMs?: number
    balances?: Array<{ asset: string; total: number }>
    opportunitiesPayload?: Array<Record<string, unknown>>
    user?: typeof AUTH_USER
    initialPreferences?: Record<
      string,
      { in_portfolio: boolean; card_mode: 'price' | 'strategy'; price_timeframe: '15m' | '1h' | '4h' | '1d' }
    >
    balancesStatus?: number
    balancesDetail?: string
  }
) {
  const sessionUser = options?.user ?? AUTH_USER
  await mockAuthenticatedSession(page, sessionUser)

  const requestedTimeframes: string[] = []
  const requestedOpportunityTiers: string[] = []
  const requestedBalanceMinUsd: string[] = []
  const preferencePatches: Array<{ symbol: string; patch: any }> = []
  const preferences: Record<
    string,
    { in_portfolio: boolean; card_mode: 'price' | 'strategy'; price_timeframe: '15m' | '1h' | '4h' | '1d' }
  > = {
    ...(options?.initialPreferences ?? {
      'BTC/USDT': { in_portfolio: true, card_mode: 'price', price_timeframe: '1d' },
    }),
  }

  await page.route('**/*', (route: any) => {
    const url = new URL(route.request().url())
    if (url.hostname === '127.0.0.1' || url.hostname === 'localhost') {
      return route.continue()
    }
    return route.abort('blockedbyclient')
  })

  await page.route('**/api/favorites/', (route: any) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(FAVORITES_PAYLOAD),
    })
  )

  await page.route('**/api/auth/me', (route: any) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(sessionUser),
    })
  )

  await page.route('**/api/opportunities/**', (route: any) => {
    const url = new URL(route.request().url())
    requestedOpportunityTiers.push(url.searchParams.get('tier') || '')
    return route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(options?.opportunitiesPayload ?? OPPORTUNITIES_PAYLOAD),
    })
  })

  await page.route('**/api/monitor/preferences', (route: any) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(preferences),
    })
  )

  await page.route('**/api/monitor/preferences/*', async (route: any) => {
    const url = new URL(route.request().url())
    const symbol = decodeURIComponent(url.pathname.split('/').pop() || '').trim()
    const patch = route.request().postDataJSON() || {}
    if (options?.preferencePatchDelayMs) {
      await sleep(options.preferencePatchDelayMs)
    }
    const current = preferences[symbol] || { in_portfolio: false, card_mode: 'price', price_timeframe: '1d' }
    const next = {
      in_portfolio: patch.in_portfolio ?? current.in_portfolio,
      card_mode: patch.card_mode ?? current.card_mode,
      price_timeframe: patch.price_timeframe ?? current.price_timeframe,
    }
    preferencePatches.push({ symbol, patch })
    preferences[symbol] = next

    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(next),
    })
  })

  await page.route('**/api/user/binance-credentials', (route: any) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        configured: Boolean(options?.binanceConfigured),
        api_key_masked: options?.binanceConfigured ? 'test****key' : null,
      }),
    })
  )

  await page.route('**/api/external/binance/spot/balances**', (route: any) => {
    const url = new URL(route.request().url())
    requestedBalanceMinUsd.push(url.searchParams.get('min_usd') || '')

    if ((options?.balancesStatus ?? 200) >= 400) {
      return route.fulfill({
        status: options?.balancesStatus ?? 503,
        contentType: 'application/json',
        body: JSON.stringify({
          detail: options?.balancesDetail ?? 'wallet unavailable',
        }),
      })
    }

    return route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        balances: options?.balances ?? [{ asset: 'BTC', total: 0.42 }],
        total_usd: 1000,
        as_of: '2025-01-01T00:00:00Z',
      }),
    })
  })

  await page.route('**/api/market/candles**', (route: any) =>
    {
      const url = new URL(route.request().url())
      requestedTimeframes.push(url.searchParams.get('timeframe') || '')
      return (async () => {
        if (options?.candlesDelayMs) {
          await sleep(options.candlesDelayMs)
        }
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            candles: buildCandles(),
          }),
        })
      })()
    }
  )

  return {
    requestedBalanceMinUsd,
    requestedOpportunityTiers,
    requestedTimeframes,
    preferencePatches,
  }
}

async function expandMonitorRow(page: any, symbolKey: string) {
  const card = page.getByTestId(`monitor-card-${symbolKey}`)
  if (await card.isVisible().catch(() => false)) {
    return
  }
  await page.getByTestId(`monitor-row-${symbolKey}`).click()
  await expect(card).toBeVisible()
}

test('defaults to In Portfolio and hides symbols without preference', async ({ page }) => {
  await setupApiMocks(page)
  await page.goto('/monitor')

  await expect(page.getByTestId('monitor-row-btc-usdt')).toBeVisible()
  await expect(page.getByTestId('monitor-card-btc-usdt')).toHaveCount(0)
  await expandMonitorRow(page, 'btc-usdt')
  await expect(page.getByTestId('monitor-card-btc-usdt')).toBeVisible()
  await expect(page.getByTestId('monitor-card-nvda')).toHaveCount(0)
})

test('monitor hides protected strategy details for common user', async ({ page }) => {
  await setupApiMocks(page, {
    opportunitiesPayload: [
      {
        ...OPPORTUNITIES_PAYLOAD[0],
        template_name: 'Estratégia protegida',
        strategy_display_name: 'EMA RSI',
        is_strategy_protected: true,
        parameters: {},
        indicator_values: null,
        details: {},
        message: 'Aguardando confirmacao do sistema para a proxima decisao.',
      },
    ],
  })
  await page.goto('/monitor')

  await expandMonitorRow(page, 'btc-usdt')
  const card = page.getByTestId('monitor-card-btc-usdt')
  await expect(card).toBeVisible()
  await expect(card.getByText('EMA RSI')).toBeVisible()
  await expect(card.getByText('Parâmetros')).toHaveCount(0)
  await expect(card.getByText('Indicadores')).toHaveCount(0)
  await expect(card.getByText('Protegido')).toHaveCount(0)
  await expect(card.getByText('Oculto')).toHaveCount(0)
  await expect(card.getByText('Exportar')).toHaveCount(0)
  await expect(card.getByText('Reavaliar')).toHaveCount(0)
  await expect(card.getByText('Ver gráfico')).toHaveCount(0)
  await expect(card.getByText('Confirmar gestão')).toHaveCount(0)
  await expect(card.getByTestId('mode-toggle-btc-usdt')).toHaveCount(0)
  await expect(card.getByTestId('timeframe-toggle-btc-usdt-15m')).toHaveCount(0)
  await expect(card.getByTestId('timeframe-toggle-btc-usdt-1h')).toHaveCount(0)
  await expect(card.getByTestId('timeframe-toggle-btc-usdt-4h')).toHaveCount(0)
  await expect(card.getByText('chart 4h')).toBeVisible()
  await expect(card.getByText('ema_rsi')).toHaveCount(0)
  await expect(card.getByText('ema_short')).toHaveCount(0)
})

test('monitor does not expose local favorite controls and keeps tier stars readable', async ({ page }) => {
  const strategyPreferenceRequests: string[] = []
  await setupApiMocks(page, { user: ADMIN_USER })
  await page.route('**/api/monitor/strategy-preferences**', (route: any) => {
    strategyPreferenceRequests.push(route.request().url())
    return route.abort('blockedbyclient')
  })
  await page.goto('/monitor')

  await page.getByTestId('monitor-filter-all').click()
  await expandMonitorRow(page, 'btc-usdt')
  await expect(page.getByTestId('monitor-card-btc-usdt')).toBeVisible()
  await expect(page.getByTestId('monitor-row-eth-usdt')).toBeVisible()
  await expect(page.getByTestId('monitor-filter-favorites')).toHaveCount(0)
  await expect(page.getByTestId('strategy-favorite-toggle-btc-usdt')).toHaveCount(0)
  await expect(page.getByTestId('strategy-favorite-toggle-eth-usdt')).toHaveCount(0)
  await expect(page.getByRole('button', { name: 'Favoritar' })).toHaveCount(0)
  await expect(page.locator('.chip-count')).not.toContainText('favoritos')
  await expect(page.getByTestId('tier-stars-btc-usdt')).toHaveText('★★★')
  await expect(page.getByTestId('tier-stars-eth-usdt')).toHaveText('★★')
  expect(strategyPreferenceRequests).toEqual([])
})

test('monitor shows tier as star classification', async ({ page }) => {
  await setupApiMocks(page)
  await page.goto('/monitor')

  await expect(page.getByTestId('tier-stars-btc-usdt')).toHaveText('★★★')
  await expect(page.getByTestId('tier-stars-eth-usdt')).toHaveText('★★')
})

test('monitor filters opportunities by star classification', async ({ page }) => {
  await setupApiMocks(page)
  await page.goto('/monitor')

  await page.getByTestId('monitor-filter-stars').selectOption('3')
  await expect(page.getByTestId('monitor-row-btc-usdt')).toBeVisible()
  await expect(page.getByTestId('monitor-row-eth-usdt')).toHaveCount(0)

  await page.getByTestId('monitor-filter-stars').selectOption('2')
  await expect(page.getByTestId('monitor-row-eth-usdt')).toBeVisible()
  await expect(page.getByTestId('monitor-row-btc-usdt')).toHaveCount(0)

  await page.getByTestId('monitor-filter-stars').selectOption('all')
  await expect(page.getByTestId('monitor-row-btc-usdt')).toBeVisible()
  await expect(page.getByTestId('monitor-row-eth-usdt')).toBeVisible()
})

test('monitor defaults to rated strategies and hides unstarred opportunities', async ({ page }) => {
  const mocks = await setupApiMocks(page, {
    opportunitiesPayload: [
      {
        ...OPPORTUNITIES_PAYLOAD[0],
        is_holding: true,
        status: 'HOLD',
        message: 'Holding position',
      },
      {
        ...OPPORTUNITIES_PAYLOAD[1],
        id: 3,
        symbol: 'SOL/USDT',
        name: 'SOL Unstarred',
        tier: null,
      },
    ],
  })
  await page.goto('/monitor')

  await expect.poll(() => mocks.requestedOpportunityTiers[0]).toBe('1,2,3')
  await expect(page.getByTestId('monitor-row-btc-usdt')).toBeVisible()
  await expect(page.getByTestId('monitor-row-sol-usdt')).toHaveCount(0)
  await expect(page.getByText('Em posição · Compra')).toBeVisible()
})

test('monitor hides non-actionable Espera and neutral opportunities from main board', async ({ page }) => {
  await setupApiMocks(page, {
    opportunitiesPayload: [
      {
        ...OPPORTUNITIES_PAYLOAD[0],
        id: 10,
        symbol: 'WAIT/USDT',
        name: 'Wait Setup',
        is_holding: false,
        next_status_label: 'entry',
        status: 'WAIT',
        message: 'Waiting for entry',
      },
      {
        ...OPPORTUNITIES_PAYLOAD[1],
        id: 11,
        symbol: 'NEUTRAL/USDT',
        name: 'Neutral Setup',
        is_holding: false,
        next_status_label: 'entry',
        status: 'NEUTRAL',
        message: 'No active signal',
      },
      {
        ...OPPORTUNITIES_PAYLOAD[0],
        id: 12,
        symbol: 'BTC/USDT',
        name: 'BTC Active',
        is_holding: true,
        next_status_label: 'exit',
        status: 'HOLDING',
        message: 'Holding position',
      },
    ],
    initialPreferences: {
      'WAIT/USDT': { in_portfolio: true, card_mode: 'price', price_timeframe: '1d' },
      'NEUTRAL/USDT': { in_portfolio: true, card_mode: 'price', price_timeframe: '1d' },
      'BTC/USDT': { in_portfolio: true, card_mode: 'price', price_timeframe: '1d' },
    },
  })
  await page.goto('/monitor')

  await expect(page.getByTestId('monitor-row-btc-usdt')).toBeVisible()
  await expect(page.getByTestId('monitor-row-wait-usdt')).toHaveCount(0)
  await expect(page.getByTestId('monitor-row-neutral-usdt')).toHaveCount(0)
  await expect(page.getByText('Estado Espera')).toHaveCount(0)
  await expect(page.getByText('Em observação · Espera')).toHaveCount(0)
  await expect(page.locator('.kpis')).not.toContainText('Espera')
})

test('monitor list keeps Compra when price timeframe preference differs from strategy timeframe', async ({ page }) => {
  await setupApiMocks(page, {
    opportunitiesPayload: [
      {
        ...OPPORTUNITIES_PAYLOAD[1],
        is_holding: true,
        status: 'EXIT_NEAR',
        next_status_label: 'exit',
        distance_to_next_status: 0.27,
        message: 'EXIT: Approaching exit',
      },
    ],
    initialPreferences: {
      'ETH/USDT': { in_portfolio: true, card_mode: 'price', price_timeframe: '4h' },
    },
  })
  await page.goto('/monitor')

  const row = page.getByTestId('monitor-row-eth-usdt')
  await expect(row).toBeVisible()
  await expect(row.getByText('Compra')).toBeVisible()
  await expect(page.getByText('Em posição · Compra')).toContainText('(1)')
  await expect(page.getByText('Em saída · Venda')).toContainText('(0)')
})

test('monitor simplifies table columns for common user', async ({ page }) => {
  await setupApiMocks(page)
  await page.goto('/monitor')

  const header = page.locator('table.signals thead tr').first()
  await expect(page.getByText('Binance system')).toHaveCount(0)
  await expect(page.getByText('Binance · live')).toHaveCount(0)
  await expect(header.getByRole('columnheader', { name: 'Distância' })).toHaveCount(0)
  await expect(header.getByRole('columnheader', { name: '7d' })).toHaveCount(0)
  await expect(header.getByRole('columnheader', { name: 'Saída' })).toHaveCount(0)
  await expect(header.getByRole('columnheader', { name: 'Status' })).toHaveCount(1)
  await expect(page.locator('.filterbar').getByRole('button', { name: 'Distância' })).toHaveCount(0)
  await expect(page.locator('.filterbar').getByRole('button', { name: 'Risco' })).toHaveCount(0)
  await expect(page.locator('.filterbar').getByRole('button', { name: 'Par' })).toHaveCount(0)
  await expect(page.getByRole('button', { name: 'Mais' })).toHaveCount(0)
  await expect(page.getByRole('button', { name: 'Abrir gráfico' }).first()).toBeVisible()
  await expect(page.getByRole('button', { name: 'Favoritar' })).toHaveCount(0)
})

test('monitor uses concise common-user row tags', async ({ page }) => {
  await setupApiMocks(page)
  await page.goto('/monitor')

  const row = page.getByTestId('monitor-row-btc-usdt')
  await expect(row.getByText('● Carteira')).toHaveText('● Carteira')
  await expect(row.getByText('Portfolio')).toHaveCount(0)
  await expect(row.getByText('▲ Strategy')).toHaveCount(0)
  await expect(row.getByTestId('tier-stars-btc-usdt')).toHaveText('★★★')
})

test('flags only crypto cards as portfolio-derived when Binance credentials are configured', async ({ page }) => {
  await setupApiMocks(page, { binanceConfigured: true, user: ADMIN_USER })
  await page.goto('/monitor')

  await page.getByTestId('monitor-filter-all').click()
  await expandMonitorRow(page, 'btc-usdt')
  await expandMonitorRow(page, 'eth-usdt')
  await expect(page.getByTestId('monitor-card-btc-usdt')).toHaveAttribute('data-portfolio-derived', 'true')
  await expect(page.getByTestId('monitor-card-eth-usdt')).toHaveAttribute('data-portfolio-derived', 'true')
  await expect(page.getByTestId('portfolio-toggle-btc-usdt')).toBeDisabled()
  await expect(page.getByTestId('portfolio-toggle-btc-usdt')).toHaveAttribute('aria-pressed', 'true')
  await expect(page.getByTestId('portfolio-toggle-eth-usdt')).toBeDisabled()
  await expect(page.getByTestId('portfolio-toggle-eth-usdt')).toHaveAttribute('aria-pressed', 'false')
})

test('uses Binance wallet holdings as the portfolio source for crypto cards', async ({ page }) => {
  const mocks = await setupApiMocks(page, {
    binanceConfigured: true,
    balances: [{ asset: 'BTC', total: 0.42 }],
    initialPreferences: {
      'BTC/USDT': { in_portfolio: false, card_mode: 'price', price_timeframe: '1d' },
    },
  })
  await page.goto('/monitor')

  await expandMonitorRow(page, 'btc-usdt')
  await expect(page.getByTestId('monitor-card-btc-usdt')).toBeVisible()
  await expect(page.getByTestId('portfolio-toggle-btc-usdt')).toHaveAttribute('aria-pressed', 'true')
  await expect(page.getByTestId('portfolio-sync-status-btc-usdt')).toContainText('Sincronizado com a Carteira Binance')
  await expect.poll(() => mocks.requestedBalanceMinUsd.at(-1)).toBe('1')
})

test('toggle in_portfolio persists across reload', async ({ page }) => {
  await setupApiMocks(page, { user: ADMIN_USER })
  await page.goto('/monitor')

  await page.getByTestId('monitor-filter-all').click()
  await expandMonitorRow(page, 'eth-usdt')
  await expect(page.getByTestId('monitor-card-eth-usdt')).toBeVisible()

  await page.getByTestId('portfolio-toggle-eth-usdt').click()
  await page.getByTestId('monitor-filter-in-portfolio').click()
  await expect(page.getByTestId('monitor-card-eth-usdt')).toBeVisible()

  await page.reload()
  await expandMonitorRow(page, 'eth-usdt')
  await expect(page.getByTestId('monitor-card-eth-usdt')).toBeVisible()
})

test('per-card mode toggle persists across reload', async ({ page }) => {
  await setupApiMocks(page, { user: ADMIN_USER })
  await page.goto('/monitor')

  await expandMonitorRow(page, 'btc-usdt')
  await expect(page.getByTestId('mode-label-btc-usdt')).toHaveText('Price')
  await page.getByTestId('mode-toggle-btc-usdt').click()
  await expect(page.getByTestId('mode-label-btc-usdt')).toHaveText('Strategy')

  await page.reload()
  await expandMonitorRow(page, 'btc-usdt')
  await expect(page.getByTestId('mode-label-btc-usdt')).toHaveText('Strategy')
})

test('per-card timeframe selection persists across reload', async ({ page }) => {
  const mocks = await setupApiMocks(page, { user: ADMIN_USER })
  await page.goto('/monitor')

  await expandMonitorRow(page, 'btc-usdt')
  await expect(page.getByTestId('timeframe-toggle-btc-usdt-1d')).toHaveAttribute('aria-pressed', 'true')
  await page.getByTestId('timeframe-toggle-btc-usdt-4h').click()
  await expect(page.getByTestId('timeframe-toggle-btc-usdt-4h')).toHaveAttribute('aria-pressed', 'true')
  await expect.poll(() => mocks.requestedTimeframes.includes('4h')).toBe(true)

  await page.reload()
  await expandMonitorRow(page, 'btc-usdt')
  await expect(page.getByTestId('timeframe-toggle-btc-usdt-4h')).toHaveAttribute('aria-pressed', 'true')
})

test('timeframe switch keeps non-chart controls interactive and shows localized chart loading', async ({ page }) => {
  const mocks = await setupApiMocks(page, { candlesDelayMs: 600, preferencePatchDelayMs: 500, user: ADMIN_USER })
  await page.goto('/monitor')

  await expandMonitorRow(page, 'btc-usdt')
  await page.getByTestId('timeframe-toggle-btc-usdt-4h').click()
  await expect(page.getByTestId('timeframe-toggle-btc-usdt-4h')).toHaveAttribute('aria-pressed', 'true')
  // UI should remain interactive even while candles are fetching.
  await expect(page.getByTestId('portfolio-toggle-btc-usdt')).toBeEnabled()

  await page.getByTestId('portfolio-toggle-btc-usdt').click()
  await expect
    .poll(() =>
      mocks.preferencePatches.some(
        (entry) => entry.symbol === 'BTC/USDT' && entry.patch && entry.patch.in_portfolio === false
      )
    )
    .toBe(true)

  // Ensure there is no global blocking loading text
  await expect(page.locator('body')).not.toContainText('Loading candles...')
})

test('derived crypto portfolio toggle stays read-only and does not persist manual changes', async ({ page }) => {
  const mocks = await setupApiMocks(page, { binanceConfigured: true, user: ADMIN_USER })
  await page.goto('/monitor')

  await page.getByTestId('monitor-filter-all').click()
  await expandMonitorRow(page, 'btc-usdt')
  await expandMonitorRow(page, 'eth-usdt')
  await expect(page.getByTestId('portfolio-toggle-btc-usdt')).toBeDisabled()
  await expect(page.getByTestId('portfolio-toggle-btc-usdt')).toHaveAttribute('aria-pressed', 'true')
  await expect(page.getByTestId('portfolio-toggle-eth-usdt')).toBeDisabled()
  await expect(page.getByTestId('portfolio-toggle-eth-usdt')).toHaveAttribute('aria-pressed', 'false')
  await expect(mocks.preferencePatches).toHaveLength(0)
})

test('shows fallback feedback when Binance wallet is unavailable', async ({ page }) => {
  await setupApiMocks(page, {
    binanceConfigured: true,
    user: ADMIN_USER,
    balancesStatus: 503,
    balancesDetail: 'Binance credentials not configured for this user',
  })
  await page.goto('/monitor')

  await page.getByTestId('monitor-filter-all').click()
  await expandMonitorRow(page, 'btc-usdt')
  await expect(page.getByTestId('portfolio-toggle-btc-usdt')).toBeDisabled()
  await expect(page.getByTestId('portfolio-toggle-btc-usdt')).toHaveAttribute('aria-pressed', 'false')
  await expect(page.getByTestId('portfolio-sync-status-btc-usdt')).toContainText('Binance credentials not configured')
})
