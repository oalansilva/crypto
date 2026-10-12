import fs from 'node:fs'
import path from 'node:path'
import { expect, test } from '@playwright/test'

const PROTO_INDEX = '/prototypes/card-1078-opcoes-periodo/'
const PROTO_COMBO = '/prototypes/card-1078-opcoes-periodo/combo.html'
const indexHtml = path.join(process.cwd(), 'public/prototypes/card-1078-opcoes-periodo/index.html')
const comboHtml = path.join(process.cwd(), 'public/prototypes/card-1078-opcoes-periodo/combo.html')

const ADMIN_USER = {
  id: 'discovery-admin',
  email: 'alan@example.com',
  name: 'Alan Silva',
  isAdmin: true,
  mustChangePassword: false,
}

const PERIOD_LABELS = [
  '15 dias',
  '1 mês',
  '3 meses',
  '6 meses',
  '1 ano',
  '2 anos',
  'Personalizado',
  'Todo o histórico',
]

test.beforeAll(() => {
  if (!fs.existsSync(indexHtml)) throw new Error(`Missing prototype: ${indexHtml}`)
  if (!fs.existsSync(comboHtml)) throw new Error(`Missing prototype: ${comboHtml}`)
})

async function expectPeriodOptions(page: import('@playwright/test').Page) {
  const select = page.getByTestId('sel-period')
  const options = select.locator('option')
  await expect(options).toHaveCount(8)
  for (const label of PERIOD_LABELS) {
    await expect(options.filter({ hasText: label })).toHaveCount(1)
  }
}

test.describe('card 1078 — proto canónico', () => {
  test('landmarks, default 15 dias, Personalizado bloqueia', async ({ page }) => {
    await page.setViewportSize({ width: 1440, height: 900 })
    await page.goto(PROTO_INDEX, { waitUntil: 'load' })
    await expect(page.getByRole('heading', { name: 'Descoberta de estratégias swing' })).toBeVisible()
    await expect(page.getByRole('heading', { name: 'Preflight' })).toBeVisible()
    await expect(page.getByRole('heading', { name: 'Rascunho de varredura' })).toBeVisible()
    await expectPeriodOptions(page)
    await expect(page.getByTestId('sel-period')).toHaveValue('15d')
    await expect(page.getByTestId('preflight-3line')).toContainText('15 dias')
    await page.getByTestId('sel-period').selectOption('custom')
    await expect(page.getByTestId('date-start')).toBeVisible()
    await expect(page.getByTestId('date-end')).toBeVisible()
    await expect(page.getByTestId('start-sweep')).toBeDisabled()
    await expect(page.getByTestId('preflight-impediments')).toContainText('Seleccione Data Inicial e Data Final.')
  })
})

test.describe('card 1078 — rota viva Descoberta', () => {
  test('default 15d e Personalizado inválido', async ({ page }) => {
    await page.addInitScript((user) => {
      localStorage.setItem('auth_access_token', 'discovery-admin-token')
      localStorage.setItem('auth_refresh_token', 'discovery-admin-refresh')
      localStorage.setItem('auth_user', JSON.stringify(user))
      localStorage.setItem('cripto-farol-onboarding-dismissed', '1')
    }, ADMIN_USER)
    await page.route('**/api/combos/templates', (route) =>
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ prebuilt: [], examples: [], custom: [] }),
      }),
    )
    await page.route('**/api/exchanges/binance/symbols', (route) =>
      route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ symbols: [] }) }),
    )
    await page.route('**/api/combos/discovery/sweeps/active', (route) =>
      route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ sweeps: [] }) }),
    )
    await page.route('**/api/combos/discovery/sweeps/history', (route) =>
      route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ sweeps: [] }) }),
    )
    await page.goto('/combo/discovery')
    await page.getByRole('tab', { name: 'Montar' }).click()
    await expectPeriodOptions(page)
    await expect(page.getByTestId('sel-period')).toHaveValue('15d')
    await page.getByTestId('sel-period').selectOption('custom')
    await expect(page.getByTestId('preflight-impediments')).toContainText('Seleccione Data Inicial e Data Final.')
    await expect(page.getByTestId('start-sweep')).toBeDisabled()
  })
})

test.describe('card 1078 — proto combo extra', () => {
  test('lista igual e Todo o histórico marcado', async ({ page }) => {
    await page.goto(PROTO_COMBO, { waitUntil: 'load' })
    await expectPeriodOptions(page)
    await expect(page.getByTestId('sel-period')).toHaveValue('all')
  })
})
