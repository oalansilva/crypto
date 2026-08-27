import { expect, test, type Page } from '@playwright/test'

const AUTH_USER = {
  id: 'visual-qa-user',
  email: 'visual.qa@example.com',
  name: 'Visual QA',
  isAdmin: false,
  mustChangePassword: false,
}

const FIXED_NOW = new Date('2025-01-15T12:00:00.000Z')

const ANALYSIS_CANDLES = Array.from({ length: 80 }, (_, index) => ({
  timestamp_utc: new Date(Date.UTC(2024, 9, 28 + index)).toISOString(),
  open: 60_000 + index * 80,
  high: 60_500 + index * 80,
  low: 59_500 + index * 80,
  close: 60_200 + index * 80,
  volume: 1_000 + index * 10,
}))

const ANALYSIS_TRANSPARENCY = {
  status: 'available',
  timeframe: '1d',
  direction: 'long',
  display_name: 'BTC 1D Long — Médias: Virada Inicial',
  description: 'No BTC em 1D, abre Long quando a média curta cruza a longa e já se mantém acima dela; encerra no cruzamento baixista da média longa.',
  effective_parameters: { short_length: 16, medium_length: 17, long_length: 33, stop_loss: 0.085 },
  indicators: [
    { key: 'ema_short', label: 'EMA', parameters: { length: 16 }, type: 'ema', panel: 'price', scale: 'price', color: '#f6465d', function: 'Mostra a direção recente com maior peso nos preços atuais.', participation: ['entry', 'exit'], references: [], series: [], availability: 'unavailable', unavailable_reason: 'Série timestampada ainda não disponível.' },
    { key: 'sma_medium', label: 'SMA intermediária', parameters: { length: 17 }, type: 'sma', panel: 'price', scale: 'price', color: '#f0b90b', function: 'Suaviza o preço para tornar a tendência mais legível.', participation: ['entry'], references: [], series: [], availability: 'unavailable', unavailable_reason: 'Série timestampada ainda não disponível.' },
    { key: 'sma_long', label: 'SMA longa', parameters: { length: 33 }, type: 'sma', panel: 'price', scale: 'price', color: '#3b82f6', function: 'Suaviza o preço para tornar a tendência mais legível.', participation: ['entry', 'exit'], references: [], series: [], availability: 'unavailable', unavailable_reason: 'Série timestampada ainda não disponível.' },
  ],
  logic_blocks: [
    { participation: 'entry', description: 'Exige alinhamento entre as médias curta, intermediária e longa para confirmar tendência.', status: 'available' },
    { participation: 'exit', description: 'A perda do alinhamento entre as médias aciona a saída.', status: 'available' },
    { participation: 'risk', description: 'Stop de perda limitado a 8,50% por operação.', status: 'available' },
  ],
}

const FAVORITES = [
  {
    id: 1,
    name: 'BTC Core',
    symbol: 'BTC/USDT',
    timeframe: '1d',
    strategy_name: 'ema_rsi',
    strategy_display_name: 'BTC 1D Long — Médias: Virada Inicial',
    strategy_description: 'No BTC em 1D, abre Long quando a média curta cruza a longa e já se mantém acima dela; encerra no cruzamento baixista da média longa.',
    parameters: { ema_short: 9, ema_long: 21, direction: 'long' },
    metrics: {
      total_return: 0.12,
      total_return_pct: 12,
      total_trades: 3,
      win_rate: 0.66,
      sharpe_ratio: 1.4,
      max_drawdown: 0.05,
      trades: [],
    },
    notes: 'fixture visual estável',
    created_at: '2025-01-10T00:00:00Z',
    tier: 1,
    start_date: null,
    end_date: null,
  },
]

const OPPORTUNITIES = [
  {
    id: 1,
    symbol: 'BTC/USDT',
    timeframe: '1d',
    template_name: 'ema_rsi',
    strategy_display_name: 'RSI: Retomada com Força',
    strategy_description: 'Combina preço acima da média exponencial com recuperação do RSI para buscar retomadas compradoras; sai quando tendência ou força relativa cedem.',
    name: 'BTC Core',
    notes: 'fixture visual estável',
    tier: 1,
    parameters: { ema_short: 9, ema_long: 21 },
    is_holding: true,
    distance_to_next_status: 0.5,
    next_status_label: 'exit',
    status: 'HOLDING',
    message: 'Holding position',
    last_price: 65000,
    entry_price: 65500,
    stop_price: 62880,
    distance_to_stop_pct: 4,
    direction: 'long',
    timestamp: '2025-01-01T00:00:00Z',
    strategy_transparency: {
      status: 'available',
      timeframe: '1d',
      logic_blocks: [
        { participation: 'entry', description: 'Compra quando a média curta confirma força acima da média longa.', status: 'available' },
        { participation: 'exit', description: 'Vende quando a média curta perde força abaixo da média longa.', status: 'available' },
      ],
    },
    details: {},
  },
]

