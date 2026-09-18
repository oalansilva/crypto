import { expect, test, type Page } from '@playwright/test'
import { readFile } from 'node:fs/promises'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
import { ACTIVE_RESTORE_MAX_ATTEMPTS } from '../../src/lib/discoveryActiveRestoreConfig'

const ADMIN_USER = {
  id: 'discovery-admin',
  email: 'alan@example.com',
  name: 'Alan Silva',
  isAdmin: true,
  mustChangePassword: false,
}

const SNAPSHOT = {
  axes: {
    templates: ['multi_ma_crossover'],
    symbols: ['BTC/USDT'],
    timeframes: ['4h', '1d'],
    directions: ['long'],
  },
  raw_total: 24,
  exclusions: {},
  excluded_count: 0,
  valid_total: 24,
  limits: { max_total: 1000 },
  errors: {},
  expires_at: '2026-09-17T13:00:00Z',
  snapshot_token: 'snapshot-token-967',
  snapshot_hash: '967abcdef967abcdef967abcdef967abcdef967abcdef967abcdef967abcdef',
  period_type: 'all',
}

const ACTIVE = {
  sweep_id: 'c91f3a07b6e24d8a9f51c2e8470b3d16',
  state: 'running',
  total: 24,
  succeeded: 10,
  failed: 0,
  skipped: 0,
  processed: 12,
  terminal_reason: null,
  terminal_code: null,
  draft_key: 'draft-967-restore',
  snapshot: SNAPSHOT,
  updated_at: '2026-09-17T00:40:00Z',
}

const ACTIVE_NO_AXES = {
  ...ACTIVE,
  snapshot: {
    ...SNAPSHOT,
    axes: undefined,
  },
}

async function installDiscoveryMocks(
  page: Page,
  opts: {
    activePayload?: typeof ACTIVE | typeof ACTIVE_NO_AXES
    failActiveUntil?: number
    /** Chamadas GET /sweeps/:id antes de devolver payload com axes (poll). */
    sweepDetailCallsBeforeAxes?: number
  } = {},
) {
  const activePayload = opts.activePayload ?? ACTIVE
  let activeCalls = 0
  let sweepDetailCalls = 0
  const failUntil = opts.failActiveUntil ?? 0
  const axesAfterCalls = opts.sweepDetailCallsBeforeAxes ?? 0

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
      body: JSON.stringify({
        prebuilt: [{ name: 'multi_ma_crossover', display_name: 'Médias', description: 'x' }],
        examples: [],
        custom: [],
      }),
    }),
  )
  await page.route('**/api/exchanges/binance/symbols', (route) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ symbols: ['BTC/USDT', 'ETH/USDT'] }),
    }),
  )
  await page.route('**/api/combos/discovery/sweeps/preflight', (route) =>
    route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(SNAPSHOT) }),
  )
  await page.route('**/api/combos/discovery/sweeps/history', (route) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        sweeps: [
          {
            sweep_id: activePayload.sweep_id,
            state: activePayload.state,
            total: activePayload.total,
            processed: activePayload.processed,
            succeeded: activePayload.succeeded,
            failed: activePayload.failed,
            skipped: activePayload.skipped,
            snapshot_hash: SNAPSHOT.snapshot_hash,
            created_at: '2026-09-16T14:00:00Z',
          },
        ],
      }),
    }),
  )
  await page.route('**/api/combos/discovery/sweeps/active', (route) => {
    activeCalls += 1
    if (activeCalls <= failUntil) {
      return route.fulfill({ status: 500, contentType: 'application/json', body: JSON.stringify({ detail: 'down' }) })
    }
    return route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ sweeps: [activePayload] }),
    })
  })
  await page.route(`**/api/combos/discovery/sweeps/${ACTIVE.sweep_id}/leaderboard**`, (route) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ results: [], total: 0, unfiltered_total: 0, offset: 0, limit: 5 }),
    }),
  )
  await page.route(`**/api/combos/discovery/sweeps/${ACTIVE.sweep_id}`, (route) => {
    sweepDetailCalls += 1
    const detailPayload =
      axesAfterCalls > 0 && sweepDetailCalls > axesAfterCalls ? ACTIVE : activePayload
    return route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(detailPayload),
    })
  })
}

function trackBrowserErrors(page: Page) {
  const errors: string[] = []
  page.on('console', (message) => {
    if (message.type() !== 'error') return
    const text = message.text()
    if (text.includes('status of 500')) return
    errors.push(`console: ${text}`)
  })
  page.on('pageerror', (error) => errors.push(`page: ${error.message}`))
  return errors
}

async function assertMontarLandmarks(page: Page) {
  await page.locator('[data-mode-tab="montar"]').click()
  await expect(page.getByTestId('mode-montar')).toBeVisible()
  await expect(page.getByText('Preflight', { exact: true })).toBeVisible()
  await expect(page.getByText('Rascunho de varredura', { exact: true })).toBeVisible()
}

