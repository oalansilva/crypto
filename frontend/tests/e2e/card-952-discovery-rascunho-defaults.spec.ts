import fs from 'node:fs'
import path from 'node:path'
import { expect, test, type Page } from '@playwright/test'

const PROTOTYPE_PATH = '/prototypes/card-952-discovery-rascunho-defaults/'
const prototypeHtml = path.join(
  process.cwd(),
  'public/prototypes/card-952-discovery-rascunho-defaults/index.html',
)

const ADMIN_USER = {
  id: 'discovery-admin',
  email: 'alan@example.com',
  name: 'Alan Silva',
  isAdmin: true,
  mustChangePassword: false,
}

const RESTORE_SNAPSHOT = {
  axes: {
    templates: ['multi_ma_crossover', 'bollinger_breakout', 'ema_rsi_reversal'],
    symbols: ['BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'BNB/USDT'],
    timeframes: ['4h', '1d'],
    directions: ['long'],
  },
  raw_total: 48,
  exclusions: {},
  excluded_count: 0,
  valid_total: 48,
  limits: { max_total: 1000 },
  errors: {},
  expires_at: '2026-08-15T13:00:00Z',
  snapshot_token: 'snapshot-token-952',
  snapshot_hash: '952abcdef952abcdef952abcdef952abcdef952abcdef952abcdef952abcdef',
  period_type: 'all',
}

const RESTORE_EMPTY_TF = {
  ...RESTORE_SNAPSHOT,
  axes: {
    ...RESTORE_SNAPSHOT.axes,
    timeframes: [] as string[],
  },
}

const ACTIVE_RUNNING = {
  sweep_id: '952running952running952running952run',
  state: 'running',
  total: 48,
  succeeded: 10,
  failed: 0,
  skipped: 0,
  processed: 10,
  terminal_reason: null,
  terminal_code: null,
  draft_key: 'draft-952-live',
  snapshot: RESTORE_SNAPSHOT,
  updated_at: '2026-08-23T00:40:00Z',
}

const TEMPLATES = [
  { name: 'multi_ma_crossover', display_name: 'Médias: tendência', description: 'x', is_readonly: true },
  { name: 'bollinger_breakout', display_name: 'Bandas: expansão', description: 'x', is_readonly: true },
  { name: 'ema_rsi_reversal', display_name: 'EMA + RSI', description: 'x', is_readonly: true },
]

const SYMBOLS = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'BNB/USDT', 'ADA/USDT']

test.beforeAll(() => {
  if (!fs.existsSync(prototypeHtml)) {
    throw new Error(`Prototype missing in checkout: ${prototypeHtml}`)
  }
})

async function installEmptyDraftMocks(page: Page, opts?: { active?: unknown[]; history?: unknown[] }) {
  await page.addInitScript((user) => {
    localStorage.setItem('auth_access_token', 'discovery-admin-token')
    localStorage.setItem('auth_refresh_token', 'discovery-admin-refresh')
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
      body: JSON.stringify({ prebuilt: TEMPLATES, examples: [], custom: [] }),
    }),
  )
  await page.route('**/api/exchanges/binance/symbols', (route) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ symbols: SYMBOLS }),
    }),
  )
  await page.route('**/api/combos/discovery/sweeps/preflight', (route) =>
    route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(RESTORE_SNAPSHOT) }),
  )
  await page.route('**/api/combos/discovery/sweeps/active', (route) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ sweeps: opts?.active ?? [] }),
    }),
  )
  await page.route('**/api/combos/discovery/sweeps/history', (route) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ sweeps: opts?.history ?? [] }),
    }),
  )
}

async function assertNewDraftMontarState(page: Page, templateTotal: number, symbolTotal: number) {
  await expect(page.getByTestId('template-count')).toContainText(`0 de ${templateTotal} selecionados`)
  await expect(page.getByTestId('symbol-count')).toContainText(`0 de ${symbolTotal} selecionados`)
  await expect(page.getByTestId('preflight-impediments')).toContainText('Falta fazer')
  await expect(page.getByTestId('start-sweep')).toBeDisabled()
  await expect(page.locator('label').filter({ hasText: '4 horas' }).locator('input')).not.toBeChecked()
  await expect(page.locator('label').filter({ hasText: '1 dia' }).locator('input')).toBeChecked()
}

async function assertProtoNewDraftState(page: Page) {
  await expect(page.getByTestId('template-count')).toContainText('0 de')
  await expect(page.getByTestId('symbol-count')).toContainText('0 de')
  await expect(page.getByTestId('template-chips')).toBeEmpty()
  await expect(page.getByTestId('symbol-chips')).toBeEmpty()
  await expect(page.getByTestId('tf-4h')).not.toBeChecked()
  await expect(page.getByTestId('tf-1d')).toBeChecked()
  await expect(page.getByTestId('preflight-impediments')).toBeVisible()
  await expect(page.getByTestId('start-sweep')).toBeDisabled()
}

