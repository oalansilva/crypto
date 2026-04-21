import { chromium } from '@playwright/test';
import fs from 'node:fs';

const outDir = new URL('../public/reports/mobile-pwa-kanban-mvp/', import.meta.url).pathname;
fs.mkdirSync(outDir, { recursive: true });
const pages = [
  { name: 'current-kanban', url: 'http://72.60.150.140:5173/kanban' },
  { name: 'prototype', url: 'http://72.60.150.140:5173/prototypes/mobile-pwa-kanban-mvp/index.html' },
];
const viewports = [
  { w: 390, h: 844, label: '390x844' },
  { w: 412, h: 915, label: '412x915' },
];

const sleep = (ms) => new Promise(r => setTimeout(r, ms));

const run = async () => {
  const browser = await chromium.launch({ headless: true });
  try {
    for (const vp of viewports) {
      const context = await browser.newContext({ viewport: { width: vp.w, height: vp.h } });
      const page = await context.newPage();

      for (const p of pages) {
        const file = `${outDir}${p.name}-${vp.label}.png`;
        await page.goto(p.url, { waitUntil: 'domcontentloaded', timeout: 60000 });
        await page.waitForLoadState('networkidle', { timeout: 60000 }).catch(() => {});
        await sleep(1500);
        await page.screenshot({ path: file, fullPage: true });
        console.log('saved', file);
      }

      await context.close();
    }
  } finally {
    await browser.close();
  }
};

await run();
