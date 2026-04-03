import { chromium } from 'playwright';

const BASE_URL = 'http://72.60.150.140:5173/kanban';
const EVIDENCE_DIR = '/root/.openclaw/workspace/crypto/qa-evidence';

const browser = await chromium.launch({ headless: true });
const page = await browser.newPage();
await page.setViewportSize({ width: 1280, height: 800 });

try {
  console.log('1. Navigating to kanban...');
  await page.goto(BASE_URL, { waitUntil: 'networkidle', timeout: 30000 });

  // Check if login is needed
  const loginInput = page.locator('input[type="text"], input[type="email"], input[name="email"], input[name="username"]').first();
  const isLoginVisible = await loginInput.isVisible({ timeout: 5000 }).catch(() => false);
  
  if (isLoginVisible) {
    console.log('Login required, filling credentials...');
    await loginInput.fill('admin@crypto.com');
    const passwordInput = page.locator('input[type="password"]').first();
    await passwordInput.fill('admin123');
    await page.click('button[type="submit"], button:has-text("Entrar"), button:has-text("Login")');
    await page.waitForURL('**/*', { timeout: 10000 });
    console.log('Logged in, URL:', page.url());
    await page.waitForLoadState('networkidle');
  }

  await page.waitForTimeout(3000);

  console.log('Current URL:', page.url());
  
  console.log('Taking debug screenshot...');
  await page.screenshot({ path: `${EVIDENCE_DIR}/card63-debug2.png`, fullPage: true });

  // Get all buttons text
  const allButtons = await page.$$eval('button', btns => btns.map(b => ({ text: b.innerText.trim(), ariaLabel: b.getAttribute('aria-label'), title: b.getAttribute('title') })));
  console.log('All buttons found:', JSON.stringify(allButtons, null, 2));

  // Get page title
  console.log('Page title:', await page.title());

} catch (error) {
  console.error('Error:', error.message);
  await page.screenshot({ path: `${EVIDENCE_DIR}/card63-error.png`, fullPage: true }).catch(() => {});
} finally {
  await browser.close();
}
