import { chromium } from 'playwright';
import fs from 'fs';

const BASE = 'http://72.60.150.140:5173';
const SESSION_FILE = '/root/.openclaw/workspace/crypto/tmp/session_card63_state.json';
const results = [];

async function getAuthTokens() {
  const email = 'qa_card63@test.com';
  const password = 'Teste1234!';
  
  let res = await fetch(`${BASE}/api/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password })
  });
  
  if (res.status === 200) {
    const data = await res.json();
    return { 
      accessToken: data.accessToken, 
      refreshToken: data.refreshToken, 
      user: { id: data.id, email: data.email, name: data.name, isAdmin: data.isAdmin } 
    };
  }
  
  // Register
  res = await fetch(`${BASE}/api/auth/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password, name: 'QA Card63' })
  });
  
  if (res.ok) {
    const loginRes = await fetch(`${BASE}/api/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });
    const data = await loginRes.json();
    return { 
      accessToken: data.accessToken, 
      refreshToken: data.refreshToken, 
      user: { id: data.id, email: data.email, name: data.name, isAdmin: data.isAdmin } 
    };
  }
  
  return null;
}

async function run() {
  const browser = await chromium.launch({ headless: true });
  
  // Get or create auth tokens
  let sessionData = null;
  if (fs.existsSync(SESSION_FILE)) {
    try { 
      const saved = JSON.parse(fs.readFileSync(SESSION_FILE, 'utf8'));
      if (saved.accessToken) {
        const meRes = await fetch(`${BASE}/api/auth/me`, {
          headers: { 'Authorization': `Bearer ${saved.accessToken}` }
        });
        if (meRes.ok) sessionData = saved;
      }
    } catch { sessionData = null; }
  }
  
  if (!sessionData) {
    sessionData = await getAuthTokens();
    if (sessionData) fs.writeFileSync(SESSION_FILE, JSON.stringify(sessionData));
  }
  
  if (!sessionData) {
    console.log('❌ Não foi possível obter tokens');
    await browser.close();
    return;
  }
  
  console.log('✅ Token obtido e validado');

  // Create context and set localStorage via navigation
  const context = await browser.newContext({
    viewport: { width: 375, height: 812 },
    deviceScaleFactor: 3,
    isMobile: true,
    hasTouch: true,
  });
  
  const page = await context.newPage();

  // Navigate to the app first - it will redirect to /login
  await page.goto(`${BASE}/login`, { waitUntil: 'domcontentloaded', timeout: 30000 });
  await page.waitForTimeout(2000);
  
  // Set localStorage while on the login page (same origin)
  await page.evaluate(({ accessToken, refreshToken, user }) => {
    localStorage.setItem('auth_access_token', accessToken);
    localStorage.setItem('auth_refresh_token', refreshToken);
    localStorage.setItem('auth_user', JSON.stringify(user));
  }, sessionData);
  
  console.log('✅ localStorage configured');
  
  // Now navigate to kanban
  await page.goto(`${BASE}/kanban`, { waitUntil: 'domcontentloaded', timeout: 30000 });
  await page.waitForTimeout(4000);
  
  const url1 = page.url();
  console.log(`   URL atual: ${url1}`);
  await page.screenshot({ path: '/root/.openclaw/workspace/crypto/qa_artifacts/card63_01_kanban.png', fullPage: true });

  if (url1.includes('login')) {
    results.push('❌ STILL on login page after auth injection');
    console.log('❌ Still on login page');
    await browser.close();
    return;
  }
  
  results.push('✅ Kanban carregou com autenticação');
  console.log('✅ Kanban loaded');

  try {
    console.log('\n2. Procurando botão 🔍 Buscar...');
    
    const allBtns = await page.$$('button');
    console.log(`   Total de botões: ${allBtns.length}`);
    for (const btn of allBtns) {
      const text = await btn.textContent();
      console.log(`   Botão: "${text?.trim()}"`);
    }

    let searchBtn = null;
    for (const btn of allBtns) {
      const text = await btn.textContent();
      if (text && (text.includes('🔍') || text.toLowerCase().includes('buscar'))) {
        searchBtn = btn;
        break;
      }
    }

    if (!searchBtn) {
      results.push('❌ Botão 🔍 Buscar NÃO encontrado no toolbar mobile');
      console.log('❌ Botão não encontrado');
    } else {
      await searchBtn.click();
      await page.waitForTimeout(1500);
      await page.screenshot({ path: '/root/.openclaw/workspace/crypto/qa_artifacts/card63_03_search_open.png', fullPage: true });
      results.push('✅ Botão 🔍 Buscar encontrado e clicado');
      console.log('✅ Botão clicado');

      // Find search input
      const allInputs = await page.$$('input');
      let searchInput = null;
      for (const inp of allInputs) {
        if (await inp.isVisible()) {
          searchInput = inp;
          break;
        }
      }
      if (!searchInput) searchInput = await page.$('input[type="search"]');
      if (!searchInput) searchInput = await page.$('input[placeholder*="buscar" i]');
      if (!searchInput) searchInput = await page.$('input[placeholder*="card" i]');
      
      if (searchInput) {
        console.log('✅ Campo de busca encontrado');
        
        // Test #54
        console.log('\n3. Digitando #54...');
        await searchInput.fill('#54');
        await page.waitForTimeout(1500);
        await page.screenshot({ path: '/root/.openclaw/workspace/crypto/qa_artifacts/card63_04_search_54.png', fullPage: true });
        await page.waitForTimeout(2000);
        
        const url54 = page.url();
        console.log(`   URL após buscar #54: ${url54}`);
        
        const pageText = await page.textContent('body');
        const has54 = pageText && (pageText.includes('#54') || pageText.includes('Card #54') || pageText.includes('card #54'));
        
        if (url54.includes('54')) {
          results.push('✅ Card #54 ABRIU - URL mudou para incluir 54');
          await page.screenshot({ path: '/root/.openclaw/workspace/crypto/qa_artifacts/card63_05_card54_opened.png', fullPage: true });
        } else if (has54) {
          results.push('✅ Card #54 ABRIU - texto 54 aparece na página');
          await page.screenshot({ path: '/root/.openclaw/workspace/crypto/qa_artifacts/card63_05_card54_opened.png', fullPage: true });
        } else {
          results.push('❌ Card #54 NÃO abriu após busca');
          await page.screenshot({ path: '/root/.openclaw/workspace/crypto/qa_artifacts/card63_05_card54_not_opened.png', fullPage: true });
        }
        
        // Back to kanban
        await page.goto(`${BASE}/kanban`, { waitUntil: 'domcontentloaded', timeout: 15000 });
        await page.waitForTimeout(2000);
        
        // Test #64
        console.log('\n4. Testando #64...');
        const sb2 = await page.$('button:has-text("🔍")');
        if (sb2) {
          await sb2.click();
          await page.waitForTimeout(1000);
          const inp2 = await page.$('input:visible');
          if (inp2) {
            await inp2.fill('#64');
            await page.waitForTimeout(2000);
            await page.screenshot({ path: '/root/.openclaw/workspace/crypto/qa_artifacts/card63_06_search_64.png', fullPage: true });
            const url64 = page.url();
            if (url64.includes('64')) {
              results.push('✅ Card #64 abriu corretamente');
            }
          }
        }
        
        await page.goto(`${BASE}/kanban`, { waitUntil: 'domcontentloaded', timeout: 15000 });
        await page.waitForTimeout(2000);
        
        // Test #999999
        console.log('\n5. Testando #999999 (inexistente)...');
        const sb3 = await page.$('button:has-text("🔍")');
        if (sb3) {
          await sb3.click();
          await page.waitForTimeout(1000);
          const inp3 = await page.$('input:visible');
          if (inp3) {
            await inp3.fill('#999999');
            await page.waitForTimeout(2500);
            await page.screenshot({ path: '/root/.openclaw/workspace/crypto/qa_artifacts/card63_07_search_999999.png', fullPage: true });
            
            const toasts = await page.$$('[role="alert"], [class*="toast"], [class*="notification"], [class*="snackbar"], .ant-message');
            if (toasts.length > 0) {
              for (const t of toasts) {
                const txt = await t.textContent();
                console.log(`   Toast: "${txt?.trim()}"`);
                results.push(`✅ Toast informativo: "${txt?.trim()}"`);
              }
            } else {
              results.push('⚠️ Nenhum toast para card inexistente #999999');
              console.log('⚠️ Nenhum toast encontrado');
            }
          }
        }
      } else {
        results.push('❌ Campo de busca não encontrado');
      }
    }
  } catch (err) {
    console.error('❌ ERRO:', err.message);
    results.push(`❌ ERRO: ${err.message}`);
    try {
      await page.screenshot({ path: '/root/.openclaw/workspace/crypto/qa_artifacts/card63_error.png', fullPage: true });
    } catch {}
  } finally {
    await browser.close();
  }

  console.log('\n=== RESULTADO DO QA CARD #63 ===');
  for (const r of results) {
    console.log(r);
  }
}

run();
