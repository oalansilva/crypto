import { chromium } from 'playwright';
import fs from 'fs';

const BASE = 'http://72.60.150.140:5173';
const SESSION_FILE = '/root/.openclaw/workspace/crypto/tmp/session_card63_state.json';
const results = [];

async function run() {
  const browser = await chromium.launch({ headless: true });
  
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
    } catch {}
  }
  
  if (!sessionData) {
    console.log('❌ Sem token');
    await browser.close();
    return;
  }

  const context = await browser.newContext({
    viewport: { width: 375, height: 812 },
    isMobile: true,
    hasTouch: true,
  });
  
  const page = await context.newPage();
  await page.goto(`${BASE}/login`, { waitUntil: 'domcontentloaded', timeout: 15000 });
  await page.waitForTimeout(1000);
  await page.evaluate(({ accessToken, refreshToken, user }) => {
    localStorage.setItem('auth_access_token', accessToken);
    localStorage.setItem('auth_refresh_token', refreshToken);
    localStorage.setItem('auth_user', JSON.stringify(user));
  }, sessionData);
  
  await page.goto(`${BASE}/kanban`, { waitUntil: 'domcontentloaded', timeout: 15000 });
  
  // Wait for kanban data to load - wait for at least one card to appear
  console.log('Aguardando dados do kanban carregar...');
  try {
    await page.waitForSelector('text=/#\\d+/', { timeout: 15000 });
    console.log('✅ Cards apareceram');
  } catch {
    console.log('⚠️ Timeout esperando cards carregarem');
  }
  await page.waitForTimeout(2000);
  await page.screenshot({ path: '/root/.openclaw/workspace/crypto/qa_artifacts/card63_data_loaded.png', fullPage: true });

  // Get visible card numbers
  const pageText = await page.textContent('body');
  console.log(`Cards visíveis: ${pageText?.match(/#\\d+/g)?.join(', ')}`);

  try {
    // Find 🔍 button
    const sb = await page.$('button:has-text("🔍")');
    if (!sb) { console.log('❌ Botão 🔍 não encontrado'); await browser.close(); return; }
    await sb.click();
    await page.waitForTimeout(1000);
    await page.screenshot({ path: '/root/.openclaw/workspace/crypto/qa_artifacts/card63_search_modal.png', fullPage: true });
    
    // Find visible input
    const inp = await page.$('input:visible');
    if (!inp) { console.log('❌ Input não encontrado'); await browser.close(); return; }
    
    // Test #64
    console.log('\nTestando #64...');
    await inp.fill('#64');
    await page.waitForTimeout(2500);
    
    const url = page.url();
    console.log(`URL: ${url}`);
    await page.screenshot({ path: '/root/.openclaw/workspace/crypto/qa_artifacts/card63_test_64.png', fullPage: true });
    
    // Check for card detail
    const drawerText = await page.textContent('body');
    const hasDrawer = drawerText?.includes('Renomear') || drawerText?.includes('Approval') || drawerText?.includes('#64');
    console.log(`Card detail aberto: ${hasDrawer}`);
    
    if (url.includes('64') || (drawerText?.includes('Renomear'))) {
      results.push('✅ Card #64 ABRIU corretamente');
      console.log('✅ Card #64 ABRIU');
    } else {
      results.push('❌ Card #64 NÃO abriu (toast: card não encontrado)');
      console.log('❌ Card #64 NÃO abriu');
    }

    // Test #54 (for comparison)
    await page.goto(`${BASE}/kanban`, { waitUntil: 'domcontentloaded', timeout: 15000 });
    await page.waitForSelector('text=/#\\d+/', { timeout: 15000 }).catch(() => {});
    await page.waitForTimeout(2000);
    
    const sb2 = await page.$('button:has-text("🔍")');
    if (sb2) {
      await sb2.click();
      await page.waitForTimeout(1000);
      const inp2 = await page.$('input:visible');
      if (inp2) {
        console.log('\nTestando #54...');
        await inp2.fill('#54');
        await page.waitForTimeout(2500);
        await page.screenshot({ path: '/root/.openclaw/workspace/crypto/qa_artifacts/card63_test_54.png', fullPage: true });
        
        const url54 = page.url();
        const body54 = await page.textContent('body');
        if (url54.includes('54') || body54?.includes('Portfolio Optimizer')) {
          results.push('✅ Card #54 ABRIU corretamente');
          console.log('✅ Card #54 ABRIU');
        } else {
          results.push('❌ Card #54 NÃO abriu');
          console.log('❌ Card #54 NÃO abriu');
        }
      }
    }

    // Test #999999
    await page.goto(`${BASE}/kanban`, { waitUntil: 'domcontentloaded', timeout: 15000 });
    await page.waitForSelector('text=/#\\d+/', { timeout: 15000 }).catch(() => {});
    await page.waitForTimeout(2000);
    
    const sb3 = await page.$('button:has-text("🔍")');
    if (sb3) {
      await sb3.click();
      await page.waitForTimeout(1000);
      const inp3 = await page.$('input:visible');
      if (inp3) {
        console.log('\nTestando #999999...');
        await inp3.fill('#999999');
        await page.waitForTimeout(2500);
        await page.screenshot({ path: '/root/.openclaw/workspace/crypto/qa_artifacts/card63_test_999999.png', fullPage: true });
        const toast = await page.$('[role="alert"]');
        if (toast) {
          const txt = await toast.textContent();
          results.push(`✅ Toast para #999999: "${txt}"`);
          console.log(`✅ Toast: "${txt}"`);
        } else {
          results.push('⚠️ Nenhum toast para #999999');
        }
      }
    }
    
  } catch (err) {
    console.error('ERRO:', err.message);
    results.push(`❌ ERRO: ${err.message}`);
  } finally {
    await browser.close();
  }

  console.log('\n=== RESULTADO ===');
  for (const r of results) console.log(r);
}

run();
