import { chromium } from '@playwright/test';
import fs from 'node:fs/promises';
import path from 'node:path';

const baseURL = 'http://127.0.0.1:5173';
const outDir = '/root/.openclaw/workspace/crypto/qa_artifacts/playwright/card-96-live-recheck';
await fs.mkdir(outDir, { recursive: true });

const browser = await chromium.launch({ headless: true });
const context = await browser.newContext({ viewport: { width: 1600, height: 1200 } });
const page = await context.newPage();
const network = [];
page.on('response', async (response) => {
  const url = response.url();
  if (url.includes('/api/opportunities') || url.includes('/api/market/candles') || url.includes('/api/auth/me') || url.includes('/api/monitor/preferences')) {
    network.push({ url, status: response.status(), method: response.request().method() });
  }
});

const login = await page.request.post(`${baseURL}/api/auth/login`, {
  data: { email: 'o.alan.silva@gmail.com', password: 'TempPass123!' },
  headers: { 'Content-Type': 'application/json' },
});
if (!login.ok()) {
  throw new Error(`Login failed: ${login.status()} ${await login.text()}`);
}
const auth = await login.json();
await context.addInitScript((payload) => {
  localStorage.setItem('auth_access_token', payload.accessToken);
  localStorage.setItem('auth_refresh_token', payload.refreshToken);
  localStorage.setItem('auth_user', JSON.stringify({
    id: payload.id,
    email: payload.email,
    name: payload.name,
    isAdmin: payload.isAdmin,
  }));
}, auth);

await page.goto(`${baseURL}/monitor`, { waitUntil: 'networkidle' });
await page.getByTestId('monitor-filter-all').click();
await page.waitForLoadState('networkidle');

const btcCard = page.getByTestId('monitor-card-btc-usdt').first();
await btcCard.waitFor({ state: 'visible', timeout: 30000 });
await btcCard.scrollIntoViewIfNeeded();
await page.screenshot({ path: path.join(outDir, '01-monitor-all.png'), fullPage: true });
await btcCard.screenshot({ path: path.join(outDir, '02-btc-card.png') });
const cardText = (await btcCard.innerText()).trim();
await fs.writeFile(path.join(outDir, '03-btc-card.txt'), cardText + '\n');

await btcCard.click();
const modal = page.getByTestId('chart-modal');
await modal.waitFor({ state: 'visible', timeout: 30000 });
await modal.screenshot({ path: path.join(outDir, '04-btc-chart-modal.png') });
const modalText = (await modal.innerText()).trim();
await fs.writeFile(path.join(outDir, '05-btc-chart-modal.txt'), modalText + '\n');
await fs.writeFile(path.join(outDir, '06-network-log.json'), JSON.stringify(network, null, 2));

const summary = [
  `URL: ${page.url()}`,
  'Observed via Playwright on live UI with dev login.',
  'BTC card text:',
  cardText,
  '',
  'BTC modal text:',
  modalText,
  '',
  'Network:',
  JSON.stringify(network, null, 2),
].join('\n');
await fs.writeFile(path.join(outDir, '07-summary.txt'), summary + '\n');

await browser.close();
