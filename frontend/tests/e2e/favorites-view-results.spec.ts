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
      win_rate: 0.5,
      sharpe_ratio: 1.2,
      max_drawdown: 0.08,
      trades: [
        {
          entry_time: '2025-01-03T00:00:00Z',
          entry_price: 100,
          exit_time: '2025-01-04T00:00:00Z',
          exit_price: 102,
          profit: 0.02,
        },
      ],
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
    strategy_display_name: 'Estratégia protegida',
    is_strategy_protected: true,
    parameters: { direction: 'long' },
    metrics: {
      total_return: 0.08,
      total_return_pct: 8,
      total_trades: 2,
      win_rate: 0.5,
      sharpe_ratio: 0.8,
      max_drawdown: 0.03,
      trades: [],
    },
    notes: 'protected crypto favorite',
    created_at: '2025-01-12T00:00:00Z',
    tier: 3,
    start_date: null,
    end_date: null,
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
  candles: [
    {
      timestamp_utc: '2025-01-01T00:00:00Z',
      open: 100,
      high: 102,
      low: 99,
      close: 101,
      volume: 1000,
    },
    {
      timestamp_utc: '2025-01-02T00:00:00Z',
      open: 101,
      high: 103,
      low: 100,
      close: 102,
      volume: 1100,
    },
  ],
  execution_mode: 'fast_1d',
  direction: 'long',
};

async function setupDeterministicApiMocks(page: any) {
  await page.addInitScript(() => {
    window.localStorage.setItem('auth_access_token', 'test-access-token');
    window.localStorage.setItem('auth_refresh_token', 'test-refresh-token');
    window.localStorage.setItem('auth_user', JSON.stringify({
      id: 'admin-user',
      email: 'admin@example.com',
      name: 'Admin User',
      isAdmin: true,
    }));
  });

  await page.route('**/*', (route: any) => {
    const url = new URL(route.request().url());
    if (url.hostname === '127.0.0.1' || url.hostname === 'localhost') {
      return route.continue();
    }
    return route.abort('blockedbyclient');
  });

  await page.route('**/api/favorites/', (route: any) => {
    if (route.request().method() === 'GET') {
      return route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(FAVORITES_PAYLOAD),
      });
    }
    return route.continue();
  });

  let backtestTriggered = false;
  await page.route('**/api/combos/backtest', (route: any) => {
    backtestTriggered = true;
    return route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(BACKTEST_PAYLOAD),
    });
  });

  return {
    wasBacktestTriggered: () => backtestTriggered,
  };
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
  expect(pageErrors).toEqual([]);
});

test('favorites hides stocks and removes Asset Type dropdown in crypto-only MVP', async ({ page }) => {
  await setupDeterministicApiMocks(page);
  await page.goto('/favorites');

  const nvdaRow = page.locator('tbody tr', { hasText: 'NVDA' });
  const btcRow = page.locator('tbody tr', { hasText: 'BTC/USDT' });
  await expect(page.getByLabel('Asset Type')).toHaveCount(0);
  await expect(nvdaRow).toHaveCount(0);
  await expect(btcRow).toHaveCount(1);
});

test('favorites filters by strategy name and timeframe separately', async ({ page }) => {
  await setupDeterministicApiMocks(page);
  await page.goto('/favorites');

  const strategyFilter = page.locator('.fav-filters label', { hasText: 'Strategy' }).locator('select');
  const timeFilter = page.locator('.fav-filters label', { hasText: 'Time' }).locator('select');

  await expect(strategyFilter.locator('option', { hasText: 'ema rsi' })).toHaveCount(1);
  await expect(strategyFilter.locator('option', { hasText: 'Protected BTC Setup' })).toHaveCount(0);
  await expect(strategyFilter.locator('option', { hasText: 'Protected BTC Setup ETH/USDT 1h' })).toHaveCount(0);
  await expect(strategyFilter.locator('option', { hasText: 'BTC Swing BTC/USDT 4h' })).toHaveCount(0);
  await expect(strategyFilter.locator('option', { hasText: 'ETH/USDT' })).toHaveCount(0);
  await expect(strategyFilter.locator('option', { hasText: 'BTC/USDT' })).toHaveCount(0);
  await expect(strategyFilter.locator('option', { hasText: '1h' })).toHaveCount(0);
  await expect(strategyFilter.locator('option', { hasText: '4h' })).toHaveCount(0);
  await expect(strategyFilter.locator('option', { hasText: 'Estratégia protegida' })).toHaveCount(1);
  await expect(timeFilter.locator('option', { hasText: '1h' })).toHaveCount(1);
  await expect(timeFilter.locator('option', { hasText: '4h' })).toHaveCount(1);

  await strategyFilter.selectOption({ label: 'ema rsi' });

  await expect(page.locator('tbody tr', { hasText: 'BTC Swing' })).toHaveCount(1);
  await expect(page.locator('tbody tr', { hasText: 'Protected BTC Setup' })).toHaveCount(0);

  await strategyFilter.selectOption('ALL');
  await timeFilter.selectOption('4h');

  await expect(page.locator('tbody tr', { hasText: 'BTC Swing' })).toHaveCount(1);
  await expect(page.locator('tbody tr', { hasText: 'Protected BTC Setup' })).toHaveCount(0);
});

test('favorites -> View Results navigates to results page', async ({ page }) => {
  const api = await setupDeterministicApiMocks(page);
  await page.goto('/favorites');

  const viewResults = page
    .locator('.fav-table-shell tbody tr', { hasText: 'BTC Swing' })
    .locator('button[title="View Results"]');
  await expect(viewResults).toBeVisible();
  await viewResults.click();

  expect(api.wasBacktestTriggered()).toBe(true);
  await expect(page).toHaveURL(/\/combo\/results$/);
  await expect(page.getByText('No results found')).toHaveCount(0);
});
