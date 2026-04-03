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
  await page.waitForTimeout(2000);
  
  console.log('Current URL:', page.url());
  
  // Fill by placeholder
  console.log('2. Filling email...');
  const emailInput = page.locator('input[placeholder="seu@email.com"]');
  await emailInput.waitFor({ state: 'visible', timeout: 5000 });
  await emailInput.fill('admin@admin.com');
  
  console.log('3. Filling password...');
  const passwordInput = page.locator('input[placeholder="••••••••"]');
  await passwordInput.fill('admin1234');
  
  await page.waitForTimeout(200);
  await page.screenshot({ path: `${EVIDENCE_DIR}/card63-before-submit.png`, fullPage: false });
  
  console.log('4. Submitting login...');
  await page.locator('button:has-text("Entrar")').first().click();
  
  await page.waitForTimeout(4000);
  console.log('URL after submit:', page.url());
  await page.screenshot({ path: `${EVIDENCE_DIR}/card63-after-login.png`, fullPage: true });

} catch (error) {
  console.error('Error:', error.message);
  await page.screenshot({ path: `${EVIDENCE_DIR}/card63-error.png`, fullPage: true }).catch(() => {});
} finally {
  await browser.close();
}
