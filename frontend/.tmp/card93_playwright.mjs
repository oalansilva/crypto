import { chromium } from '@playwright/test';
import fs from 'fs';

const token = process.env.TOKEN;
const outDir = '/root/.openclaw/workspace/crypto/qa_artifacts/playwright/card-93-falso-positivo-saida';
const browser = await chromium.launch({ headless: true });
const context = await browser.newContext({ viewport: { width: 1600, height: 1200 } });
const page = await context.newPage();
const requests = [];
page.on('response', async (resp) => {
  const url = resp.url();
  if (url.includes('/api/opportunities') || url.includes('/api/market-data/candles')) {
    let body = '';
    try { body = await resp.text(); } catch {}
    requests.push({ url, status: resp.status(), body: body.slice(0, 4000) });
  }
});
await page.addInitScript((tok) => {
  window.localStorage.setItem('auth_access_token', tok);
}, token);
await page.goto('http://127.0.0.1:5173/monitor', { waitUntil: 'networkidle' });
const btcCard = page.getByTestId('monitor-card-btc-usdt');
await btcCard.waitFor({ state: 'visible', timeout: 15000 });
await page.screenshot({ path: `${outDir}/monitor-full.png`, fullPage: true });
await btcCard.scrollIntoViewIfNeeded();
await btcCard.screenshot({ path: `${outDir}/btc-card.png` });
const cardText = await btcCard.innerText();
await btcCard.click();
const modal = page.getByTestId('chart-modal');
await modal.waitFor({ state: 'visible', timeout: 15000 });
await modal.screenshot({ path: `${outDir}/btc-modal.png` });
const modalText = await modal.innerText();
const timeframePressed = {};
for (const tf of ['15m','1h','4h','1d']) {
  const btn = page.getByTestId(`chart-timeframe-${tf}`);
  timeframePressed[tf] = await btn.getAttribute('aria-pressed');
}
fs.writeFileSync(`${outDir}/observations.json`, JSON.stringify({ cardText, modalText, timeframePressed, requests }, null, 2));
await browser.close();
