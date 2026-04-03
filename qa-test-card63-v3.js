const { chromium } = require('playwright');

const ACCESS_TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJiZGEwZjJhYi02M2UwLTQwNjktOTIxOS04MTE3OWI4ODg0OTciLCJ1c2VyX2lkIjoiYmRhMGYyYWItNjNlMC00MDY5LTkyMTktODExNzliODg4NDk3IiwiZW1haWwiOiJ0ZXN0QHRlc3QuY29tIiwidHlwZSI6ImFjY2VzcyIsImlhdCI6MTc3NTIyMDA2NCwiZXhwIjoxNzc1MjIwOTY0fQ.AOFbufWnHsl4mcnm-NQKl6FDKMNrbGuDCVK3Rnm9Um4';
const REFRESH_TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJiZGEwZjJhYi02M2UwLTQwNjktOTIxOS04MTE3OWI4ODg0OTciLCJ0eXBlIjoicmVmcmVzaCIsImlhdCI6MTc3NTIyMDA2NCwiZXhwIjoxNzc1ODI0ODY0fQ.ttznGNIDwDcQz2E1ftBoZt-TrTj0vKNr7PbzDQSpzEI';
const USER = { id: 'bda0f2ab-63e0-4069-9219-81179b888497', email: 'test@test.com', name: 'Test User', isAdmin: false };

(async () => {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext();
  const page = await context.newPage();
  await page.setViewportSize({ width: 1280, height: 800 });

  // Inject auth tokens into localStorage before navigating
  await page.goto('http://72.60.150.140:5173/kanban');
  await page.evaluate(([accessToken, refreshToken, user]) => {
    localStorage.setItem('auth_access_token', accessToken);
    localStorage.setItem('auth_refresh_token', refreshToken);
    localStorage.setItem('auth_user', JSON.stringify(user));
  }, [ACCESS_TOKEN, REFRESH_TOKEN, USER]);

  console.log('1. Navegando para Kanban com auth...');
  await page.goto('http://72.60.150.140:5173/kanban', { waitUntil: 'networkidle', timeout: 30000 });
  await page.waitForTimeout(2000);

  console.log('2. Tirando screenshot do toolbar desktop...');
  await page.screenshot({ path: '/root/.openclaw/workspace/crypto/qa-evidence/card63-search-desktop-ok.png', fullPage: false });

  // Click the Buscar button using aria-label
  console.log('3. Clicando no botão Buscar...');
  await page.locator('button[aria-label="Search cards"]').first().click();
  await page.waitForTimeout(500);

  // Type in the search input using keyboard.type
  console.log('4. Digitando #63...');
  await page.keyboard.type('#63');
  await page.waitForTimeout(1000);

  // Check if there's a toast or drawer appearing
  console.log('5. Pressionando Enter...');
  await page.keyboard.press('Enter');
  await page.waitForTimeout(3000);

  console.log('6. Tirando screenshot do resultado (após Enter)...');
  await page.screenshot({ path: '/root/.openclaw/workspace/crypto/qa-evidence/card63-search-result.png', fullPage: false });

  // Check if there's a drawer open
  const drawer = await page.locator('[class*="drawer"], [class*="panel"], [role="dialog"], aside').filter({ hasText: /#63|63/ }).first();
  const drawerVisible = await drawer.isVisible().catch(() => false);
  console.log('   Drawer visível:', drawerVisible);

  // Test #71
  console.log('7. Testando com #71...');
  await page.keyboard.type('#71');
  await page.waitForTimeout(1000);
  await page.keyboard.press('Enter');
  await page.waitForTimeout(2000);
  await page.screenshot({ path: '/root/.openclaw/workspace/crypto/qa-evidence/card63-search-71.png', fullPage: false });

  const drawer71 = await page.locator('[class*="drawer"], [class*="panel"], [role="dialog"], aside').filter({ hasText: /#71|71/ }).first();
  const drawer71Visible = await drawer71.isVisible().catch(() => false);
  console.log('   Drawer #71 visível:', drawer71Visible);

  await browser.close();
  console.log('Done!');
})();
