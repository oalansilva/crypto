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
  
  // Fill by placeholder using type (keyboard)
  console.log('2. Filling email using keyboard...');
  const emailInput = page.locator('input[placeholder="seu@email.com"]');
  await emailInput.waitFor({ state: 'visible', timeout: 5000 });
  await emailInput.click();
  await page.keyboard.type('admin@admin.com', { delay: 50 });
  
  console.log('3. Filling password using keyboard...');
  const passwordInput = page.locator('input[placeholder="••••••••"]');
  await passwordInput.click();
  await page.keyboard.type('admin1234', { delay: 50 });
  
  await page.waitForTimeout(300);
  await page.screenshot({ path: `${EVIDENCE_DIR}/card63-before-submit2.png`, fullPage: false });
  
  // Check values
  const emailVal = await emailInput.inputValue();
  const passVal = await passwordInput.inputValue();
  console.log('Email value:', emailVal);
  console.log('Password value length:', passVal.length);
  
  console.log('4. Submitting login...');
  await page.locator('button:has-text("Entrar")').first().click();
  
  await page.waitForURL('**/kanban**', { timeout: 5000 }).catch(() => {});
  await page.waitForTimeout(3000);
  console.log('URL after submit:', page.url());
  await page.screenshot({ path: `${EVIDENCE_DIR}/card63-after-login2.png`, fullPage: true });

} catch (error) {
  console.error('Error:', error.message);
  await page.screenshot({ path: `${EVIDENCE_DIR}/card63-error.png`, fullPage: true }).catch(() => {});
} finally {
  await browser.close();
}
