import { expect, test } from '@playwright/test'

async function blockExternalNetwork(page: any) {
  await page.route('**/*', (route: any) => {
    const url = new URL(route.request().url())
    if (url.hostname === '127.0.0.1' || url.hostname === 'localhost') {
      return route.continue()
    }
    return route.abort('blockedbyclient')
  })
}

async function mockMonitorApi(page: any) {
  await page.route('**/api/opportunities/?tier=*', (route: any) =>
    route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify([]) })
  )
  await page.route('**/api/monitor/preferences', (route: any) =>
    route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({}) })
  )
  await page.route('**/api/user/binance-credentials', (route: any) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ configured: false, api_key_masked: null }),
    })
  )
}

test('first-use onboarding prompt appears and can be dismissed', async ({ page }) => {
  await blockExternalNetwork(page)
  await mockMonitorApi(page)

  await page.goto('/monitor')

  await expect(page.getByTestId('onboarding-prompt')).toBeVisible()
  await expect(page.getByText('Comece pelo fluxo certo')).toBeVisible()
  await expect(page.getByText('O Cripto Farol comeca pelos Favoritos')).toBeVisible()
  await expect(page.getByText('Apoio a decisao, com leitura de contexto e disciplina.')).toBeVisible()

  await page.getByRole('button', { name: 'Dispensar' }).click()
  await expect(page.getByTestId('onboarding-prompt')).toHaveCount(0)

  await page.reload()
  await expect(page.getByTestId('onboarding-prompt')).toHaveCount(0)
})

test('help route explains journey and is available in navigation', async ({ page }) => {
  await blockExternalNetwork(page)

  await page.goto('/help')

  await expect(page.getByTestId('help-page')).toBeVisible()
  await expect(page.getByRole('heading', { name: 'Como usar o Cripto Farol no primeiro acesso' })).toBeVisible()
  const guide = page.getByTestId('onboarding-guide')
  await expect(guide.locator('.onboarding-step').nth(0).getByRole('heading', { name: 'Favoritos' })).toBeVisible()
  await expect(guide.locator('.onboarding-step').nth(1).getByRole('heading', { name: 'Selecionar estrategias' })).toBeVisible()
  await expect(guide.locator('.onboarding-step').nth(2).getByRole('heading', { name: 'Monitor' })).toBeVisible()
  await expect(guide.locator('.onboarding-step').nth(3).getByRole('heading', { name: 'Carteira Binance opcional' })).toBeVisible()
  await expect(guide).toContainText('nao e requisito para comecar')
  await expect(page.getByText('Sem promessa de lucro')).toBeVisible()

  const navigation = page.getByRole('navigation', { name: 'Navegacao principal' })
  await expect(navigation.getByRole('link', { name: 'Ajuda', exact: true })).toBeVisible()
})

test('Monitor and Favorites show contextual help panels', async ({ page }) => {
  await blockExternalNetwork(page)
  await mockMonitorApi(page)

  await page.goto('/monitor')
  await expect(page.getByTestId('screen-help-panel')).toContainText('Como usar o Monitor')
  await expect(page.getByTestId('screen-help-panel')).toContainText('estrategias que voce selecionou em Favoritos')
  await expect(page.getByText('sempre como apoio a decisao')).toBeVisible()

  await page.goto('/favorites')
  await expect(page.getByTestId('screen-help-panel')).toContainText('Como usar Favoritos')
  await expect(page.getByText('Comece por aqui: compare estrategias')).toBeVisible()
})
