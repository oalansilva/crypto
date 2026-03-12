import { chromium } from 'playwright';
import fs from 'node:fs/promises';

const outDir = new URL('./', import.meta.url).pathname;
await fs.mkdir(outDir, { recursive: true });

const targets = [
  { name: 'proto-desktop', url: 'http://127.0.0.1:5173/prototypes/improve-wallet-screen/', viewport: { width: 1440, height: 900 } },
  { name: 'impl-desktop-loaded', url: 'http://127.0.0.1:5173/external/balances', viewport: { width: 1440, height: 900 } },
  { name: 'proto-mobile', url: 'http://127.0.0.1:5173/prototypes/improve-wallet-screen/', viewport: { width: 390, height: 844 }, mobile: true },
  { name: 'impl-mobile-loaded', url: 'http://127.0.0.1:5173/external/balances', viewport: { width: 390, height: 844 }, mobile: true },
];

function metricsScript() {
  const q = (sel) => document.querySelector(sel);
  const rect = (el) => {
    if (!el) return null;
    const r = el.getBoundingClientRect();
    return { x: Math.round(r.x), y: Math.round(r.y), width: Math.round(r.width), height: Math.round(r.height) };
  };
  const main = q('main');
  const heading = Array.from(document.querySelectorAll('h1')).find((el) => /Carteira/i.test(el.textContent || ''));
  const balancesTitle = Array.from(document.querySelectorAll('h2,h3,div,span')).find((el) => (el.textContent || '').trim() === 'Balances');
  const balancesPanel = balancesTitle?.closest('section,article,div');
  return {
    url: location.href,
    title: document.title,
    bodyTextSample: (document.body.innerText || '').replace(/\s+/g, ' ').trim().slice(0, 1200),
    headingRect: rect(heading),
    mainRect: rect(main),
    balancesPanelRect: rect(balancesPanel),
    horizontalScroll: Math.max(0, document.documentElement.scrollWidth - window.innerWidth),
  };
}

const browser = await chromium.launch({ headless: true });
const summary = [];
for (const t of targets) {
  const context = await browser.newContext({ viewport: t.viewport, isMobile: !!t.mobile, deviceScaleFactor: 1 });
  const page = await context.newPage();
  await page.goto(t.url, { waitUntil: 'networkidle', timeout: 60000 });
  await page.waitForTimeout(2500);
  if (t.name.includes('impl')) {
    await page.waitForSelector('text=Balances', { timeout: 30000 });
    await page.waitForTimeout(1000);
  }
  const shotPath = `${outDir}/${t.name}.png`;
  await page.screenshot({ path: shotPath, fullPage: false });
  const metrics = await page.evaluate(metricsScript);
  summary.push({
    name: t.name,
    sourceUrl: t.url,
    viewport: t.viewport,
    mobile: !!t.mobile,
    screenshot: shotPath,
    url: `http://72.60.150.140:5173/qa-artifacts/playwright/improve-wallet-screen/rerun-2026-03-12-1056/${t.name}.png`,
    metrics,
  });
  console.log(JSON.stringify(summary.at(-1), null, 2));
  await context.close();
}
await browser.close();
await fs.writeFile(`${outDir}/summary.json`, JSON.stringify(summary, null, 2));
