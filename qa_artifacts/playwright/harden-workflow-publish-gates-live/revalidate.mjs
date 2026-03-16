import { chromium } from 'playwright';
import fs from 'node:fs/promises';

const out = new URL('./', import.meta.url);
await fs.mkdir(out, { recursive: true });
const browser = await chromium.launch({ headless: true, chromiumSandbox: false });
const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
await page.goto('http://72.60.150.140:5173/kanban', { waitUntil: 'networkidle' });
await page.screenshot({ path: new URL('02-board-live.png', out).pathname, fullPage: true });
await page.getByRole('button', { name: /Open details for harden-workflow-publish-gates/i }).click();
await page.waitForLoadState('networkidle');
await page.screenshot({ path: new URL('03-drawer-live.png', out).pathname, fullPage: true });
const payload = await page.evaluate(async () => {
  const [kanbanRes, changeRes, commentsRes] = await Promise.all([
    fetch('http://72.60.150.140:8003/api/workflow/kanban/changes?project_slug=crypto').then(r => r.json()),
    fetch('http://72.60.150.140:8003/api/workflow/projects/crypto/changes/harden-workflow-publish-gates').then(r => r.json()),
    fetch('http://72.60.150.140:8003/api/workflow/kanban/changes/harden-workflow-publish-gates/comments?project_slug=crypto').then(r => r.json()),
  ]);
  return { kanbanRes, changeRes, commentsRes, drawerText: document.body.innerText };
});
await fs.writeFile(new URL('04-live-ui-payload.json', out), JSON.stringify(payload, null, 2));
await browser.close();
