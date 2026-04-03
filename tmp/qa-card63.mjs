import { chromium } from 'playwright';

const BASE = 'http://72.60.150.140:5173';
const API = 'http://72.60.150.140:8003/api';

async function run() {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    viewport: { width: 1280, height: 800 }
  });
  const page = await context.newPage();

  const errors = [];
  page.on('console', msg => {
    if (msg.type() === 'error') errors.push(msg.text());
  });

  let passed = 0;
  let failed = 0;

  function assert(condition, label) {
    if (condition) {
      console.log(`✅ ${label}`);
      passed++;
    } else {
      console.log(`❌ ${label}`);
      failed++;
    }
  }

  try {
    // 1. Login via API to get token
    console.log('\n--- Login via API ---');
    const loginResp = await fetch(`${API}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email: 'qa@test.com', password: 'test123456' })
    });
    const login = await loginResp.json();
    const token = login.accessToken;
    console.log(`✅ Login OK: ${login.email}, token=${token.substring(0, 20)}...`);

    // 2. Navigate to login page
    console.log('\n--- Navegando para login ---');
    await page.goto(`${BASE}/login`, { waitUntil: 'networkidle', timeout: 30000 });
    await page.waitForTimeout(1000);

    // 3. Fill login form
    console.log('Preenchendo formulário de login...');
    const emailInput = page.locator('input[type="email"]').first();
    const passwordInput = page.locator('input[type="password"]').first();
    
    await emailInput.fill('qa@test.com');
    await passwordInput.fill('test123456');
    
    const submitBtn = page.locator('button[type="submit"]').first();
    await submitBtn.click();
    
    // Wait for redirect to kanban
    await page.waitForURL('**/kanban**', { timeout: 10000 }).catch(() => {
      console.log('Timeout waiting for kanban redirect, current URL:', page.url());
    });
    await page.waitForTimeout(2000);

    const currentUrl = page.url();
    console.log(`URL atual: ${currentUrl}`);
    const kanbanLoaded = currentUrl.includes('/kanban');
    console.log(`Kanban carregado: ${kanbanLoaded}`);

    // If not on kanban, try to go there directly
    if (!kanbanLoaded) {
      console.log('Navegando diretamente para /kanban...');
      await page.goto(`${BASE}/kanban`, { waitUntil: 'networkidle', timeout: 30000 });
      await page.waitForTimeout(2000);
    }

    // Check if still on login
    const stillOnLogin = await page.locator('input[type="email"]').isVisible().catch(() => false);
    if (stillOnLogin) {
      console.log('❌ Ainda na página de login - não conseguiu autenticar');
      await page.screenshot({ path: '/root/.openclaw/workspace/crypto/tmp/qa-card63-login-fail.png', fullPage: true });
      failed++;
      await browser.close();
      console.log(`\n--- Resultado: ${passed}✅ / ${failed}❌ ---`);
      process.exit(1);
    }

    // 4. Now on kanban - find search input
    console.log('\n--- Localizando campo de busca ---');
    
    const searchSelectors = [
      'input[placeholder*="buscar" i]',
      'input[placeholder*="search" i]',
      'input[placeholder*="procurar" i]',
      'input[placeholder*="card" i]',
      'input[type="search"]',
      'input[data-testid*="search"]',
      '.search-input',
      '[class*="search"] input',
      'input[class*="search"]'
    ];

    let searchInput = null;
    for (const sel of searchSelectors) {
      const el = page.locator(sel).first();
      if (await el.isVisible({ timeout: 500 }).catch(() => false)) {
        searchInput = el;
        console.log(`✅ Campo de busca encontrado: ${sel}`);
        break;
      }
    }

    if (!searchInput) {
      const allInputs = await page.locator('input').all();
      console.log(`Total de inputs na página: ${allInputs.length}`);
      for (let i = 0; i < allInputs.length; i++) {
        const inp = allInputs[i];
        const ph = await inp.getAttribute('placeholder').catch(() => '');
        const type = await inp.getAttribute('type').catch(() => '');
        const cls = await inp.getAttribute('class').catch(() => '');
        const visible = await inp.isVisible().catch(() => false);
        console.log(`  Input ${i}: type=${type}, placeholder="${ph}", class="${cls.substring(0, 80)}", visible=${visible}`);
      }
      
      // Dump page content to understand structure
      const bodyText = await page.locator('body').innerText().catch(() => '');
      console.log('Page text snippet:', bodyText.substring(0, 300));
    }

    if (!searchInput) {
      console.log('❌ Campo de busca NÃO encontrado na página');
      await page.screenshot({ path: '/root/.openclaw/workspace/crypto/tmp/qa-card63-no-search.png', fullPage: true });
      failed++;
    } else {
      // Test 1: Search for #54
      console.log('\n--- Teste 1: Busca #54 ---');
      await searchInput.fill('');
      await searchInput.fill('#54');
      await page.waitForTimeout(2000);

      const drawerVisible = await page.locator('[role="dialog"], .drawer, [class*="drawer"], [class*="modal"], [class*="overlay"]').isVisible().catch(() => false);
      const urlAfterSearch = page.url();
      const card54InContent = await page.locator('text=/#54|card.*54|54.*card/i').first().isVisible().catch(() => false);
      
      console.log(`Drawer/modal aberto: ${drawerVisible}`);
      console.log(`URL após busca: ${urlAfterSearch}`);
      console.log(`Card 54 visível: ${card54InContent}`);

      await page.screenshot({ path: '/root/.openclaw/workspace/crypto/tmp/qa-card63-test1.png', fullPage: true });

      assert(drawerVisible || urlAfterSearch.includes('54') || card54InContent, 'Busca #54 abre card diretamente');

      // Close drawer
      await page.keyboard.press('Escape');
      await page.waitForTimeout(500);
      await searchInput.fill('');
      await page.waitForTimeout(500);

      // Test 2: Normal text search
      console.log('\n--- Teste 2: Busca por texto normal ---');
      await searchInput.fill('portfolio');
      await page.waitForTimeout(2000);
      
      const portfolioVisible = await page.locator('text=/portfolio/i').first().isVisible().catch(() => false);
      console.log(`Resultados de "portfolio" visíveis: ${portfolioVisible}`);
      await page.screenshot({ path: '/root/.openclaw/workspace/crypto/tmp/qa-card63-test2.png', fullPage: true });
      
      assert(portfolioVisible, 'Busca normal retorna resultados');

      await searchInput.fill('');
      await page.waitForTimeout(500);

      // Test 3: Non-existent card
      console.log('\n--- Teste 3: Busca #999999 (inexistente) ---');
      await searchInput.fill('#999999');
      await page.waitForTimeout(2000);

      const toastOrMsg = await page.locator('[class*="toast"], [role="alert"], [class*="notification"], text=/não enc|não encontr|não existe/i').isVisible().catch(() => false);
      const drawerStillClosed = !(await page.locator('[role="dialog"], .drawer, [class*="drawer"], [class*="modal"]').isVisible().catch(() => false));
      console.log(`Toast/msg ou drawer fechado: ${toastOrMsg || drawerStillClosed}`);
      await page.screenshot({ path: '/root/.openclaw/workspace/crypto/tmp/qa-card63-test3.png', fullPage: true });

      assert(toastOrMsg || drawerStillClosed, 'Card inexistente (#999999) não abre drawer ou exibe toast');
    }

  } catch (err) {
    console.error('❌ Erro durante teste:', err.message);
    await page.screenshot({ path: '/root/.openclaw/workspace/crypto/tmp/qa-card63-error.png', fullPage: true });
    failed++;
  }

  await browser.close();

  console.log(`\n--- Resultado: ${passed}✅ / ${failed}❌ ---`);
  if (errors.length > 0) {
    console.log('Console errors:', errors.slice(0, 5));
  }
  process.exit(failed > 0 ? 1 : 0);
}

run();
