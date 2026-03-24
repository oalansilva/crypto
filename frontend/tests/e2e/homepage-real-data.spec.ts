import { expect, test } from '@playwright/test'

async function blockExternalNetwork(page: any) {
  await page.route('**/*', (route: any) => {
    const url = new URL(route.request().url())
    if (url.hostname === '127.0.0.1' || url.hostname === 'localhost') {
      return route.continue()
    }
    return route.abort('blockedbyclient')
  })
}

async function mockHomeApis(
  page: any,
  opts?: {
    favorites?: unknown[]
    balancesStatus?: number
    balancesBody?: unknown
    changes?: unknown[]
    changeDetails?: Record<string, unknown>
    labRunsStatus?: number
    labRunsBody?: unknown
    marketPricesStatus?: number
    marketPricesBody?: unknown
  },
) {
  const favorites = opts?.favorites ?? [
    {
      id: 11,
      name: 'Breakout Pro',
      symbol: 'BTC/USDT',
      timeframe: '4h',
      strategy_name: 'Breakout Pro',
      metrics: { total_return_pct: 18.4 },
      created_at: '2026-03-24T09:30:00Z',
    },
    {
      id: 12,
      name: 'Fallback sem ROI',
      symbol: 'ETH/USDT',
      timeframe: '1h',
      strategy_name: 'Fallback sem ROI',
      metrics: null,
      created_at: '2026-03-24T10:30:00Z',
    },
  ]

  const changes = opts?.changes ?? [
    {
      id: 'implementa-na-interface-inicial',
      title: 'Implementa na interface inicial',
      card_number: 48,
      path: 'openspec/changes/implementa-na-interface-inicial/proposal.md',
      status: { DEV: 'done', QA: 'pending' },
      archived: false,
      column: 'DEV',
      position: 0,
      item_type: 'change',
    },
  ]

  const balancesBody = opts?.balancesBody ?? {
    balances: [{ asset: 'BTC', total: 0.25, value_usd: 15000 }],
    total_usd: 15000,
    as_of: new Date(Date.now() - 25 * 60_000).toISOString(),
  }

  const changeDetails = opts?.changeDetails ?? {
    'implementa-na-interface-inicial': {
      id: 'wf-48',
      project_id: 'crypto',
      change_id: 'implementa-na-interface-inicial',
      title: 'Implementa na interface inicial',
      description: 'Troca mocks da Home por dados reais.',
      status: 'DEV',
      card_number: 48,
      created_at: '2026-03-23T14:00:00Z',
      updated_at: '2026-03-24T12:40:00Z',
    },
  }

  const labRunsBody = opts?.labRunsBody ?? {
    runs: [
      {
        run_id: 'run-btc-1d',
        status: 'running',
        step: 'execution',
        created_at_ms: Date.parse('2026-03-24T12:15:00Z'),
        updated_at_ms: Date.parse('2026-03-24T12:40:00Z'),
        viewer_url: 'http://127.0.0.1:4173/lab/runs/run-btc-1d',
      },
      {
        run_id: 'run-sol-4h',
        status: 'done',
        step: 'review',
        created_at_ms: Date.parse('2026-03-24T08:00:00Z'),
        updated_at_ms: Date.parse('2026-03-24T08:30:00Z'),
        viewer_url: 'http://127.0.0.1:4173/lab/runs/run-sol-4h',
      },
    ],
  }

  const marketPricesBody = opts?.marketPricesBody ?? {
    prices: [
      { symbol: 'BTCUSDT', price: 65234.12, change_24h_pct: 2.4 },
      { symbol: 'ETHUSDT', price: 3210.5, change_24h_pct: -1.1 },
      { symbol: 'SOLUSDT', price: 145.33, change_24h_pct: 4.8 },
    ],
    fetched_at: '2026-03-24T12:45:00Z',
  }

  await page.route('**/api/health', async (route: any) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ status: 'ok', service: 'crypto-api' }),
    })
  })

  await page.route('**/api/favorites/', async (route: any) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(favorites),
    })
  })

  await page.route('**/api/external/binance/spot/balances', async (route: any) => {
    await route.fulfill({
      status: opts?.balancesStatus ?? 200,
      contentType: 'application/json',
      body: JSON.stringify(balancesBody),
    })
  })

  await page.route('**/api/workflow/kanban/changes?project_slug=crypto', async (route: any) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ items: changes }),
    })
  })

  await page.route('**/api/workflow/projects/crypto/changes/*', async (route: any) => {
    const changeId = decodeURIComponent(route.request().url().split('/').pop() || '')
    const detail = changeDetails[changeId]
    if (!detail) {
      await route.fulfill({ status: 404, contentType: 'application/json', body: JSON.stringify({ detail: 'not found' }) })
      return
    }
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(detail),
    })
  })

  await page.route('**/api/lab/runs?limit=5', async (route: any) => {
    await route.fulfill({
      status: opts?.labRunsStatus ?? 200,
      contentType: 'application/json',
      body: JSON.stringify(labRunsBody),
    })
  })

  await page.route('**/api/market/prices', async (route: any) => {
    await route.fulfill({
      status: opts?.marketPricesStatus ?? 200,
      contentType: 'application/json',
      body: JSON.stringify(marketPricesBody),
    })
  })
}

test('HomePage desktop renders real data and explicit snapshot labels', async ({ page }) => {
  await blockExternalNetwork(page)
  await mockHomeApis(page)

  await page.goto('/')

  await expect(page.getByRole('heading', { name: 'Seu snapshot diário de crypto' })).toBeVisible()
  await expect(page.getByTestId('home-kpi-best-strategy').getByText('Breakout Pro')).toBeVisible()
  await expect(page.getByTestId('home-kpi-best-strategy').getByText(/ROI \+18\.4%/)).toBeVisible()
  await expect(page.getByTestId('home-kpi-freshness').getByText('há 25 min')).toBeVisible()
  await expect(page.getByTestId('home-focus-section').getByText('Implementa na interface inicial')).toBeVisible()
  await expect(page.getByTestId('home-focus-section').getByText('Card #48')).toBeVisible()
  await expect(page.getByTestId('home-runs-section').getByText('run-btc-1d')).toBeVisible()
  await expect(page.getByTestId('home-runs-section').getByText('execution')).toBeVisible()
  await expect(page.getByTestId('home-market-section').getByText('BTCUSDT')).toBeVisible()
  await expect(page.getByTestId('home-market-section').getByText('+2.4%')).toBeVisible()

  await expect(page.getByText('valor ilustrativo').first()).toBeVisible()
})

test('HomePage mobile shows empty and error fallbacks without blank sections', async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 })
  await blockExternalNetwork(page)
  await mockHomeApis(page, {
    favorites: [],
    balancesStatus: 500,
    balancesBody: { detail: 'boom' },
    changes: [],
    changeDetails: {},
    labRunsBody: { runs: [] },
    marketPricesBody: { prices: [], fetched_at: null },
  })

  await page.goto('/')

  await expect(page.getByTestId('home-kpi-best-strategy').getByText('Nenhuma estratégia favoritada')).toBeVisible()
  await expect(page.getByTestId('home-kpi-freshness').getByText('não disponível')).toBeVisible()
  await expect(page.getByTestId('home-focus-section').getByText('Nenhuma mudança ativa no momento')).toBeVisible()
  await expect(page.getByTestId('home-runs-section').getByText('Nenhuma run recente encontrada.')).toBeVisible()
  await expect(page.getByTestId('home-market-section').getByText('Nenhum preço disponível agora.')).toBeVisible()
})
