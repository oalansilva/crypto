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
    const { accessToken, refreshToken, ...user } = login;
    console.log(`Logged in: ${login.email}`);

    // Go to kanban first
    await page.goto(`${BASE}/kanban`, { waitUntil: 'networkidle', timeout: 30000 });
    
    // Set localStorage with auth data
    await page.evaluate(({ accessToken, refreshToken, user }) => {
      localStorage.setItem('auth_access_token', accessToken);
      localStorage.setItem('auth_refresh_token', refreshToken);
      localStorage.setItem('auth_user', JSON.stringify(user));
    }, { accessToken, refreshToken, user });
    
    // Reload to apply localStorage
    await page.reload({ waitUntil: 'networkidle' });
    await page.waitForTimeout(3000);
    
    console.log(`URL: ${page.url()}`);

    // Check if still on login
    const onLogin = await page.locator('input[type="email"]').isVisible().catch(() => false);
    if (onLogin) {
      console.log('Still on login page - auth not working');
      await page.screenshot({ path: '/root/.openclaw/workspace/crypto/tmp/qa-card63-login-state.png' });
    } else {
      // Find search elements
      const searchPlaceholders = await page.locator('[placeholder*="search" i], [placeholder*="Search" i], [placeholder*="buscar" i]').all();
      console.log(`Search placeholders found: ${searchPlaceholders.length}`);
      
      const inputs = await page.locator('input').all();
      console.log(`Total inputs: ${inputs.length}`);
      for (let i = 0; i < inputs.length; i++) {
        const ph = await inputs[i].getAttribute('placeholder').catch(() => '');
        const type = await inputs[i].getAttribute('type').catch(() => '');
        const visible = await inputs[i].isVisible().catch(() => false);
        console.log(`  Input ${i}: type=${type}, placeholder="${ph}", visible=${visible}`);
      }

      await page.screenshot({ path: '/root/.openclaw/workspace/crypto/tmp/qa-card63-kanban-auth.png', fullPage: true });
      console.log('Screenshot saved');
    }

  } catch (err) {
    console.error('Error:', err.message);
    await page.screenshot({ path: '/root/.openclaw/workspace/crypto/tmp/qa-card63-error.png' });
  }

  await browser.close();
}

run();
