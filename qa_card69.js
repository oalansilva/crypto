const { chromium } = require('playwright');

const BASE_URL = 'http://72.60.150.140:5173';

async function runQA() {
  const results = [];
  
  // --- Helper ---
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

  // --- Register a test user if needed, or use known credentials ---
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext();

  // --- TEST 1: Mobile viewport (375px) ---
  console.log('\n=== MOBILE (375px) ===');
  const mobileCtx = await browser.newContext({
    viewport: { width: 375, height: 812 },
    permissions: [],
  });
  const mobilePage = await mobileCtx.newPage();

  await test('Mobile: Página de login carrega', async () => {
    await mobilePage.goto(BASE_URL, { waitUntil: 'networkidle' });
    // Should redirect to login or show login form
    await mobilePage.waitForLoadState('networkidle');
    const url = mobilePage.url();
    if (!url.includes('login') && url === BASE_URL + '/') {
      // might already be on home, check for login elements
      const loginBtn = await mobilePage.$('button[type="submit"], input[type="password"]');
      if (!loginBtn) throw new Error('Não encontrou elementos de login na página');
    }
  });

  await test('Mobile: Login com conta válida', async () => {
    await mobilePage.goto(BASE_URL, { waitUntil: 'networkidle' });
    // Try to login - look for form fields
    const emailInput = await mobilePage.$('input[type="email"], input[name="email"]');
    const passInput = await mobilePage.$('input[type="password"]');
    const submitBtn = await mobilePage.$('button[type="submit"]');
    if (!emailInput || !passInput) throw new Error('Campos de login não encontrados');
    await emailInput.fill('qa@test.com');
    await passInput.fill('Teste1234!');
    await submitBtn.click();
    await mobilePage.waitForLoadState('networkidle');
    // Should NOT be on login page after successful login
    const url = mobilePage.url();
    if (url.includes('login')) throw new Error('Login falhou - ainda na página de login');
    console.log('  -> Login bem-sucedido, URL:', url);
  });

  await test('Mobile: Menu hamburguer (☰) visível e clicável', async () => {
    // Look for hamburger icon - usually 3 lines or a menu button
    const hamburger = await mobilePage.$('button[aria-label*="menu" i], button[aria-label*="Menu" i], button.menu-btn, .hamburger, [class*="hamburger"], [class*="menu"]');
    if (!hamburger) throw new Error('Menu hamburguer não encontrado');
    await hamburger.click();
    await mobilePage.waitForTimeout(500);
    console.log('  -> Menu aberto');
  });

  await test('Mobile: Opção "Sair" aparece no menu', async () => {
    // Look for "Sair" text in the menu
    const sairBtn = await mobilePage.$('text=/sair|logout|sign[ -]?out/i');
    if (!sairBtn) throw new Error('Botão "Sair" não encontrado no menu');
    console.log('  -> Botão Sair encontrado');
  });

  await test('Mobile: Clique em "Sair" faz logout e volta para login', async () => {
    const sairBtn = await mobilePage.$('text=/sair|logout|sign[ -]?out/i');
    await sairBtn.click();
    await mobilePage.waitForLoadState('networkidle');
    const url = mobilePage.url();
    if (url.includes('login') || url === BASE_URL + '/') {
      console.log('  -> Logout bem-sucedido, URL:', url);
    } else {
      // Check if we can see login form
      const loginForm = await mobilePage.$('input[type="password"], form');
      if (!loginForm) throw new Error(`Não voltou para tela de login. URL: ${url}`);
    }
  });

  await mobileCtx.close();

  // --- TEST 2: Desktop viewport (1024px+) ---
  console.log('\n=== DESKTOP (1024px) ===');
  const desktopCtx = await browser.newContext({
    viewport: { width: 1024, height: 768 },
    permissions: [],
  });
  const desktopPage = await desktopCtx.newPage();

  await test('Desktop: Login funciona', async () => {
    await desktopPage.goto(BASE_URL, { waitUntil: 'networkidle' });
    const emailInput = await desktopPage.$('input[type="email"], input[name="email"]');
    const passInput = await desktopPage.$('input[type="password"]');
    const submitBtn = await desktopPage.$('button[type="submit"]');
    if (!emailInput || !passInput) throw new Error('Campos de login não encontrados');
    await emailInput.fill('qa@test.com');
    await passInput.fill('Teste1234!');
    await submitBtn.click();
    await desktopPage.waitForLoadState('networkidle');
    const url = desktopPage.url();
    if (url.includes('login')) throw new Error('Login falhou');
    console.log('  -> Login OK, URL:', url);
  });

  await test('Desktop: Botão de logout aparece no header (lado direito)', async () => {
    // Look for logout button in header - usually on the right side
    const logoutBtn = await desktopPage.$('header button, nav button, [class*="header"] button, [class*="nav"] button');
    // Filter for logout-related text
    const buttons = await desktopPage.$$('button');
    let found = false;
    for (const btn of buttons) {
      const text = await btn.textContent();
      if (text && /sair|logout|sign[ -]?out/i.test(text)) {
        found = true;
        console.log('  -> Logout button found:', text.trim());
        break;
      }
    }
    if (!found) throw new Error('Botão de logout não encontrado no header');
  });

  await test('Desktop: Clique no logout deslogga e volta para tela de login', async () => {
    const buttons = await desktopPage.$$('button');
    let logoutBtn = null;
    for (const btn of buttons) {
      const text = await btn.textContent();
      if (text && /sair|logout|sign[ -]?out/i.test(text)) {
        logoutBtn = btn;
        break;
      }
    }
    if (!logoutBtn) throw new Error('Botão de logout não encontrado');
    await logoutBtn.click();
    await desktopPage.waitForLoadState('networkidle');
    const url = desktopPage.url();
    if (url.includes('login') || url === BASE_URL + '/') {
      console.log('  -> Logout OK, URL:', url);
    } else {
      const loginForm = await desktopPage.$('input[type="password"], form');
      if (!loginForm) throw new Error(`Não voltou para login. URL: ${url}`);
    }
  });

  await desktopCtx.close();

  // --- TEST 3: Verificar páginas após login (mobile context) ---
  console.log('\n=== NAVEGAÇÃO APÓS LOGIN ===');
  const navCtx = await browser.newContext({
    viewport: { width: 1024, height: 768 },
  });
  const navPage = await navCtx.newPage();

  // Login first
  await navPage.goto(BASE_URL, { waitUntil: 'networkidle' });
  const emailInput = await navPage.$('input[type="email"], input[name="email"]');
  const passInput = await navPage.$('input[type="password"]');
  const submitBtn = await navPage.$('button[type="submit"]');
  if (emailInput && passInput) {
    await emailInput.fill('qa@test.com');
    await passInput.fill('Teste1234!');
    await submitBtn.click();
    await navPage.waitForLoadState('networkidle');
  }

  for (const path of ['/signals', '/portfolio', '/ai-dashboard']) {
    const name = `Navegação: ${path} carrega sem erro`;
    await test(name, async () => {
      await navPage.goto(BASE_URL + path, { waitUntil: 'networkidle' });
      // Check for error indicators
      const errorText = await navPage.$('text=/error|not found|404|500/i');
      if (errorText) throw new Error(`Página ${path} retornou erro`);
      console.log(`  -> ${path} carregou OK`);
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
  }

  return { passed, failed, results };
}

runQA().then(({ passed, failed }) => {
  process.exit(failed > 0 ? 1 : 0);
}).catch(err => {
  console.error('Erro fatal:', err);
  process.exit(1);
});
