import { expect, test } from '@playwright/test';

const FAVORITES_PAYLOAD = [
  {
    id: 1,
    name: 'NVDA Momentum',
    symbol: 'NVDA',
    timeframe: '1d',
    strategy_name: 'ema_rsi',
    parameters: { ema_short: 9, ema_long: 21, direction: 'long' },
    metrics: {
      total_return: 0.12,
      total_return_pct: 12,
      total_trades: 3,
      win_rate: 0.66,
      sharpe_ratio: 1.4,
      max_drawdown: 0.05,
      trades: [
        {
          entry_time: '2025-01-01T00:00:00Z',
          entry_price: 100,
          exit_time: '2025-01-02T00:00:00Z',
          exit_price: 101,
          profit: 0.01,
        },
      ],
    },
    notes: 'seeded by e2e',
    created_at: '2025-01-10T00:00:00Z',
    tier: 3,
    start_date: null,
    end_date: null,
  },
  {
    id: 2,
    name: 'BTC Swing BTC/USDT 4h',
    symbol: 'BTC/USDT',
    timeframe: '4h',
    strategy_name: 'ema_rsi',
    parameters: { ema_short: 12, ema_long: 26, direction: 'long' },
    metrics: {
      total_return: 0.2,
      total_return_pct: 20,
      total_trades: 4,
      trades: [],
      win_rate: 0.5,
      sharpe_ratio: 1.2,
      max_drawdown: 0.08,
    },
    notes: 'crypto favorite',
    created_at: '2025-01-11T00:00:00Z',
    tier: 2,
    start_date: null,
    end_date: null,
  },
  {
    id: 3,
    name: 'Protected BTC Setup ETH/USDT 1h',
    symbol: 'ETH/USDT',
    timeframe: '1h',
    strategy_name: 'Estratégia protegida',
    strategy_display_name: 'EMA RSI Volume',
    is_strategy_protected: true,
    parameters: { direction: 'long' },
    metrics: {
      total_return: 0.08,
      total_return_pct: 8,
      total_trades: 2,
      win_rate: 0.5,
      sharpe_ratio: 0.8,
      max_drawdown: 0.03,
      trades: [
        {
          entry_time: '2025-01-01T00:00:00Z',
          entry_price: 100,
          exit_time: '2025-01-02T00:00:00Z',
          exit_price: 101,
          profit: 0.01,
          type: 'long',
        },
      ],
      trades_history_cached: true,
      analysis_candles: Array.from({ length: 40 }, (_, index) => {
        const open = 100 + index * 0.4;
        const close = open + (index % 2 === 0 ? 0.8 : -0.3);
        return {
          timestamp_utc: new Date(Date.UTC(2025, 0, index + 1)).toISOString(),
          open,
          high: Math.max(open, close) + 1,
          low: Math.min(open, close) - 1,
          close,
          volume: 900 + index * 10,
        };
      }),
      analysis_indicator_data: {},
      analysis_execution_mode: 'favorite_cache',
    },
    notes: 'protected crypto favorite',
    created_at: '2025-01-12T00:00:00Z',
    tier: 3,
    start_date: null,
    end_date: null,
  },
  {
    id: 4,
    name: 'BTC Legacy BTC/USDT 4h',
    symbol: 'BTC/USDT',
    timeframe: '4h',
    strategy_name: 'multi_ma_crossover',
    parameters: { ema_short: 9, sma_medium: 21, sma_long: 50, direction: 'long' },
    metrics: {
      total_return: 0.2,
      total_return_pct: 20,
      total_trades: 1,
      trades: [
        {
          entry_time: '2025-01-01T00:00:00Z',
          entry_price: 100,
          exit_time: '2025-01-02T00:00:00Z',
          exit_price: 101,
          profit: 0.01,
          type: 'long',
        },
      ],
      win_rate: 1,
      sharpe_ratio: 1.2,
      max_drawdown: 0.08,
    },
    notes: 'legacy cached trades without chart context',
    created_at: '2025-01-13T00:00:00Z',
    tier: 2,
    start_date: null,
    end_date: null,
  },
  {
    id: 5,
    name: 'multi_ma_crossover (batch)',
    symbol: 'HBAR/USDT',
    timeframe: '1d',
    strategy_name: 'multi_ma_crossover',
    parameters: { ema_short: 9, sma_medium: 21, sma_long: 50, direction: 'long', stop_loss: 0.09, data_source: 'ccxt' },
    metrics: {
      total_return: 15081.33,
      total_return_pct: 15081.33,
      total_trades: 44,
      trades: [],
      win_rate: 0.3864,
      sharpe_ratio: 0.32,
      max_drawdown: 0.5142,
      profit_factor: 2.13,
      sqn: 7.74,
      max_loss: 0.0914,
      avg_atr: 0.01,
    },
    notes: 'batch generated favorite',
    created_at: '2025-01-14T00:00:00Z',
    tier: 1,
    start_date: null,
    end_date: null,
  },
  {
    id: 6,
    name: 'multi_ma_crossoverV2 - BTC/USDT 1d (batch)',
    symbol: 'BTC/USDT',
    timeframe: '1d',
    strategy_name: 'multi_ma_crossoverV2',
    parameters: { direction: 'long', ema_short: 10, sma_medium: 16, sma_long: 22, stop_loss: 0.035, data_source: 'ccxt' },
    metrics: {
      total_return: 0.42,
      total_return_pct: 42,
      total_trades: 10,
      trades: [],
      win_rate: 0.6,
      sharpe_ratio: 1.8,
      max_drawdown: 0.11,
    },
    notes: 'batch generated BTC favorite',
    created_at: '2026-02-26T13:52:28Z',
    tier: 1,
    start_date: null,
    end_date: null,
  },
  {
    id: 201,
    name: 'BTC Multi MA Crossover - Price Action',
    symbol: 'BTC/USDT',
    timeframe: '1d',
    strategy_name: 'Estratégia protegida',
    strategy_display_name: 'Multi MA Crossover',
    is_strategy_protected: true,
    parameters: { direction: 'long' },
    metrics: {
      total_return: 1029.9985,
      total_return_pct: 102999.85,
      total_trades: 219,
      trades: [
        {
          entry_time: '2026-05-02T00:00:00Z',
          entry_price: 78231.13,
          exit_time: '2026-05-14T00:00:00Z',
          exit_price: 79313.61,
          profit: 0.012317,
          type: 'long',
        },
      ],
      trades_history_cached: true,
      analysis_candles: Array.from({ length: 80 }, (_, index) => {
        const open = 72000 + index * 120;
        const close = open + (index % 3 === 0 ? 280 : -140);
        return {
          timestamp_utc: new Date(Date.UTC(2026, 2, index + 1)).toISOString(),
          open,
          high: Math.max(open, close) + 350,
          low: Math.min(open, close) - 350,
          close,
          volume: 12000 + index * 25,
        };
      }),
      analysis_indicator_data: {},
      analysis_execution_mode: 'favorite_cache',
    },
    notes: 'quant btc cached favorite',
    created_at: '2026-05-14T00:00:00Z',
    tier: 1,
    start_date: '2017-08-17',
    end_date: '2026-05-14',
  },
];

