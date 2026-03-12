import { chromium } from 'playwright';

const url = 'http://72.60.150.140:5173/prototypes/improve-wallet-screen/';
const outDesktop = 'qa_artifacts/playwright/improve-wallet-screen/proto-desktop.png';
const outMobile = 'qa_artifacts/playwright/improve-wallet-screen/proto-mobile.png';

const browser = await chromium.launch();
const page = await browser.newPage();

await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 60000 });
await page.setViewportSize({ width: 1440, height: 900 });
await page.waitForTimeout(500);
await page.screenshot({ path: outDesktop, fullPage: false });

await page.setViewportSize({ width: 390, height: 844 });
await page.waitForTimeout(500);
await page.screenshot({ path: outMobile, fullPage: false });

await browser.close();
console.log('saved', outDesktop, outMobile);
