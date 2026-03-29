import { chromium } from '@playwright/test';
import fs from 'node:fs/promises';
import path from 'node:path';

const FLOW = 'harden-workflow-publish-gates-ui-simplification';
const OUT = path.resolve('/root/.openclaw/workspace/crypto/qa_artifacts/playwright', FLOW);
const BASE_URL = 'http://72.60.150.140:5173';
const API_BASE = 'http://72.60.150.140:8003/api';
const CHANGE_ID = 'harden-workflow-publish-gates';
const CHANGE_TITLE = 'harden workflow publish gates';

await fs.mkdir(OUT, { recursive: true });

const browser = await chromium.launch({ headless: true });
const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });

const artifact = (name) => ({
  path: path.join(OUT, name),
  url: `${BASE_URL}/qa-artifacts/playwright/${FLOW}/${name}`,
});

const writeJson = async (name, data) => {
  const target = artifact(name);
  await fs.writeFile(target.path, JSON.stringify(data, null, 2));
  return target;
};

const shot = async (name, locator = page) => {
  const target = artifact(name);
  await locator.screenshot({ path: target.path });
  return target;
};

const checks = [];
let passed = false;
let commentBody = '';

try {
  const [boardRes, changeRes, commentsRes] = await Promise.all([
    fetch(`${API_BASE}/workflow/kanban/changes?project_slug=crypto`).then((r) => r.json()),
    fetch(`${API_BASE}/workflow/projects/crypto/changes/${CHANGE_ID}`).then((r) => r.json()),
    fetch(`${API_BASE}/workflow/kanban/changes/${CHANGE_ID}/comments?project_slug=crypto`).then((r) => r.json()),
  ]);

  const boardItem = boardRes.items.find((item) => item.id === CHANGE_ID);
  if (!boardItem) throw new Error(`Change ${CHANGE_ID} not found on live board`);

  await writeJson('01-board-item.json', boardItem);
  await writeJson('02-change.json', changeRes);
  await writeJson('03-comments-before.json', commentsRes);

  await page.goto(`${BASE_URL}/kanban`, { waitUntil: 'networkidle' });
  const card = page.getByRole('button', { name: new RegExp(`Open details for ${CHANGE_ID}`, 'i') });
  await card.scrollIntoViewIfNeeded();
  await card.click();

  const drawer = page.locator('aside').filter({ hasText: CHANGE_TITLE }).first();
  await drawer.waitFor({ state: 'visible' });

  const boardShot = await shot('04-board.png');
  const drawerShot = await shot('05-drawer.png', drawer);

  const uiData = await page.evaluate(() => {
    const text = document.body.innerText;
    const aside = document.querySelector('aside');
    return {
      bodyText: text,
      drawerText: aside?.innerText || '',
      stageAtualCount: (text.match(/Stage atual/gi) || []).length,
      runtimeStageCount: (text.match(/Runtime stage/gi) || []).length,
      qaFunctionalCount: (text.match(/QA functional/gi) || []).length,
      publishCount: (text.match(/Publish/gi) || []).length,
      readyForHomologationCount: (text.match(/Ready for homologation/gi) || []).length,
      alanHomologationCount: (text.match(/Homologation/gi) || []).length,
      currentStageCount: (text.match(/Current stage/gi) || []).length,
    };
  });
  const uiArtifact = await writeJson('06-ui-text-checks.json', uiData);

  const cardText = await card.innerText();
  const drawerText = await drawer.innerText();

  const cardHasRuntimeStage = /Runtime stage/i.test(cardText);
  const cardHasQaFunctional = /QA functional/i.test(cardText);
  const cardHasPublish = /Publish/i.test(cardText);
  const cardHasReady = /Ready for homologation/i.test(cardText);
  const drawerHasRuntimeStage = /Runtime stage/i.test(drawerText) || /Stage atual/i.test(drawerText);
  const drawerHasQaFunctional = /QA functional/i.test(drawerText);
  const drawerHasPublish = /Publish/i.test(drawerText);
  const drawerHasReady = /Ready for homologation/i.test(drawerText);

  checks.push(
    { name: 'card does not show Runtime stage / Stage atual', ok: !cardHasRuntimeStage },
    { name: 'card does not show QA functional', ok: !cardHasQaFunctional },
    { name: 'card shows Publish', ok: cardHasPublish },
    { name: 'card shows Ready for homologation', ok: cardHasReady },
    { name: 'drawer does not show Runtime stage / Stage atual', ok: !drawerHasRuntimeStage },
    { name: 'drawer does not show QA functional', ok: !drawerHasQaFunctional },
    { name: 'drawer shows Publish', ok: drawerHasPublish },
    { name: 'drawer shows Ready for homologation', ok: drawerHasReady },
    { name: 'runtime change status remains Homologation', ok: changeRes.status === 'Homologation' },
    { name: 'board column remains Homologation', ok: boardItem.column === 'Homologation' },
  );

  passed = checks.every((c) => c.ok);

  const summary = {
    flow: FLOW,
    changeId: CHANGE_ID,
    passed,
    checks,
    runtime: {
      status: changeRes.status,
      boardColumn: boardItem.column,
      boardStatus: boardItem.status,
    },
    artifacts: {
      boardItem: `${BASE_URL}/qa-artifacts/playwright/${FLOW}/01-board-item.json`,
      change: `${BASE_URL}/qa-artifacts/playwright/${FLOW}/02-change.json`,
      commentsBefore: `${BASE_URL}/qa-artifacts/playwright/${FLOW}/03-comments-before.json`,
      board: boardShot.url,
      drawer: drawerShot.url,
      uiChecks: uiArtifact.url,
    },
  };

  if (passed) {
    commentBody = `feito: revalidei no live a simplificação visual de \`${CHANGE_ID}\` no /kanban; a UI padrão não mostra mais \`Runtime stage\`/\`Stage atual\` nem \`QA functional\`, e mantém visíveis só os auxiliares \`Publish\` e \`Ready for homologation\`. bloqueio: nenhum. próximo passo: seguir com Homologation; coluna/runtime foram preservados sem nova movimentação. Evidências: board ${boardShot.url} | drawer ${drawerShot.url} | checks ${uiArtifact.url} | runtime ${summary.artifacts.change}`;
    const postRes = await fetch(`${API_BASE}/workflow/kanban/changes/${CHANGE_ID}/comments?project_slug=crypto`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ author: 'QA', body: commentBody }),
    }).then((r) => r.json());
    summary.commentPosted = postRes;
    summary.commentBody = commentBody;
    await writeJson('07-comment-post-response.json', postRes);
  } else {
    commentBody = `bloqueio: a simplificação visual de \`${CHANGE_ID}\` falhou na revalidação live do /kanban. checks com falha: ${checks.filter((c) => !c.ok).map((c) => c.name).join('; ')}. próximo passo: ajustar a UI live para esconder \`Runtime stage\`/\`Stage atual\` e \`QA functional\`, mantendo \`Publish\` e \`Ready for homologation\` visíveis. Evidências: board ${boardShot.url} | drawer ${drawerShot.url} | checks ${uiArtifact.url} | runtime ${summary.artifacts.change}`;
    const postRes = await fetch(`${API_BASE}/workflow/kanban/changes/${CHANGE_ID}/comments?project_slug=crypto`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ author: 'QA', body: commentBody }),
    }).then((r) => r.json());
    summary.commentPosted = postRes;
    summary.commentBody = commentBody;
    await writeJson('07-comment-post-response.json', postRes);
  }

  await writeJson('08-summary.json', summary);
  console.log(JSON.stringify(summary, null, 2));
} catch (error) {
  const failureShot = await shot('99-failure.png').catch(() => null);
  const summary = {
    flow: FLOW,
    changeId: CHANGE_ID,
    passed: false,
    error: String(error?.stack || error),
    failureScreenshot: failureShot?.url || null,
    checks,
  };
  await writeJson('08-summary.json', summary);
  console.log(JSON.stringify(summary, null, 2));
  process.exitCode = 1;
} finally {
  await page.close().catch(() => {});
  await browser.close().catch(() => {});
}