const BACKTEST_PAYLOAD = {
  template_name: 'ema_rsi',
  symbol: 'BTC/USDT',
  timeframe: '4h',
  parameters: { ema_short: 12, ema_long: 26, direction: 'long' },
  metrics: { total_trades: 1, win_rate: 1, total_return: 0.01, avg_profit: 0.01, max_drawdown: 0 },
  trades: [
    {
      entry_time: '2025-01-01T00:00:00Z',
      entry_price: 100,
      exit_time: '2025-01-02T00:00:00Z',
      exit_price: 101,
      profit: 0.01,
      type: 'long',
    },
  ],
  indicator_data: {},
  candles: Array.from({ length: 40 }, (_, index) => {
    const open = 100 + index * 0.7;
    const close = open + (index % 2 === 0 ? 1 : -0.4);
    return {
      timestamp_utc: new Date(Date.UTC(2025, 0, index + 1)).toISOString(),
      open,
      high: Math.max(open, close) + 1,
      low: Math.min(open, close) - 1,
      close,
      volume: 1000 + index * 20,
    };
  }),
  execution_mode: 'fast_1d',
  direction: 'long',
};

const CURRENT_MARKET_CANDLES = Array.from({ length: 60 }, (_, index) => {
  const open = 200 + index * 1.1;
  const close = open + (index % 2 === 0 ? 1.5 : -0.6);
  return {
    timestamp_utc: new Date(Date.UTC(2026, 4, index + 1)).toISOString(),
    open,
    high: Math.max(open, close) + 1.25,
    low: Math.min(open, close) - 1.25,
    close,
    volume: 2000 + index * 30,
  };
});

const FULL_HISTORY_MARKET_CANDLES = Array.from({ length: 120 }, (_, index) => {
  const open = 65000 + index * 90;
  const close = open + (index % 2 === 0 ? 180 : -120);
  return {
    timestamp_utc: new Date(Date.UTC(2025, 10, index + 1)).toISOString(),
    open,
    high: Math.max(open, close) + 240,
    low: Math.min(open, close) - 240,
    close,
    volume: 9000 + index * 30,
  };
});

