import { expect, test } from '@playwright/test'

async function setupApiMocks(page: any, opts?: { configured?: boolean }) {
  const configured = opts?.configured ?? false

  await page.route('**/*', (route: any) => {
    const url = new URL(route.request().url())
    if (url.hostname === '127.0.0.1' || url.hostname === 'localhost') {
      return route.continue()
    }
    return route.abort('blockedbyclient')
  })

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

test('user preferences page manages Binance credentials', async ({ page }) => {
  await setupApiMocks(page)

  await page.goto('/preferences')

  await expect(page.getByRole('heading', { name: 'Preferências', exact: true })).toBeVisible()
  await expect(page.getByText('Credenciais Binance')).toBeVisible()
  await expect(
    page.getByText(
      'A Home e a carteira usam uma chave API vinculada ao usuário logado. Use permissão somente leitura e mantenha IP whitelist habilitado na Binance.',
    ),
  ).toBeVisible()
  await expect(page.getByText('Não configurada')).toBeVisible()

  const apiKey = page.getByLabel('Binance API Key read-only')
  const apiSecret = page.getByLabel('Binance API Secret read-only')

  await expect(apiKey).toHaveAttribute('placeholder', 'API Key read-only da Binance')
  await expect(apiKey).toHaveAttribute('autocomplete', 'off')
  await expect(apiKey).toHaveAttribute('data-lpignore', 'true')
  await expect(apiSecret).toHaveAttribute('placeholder', 'API Secret da chave read-only')
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
  await expect(page.getByText('abcd****wxyz')).toBeVisible()
  await expect(apiSecret).toHaveValue('')
})
