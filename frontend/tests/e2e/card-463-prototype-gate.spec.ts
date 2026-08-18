import { test, expect } from '@playwright/test';
import fs from 'node:fs';
import path from 'node:path';

const PROTOTYPE_PATH = '/prototypes/card-463-saldo-usdt-compra/';
const prototypeHtml = path.join(process.cwd(), 'public/prototypes/card-463-saldo-usdt-compra/index.html');

test.beforeAll(() => {
  if (!fs.existsSync(prototypeHtml)) {
    throw new Error(`Prototype missing in checkout: ${prototypeHtml}`);
  }
});

test.beforeEach(({ baseURL }) => {
  expect(baseURL || '', 'prototype e2e must use Playwright preview, not live DEV').not.toContain(
    'dev.criptofarol.com.br',
  );
});

async function openScenarios(page: import('@playwright/test').Page) {
  const dialog = page.getByTestId('trade-dialog');
  if (await dialog.evaluate((el) => el.classList.contains('open')).catch(() => false)) {
    await page.getByTestId('close-trade').click();
  }
  const details = page.locator('details.prototype-scenarios').filter({ visible: true }).first();
  if (!(await details.evaluate((el) => el.open))) {
    await details.locator('summary').click();
  }
}

test.describe('Card 463 prototype gate (revalidado)', () => {
  test('desktop: saldo real visível e estados', async ({ page }) => {
    await page.goto(PROTOTYPE_PATH, { waitUntil: 'load' });
    await expect(page.locator('h1')).toHaveText('Monitor de ativos');
    const consoleErrors: string[] = [];
    page.on('console', (m) => { if (m.type() === 'error') consoleErrors.push(m.text()); });
    page.on('pageerror', (e) => consoleErrors.push(String(e)));

    await page.getByTestId('open-trade').click();
    await expect(page.getByTestId('trade-dialog')).toHaveClass(/open/);
    await expect(page.getByTestId('quote-balance')).toHaveText('100,65 USDT');
    await expect(page.getByTestId('quote-balance')).toHaveText('100,65 USDT');

    await openScenarios(page);
    await page.getByTestId('scenario-loading').click();
    await expect(page.getByTestId('quote-balance')).toHaveText('carregando…');

    await openScenarios(page);
    await page.getByTestId('scenario-unavailable').click();
    await expect(page.getByTestId('quote-balance')).toHaveText('indisponível');
    await expect(page.locator('#buy-error')).toContainText('Não foi possível consultar o saldo');

    await openScenarios(page);
    await page.getByTestId('scenario-insufficient').click();
    await expect(page.getByTestId('quote-balance')).toHaveText('0,65 USDT');
    await expect(page.locator('#buy-error')).toContainText('Simple Earn');
    await expect(page.locator('#buy-error')).toContainText('0,65 USDT disponíveis');

    await openScenarios(page);
    await page.getByTestId('scenario-wallet').click();
    await expect(page.getByTestId('usdt-row')).toBeVisible();
    await expect(page.getByTestId('earn-note')).toContainText('100,00 em Simple Earn');
    await page.locator('#nav-monitor').click();
    await expect(page.locator('h1')).toHaveText('Monitor de ativos');

    expect(consoleErrors).toEqual([]);
  });

  test('mobile 390x844: modal, carteira e monitor sem overflow', async ({ page }) => {
    await page.setViewportSize({ width: 390, height: 844 });
    await page.goto(PROTOTYPE_PATH, { waitUntil: 'load' });
    const consoleErrors: string[] = [];
    page.on('console', (m) => { if (m.type() === 'error') consoleErrors.push(m.text()); });
    page.on('pageerror', (e) => consoleErrors.push(String(e)));

    await page.getByTestId('open-trade-mobile').click();
    await expect(page.getByTestId('quote-balance')).toHaveText('100,65 USDT');
    let overflow = await page.evaluate(() => document.documentElement.scrollWidth > document.documentElement.clientWidth);
    expect(overflow).toBe(false);

    await openScenarios(page);
    await page.getByTestId('scenario-wallet-m').click();
    await expect(page.getByTestId('usdt-mobile-row')).toBeVisible();
    overflow = await page.evaluate(() => document.documentElement.scrollWidth > document.documentElement.clientWidth);
    expect(overflow).toBe(false);

    expect(consoleErrors).toEqual([]);
  });
});
