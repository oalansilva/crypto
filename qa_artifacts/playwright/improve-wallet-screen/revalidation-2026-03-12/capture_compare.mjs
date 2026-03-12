import { chromium, devices } from 'playwright';
import fs from 'node:fs/promises';

const targets = [
  { name: 'proto-desktop', url: 'http://127.0.0.1:5173/prototypes/improve-wallet-screen/', viewport: { width: 1440, height: 900 } },
  { name: 'impl-desktop', url: 'http://127.0.0.1:5173/external/balances', viewport: { width: 1440, height: 900 } },
  { name: 'proto-mobile', url: 'http://127.0.0.1:5173/prototypes/improve-wallet-screen/', viewport: { width: 390, height: 844 }, mobile: true },
  { name: 'impl-mobile', url: 'http://127.0.0.1:5173/external/balances', viewport: { width: 390, height: 844 }, mobile: true },
];

const browser = await chromium.launch({ headless: true });
for (const t of targets) {
  const context = await browser.newContext({ viewport: t.viewport, isMobile: !!t.mobile, deviceScaleFactor: 1 });
  const page = await context.newPage();
  await page.goto(t.url, { waitUntil: 'networkidle', timeout: 60000 });
  await page.waitForTimeout(1500);
  const path = `qa_artifacts/playwright/improve-wallet-screen/revalidation-2026-03-12/${t.name}.png`;
  await page.screenshot({ path, fullPage: false });
  console.log('saved', path, await page.title(), page.url());
  await context.close();
}
await browser.close();