const MONITOR_OPPORTUNITIES_PAYLOAD = [
  {
    id: 2,
    symbol: 'BTC/USDT',
    asset_type: 'crypto',
    timeframe: '4h',
    template_name: 'ema_rsi',
    name: 'BTC Swing BTC/USDT 4h',
    tier: 2,
    parameters: { ema_short: 12, ema_long: 26, direction: 'long' },
    is_holding: false,
    distance_to_next_status: 1.2,
    next_status_label: 'entry',
    signal_history: [
      {
        timestamp: '2025-01-01T00:00:00.000Z',
        signal: 1,
        type: 'entry',
        reason: 'entry',
        price: 100,
      },
      {
        timestamp: '2025-01-02T00:00:00.000Z',
        signal: -1,
        type: 'exit',
        reason: 'exit_logic',
        price: 101,
      },
      {
        timestamp: '2026-05-10T00:00:00.000Z',
        signal: 1,
        type: 'entry',
        reason: 'entry',
        price: 210,
      },
      {
        timestamp: '2026-05-20T00:00:00.000Z',
        signal: -1,
        type: 'exit',
        reason: 'exit_logic',
        price: 225,
      },
    ],
    entry_price: null,
    stop_price: null,
    distance_to_stop_pct: null,
    status: 'WAIT',
    badge: 'neutral',
    message: 'Waiting',
    last_price: 230,
    timestamp: '2026-05-29T00:00:00.000Z',
    details: {},
  },
  {
    id: 3,
    symbol: 'ETH/USDT',
    asset_type: 'crypto',
    timeframe: '1h',
    template_name: 'Estratégia protegida',
    name: 'Protected BTC Setup ETH/USDT 1h',
    tier: 3,
    parameters: {},
    is_holding: false,
    distance_to_next_status: 0.8,
    next_status_label: 'entry',
    signal_history: [
      {
        timestamp: '2025-01-01T00:00:00.000Z',
        signal: 1,
        type: 'entry',
        reason: 'entry',
        price: 100,
      },
      {
        timestamp: '2025-01-02T00:00:00.000Z',
        signal: -1,
        type: 'exit',
        reason: 'exit',
        price: 101,
      },
      {
        timestamp: '2026-05-12T00:00:00.000Z',
        signal: 1,
        type: 'entry',
        reason: 'entry',
        price: 214,
      },
      {
        timestamp: '2026-05-22T00:00:00.000Z',
        signal: -1,
        type: 'exit',
        reason: 'exit',
        price: 228,
      },
    ],
    entry_price: null,
    stop_price: null,
    distance_to_stop_pct: null,
    status: 'WAIT',
    badge: 'neutral',
    message: 'Waiting',
    last_price: 230,
    timestamp: '2026-05-29T00:00:00.000Z',
    details: {},
  },
];

function cloneFavoritesPayload() {
  return JSON.parse(JSON.stringify(FAVORITES_PAYLOAD));
}

async function setupDeterministicApiMocks(page: any, options?: { user?: Record<string, any>; hangOpportunities?: boolean }) {
  const authUser = options?.user || {
      id: 'admin-user',
      email: 'admin@example.com',
      name: 'Admin User',
      isAdmin: true,
    };
  await page.addInitScript((user: Record<string, any>) => {
    window.localStorage.setItem('auth_access_token', 'test-access-token');
    window.localStorage.setItem('auth_refresh_token', 'test-refresh-token');
    window.localStorage.setItem('auth_user', JSON.stringify(user));
  }, authUser);

  await page.route('**/*', (route: any) => {
    const url = new URL(route.request().url());
    if (url.hostname === '127.0.0.1' || url.hostname === 'localhost') {
      return route.continue();
    }
    return route.abort('blockedbyclient');
  });

  let serverFavoritesPayload = cloneFavoritesPayload();

  await page.route('**/api/favorites/', (route: any) => {
    if (route.request().method() === 'GET') {
      return route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(serverFavoritesPayload),
      });
    }
    return route.continue();
  });

  let backtestTriggeredCount = 0;
  let favoriteTradesTriggeredCount = 0;
  let marketCandlesTriggeredCount = 0;
  let opportunitiesTriggeredCount = 0;
  await page.route('**/api/combos/backtest', (route: any) => {
    backtestTriggeredCount += 1;
    return route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(BACKTEST_PAYLOAD),
    });
  });

  await page.route(/.*\/api\/favorites\/(2|4)\/trades$/, (route: any) => {
    favoriteTradesTriggeredCount += 1;
    const url = new URL(route.request().url());
    const favoriteId = Number(url.pathname.match(/\/favorites\/(\d+)\/trades$/)?.[1] ?? 2);
    const simulatesLegacyMismatch = favoriteId === 2;
    const cachedMetrics = {
      ...BACKTEST_PAYLOAD.metrics,
      trades: BACKTEST_PAYLOAD.trades,
      trades_history_cached: true,
      trades_metrics_match: !simulatesLegacyMismatch,
      trades_metrics_deltas: simulatesLegacyMismatch ? { total_return_pct: { saved: 20, regenerated: 1 } } : {},
      analysis_candles: BACKTEST_PAYLOAD.candles,
      analysis_indicator_data: BACKTEST_PAYLOAD.indicator_data,
      analysis_execution_mode: BACKTEST_PAYLOAD.execution_mode,
    };
    serverFavoritesPayload = serverFavoritesPayload.map((fav: any) => (
      fav.id === favoriteId ? { ...fav, metrics: cachedMetrics } : fav
    ));
    return route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        favorite_id: favoriteId,
        trades: BACKTEST_PAYLOAD.trades,
        metrics: cachedMetrics,
        metrics_match: !simulatesLegacyMismatch,
        metrics_deltas: cachedMetrics.trades_metrics_deltas,
        regenerated: true,
        candles: BACKTEST_PAYLOAD.candles,
        indicator_data: BACKTEST_PAYLOAD.indicator_data,
        execution_mode: BACKTEST_PAYLOAD.execution_mode,
      }),
    });
  });

  await page.route('**/api/market/candles**', (route: any) => {
    marketCandlesTriggeredCount += 1;
    const url = new URL(route.request().url());
    const isFullHistory = url.searchParams.get('full_history') === 'true';
    const candles = isFullHistory ? FULL_HISTORY_MARKET_CANDLES : CURRENT_MARKET_CANDLES;
    return route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        symbol: url.searchParams.get('symbol'),
        timeframe: url.searchParams.get('timeframe'),
        count: candles.length,
        candles,
      }),
    });
  });

  await page.route('**/api/opportunities**', (route: any) => {
    opportunitiesTriggeredCount += 1;
    if (options?.hangOpportunities) {
      return;
    }
    return route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(MONITOR_OPPORTUNITIES_PAYLOAD),
    });
  });

  return {
    wasBacktestTriggered: () => backtestTriggeredCount > 0,
    wasFavoriteTradesTriggered: () => favoriteTradesTriggeredCount > 0,
    backtestTriggeredCount: () => backtestTriggeredCount,
    favoriteTradesTriggeredCount: () => favoriteTradesTriggeredCount,
    marketCandlesTriggeredCount: () => marketCandlesTriggeredCount,
    opportunitiesTriggeredCount: () => opportunitiesTriggeredCount,
  };
}

