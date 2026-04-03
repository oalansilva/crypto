import { chromium } from 'playwright';

const BASE_URL = 'http://72.60.150.140:5173/kanban';
const EVIDENCE_DIR = '/root/.openclaw/workspace/crypto/qa-evidence';

const browser = await chromium.launch({ headless: true });
const context = await browser.newContext();
const page = await context.newPage();
await page.setViewportSize({ width: 1280, height: 800 });

try {
  console.log('1. Navigating to kanban...');
  await page.goto(BASE_URL, { waitUntil: 'domcontentloaded', timeout: 30000 });
  await page.waitForTimeout(1000);
  
  // Check what page we're on
  console.log('URL:', page.url());
  
  // Get all inputs
  const inputs = await page.$$eval('input', ins => ins.map(i => ({ type: i.type, name: i.name, placeholder: i.placeholder })));
  console.log('Inputs found:', JSON.stringify(inputs, null, 2));
  
  // Check for any redirect
  if (!page.url().includes('login')) {
    console.log('Not on login page, may have session');
    await page.screenshot({ path: `${EVIDENCE_DIR}/card63-debug-final.png`, fullPage: true });
  }

} catch (error) {
  console.error('Error:', error.message);
} finally {
  await browser.close();
}
