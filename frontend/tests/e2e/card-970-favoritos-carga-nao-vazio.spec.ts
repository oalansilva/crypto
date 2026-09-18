import { expect, test, type Page } from '@playwright/test';

const AUTH_USER = {
  id: 'card-970-user',
  email: 'card970@example.com',
  name: 'Card 970',
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
    id: 102,
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

async function mockAuthenticatedSession(page: Page) {
  await page.addInitScript((user) => {
    window.localStorage.setItem('auth_access_token', 'test-access-token');
    window.localStorage.setItem('auth_refresh_token', 'test-refresh-token');
    window.localStorage.setItem('auth_user', JSON.stringify(user));
  }, AUTH_USER);
}

const SLIM_CRYPTO_FAVORITES = [
  {
    ...CRYPTO_FAVORITES[0],
    metrics: {
      total_return: 0.21,
      total_trades: 12,
      sharpe_ratio: 0.38,
      win_rate: 0.58,
      max_drawdown: 0.11,
      trades_history_cached: true,
    },
  },
];

const SLIM_TRADES_PAYLOAD = {
  favorite_id: 101,
  trades: [
    {
      entry_time: '2026-01-01T00:00:00Z',
      exit_time: '2026-01-02T00:00:00Z',
      entry_price: 100,
      exit_price: 110,
      type: 'long',
    },
  ],
  metrics: {
    total_return: 0.21,
    total_trades: 1,
    sharpe_ratio: 0.38,
    win_rate: 1,
    max_drawdown: 0.05,
    trades_history_cached: true,
    trades_metrics_match: true,
  },
  metrics_match: true,
  metrics_deltas: {},
  regenerated: true,
  candles: [
    {
      timestamp_utc: '2026-01-01T00:00:00Z',
      open: 100,
      high: 110,
      low: 95,
      close: 105,
    },
  ],
  indicator_data: {},
  execution_mode: 'favorite_regenerated',
};

async function mockFavoritesApi(
  page: Page,
  options: {
    favorites?: unknown;
    favoritesStatus?: number;
    opportunitiesStatus?: number;
    trackTrades?: boolean;
    tradesDelayMs?: number;
  } = {},
) {
  const favoritesBody = options.favorites ?? CRYPTO_FAVORITES;
  const favoritesStatus = options.favoritesStatus ?? 200;
  const opportunitiesStatus = options.opportunitiesStatus ?? 200;
  let favoriteTradesTriggered = false;

  await page.route('**/api/**', async (route) => {
    const url = route.request().url();

    if (url.match(/\/api\/favorites\/\d+\/trades(?:\?|$)/)) {
      if (options.trackTrades) {
        favoriteTradesTriggered = true;
      }
      if (options.tradesDelayMs) {
        await new Promise((resolve) => setTimeout(resolve, options.tradesDelayMs));
      }
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(SLIM_TRADES_PAYLOAD),
      });
      return;
    }
    if (url.includes('/api/market/candles')) {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          symbol: 'SOL/USDT',
          timeframe: '1d',
          count: 1,
          candles: SLIM_TRADES_PAYLOAD.candles,
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
        body: favoritesStatus === 200 ? JSON.stringify(favoritesBody) : JSON.stringify({ detail: 'fail' }),
      });
      return;
    }
    if (url.includes('/api/opportunities')) {
      await route.fulfill({
        status: opportunitiesStatus,
        contentType: 'application/json',
        body: opportunitiesStatus === 200 ? '[]' : JSON.stringify({ detail: 'fail' }),
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
    await route.fulfill({ status: 200, contentType: 'application/json', body: '{}' });
  });

  return {
    wasFavoriteTradesTriggered: () => favoriteTradesTriggered,
  };
}

