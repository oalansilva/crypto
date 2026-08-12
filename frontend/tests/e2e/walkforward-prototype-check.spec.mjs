import { chromium } from 'playwright';

const results = [];
function check(name, ok, detail = '') {
  results.push({ name, ok, detail });
  console.log(`${ok ? 'PASS' : 'FAIL'} | ${name}${detail ? ' | ' + detail : ''}`);
}

const browser = await chromium.launch();

async function runViewport(label, viewport) {
  console.log(`\n=== ${label} ===`);
  const page = await browser.newPage({ viewport });
  const errors = [];
  page.on('console', m => { if (m.type() === 'error') errors.push(m.text()); });
  page.on('pageerror', e => errors.push(String(e)));

  await page.goto('https://dev.criptofarol.com.br/prototypes/walk-forward-gate/', { waitUntil: 'networkidle' });

  // Expand scenario controls
  await page.locator('.prototype-scenarios summary').first().click();
  await page.locator('.scenario-actions button').first().waitFor({ state: 'visible' });

  // Default state: GO scenario
  check(`[${label}] verdict badge GO visible`, await page.getByTestId('verdict-badge').isVisible());
  check(`[${label}] NO-GO badge hidden`, await page.getByTestId('verdict-badge-nogo').isHidden());
  check(`[${label}] gono banner GO text`, (await page.locator('#gono-title').textContent()).includes('aprovada'));
  check(`[${label}] split chip 70/30`, (await page.getByTestId('split-chip').textContent()).includes('70'));
  if (viewport.width > 900) {
    check(`[${label}] OOS column present`, await page.getByTestId('oos-col-head').isVisible());
  } else {
    check(`[${label}] mobile holdout values present`, (await page.locator('.mobile-results').textContent()).includes('holdout'));
  }
  check(`[${label}] Calmar GO`, (await page.getByTestId('verdict-calmar').textContent()).includes('GO'));
  check(`[${label}] save button enabled (GO)`, !(await page.getByTestId('btn-save').isDisabled()));

  // Open save modal on GO
  await page.getByTestId('btn-save').click();
  check(`[${label}] modal opens`, await page.getByTestId('close-modal').isVisible());
  check(`[${label}] nogo block hidden on GO`, await page.locator('#nogo-block').isHidden());
  check(`[${label}] confirm save enabled on GO`, !(await page.getByTestId('btn-confirm-save').isDisabled()));
  await page.getByTestId('btn-cancel-save').click();
  check(`[${label}] modal closes`, await page.getByTestId('close-modal').isHidden());

  // NO-GO scenario
  await page.getByTestId('scenario-nogo').click();
  check(`[${label}] NO-GO badge visible`, await page.getByTestId('verdict-badge-nogo').isVisible());
  check(`[${label}] GO badge hidden`, await page.getByTestId('verdict-badge').isHidden());
  check(`[${label}] gono banner NO-GO text`, (await page.locator('#gono-title').textContent()).includes('reprovada'));
  if (viewport.width <= 900) {
    check(`[${label}] mobile Calmar NO-GO visible`, (await page.getByTestId('m-calmar-verdict').textContent()).includes('NO-GO'));
    check(`[${label}] mobile CAGR GO visible`, (await page.getByTestId('m-cagr-verdict').textContent()).includes('GO'));
  } else {
    check(`[${label}] Calmar NO-GO`, (await page.getByTestId('verdict-calmar').textContent()).includes('NO-GO'));
  }
  check(`[${label}] reasons list visible`, (await page.getByTestId('nogo-reasons').locator('li').count()) >= 1);

  check(`[${label}] NO-GO icon is X`, (await page.locator('#gono-icon').textContent()) === '\u2715');
  check(`[${label}] block hint visible on NO-GO`, await page.getByTestId('btn-block-hint').isVisible());
  await page.getByTestId('btn-save').click();
  check(`[${label}] nogo block visible in modal`, await page.locator('#nogo-block').isVisible());
  check(`[${label}] override row visible`, await page.locator('#override-row').isVisible());
  check(`[${label}] confirm save DISABLED (NO-GO, no override)`, await page.getByTestId('btn-confirm-save').isDisabled());
  await page.keyboard.press('Escape');
  check(`[${label}] Escape closes modal`, await page.getByTestId('close-modal').isHidden());
  check(`[${label}] focus restored after Escape`, (await page.evaluate(() => document.activeElement.id)) === 'btn-save-go');

  // Override flow (scenario button, admin)
  await page.getByTestId('scenario-override').click();
  check(`[${label}] override icon is X`, (await page.locator('#gono-icon').textContent()) === '\u2715');
  check(`[${label}] override button text`, (await page.getByTestId('btn-save').textContent()).includes('override'));
  await page.getByTestId('btn-save').click();
  check(`[${label}] override checkbox pre-checked (admin)`, await page.getByTestId('override-check').isChecked());
  check(`[${label}] confirm save enabled (admin override)`, !(await page.getByTestId('btn-confirm-save').isDisabled()));
  await page.getByTestId('btn-confirm-save').click();
  check(`[${label}] override saves with feedback`, (await page.locator('#modal-feedback').textContent()).includes('override'));
  await page.getByTestId('close-modal').click().catch(() => {});

  // Insufficient holdout scenario
  await page.getByTestId('scenario-insufficient').click();
  check(`[${label}] warn badge visible (insufficient)`, await page.getByTestId('verdict-badge-warn').isVisible());
  check(`[${label}] insufficient title`, (await page.locator('#gono-title').textContent()).includes('suficientes'));
  check(`[${label}] insufficient calmar dash`, (await page.getByTestId('verdict-calmar').textContent()).trim() === '\u2014');
  check(`[${label}] insufficient hint`, await page.getByTestId('btn-block-hint').isVisible());

  // Favorites revalidation
  await page.getByTestId('scenario-revalidate').click();
  check(`[${label}] favorites view visible`, await page.locator('#favorites-view').isVisible());
  check(`[${label}] revalidation banner visible`, await page.getByTestId('reval-banner').isVisible());
  check(`[${label}] reval window stated (90 dias)`, (await page.getByTestId('reval-banner').textContent()).includes('90 dias'));
  if (viewport.width > 900) {
    check(`[${label}] revalidate button per favorite`, await page.getByTestId('btn-revalidate').isVisible());
    await page.getByTestId('btn-revalidate').click();
    check(`[${label}] revalidate clicked state`, (await page.getByTestId('btn-revalidate').textContent()).includes('Revalidado'));
  }
  if (viewport.width <= 900) {
    check(`[${label}] mobile reval NO-GO badge`, (await page.getByTestId('reval-badge-m').textContent()).includes('NO-GO'));
  } else {
    check(`[${label}] reval NO-GO badge`, (await page.getByTestId('reval-badge').textContent()).includes('NO-GO'));
  }
  await page.getByTestId('btn-view-report').click();
  check(`[${label}] report opens (mock)`, (await page.locator('#reval-banner').textContent()).includes('Relatório aberto'));

  // Split config (back to results view first)
  const backBtn = page.locator('#nav-results:visible, #tab-results:visible').first();
  await backBtn.click();
  const details = page.locator('#results-view details').first();
  if ((await details.getAttribute('open')) === null) {
    await details.locator('summary').click();
  }
  await page.getByTestId('scenario-go').click();
  await page.getByTestId('btn-split-config').click();
  check(`[${label}] split chip updated to 60/40`, (await page.getByTestId('split-chip').textContent()).includes('60'));

  check(`[${label}] no console/page errors`, errors.length === 0, errors.slice(0, 3).join(' || '));
  await page.close();
}

await runViewport('desktop 1440x900', { width: 1440, height: 900 });
await runViewport('mobile 390x844', { width: 390, height: 844 });

await browser.close();
const failed = results.filter(r => !r.ok);
console.log(`\nTOTAL: ${results.length} checks, ${failed.length} failed`);
process.exit(failed.length ? 1 : 0);
