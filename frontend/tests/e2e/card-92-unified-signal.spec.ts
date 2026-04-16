import { expect, test } from '@playwright/test'

const AUTH_USER = {
  id: 'test-user',
  email: 'qa@test.com',
  name: 'QA User',
  isAdmin: false,
}

const DASHBOARD_PAYLOAD = {
  generated_at: '2026-04-14T19:00:00.000Z',
  insights: [],
  fear_greed: { value: 64, label: 'Greed', tone: 'bullish' },
  indicators: [],
  recent_signals: [
    {
      id: 'unified-btcusdt',
      asset: 'BTC/USDT',
      action: 'BUY',
      confidence: 88,
      reason: 'Consolidação em compra: apoio de AI Dashboard, Signals; conflito com On-chain.',
      direction: 'Compra',
      strength: 2,
      total_sources: 3,
      price: 97250,
      sources: [
        { source: 'AI Dashboard', action: 'BUY', confidence: 91, direction: 'Compra', status: 'supporting', reason: 'RSI 28.4 em sobrevenda' },
        { source: 'Signals', action: 'BUY', confidence: 88, direction: 'Compra', status: 'supporting', reason: 'RSI 40% · MACD 17% · Sentimento 22%' },
        { source: 'On-chain', action: 'SELL', confidence: 67, direction: 'Venda', status: 'conflicting', reason: 'Fluxo on-chain defensivo.' },
      ],
    },
    {
      id: 'unified-ethusdt',
      asset: 'ETH/USDT',
      action: 'HOLD',
      confidence: 0,
      reason: 'Sinal neutro por conflito entre fontes: AI Dashboard, On-chain.',
      direction: 'Neutro',
      strength: 1,
      total_sources: 3,
      price: 3520,
      sources: [
        { source: 'AI Dashboard', action: 'SELL', confidence: 74, direction: 'Venda', status: 'conflicting', reason: 'Perda de momentum.' },
        { source: 'Signals', action: 'HOLD', confidence: 55, direction: 'Neutro', status: 'neutral', reason: 'Sem gatilho técnico.' },
        { source: 'On-chain', action: 'BUY', confidence: 72, direction: 'Compra', status: 'conflicting', reason: 'Recuperação on-chain.' },
      ],
    },
  ],
  stats: { hit_rate: 62, total_signals: 2, avg_confidence: 72 },
  news: [],
  section_errors: {},
}

async function mockAuthenticatedSession(page: any) {
  await page.addInitScript((user) => {
    window.localStorage.setItem('auth_access_token', 'test-access-token')
    window.localStorage.setItem('auth_refresh_token', 'test-refresh-token')
    window.localStorage.setItem('auth_user', JSON.stringify(user))
  }, AUTH_USER)

  await page.route('**/api/auth/me', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(AUTH_USER),
    })
  })
}

async function mockUnifiedDashboard(page: any) {
  await page.route('**/api/ai/dashboard', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(DASHBOARD_PAYLOAD),
    })
  })
}

test('card #92 renders one consolidated signal per asset with source breakdown', async ({ page }) => {
  await mockAuthenticatedSession(page)
  await mockUnifiedDashboard(page)

  await page.goto('/ai-dashboard')

  await expect(page.getByText('AI Dashboard').first()).toBeVisible()
  await expect(page.getByText(/sinais unificados/i)).toBeVisible()
  await expect(page.getByTestId('ai-signal-card-btc-usdt')).toBeVisible()
  await expect(page.getByTestId('ai-signal-card-eth-usdt')).toBeVisible()
  await expect(page.getByTestId('ai-signal-card-btc-usdt')).toContainText('2/3')
  await expect(page.getByTestId('ai-signal-card-eth-usdt')).toContainText('1/3')

  await page.getByTestId('ai-signal-card-btc-usdt').locator('summary').click()

  await expect(page.getByTestId('ai-signal-card-btc-usdt')).toContainText('Fontes do sinal')
  await expect(page.getByTestId('ai-signal-card-btc-usdt-source-ai-dashboard')).toContainText('Confirma')
  await expect(page.getByTestId('ai-signal-card-btc-usdt-source-signals')).toContainText('Confirma')
  await expect(page.getByTestId('ai-signal-card-btc-usdt-source-on-chain')).toContainText('Conflita')
})

test('card #92 keeps deterministic conflict handling and remains usable on mobile', async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 })
  await mockAuthenticatedSession(page)
  await mockUnifiedDashboard(page)

  await page.goto('/ai-dashboard')

  await expect(page.getByTestId('ai-signal-card-eth-usdt')).toBeVisible()
  await expect(page.getByTestId('ai-signal-card-eth-usdt')).toContainText('HOLD')
  await expect(page.getByTestId('ai-signal-card-eth-usdt')).toContainText('Neutro')

  await page.getByTestId('ai-signal-card-eth-usdt').locator('summary').click()

  await expect(page.getByTestId('ai-signal-card-eth-usdt-source-ai-dashboard')).toBeVisible()
  await expect(page.getByTestId('ai-signal-card-eth-usdt-source-on-chain')).toBeVisible()
  await expect(page.getByTestId('ai-signal-card-eth-usdt-source-signals')).toBeVisible()
})

test('ai-dashboard hides legacy non-unified signals instead of rendering fake 0/0 cards', async ({ page }) => {
  await mockAuthenticatedSession(page)

  await page.route('**/api/ai/dashboard', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        generated_at: '2026-04-14T19:00:00.000Z',
        insights: [],
        fear_greed: { value: 64, label: 'Greed', tone: 'bullish' },
        indicators: [],
        recent_signals: [
          { id: 'legacy-1', asset: 'USDP/USDT', action: 'BUY', confidence: 67, reason: 'RSI 33.3 neutro + MACD bullish + Bollinger em banda superior' },
          { id: 'legacy-2', asset: 'HOME/USDT', action: 'BUY', confidence: 63, reason: 'RSI 30.6 neutro + MACD neutral + Bollinger em faixa média' },
        ],
        stats: { hit_rate: 62, total_signals: 2, avg_confidence: 72 },
        news: [],
        section_errors: {},
      }),
    })
  })

  await page.goto('/ai-dashboard')

  await expect(page.getByText(/itens legados de fonte única foram ocultados/i)).toBeVisible()
  await expect(page.getByText('USDP/USDT')).toHaveCount(0)
  await expect(page.getByText('0/0')).toHaveCount(0)
})
