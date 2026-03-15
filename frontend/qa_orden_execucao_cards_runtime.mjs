import { chromium } from 'playwright';
import fs from 'node:fs/promises';
import path from 'node:path';
import { execFileSync } from 'node:child_process';

const REPO_ROOT = path.resolve('..');
const BASE_URL = 'http://127.0.0.1:5173';
const API_BASE = 'http://127.0.0.1:8003/api';
const FLOW = 'orden-execu-o-dos-cards-runtime';
const outDir = path.join(REPO_ROOT, 'qa_artifacts/playwright', FLOW);
await fs.mkdir(outDir, { recursive: true });

const SOURCE_ID = 'orden-execu-o-dos-cards';
const HELPER_ID = 'numera-o-cards';
const PSQL = ['-h', '127.0.0.1', '-U', 'workflow_app', '-d', 'workflow'];
const env = { ...process.env, PGPASSWORD: 'workflow_app_change_me' };

function psql(sql) {
  return execFileSync('psql', [...PSQL, '-t', '-A', '-c', sql], { encoding: 'utf8', env }).trim();
}

async function saveJson(name, data) {
  await fs.writeFile(path.join(outDir, name), JSON.stringify(data, null, 2));
}

async function fetchBoard() {
  const res = await fetch(`${API_BASE}/workflow/kanban/changes?project_slug=crypto`);
  if (!res.ok) throw new Error(`board fetch failed: ${res.status}`);
  return res.json();
}

async function qaOrder() {
  const board = await fetchBoard();
  return board.items.filter((it) => it.column === 'QA').map((it) => it.id);
}

function seedHelperToQa() {
  const original = JSON.parse(psql(`select row_to_json(t)::text from (select change_id, status from wf_changes where change_id = '${HELPER_ID}') t;`));
  psql(`update wf_changes set status = 'QA', updated_at = now() where change_id = '${HELPER_ID}';`);
  return original;
}

function restoreHelper(original) {
  psql(`update wf_changes set status = '${original.status}', updated_at = now() where change_id = '${original.change_id}';`);
}

const state = { verdict: 'BLOCKED', summary: [], evidence: [], nextStep: '' };
const browser = await chromium.launch({ headless: true });
const context = await browser.newContext({ viewport: { width: 1440, height: 900 } });
const page = await context.newPage();
let originalHelper;

