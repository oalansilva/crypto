async page => {
  const fs = require('fs');
  const path = require('path');

  const baseUrl = 'http://127.0.0.1:5173';
  const publicBase = 'http://72.60.150.140:5173/qa-artifacts/playwright';
  const root = '/root/.openclaw/workspace/crypto/qa_artifacts/playwright';
  const stamp = new Date().toISOString().replace(/[:.]/g, '-');
  const title = `QA Kanban ${stamp}`;
  const description = `Manual QA drag/drop verification ${stamp}`;
  const result = { stamp, title, description, verdict: 'PASS', defects: [], flows: {} };

  const ensureDir = (name) => {
    const dir = path.join(root, name);
    fs.mkdirSync(dir, { recursive: true });
    return dir;
  };
  const shot = async (name, file) => {
    const full = path.join(ensureDir(name), file);
    await page.screenshot({ path: full, fullPage: true });
    return `${publicBase}/${name}/${file}`;
  };
  const writeSummary = (name, obj) => fs.writeFileSync(path.join(ensureDir(name), 'summary.json'), JSON.stringify(obj, null, 2));
  const getBoard = async () => {
    const data = await page.evaluate(async () => {
      const res = await fetch('/api/workflow/kanban/changes?project_slug=crypto');
      return await res.json();
    });
    return data.items;
  };
  const getChange = async (id) => (await getBoard()).find((it) => it.id === id) || null;
  const waitForColumn = async (id, column, timeout = 15000) => {
    const started = Date.now();
    while (Date.now() - started < timeout) {
      const item = await getChange(id);
      if (item && item.column === column) return item;
      await page.waitForTimeout(300);
    }
    throw new Error(`Timed out waiting for ${id} in ${column}`);
  };
  const defect = (flow, extra) => { result.verdict = 'FAIL'; result.defects.push({ flow, ...extra }); };
  const checkStatus = (item, key, expected, flow) => {
    const actual = item?.status?.[key];
    if (actual !== expected) defect(flow, { summary: `Gate ${key} mismatch`, expected, actual, id: item?.id });
  };

  await page.setViewportSize({ width: 1440, height: 900 });
  await page.goto(`${baseUrl}/kanban`, { waitUntil: 'networkidle' });

  const flow1 = 'create-card';
  result.flows[flow1] = { links: {} };
  result.flows[flow1].links.before = await shot(flow1, '01-before.png');
  await page.getByPlaceholder('Novo card / backlog item').nth(0).fill(title);
  await page.getByPlaceholder('Descrição opcional').nth(0).fill(description);
  await page.getByRole('button', { name: 'Criar card' }).click();
  await page.waitForTimeout(1200);
  const created = (await getBoard()).find((it) => it.title === title);
  if (!created) throw new Error('Created card not found in board API');
  result.changeId = created.id;
  result.flows[flow1].changeId = created.id;
  if (created.column !== 'Pending') defect(flow1, { summary: 'Created card not in Pending', expected: 'Pending', actual: created.column, id: created.id });
  if (created.description !== description) defect(flow1, { summary: 'Description not persisted', expected: description, actual: created.description, id: created.id });
  result.flows[flow1].links.after = await shot(flow1, '02-after.png');
  const desktopCard = page.getByRole('button', { name: new RegExp(created.id) }).first();
  await desktopCard.click();
  await page.waitForTimeout(800);
  const drawerText = await page.locator('aside').textContent();
  if (!drawerText?.includes(description)) defect(flow1, { summary: 'Drawer missing description', expected: description, actual: drawerText, id: created.id });
  result.flows[flow1].links.drawer = await shot(flow1, '03-drawer.png');
  await page.getByRole('button', { name: 'Close panel' }).click();
  writeSummary(flow1, result.flows[flow1]);

  const flow2 = 'desktop-drag';
  result.flows[flow2] = { links: {}, transitions: [] };
  result.flows[flow2].links.before = await shot(flow2, '01-before.png');
  let current = 'Pending';
  for (const target of ['PO', 'DEV', 'QA']) {
    const targetCol = page.locator('section').filter({ has: page.getByText(target) }).first();
    const card = page.getByRole('button', { name: new RegExp(created.id) }).first();
    await card.scrollIntoViewIfNeeded();
    const sourceBox = await card.boundingBox();
    const targetBox = await targetCol.boundingBox();
    if (!sourceBox || !targetBox) throw new Error(`Missing drag boxes ${current}->${target}`);
    await page.mouse.move(sourceBox.x + sourceBox.width / 2, sourceBox.y + 20);
    await page.mouse.down();
    await page.mouse.move(targetBox.x + targetBox.width / 2, targetBox.y + 120, { steps: 24 });
    await page.mouse.up();
    const moved = await waitForColumn(created.id, target, 15000);
    result.flows[flow2].transitions.push({ from: current, to: target, status: moved.status });
    current = target;
    await page.waitForTimeout(500);
  }
  const afterQa = await getChange(created.id);
  if (!afterQa) throw new Error('Card missing after drag flow');
  if (afterQa.column !== 'QA') defect(flow2, { summary: 'Card did not end in QA', expected: 'QA', actual: afterQa.column, id: created.id });
  checkStatus(afterQa, 'PO', 'approved', flow2);
  checkStatus(afterQa, 'DEV', 'approved', flow2);
  checkStatus(afterQa, 'QA', 'pending', flow2);
  result.flows[flow2].links.after = await shot(flow2, '02-after-qa.png');
  await page.getByRole('button', { name: new RegExp(created.id) }).first().click();
  await page.waitForTimeout(700);
  result.flows[flow2].links.drawer = await shot(flow2, '03-drawer-qa.png');
  await page.getByRole('button', { name: 'Close panel' }).click();
  await page.reload({ waitUntil: 'networkidle' });
  const afterReload = await waitForColumn(created.id, 'QA', 15000);
  result.flows[flow2].afterReload = afterReload;
  checkStatus(afterReload, 'PO', 'approved', flow2);
  checkStatus(afterReload, 'DEV', 'approved', flow2);
  checkStatus(afterReload, 'QA', 'pending', flow2);
  result.flows[flow2].links.reload = await shot(flow2, '04-after-reload.png');
  writeSummary(flow2, result.flows[flow2]);

  const flow3 = 'mobile-long-press';
  result.flows[flow3] = { links: {} };
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto(`${baseUrl}/kanban`, { waitUntil: 'networkidle' });
  await page.getByRole('tab', { name: /^QA / }).click();
  await page.waitForTimeout(1000);
  result.flows[flow3].links.before = await shot(flow3, '01-before.png');
  const mobileCard = page.getByRole('button', { name: new RegExp(created.id) }).first();
  const box = await mobileCard.boundingBox();
  if (!box) throw new Error('Mobile card not found in QA tab');
  await page.evaluate(async ({ x, y }) => {
    const fire = (type, tx, ty) => {
      const el = document.elementFromPoint(tx, ty) || document.body;
      const touchObj = new Touch({ identifier: 1, target: el, clientX: tx, clientY: ty, pageX: tx, pageY: ty, radiusX: 2, radiusY: 2, rotationAngle: 0, force: type === 'touchend' ? 0 : 1 });
      const event = new TouchEvent(type, {
        touches: type === 'touchend' ? [] : [touchObj],
        targetTouches: type === 'touchend' ? [] : [touchObj],
        changedTouches: [touchObj],
        bubbles: true,
        cancelable: true,
      });
      el.dispatchEvent(event);
    };
    fire('touchstart', x, y);
    await new Promise((r) => setTimeout(r, 650));
    fire('touchend', x, y);
  }, { x: box.x + box.width / 2, y: box.y + 20 });
  await page.waitForTimeout(700);
  const moveSheet = page.getByText('Mover card');
  if (!(await moveSheet.isVisible().catch(() => false))) {
    defect(flow3, { summary: 'Long press did not open move sheet', expected: 'Move sheet visible', actual: 'Move sheet hidden', id: created.id });
  } else {
    await page.getByRole('button', { name: /^DEV/ }).click();
    const movedDev = await waitForColumn(created.id, 'DEV', 15000);
    checkStatus(movedDev, 'PO', 'approved', flow3);
    checkStatus(movedDev, 'DEV', 'pending', flow3);
    result.flows[flow3].links.after = await shot(flow3, '02-after-dev.png');
    await page.getByRole('tab', { name: /^DEV / }).click();
    await page.waitForTimeout(700);
    result.flows[flow3].links.stage = await shot(flow3, '03-dev-tab.png');
    const devCard = page.getByRole('button', { name: new RegExp(created.id) }).first();
    const devBox = await devCard.boundingBox();
    if (devBox) {
      await page.evaluate(async ({ x, y }) => {
        const fire = (type, tx, ty) => {
          const el = document.elementFromPoint(tx, ty) || document.body;
          const touchObj = new Touch({ identifier: 2, target: el, clientX: tx, clientY: ty, pageX: tx, pageY: ty, radiusX: 2, radiusY: 2, rotationAngle: 0, force: type === 'touchend' ? 0 : 1 });
          const event = new TouchEvent(type, {
            touches: type === 'touchend' ? [] : [touchObj],
            targetTouches: type === 'touchend' ? [] : [touchObj],
            changedTouches: [touchObj],
            bubbles: true,
            cancelable: true,
          });
          el.dispatchEvent(event);
        };
        fire('touchstart', x, y);
        await new Promise((r) => setTimeout(r, 650));
        fire('touchend', x, y);
      }, { x: devBox.x + devBox.width / 2, y: devBox.y + 20 });
      await page.waitForTimeout(500);
      if (await moveSheet.isVisible().catch(() => false)) {
        await page.getByRole('button', { name: /^QA/ }).click();
        await waitForColumn(created.id, 'QA', 15000);
      }
    }
  }
  writeSummary(flow3, result.flows[flow3]);

  result.finalState = await getChange(created.id);
  fs.writeFileSync(path.join(root, 'kanban-manual-backlog-and-drag-drop-summary.json'), JSON.stringify(result, null, 2));
  console.log(JSON.stringify(result, null, 2));
}
