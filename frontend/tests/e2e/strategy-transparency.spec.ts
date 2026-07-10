import { expect, test } from '@playwright/test'

const USER = {
  id: 'common-user',
  email: 'trader@example.com',
  name: 'Trader',
  isAdmin: false,
}

const CANDLES = [
  { timestamp_utc: '2026-07-01T00:00:00Z', open: 100, high: 104, low: 99, close: 103, volume: 1000 },
  { timestamp_utc: '2026-07-02T00:00:00Z', open: 103, high: 106, low: 102, close: 105, volume: 1100 },
  { timestamp_utc: '2026-07-03T00:00:00Z', open: 105, high: 107, low: 103, close: 104, volume: 1200 },
]

const transparency = (timeframe = '1d') => ({
  status: 'available',
  strategy_key: 'ema_rsi',
  display_name: 'EMA + RSI: Retomada de Tendência',
  description: 'Combina direção por EMA e força relativa por RSI para apoiar entradas e saídas.',
  timeframe,
  parameters: { ema_length: 20, rsi_length: 14, stop_loss: 0.02 },
  indicators: [
    {
      key: 'trend',
      type: 'ema',
      label: 'EMA (20)',
      parameters: { length: 20 },
      function: 'Mostra a direção recente do preço.',
      panel: 'price',
      scale: 'price',
      color: '#fcd535',
      participation: ['entry', 'exit'],
      references: [],
      execution_columns: ['trend'],
      series_status: 'available',
      series: CANDLES.map((candle, index) => ({ timestamp_utc: candle.timestamp_utc, value: 101 + index })),
      unavailable_reason: null,
    },
    {
      key: 'rsi_14',
      type: 'rsi',
      label: 'RSI (14)',
      parameters: { length: 14 },
      function: 'Mede a força relativa do movimento.',
      panel: 'oscillator',
      scale: 'oscillator',
      color: '#a970ff',
      participation: ['entry', 'exit'],
      references: [{ value: 30, label: 'Sobrevenda' }, { value: 70, label: 'Sobrecompra' }],
      execution_columns: ['rsi_14'],
      series_status: 'available',
      series: [
        { timestamp_utc: CANDLES[0].timestamp_utc, value: 42 },
        { timestamp_utc: CANDLES[2].timestamp_utc, value: 58 },
      ],
      unavailable_reason: null,
    },
  ],
  logic_blocks: [
    { participation: 'entry', description: 'A entrada exige direção e força alinhadas.' },
    { participation: 'risk', description: 'O stop limita a exposição.' },
  ],
  unavailable_reason: null,
})

function favoritePayload(manifest = transparency()) {
  return {
    id: 1,
    name: 'BTC Transparente',
    symbol: 'BTC/USDT',
    timeframe: '1d',
    strategy_name: 'Estratégia protegida',
    strategy_display_name: manifest.display_name,
    strategy_description: manifest.description,
    strategy_transparency: manifest,
    is_strategy_protected: true,
    parameters: {},
    metrics: {
      total_return: 0.12,
      total_return_pct: 12,
      total_trades: 1,
      win_rate: 1,
      sharpe_ratio: 1.2,
      max_drawdown: 0.04,
      trades_history_cached: true,
      trades: [{
        entry_time: CANDLES[0].timestamp_utc,
        entry_price: 100,
        exit_time: CANDLES[2].timestamp_utc,
        exit_price: 104,
        profit: 0.04,
        type: 'long',
      }],
      analysis_candles: CANDLES,
      analysis_indicator_data: {},
      analysis_strategy_transparency: manifest,
      analysis_execution_mode: 'favorite_cache',
    },
    notes: 'Estratégia de teste',
    created_at: '2026-07-03T00:00:00Z',
    tier: 1,
    start_date: null,
    end_date: null,
  }
}

async function authenticate(page: any) {
  await page.addInitScript((user) => {
    window.localStorage.setItem('auth_access_token', 'test-access-token')
    window.localStorage.setItem('auth_refresh_token', 'test-refresh-token')
    window.localStorage.setItem('auth_user', JSON.stringify(user))
  }, USER)
}

async function blockExternalTraffic(page: any) {
  await page.route('**/*', (route: any) => {
    const url = new URL(route.request().url())
    if (url.hostname === '127.0.0.1' || url.hostname === 'localhost') return route.continue()
    return route.abort('blockedbyclient')
  })
}