async function expectNoHorizontalOverflow(page: any) {
  const overflow = await page.evaluate(() => {
    const shell = document.querySelector('.fav-table-shell') as HTMLElement | null;
    return {
      documentOverflow: document.documentElement.scrollWidth - document.documentElement.clientWidth,
      shellOverflow: shell ? shell.scrollWidth - shell.clientWidth : 0,
    };
  });

  expect(overflow.documentOverflow).toBeLessThanOrEqual(1);
  expect(overflow.shellOverflow).toBeLessThanOrEqual(1);
}

test.use({ viewport: { width: 1366, height: 900 } });

test('favorites page renders list from mocked API', async ({ page }) => {
  const pageErrors: string[] = [];
  page.on('pageerror', (err) => pageErrors.push(err.message));

  await setupDeterministicApiMocks(page);
  await page.goto('/favorites');

  await expect(page.getByRole('heading', { name: 'Estratégias favoritas' })).toBeVisible();
  await expect(page.getByRole('cell', { name: 'NVDA' }).first()).toHaveCount(0);
  await expect(page.getByRole('cell', { name: 'BTC/USDT' }).first()).toBeVisible();
  await expect(page.getByRole('cell', { name: /ema rsi/i }).first()).toBeVisible();
  await expect(page.getByRole('cell', { name: /Protected BTC Setup/i }).first()).toBeVisible();
  await expect(page.getByRole('cell', { name: 'Protected BTC Setup ETH/USDT 1h' }).first()).toHaveCount(0);
  await expect(page.getByRole('cell', { name: /Estratégia protegida/i }).first()).toHaveCount(0);

  const btcBatchRow = page.locator('.fav-table-shell tbody tr', { hasText: 'multi ma crossoverV2' });
  await expect(btcBatchRow.locator('.metric-cell.strong')).toHaveText('+42.00%');
  await expect(btcBatchRow.locator('.metric-cell.strong')).not.toHaveText('+4200.00%');

  const hbarRow = page.locator('.fav-table-shell tbody tr', { hasText: 'HBAR/USDT' });
  await expect(hbarRow.locator('.metric-cell.strong')).toHaveText('+15081.33%');
  await expect(hbarRow.locator('.metric-cell.strong')).not.toHaveText('+1508133.00%');
  expect(pageErrors).toEqual([]);
});

test('favorites hides stocks and removes Asset Type dropdown in crypto-only MVP', async ({ page }) => {
  await setupDeterministicApiMocks(page);
  await page.goto('/favorites');

  const nvdaRow = page.locator('tbody tr', { hasText: 'NVDA' });
  const btcRow = page.locator('tbody tr', { hasText: 'BTC Swing' });
  await expect(page.getByLabel('Asset Type')).toHaveCount(0);
  await expect(nvdaRow).toHaveCount(0);
  await expect(btcRow).toHaveCount(1);
});

test('favorites grid fits common desktop without horizontal scrolling', async ({ page }) => {
  await setupDeterministicApiMocks(page);
  await page.setViewportSize({ width: 1366, height: 900 });
  await page.goto('/favorites');

  await expect(page.locator('.fav-table-shell')).toBeVisible();
  await expect(page.locator('.fav-table-shell thead th.strategy-col')).toHaveText('Estratégia');
  await expect(page.getByRole('cell', { name: 'BTC/USDT' }).first()).toBeVisible();
  await expect(page.locator('.fav-table-shell').locator('.telegram-col').first()).toBeHidden();
  await expect(page.locator('.fav-table-shell').locator('.direction-col').first()).toBeHidden();
  await expect(page.locator('.fav-table-shell').locator('.advanced-col').first()).toBeHidden();
  await expectNoHorizontalOverflow(page);
});

test('favorites grid keeps strategy readable on wide desktop', async ({ page }) => {
  await setupDeterministicApiMocks(page);
  await page.setViewportSize({ width: 1920, height: 900 });
  await page.goto('/favorites');

  const table = page.locator('.fav-table-shell');
  const strategyHeader = table.locator('thead th.strategy-col');
  const strategyCell = table.locator('tbody tr', { hasText: 'BTC/USDT' }).first().locator('.strategy-cell');

  await expect(strategyHeader).toHaveText('Estratégia');
  await expect(table.locator('.advanced-col').first()).toBeHidden();
  await expect(table.locator('.direction-col').first()).toBeHidden();
  await expect(strategyCell).toBeVisible();
  await expect.poll(async () => {
    const box = await strategyCell.boundingBox();
    return Math.round(box?.width ?? 0);
  }).toBeGreaterThanOrEqual(220);
  await expectNoHorizontalOverflow(page);
});

