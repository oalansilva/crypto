import playwright from '../frontend/node_modules/@playwright/test/index.js';
import fs from 'node:fs/promises';
import path from 'node:path';

const { chromium, expect } = playwright;
const AUTH_USER = { id: 'test-user', email: 'test@example.com', name: 'Test User', isAdmin: false };
const outDir = '/root/.openclaw/workspace/crypto/qa_artifacts/playwright/card-96-mock-observation';
await fs.mkdir(outDir, { recursive: true });
const browser = await chromium.launch({ headless: true });
const page = await browser.newPage({ viewport: { width: 1440, height: 1100 } });

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

await page.route('**/api/auth/me', (route) => route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(AUTH_USER) }));
await page.route('**/api/favorites/', (route) => route.fulfill({
  status: 200, contentType: 'application/json', body: JSON.stringify([{ id: 2, name: 'BTC Trend', symbol: 'BTC/USDT', timeframe: '1d', strategy_name: 'multi_ma_crossover', parameters: {}, metrics: {}, created_at: '2025-01-01T00:00:00Z', tier: 1 }])
}));
await page.route('**/api/opportunities/**', (route) => route.fulfill({
  status: 200,
  contentType: 'application/json',
  body: JSON.stringify([{ id: 2, symbol: 'BTC/USDT', timeframe: '1d', template_name: 'multi_ma_crossover', name: 'multi_ma_crossover - BTC/USDT 1d (00:12:26)', notes: '', tier: 1, parameters: { direction: 'long', ema_short: 18, sma_medium: 20, sma_long: 35, stop_loss: 0.042 }, is_holding: false, distance_to_next_status: 2.22, next_status_label: 'wait', status: 'EXIT', message: 'Exit signaled', last_price: 74924, timestamp: '2026-04-16T04:00:00Z', details: { indicator_values: { short: 71346.57, medium: 69796.70, long: 70294.60, open: 74131.55, close: 74809.99 }, indicator_values_candle_time: '2026-04-15T00:00:00+00:00', price_timeframe: '1h', signal_resolution: { signal: 'WAIT', strategy_timeframe: '1d', display_timeframe: '1h', reference_candle: '2026-04-15T00:00:00+00:00', latest_displayed_candle: '2026-04-16T04:00:00+00:00', reasons: ['SINAL INCONCLUSIVO: estado não confirmado.', 'EXIT bloqueado: timeframe da estratégia não corresponde ao timeframe exibido.', 'EXIT bloqueado: candle de referência não corresponde ao último candle exibido.'] }, stop_price: 69898.27618, entry_price: 72962.71 } }])
}));
await page.route('**/api/monitor/preferences', (route) => route.fulfill({
  status: 200,
  contentType: 'application/json',
  body: JSON.stringify({ __global__: { in_portfolio: false, card_mode: 'strategy', price_timeframe: '1d', theme: 'dark-green' }, 'BTC/USDT': { in_portfolio: true, card_mode: 'strategy', price_timeframe: '1h', theme: 'dark-green' } })
}));
await page.route('**/api/market/candles**', (route) => route.fulfill({
  status: 200,
  contentType: 'application/json',
  body: JSON.stringify({ candles: [
    { timestamp_utc: '2026-04-16T01:00:00Z', open: 74850, high: 74910, low: 74790, close: 74880, volume: 82.413 },
    { timestamp_utc: '2026-04-16T02:00:00Z', open: 74880, high: 74940, low: 74820, close: 74895, volume: 91.127 },
    { timestamp_utc: '2026-04-16T03:00:00Z', open: 74895, high: 75005, low: 74865, close: 74905, volume: 104.252 },
    { timestamp_utc: '2026-04-16T04:00:00Z', open: 74888.21, high: 75010, low: 74839.51, close: 74930.98, volume: 112.613 },
  ] })
}));

await page.goto('http://127.0.0.1:5173/monitor', { waitUntil: 'networkidle' });
const allBtn = page.getByTestId('monitor-filter-all');
if (await allBtn.isVisible()) await allBtn.click();
const card = page.getByTestId('monitor-card-btc-usdt');
await expect(card).toBeVisible();
await expect(card.getByText('WAIT', { exact: true })).toBeVisible();
await expect(card).toContainText('SINAL INCONCLUSIVO: estado não confirmado.');
await expect(card).toContainText('EXIT bloqueado: timeframe da estratégia não corresponde ao timeframe exibido.');
await expect(card).toContainText('signal: WAIT');
await expect(card).toContainText('strategy tf: 1d');
await expect(card).toContainText('display tf: 1h');
await card.screenshot({ path: path.join(outDir, '01-btc-card.png') });
await fs.writeFile(path.join(outDir, '01-btc-card.txt'), await card.innerText());
await card.click();
const dialog = page.getByRole('dialog');
await expect(dialog).toBeVisible();
await expect(dialog).toContainText('Resolved state');
await expect(dialog).toContainText('WAIT');
await expect(dialog).toContainText('Strategy timeframe');
await expect(dialog).toContainText('Displayed timeframe');
await expect(dialog).toContainText('Reference candle');
await expect(dialog).toContainText('Latest displayed candle');
await expect(dialog).toContainText('EXIT bloqueado: candle de referência não corresponde ao último candle exibido.');
await dialog.screenshot({ path: path.join(outDir, '02-btc-modal.png') });
await fs.writeFile(path.join(outDir, '02-btc-modal.txt'), await dialog.innerText());
await browser.close();
console.log(JSON.stringify({ outDir }, null, 2));