async function assertHappyDiscoveryLandmarks(page: Page) {
  await expect(page.getByRole('heading', { name: /Descoberta de estratégias swing/i })).toBeVisible()
  await expect(page.getByTestId('sweep-progress')).toBeVisible()
  await expect(page.getByTestId('progress-count')).toContainText('12 de 24')
  await expect(page.getByTestId('mode-acomp')).toBeVisible()
  await expect(page.getByText('Não foi possível verificar a varredura ativa')).toHaveCount(0)
  await expect(page.getByTestId('recovery-retry')).toHaveCount(0)
  await assertMontarLandmarks(page)
}

test.describe('card 967 — reconstituição automática do Acompanhar', () => {
  test('GET activo falha uma vez e o retry automático hidrata sem clique', async ({ page }) => {
    test.setTimeout(60_000)
    const errors = trackBrowserErrors(page)
    await page.setViewportSize({ width: 1440, height: 900 })
    await installDiscoveryMocks(page, { failActiveUntil: 1 })
    await page.goto('/combo/discovery')
    await expect(page.getByTestId('sweep-progress')).toBeVisible({ timeout: 15_000 })
    await expect(page.locator('[data-mode-tab="acomp"]')).toContainText('c91f3a07')
    await assertHappyDiscoveryLandmarks(page)
    expect(errors).toEqual([])
  })

  test('payload sem axes ainda mostra sweep_id e progresso', async ({ page }) => {
    const errors = trackBrowserErrors(page)
    await page.setViewportSize({ width: 1440, height: 900 })
    await installDiscoveryMocks(page, { activePayload: ACTIVE_NO_AXES })
    await page.goto('/combo/discovery')
    await expect(page.getByTestId('progress-count')).toContainText('12 de 24')
    await expect(page.getByTestId('mode-acomp')).toContainText('c91f3a07')
    await expect(page.getByText('Não foi possível verificar a varredura ativa')).toHaveCount(0)
    expect(errors).toEqual([])
  })

  test('poll hidrata axes tardios e congela rascunho', async ({ page }) => {
    test.setTimeout(60_000)
    const errors = trackBrowserErrors(page)
    await page.setViewportSize({ width: 1440, height: 900 })
    await installDiscoveryMocks(page, {
      activePayload: ACTIVE_NO_AXES,
      sweepDetailCallsBeforeAxes: 1,
    })
    await page.goto('/combo/discovery')
    await expect(page.getByTestId('progress-count')).toContainText('12 de 24')
    await page.locator('[data-mode-tab="montar"]').click()
    await expect(page.getByText('Editável · preflight server-side atualizado')).toBeVisible({ timeout: 3000 })
    await expect(page.getByText('CONGELADO', { exact: true })).toBeVisible({ timeout: 12_000 })
    await expect(page.getByText('Congelado pelo snapshot ativo')).toBeVisible()
    expect(errors).toEqual([])
  })

  test('residual só após teto — banner vermelho, retry e start bloqueado', async ({ page }) => {
    test.setTimeout(60_000)
    await page.setViewportSize({ width: 1440, height: 900 })
    // StrictMode remonta o efeito de restore — reserva folga acima do teto automático.
    await installDiscoveryMocks(page, { failActiveUntil: ACTIVE_RESTORE_MAX_ATTEMPTS * 3 })
    await page.goto('/combo/discovery')
    await expect(page.getByTestId('recovery-retry')).toBeVisible({ timeout: 20_000 })
    await expect(page.getByText('Não foi possível verificar a varredura ativa')).toBeVisible()
    await expect(page.getByTestId('start-sweep')).toBeDisabled()
  })
})

test.describe('card 967 — gate proto vs rota (layout)', () => {
  const protoPath = '/prototypes/card-967-discovery-recupera-varredura-ativa/'

  async function assertProtoLandmarks(page: Page) {
    await expect(page.getByRole('heading', { name: /Descoberta de estratégias swing/i })).toBeVisible()
    await expect(page.getByText('12 de 24')).toBeVisible()
    await expect(page.getByText('Não foi possível verificar a varredura ativa')).toHaveCount(0)
    await page.locator('[data-mode="montar"]').click()
    await expect(page.getByText('Preflight', { exact: true })).toBeVisible()
    await expect(page.getByText('Rascunho de varredura', { exact: true })).toBeVisible()
  }

  for (const viewport of [
    { width: 1440, height: 900, label: 'desktop' },
    { width: 390, height: 844, label: 'mobile' },
  ]) {
    test(`${viewport.label} — proto e rota alinhados ao caminho feliz`, async ({ page }) => {
      test.setTimeout(60_000)
      const errors = trackBrowserErrors(page)
      await page.setViewportSize({ width: viewport.width, height: viewport.height })

      await page.goto(protoPath, { waitUntil: 'load' })
      await assertProtoLandmarks(page)

      await installDiscoveryMocks(page)
      await page.goto('/combo/discovery')
      await assertHappyDiscoveryLandmarks(page)
      expect(errors).toEqual([])
    })
  }
})

test('card 967 — constante de teto exportada', async () => {
  const __dirname = path.dirname(fileURLToPath(import.meta.url))
  const source = await readFile(path.resolve(__dirname, '../../src/lib/discoveryActiveRestoreConfig.ts'), 'utf8')
  expect(source).toContain('ACTIVE_RESTORE_MAX_ATTEMPTS')
  expect(ACTIVE_RESTORE_MAX_ATTEMPTS).toBeGreaterThanOrEqual(3)
})