test('favorites strategy column avoids duplicated raw strategy labels', async ({ page }) => {
  await setupDeterministicApiMocks(page);
  await page.goto('/favorites');

  const hbarRow = page.locator('.fav-table-shell tbody tr', { hasText: 'HBAR/USDT' });
  const strategyCell = hbarRow.locator('.strategy-cell');

  await expect(strategyCell.locator('strong')).toHaveText('multi ma crossover');
  await expect(strategyCell).not.toContainText('multi_ma_crossover');
  await expect(strategyCell.locator('.strategy-description')).toHaveCount(0);
});

test('favorites search matches combined symbol quote and strategy terms', async ({ page }) => {
  await setupDeterministicApiMocks(page);
  await page.goto('/favorites');

  await page.locator('.fav-search input').fill('BTC/USDT USDT multi ma crossoverV2');

  const targetRow = page.locator('.fav-table-shell tbody tr', { hasText: 'multi ma crossoverV2' });
  await expect(targetRow).toHaveCount(1);
  await expect(targetRow.getByRole('cell', { name: 'BTC/USDT' })).toBeVisible();
  await expect(targetRow.locator('.strategy-cell')).toContainText('multi ma crossoverV2');
  await expect(page.locator('.fav-table-shell tbody tr', { hasText: 'HBAR/USDT' })).toHaveCount(0);
});

test('favorites mobile cards fit viewport without horizontal scrolling', async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await setupDeterministicApiMocks(page);
  await page.goto('/favorites');

  await expect(page.locator('.fav-mobile-list')).toBeVisible();
  await expect(page.locator('.fav-table-shell')).toBeHidden();
  await expectNoHorizontalOverflow(page);
});

test('favorites filters by strategy name and timeframe separately', async ({ page }) => {
  await setupDeterministicApiMocks(page);
  await page.goto('/favorites');

  const strategyFilter = page.locator('.fav-filters label', { hasText: 'Strategy' }).locator('select');
  const timeFilter = page.locator('.fav-filters label', { hasText: 'Time' }).locator('select');

  await expect(strategyFilter.locator('option[value="ema rsi"]')).toHaveCount(1);
  await expect(strategyFilter.locator('option', { hasText: 'Protected BTC Setup' })).toHaveCount(0);
  await expect(strategyFilter.locator('option', { hasText: 'Protected BTC Setup ETH/USDT 1h' })).toHaveCount(0);
  await expect(strategyFilter.locator('option', { hasText: 'BTC Swing BTC/USDT 4h' })).toHaveCount(0);
  await expect(strategyFilter.locator('option', { hasText: 'ETH/USDT' })).toHaveCount(0);
  await expect(strategyFilter.locator('option', { hasText: 'BTC/USDT' })).toHaveCount(0);
  await expect(strategyFilter.locator('option', { hasText: '1h' })).toHaveCount(0);
  await expect(strategyFilter.locator('option', { hasText: '4h' })).toHaveCount(0);
  await expect(strategyFilter.locator('option[value="EMA RSI Volume"]')).toHaveCount(1);
  await expect(strategyFilter.locator('option[value="Estratégia protegida"]')).toHaveCount(0);
  await expect(timeFilter.locator('option', { hasText: '1h' })).toHaveCount(1);
  await expect(timeFilter.locator('option', { hasText: '4h' })).toHaveCount(1);

  await strategyFilter.selectOption({ label: 'ema rsi' });

  await expect(page.locator('tbody tr', { hasText: 'BTC Swing' })).toHaveCount(1);
  await expect(page.locator('tbody tr', { hasText: 'Protected BTC Setup' })).toHaveCount(0);

  await strategyFilter.selectOption({ label: 'EMA RSI Volume' });

  await expect(page.locator('tbody tr', { hasText: 'BTC Swing' })).toHaveCount(0);
  await expect(page.locator('tbody tr', { hasText: 'Protected BTC Setup' })).toHaveCount(1);
  await expect(page.locator('tbody tr', { hasText: 'ema_short' })).toHaveCount(0);

  await strategyFilter.selectOption('ALL');
  await timeFilter.selectOption('4h');

  await expect(page.locator('tbody tr', { hasText: 'BTC Swing' })).toHaveCount(1);
  await expect(page.locator('tbody tr', { hasText: 'Protected BTC Setup' })).toHaveCount(0);
});

