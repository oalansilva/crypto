import playwright from '../frontend/node_modules/@playwright/test/index.js';
const { chromium } = playwright;
import fs from 'node:fs/promises';
import path from 'node:path';

const outDir = '/root/.openclaw/workspace/crypto/qa_artifacts/playwright/card-96-live-observation';
await fs.mkdir(outDir, { recursive: true });
const browser = await chromium.launch({ headless: true });
const page = await browser.newPage({ viewport: { width: 1600, height: 1200 } });
const requests = [];
page.on('response', async (res) => {
  const url = res.url();
  if (url.includes('/api/monitor/preferences') || url.includes('/api/market/candles') || url.includes('/api/opportunities')) {
    requests.push({ url, status: res.status() });
  }
});
await page.goto('http://127.0.0.1:5173/monitor', { waitUntil: 'networkidle' });
await page.screenshot({ path: path.join(outDir, '01-monitor-in-portfolio.png'), fullPage: true });
let body = await page.locator('body').innerText();
await fs.writeFile(path.join(outDir, '01-monitor-in-portfolio.txt'), body);

const allButton = page.getByTestId('monitor-filter-all');
if (await allButton.isVisible()) {
  await allButton.click();
  await page.waitForTimeout(1500);
}
await page.screenshot({ path: path.join(outDir, '02-monitor-all.png'), fullPage: true });
body = await page.locator('body').innerText();
await fs.writeFile(path.join(outDir, '02-monitor-all.txt'), body);

const btcCard = page.getByTestId('monitor-card-btc-usdt').first();
if (await btcCard.count()) {
  await btcCard.scrollIntoViewIfNeeded();
  await btcCard.screenshot({ path: path.join(outDir, '03-btc-card.png') });
  await fs.writeFile(path.join(outDir, '03-btc-card.txt'), await btcCard.innerText());
  await btcCard.click();
  await page.waitForTimeout(1200);
  const dialog = page.getByRole('dialog').first();
  if (await dialog.count()) {
    await dialog.screenshot({ path: path.join(outDir, '04-btc-modal.png') });
    await fs.writeFile(path.join(outDir, '04-btc-modal.txt'), await dialog.innerText());
  }
}
await fs.writeFile(path.join(outDir, 'network.json'), JSON.stringify(requests, null, 2));
await browser.close();
console.log(JSON.stringify({ outDir }, null, 2));
