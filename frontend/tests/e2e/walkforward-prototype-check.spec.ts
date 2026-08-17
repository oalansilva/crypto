import { test, expect, type Page } from '@playwright/test'
import fs from 'node:fs'
import path from 'node:path'

const prototypeHtml = path.join(process.cwd(), 'public/prototypes/walk-forward-gate/index.html')

test.describe.configure({ timeout: 120_000 })

test.beforeAll(() => {
  if (!fs.existsSync(prototypeHtml)) {
    throw new Error(`Prototype missing in checkout: ${prototypeHtml}`)
  }
})

test.beforeEach(({ baseURL }) => {
  expect(baseURL || '', 'prototype e2e must use Playwright preview, not live DEV').not.toContain(
    'dev.criptofarol.com.br',
  )
})

async function openScenarios(page: Page) {
  await page.locator('.prototype-scenarios summary').first().click()
  await page.locator('.scenario-actions button').first().waitFor({ state: 'visible' })
}

async function runViewport(page: Page, viewport: { width: number; height: number }) {
  const errors: string[] = []
  page.on('console', (m) => {
    if (m.type() === 'error') errors.push(m.text())
  })
  page.on('pageerror', (e) => errors.push(String(e)))

  await page.setViewportSize(viewport)
  await page.goto('/prototypes/walk-forward-gate/', { waitUntil: 'load' })
  await openScenarios(page)

  await expect(page.getByTestId('verdict-badge')).toBeVisible()
  await expect(page.getByTestId('verdict-badge-nogo')).toBeHidden()
  await expect(page.locator('#gono-title')).toContainText('aprovada')
  await expect(page.getByTestId('split-chip')).toContainText('70')
  if (viewport.width > 900) {
    await expect(page.getByTestId('oos-col-head')).toBeVisible()
  } else {
    await expect(page.locator('.mobile-results')).toContainText('holdout')
  }
  await expect(page.getByTestId('verdict-calmar')).toContainText('GO')
  await expect(page.getByTestId('btn-save')).toBeEnabled()

  await page.getByTestId('btn-save').click()
  await expect(page.getByTestId('close-modal')).toBeVisible()
  await expect(page.locator('#nogo-block')).toBeHidden()
  await expect(page.getByTestId('btn-confirm-save')).toBeEnabled()
  await page.getByTestId('btn-cancel-save').click()
  await expect(page.getByTestId('close-modal')).toBeHidden()

  await page.getByTestId('scenario-nogo').click()
  await expect(page.getByTestId('verdict-badge-nogo')).toBeVisible()
  await expect(page.getByTestId('verdict-badge')).toBeHidden()
  await expect(page.locator('#gono-title')).toContainText('reprovada')
  if (viewport.width <= 900) {
    await expect(page.getByTestId('m-calmar-verdict')).toContainText('NO-GO')
    await expect(page.getByTestId('m-cagr-verdict')).toContainText('GO')
  } else {
    await expect(page.getByTestId('verdict-calmar')).toContainText('NO-GO')
  }
  expect(await page.getByTestId('nogo-reasons').locator('li').count()).toBeGreaterThanOrEqual(1)
  await expect(page.locator('#gono-icon')).toHaveText('✕')
  await expect(page.getByTestId('btn-block-hint')).toBeVisible()
  await page.getByTestId('btn-save').click()
  await expect(page.locator('#nogo-block')).toBeVisible()
  await expect(page.locator('#override-row')).toBeVisible()
  await expect(page.getByTestId('btn-confirm-save')).toBeDisabled()
  await page.keyboard.press('Escape')
  await expect(page.getByTestId('close-modal')).toBeHidden()
  expect(await page.evaluate(() => document.activeElement?.id)).toBe('btn-save-go')

  await page.getByTestId('scenario-override').click()
  await expect(page.locator('#gono-icon')).toHaveText('✕')
  await expect(page.getByTestId('btn-save')).toContainText('override')
  await page.getByTestId('btn-save').click()
  await expect(page.getByTestId('override-check')).toBeChecked()
  await expect(page.getByTestId('btn-confirm-save')).toBeEnabled()
  await page.getByTestId('btn-confirm-save').click()
  await expect(page.locator('#modal-feedback')).toContainText('override')
  await page.getByTestId('close-modal').click({ timeout: 2_000 }).catch(() => {})

  await page.getByTestId('scenario-insufficient').click()
  await expect(page.getByTestId('verdict-badge-warn')).toBeVisible()
  await expect(page.locator('#gono-title')).toContainText('suficientes')
  await expect(page.getByTestId('verdict-calmar')).toHaveText('—')
  await expect(page.getByTestId('btn-block-hint')).toBeVisible()

  await page.getByTestId('scenario-revalidate').click()
  await expect(page.locator('#favorites-view')).toBeVisible()
  await expect(page.getByTestId('reval-banner')).toBeVisible()
  await expect(page.getByTestId('reval-banner')).toContainText('90 dias')
  if (viewport.width > 900) {
    await expect(page.getByTestId('btn-revalidate')).toBeVisible()
    await page.getByTestId('btn-revalidate').click()
    await expect(page.getByTestId('btn-revalidate')).toContainText('Revalidado')
    await expect(page.getByTestId('reval-badge')).toContainText('NO-GO')
  } else {
    await expect(page.getByTestId('reval-badge-m')).toContainText('NO-GO')
  }
  await page.getByTestId('btn-view-report').click()
  await expect(page.locator('#reval-banner')).toContainText('Relatório aberto')

  const backBtn = page.locator('#nav-results:visible, #tab-results:visible').first()
  await backBtn.click()
  const details = page.locator('#results-view details').first()
  if ((await details.getAttribute('open')) === null) {
    await details.locator('summary').click()
  }
  await page.getByTestId('scenario-go').click()
  await page.getByTestId('btn-split-config').click()
  await expect(page.getByTestId('split-chip')).toContainText('60')
  expect(errors, errors.slice(0, 3).join(' || ')).toEqual([])
}

test('walk-forward prototype desktop uses local preview', async ({ page }) => {
  await runViewport(page, { width: 1440, height: 900 })
})

test('walk-forward prototype mobile uses local preview', async ({ page }) => {
  await runViewport(page, { width: 390, height: 844 })
})
