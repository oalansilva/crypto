import { expect, test, type Page } from '@playwright/test';

const AUTH_USER = {
  id: 'card-983-user',
  email: 'card983@example.com',
  name: 'Card 983',
  isAdmin: true,
  mustChangePassword: false,
};

const CRYPTO_FAVORITES = [
  {
    id: 101,
    name: 'SOL swing',
    symbol: 'SOL/USDT',
    timeframe: '1d',
    strategy_name: 'ema_rsi',
    parameters: { direction: 'long' },
    metrics: { total_return: 0.21, total_trades: 12, sharpe_ratio: 0.38, win_rate: 0.58, max_drawdown: 0.11 },
    created_at: '2026-01-01T00:00:00Z',
    tier: 2,
  },
  {
    id: 102,
    name: 'ETH swing',
    symbol: 'ETH/USDT',
    timeframe: '1d',
    strategy_name: 'ema_rsi',
    parameters: { direction: 'long' },
    metrics: { total_return: 0.15, total_trades: 8, sharpe_ratio: 0.31, win_rate: 0.5, max_drawdown: 0.09 },
    created_at: '2026-01-02T00:00:00Z',
    tier: 3,
  },
];

const OPPORTUNITIES = [
  {
    id: 101,
    symbol: 'SOL/USDT',
    asset_type: 'crypto',
    timeframe: '1d',
    direction: 'long',
    template_name: 'ema_rsi',
    name: 'SOL swing',
    notes: null,
    tier: 2,
    parameters: {},
    is_holding: true,
    distance_to_next_status: 0.42,
    next_status_label: 'exit',
    indicator_values: null,
    indicator_values_candle_time: null,
    signal_history: [],
    is_strategy_protected: false,
    strategy_display_name: 'EMA RSI',
    strategy_description: null,
    strategy_transparency: null,
    action_label: null,
    entry_action_label: null,
    exit_action_label: null,
    next_action_label: null,
    entry_price: 100,
    stop_price: 90,
    distance_to_stop_pct: 4.2,
    status: 'HOLD',
    badge: 'info',
    message: 'Em Hold',
    last_price: 105,
    timestamp: '2026-09-18T00:00:00Z',
    details: {},
  },
];

const WALLET_BALANCES = {
  balances: [
    { asset: 'BTC', free: 0.1, locked: 0, total: 0.1, value_usd: 5000 },
    { asset: 'ETH', free: 1, locked: 0, total: 1, value_usd: 3000 },
  ],
  total_usd: 8000,
  as_of: '2026-03-20T12:00:00Z',
};

async function mockAuthenticatedSession(page: Page) {
  await page.addInitScript((user) => {
    window.localStorage.setItem('auth_access_token', 'stale-access-token');
    window.localStorage.setItem('auth_refresh_token', 'test-refresh-token');
    window.localStorage.setItem('auth_user', JSON.stringify(user));
    window.localStorage.setItem('cripto-farol-onboarding-dismissed', '1');
  }, AUTH_USER);
}

async function mockRenewalApis(
  page: Page,
  options: {
    favoritesTransient401?: boolean;
    favoritesNetworkFail?: boolean;
    refreshFails?: boolean;
  } = {},
) {
  let favoritesHits = 0;

  await page.route('**/api/**', async (route) => {
    const url = route.request().url();

    if (url.includes('/api/auth/refresh')) {
      if (options.refreshFails) {
        await route.fulfill({ status: 401, contentType: 'application/json', body: JSON.stringify({ detail: 'expired' }) });
        return;
      }
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          accessToken: 'fresh-access-token',
          refreshToken: 'test-refresh-token',
          id: AUTH_USER.id,
          userId: AUTH_USER.id,
          email: AUTH_USER.email,
          name: AUTH_USER.name,
          isAdmin: AUTH_USER.isAdmin,
          mustChangePassword: AUTH_USER.mustChangePassword,
          expiresIn: 3600,
        }),
      });
      return;
    }

    if (url.includes('/api/auth/me')) {
      if (options.refreshFails) {
        await route.fulfill({ status: 401, contentType: 'application/json', body: JSON.stringify({ detail: 'stale' }) });
        return;
      }
      await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(AUTH_USER) });
      return;
    }

    if (url.match(/\/api\/favorites\/?(\?|$)/)) {
      favoritesHits += 1;
      if (options.favoritesNetworkFail) {
        await route.fulfill({ status: 500, contentType: 'application/json', body: JSON.stringify({ detail: 'fail' }) });
        return;
      }
      if (options.favoritesTransient401 && favoritesHits === 1) {
        await route.fulfill({ status: 401, contentType: 'application/json', body: JSON.stringify({ detail: 'stale' }) });
        return;
      }
      await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(CRYPTO_FAVORITES) });
      return;
    }

    if (url.includes('/api/opportunities')) {
      await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(OPPORTUNITIES) });
      return;
    }

    if (url.includes('/api/external/binance/spot/balances')) {
      await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(WALLET_BALANCES) });
      return;
    }

    if (url.includes('/api/monitor/preferences')) {
      await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({}) });
      return;
    }

    if (url.includes('/api/monitor/spot-market-orders/eligibility')) {
      await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ items: [] }) });
      return;
    }

    if (url.includes('/api/user/binance-credentials')) {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ configured: false, api_key_masked: null }),
      });
      return;
    }

    if (url.includes('/api/users/me/telegram-settings')) {
      await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ telegramAlertsEnabled: false }) });
      return;
    }

    if (url.includes('/api/health')) {
      await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ status: 'ok' }) });
      return;
    }

    if (url.includes('/api/portfolio/kpi')) {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          pnl_today_pct: 1,
          pnl_today_vs_btc_pct: 0.5,
          drawdown_30d_pct: 2,
          drawdown_peak_date: null,
          btc_change_24h_pct: 0.2,
          total_usd: 1000,
          btc_value: 500,
          usdt_value: 300,
          eth_value: 200,
          other_usd: 0,
          _history_insufficient: false,
        }),
      });
      return;
    }

    if (url.includes('/api/market/prices')) {
      await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ prices: [], fetched_at: null }) });
      return;
    }

    if (url.includes('/api/workflow/kanban/changes')) {
      await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ items: [] }) });
      return;
    }

    await route.fulfill({ status: 200, contentType: 'application/json', body: '{}' });
  });
}

