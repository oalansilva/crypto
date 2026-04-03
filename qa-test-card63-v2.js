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

  // Find and list all buttons to locate the search button
  console.log('3. Listando botões na página...');
  const allButtons = await page.locator('button').all();
  for (const btn of allButtons) {
    const label = await btn.getAttribute('aria-label') || '';
    const title = await btn.getAttribute('title') || '';
    const text = (await btn.textContent() || '').trim();
    const classes = await btn.getAttribute('class') || '';
    console.log(`  Button: text="${text}" aria-label="${label}" title="${title}" class="${classes}"`);
  }

  // Try to find the search button by various selectors
  let searchClicked = false;
  
  // Try clicking by aria-label containing "buscar" or "search"
  const buscarBtns = await page.locator('button[aria-label*="buscar" i], button[aria-label*="search" i]').all();
  if (buscarBtns.length > 0) {
    await buscarBtns[0].click();
    searchClicked = true;
    console.log('  ✓ Clicou no botão Buscar (aria-label)');
  }

  // Try by title
  if (!searchClicked) {
    const titleBtns = await page.locator('button[title*="buscar" i], button[title*="search" i]').all();
    if (titleBtns.length > 0) {
      await titleBtns[0].click();
      searchClicked = true;
      console.log('  ✓ Clicou no botão Buscar (title)');
    }
  }

  // Try by text content
  if (!searchClicked) {
    const textBtns = await page.locator('button').filter({ hasText: /buscar|search|🔍/i }).all();
    if (textBtns.length > 0) {
      await textBtns[0].click();
      searchClicked = true;
      console.log('  ✓ Clicou no botão Buscar (texto)');
    }
  }

  if (!searchClicked) {
    // Take screenshot and list all to understand layout
    await page.screenshot({ path: '/root/.openclaw/workspace/crypto/qa-evidence/card63-no-search-btn.png', fullPage: false });
    console.log('  ✗ Botão Buscar NÃO encontrado');
    console.log('  → Tirando screenshot para debug...');
  } else {
    await page.waitForTimeout(1000);
    
    // Find the search input
    console.log('4. Procurando campo de input...');
    const inputs = await page.locator('input').all();
    for (const inp of inputs) {
      const type = await inp.getAttribute('type') || '';
      const placeholder = await inp.getAttribute('placeholder') || '';
      const classes = await inp.getAttribute('class') || '';
      console.log(`  Input: type="${type}" placeholder="${placeholder}" class="${classes}"`);
    }
    
    // Type #63
    const searchInputs = await page.locator('input').filter({ hasNot: page.locator('input[type="password"]') }).all();
    for (const inp of searchInputs) {
      const visible = await inp.isVisible();
      if (visible) {
        await inp.fill('#63');
        console.log('  ✓ Digitou #63');
        break;
      }
    }
    
    await page.waitForTimeout(2000);
    await page.keyboard.press('Enter');
    await page.waitForTimeout(3000);
    
    console.log('5. Tirando screenshot do resultado...');
    await page.screenshot({ path: '/root/.openclaw/workspace/crypto/qa-evidence/card63-search-result.png', fullPage: false });
    
    // Test #71
    console.log('6. Testando com #71...');
    const inputs2 = await page.locator('input').all();
    for (const inp of inputs2) {
      const visible = await inp.isVisible();
      if (visible) {
        await inp.fill('#71');
        break;
      }
    }
    await page.keyboard.press('Enter');
    await page.waitForTimeout(2000);
    await page.screenshot({ path: '/root/.openclaw/workspace/crypto/qa-evidence/card63-search-71.png', fullPage: false });
    console.log('  ✓ Screenshot #71 salvo');
  }

  await browser.close();
  console.log('Done!');
})();
