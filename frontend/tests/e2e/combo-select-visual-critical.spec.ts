import { expect, test, type Page } from '@playwright/test'

const ADMIN_USER = {
  id: 'combo-select-admin',
  email: 'alan@example.com',
  name: 'Alan Silva',
  isAdmin: true,
  mustChangePassword: false,
}

const TEMPLATES = {
  prebuilt: [
    {
      name: 'multi_ma_crossover',
      display_name: 'Médias Móveis: Tendência em Virada',
      description: 'Compara médias de velocidades diferentes e entra quando a média curta assume a liderança sobre a tendência longa; encerra quando essa hierarquia se desfaz.',
      is_readonly: true,
    },
  ],
  examples: [],
  custom: [],
}

async function installMocks(page: Page) {
  await page.addInitScript((user) => {
    localStorage.setItem('auth_access_token', 'combo-select-admin-token')
    localStorage.setItem('auth_refresh_token', 'combo-select-admin-refresh')
    localStorage.setItem('auth_user', JSON.stringify(user))
    localStorage.setItem('cripto-farol-onboarding-dismissed', '1')
  }, ADMIN_USER)

  await page.route('**/api/**', (route) =>
    route.fulfill({ status: 200, contentType: 'application/json', body: '{}' }),
  )
  await page.route('**/api/auth/me', (route) =>
    route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(ADMIN_USER) }),
  )
  await page.route('**/api/combos/templates', (route) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(TEMPLATES),
    }),
  )
}

test('combo select shows public catalog title instead of Title-Case technical name', async ({ page }) => {
  await installMocks(page)
  await page.goto('/combo/select')

  const title = page.getByTestId('combo-select-strategy-title')
  await expect(title).toHaveText('Médias Móveis: Tendência em Virada')
  await expect(page.getByText('Multi Ma Crossover')).toHaveCount(0)
  await expect(page.getByText('multi_ma_crossover')).toHaveCount(0)
  await expect(page.getByText('Compara médias de velocidades diferentes')).toBeVisible()

  await expect(page).toHaveScreenshot('combo-select-identity.png', {
    animations: 'disabled',
    caret: 'hide',
    fullPage: false,
  })
})
