import { expect, test, type Page } from '@playwright/test';

const AUTH_USER = {
  id: 'card-975-user',
  email: 'card975@example.com',
  name: 'Card 975',
  isAdmin: false,
  mustChangePassword: false,
};

const CRYPTO_FAVORITES = [
  {
    id: 201,
    name: 'SOL swing',
    symbol: 'SOL/USDT',
    timeframe: '1d',
    strategy_name: 'ema_rsi',
    parameters: { direction: 'long' },
    metrics: {
      total_return: 0.21,
      total_trades: 12,
      sharpe_ratio: 0.38,
      win_rate: 0.58,
      max_drawdown: 0.11,
    },
    created_at: '2026-01-01T00:00:00Z',
    tier: 2,
    start_date: null,
    end_date: null,
  },
  {
    id: 202,
    name: 'ETH swing',
    symbol: 'ETH/USDT',
    timeframe: '1d',
    strategy_name: 'ema_rsi',
    parameters: { direction: 'long' },
    metrics: {
      total_return: 0.15,
      total_trades: 8,
      sharpe_ratio: 0.31,
      win_rate: 0.5,
      max_drawdown: 0.09,
    },
    created_at: '2026-01-02T00:00:00Z',
    tier: 3,
    start_date: null,
    end_date: null,
  },
];

const OPPORTUNITY_SUBSET = [
  {
    id: 201,
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
    id: 202,
    symbol: 'ETH/USDT',
    asset_type: 'crypto',
    timeframe: '1d',
    direction: 'long',
    template_name: 'ema_rsi',
    name: 'ETH swing',
    notes: null,
    tier: 3,
    parameters: {},
    is_holding: true,
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
    window.localStorage.setItem('auth_access_token', 'test-access-token');
    window.localStorage.setItem('auth_refresh_token', 'test-refresh-token');
    window.localStorage.setItem('auth_user', JSON.stringify(user));
    window.localStorage.setItem('cripto-farol-onboarding-dismissed', '1');
  }, AUTH_USER);
}

async function mockMonitorApis(
  page: Page,
  options: {
    favorites?: unknown;
    favoritesStatus?: number;
    opportunities?: unknown;
    opportunitiesStatus?: number;
  } = {},
) {
  const favoritesBody = options.favorites ?? CRYPTO_FAVORITES;
  const favoritesStatus = options.favoritesStatus ?? 200;
  const opportunitiesBody = options.opportunities ?? OPPORTUNITY_SUBSET;
  const opportunitiesStatus = options.opportunitiesStatus ?? 200;

  await page.route('**/api/**', async (route) => {
    const url = route.request().url();

    if (url.includes('/api/auth/refresh')) {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          accessToken: 'test-access-token',
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
      await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(AUTH_USER) });
      return;
    }
    if (url.match(/\/api\/favorites\/?(\?|$)/)) {
      await route.fulfill({
        status: favoritesStatus,
        contentType: 'application/json',
        body: favoritesStatus === 200
          ? JSON.stringify(favoritesBody)
          : JSON.stringify({ detail: 'fail' }),
      });
      return;
    }
    if (url.includes('/api/opportunities')) {
      await route.fulfill({
        status: opportunitiesStatus,
        contentType: 'application/json',
        body: opportunitiesStatus === 200
          ? JSON.stringify(opportunitiesBody)
          : JSON.stringify({ detail: 'A lista de favoritos não chegou. Isto não significa que não há estratégias.' }),
      });
      return;
    }
    if (url.includes('/api/monitor/preferences')) {
      await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({}) });
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
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ telegramAlertsEnabled: false }),
      });
      return;
    }
    if (url.includes('/api/monitor/spot-market-orders/eligibility')) {
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
  test.describe(`card-975 ${project.name}`, () => {
    test.use({ viewport: { width: project.width, height: project.height } });

    test('first paint shows signals table without catalog-empty copy', async ({ page }) => {
      await mockAuthenticatedSession(page);
      await mockMonitorApis(page);
      await page.goto('/monitor');
      if (project.width < 740) {
        await expect(page.getByTestId('monitor-card-sol-usdt')).toBeVisible();
        await expect(page.getByTestId('monitor-card-eth-usdt')).toBeVisible();
      } else {
        await expect(page.getByTestId('monitor-row-sol-usdt')).toBeVisible();
        await expect(page.getByTestId('monitor-row-eth-usdt')).toBeVisible();
        await expect(page.locator('table.signals').first()).toBeVisible();
      }
      await expect(page.getByText('Nenhum ativo disponível no monitor')).toHaveCount(0);
    });

    test('200 empty with crypto favorites shows load error copy', async ({ page }) => {
      await mockAuthenticatedSession(page);
      await mockMonitorApis(page, { opportunities: [] });
      await page.goto('/monitor');
      await expect(page.getByTestId('monitor-load-error')).toBeVisible();
      await expect(page.getByText('Não foi possível carregar as estratégias.')).toBeVisible();
      await expect(page.getByText('A lista de favoritos não chegou. Isto não significa que não há estratégias.')).toBeVisible();
      await expect(page.getByRole('button', { name: 'Tentar de novo' })).toBeVisible();
      await expect(page.getByText('Nenhum ativo disponível no monitor')).toHaveCount(0);
    });

    test('HTTP failure keeps load error surface', async ({ page }) => {
      await mockAuthenticatedSession(page);
      await mockMonitorApis(page, { opportunitiesStatus: 503 });
      await page.goto('/monitor');
      await expect(page.getByTestId('monitor-load-error')).toBeVisible();
      await expect(page.getByText('Nenhum ativo disponível no monitor')).toHaveCount(0);
    });

    test('favorites failure with empty opportunities shows load error not loading', async ({ page }) => {
      await mockAuthenticatedSession(page);
      await mockMonitorApis(page, { favoritesStatus: 500, opportunities: [] });
      await page.goto('/monitor');
      await expect(page.getByText('Carregando sinais...')).toHaveCount(0);
      await expect(page.getByTestId('monitor-load-error')).toBeVisible();
      await expect(page.getByText('Nenhum ativo disponível no monitor')).toHaveCount(0);
    });

    test('filter empty uses filter copy not catalog empty', async ({ page }) => {
      await mockAuthenticatedSession(page);
      await mockMonitorApis(page);
      await page.goto('/monitor');
      await page.getByPlaceholder('Buscar par, estratégia, tag...').fill('ZZZZ');
      await expect(page.getByTestId('monitor-filter-empty')).toBeVisible();
      await expect(page.getByText('Não há resultado com estes filtros.')).toBeVisible();
      await expect(page.getByText('Nenhum ativo disponível no monitor')).toHaveCount(0);
    });

    test('real catalog empty when session has no crypto favorites', async ({ page }) => {
      await mockAuthenticatedSession(page);
      await mockMonitorApis(page, { favorites: [], opportunities: [] });
      await page.goto('/monitor');
      await expect(page.getByText('Nenhum ativo disponível no monitor')).toBeVisible();
      await expect(page.getByTestId('monitor-load-error')).toHaveCount(0);
    });
  });
}