test('favorites exposes one analysis CTA instead of separate trades/results actions', async ({ page }) => {
  const api = await setupDeterministicApiMocks(page);
  await page.goto('/favorites');

  const btcRow = page.locator('.fav-table-shell tbody tr', { hasText: 'BTC Swing' });
  await expect(btcRow.locator('button[title="View Trades"]')).toHaveCount(0);
  await expect(btcRow.locator('button[title="View Results"]')).toHaveCount(0);
  await expect(btcRow.locator('button[title="Chat com o agente"]')).toHaveCount(0);
  await expect(btcRow.getByRole('button', { name: /Trader/i })).toHaveCount(0);

  const analysis = btcRow.locator('button[title="Ver análise completa"]');
  await expect(analysis).toHaveCount(1);
  await analysis.click();

  expect(api.wasBacktestTriggered()).toBe(false);
  expect(api.wasFavoriteTradesTriggered()).toBe(true);
  await expect(page).toHaveURL(/\/combo\/results$/);
  await expect(page.getByText('No results found')).toHaveCount(0);
  await expect(page.getByText('Lista de operações')).toBeVisible();
  await expect(page.getByRole('button', { name: /Voltar aos favoritos/i })).toBeVisible();
});

test('favorites mobile card exposes one analysis CTA', async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await setupDeterministicApiMocks(page);
  await page.goto('/favorites');

  const btcCard = page.locator('.fav-mobile-card', { hasText: 'BTC Swing' });
  await expect(btcCard).toBeVisible();
  await expect(btcCard.locator('button[title="View Trades"]')).toHaveCount(0);
  await expect(btcCard.locator('button[title="View Results"]')).toHaveCount(0);
  await expect(btcCard.locator('button[title="Chat com o agente"]')).toHaveCount(0);
  await expect(btcCard.getByRole('button', { name: /Trader/i })).toHaveCount(0);
  await expect(btcCard.locator('button[title="Ver análise completa"]')).toHaveCount(1);
  await expect(btcCard.getByRole('button', { name: /Analisar/i })).toBeVisible();
});

test('favorites analysis regenerates missing trades into result view', async ({ page }) => {
  const api = await setupDeterministicApiMocks(page);
  await page.goto('/favorites');

  const analysis = page
    .locator('.fav-table-shell tbody tr', { hasText: 'BTC Swing' })
    .locator('button[title="Ver análise completa"]');
  await expect(analysis).toBeVisible();
  await analysis.click();

  expect(api.wasFavoriteTradesTriggered()).toBe(true);
  await expect(page).toHaveURL(/\/combo\/results$/);
  await expect(page.getByRole('button', { name: /Voltar aos favoritos/i })).toBeVisible();
  await expect(page.getByText('Histórico reconstruído pode divergir do resumo salvo.')).toHaveCount(0);
  await expect(page.getByText('Lista de operações')).toBeVisible();
  await expect(page.getByTestId('monitor-aligned-result-chart')).toBeVisible();
  await expect(page.getByTestId('monitor-aligned-result-chart')).toHaveAttribute('data-marker-count', '4');
  await expect(page.getByTestId('monitor-aligned-result-chart')).toHaveAttribute('data-marker-labels', /COMPRA.*VENDA/);
  await expect(page.getByTestId('monitor-aligned-result-chart')).not.toHaveAttribute('data-marker-labels', /BUY|SELL|SHORT|COVER/);
  await expect(page.getByTestId('result-main-chart')).toBeVisible();
  await expect(page.getByText('BTC/USDT • 4h • 160 velas')).toBeVisible();
  await expect(page.getByTestId('result-chart-zoom-in')).toBeVisible();
  await expect(page.getByTestId('result-chart-zoom-out')).toBeVisible();
  await expect(page.getByTestId('result-chart-zoom-reset')).toBeVisible();
  await expect(page.getByTestId('result-chart-visible-bars')).toContainText('velas');
  const visibleBarsBeforeWheel = await page.getByTestId('result-chart-visible-bars').textContent();
  await page.getByTestId('result-main-chart').hover();
  await page.mouse.wheel(0, -600);
  await expect.poll(async () => page.getByTestId('result-chart-visible-bars').textContent()).not.toBe(visibleBarsBeforeWheel);
  await expect(page.getByRole('columnheader', { name: 'Tipo' })).toBeVisible();
  await expect(page.getByRole('columnheader', { name: 'Data e hora' })).toBeVisible();
  await expect(page.getByRole('columnheader', { name: 'Sinal' })).toBeVisible();
  await expect(page.getByRole('columnheader', { name: 'Valor da posição' })).toBeVisible();
  await expect(page.getByText('100.00 USD').first()).toBeVisible();
  await expect(page.getByText('May 10, 2026').first()).toBeVisible();
  await expect(page.getByText('May 20, 2026').first()).toBeVisible();
  await expect(page.getByText('Jan 1, 2025').first()).toBeVisible();
  await expect(page.getByText('Jan 2, 2025').first()).toBeVisible();

  const tradeTableBodyBackground = await page.locator('table tbody').evaluate((node) => {
    return window.getComputedStyle(node).backgroundColor;
  });
  expect(tradeTableBodyBackground).toBe('rgb(30, 35, 41)');

  await page.getByRole('button', { name: /Voltar aos favoritos/i }).click();
  await expect(page).toHaveURL(/\/favorites$/);
  await expect(page.getByRole('heading', { name: 'Estratégias favoritas' })).toBeVisible();

  const cachedAnalysis = page
    .locator('.fav-table-shell tbody tr', { hasText: 'BTC Swing' })
    .locator('button[title="Ver análise completa"]');
  await expect(cachedAnalysis).toBeVisible();
  await cachedAnalysis.click();

  expect(api.backtestTriggeredCount()).toBe(0);
  expect(api.favoriteTradesTriggeredCount()).toBe(1);
  expect(api.marketCandlesTriggeredCount()).toBeGreaterThanOrEqual(1);
  expect(api.opportunitiesTriggeredCount()).toBeGreaterThanOrEqual(2);
  await expect(page).toHaveURL(/\/combo\/results$/);
  await expect(page.getByText('May 10, 2026').first()).toBeVisible();
  await expect(page.getByText('Jan 1, 2025').first()).toBeVisible();
});

