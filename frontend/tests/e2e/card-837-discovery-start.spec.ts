import { expect, test, type Page } from '@playwright/test'

// Card #837 — "Reload after cancel does not pin to the old run"
// (openspec/specs/discovery-sweep/spec.md; tasks 3.4, 4.1, 4.2).
// Rota /combo/discovery: após reload pós-cancelar, montar outra seleção e
// clicar Iniciar cria UMA varredura nova — sem segundo botão e sem limpar
// dados do navegador. testids `live-block-note` / `start-error` já existem.

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
  raw_total: 2,
  exclusions: {},
  excluded_count: 0,
  valid_total: 2,
  limits: { max_total: 1000 },
  errors: {},
  expires_at: '2026-09-05T13:00:00Z',
  snapshot_token: 'snapshot-token-837',
  snapshot_hash: '837abcdef837abcdef837abcdef837abcdef837abcdef837abcdef837abcdef',
  period_type: '2y',
  start_date: '2024-01-01',
  end_date: '2024-12-31',
}

const CANCELLED_ID = 'deadbeefdeadbeefdeadbeefdeadbeef'
const NEW_ID = '83700000000000000000000000000837'

const CANCELLED = {
  sweep_id: CANCELLED_ID,
  state: 'cancelled',
  total: 2,
  succeeded: 0,
  failed: 0,
  skipped: 2,
  processed: 2,
  terminal_reason: null,
  terminal_code: null,
  draft_key: 'draft-837-dead',
  snapshot: SNAPSHOT,
  updated_at: '2026-09-05T00:40:00Z',
}

const NEW_SWEEP = {
  sweep_id: NEW_ID,
  state: 'running',
  total: 2,
  succeeded: 0,
  failed: 0,
  skipped: 0,
  processed: 0,
  terminal_reason: null,
  terminal_code: null,
  draft_key: 'draft-837-new',
  snapshot: SNAPSHOT,
  updated_at: '2026-09-05T00:41:00Z',
}

async function installStartMocks(page: Page, phase: { active: unknown[] }) {
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
  await page.route('**/api/combos/discovery/sweeps/active', (route) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ sweeps: phase.active }),
    }),
  )
  await page.route('**/api/combos/discovery/sweeps/history', (route) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        sweeps: [
          {
            sweep_id: CANCELLED_ID,
            state: 'cancelled',
            total: 2,
            processed: 2,
            succeeded: 0,
            failed: 0,
            skipped: 2,
            snapshot_hash: SNAPSHOT.snapshot_hash,
            created_at: '2026-09-04T14:00:00Z',
          },
        ],
      }),
    }),
  )
  await page.route('**/api/combos/discovery/sweeps', (route) => {
    if (route.request().method() !== 'POST') return route.fallback()
    return route.fulfill({
      status: 201,
      contentType: 'application/json',
      body: JSON.stringify({
        sweep_id: NEW_ID,
        state: 'running',
        total: 2,
        idempotency_key: 'draft-837-new',
      }),
    })
  })
  await page.route(`**/api/combos/discovery/sweeps/${CANCELLED_ID}`, (route) =>
    route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(CANCELLED) }),
  )
  await page.route(`**/api/combos/discovery/sweeps/${NEW_ID}`, (route) =>
    route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(NEW_SWEEP) }),
  )
  await page.route('**/api/combos/discovery/sweeps/*/leaderboard**', (route) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ results: [], total: 0, unfiltered_total: 0, offset: 0, limit: 3 }),
    }),
  )
}

test('card 837 — reload após cancelar não prende à run morta; Iniciar cria varredura nova', async ({
  page,
}) => {
  await page.setViewportSize({ width: 1440, height: 1000 })
  const phase: { active: unknown[] } = { active: [CANCELLED] }
  await installStartMocks(page, phase)
  await page.goto('/combo/discovery')

  // Run morta reconciliada: sem bloco de progresso ativo, rascunho liberado.
  await expect(page.getByTestId('sweep-progress')).toHaveCount(0)
  await expect(page.getByTestId('start-sweep')).toBeEnabled()

  // Reload pós-cancelar: o servidor já não tem ativo; a tela continua livre.
  phase.active = []
  await page.reload()
  await expect(page.getByTestId('sweep-progress')).toHaveCount(0)
  await expect(page.getByTestId('start-sweep')).toBeEnabled()

  // Monta outra seleção (desmarca 1d) e inicia: nasce UMA varredura nova.
  await page.getByText('1 dia').click()
  await expect(page.getByTestId('start-sweep')).toBeEnabled()
  await page.getByTestId('start-sweep').click()

  await expect(page.getByTestId('sweep-progress')).toBeVisible()
  await expect(page.getByTestId('sweep-progress')).toContainText(NEW_ID)
  // Sem segundo botão de início e sem erro operacional na tela.
  await expect(page.getByTestId('start-sweep')).toHaveCount(1)
  await expect(page.getByTestId('live-block-note')).toHaveCount(0)
  await expect(page.getByTestId('start-error')).toHaveCount(0)

  // Nenhuma limpeza de dados do navegador no caminho.
  const token = await page.evaluate(() => localStorage.getItem('auth_access_token'))
  expect(token).toBe('discovery-admin-token')
  const draftKey = await page.evaluate(() =>
    sessionStorage.getItem('discovery-draft-idempotency-key'),
  )
  expect(draftKey).toBeTruthy()
})

test('card 837 — outra seleção com live em curso mostra orientação sem duplicar', async ({
  page,
}) => {
  await page.setViewportSize({ width: 1440, height: 1000 })
  const phase: { active: unknown[] } = {
    active: [{ ...NEW_SWEEP, state: 'running' }],
  }
  await installStartMocks(page, phase)
  await page.goto('/combo/discovery')

  await expect(page.getByTestId('sweep-progress')).toBeVisible()
  // Seleção da tela diverge da live (mock tem 4h+1d; desmarca 1d): bloqueio
  // orientado aparece e nenhum erro técnico é exposto.
  await page.getByText('1 dia').click()
  await expect(page.getByTestId('live-block-note')).toBeVisible()
  await expect(page.getByTestId('live-block-note')).toContainText('Cancele')
  await expect(page.getByTestId('start-error')).toHaveCount(0)
})
