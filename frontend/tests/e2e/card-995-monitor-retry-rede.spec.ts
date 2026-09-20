import { expect, test, type Page } from '@playwright/test';

const AUTH_USER = {
  id: 'card-995-user',
  email: 'card995@example.com',
  name: 'Card 995',
  isAdmin: false,
  mustChangePassword: false,
};

const CRYPTO_FAVORITES = [
  {
    id: 301,
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
    id: 302,
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
    id: 301,
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
  {
    id: 302,
    symbol: 'ETH/USDT',
    asset_type: 'crypto',
    timeframe: '1d',
    direction: 'long',
    template_name: 'ema_rsi',
    name: 'ETH swing',
    notes: null,
    tier: 3,
    parameters: {},
    is_holding: false,
    distance_to_next_status: 0.55,
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
    entry_price: 2000,
    stop_price: 1900,
    distance_to_stop_pct: 3.1,
    status: 'HOLD',
    badge: 'info',
    message: 'Em Hold',
    last_price: 2100,
    timestamp: '2026-09-18T00:00:00Z',
    details: {},
  },
];

async function mockAuthenticatedSession(page: Page) {
  await page.addInitScript((user) => {
    window.localStorage.setItem('auth_access_token', 'stale-access-token');
    window.localStorage.setItem('auth_refresh_token', 'test-refresh-token');
    window.localStorage.setItem('auth_user', JSON.stringify(user));
    window.localStorage.setItem('cripto-farol-onboarding-dismissed', '1');
  }, AUTH_USER);
}

type MockOptions = {
  opportunitiesNetworkFailUntil?: number;
  opportunitiesAlwaysNetworkFail?: boolean;
  preferencesFail?: boolean;
  refreshFails?: boolean;
};

async function mockMonitorApis(page: Page, options: MockOptions = {}) {
  let opportunityHits = 0;

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
      await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(CRYPTO_FAVORITES) });
      return;
    }

    if (url.includes('/api/opportunities')) {
      opportunityHits += 1;
      if (options.opportunitiesAlwaysNetworkFail) {
        await route.abort('failed');
        return;
      }
      if (options.opportunitiesNetworkFailUntil && opportunityHits <= options.opportunitiesNetworkFailUntil) {
        await route.abort('failed');
        return;
      }
      await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(OPPORTUNITIES) });
      return;
    }

    if (url.includes('/api/monitor/preferences')) {
      if (options.preferencesFail) {
        await route.fulfill({ status: 500, contentType: 'application/json', body: JSON.stringify({ detail: 'fail' }) });
        return;
      }
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

    await route.fulfill({ status: 200, contentType: 'application/json', body: '{}' });
  });
}

for (const project of [
  { name: 'desktop', width: 1280, height: 800 },
  { name: 'mobile', width: 390, height: 844 },
] as const) {
  test.describe(`card-995 ${project.name}`, () => {
    test.use({ viewport: { width: project.width, height: project.height } });

    test('transient network cut stays on loading then lists signals', async ({ page }) => {
      await mockAuthenticatedSession(page);
      await mockMonitorApis(page, { opportunitiesNetworkFailUntil: 1 });
      await page.goto('/monitor');
      await expect(page.getByTestId('monitor-load-error')).toHaveCount(0);
      if (await page.getByTestId('monitor-loading').isVisible()) {
        await expect(page.getByText('Carregando sinais...')).toBeVisible();
        await expect(page.locator('.kpi-val[data-kpi-pending="true"]')).toHaveCount(4);
      }
      if (project.width < 740) {
        await expect(page.getByTestId('monitor-card-sol-usdt')).toBeVisible({ timeout: 15_000 });
      } else {
        await expect(page.getByTestId('monitor-row-sol-usdt')).toBeVisible({ timeout: 15_000 });
        await expect(page.locator('table.signals').first()).toBeVisible({ timeout: 15_000 });
      }
      await expect(page.getByText('Não foi possível carregar as estratégias.')).toHaveCount(0);
      await expect(page.getByText('Não foi possível carregar preferências do monitor.')).toHaveCount(0);
    });

    test('persistent network failure shows #975 after wait', async ({ page }) => {
      await mockAuthenticatedSession(page);
      await mockMonitorApis(page, { opportunitiesAlwaysNetworkFail: true });
      await page.goto('/monitor');
      await expect(page.getByTestId('monitor-load-error')).toBeVisible({ timeout: 10_000 });
      await expect(page.getByTestId('monitor-load-error').getByText('Não foi possível carregar as estratégias.')).toBeVisible();
      await expect(page.getByText('Nenhum ativo disponível no monitor')).toHaveCount(0);
      await expect(page.locator('.kpi-val[data-kpi-pending="true"]')).toHaveCount(4);
    });

    test('retry rereads without refresh=true', async ({ page }) => {
      await mockAuthenticatedSession(page);
      await mockMonitorApis(page, { opportunitiesAlwaysNetworkFail: true });
      await page.goto('/monitor');
      await expect(page.getByTestId('monitor-load-error')).toBeVisible({ timeout: 10_000 });

      let retryUrl = '';
      await page.unroute('**/api/opportunities**');
      await page.route('**/api/opportunities**', async (route) => {
        retryUrl = route.request().url();
        await route.abort('failed');
      });

      await page.getByTestId('monitor-retry').click();
      await expect.poll(() => retryUrl, { timeout: 10_000 }).not.toBe('');
      expect(retryUrl).not.toContain('refresh=true');
      expect(await page.getByTestId('monitor-retry').getAttribute('data-load-mode')).toBe('reread');
    });

    test('Atualizar sends refresh=true', async ({ page }) => {
      await mockAuthenticatedSession(page);
      await mockMonitorApis(page);
      let refreshUrl = '';
      await page.route('**/api/opportunities**', async (route) => {
        refreshUrl = route.request().url();
        await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(OPPORTUNITIES) });
      });
      await page.goto('/monitor');
      await page.getByTestId('monitor-refresh').click();
      await expect.poll(() => refreshUrl).toContain('refresh=true');
      expect(await page.getByTestId('monitor-refresh').getAttribute('data-load-mode')).toBe('recompute');
    });

    test('preferences failure does not toast when list succeeds', async ({ page }) => {
      await mockAuthenticatedSession(page);
      await mockMonitorApis(page, { preferencesFail: true });
      await page.goto('/monitor');
      if (project.width < 740) {
        await expect(page.getByTestId('monitor-card-sol-usdt')).toBeVisible({ timeout: 15_000 });
      } else {
        await expect(page.getByTestId('monitor-row-sol-usdt')).toBeVisible({ timeout: 15_000 });
      }
      await expect(page.getByText('Não foi possível carregar preferências do monitor.')).toHaveCount(0);
    });

    test('dead session redirects to login', async ({ page }) => {
      await mockAuthenticatedSession(page);
      await mockMonitorApis(page, { refreshFails: true });
      await page.route('**/api/opportunities**', async (route) => {
        await route.fulfill({ status: 401, contentType: 'application/json', body: JSON.stringify({ detail: 'stale' }) });
      });
      await page.goto('/monitor');
      await expect(page).toHaveURL(/\/login/, { timeout: 15_000 });
      await expect(page.getByTestId('monitor-load-error')).toHaveCount(0);
    });
  });
}
