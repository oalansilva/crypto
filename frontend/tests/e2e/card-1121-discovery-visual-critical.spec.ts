/**
 * Card #1121 — visual da Descoberta multiclasse (1440 e 390, tema escuro, API simulada).
 *
 * Regiões do delta do protótipo aprovado: Preflight por classe, quadro "Por ativo", Decidir com o filtro
 * Classe e o bloco do candidato, e o modal de promoção de NVDA. Tolerância 0,05 como no visual da
 * Descoberta (fallback de fonte no CI); quebra real de layout passa muito disso.
 */
import { expect, test, type Page } from '@playwright/test'
import {
  ASSETS_COLLECTING,
  ASSETS_DONE,
  SWEEP_ID,
  buildMixedDraft,
  installDiscoveryMulticlassMocks,
} from './helpers/discoveryMulticlassMock'

const SHOT = { animations: 'disabled' as const, caret: 'hide' as const, maxDiffPixelRatio: 0.05 }

async function noHorizontalScroll(page: Page) {
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= document.documentElement.clientWidth)).toBe(true)
}

test('card 1121 — Preflight misto e "Por ativo"', async ({ page }) => {
  await installDiscoveryMulticlassMocks(page, { assets: ASSETS_COLLECTING })
  await page.goto('/combo/discovery')
  await buildMixedDraft(page)
  await expect(page.getByTestId('preflight-collect')).toBeVisible()
  await noHorizontalScroll(page)
  await expect(page.getByRole('complementary', { name: 'Preflight da varredura' })).toHaveScreenshot('card-1121-preflight.png', SHOT)

  await page.getByTestId('start-sweep').click()
  const board = page.getByTestId('sweep-assets')
  await expect(board.locator('li').first()).toContainText('Coletando histórico · 1d · página 3 de 6')
  await noHorizontalScroll(page)
  await expect(board).toHaveScreenshot('card-1121-por-ativo.png', SHOT)
})

test('card 1121 — Decidir multiclasse e modal de promoção', async ({ page }) => {
  await installDiscoveryMulticlassMocks(page, {
    sweepState: 'completed',
    assets: ASSETS_DONE,
    history: [{ sweep_id: SWEEP_ID, state: 'completed', total: 3, processed: 3, succeeded: 3, failed: 0, skipped: 0, snapshot_hash: '1121', created_at: '2026-10-26T12:00:00Z' }],
  })
  await page.goto('/combo/discovery')
  await page.getByRole('tab', { name: 'Decidir' }).click()
  await expect(page.getByTestId('decidir-table').locator('tr.result-row')).toHaveCount(3)
  await noHorizontalScroll(page)
  const nvda = page.getByTestId('decidir-table').locator('tr.result-row').filter({ hasText: 'RS-NVDA1121B2' })
  await expect(nvda.getByTestId('candidate-class-block')).toHaveScreenshot('card-1121-bloco-nvda.png', SHOT)
  await expect(page.getByTestId('mode-decidir').locator('> div').first()).toHaveScreenshot('card-1121-decidir-cabecalho.png', SHOT)

  await page.getByTestId('promote-RS-NVDA1121B2').click()
  const dialog = page.getByRole('dialog', { name: 'Promover a favorito' })
  await expect(dialog).toBeVisible()
  await expect(dialog).toHaveScreenshot('card-1121-modal-nvda.png', SHOT)
})