for (const project of [
  { name: 'desktop', width: 1280, height: 800 },
  { name: 'mobile', width: 390, height: 844 },
] as const) {
  test.describe(`card-970 ${project.name}`, () => {
    test.use({ viewport: { width: project.width, height: project.height } });

    test('happy path lists crypto pairs without catalog-empty copy', async ({ page }) => {
      await mockAuthenticatedSession(page);
      await mockFavoritesApi(page);
      await page.goto('/favorites');
      await expect(page.getByRole('heading', { name: 'Estratégias favoritas' })).toBeVisible();
      if (project.width < 500) {
        await expect(page.getByTestId('favorite-101-mobile')).toBeVisible();
      } else {
        await expect(page.getByTestId('favorite-101')).toBeVisible();
      }
      await expect(page.getByText('Nenhuma estratégia favorita encontrada')).toHaveCount(0);
      await expect(page.getByText('0 estratégias carregadas')).toHaveCount(0);
    });

    test('load error shows retry without catalog-empty copy', async ({ page }) => {
      await mockAuthenticatedSession(page);
      await mockFavoritesApi(page, { favoritesStatus: 500 });
      await page.goto('/favorites');
      const errorSurface = project.width < 500
        ? page.locator('.fav-mobile-list')
        : page.locator('.fav-table-shell');
      await expect(errorSurface.getByTestId('favorites-load-error')).toBeVisible();
      await expect(errorSurface.getByRole('button', { name: 'Tentar de novo' })).toBeVisible();
      await expect(page.getByText('Nenhuma estratégia favorita encontrada')).toHaveCount(0);
    });

    test('filter empty uses filter copy', async ({ page }) => {
      await mockAuthenticatedSession(page);
      await mockFavoritesApi(page);
      await page.goto('/favorites');
      await page.getByPlaceholder('Buscar por símbolo ou estratégia').fill('ZZZ');
      const filterSurface = project.width < 500
        ? page.locator('.fav-mobile-list')
        : page.locator('.fav-table-shell');
      await expect(filterSurface.getByTestId('favorites-filter-empty')).toBeVisible();
      await expect(page.getByText('Nenhuma estratégia favorita encontrada')).toHaveCount(0);
    });

    test('monitor load failure is not catalog empty', async ({ page }) => {
      await mockAuthenticatedSession(page);
      await mockFavoritesApi(page, { opportunitiesStatus: 500 });
      await page.goto('/monitor');
      await expect(page.getByTestId('monitor-load-error')).toBeVisible();
      await expect(page.getByText('Nenhum ativo disponível no monitor')).toHaveCount(0);
    });

    test('empty crypto catalog with Todas tier and empty search', async ({ page }) => {
      await mockAuthenticatedSession(page);
      await mockFavoritesApi(page, { favorites: [] });
      await page.goto('/favorites');
      await expect(page.getByRole('heading', { name: 'Estratégias favoritas' })).toBeVisible();
      await expect(page.getByRole('button', { name: /Todas 0/i })).toBeVisible();
      await expect(page.getByPlaceholder('Buscar por símbolo ou estratégia')).toHaveValue('');
      const emptySurface = project.width < 500
        ? page.locator('.fav-mobile-list')
        : page.locator('.fav-table-shell');
      await expect(emptySurface.getByText('Nenhuma estratégia favorita encontrada.')).toBeVisible();
      await expect(page.getByTestId('favorites-filter-empty')).toHaveCount(0);
      await expect(page.getByTestId('favorites-load-error')).toHaveCount(0);
    });

    test('analysis after slim list payload loads trades from API', async ({ page }) => {
      await mockAuthenticatedSession(page);
      const api = await mockFavoritesApi(page, {
        favorites: SLIM_CRYPTO_FAVORITES,
        trackTrades: true,
        tradesDelayMs: 3500,
      });
      await page.goto('/favorites');
      const openAnalysis = project.width < 500
        ? page.getByTestId('favorite-101-mobile').getByRole('button', { name: /Analisar/i })
        : page.getByTestId('open-chart-101');
      await expect(openAnalysis).toBeVisible();
      await openAnalysis.click();
      await expect(page).toHaveURL(/\/combo\/results$/);
      expect(api.wasFavoriteTradesTriggered()).toBe(true);
      await expect(page.getByText('Lista de operações')).toBeVisible();
      await expect(page.getByRole('button', { name: /Voltar aos favoritos/i })).toBeVisible();
    });
  });
}
