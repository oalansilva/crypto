import { expect, test } from '@playwright/test'

type TestUser = {
  id: string
  email: string
  name: string
  isAdmin: boolean
}

const user: TestUser = {
  id: 'change-password-user',
  email: 'change-password@example.com',
  name: 'Change Password User',
  isAdmin: false,
}

async function setupAuthenticatedUser(page: any) {
  await page.addInitScript((authUser: TestUser) => {
    window.localStorage.setItem('auth_access_token', 'test-access-token')
    window.localStorage.setItem('auth_refresh_token', 'test-refresh-token')
    window.localStorage.setItem('auth_user', JSON.stringify(authUser))
  }, user)

  await page.route('**/*', (route: any) => {
    const url = new URL(route.request().url())
    if (url.hostname === '127.0.0.1' || url.hostname === 'localhost') {
      return route.continue()
    }
    return route.abort('blockedbyclient')
  })

  await page.route('**/api/auth/me', (route: any) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(user),
    })
  )
}

test('change password fields keep icons clear of input text', async ({ page }) => {
  await setupAuthenticatedUser(page)

  await page.goto('/change-password')
  await expect(page.getByRole('heading', { name: 'Alterar Senha' })).toBeVisible()

  const inputs = page.locator('.input-with-icon')
  await expect(inputs).toHaveCount(3)

  const spacings = await inputs.evaluateAll((elements) =>
    elements.map((element) => {
      const inputElement = element as HTMLInputElement
      const wrapper = inputElement.parentElement
      const icon = wrapper?.querySelector('.input-icon')
      const inputBox = inputElement.getBoundingClientRect()
      const iconBox = icon?.getBoundingClientRect()
      const paddingLeft = Number.parseFloat(window.getComputedStyle(inputElement).paddingLeft)

      inputElement.value = 'SenhaForte123!'

      return {
        iconRight: iconBox?.right ?? 0,
        textStart: inputBox.left + paddingLeft,
        paddingLeft,
      }
    }),
  )

  for (const spacing of spacings) {
    expect(spacing.paddingLeft).toBeGreaterThanOrEqual(48)
    expect(spacing.iconRight).toBeLessThanOrEqual(spacing.textStart - 8)
  }
})
