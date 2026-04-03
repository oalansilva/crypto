import { chromium } from 'playwright';

const BASE = 'http://72.60.150.140:5173';
const API = 'http://72.60.150.140:8003/api';

async function run() {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    viewport: { width: 1280, height: 800 },
    storageState: undefined // Fresh state
  });
  const page = await context.newPage();

  let passed = 0;
  let failed = 0;

  function assert(condition, label) {
    if (condition) { console.log(`✅ ${label}`); passed++; }
    else { console.log(`❌ ${label}`); failed++; }
  }

  try {
    // 1. Navigate to kanban directly
    console.log('\n--- Navegando para Kanban ---');
    await page.goto(`${BASE}/kanban`, { waitUntil: 'networkidle', timeout: 30000 });
    await page.waitForTimeout(2000);
    
    // Should redirect to login
    console.log(`URL: ${page.url()}`);
    const onLogin = page.url().includes('/login');
    
    if (onLogin) {
      console.log('Redirected to login - logging in via UI...');
      
      // Fill login form
      await page.locator('input[type="email"]').fill('qa@test.com');
      await page.locator('input[type="password"]').fill('test123456');
      await page.locator('button[type="submit"]').click();
      
      // Wait for navigation
      await page.waitForTimeout(5000);
      console.log(`After login URL: ${page.url()}`);
    }

    // Check if kanban loaded
    const onKanban = page.url().includes('/kanban');
    console.log(`On Kanban: ${onKanban}`);

    if (!onKanban) {
      console.log('Could not reach kanban');
      await page.screenshot({ path: '/root/.openclaw/workspace/crypto/tmp/qa-card63-nokanban.png' });
      failed++;
    } else {
      // Wait for content to load
      await page.waitForTimeout(3000);

      // Try to find search input - look for any search-like element
      console.log('\n--- Procurando campo de busca ---');
      
      // Check all possible search locations
      const searchSelectors = [
        'input[placeholder*="search" i]',
        'input[placeholder*="Search" i]',
        'input[placeholder*="buscar" i]',
        'input[placeholder*="procurar" i]',
        'input[type="search"]',
        'input[class*="search" i]',
        '[class*="search"] input',
        '[class*="Search"]'
      ];

      let foundSearch = false;
      for (const sel of searchSelectors) {
        const count = await page.locator(sel).count();
        if (count > 0) {
          const visible = await page.locator(sel).first().isVisible().catch(() => false);
          console.log(`  ${sel}: count=${count}, visible=${visible}`);
          if (visible) foundSearch = true;
        }
      }

      // Check all inputs
      const allInputs = await page.locator('input').all();
      console.log(`Total inputs: ${allInputs.length}`);
      for (const inp of allInputs) {
        const ph = await inp.getAttribute('placeholder').catch(() => 'none');
        const type = await inp.getAttribute('type').catch(() => 'none');
        const visible = await inp.isVisible().catch(() => false);
        console.log(`  input: type=${type}, placeholder="${ph}", visible=${visible}`);
      }

      // Take screenshot
      await page.screenshot({ path: '/root/.openclaw/workspace/crypto/tmp/qa-card63-kanban-final.png', fullPage: true });
      console.log('Screenshot saved');

      if (!foundSearch) {
        console.log('❌ CAMPO DE BUSCA NÃO ENCONTRADO');
        
        // Look for any button with search icon
        const buttonsWithSearch = await page.locator('button:has-text("search"), button:has-text("Search"), button:has-text("🔍")').all();
        console.log(`Buttons with search text: ${buttonsWithSearch.length}`);
        
        // Check for any icon buttons in toolbar
        const iconButtons = await page.locator('button svg').all();
        console.log(`Buttons with icons: ${iconButtons.length}`);
        
        failed++;
      } else {
        // Test 1: Search for #54
        console.log('\n--- Teste 1: Busca #54 ---');
        const searchInput = page.locator('input[placeholder*="search" i], input[placeholder*="Search" i]').first();
        await searchInput.fill('#54');
        await page.waitForTimeout(2000);
        
        const drawerVisible = await page.locator('[role="dialog"], .drawer, [class*="drawer"], [class*="modal"]').isVisible().catch(() => false);
        const urlAfter = page.url();
        await page.screenshot({ path: '/root/.openclaw/workspace/crypto/tmp/qa-card63-test1.png', fullPage: true });
        
        assert(drawerVisible || urlAfter.includes('54'), 'Busca #54 abre card diretamente');
        
        // Close drawer
        await page.keyboard.press('Escape');
        await page.waitForTimeout(500);
        await searchInput.fill('');
        await page.waitForTimeout(500);
        
        // Test 2: Normal text search
        console.log('\n--- Teste 2: Busca normal ---');
        await searchInput.fill('portfolio');
        await page.waitForTimeout(2000);
        const portfolioResults = await page.locator('text=/portfolio/i').first().isVisible().catch(() => false);
        await page.screenshot({ path: '/root/.openclaw/workspace/crypto/tmp/qa-card63-test2.png', fullPage: true });
        assert(portfolioResults, 'Busca normal retorna resultados');
        
        await searchInput.fill('');
        await page.waitForTimeout(500);
        
        // Test 3: Non-existent card
        console.log('\n--- Teste 3: Card inexistente ---');
        await searchInput.fill('#999999');
        await page.waitForTimeout(2000);
        const toast = await page.locator('[class*="toast"], [role="alert"]').isVisible().catch(() => false);
        const noDrawer = !(await page.locator('[role="dialog"], .drawer, [class*="drawer"], [class*="modal"]').isVisible().catch(() => false));
        await page.screenshot({ path: '/root/.openclaw/workspace/crypto/tmp/qa-card63-test3.png', fullPage: true });
        assert(toast || noDrawer, 'Card inexistente exibe toast ou não abre drawer');
      }
    }

  } catch (err) {
    console.error('❌ Erro:', err.message);
    await page.screenshot({ path: '/root/.openclaw/workspace/crypto/tmp/qa-card63-error.png' });
    failed++;
  }

  await browser.close();
  console.log(`\n--- Resultado: ${passed}✅ / ${failed}❌ ---`);
  process.exit(failed > 0 ? 1 : 0);
}

run();
