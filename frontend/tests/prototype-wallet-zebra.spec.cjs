const { test, expect } = require('@playwright/test')

test('prototype wallet zebra — desktop', async ({ page }) => {
  await page.goto('/prototypes/wallet-easier-reading/')
  await page.waitForLoadState('networkidle')
  const consoleErrors = []
  page.on('console', (m) => { if (m.type() === 'error') consoleErrors.push(m.text()) })
  page.on('pageerror', (e) => consoleErrors.push(String(e)))

  const desktopTable = page.locator('table.desktop-table')
  await expect(desktopTable).toBeVisible()

  const rows = desktopTable.locator('tbody tr')
  await expect(rows).toHaveCount(2)

  const bg1 = await rows.nth(0).evaluate((el) => getComputedStyle(el).backgroundColor)
  const bg2 = await rows.nth(1).evaluate((el) => getComputedStyle(el).backgroundColor)
  expect(bg1).not.toBe(bg2)

  await expect(page.locator('body')).not.toContainText('Saldos lidos da Binance Spot por chave API read-only')
  await expect(page.locator('body')).not.toContainText('Layout responsivo: tabela no desktop e cards no mobile')
  await expect(page.locator('.chip')).toHaveCount(0)

  await expect(page.locator('h1')).toHaveText('Carteira')
  await expect(rows.nth(0)).toContainText('BTC')
  await expect(rows.nth(1)).toContainText('ETH')

  const mobileCards = page.locator('.mobile-cards')
  const mobileVisible = await mobileCards.isVisible()
  expect(mobileVisible).toBe(false)

  const desktopVisible = await desktopTable.isVisible()
  expect(desktopVisible).toBe(true)

  expect(consoleErrors).toEqual([])
})

test('prototype wallet zebra — mobile', async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 })
  await page.goto('/prototypes/wallet-easier-reading/')
  await page.waitForLoadState('networkidle')
  const consoleErrors = []
  page.on('console', (m) => { if (m.type() === 'error') consoleErrors.push(m.text()) })
  page.on('pageerror', (e) => consoleErrors.push(String(e)))

  const desktopTable = page.locator('table.desktop-table')
  const desktopVisible = await desktopTable.isVisible()
  expect(desktopVisible).toBe(false)

  const mobileCards = page.locator('.mobile-cards')
  await expect(mobileCards).toBeVisible()
  await expect(mobileCards.locator('.mcard')).toHaveCount(2)
  await expect(mobileCards.locator('.mcard').nth(0)).toContainText('BTC')

  const zebraInCards = await mobileCards.locator('.mcard').evaluateAll((els) => {
    const bgs = els.map((el) => getComputedStyle(el).backgroundColor)
    return new Set(bgs).size
  })
  expect(zebraInCards).toBe(1)

  await expect(page.locator('body')).not.toContainText('Saldos lidos da Binance Spot por chave API read-only')
  await expect(page.locator('.chip')).toHaveCount(0)

  expect(consoleErrors).toEqual([])
})
