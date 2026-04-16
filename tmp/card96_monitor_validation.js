const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const BASE_URL = 'http://127.0.0.1:5173';
const API_URL = 'http://127.0.0.1:8003';
const OUT_DIR = '/root/.openclaw/workspace/crypto/qa_artifacts/playwright/card-96-monitor-exit-signal';

(async () => {
  fs.mkdirSync(OUT_DIR, { recursive: true });

  const loginRes = await fetch(`${API_URL}/api/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email: 'o.alan.silva@gmail.com', password: 'qa-bypass' }),
  });
  if (!loginRes.ok) throw new Error(`login failed: ${loginRes.status}`);
  const login = await loginRes.json();

  const opportunitiesRes = await fetch(`${API_URL}/api/opportunities/?tier=all`, {
    headers: { Authorization: `Bearer ${login.accessToken}` },
  });
  if (!opportunitiesRes.ok) throw new Error(`opportunities failed: ${opportunitiesRes.status}`);
  const opportunities = await opportunitiesRes.json();
  const btc = opportunities.find((item) => item.symbol === 'BTC/USDT');
  fs.writeFileSync(path.join(OUT_DIR, '01-opportunities.json'), JSON.stringify({ count: opportunities.length, btc }, null, 2));

  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({ viewport: { width: 1600, height: 1200 } });
  const page = await context.newPage();

  await page.addInitScript((auth) => {
    window.localStorage.setItem('auth_access_token', auth.accessToken);
    window.localStorage.setItem('auth_refresh_token', auth.refreshToken);
    window.localStorage.setItem('auth_user', JSON.stringify({
      id: auth.userId,
      email: auth.email,
      name: auth.name,
      isAdmin: !!auth.isAdmin,
    }));
  }, login);

  const requests = [];
  page.on('response', async (response) => {
    const url = response.url();
    if (url.includes('/api/opportunities/') || url.includes('/api/monitor/preferences') || url.includes('/api/market/candles')) {
      requests.push({ url, status: response.status() });
    }
  });

  await page.goto(`${BASE_URL}/monitor`, { waitUntil: 'networkidle' });
  await page.screenshot({ path: path.join(OUT_DIR, '02-monitor-initial.png'), fullPage: true });

  const allButton = page.getByRole('button', { name: /^All$/ }).last();
  if (await allButton.isVisible()) {
    await allButton.click();
    await page.waitForLoadState('networkidle');
  }

  const btcCard = page.locator('[data-testid="monitor-card-btc-usdt"]').first();
  await btcCard.waitFor({ state: 'visible', timeout: 15000 });
  await btcCard.scrollIntoViewIfNeeded();
  await page.screenshot({ path: path.join(OUT_DIR, '03-monitor-btc-card.png'), fullPage: true });

  const btcText = await btcCard.innerText();
  fs.writeFileSync(path.join(OUT_DIR, '04-btc-card.txt'), btcText);

  await btcCard.click();
  const dialog = page.getByRole('dialog');
  await dialog.waitFor({ state: 'visible', timeout: 15000 });
  await page.screenshot({ path: path.join(OUT_DIR, '05-btc-chart-modal.png'), fullPage: true });

  const dialogText = await dialog.innerText();
  fs.writeFileSync(path.join(OUT_DIR, '06-btc-chart-modal.txt'), dialogText);
  fs.writeFileSync(path.join(OUT_DIR, '07-network-log.json'), JSON.stringify(requests, null, 2));

  await browser.close();
})();
