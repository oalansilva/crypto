import { chromium } from 'playwright';
import fs from 'node:fs/promises';
import path from 'node:path';

const BASE_URL = 'http://127.0.0.1:5173';
const API_BASE = 'http://127.0.0.1:8003/api';
const FLOW = 'kanban-manual-backlog-and-drag-drop-revalidation';
const outDir = path.resolve('qa_artifacts/playwright', FLOW);
await fs.mkdir(outDir, { recursive: true });

const state = {
  verdict: 'BLOCKED',
  summary: [],
  evidence: [],
  nextStep: '',
};

async function saveJson(name, data) {
  await fs.writeFile(path.join(outDir, name), JSON.stringify(data, null, 2));
}

async function fetchBoard() {
  const res = await fetch(`${API_BASE}/workflow/kanban/changes?project_slug=crypto`);
  if (!res.ok) throw new Error(`Board fetch failed: ${res.status}`);
  return res.json();
}

async function updateChange(changeId, status) {
  const res = await fetch(`${API_BASE}/workflow/projects/crypto/changes/${encodeURIComponent(changeId)}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ status }),
  });
  if (!res.ok) throw new Error(`Update ${changeId} -> ${status} failed: ${res.status} ${await res.text()}`);
  return res.json();
}

async function getItem(changeId) {
  const board = await fetchBoard();
  return board.items.find((it) => it.id === changeId);
}

const sourceId = 'orden-execu-o-dos-cards';
const targetId = 'kanban-manual-backlog-and-drag-drop';
let originalSource;
let originalTarget;

const browser = await chromium.launch({ headless: true });
const context = await browser.newContext({ viewport: { width: 1440, height: 900 } });
const page = await context.newPage();

try {
  originalSource = await getItem(sourceId);
  originalTarget = await getItem(targetId);
  await saveJson('00-initial-board.json', { originalSource, originalTarget });

  if (!originalSource || !originalTarget) throw new Error('Required kanban cards not found in runtime board');
  if (originalSource.column !== 'PO') throw new Error(`Expected ${sourceId} to start in PO, got ${originalSource.column}`);

  // ensure DEV has a real target card to drop on top of
  await updateChange(targetId, 'DEV');
  const targetInDev = await getItem(targetId);
  if (targetInDev?.column !== 'DEV') throw new Error(`Could not place ${targetId} in DEV before test`);

  await page.goto(`${BASE_URL}/kanban`, { waitUntil: 'networkidle' });
  await page.screenshot({ path: path.join(outDir, '01-desktop-before.png'), fullPage: true });

  const sourceCard = page.getByRole('button', { name: new RegExp(`Open details for ${sourceId}`) });
  const targetCard = page.getByRole('button', { name: new RegExp(`Open details for ${targetId}`) });
  await sourceCard.waitFor({ state: 'visible' });
  await targetCard.waitFor({ state: 'visible' });

  await sourceCard.evaluate((element, changeId) => {
    const dt = new DataTransfer();
    dt.setData('application/x-kanban-change-id', changeId);
    dt.setData('text/plain', changeId);
    window.__kanbanDt = dt;
    element.dispatchEvent(new DragEvent('dragstart', { bubbles: true, cancelable: true, dataTransfer: dt }));
  }, sourceId);

  await targetCard.evaluate((element) => {
    const dt = window.__kanbanDt;
    element.dispatchEvent(new DragEvent('dragenter', { bubbles: true, cancelable: true, dataTransfer: dt }));
    element.dispatchEvent(new DragEvent('dragover', { bubbles: true, cancelable: true, dataTransfer: dt }));
    element.dispatchEvent(new DragEvent('drop', { bubbles: true, cancelable: true, dataTransfer: dt }));
  });

  await page.waitForTimeout(1500);
  await page.waitForFunction(async (sid) => {
    const res = await fetch(`/api/workflow/kanban/changes?project_slug=crypto`);
    const data = await res.json();
    return data.items?.some((it) => it.id === sid && it.column === 'DEV');
  }, sourceId, { timeout: 15000 });

  await page.screenshot({ path: path.join(outDir, '02-desktop-after-drop.png'), fullPage: true });

  await page.reload({ waitUntil: 'networkidle' });
  await page.screenshot({ path: path.join(outDir, '03-desktop-after-refresh.png'), fullPage: true });

  const sourceAfterDesktop = await getItem(sourceId);
  if (sourceAfterDesktop?.column !== 'DEV') throw new Error(`Desktop move did not persist after refresh; got ${sourceAfterDesktop?.column}`);

  // mobile long-press + move sheet
  await page.setViewportSize({ width: 390, height: 844 });
  await page.reload({ waitUntil: 'networkidle' });
  await page.getByRole('tab', { name: /DEV/i }).click();
  const mobileCard = page.getByRole('button', { name: new RegExp(`Open details for ${sourceId}`) });
  await mobileCard.waitFor({ state: 'visible' });
  const box = await mobileCard.boundingBox();
  if (!box) throw new Error('Could not get mobile card bounding box');
  const touch = { identifier: 1, clientX: box.x + box.width / 2, clientY: box.y + Math.min(40, box.height / 2) };
  await mobileCard.dispatchEvent('touchstart', { touches: [touch], changedTouches: [touch] });
  await page.waitForTimeout(650);
  await mobileCard.dispatchEvent('touchend', { touches: [], changedTouches: [touch] });

  await page.getByText('Mover card').waitFor({ state: 'visible', timeout: 10000 });
  await page.screenshot({ path: path.join(outDir, '04-mobile-move-sheet.png'), fullPage: true });
  await page.getByRole('button', { name: /PO/ }).click();
  await page.waitForTimeout(1500);
  await page.screenshot({ path: path.join(outDir, '05-mobile-after-move.png'), fullPage: true });

  const sourceAfterMobile = await getItem(sourceId);
  if (sourceAfterMobile?.column !== 'PO') throw new Error(`Mobile move did not persist immediately; got ${sourceAfterMobile?.column}`);

  await page.reload({ waitUntil: 'networkidle' });
  await page.getByRole('tab', { name: /PO/i }).click();
  await page.getByRole('button', { name: new RegExp(`Open details for ${sourceId}`) }).waitFor({ state: 'visible', timeout: 10000 });
  await page.screenshot({ path: path.join(outDir, '06-mobile-after-refresh.png'), fullPage: true });

  const sourceAfterMobileRefresh = await getItem(sourceId);
  if (sourceAfterMobileRefresh?.column !== 'PO') throw new Error(`Mobile move did not persist after refresh; got ${sourceAfterMobileRefresh?.column}`);

  state.verdict = 'PASS';
  state.summary.push('Desktop: card moved from PO to DEV even when dropped on top of another DEV card, and the change persisted after refresh.');
  state.summary.push('Mobile: long-press opened the move sheet, moving the card back to PO succeeded, and the change persisted after refresh.');
  state.nextStep = 'No QA action needed; hand off for normal merge/homologation flow.';
} catch (error) {
  state.verdict = 'FAIL';
  state.summary.push(error instanceof Error ? error.message : String(error));
  state.nextStep = 'DEV should inspect the failing interaction/persistence path using the attached screenshots and runtime state.';
  try {
    await page.screenshot({ path: path.join(outDir, '99-failure.png'), fullPage: true });
  } catch {}
} finally {
  // cleanup / restore original runtime state
  try {
    if (originalSource) await updateChange(sourceId, originalSource.column);
  } catch {}
  try {
    if (originalTarget) await updateChange(targetId, originalTarget.column);
  } catch {}
  const finalSource = await getItem(sourceId).catch(() => null);
  const finalTarget = await getItem(targetId).catch(() => null);
  await saveJson('07-final-board.json', { finalSource, finalTarget, state });
  await browser.close();
}

const files = await fs.readdir(outDir);
state.evidence = files
  .filter((name) => /\.(png|json)$/i.test(name))
  .sort()
  .map((name) => ({
    file: name,
    path: `qa_artifacts/playwright/${FLOW}/${name}`,
    url: `http://72.60.150.140:5173/qa-artifacts/playwright/${FLOW}/${name}`,
  }));
await saveJson('summary.json', state);
console.log(JSON.stringify(state, null, 2));