test('favorites analysis backfills chart context for legacy saved BTC multi MA trades', async ({ page }) => {
  const api = await setupDeterministicApiMocks(page);
  await page.goto('/favorites');

  const analysis = page
    .locator('.fav-table-shell tbody tr', { hasText: 'BTC Legacy' })
    .locator('button[title="Ver análise completa"]');
  await expect(analysis).toBeVisible();
  await analysis.click();

  expect(api.backtestTriggeredCount()).toBe(0);
  expect(api.favoriteTradesTriggeredCount()).toBe(1);
  await expect(page).toHaveURL(/\/combo\/results$/);
  await expect(page.getByText('Histórico reconstruído pode divergir do resumo salvo.')).toHaveCount(0);
  await expect(page.getByText('Chart data not available for this run.')).toHaveCount(0);
  await expect(page.getByText(/multi_ma_crossover - Ação de preço/i)).toBeVisible();
  await expect(page.getByTestId('monitor-aligned-result-chart')).toBeVisible();
  await expect(page.getByTestId('result-chart-zoom-in')).toBeVisible();
  await expect(page.getByText('BTC/USDT • 4h • 160 velas')).toBeVisible();

  await page.getByRole('button', { name: /Voltar aos favoritos/i }).click();
  await expect(page).toHaveURL(/\/favorites$/);

  const cachedAnalysis = page
    .locator('.fav-table-shell tbody tr', { hasText: 'BTC Legacy' })
    .locator('button[title="Ver análise completa"]');
  await cachedAnalysis.click();

  expect(api.backtestTriggeredCount()).toBe(0);
  expect(api.favoriteTradesTriggeredCount()).toBe(1);
  await expect(page.getByText(/multi_ma_crossover - Ação de preço/i)).toBeVisible();
});

test('favorites analysis opens cached multi MA chart when trade recovery hangs', async ({ page }) => {
  await setupDeterministicApiMocks(page);
  const dialogs: string[] = [];
  page.on('dialog', async (dialog) => {
    dialogs.push(dialog.message());
    await dialog.dismiss();
  });
  await page.route('**/api/favorites/5/trades', () => {
    // Simulates live full-history trade recovery taking too long.
  });

  await page.goto('/favorites');

  const analysis = page
    .locator('.fav-table-shell tbody tr', { hasText: 'HBAR/USDT' })
    .locator('button[title="Ver análise completa"]');
  await expect(analysis).toBeVisible();
  await analysis.click();

  await expect(page).toHaveURL(/\/combo\/results$/);
  await expect(page.getByTestId('monitor-aligned-result-chart')).toBeVisible();
  const parameters = page.getByTestId('combo-result-parameters');
  await expect(parameters.getByText('Direção')).toBeVisible();
  await expect(parameters.getByText('Compra')).toBeVisible();
  await expect(parameters.getByText('EMA curta')).toBeVisible();
  await expect(parameters.getByText('SMA média')).toBeVisible();
  await expect(parameters.getByText('SMA longa')).toBeVisible();
  await expect(parameters.getByText('Stop de perda')).toBeVisible();
  await expect(parameters.getByText('9.00%')).toBeVisible();
  await expect(parameters.getByText('Fonte de dados')).toBeVisible();
  await expect(parameters.getByText('CCXT')).toBeVisible();
  await expect(parameters.getByText('direction', { exact: true })).toHaveCount(0);
  await expect(parameters.getByText('ema short', { exact: true })).toHaveCount(0);
  await expect(parameters.getByText('sma medium', { exact: true })).toHaveCount(0);
  await expect(parameters.getByText('sma long', { exact: true })).toHaveCount(0);
  await expect(parameters.getByText('stop loss', { exact: true })).toHaveCount(0);
  await expect(parameters.getByText('data source', { exact: true })).toHaveCount(0);
  await expect(page.getByText('HBAR/USDT • 1d • 120 velas')).toBeVisible();
  expect(dialogs).toEqual([]);
});

