import { chromium } from '@playwright/test';

const AUTH_USER = {
  id: 'test-user',
  email: 'test@example.com',
  name: 'Test User',
  isAdmin: false,
};

const baseURL = 'http://127.0.0.1:4175';
const outDir = '/root/.openclaw/workspace/crypto/qa_artifacts/playwright/card-96-qa-turn-current';

async function captureScenario(name, opportunitiesPayload, preferencesPayload) {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({ viewport: { width: 390, height: 844 } });
  const page = await context.newPage();

  await page.addInitScript((user) => {
    window.localStorage.setItem('auth_access_token', 'test-access-token');
    window.localStorage.setItem('auth_refresh_token', 'test-refresh-token');
    window.localStorage.setItem('auth_user', JSON.stringify(user));
  }, AUTH_USER);

  await page.route('**/*', (route) => {
    const url = new URL(route.request().url());
    if (url.hostname === '127.0.0.1' || url.hostname === 'localhost') {
      return route.continue();
    }
    return route.abort('blockedbyclient');
  });

  await page.route('**/api/auth/me', (route) =>
    route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(AUTH_USER) })
  );
  await page.route('**/api/favorites/', (route) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify([
        {
          id: 5,
          name: 'BTC Trend',
          symbol: 'BTC/USDT',
          timeframe: '1d',
          strategy_name: 'multi_ma_crossover',
          parameters: {},
          metrics: {},
          created_at: '2026-04-16T00:00:00Z',
          tier: 1,
        },
      ]),
    })
  );
  await page.route('**/api/opportunities/**', (route) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify([opportunitiesPayload]),
    })
  );
  await page.route('**/api/monitor/preferences', (route) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(preferencesPayload),
    })
  );
  await page.route('**/api/market/candles**', (route) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        candles: [
          { timestamp_utc: '2026-04-16T00:00:00Z', open: 100, high: 102, low: 99, close: 101, volume: 1000 },
          { timestamp_utc: '2026-04-16T01:00:00Z', open: 101, high: 103, low: 100, close: 102, volume: 1100 },
        ],
      }),
    })
  );

  await page.goto(`${baseURL}/monitor`, { waitUntil: 'domcontentloaded' });
  const card = page.getByTestId('monitor-card-btc-usdt');
  await card.waitFor({ state: 'visible', timeout: 20000 });
  await card.screenshot({ path: `${outDir}/${name}-card.png` });
  await card.click();
  const dialog = page.getByRole('dialog');
  await dialog.waitFor({ state: 'visible', timeout: 20000 });

  await page.screenshot({ path: `${outDir}/${name}-modal.png`, fullPage: true });
  const historyVisible = await page.getByTestId('chart-modal-signal-history').isVisible().catch(() => false);
  const mismatchText = await page.getByText('EXIT bloqueado: timeframe da estratégia não corresponde ao timeframe exibido.').count().catch(() => 0);
  const markerText = await page.getByText('Markers aligned with chart timeframe.').count().catch(() => 0);
  const signalContext = await page.getByText('Resolved state').count().catch(() => 0);

  await page.close();
  await context.close();
  await browser.close();

  return {
    historyVisible,
    mismatchText: mismatchText > 0,
    markerText: markerText > 0,
    signalContext: signalContext > 0,
  };
}

(async () => {
  const mismatch = await captureScenario(
    'mismatch',
    {
      id: 4,
      symbol: 'BTC/USDT',
      timeframe: '1d',
      template_name: 'multi_ma_crossover',
      name: 'BTC Trend',
      notes: '',
      tier: 1,
      parameters: { direction: 'long', ema_short: 18, sma_medium: 20, sma_long: 35, stop_loss: 0.042 },
      indicator_values: { short: 71346.57, medium: 69796.7, long: 70294.6, open: 74131.55, close: 74809.99 },
      indicator_values_candle_time: '2026-04-15T00:00:00+00:00',
      is_holding: false,
      distance_to_next_status: 2.22,
      next_status_label: 'entry',
      status: 'EXIT_SIGNAL',
      message: '',
      last_price: 74924,
      timestamp: '2026-04-16T04:00:00Z',
      details: {},
    },
    {
      __global__: { in_portfolio: false, card_mode: 'strategy', price_timeframe: '1d', theme: 'dark-green' },
      'BTC/USDT': { in_portfolio: true, card_mode: 'strategy', price_timeframe: '1h', theme: 'dark-green' },
    }
  );

  const history = await captureScenario(
    'history',
    {
      id: 5,
      symbol: 'BTC/USDT',
      timeframe: '1d',
      template_name: 'multi_ma_crossover',
      name: 'BTC Trend History',
      notes: '',
      tier: 1,
      parameters: { direction: 'long', ema_short: 18, sma_medium: 20, sma_long: 35, stop_loss: 0.042 },
      indicator_values: { short: 71346.57, medium: 69796.7, long: 70294.6, open: 74131.55, close: 74809.99 },
      indicator_values_candle_time: '2026-04-15T00:00:00+00:00',
      is_holding: true,
      distance_to_next_status: 0.88,
      next_status_label: 'exit',
      status: 'HOLDING',
      message: 'Em Hold. Distância para saída: 0.88%',
      last_price: 74924,
      timestamp: '2026-04-16T00:00:00Z',
      details: {},
      signal_history: [
        { timestamp: '2026-04-10T00:00:00+00:00', signal: 1, type: 'entry', reason: 'entry', price: 70210.15 },
        { timestamp: '2026-04-13T00:00:00+00:00', signal: -1, type: 'exit', reason: 'exit_logic', price: 72150.42 },
        { timestamp: '2026-04-15T00:00:00+00:00', signal: 1, type: 'entry', reason: 'entry', price: 73980.37 },
      ],
    },
    {
      __global__: { in_portfolio: false, card_mode: 'strategy', price_timeframe: '1d', theme: 'dark-green' },
      'BTC/USDT': { in_portfolio: true, card_mode: 'strategy', price_timeframe: '1d', theme: 'dark-green' },
    }
  );

  console.log(JSON.stringify({ mismatch, history }));
})();
