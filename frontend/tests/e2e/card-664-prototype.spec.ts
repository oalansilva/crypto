import { test, expect, type Page } from '@playwright/test'

const prototypePath = '/prototypes/card-664-discovery-restore-reload/'

async function assertNoBrowserErrors(page: Page) {
  const errors: string[] = []
  page.on('console', (message) => {
    if (message.type() === 'error') errors.push(`console: ${message.text()}`)
  })
  page.on('pageerror', (error) => errors.push(`page: ${error.message}`))
  return errors
}

async function openPrototype(page: Page) {
  await page.goto(prototypePath, { waitUntil: 'load' })
  await expect(page.locator('#active-card')).toBeVisible()
  await expect(page.locator('#progress-count')).toContainText('21 de 28')
  await expect(page.getByText('Varredura ativa recuperada do servidor')).toBeVisible()
}

test.describe('card 664 — retorno da descoberta após reload', () => {
  test('desktop restaura o sweep, pausa/retoma e preserva o snapshot', async ({ page }) => {
    const errors = await assertNoBrowserErrors(page)
    await page.setViewportSize({ width: 1440, height: 1000 })
    await openPrototype(page)
    await expect(page.locator('#start-sweep')).toBeDisabled()

    await page.getByRole('button', { name: 'Pausar' }).click()
    await expect(page.locator('#active-state-chip')).toHaveText('PAUSED')
    await expect(page.getByRole('button', { name: 'Retomar' })).toBeVisible()

    await page.getByRole('button', { name: 'Retomar' }).click()
    await expect(page.locator('#wake-note')).toBeVisible()
    await page.waitForTimeout(1_100)
    await page.reload()
    await expect(page.locator('#active-card')).toBeVisible()
      await expect(page.locator('#progress-count')).toHaveText('22 de 28')
    await expect(page.locator('#draft-chip')).toHaveText('CONGELADO')

    await page.selectOption('#fixture', 'error')
    await expect(page.locator('#active-card')).toBeHidden()
    await expect(page.getByText('Não foi possível verificar a varredura ativa')).toBeVisible()
    await expect(page.getByRole('button', { name: 'Tentar novamente' })).toBeVisible()
    await page.getByRole('button', { name: 'Tentar novamente' }).click()
    await expect(page.locator('#active-card')).toBeVisible()
    await expect(page.locator('#progress-heading')).toBeFocused()
    await page.selectOption('#fixture', 'loading')
    await expect(page.getByText('Verificando varredura ativa…')).toBeVisible()
    await expect(page.locator('#active-card')).toBeHidden()
    await expect(page.locator('#new-draft')).toBeDisabled()
    await page.selectOption('#fixture', 'none')
    await expect(page.locator('#draft-status')).toContainText('nenhum sweep')
    await expect(page.locator('#active-card')).toBeHidden()
    await expect(page.locator('#start-sweep')).toBeEnabled()

    for (const state of ['pending', 'cancelling', 'failed', 'partial_failure']) {
      await page.selectOption('#fixture', state)
      await expect(page.locator('#active-state-chip')).toHaveText(state.toUpperCase())
      await expect(page.locator('#active-card')).toBeVisible()
    }
    await page.selectOption('#fixture', 'pending')
    await expect(page.locator('#active-state-chip')).toHaveText('PENDING')
    await page.getByRole('button', { name: 'Cancelar' }).click()
    await page.getByRole('button', { name: 'Confirmar cancelamento' }).click()
    await expect(page.locator('#active-state-chip')).toHaveText('CANCELLED')
    await page.selectOption('#fixture', 'deferred')
    await expect(page.locator('#wake-note')).toContainText('deferred')
    await page.selectOption('#fixture', 'running')
    await expect(page.locator('#start-sweep')).toBeDisabled()
    await page.getByRole('button', { name: 'Novo rascunho' }).click()
    await expect(page.locator('#draft-key')).toHaveText('c4e81a90…')
    await expect(page.locator('#start-sweep')).toBeEnabled()
    await expect(page.locator('#active-card')).toBeVisible()
    await page.getByRole('button', { name: 'Histórico de varreduras' }).click()
    await expect(page.locator('#history-panel')).toBeVisible()
    await page.selectOption('#run-selector', 'previous')
    await expect(page.locator('#leaderboard-meta')).toContainText('#7b3ca7ad')
    await expect(page.locator('#results-body')).toContainText('EMA: retomada histórica')
    await expect(page.locator('#active-card')).toBeVisible()
    await page.selectOption('#run-selector', 'other-active')
    await expect(page.locator('#leaderboard-meta')).toContainText('#a8c12e4b')
    await expect(page.locator('#results-body')).toContainText('Volume: rompimento')
    await expect(page.locator('#active-sweep-id')).toContainText('#a8c12e4b')
    await expect(page.locator('#active-state-chip')).toHaveText('PAUSED')
    await expect(page.locator('#active-card')).toBeVisible()
    await page.selectOption('#run-selector', 'active')
    await expect(page.locator('#leaderboard-meta')).toContainText('#fd40d0c9')
    await page.selectOption('#fixture', 'completed')
    await expect(page.locator('#active-state-chip')).toHaveText('COMPLETED')
    await expect(page.getByRole('button', { name: 'Pausar' })).toBeDisabled()
    await page.reload()
    await expect(page.locator('#active-card')).toBeHidden()
    await expect(page.locator('#draft-status')).toContainText('nenhum sweep')
    await expect(page.locator('#run-selector')).toHaveValue('same-terminal')
    await expect(page.locator('#leaderboard-meta')).toContainText('#fd40d0c9')
    await expect(page.locator('#leaderboard-meta')).toContainText('concluída')
    await expect(page.locator('#results-body')).toContainText('Bandas: expansão de volatilidade')
    await page.selectOption('#fixture', 'running')
    await page.selectOption('#fixture', 'race')
    await expect(page.locator('#active-card')).toBeHidden()
    await expect(page.locator('#run-selector')).toHaveValue('same-terminal')
    await expect(page.locator('#leaderboard-meta')).toContainText('#fd40d0c9')
    const undersized = await page.evaluate(() =>
      [...document.querySelectorAll('button, select')].filter((el) => {
        const box = el.getBoundingClientRect()
        return box.height > 0 && box.width > 0 && box.height < 44
      }).map((el) => (el as HTMLElement).id || (el as HTMLElement).className),
    )
    expect(undersized).toEqual([])
    await page.screenshot({ path: '/tmp/card-664-discovery-desktop.png', fullPage: true })
    expect(errors).toEqual([])
  })

  test('mobile mantém o sweep recuperado sem overflow horizontal', async ({ page }) => {
    const errors = await assertNoBrowserErrors(page)
    await page.setViewportSize({ width: 390, height: 844 })
    await openPrototype(page)

    await expect(page.locator('#active-card')).toBeVisible()
    await expect(page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).resolves.toBe(true)
    await page.getByRole('button', { name: 'Pausar' }).click()
    await expect(page.locator('#active-state-chip')).toHaveText('PAUSED')
    await expect(page.getByRole('button', { name: 'Retomar' })).toBeVisible()
    await page.screenshot({ path: '/tmp/card-664-discovery-mobile.png', fullPage: true })
    expect(errors).toEqual([])
  })
})