try {
  originalHelper = seedHelperToQa();
  await page.goto(`${BASE_URL}/kanban`, { waitUntil: 'networkidle' });
  await page.screenshot({ path: path.join(outDir, '01-before-desktop.png'), fullPage: true });

  const initialOrder = await qaOrder();
  await saveJson('00-initial-order.json', { initialOrder });

  const sourceCard = page.getByRole('button', { name: new RegExp(`Open details for ${SOURCE_ID}`) });
  const helperCard = page.getByRole('button', { name: new RegExp(`Open details for ${HELPER_ID}`) });
  await sourceCard.waitFor({ state: 'visible' });
  await helperCard.waitFor({ state: 'visible' });

  const boardUp = sourceCard.locator('button').filter({ hasText: 'Move up' }).first();
  const boardDown = sourceCard.locator('button').filter({ hasText: 'Move down' }).first();
  const boardStates = { upDisabled: await boardUp.isDisabled(), downDisabled: await boardDown.isDisabled() };
  await saveJson('01-board-button-states.json', boardStates);

  let afterBoardAction = initialOrder;
  let boardAction = 'none';
  if (!boardStates.downDisabled) {
    boardAction = 'down';
    await boardDown.click();
    await page.waitForTimeout(1200);
    afterBoardAction = await qaOrder();
  } else if (!boardStates.upDisabled) {
    boardAction = 'up';
    await boardUp.click();
    await page.waitForTimeout(1200);
    afterBoardAction = await qaOrder();
  }
  await page.screenshot({ path: path.join(outDir, '02-after-board-action.png'), fullPage: true });

  await sourceCard.click();
  const drawerUp = page.getByRole('button', { name: 'Move up' }).last();
  const drawerDown = page.getByRole('button', { name: 'Move down' }).last();
  await drawerUp.waitFor({ state: 'visible' });
  const drawerStates = { upDisabled: await drawerUp.isDisabled(), downDisabled: await drawerDown.isDisabled() };
  await saveJson('03-drawer-button-states.json', drawerStates);

  let afterDrawerAction = afterBoardAction;
  let drawerAction = 'none';
  if (!drawerStates.upDisabled) {
    drawerAction = 'up';
    await drawerUp.click();
    await page.waitForTimeout(1200);
    afterDrawerAction = await qaOrder();
  } else if (!drawerStates.downDisabled) {
    drawerAction = 'down';
    await drawerDown.click();
    await page.waitForTimeout(1200);
    afterDrawerAction = await qaOrder();
  }
  await page.screenshot({ path: path.join(outDir, '04-after-drawer-action.png'), fullPage: true });
  await page.reload({ waitUntil: 'networkidle' });
  const afterReload = await qaOrder();
  await page.screenshot({ path: path.join(outDir, '04-after-reload.png'), fullPage: true });

  await saveJson('05-orders.json', { initialOrder, boardAction, afterBoardAction, drawerAction, afterDrawerAction, afterReload });

  const changedAfterBoard = JSON.stringify(afterBoardAction) !== JSON.stringify(initialOrder);
  const changedAfterDrawer = JSON.stringify(afterDrawerAction) !== JSON.stringify(afterBoardAction);
  const sourceStillQa = (await fetchBoard()).items.find((it) => it.id === SOURCE_ID)?.column === 'QA';
  const helperStillQa = (await fetchBoard()).items.find((it) => it.id === HELPER_ID)?.column === 'QA';
  await saveJson('06-columns.json', { sourceStillQa, helperStillQa });

  if (!changedAfterBoard) {
    state.verdict = 'FAIL';
    state.summary.push('Move down no board não alterou a ordem da coluna QA em runtime real.');
    state.summary.push('A change permaneceu em QA; não houve mudança de coluna/gates.');
    state.nextStep = 'DEV precisa corrigir a persistência/ordenação intra-coluna no runtime do Kanban e devolver para QA.';
  } else if (!changedAfterDrawer) {
    state.verdict = 'FAIL';
    state.summary.push('Move up no drawer não alterou a ordem da coluna QA em runtime real.');
    state.summary.push('A change permaneceu em QA; não houve mudança de coluna/gates.');
    state.nextStep = 'DEV precisa corrigir a ação de reorder no drawer e devolver para QA.';
  } else if (!sourceStillQa || !helperStillQa) {
    state.verdict = 'FAIL';
    state.summary.push('O reorder afetou coluna/gates, o que viola o escopo esperado.');
    state.nextStep = 'DEV precisa restringir o reorder para intra-coluna e devolver para QA.';
  } else {
    state.verdict = 'PASS';
    state.summary.push('Move up/down atualizou a ordem da coluna QA no runtime real.');
    state.summary.push('Refresh preservou a ordem e nenhuma coluna/gate mudou.');
    state.nextStep = 'Promover para Alan homologation.';
  }
} catch (error) {
  state.verdict = 'FAIL';
  state.summary.push(error instanceof Error ? error.message : String(error));
  state.nextStep = 'DEV precisa investigar o fluxo com a evidência anexada e devolver para QA.';
  try { await page.screenshot({ path: path.join(outDir, '99-failure.png'), fullPage: true }); } catch {}
} finally {
  try { if (originalHelper) restoreHelper(originalHelper); } catch {}
  await browser.close();
  const files = (await fs.readdir(outDir)).filter((n) => /\.(png|json)$/i.test(n)).sort();
  state.evidence = files.map((name) => ({
    file: name,
    path: `qa_artifacts/playwright/${FLOW}/${name}`,
    url: `http://72.60.150.140:5173/qa-artifacts/playwright/${FLOW}/${name}`,
  }));
  await saveJson('summary.json', state);
  console.log(JSON.stringify(state, null, 2));
}
