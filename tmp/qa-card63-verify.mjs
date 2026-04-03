import { chromium } from 'playwright';

const BASE = 'http://72.60.150.140:5173';
const API = 'http://72.60.150.140:8003/api';

async function run() {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    viewport: { width: 1280, height: 800 }
  });
  const page = await context.newPage();

  try {
    // Login via API
    const loginResp = await fetch(`${API}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email: 'qa@test.com', password: 'test123456' })
    });
    const login = await loginResp.json();
    console.log(`Logged in: ${login.email}`);

    // Navigate to login page and login
    await page.goto(`${BASE}/login`, { waitUntil: 'networkidle', timeout: 30000 });
    await page.locator('input[type="email"]').fill('qa@test.com');
    await page.locator('input[type="password"]').fill('test123456');
    await page.locator('button[type="submit"]').click();
    
    // Wait for redirect
    await page.waitForTimeout(3000);
    console.log(`URL after login: ${page.url()}`);

    // Go to kanban
    await page.goto(`${BASE}/kanban`, { waitUntil: 'networkidle', timeout: 30000 });
    await page.waitForTimeout(2000);
    console.log(`URL: ${page.url()}`);

    // Check if still on login
    const onLogin = await page.locator('input[type="email"]').isVisible().catch(() => false);
    if (onLogin) {
      console.log('Still on login page');
      await page.screenshot({ path: '/root/.openclaw/workspace/crypto/tmp/qa-card63-login.png' });
    } else {
      // Check all inputs
      const inputs = await page.locator('input').all();
      console.log(`Inputs found: ${inputs.length}`);
      for (let i = 0; i < inputs.length; i++) {
        const ph = await inputs[i].getAttribute('placeholder').catch(() => '');
        const type = await inputs[i].getAttribute('type').catch(() => '');
        const visible = await inputs[i].isVisible().catch(() => false);
        console.log(`  Input ${i}: type=${type}, placeholder="${ph}", visible=${visible}`);
      }

      // Screenshot of kanban
      await page.screenshot({ path: '/root/.openclaw/workspace/crypto/tmp/qa-card63-kanban.png', fullPage: true });
      console.log('Screenshot saved');
    }

  } catch (err) {
    console.error('Error:', err.message);
    await page.screenshot({ path: '/root/.openclaw/workspace/crypto/tmp/qa-card63-error.png' });
  }

  await browser.close();
}

run();
