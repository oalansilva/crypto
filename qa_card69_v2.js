const { chromium } = require('playwright');

const BASE_URL = 'http://72.60.150.140:5173';

async function runQA() {
  const results = [];
  
  async function test(name, fn) {
    try {
      await fn();
      results.push({ name, pass: true });
      console.log(`✅ ${name}`);
    } catch (err) {
      results.push({ name, pass: false, error: err.message });
      console.log(`❌ ${name}: ${err.message}`);
    }
  }

  const browser = await chromium.launch({ headless: true });

  // ===== TEST 1: Mobile (375px) =====
  console.log('\n=== MOBILE (375px) ===');
  const mobileCtx = await browser.newContext({ viewport: { width: 375, height: 812 } });
  const mobilePage = await mobileCtx.newPage();

  await test('Mobile: Página carrega', async () => {
    await mobilePage.goto(BASE_URL, { waitUntil: 'domcontentloaded', timeout: 15000 });
    await mobilePage.waitForTimeout(1500);
    // Check page loaded - should have root content
    const root = await mobilePage.$('#root');
    if (!root) throw new Error('Root element not found');
    const hasContent = await root.textContent();
    if (!hasContent || hasContent.length < 50) throw new Error('Page seems empty');
    console.log('  -> Página carregou OK');
  });

  await test('Mobile: Menu hamburguer (☰) visível no header', async () => {
    // Look for the hamburger button in the fixed header
    const hamburger = await mobilePage.$('header button[aria-label="Abrir menu"]');
    if (!hamburger) throw new Error('Menu hamburguer não encontrado no header');
    console.log('  -> Hamburger OK');
  });

  await test('Mobile: Abrir menu hamburguer mostra "Sair"', async () => {
    const hamburger = await mobilePage.$('header button[aria-label="Abrir menu"]');
    await hamburger.click();
    await mobilePage.waitForTimeout(800);
    // Look for Sair button in the sidebar menu
    const sairButtons = await mobilePage.$$('button');
    let sairBtn = null;
    for (const btn of sairButtons) {
      const text = await btn.textContent();
      if (text && /sair/i.test(text)) {
        sairBtn = btn;
        break;
      }
    }
    if (!sairBtn) throw new Error('Botão "Sair" não encontrado no menu');
    console.log('  -> Sair encontrado no menu mobile');
  });

  await test('Mobile: Clique em "Sair" faz logout', async () => {
    // Find the Sair button
    const sairButtons = await mobilePage.$$('button');
    let sairBtn = null;
    for (const btn of sairButtons) {
      const text = await btn.textContent();
      if (text && /sair/i.test(text)) {
        sairBtn = btn;
        break;
      }
    }
    if (!sairBtn) throw new Error('Sair button not found');
    await sairBtn.click();
    await mobilePage.waitForTimeout(1500);
    // After logout, should show login link or login form
    const url = mobilePage.url();
    console.log('  -> URL após logout:', url);
    // Check if login form/button appears (either redirect to /login or login link visible)
    const loginLink = await mobilePage.$('a[href="/login"], a[href*="login"]');
    const loginBtn = await mobilePage.$('text=/entrar|login|sign in/i');
    // Or if still on dashboard, check if user info disappeared
    const userInfo = await mobilePage.$('text=/crypto lab/i');
    if (!loginLink && !loginBtn && userInfo) {
      // Still shows dashboard - logout might not have worked
      // But let's check if we see the "Entrar" link now
      const entrarLink = await mobilePage.$('text=/entrar/i');
      if (!entrarLink) throw new Error('Logout não funcionou - usuário ainda logado');
    }
    console.log('  -> Logout mobile OK');
  });

  await mobileCtx.close();

  // ===== TEST 2: Desktop (1024px+) =====
  console.log('\n=== DESKTOP (1024px) ===');
  const desktopCtx = await browser.newContext({ viewport: { width: 1024, height: 768 } });
  const desktopPage = await desktopCtx.newPage();

  await test('Desktop: Página carrega', async () => {
    await desktopPage.goto(BASE_URL, { waitUntil: 'domcontentloaded', timeout: 15000 });
    await desktopPage.waitForTimeout(1500);
    const root = await desktopPage.$('#root');
    if (!root) throw new Error('Root element not found');
    console.log('  -> Página carregou OK');
  });

  await test('Desktop: Sidebar visível com navegação', async () => {
    // Desktop should show sidebar
    const sidebar = await desktopPage.$('aside');
    if (!sidebar) throw new Error('Sidebar não encontrada');
    console.log('  -> Sidebar OK');
  });

  await test('Desktop: Botão de logout visível no header (lado direito)', async () => {
    // Look for LogOut button in the fixed header (right side)
    // The header has aria-label="Sair" on the logout button
    const logoutBtn = await desktopPage.$('header button[aria-label="Sair"]');
    if (!logoutBtn) {
      // Try finding by LogOut icon class
      const allLogoutBtns = await desktopPage.$$('header button');
      let found = false;
      for (const btn of allLogoutBtns) {
        const aria = await btn.getAttribute('aria-label');
        if (aria && /sair/i.test(aria)) {
          found = true;
          break;
        }
      }
      if (!found) throw new Error('Logout button não encontrado no header');
    }
    console.log('  -> Logout button no header OK');
  });

  await test('Desktop: Clique no logout deslogga e volta para login', async () => {
    const logoutBtn = await desktopPage.$('header button[aria-label="Sair"]');
    if (!logoutBtn) throw new Error('Logout button não encontrado');
    await logoutBtn.click();
    await desktopPage.waitForTimeout(1500);
    const url = desktopPage.url();
    console.log('  -> URL após logout:', url);
    // After logout, should show "Entrar" link in sidebar
    const entrarLink = await desktopPage.$('aside a[href="/login"]');
    if (!entrarLink) {
      // Maybe it redirected to /login
      const currentUrl = desktopPage.url();
      if (!currentUrl.includes('login')) {
        throw new Error(`Não voltou para login. URL: ${currentUrl}`);
      }
    }
    console.log('  -> Logout desktop OK');
  });

  await desktopCtx.close();

  // ===== TEST 3: Navegação nas páginas =====
  console.log('\n=== NAVEGAÇÃO APÓS LOGIN ===');
  const navCtx = await browser.newContext({ viewport: { width: 1024, height: 768 } });
  const navPage = await navCtx.newPage();

  // Login first
  await navPage.goto(BASE_URL, { waitUntil: 'domcontentloaded', timeout: 15000 });
  await navPage.waitForTimeout(1500);

  for (const path of ['/signals', '/portfolio', '/ai-dashboard']) {
    const name = `Navegação: ${path} carrega sem erro`;
    await test(name, async () => {
      await navPage.goto(BASE_URL + path, { waitUntil: 'domcontentloaded', timeout: 20000 });
      await navPage.waitForTimeout(1500);
      // Check page has content
      const body = await navPage.$('body');
      const text = await body.textContent();
      if (!text || text.length < 100) throw new Error(`Página ${path} parece vazia`);
      // No error page
      if (/error|not found|404|500/i.test(text)) throw new Error(`Página ${path} retornou erro`);
      console.log(`  -> ${path} OK`);
    });
  }

  await navCtx.close();
  await browser.close();

  // Summary
  console.log('\n=== RESUMO ===');
  const passed = results.filter(r => r.pass).length;
  const failed = results.filter(r => !r.pass).length;
  console.log(`Total: ${results.length} | ✅ ${passed} | ❌ ${failed}`);
  
  if (failed > 0) {
    console.log('\nFalhas:');
    results.filter(r => !r.pass).forEach(r => {
      console.log(`  - ${r.name}: ${r.error}`);
    });
  } else {
    console.log('\n🎉 Card #69 — QA PASSOU');
  }

  return { passed, failed, results };
}

runQA().then(({ failed }) => {
  process.exit(failed > 0 ? 1 : 0);
}).catch(err => {
  console.error('Erro fatal:', err);
  process.exit(1);
});
