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
    
    // Click login and wait for navigation
    await page.click('button[type="submit"], button:has-text("Entrar"), button:has-text("Login")');
    
    // Wait a bit for response
    await page.waitForTimeout(3000);
    console.log('After login click, URL:', page.url());
    
    // Check for error messages
    const errorMsg = await page.locator('[class*="error" i], [class*="alert" i], [role="alert"]').first().textContent().catch(() => 'no error');
    console.log('Error message (if any):', errorMsg);
    
    // Check if we're still on login page
    if (page.url().includes('login')) {
      // Try different credentials
      console.log('Login failed, trying different credentials...');
      
      // Clear and refill
      await loginInput.clear();
      await loginInput.fill('admin@admin.com');
      await passwordInput.clear();
      await passwordInput.fill('password');
      await page.click('button[type="submit"]');
      await page.waitForTimeout(3000);
      console.log('URL after attempt 2:', page.url());
    }
  }

  await page.waitForTimeout(2000);
  console.log('Final URL:', page.url());
  await page.screenshot({ path: `${EVIDENCE_DIR}/card63-debug3.png`, fullPage: true });

} catch (error) {
  console.error('Error:', error.message);
  await page.screenshot({ path: `${EVIDENCE_DIR}/card63-error.png`, fullPage: true }).catch(() => {});
} finally {
  await browser.close();
}
