import { expect, test } from '@playwright/test'

type TestUser = {
  id: string
  email: string
  name: string
  isAdmin: boolean
}

const user: TestUser = {
  id: 'profile-user',
  email: 'profile@example.com',
  name: 'Nome Atual',
  isAdmin: false,
}

async function setupAuthenticatedProfile(page: any) {
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

  await page.route('**/api/users/me', async (route: any) => {
    if (route.request().method() === 'PUT') {
      const body = JSON.parse(route.request().postData() || '{}') as { name?: string }
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          ...user,
          name: body.name || user.name,
          createdAt: '2026-05-01T10:00:00Z',
          lastLogin: '2026-05-02T10:00:00Z',
        }),
      })
      return
    }

    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        ...user,
        createdAt: '2026-05-01T10:00:00Z',
        lastLogin: '2026-05-02T10:00:00Z',
      }),
    })
  })
}

test('profile save shows visible success feedback', async ({ page }) => {
  await setupAuthenticatedProfile(page)

  await page.goto('/profile')
  await expect(page.getByRole('heading', { name: 'Meu Perfil' })).toBeVisible()

  await page.getByLabel('Nome').fill('Nome Atualizado')
  await page.getByRole('button', { name: 'Salvar perfil' }).click()

  const successToast = page.getByRole('status').filter({ hasText: 'Perfil atualizado' })
  await expect(successToast).toBeVisible()
  await expect(successToast).toContainText('Seu nome foi salvo com sucesso.')

  await successToast.getByRole('button', { name: 'Fechar notificação' }).click()
  await expect(successToast).not.toBeVisible()
})