test('common user opens protected favorite chart without moving averages or MA values', async ({ page }) => {
  const api = await setupDeterministicApiMocks(page, {
    user: {
      id: 'common-user',
      email: 'user@example.com',
      name: 'Common User',
      isAdmin: false,
    },
  });
  await page.goto('/favorites');

  const protectedRow = page.locator('.fav-table-shell tbody tr', { hasText: 'ETH/USDT' });
  const analysis = protectedRow.locator('button[title="Ver análise completa"]');
  await expect(analysis).toBeVisible();
  await analysis.click();

  expect(api.favoriteTradesTriggeredCount()).toBe(0);
  await expect(page).toHaveURL(/\/combo\/results$/);
  await expect(page.getByTestId('monitor-aligned-result-chart')).toBeVisible();
  await expect(page.getByText(/EMA RSI Volume - Ação de preço/i)).toBeVisible();
  await expect(page.getByText(/Estratégia protegida - Ação de preço/i)).toHaveCount(0);
  await expect(page.getByTestId('monitor-aligned-result-chart')).toHaveAttribute('data-marker-count', '4');
  await expect(page.getByTestId('result-main-chart')).toBeVisible();
  await expect(page.getByText('ETH/USDT • 1h • 160 velas')).toBeVisible();
  await expect(page.getByText('May 12, 2026').first()).toBeVisible();
  await expect(page.getByText('Jan 1, 2025').first()).toBeVisible();
  await expect(page.getByText('Jan 2, 2025').first()).toBeVisible();
  await expect(page.getByTestId('result-chart-overlays')).toHaveCount(0);
  await expect(page.getByText(/EMA 9|SMA 21|SMA 50/)).toHaveCount(0);
  await expect(page.getByText('Parâmetros técnicos protegidos para este perfil.')).toBeVisible();

  const visibleBarsBeforeWheel = await page.getByTestId('result-chart-visible-bars').textContent();
  await page.getByTestId('result-main-chart').hover();
  await page.mouse.wheel(0, -600);
  await expect.poll(async () => page.getByTestId('result-chart-visible-bars').textContent()).not.toBe(visibleBarsBeforeWheel);
});

test('favorites opens Multi MA Crossover full-history chart even when monitor sync is slow', async ({ page }) => {
  const api = await setupDeterministicApiMocks(page, {
    user: {
      id: 'common-user',
      email: 'user@example.com',
      name: 'Common User',
      isAdmin: false,
    },
    hangOpportunities: true,
  });
  await page.goto('/favorites');

  const quantRow = page.locator('.fav-table-shell tbody tr', { hasText: 'BTC Multi MA Crossover - Price Action' });
  const analysis = quantRow.locator('button[title="Ver análise completa"]');
  await expect(analysis).toBeVisible();
  await analysis.click();

  expect(api.opportunitiesTriggeredCount()).toBe(1);
  await expect(page).toHaveURL(/\/combo\/results$/, { timeout: 5000 });
  await expect(page.getByTestId('monitor-aligned-result-chart')).toBeVisible();
  await expect(page.getByTestId('result-main-chart')).toBeVisible();
  await expect(page.getByText(/Multi MA Crossover - Ação de preço/i)).toBeVisible();
  await expect(page.getByText('BTC/USDT • 1d • 200 velas')).toBeVisible();
  await expect(page.getByTestId('result-chart-visible-bars')).toContainText('180 velas');
  await expect(page.getByText('BTC/USDT • 1d • 120 velas')).toHaveCount(0);
  await expect(page.getByText('BTC/USDT • 1d • 60 velas')).toHaveCount(0);
  await expect(page.getByText('BTC/USDT • 1d • 80 velas')).toHaveCount(0);
});

test('favorites analysis uses full market history over stale saved analysis velas', async ({ page }) => {
  const api = await setupDeterministicApiMocks(page);
  await page.goto('/favorites');

  const analysis = page
    .locator('.fav-table-shell tbody tr', { hasText: 'Protected BTC Setup' })
    .locator('button[title="Ver análise completa"]');
  await expect(analysis).toBeVisible();
  await analysis.click();

  expect(api.marketCandlesTriggeredCount()).toBe(1);
  expect(api.opportunitiesTriggeredCount()).toBe(1);
  await expect(page).toHaveURL(/\/combo\/results$/);
  await expect(page.getByTestId('monitor-aligned-result-chart')).toBeVisible();
  await expect(page.getByText('ETH/USDT • 1h • 160 velas')).toBeVisible();
  await expect(page.getByText('ETH/USDT • 1h • 120 velas')).toHaveCount(0);
  await expect(page.getByText('ETH/USDT • 1h • 40 velas')).toHaveCount(0);
  await expect(page.getByText('May 12, 2026').first()).toBeVisible();
  await expect(page.getByText('Jan 1, 2025').first()).toBeVisible();
});

test('favorites analysis preserves saved trades and adds monitor signal history without duplicates', async ({ page }) => {
  const api = await setupDeterministicApiMocks(page);
  await page.goto('/favorites');

  const analysis = page
    .locator('.fav-table-shell tbody tr', { hasText: 'BTC Swing' })
    .locator('button[title="Ver análise completa"]');
  await expect(analysis).toBeVisible();
  await analysis.click();

  expect(api.wasFavoriteTradesTriggered()).toBe(true);
  expect(api.opportunitiesTriggeredCount()).toBe(1);
  await expect(page).toHaveURL(/\/combo\/results$/);
  await expect(page.getByTestId('monitor-aligned-result-chart')).toHaveAttribute('data-marker-count', '4');
  await expect(page.getByText('Jan 1, 2025')).toHaveCount(1);
  await expect(page.getByText('Jan 2, 2025')).toHaveCount(1);
  await expect(page.getByText('May 10, 2026').first()).toBeVisible();
  await expect(page.getByText('May 20, 2026').first()).toBeVisible();
});
