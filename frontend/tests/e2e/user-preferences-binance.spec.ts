import { expect, test } from '@playwright/test'

type TestUser = {
  id: string
  email: string
  name: string
  isAdmin: boolean
}

const user: TestUser = {
  id: 'profile-binance-user',
  email: 'profile.binance@example.com',
  name: 'Profile Binance',
  isAdmin: false,
}

async function setupApiMocks(page: any, opts?: { configured?: boolean }) {
  const configured = opts?.configured ?? false

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

  await page.route('**/api/users/me', (route: any) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        ...user,
        createdAt: '2026-05-01T10:00:00Z',
        lastLogin: '2026-05-02T10:00:00Z',
      }),
    })
  )

  await page.route('**/api/user/binance-credentials', async (route: any) => {
    const method = route.request().method()
    if (method === 'PUT') {
      const body = route.request().postDataJSON() as { api_key?: string; api_secret?: string }
      if (String(body?.api_key || '').includes('@')) {
        return route.fulfill({
          status: 400,
          contentType: 'application/json',
          body: JSON.stringify({ detail: 'API Key inválida' }),
        })
      }
      return route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ configured: true, api_key_masked: 'abcd****wxyz' }),
      })
    }
    if (method === 'DELETE') {
      return route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ ok: true }),
      })
    }
    return route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        configured,
        api_key_masked: configured ? 'abcd****wxyz' : null,
      }),
    })
  })
}

test('user profile manages Binance credentials', async ({ page }) => {
  await setupApiMocks(page)

  await page.goto('/profile')

  await expect(page.getByRole('heading', { name: 'Meu Perfil', exact: true })).toBeVisible()
  await expect(page.getByRole('heading', { name: 'Dados da conta', exact: true })).toBeVisible()
  await expect(page.getByRole('heading', { name: 'Credenciais Binance', exact: true })).toBeVisible()
  await expect(page.getByText('Chave API somente leitura vinculada à sua conta.')).toBeVisible()
  await expect(page.getByText('Status da chave')).toBeVisible()
  await expect(page.getByText('Não configurada')).toBeVisible()
  await expect(page.getByText('Nenhuma chave salva. Cole API Key e Secret abaixo para conectar.')).toBeVisible()

  const apiKey = page.getByLabel('Binance API Key read-only')
  const apiSecret = page.getByLabel('Binance API Secret read-only')

  await expect(apiKey).toHaveAttribute('placeholder', 'Cole a API Key da Binance')
  await expect(apiKey).toHaveAttribute('autocomplete', 'off')
  await expect(apiKey).toHaveAttribute('data-lpignore', 'true')
  await expect(apiSecret).toHaveAttribute('placeholder', 'Cole o API Secret da mesma chave')
  await expect(apiSecret).toHaveAttribute('autocomplete', 'new-password')
  await expect(apiSecret).toHaveAttribute('data-lpignore', 'true')

  await apiKey.fill('alan@example.com')
  await apiSecret.fill('senha-da-binance')
  await page.getByRole('button', { name: /Salvar credenciais/ }).click()
  await expect(page.getByText('Este campo não aceita e-mail.')).toBeVisible()

  await apiKey.fill('valid-binance-api-key')
  await apiSecret.fill('valid-binance-api-secret')
  await page.getByRole('button', { name: /Salvar credenciais/ }).click()
  await expect(page.getByText('Configurada')).toBeVisible()
  await expect(page.getByText('API Key atual')).toBeVisible()
  await expect(page.getByText('abcd****wxyz')).toBeVisible()
  await expect(page.getByRole('button', { name: 'Remover chave' })).toBeVisible()
  await expect(page.getByRole('button', { name: /Atualizar credenciais/ })).toBeVisible()
  await expect(apiSecret).toHaveValue('')
})

test('legacy preferences route redirects to profile', async ({ page }) => {
  await setupApiMocks(page)
  await page.goto('/preferences')
  await expect(page).toHaveURL(/\/profile$/)
  await expect(page.getByRole('heading', { name: 'Meu Perfil', exact: true })).toBeVisible()
  await expect(page.getByText('Credenciais Binance')).toBeVisible()
})