const PORTFOLIO_KPI = {
  pnl_today_pct: 2.5,
  pnl_today_vs_btc_pct: 0.8,
  drawdown_30d_pct: -3.1,
  drawdown_peak_date: '2025-01-10T00:00:00Z',
  btc_change_24h_pct: 1.7,
  total_usd: 17250,
  btc_value: 16250,
  usdt_value: 1000,
  eth_value: 0,
  other_usd: 0,
  _history_insufficient: false,
}

async function blockExternalNetwork(page: Page) {
  await page.route('**/*', (route) => {
    const url = new URL(route.request().url())
    if (url.hostname === '127.0.0.1' || url.hostname === 'localhost') {
      return route.continue()
    }
    return route.abort('blockedbyclient')
  })
}

async function setAuthenticatedSession(page: Page) {
  await page.addInitScript((user) => {
    window.localStorage.setItem('auth_access_token', 'visual-qa-token')
    window.localStorage.setItem('auth_refresh_token', 'visual-qa-refresh-token')
    window.localStorage.setItem('auth_user', JSON.stringify(user))
  }, AUTH_USER)
}

async function installStableApiMocks(page: Page) {
  await blockExternalNetwork(page)
  await setAuthenticatedSession(page)

  const preferences = {
    __global__: { in_portfolio: false, card_mode: 'price', price_timeframe: '1d', theme: 'dark-green' },
    'BTC/USDT': { in_portfolio: true, card_mode: 'price', price_timeframe: '1d', theme: 'dark-green' },
  }

  await page.route('**/api/auth/me', (route) =>
    route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(AUTH_USER) }),
  )
  await page.route('**/api/favorites/', (route) =>
    route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(FAVORITES) }),
  )
  await page.route('**/api/favorites/1/trades', (route) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        favorite_id: 1,
        trades: [],
        metrics: { ...FAVORITES[0].metrics, analysis_candles: ANALYSIS_CANDLES, analysis_strategy_transparency: ANALYSIS_TRANSPARENCY },
        metrics_match: true,
        metrics_deltas: {},
        regenerated: true,
        candles: ANALYSIS_CANDLES,
        indicator_data: {},
        execution_mode: 'visual_fixture',
        strategy_transparency: ANALYSIS_TRANSPARENCY,
      }),
    }),
  )
  await page.route('**/api/opportunities/**', (route) =>
    route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(OPPORTUNITIES) }),
  )
  await page.route('**/api/monitor/preferences', (route) =>
    route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(preferences) }),
  )
  await page.route('**/api/monitor/preferences/*', (route) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ in_portfolio: true, card_mode: 'price', price_timeframe: '1d', theme: 'dark-green' }),
    }),
  )
  await page.route('**/api/user/binance-credentials', (route) =>
    route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ configured: false, api_key_masked: null }) }),
  )
  await page.route('**/api/users/me/telegram-settings', (route) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        telegramUsername: null,
        telegramAlertsEnabled: false,
        linked: false,
        linkedAt: null,
        usernameMismatch: false,
        botUsername: 'criptofarol_bot',
        hasPendingLinkToken: false,
      }),
    }),
  )
  await page.route('**/api/monitor/spot-market-orders/eligibility', (route) => {
    const body = route.request().postDataJSON() as { symbols?: string[] } | null
    return route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        items: (body?.symbols ?? []).map((symbol) => ({
          symbol: symbol.replace(/[^a-zA-Z0-9]/g, '').toUpperCase(),
          eligible: true,
          reason: null,
        })),
      }),
    })
  })
  await page.route('**/api/monitor/spot-stop-order**', (route) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ protected: false, symbol: 'BTCUSDT', client_order_id: 'cfstop_visual', order: null }),
    }),
  )
  await page.route('**/api/external/binance/spot/balances**', (route) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        balances: [
          { asset: 'BTC', free: 0.25, locked: 0, total: 0.25, price_usdt: 65000, value_usd: 16250, avg_cost_usdt: 60000, pnl_usd: 1250, pnl_pct: 8.33 },
          { asset: 'USDC', free: 1000, locked: 0, total: 1000, price_usdt: 1, value_usd: 1000, avg_cost_usdt: 1, pnl_usd: 0, pnl_pct: 0 },
        ],
        total_usd: 17250,
      }),
    }),
  )
  await page.route('**/api/portfolio/kpi', (route) =>
    route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(PORTFOLIO_KPI) }),
  )
  await page.route('**/api/market/candles**', (route) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        candles: [
          { timestamp_utc: '2025-01-01T00:00:00Z', open: 64000, high: 65500, low: 63500, close: 65000, volume: 1000 },
          { timestamp_utc: '2025-01-02T00:00:00Z', open: 65000, high: 66000, low: 64500, close: 65500, volume: 1200 },
        ],
      }),
    }),
  )
  await page.route('**/api/health', (route) =>
    route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ status: 'ok', service: 'crypto-api' }) }),
  )
  await page.route('**/api/workflow/kanban/changes?project_slug=crypto', (route) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        items: [
          {
            id: 'visual-qa',
            title: 'Validação visual automática',
            card_number: 284,
            path: 'openspec/changes/card-284-automated-qa-gate/proposal.md',
            status: {},
            archived: false,
            column: 'Aprovação de Design',
            position: 0,
            item_type: 'change',
            ui_impact: 'affected',
            design_ref: 'openspec/changes/card-284-automated-qa-gate/design.md',
            design_digest: 'visual-design-digest',
            prototype_ref: 'frontend/public/prototypes/card-284-automated-qa-gate/index.html',
            prototype_digest: 'visual-prototype-digest',
            design_critique_verdict: 'PASS',
            design_delivered_at: '2025-01-15T10:00:00Z',
          },
        ],
      }),
    }),
  )
  await page.route('**/api/workflow/projects/crypto/changes/*', (route) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        id: 'visual-qa',
        project_id: 'crypto',
        change_id: 'visual-qa',
        title: 'Validação visual automática',
        status: 'Aprovação de Design',
        card_number: 284,
        created_at: '2025-01-01T00:00:00Z',
        updated_at: '2025-01-01T00:00:00Z',
      }),
    }),
  )
  await page.route('**/api/workflow/kanban/changes/*/tasks?project_slug=crypto', (route) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ change_id: 'visual-qa', path: 'openspec/changes/visual-qa/tasks.md', sections: [] }),
    }),
  )
  await page.route('**/api/workflow/kanban/changes/*/comments?project_slug=crypto', (route) =>
    route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ change_id: 'visual-qa', items: [] }) }),
  )
  await page.route('**/api/workflow/projects/crypto/changes/*/tasks', (route) =>
    route.fulfill({ status: 200, contentType: 'application/json', body: '[]' }),
  )
  await page.route('**/api/market/prices', (route) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ prices: [{ symbol: 'BTCUSDT', price: 65000, change_24h_pct: 2.4 }], fetched_at: '2025-01-01T00:00:00Z' }),
    }),
  )
}

