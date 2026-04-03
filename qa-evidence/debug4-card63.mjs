import { chromium } from 'playwright';

const BASE_URL = 'http://72.60.150.140:5173/kanban';
const EVIDENCE_DIR = '/root/.openclaw/workspace/crypto/qa-evidence';

const browser = await chromium.launch({ headless: true });
const context = await browser.newContext();
const page = await context.newPage();
await page.setViewportSize({ width: 1280, height: 800 });

try {
  console.log('1. Navigating to kanban directly...');
  await page.goto(BASE_URL, { waitUntil: 'networkidle', timeout: 30000 });
  console.log('URL after direct nav:', page.url());
  
  // Check current state
  await page.screenshot({ path: `${EVIDENCE_DIR}/card63-debug4.png`, fullPage: true });
  
  const allButtons = await page.$$eval('button', btns => btns.map(b => ({ text: b.innerText.trim() })));
  console.log('Buttons:', JSON.stringify(allButtons));

  // If redirected to login, try to login with test credentials
  if (page.url().includes('login')) {
    console.log('On login page, trying test credentials...');
    
    // Wait for form to load
    await page.waitForSelector('input[type="email"], input[name="email"]', { timeout: 5000 });
    
    await page.fill('input[type="email"], input[name="email"]', 'test@test.com');
    await page.fill('input[type="password"]', 'test123');
    await page.click('button[type="submit"]');
    await page.waitForTimeout(3000);
    
    console.log('After login attempt:', page.url());
    await page.screenshot({ path: `${EVIDENCE_DIR}/card63-debug5.png`, fullPage: true });
  }

} catch (error) {
  console.error('Error:', error.message);
  await page.screenshot({ path: `${EVIDENCE_DIR}/card63-error.png`, fullPage: true }).catch(() => {});
} finally {
  await browser.close();
}
