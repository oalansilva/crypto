import { chromium } from 'playwright';

const BASE_URL = 'http://72.60.150.140:5173/kanban';
const EVIDENCE_DIR = '/root/.openclaw/workspace/crypto/qa-evidence';

const browser = await chromium.launch({ headless: true });
const context = await browser.newContext();
const page = await context.newPage();
await page.setViewportSize({ width: 1280, height: 800 });

try {
  console.log('1. Navigating to kanban...');
  await page.goto(BASE_URL, { waitUntil: 'networkidle', timeout: 30000 });
  
  // Wait for login form
  await page.waitForSelector('input[type="email"], input[name="email"]', { timeout: 5000 });
  
  // Try to register a new user
  console.log('2. Clicking "Criar Conta"...');
  await page.click('button:has-text("Criar Conta")');
  await page.waitForTimeout(500);
  
  await page.screenshot({ path: `${EVIDENCE_DIR}/card63-register.png`, fullPage: true });
  
  // Check what's on the register page
  const emailInput = page.locator('input[type="email"], input[name="email"]').first();
  const emailVisible = await emailInput.isVisible().catch(() => false);
  
  if (emailVisible) {
    console.log('3. Filling registration form...');
    await emailInput.fill('qa_test_63@example.com');
    
    const passwordInput = page.locator('input[type="password"]').first();
    await passwordInput.fill('qa_test_pass_123');
    await page.waitForTimeout(200);
    
    // Try to submit
    await page.click('button[type="submit"], button:has-text("Criar Conta")');
    await page.waitForTimeout(3000);
    
    console.log('URL after registration:', page.url());
    await page.screenshot({ path: `${EVIDENCE_DIR}/card63-after-reg.png`, fullPage: true });
  }

} catch (error) {
  console.error('Error:', error.message);
  await page.screenshot({ path: `${EVIDENCE_DIR}/card63-error.png`, fullPage: true }).catch(() => {});
} finally {
  await browser.close();
}
