import { expect, test } from '@playwright/test'

const PROTO_PATH = '/prototypes/card-1008-scalp-ws-estado-fresco/'

const viewports = [
  { name: 'desktop', width: 1280, height: 800 },
  { name: 'mobile', width: 390, height: 844 },
] as const

for (const viewport of viewports) {
  test.describe(`card-1008 proto ${viewport.name}`, () => {
    test.use({ viewport: { width: viewport.width, height: viewport.height } })

    test('off → on fresh → livro indisponível → fresh → kill → nokey', async ({ page }) => {
      await page.goto(PROTO_PATH)
      await page.waitForSelector('#scalp-switch')

      const moduleEl = page.locator('#scalp-module')
      await expect(moduleEl).toHaveAttribute('data-state', 'off')
      await expect(page.locator('#scalp-status')).not.toContainText('livro indisponível')

      await page.click('#scalp-switch')
      await expect(moduleEl).toHaveAttribute('data-state', 'on')
      await expect(page.locator('#scalp-switch')).toHaveText('Ligado')
      await expect(page.locator('#scalp-status')).not.toHaveText('livro indisponível')

      await page.click('#scalp-sim-nobook')
      await expect(moduleEl).toHaveAttribute('data-state', 'on')
      await expect(moduleEl).toHaveAttribute('data-book', 'unavailable')
      await expect(page.locator('#scalp-status')).toHaveText('livro indisponível')
      await expect(page.locator('#scalp-switch')).toHaveText('Ligado')

      await page.click('#scalp-sim-fresh')
      await expect(moduleEl).toHaveAttribute('data-book', 'fresh')
      await expect(page.locator('#scalp-status')).not.toHaveText('livro indisponível')

      await page.click('#scalp-sim-kill')
      await expect(moduleEl).toHaveAttribute('data-state', 'kill')
      await expect(page.locator('#scalp-kill')).toBeVisible()
      await expect(page.locator('#scalp-status')).not.toContainText('livro indisponível')

      await page.click('#scalp-no-key')
      await expect(moduleEl).toHaveAttribute('data-state', 'nokey')
      await expect(page.locator('#scalp-status')).not.toContainText('livro indisponível')

      await page.click('#scalp-has-key')
      await expect(moduleEl).toHaveAttribute('data-state', 'off')
    })
  })
}
