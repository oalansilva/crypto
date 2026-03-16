import { chromium } from 'playwright';
import fs from 'node:fs/promises';
import path from 'node:path';

const outDir = '/root/.openclaw/workspace/crypto/frontend/qa_artifacts/playwright/numera-o-cards-live-recheck';
await fs.mkdir(outDir, { recursive: true });
const baseUrl = 'http://127.0.0.1:5173/kanban';

const browser = await chromium.launch({ headless: true });
const context = await browser.newContext({ viewport: { width: 1440, height: 900 } });
const page = await context.newPage();
const result = { boardHasHash16: false, drawerHasHash16: false, afterReloadBoardHasHash16: false, notes: [] };

try {
  await page.goto(baseUrl, { waitUntil: 'networkidle' });
  await page.screenshot({ path: path.join(outDir, '01-board-initial.png'), fullPage: true });
  const body1 = await page.locator('body').innerText();
  result.boardHasHash16 = /#16\b/.test(body1);
  result.notes.push(`board initial has #16: ${result.boardHasHash16}`);

  const card = page.getByRole('button', { name: /Open details for numera-o-cards/i });
  await card.waitFor({ state: 'visible', timeout: 15000 });
  await card.click();
  await page.waitForTimeout(1000);
  await page.screenshot({ path: path.join(outDir, '02-drawer-open.png'), fullPage: true });
  const body2 = await page.locator('body').innerText();
  result.drawerHasHash16 = /#16\b/.test(body2);
  result.notes.push(`drawer open has #16: ${result.drawerHasHash16}`);

  await page.reload({ waitUntil: 'networkidle' });
  await page.screenshot({ path: path.join(outDir, '03-board-after-reload.png'), fullPage: true });
  const body3 = await page.locator('body').innerText();
  result.afterReloadBoardHasHash16 = /#16\b/.test(body3);
  result.notes.push(`board after reload has #16: ${result.afterReloadBoardHasHash16}`);

  await fs.writeFile(path.join(outDir, 'summary.json'), JSON.stringify(result, null, 2));
  console.log(JSON.stringify(result, null, 2));
} catch (error) {
  result.error = error instanceof Error ? error.message : String(error);
  await fs.writeFile(path.join(outDir, 'summary.json'), JSON.stringify(result, null, 2));
  console.log(JSON.stringify(result, null, 2));
  process.exitCode = 1;
} finally {
  await browser.close();
}
