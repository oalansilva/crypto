import { expect, test, type Page } from '@playwright/test'

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
  raw_total: 28,
  exclusions: {},
  excluded_count: 0,
  valid_total: 28,
  limits: { max_total: 1000 },
  errors: {},
  expires_at: '2026-08-23T13:00:00Z',
  snapshot_token: 'snapshot-token-664',
  snapshot_hash: '5447abcdef5447abcdef5447abcdef5447abcdef5447abcdef5447abcdef5447',
  period_type: '2y',
}

const ACTIVE = {
  sweep_id: 'fd40d0c9f58d4cf28574951b2b3bbbb5',
  state: 'running',
  total: 28,
  succeeded: 21,
  failed: 0,
  skipped: 0,
  processed: 21,
  terminal_reason: null,
  terminal_code: null,
  draft_key: 'draft-664-restore',
  snapshot: SNAPSHOT,
  updated_at: '2026-08-23T00:40:00Z',
}

async function installRestoreMocks(page: Page, initial: typeof ACTIVE) {
  let sweep = { ...initial }
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
  await page.route('**/api/combos/discovery/sweeps/active', (route) => {
    const terminal = ['completed', 'failed', 'cancelled', 'partial_failure'].includes(sweep.state)
    return route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ sweeps: terminal ? [] : [sweep] }),
    })
  })
  await page.route('**/api/combos/discovery/sweeps/history', (route) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        sweeps: [
          {
            sweep_id: sweep.sweep_id,
            state: sweep.state,
            total: sweep.total,
            processed: sweep.processed,
            succeeded: sweep.succeeded,
            failed: sweep.failed,
            skipped: sweep.skipped,
            snapshot_hash: SNAPSHOT.snapshot_hash,
            created_at: '2026-08-22T14:00:00Z',
          },
        ],
      }),
    }),
  )
  await page.route(`**/api/combos/discovery/sweeps/${sweep.sweep_id}/pause`, (route) => {
    sweep = { ...sweep, state: 'paused' }
    return route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(sweep) })
  })
  await page.route(`**/api/combos/discovery/sweeps/${sweep.sweep_id}/resume`, (route) => {
    sweep = { ...sweep, state: 'running', processed: sweep.processed + 1, succeeded: sweep.succeeded + 1 }
    return route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ ...sweep, wake_up_state: 'pending', dispatch_status: 'queued' }),
    })
  })
  await page.route(`**/api/combos/discovery/sweeps/${sweep.sweep_id}/leaderboard**`, (route) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ results: [], total: 0, unfiltered_total: 0, offset: 0, limit: 3 }),
    }),
  )
  await page.route(`**/api/combos/discovery/sweeps/${sweep.sweep_id}`, (route) =>
    route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(sweep) }),
  )
}

test('card 664 — reload reconstitui o sweep ativo e não o terminal', async ({ page }) => {
  await page.setViewportSize({ width: 1440, height: 1000 })
  await installRestoreMocks(page, ACTIVE)
  await page.goto('/combo/discovery')
  await expect(page.getByTestId('sweep-progress')).toBeVisible()
  await expect(page.getByTestId('progress-count')).toContainText('21 de 28')
  await expect(page.getByTestId('active-state-chip')).toHaveText('RUNNING')
  await expect(page.getByTestId('start-sweep')).toBeDisabled()
  await expect(page.getByTestId('recovery-banner')).toBeVisible()

  await page.reload()
  await expect(page.getByTestId('sweep-progress')).toBeVisible()
  await expect(page.getByTestId('progress-count')).toContainText('21 de 28')
  await expect(page.locator('#draft-status')).toContainText('Congelado')

  await installRestoreMocks(page, { ...ACTIVE, state: 'completed', processed: 28, succeeded: 28 })
  await page.reload()
  await expect(page.getByTestId('sweep-progress')).toHaveCount(0)
  await expect(page.getByTestId('start-sweep')).toBeEnabled()
})

test('card 664 — pausar, recarregar e retomar avança processed', async ({ page }) => {
  await installRestoreMocks(page, ACTIVE)
  await page.goto('/combo/discovery')
  await page.getByTestId('pause-sweep').click()
  await expect(page.getByTestId('active-state-chip')).toHaveText('PAUSED')
  await expect(page.getByRole('button', { name: 'Retomar' })).toBeVisible()

  await page.reload()
  await expect(page.getByTestId('active-state-chip')).toHaveText('PAUSED')
  await page.getByRole('button', { name: 'Retomar' }).click()
  await expect(page.getByTestId('active-state-chip')).toHaveText('RUNNING')
  await expect(page.getByTestId('progress-count')).toContainText('22 de 28')
})

test('card 664 — mobile sem overflow com sweep recuperado', async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 })
  await installRestoreMocks(page, { ...ACTIVE, state: 'paused' })
  await page.goto('/combo/discovery')
  await expect(page.getByTestId('sweep-progress')).toBeVisible()
  await expect(page.getByRole('button', { name: 'Retomar' })).toBeVisible()
  const overflow = await page.evaluate(
    () => document.documentElement.scrollWidth > document.documentElement.clientWidth,
  )
  expect(overflow).toBe(false)
})

test('card 664 — erro de recuperação com retry restaura o painel', async ({ page }) => {
  await page.setViewportSize({ width: 1440, height: 1000 })
  let activeCalls = 0
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
      body: JSON.stringify({ prebuilt: [{ name: 'multi_ma_crossover', display_name: 'Médias', description: 'x' }], examples: [], custom: [] }),
    }),
  )
  await page.route('**/api/exchanges/binance/symbols', (route) =>
    route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ symbols: ['BTC/USDT'] }) }),
  )
  await page.route('**/api/combos/discovery/sweeps/preflight', (route) =>
    route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(SNAPSHOT) }),
  )
  await page.route('**/api/combos/discovery/sweeps/history', (route) =>
    route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ sweeps: [] }) }),
  )
  await page.route('**/api/combos/discovery/sweeps/active', (route) => {
    activeCalls += 1
    if (activeCalls < 3) {
      return route.fulfill({ status: 500, contentType: 'application/json', body: JSON.stringify({ detail: 'down' }) })
    }
    return route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ sweeps: [ACTIVE] }),
    })
  })
  await page.route(`**/api/combos/discovery/sweeps/${ACTIVE.sweep_id}/leaderboard**`, (route) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ results: [], total: 0, unfiltered_total: 0, offset: 0, limit: 3 }),
    }),
  )
  await page.goto('/combo/discovery')
  await expect(page.getByTestId('recovery-retry')).toBeVisible()
  await expect(page.getByTestId('start-sweep')).toBeDisabled()
  await page.getByTestId('recovery-retry').click()
  await expect(page.getByTestId('sweep-progress')).toBeVisible()
  await expect(page.locator('#progress-heading')).toBeFocused()
})
