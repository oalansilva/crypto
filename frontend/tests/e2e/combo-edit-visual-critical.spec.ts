import { expect, test, type Page } from '@playwright/test'

const ADMIN_USER = {
  id: 'combo-edit-admin',
  email: 'alan@example.com',
  name: 'Alan Silva',
  isAdmin: true,
  mustChangePassword: false,
}

const TEMPLATE = {
  name: 'multi_ma_crossover',
  display_name: 'Médias Móveis: Tendência em Virada',
  description: 'Compara médias de velocidades diferentes e entra quando a média curta assume a liderança sobre a tendência longa; encerra quando essa hierarquia se desfaz.',
  is_readonly: true,
  indicators: [],
  entry_logic: 'short > long',
  exit_logic: 'crossover down',
  optimization_schema: {},
}

async function installMocks(page: Page) {
  const identityPuts: string[] = []
  await page.addInitScript((user) => {
    localStorage.setItem('auth_access_token', 'combo-edit-admin-token')
    localStorage.setItem('auth_refresh_token', 'combo-edit-admin-refresh')
    localStorage.setItem('auth_user', JSON.stringify(user))
    localStorage.setItem('cripto-farol-onboarding-dismissed', '1')
  }, ADMIN_USER)

  await page.route('**/api/**', (route) =>
    route.fulfill({ status: 200, contentType: 'application/json', body: '{}' }),
  )
  await page.route('**/api/auth/me', (route) =>
    route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(ADMIN_USER) }),
  )
  await page.route('**/api/combos/meta/multi_ma_crossover/identity', async (route) => {
    identityPuts.push(route.request().postData() || '')
    return route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        ...TEMPLATE,
        display_name: 'Médias Móveis: Título editado',
        description: TEMPLATE.description,
      }),
    })
  })
  await page.route('**/api/combos/meta/multi_ma_crossover', (route) => {
    if (route.request().method() === 'PUT') {
      return route.fulfill({ status: 403, contentType: 'application/json', body: JSON.stringify({ detail: 'read-only' }) })
    }
    return route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(TEMPLATE),
    })
  })
  await page.route('**/api/combos/templates', (route) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ prebuilt: [TEMPLATE], examples: [], custom: [] }),
    }),
  )
  return identityPuts
}

test('combo edit lets admin change public title on a readonly template', async ({ page }) => {
  const identityPuts = await installMocks(page)
  await page.goto('/combo/edit/multi_ma_crossover')

  await expect(page.getByTestId('combo-edit-heading')).toHaveText('Médias Móveis: Tendência em Virada')
  await expect(page.getByTestId('combo-identity-title-input')).toHaveValue('Médias Móveis: Tendência em Virada')
  await expect(page.getByText('Read-Only Template')).toHaveCount(0)

  await expect(page).toHaveScreenshot('combo-edit-identity.png', {
    animations: 'disabled',
    caret: 'hide',
    fullPage: false,
  })

  await page.getByTestId('combo-identity-title-input').fill('Médias Móveis: Título editado')
  await page.getByTestId('combo-identity-save').click()
  await expect(page).toHaveURL(/\/combo\/select/)
  expect(identityPuts.some((body) => body.includes('Médias Móveis: Título editado'))).toBe(true)
})

// Inventory path: /combo/edit/:templateName
