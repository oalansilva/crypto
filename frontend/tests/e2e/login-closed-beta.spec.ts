import { expect, test } from '@playwright/test'

test('login page does not expose public account creation during closed beta', async ({ page }) => {
  await page.goto('/login')

  await expect(page.getByRole('heading', { name: 'Bem-vindo de volta' })).toBeVisible()
  await expect(page.locator('input[type="email"]')).toBeVisible()
  await expect(page.locator('input[type="password"]')).toBeVisible()
  await expect(page.getByRole('button', { name: 'Entrar' })).toBeVisible()
  await expect(page.getByRole('link', { name: 'Esqueci minha senha' })).toBeVisible()
  await expect(page.getByRole('button', { name: 'Criar Conta' })).toHaveCount(0)
  await expect(page.getByText('Criar conta')).toHaveCount(0)
  await expect(page.getByText('Nome')).toHaveCount(0)
  await expect(page.getByText('Confirmar Senha')).toHaveCount(0)
})
