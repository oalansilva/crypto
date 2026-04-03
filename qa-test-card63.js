const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  await page.setViewportSize({ width: 1280, height: 800 });

  console.log('1. Abrindo Kanban...');
  await page.goto('http://72.60.150.140:5173/kanban', { waitUntil: 'networkidle', timeout: 30000 });

  console.log('2. Tirando screenshot do toolbar desktop...');
  await page.screenshot({ path: '/root/.openclaw/workspace/crypto/qa-evidence/card63-search-desktop-ok.png', fullPage: false });

  // Wait for page to settle
  await page.waitForTimeout(2000);

  // Look for the search button (🔍 Buscar)
  console.log('3. Procurando botão Buscar...');
  const searchButton = await page.locator('button:has-text("Buscar"), button:has-text("🔍"), [class*="search"], [aria-label*="search" i], [aria-label*="buscar" i]').first();
  
  let clicked = false;
  try {
    await searchButton.click({ timeout: 5000 });
    clicked = true;
    console.log('   ✓ Botão Buscar clicado');
  } catch (e) {
    console.log('   Botão não encontrado pelo texto, tentando outras formas...');
    // Try finding by aria-label or title
    const allButtons = await page.locator('button').all();
    for (const btn of allButtons) {
      const label = await btn.getAttribute('aria-label') || await btn.getAttribute('title') || '';
      const text = await btn.textContent() || '';
      console.log(`   Button: "${text}" | aria-label: "${label}"`);
      if (label.toLowerCase().includes('buscar') || label.toLowerCase().includes('search') || text.includes('🔍') || text.includes('Buscar')) {
        await btn.click();
        clicked = true;
        console.log('   ✓ Botão encontrado e clicado');
        break;
      }
    }
  }

  await page.waitForTimeout(1000);

  if (clicked) {
    // Type #63 in search input
    console.log('4. Digitando #63 no campo de busca...');
    const inputs = await page.locator('input[type="text"], input[placeholder*=""], input').all();
    let foundInput = false;
    for (const inp of inputs) {
      const visible = await inp.isVisible();
      if (visible) {
        await inp.fill('#63');
        foundInput = true;
        console.log('   ✓ Input encontrado e #63 digitado');
        break;
      }
    }
    
    if (!foundInput) {
      // Just type directly
      await page.keyboard.type('#63');
    }

    await page.waitForTimeout(2000);
    
    // Take screenshot of search result
    console.log('5. Tirando screenshot do resultado...');
    await page.screenshot({ path: '/root/.openclaw/workspace/crypto/qa-evidence/card63-search-result.png', fullPage: false });

    // Try pressing Enter
    await page.keyboard.press('Enter');
    await page.waitForTimeout(2000);
    await page.screenshot({ path: '/root/.openclaw/workspace/crypto/qa-evidence/card63-search-result.png', fullPage: false });

    // Now test with #71
    console.log('6. Limpando e testando #71...');
    const inputs2 = await page.locator('input[type="text"], input').all();
    for (const inp of inputs2) {
      const visible = await inp.isVisible();
      if (visible) {
        await inp.fill('');
        await inp.fill('#71');
        break;
      }
    }
    await page.keyboard.press('Enter');
    await page.waitForTimeout(2000);
    await page.screenshot({ path: '/root/.openclaw/workspace/crypto/qa-evidence/card63-search-71.png', fullPage: false });
    console.log('   ✓ Screenshot de #71 salvo');
  }

  await browser.close();
  console.log('Done!');
})();