async function capture(page: Page, name: string) {
  await expect(page).toHaveScreenshot(name, {
    animations: 'disabled',
    caret: 'hide',
    fullPage: true,
  })
}

test.beforeEach(async ({ page }) => {
  await page.clock.install({ time: FIXED_NOW })
})

test('visual critical login', async ({ page }) => {
  await blockExternalNetwork(page)
  await page.goto('/login')
  await expect(page.getByRole('heading', { name: 'Bem-vindo de volta' })).toBeVisible()
  await capture(page, 'login.png')
})

test('visual critical home', async ({ page }) => {
  await installStableApiMocks(page)
  await page.goto('/home')
  await expect(page.getByRole('heading', { name: 'Seu snapshot diário de crypto' })).toBeVisible()
  await expect(page.getByTestId('home-kpi-pnl').getByText('+2.50%')).toBeVisible()
  await expect(page.getByText('Bitcoin', { exact: true })).toBeVisible()
  await page.clock.runFor(2_000)
  await capture(page, 'home.png')
})

test('visual critical monitor', async ({ page }) => {
  await installStableApiMocks(page)
  await page.goto('/monitor')
  await expect(page.getByTestId('monitor-status-tab')).toBeVisible()
  await expect(page.locator('[data-testid="open-spot-trade-btc-usdt"]:visible').first()).toBeVisible()
  await capture(page, 'monitor.png')
})

