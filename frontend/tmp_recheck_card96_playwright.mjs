import { chromium } from '@playwright/test';
import fs from 'node:fs/promises';
import path from 'node:path';

const baseURL = 'http://127.0.0.1:4175';
const outDir = '/root/.openclaw/workspace/crypto/frontend/qa_artifacts/playwright/card-96-playwright-verification';
await fs.mkdir(outDir, { recursive: true });

const AUTH_USER = { id: 'test-user', email: 'test@example.com', name: 'Test User', isAdmin: false };

async function setupCommonRoutes(page) {
  await page.addInitScript((user) => {
    window.localStorage.setItem('auth_access_token', 'test-access-token');
    window.localStorage.setItem('auth_refresh_token', 'test-refresh-token');
    window.localStorage.setItem('auth_user', JSON.stringify(user));
  }, AUTH_USER);

  await page.route('**/*', (route) => {
    const url = new URL(route.request().url());
    if (url.hostname === '127.0.0.1' || url.hostname === 'localhost') return route.continue();
    return route.abort('blockedbyclient');
  });

  await page.route('**/api/auth/me', (route) =>
    route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(AUTH_USER) })
  );

  await page.route('**/api/favorites/', (route) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify([{ id: 4, name: 'BTC Trend', symbol: 'BTC/USDT', timeframe: '1d', strategy_name: 'multi_ma_crossover', parameters: {}, metrics: {}, created_at: '2026-04-15T00:00:00Z', tier: 1 }]),
    })
  );

  await page.route('**/api/monitor/preferences', (route) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        __global__: { in_portfolio: false, card_mode: 'strategy', price_timeframe: '1d', theme: 'dark-green' },
        'BTC/USDT': { in_portfolio: true, card_mode: 'strategy', price_timeframe: '1h', theme: 'dark-green' },
      }),
    })
  );

  await page.route('**/api/market/candles**', (route) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ candles: [
          { timestamp_utc: '2026-04-16T01:00:00Z', open: 74850, high: 74910, low: 74790, close: 74880, volume: 82.413 },
          { timestamp_utc: '2026-04-16T02:00:00Z', open: 74880, high: 74940, low: 74820, close: 74895, volume: 91.127 },
          { timestamp_utc: '2026-04-16T03:00:00Z', open: 74895, high: 75005, low: 74865, close: 74905, volume: 104.252 },
          { timestamp_utc: '2026-04-16T04:00:00Z', open: 74905, high: 75010, low: 74839, close: 74930.98, volume: 112.613 },
        ]}),
    })
  );
}

function opportunitiesPayload(displayTf) {
  const isAligned = displayTf === '1d';
  return {
    status: 200,
    contentType: 'application/json',
    body: JSON.stringify([
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
        status: isAligned ? 'WAIT' : 'EXIT_SIGNAL',
        message: '',
        last_price: 74924,
        timestamp: '2026-04-16T04:00:00Z',
        details: {},
        signal_history: [
          { timestamp: '2026-04-10T00:00:00+00:00', signal: 1, type: 'entry', reason: 'entry', price: 70210.15 },
          { timestamp: '2026-04-13T00:00:00+00:00', signal: -1, type: 'exit', reason: 'exit_logic', price: 72150.42 },
        ],
      },
    ]),
  };
}

const browser = await chromium.launch({ headless: true });
const page = await browser.newPage({ viewport: { width: 1280, height: 1800 } });
await setupCommonRoutes(page);

await page.route('**/api/opportunities/**', () => opportunitiesPayload('1h'));
await page.goto(baseURL + '/monitor', { waitUntil: 'domcontentloaded' });
await page.waitForSelector("[data-testid='monitor-card-btc-usdt']", { timeout: 30000 });
const card = page.getByTestId('monitor-card-btc-usdt').first();
await card.screenshot({ path: path.join(outDir, '01-mismatch-card.png') });
await card.click();
const dialog = page.getByRole('dialog');
await dialog.waitFor({ state: 'visible' });
const mismatchText = await dialog.innerText();
await dialog.screenshot({ path: path.join(outDir, '02-mismatch-modal.png') });

await page.unroute('**/api/opportunities/**');
await page.route('**/api/opportunities/**', () => opportunitiesPayload('1d'));
await page.goto(baseURL + '/monitor', { waitUntil: 'domcontentloaded' });
await page.waitForSelector("[data-testid='monitor-card-btc-usdt']", { timeout: 30000 });
await card.click();
await dialog.waitFor({ state: 'visible' });
const historyText = await dialog.innerText();
await dialog.screenshot({ path: path.join(outDir, '03-history-modal.png') });

await fs.writeFile(path.join(outDir, '04-mismatch-summary.txt'), mismatchText);
await fs.writeFile(path.join(outDir, '05-history-summary.txt'), historyText);
await fs.writeFile(path.join(outDir, '06-observations.json'), JSON.stringify({ mismatchText, historyText }, null, 2));
await browser.close();