for (const project of [
  { name: 'desktop', width: 1280, height: 800 },
  { name: 'mobile', width: 390, height: 844 },
] as const) {
  test.describe(`card-983 ${project.name}`, () => {
    test.use({ viewport: { width: project.width, height: project.height } });

    test('renewal window lists favorites without #970 load error', async ({ page }) => {
      await mockAuthenticatedSession(page);
      await mockRenewalApis(page, { favoritesTransient401: true });
      await page.goto('/favorites');
      await expect(page.getByTestId('favorites-renewal-ok')).toBeVisible();
      await expect(page.getByText('Não foi possível carregar as estratégias favoritas.')).toHaveCount(0);
      await expect(page.getByText('Nenhuma estratégia favorita encontrada')).toHaveCount(0);
      if (project.width < 500) {
        await expect(page.getByTestId('favorite-101-mobile')).toBeVisible();
      } else {
        await expect(page.getByTestId('favorite-101')).toBeVisible();
      }
    });

    test('real network failure keeps #970 retry copy', async ({ page }) => {
      await mockAuthenticatedSession(page);
      await mockRenewalApis(page, { favoritesNetworkFail: true });
      await page.goto('/favorites');
      const errorSurface = project.width < 500
        ? page.locator('.fav-mobile-list')
        : page.locator('.fav-table-shell');
      await expect(errorSurface.getByTestId('favorites-load-error')).toBeVisible();
      await expect(page.getByText('Nenhuma estratégia favorita encontrada')).toHaveCount(0);
    });

    test('home KPI survives transient favorites 401', async ({ page }) => {
      await mockAuthenticatedSession(page);
      await mockRenewalApis(page, { favoritesTransient401: true });
      await page.goto('/home');
      await expect(page.getByTestId('home-kpi-best-strategy')).toContainText('ema_rsi');
      await expect(page.getByText('Não foi possível carregar `/api/favorites`.')).toHaveCount(0);
    });

    test('monitor lists signals during renewal', async ({ page }) => {
      await mockAuthenticatedSession(page);
      await mockRenewalApis(page, { favoritesTransient401: true });
      await page.goto('/monitor');
      await page.getByTestId('monitor-filter-all').click();
      if (project.width < 740) {
        await expect(page.getByTestId('monitor-card-sol-usdt')).toBeVisible();
      } else {
        await expect(page.locator('table.signals').first()).toBeVisible();
      }
      await expect(page.getByText('Não foi possível carregar as estratégias.')).toHaveCount(0);
    });

    test('wallet shows balances during renewal', async ({ page }) => {
      await mockAuthenticatedSession(page);
      await mockRenewalApis(page, { favoritesTransient401: true });
      await page.goto('/external/balances');
      await expect(page.getByTestId('wallet-renewal-ok')).toBeVisible();
      await expect(page.getByText('Erro ao carregar')).toHaveCount(0);
    });

    test('dead refresh sends operator to login', async ({ page }) => {
      await mockAuthenticatedSession(page);
      await mockRenewalApis(page, { refreshFails: true, favoritesTransient401: true });
      await page.goto('/favorites');
      await expect(page).toHaveURL(/\/login/, { timeout: 15000 });
      await expect(page.getByTestId('favorites-load-error')).toHaveCount(0);
    });
  });
}