test('visual critical monitor trade explanation', async ({ page }) => {
  await installStableApiMocks(page)
  await page.route('**/api/monitor/preferences', (route) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        __global__: { in_portfolio: false, card_mode: 'strategy', price_timeframe: '1d', theme: 'dark-green' },
        'BTC/USDT': { in_portfolio: true, card_mode: 'strategy', price_timeframe: '1d', theme: 'dark-green' },
      }),
    }),
  )
  await page.route('**/api/favorites/1/trades', (route) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        trades: [{
          entry_time: '2025-01-02T00:00:00Z',
          entry_price: 65500,
          type: 'long',
          entry_explanation: {
            status: 'available', direction: 'long', timeframe: '1d', action: 'Compra', trigger: 'entry_rule',
            summary: 'Compra confirmada após a média curta cruzar acima da média longa.',
            decision_candle_time: '2025-01-01T00:00:00Z', execution_time: '2025-01-02T00:00:00Z', execution_price: 65500,
            evidence: [{ key: 'ema_short', label: 'EMA curta', value: 65220, timestamp_utc: '2025-01-01T00:00:00Z', state: 'confirmed' }],
          },
          current_state_explanation: {
            status: 'available', direction: 'long', timeframe: '1d', action: 'Compra ativa', trigger: 'open_position',
            summary: 'A posição continua aberta porque a regra de saída ainda não foi confirmada.',
            rule_summary: 'Venda quando a média curta cruzar abaixo da média longa.',
            risk_summary: 'Stop de proteção 4,00% abaixo da entrada.',
            decision_candle_time: '2025-01-02T00:00:00Z',
            evidence: [{ key: 'ema_long', label: 'EMA longa', value: 64800, timestamp_utc: '2025-01-02T00:00:00Z', state: 'pending' }],
          },
        }],
        metrics: { total_trades: 0, win_rate: 0, total_return: 0, avg_profit: 0 },
      }),
    }),
  )

  await page.goto('/monitor')
  const dismissOnboarding = page.getByRole('button', { name: 'Dispensar' })
  if (await dismissOnboarding.isVisible()) {
    await dismissOnboarding.click()
  }
  await page.getByRole('button', { name: 'Ver Trades' }).click()
  const dialog = page.getByRole('dialog')
  await expect(dialog.getByRole('button', { name: 'Ver decisão da operação' })).toHaveCount(0)
  await expect(dialog.getByTestId(/trade-explanation/)).toHaveCount(0)
  await expect(dialog.getByText('Por que continua aberto')).toHaveCount(0)
  await expect(dialog.getByText('Como funciona a estratégia')).toHaveCount(0)
  await expect(dialog.getByText('Estas regras não mudam com a posição atual do trade.')).toHaveCount(0)
  await expect(page).toHaveScreenshot('monitor-trade-explanation.png', {
    animations: 'disabled',
    caret: 'hide',
    fullPage: false,
  })
})

test('visual critical favorites', async ({ page }) => {
  await installStableApiMocks(page)
  await page.goto('/favorites')
  await expect(page.getByRole('heading', { name: 'Estratégias favoritas' })).toBeVisible()
  await capture(page, 'favorites.png')
})

test('visual critical favorite analysis', async ({ page }) => {
  await installStableApiMocks(page)
  await page.goto('/favorites')
  const dismissOnboarding = page.getByRole('button', { name: 'Dispensar' })
  if (await dismissOnboarding.isVisible()) {
    await dismissOnboarding.click()
  }
  await page.locator('button[title="Ver análise completa"]:visible').click()
  await expect(page.getByTestId('combo-result-summary')).toBeVisible()
  await expect(page.getByText('Parâmetros efetivos')).toBeHidden()
  expect(await page.evaluate(() => document.documentElement.scrollWidth > document.documentElement.clientWidth + 1)).toBe(false)
  await capture(page, 'favorite-analysis.png')
})

test('visual critical wallet', async ({ page }) => {
  await installStableApiMocks(page)
  await page.goto('/external/balances')
  await expect(page.getByRole('heading', { name: 'Carteira', exact: true })).toBeVisible()
  await capture(page, 'wallet.png')
})

test('visual critical profile', async ({ page }) => {
  await installStableApiMocks(page)
  await page.route('**/api/users/me', (route) =>
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        ...AUTH_USER,
        createdAt: '2025-01-01T00:00:00Z',
        lastLogin: '2025-01-15T12:00:00Z',
      }),
    }),
  )
  await page.goto('/profile')
  await expect(page.getByRole('heading', { name: 'Meu Perfil', exact: true })).toBeVisible()
  await expect(page.getByText('Credenciais Binance')).toBeVisible()
  await expect(page.getByTestId('telegram-alerts-form')).toBeVisible()
  await capture(page, 'profile.png')
})
