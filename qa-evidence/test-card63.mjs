import { chromium } from 'playwright';

const BASE_URL = 'http://72.60.150.140:5173/kanban';
const EVIDENCE_DIR = '/root/.openclaw/workspace/crypto/qa-evidence';

const browser = await chromium.launch({ headless: true });
const page = await browser.newPage();
await page.setViewportSize({ width: 1280, height: 800 });

try {
  console.log('1. Navigating to kanban...');
  await page.goto(BASE_URL, { waitUntil: 'networkidle', timeout: 30000 });

  // Check if login is needed
  const loginInput = page.locator('input[type="text"], input[type="email"], input[name="email"], input[name="username"]').first();
  const isLoginVisible = await loginInput.isVisible({ timeout: 5000 }).catch(() => false);
  
  if (isLoginVisible) {
    console.log('Login required, filling credentials...');
    await loginInput.fill('admin@crypto.com');
    const passwordInput = page.locator('input[type="password"]').first();
    await passwordInput.fill('admin123');
    await page.click('button[type="submit"], button:has-text("Entrar"), button:has-text("Login")');
    await page.waitForLoadState('networkidle');
    console.log('Logged in.');
  }

  // Wait for kanban to load
  await page.waitForTimeout(2000);

  console.log('2. Taking Screenshot 1: toolbar with 🔍 Buscar button...');
  await page.screenshot({ path: `${EVIDENCE_DIR}/card63-toolbar-desktop.png`, fullPage: false });

  // Look for the 🔍 Buscar button in toolbar
  const searchButton = page.locator('button:has-text("🔍"), button:has-text("Buscar")').first();
  const searchBtnVisible = await searchButton.isVisible({ timeout: 5000 }).catch(() => false);
  
  if (!searchBtnVisible) {
    // Try to find it by aria or title
    const altSearchBtn = page.locator('button[aria-label*="search" i], button[title*="search" i], button[aria-label*="buscar" i]').first();
    const altVisible = await altSearchBtn.isVisible({ timeout: 3000 }).catch(() => false);
    if (altVisible) {
      console.log('Found search button by aria/title');
      await altSearchBtn.click();
    } else {
      throw new Error('🔍 Buscar button not found in toolbar!');
    }
  } else {
    console.log('3. Clicking 🔍 Buscar button...');
    await searchButton.click();
  }

  await page.waitForTimeout(500);

  console.log('4. Taking Screenshot 2: modal open...');
  await page.screenshot({ path: `${EVIDENCE_DIR}/card63-modal-open.png`, fullPage: false });

  // Find the search input in modal
  const searchInput = page.locator('input[placeholder*="buscar" i], input[placeholder*="search" i], input[aria-label*="buscar" i], input[id*="search" i]').first();
  const inputVisible = await searchInput.isVisible({ timeout: 5000 }).catch(() => false);
  
  if (!inputVisible) {
    throw new Error('Search input not found in modal!');
  }

  console.log('5. Typing "63" and pressing Enter...');
  await searchInput.fill('63');
  await page.keyboard.press('Enter');
  await page.waitForTimeout(1500);

  console.log('6. Taking Screenshot 3: card #63 drawer open...');
  await page.screenshot({ path: `${EVIDENCE_DIR}/card63-drawer-open.png`, fullPage: false });

  // Now test #71
  console.log('7. Testing card #71...');
  
  // Close current drawer/modal first
  const closeBtn = page.locator('button[aria-label*="close" i], button:has-text("✕"), button:has-text("×"), [data-testid*="close"]').first();
  const closeVisible = await closeBtn.isVisible({ timeout: 2000 }).catch(() => false);
  if (closeVisible) {
    await closeBtn.click();
    await page.waitForTimeout(500);
  }

  // Reopen search modal
  const searchBtn2 = page.locator('button:has-text("🔍"), button:has-text("Buscar")').first();
  await searchBtn2.click();
  await page.waitForTimeout(500);

  const searchInput2 = page.locator('input[placeholder*="buscar" i], input[placeholder*="search" i]').first();
  await searchInput2.fill('71');
  await page.keyboard.press('Enter');
  await page.waitForTimeout(1500);

  await page.screenshot({ path: `${EVIDENCE_DIR}/card71-drawer-open.png`, fullPage: false });
  console.log('Card #71 screenshot saved.');

  console.log('\n✅ TEST PASSOU!');
  console.log('Evidências:');
  console.log(`  - ${EVIDENCE_DIR}/card63-toolbar-desktop.png`);
  console.log(`  - ${EVIDENCE_DIR}/card63-modal-open.png`);
  console.log(`  - ${EVIDENCE_DIR}/card63-drawer-open.png`);
  console.log(`  - ${EVIDENCE_DIR}/card71-drawer-open.png`);

} catch (error) {
  console.error('❌ TEST FALHOU:', error.message);
  await page.screenshot({ path: `${EVIDENCE_DIR}/card63-error.png`, fullPage: false }).catch(() => {});
  console.log('Error screenshot:', `${EVIDENCE_DIR}/card63-error.png`);
  process.exit(1);
} finally {
  await browser.close();
}
