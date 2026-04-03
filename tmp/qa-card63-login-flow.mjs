import { chromium } from 'playwright';

const BASE = 'http://72.60.150.140:5173';
const API = 'http://72.60.150.140:8003/api';

async function run() {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({ viewport: { width: 1280, height: 800 } });
  const page = await context.newPage();

  try {
    // Go to login page
    console.log('Going to login...');
    await page.goto(`${BASE}/login`, { waitUntil: 'networkidle', timeout: 30000 });
    await page.waitForTimeout(1000);
    console.log(`URL: ${page.url()}`);

    // Fill form
    await page.locator('input[type="email"]').fill('qa@test.com');
    await page.locator('input[type="password"]').fill('test123456');
    
    // Submit
    console.log('Submitting login...');
    await page.locator('button[type="submit"]').click();
    
    // Wait for navigation
    await page.waitForTimeout(5000);
    console.log(`After submit URL: ${page.url()}`);
    
    // Check where we are
    const url = page.url();
    
    if (url.includes('/kanban')) {
      console.log('✅ On Kanban page');
    } else if (url.includes('/login')) {
      console.log('Still on login - checking for errors...');
      const errorMsg = await page.locator('[class*="error"], [class*="alert"], [role="alert"]').first().textContent().catch(() => '');
      console.log(`Error message: ${errorMsg}`);
    } else {
      console.log(`On different page: ${url}`);
    }

    // Now go to kanban
    console.log('\nNavigating to /kanban...');
    await page.goto(`${BASE}/kanban`, { waitUntil: 'networkidle', timeout: 30000 });
    await page.waitForTimeout(3000);
    console.log(`URL: ${page.url()}`);
    
    // Take screenshot
    await page.screenshot({ path: '/root/.openclaw/workspace/crypto/tmp/qa-card63-after-nav.png', fullPage: true });
    
    // Check for search
    const allInputs = await page.locator('input').all();
    console.log(`Inputs: ${allInputs.length}`);
    for (const inp of allInputs) {
      const ph = await inp.getAttribute('placeholder').catch(() => 'none');
      const type = await inp.getAttribute('type').catch(() => 'none');
      const visible = await inp.isVisible().catch(() => false);
      console.log(`  input: type=${type}, placeholder="${ph}", visible=${visible}`);
    }
    
    // Check for search elements by text
    const searchByText = await page.locator('text=/search|buscar|procurar/i').all();
    console.log(`Text elements matching search: ${searchByText.length}`);

  } catch (err) {
    console.error('Error:', err.message);
    await page.screenshot({ path: '/root/.openclaw/workspace/crypto/tmp/qa-card63-error.png' });
  }

  await browser.close();
}

run();