test.describe('card 952 — rascunho novo (rota viva)', () => {
  test('desktop: primeira abertura vazia, só 1 dia, 4h marcável', async ({ page }) => {
    await page.setViewportSize({ width: 1440, height: 900 })
    await installEmptyDraftMocks(page)
    await page.goto('/combo/discovery')
    await expect(page.getByRole('heading', { name: 'Descoberta de estratégias swing' })).toBeVisible()
    await assertNewDraftMontarState(page, 3, 5)
    await page.getByText('4 horas').click()
    await expect(page.locator('label').filter({ hasText: '4 horas' }).locator('input')).toBeChecked()
    await page.getByRole('checkbox', { name: 'Médias: tendência' }).first().click()
    await page.getByRole('checkbox', { name: 'BTC/USDT' }).first().click()
    await expect(page.getByTestId('preflight-impediments')).toHaveCount(0)
  })

  test('mobile: início bloqueado com seleção vazia', async ({ page }) => {
    await page.setViewportSize({ width: 390, height: 844 })
    await installEmptyDraftMocks(page)
    await page.goto('/combo/discovery')
    await assertNewDraftMontarState(page, 3, 5)
    const overflow = await page.evaluate(
      () => document.documentElement.scrollWidth <= document.documentElement.clientWidth,
    )
    expect(overflow).toBe(true)
  })

  test('Novo rascunho limpa seleção com live em curso', async ({ page }) => {
    await installEmptyDraftMocks(page, { active: [ACTIVE_RUNNING] })
    await page.route(`**/api/combos/discovery/sweeps/${ACTIVE_RUNNING.sweep_id}`, (route) =>
      route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(ACTIVE_RUNNING) }),
    )
    await page.route(`**/api/combos/discovery/sweeps/${ACTIVE_RUNNING.sweep_id}/leaderboard**`, (route) =>
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ results: [], total: 0, unfiltered_total: 0, offset: 0, limit: 3 }),
      }),
    )
    await page.goto('/combo/discovery')
    await expect(page.getByTestId('new-draft')).toBeVisible()
    await page.getByTestId('new-draft').click()
    await page.getByRole('tab', { name: 'Montar' }).click()
    await assertNewDraftMontarState(page, 3, 5)
  })

  test('restore preserva eixos gravados', async ({ page }) => {
    await installEmptyDraftMocks(page, {
      active: [ACTIVE_RUNNING],
      history: [
        {
          sweep_id: ACTIVE_RUNNING.sweep_id,
          state: 'running',
          total: 48,
          processed: 10,
          succeeded: 10,
          failed: 0,
          skipped: 0,
          snapshot_hash: RESTORE_SNAPSHOT.snapshot_hash,
          created_at: '2026-08-22T14:00:00Z',
        },
      ],
    })
    await page.route(`**/api/combos/discovery/sweeps/${ACTIVE_RUNNING.sweep_id}`, (route) =>
      route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(ACTIVE_RUNNING) }),
    )
    await page.route(`**/api/combos/discovery/sweeps/${ACTIVE_RUNNING.sweep_id}/leaderboard**`, (route) =>
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ results: [], total: 0, unfiltered_total: 0, offset: 0, limit: 3 }),
      }),
    )
    await page.goto('/combo/discovery')
    await page.getByRole('tab', { name: 'Montar' }).click()
    await expect(page.getByTestId('template-count')).toContainText('3 de 3 selecionados')
    await expect(page.getByTestId('symbol-count')).toContainText('4 de 5 selecionados')
    await expect(page.locator('label').filter({ hasText: '4 horas' }).locator('input')).toBeChecked()
    await expect(page.locator('label').filter({ hasText: '1 dia' }).locator('input')).toBeChecked()
  })

  test('restore sem timeframes não inventa 4h+1d', async ({ page }) => {
    const sweep = { ...ACTIVE_RUNNING, snapshot: RESTORE_EMPTY_TF }
    await installEmptyDraftMocks(page, { active: [sweep] })
    await page.route(`**/api/combos/discovery/sweeps/${sweep.sweep_id}`, (route) =>
      route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(sweep) }),
    )
    await page.route(`**/api/combos/discovery/sweeps/${sweep.sweep_id}/leaderboard**`, (route) =>
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ results: [], total: 0, unfiltered_total: 0, offset: 0, limit: 3 }),
      }),
    )
    await page.goto('/combo/discovery')
    await page.getByRole('tab', { name: 'Montar' }).click()
    await expect(page.locator('label').filter({ hasText: '4 horas' }).locator('input')).not.toBeChecked()
    await expect(page.locator('label').filter({ hasText: '1 dia' }).locator('input')).not.toBeChecked()
    await expect(page.getByText('Selecione ao menos um timeframe.')).toBeVisible()
  })
})

test.describe('card 952 — alinhamento ao proto', () => {
  test('desktop proto: defaults do rascunho novo', async ({ page }) => {
    await page.setViewportSize({ width: 1440, height: 900 })
    await page.goto(PROTOTYPE_PATH, { waitUntil: 'load' })
    await assertProtoNewDraftState(page)
    await page.getByText('4 horas').click()
    await expect(page.getByTestId('tf-4h')).toBeChecked()
  })

  test('mobile proto: defaults e sem overflow', async ({ page }) => {
    await page.setViewportSize({ width: 390, height: 844 })
    await page.goto(PROTOTYPE_PATH, { waitUntil: 'load' })
    await assertProtoNewDraftState(page)
    const overflow = await page.evaluate(
      () => document.documentElement.scrollWidth <= document.documentElement.clientWidth,
    )
    expect(overflow).toBe(true)
  })
})