async function mockSharedApis(page: any, manifest = transparency()) {
  const favorite = favoritePayload(manifest)
  await page.route('**/api/auth/me', (route: any) => route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(USER) }))
  await page.route('**/api/favorites/', (route: any) => route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify([favorite]) }))
  await page.route('**/api/favorites/1/trades', (route: any) => route.fulfill({
    status: 200,
    contentType: 'application/json',
    body: JSON.stringify({
      favorite_id: 1,
      trades: favorite.metrics.trades,
      metrics: favorite.metrics,
      metrics_match: true,
      metrics_deltas: {},
      regenerated: false,
      candles: CANDLES,
      indicator_data: {},
      strategy_transparency: manifest,
      execution_mode: 'favorite_cache',
    }),
  }))
  await page.route('**/api/market/candles**', (route: any) => route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ candles: CANDLES }) }))
  await page.route('**/api/monitor/preferences', (route: any) => route.fulfill({
    status: 200,
    contentType: 'application/json',
    body: JSON.stringify({
      __global__: { in_portfolio: false, card_mode: 'strategy', price_timeframe: '1d', theme: 'dark-green' },
      'BTC/USDT': { in_portfolio: true, card_mode: 'strategy', price_timeframe: '1d', theme: 'dark-green' },
    }),
  }))
  await page.route('**/api/user/binance-credentials', (route: any) => route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ configured: false }) }))
  return favorite
}

test.describe('transparência em Favoritos', () => {
  test.use({ viewport: { width: 1366, height: 900 } })

  test('mostra manifesto, overlay, painel e legenda timestampada para trader comum', async ({ page }) => {
    await authenticate(page)
    await blockExternalTraffic(page)
    await mockSharedApis(page)
    await page.route('**/api/opportunities**', (route: any) => route.fulfill({ status: 200, contentType: 'application/json', body: '[]' }))

    await page.goto('/favorites')
    await page.locator('.fav-table-shell tbody tr', { hasText: 'BTC/USDT' }).locator('button[title="Ver análise completa"]').click()

    const chart = page.getByTestId('monitor-aligned-result-chart')
    await expect(chart).toBeVisible()
    await expect(page.getByTestId('monitor-aligned-result-chart-strategy-transparency')).toBeVisible()
    await expect(page.getByTestId('monitor-aligned-result-chart-indicator-trend')).toContainText('EMA (20)')
    await expect(page.getByTestId('monitor-aligned-result-chart-indicator-rsi_14')).toContainText('RSI (14)')
    await expect(page.getByTestId('monitor-aligned-result-chart-indicator-rsi_14')).toContainText('58.00')
    await expect(page.getByTestId('monitor-aligned-result-chart-indicator-panel-oscillator')).toBeVisible()
    await expect(page.getByText('Sobrevenda (30.00)')).toBeVisible()
    await expect(page.getByText(/A entrada exige direção e força alinhadas/)).toBeVisible()
    await expect(page.getByText(/Parâmetros técnicos protegidos/)).toHaveCount(0)
    await expect(chart).toHaveAttribute('data-marker-count', '2')
  })
})

test.describe('transparência no Monitor mobile', () => {
  test.use({ viewport: { width: 390, height: 844 } })

  test('mantém painel acessível e limpa séries de timeframe incompatível', async ({ page }) => {
    const mismatchManifest = transparency('4h')
    await authenticate(page)
    await blockExternalTraffic(page)
    await mockSharedApis(page, mismatchManifest)
    await page.route('**/api/opportunities**', (route: any) => route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify([{
        id: 1,
        symbol: 'BTC/USDT',
        timeframe: '1d',
        template_name: 'Estratégia protegida',
        strategy_display_name: mismatchManifest.display_name,
        strategy_description: mismatchManifest.description,
        strategy_transparency: mismatchManifest,
        is_strategy_protected: true,
        name: 'BTC Transparente',
        notes: '',
        tier: 1,
        parameters: {},
        is_holding: true,
        distance_to_next_status: 0.5,
        next_status_label: 'exit',
        status: 'HOLDING',
        message: 'Posição ativa',
        last_price: 104,
        timestamp: CANDLES[2].timestamp_utc,
        indicator_values_candle_time: CANDLES[2].timestamp_utc,
        signal_history: [{ timestamp: CANDLES[0].timestamp_utc, signal: 1, type: 'entry', reason: 'entry', price: 100 }],
        details: {},
      }]),
    }))

    await page.goto('/monitor')
    await page.getByTestId('monitor-card-btc-usdt').getByRole('button', { name: 'Abrir Gráfico' }).click()

    const dialog = page.getByRole('dialog')
    await expect(dialog).toBeVisible()
    await expect(dialog.getByTestId('chart-modal-surface-strategy-transparency')).toBeVisible()
    await expect(dialog.getByText('Indicadores indisponíveis: o manifesto usa 4H e o gráfico exibe 1D.')).toBeVisible()
    await expect(dialog.getByTestId('chart-modal-surface-indicator-panel-oscillator')).toHaveCount(0)
    await expect(dialog.getByTestId('chart-zoom-in')).toBeVisible()
    const zoomBox = await dialog.getByTestId('chart-zoom-in').boundingBox()
    expect(zoomBox?.height).toBeGreaterThanOrEqual(44)
    const fits = await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth + 1)
    expect(fits).toBe(true)
    await dialog.getByTestId('chart-modal-close').focus()
    await page.keyboard.press('Enter')
    await expect(dialog).toHaveCount(0)
  })
})
