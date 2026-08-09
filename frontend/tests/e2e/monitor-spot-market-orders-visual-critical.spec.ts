import { expect, test } from '@playwright/test'

const user = {
  id: 'spot-market-visual-user',
  email: 'visual@example.com',
  name: 'Visual User',
  isAdmin: false,
  mustChangePassword: false,
}

const opportunity = {
  id: 385,
  symbol: 'BTC/USDT',
  asset_type: 'cryptomoeda',
  timeframe: '1d',
  direction: 'long',
  template_name: 'ema',
  name: 'BTC Long',
  notes: '',
  tier: 1,
  is_holding: true,
  distance_to_next_status: 1,
  next_status_label: 'exit',
  status: 'HOLDING',
  last_price: 65000,
  timestamp: '2026-08-06T00:00:00Z',
  entry_price: 62000,
  stop_price: 61000,
  distance_to_stop_pct: 6.1,
  parameters: {},
  signal_history: [],
  details: {},
}

test('painel de confirmação Spot preserva o Monitor em desktop e mobile', async ({ page }) => {
  await page.addInitScript((authenticatedUser) => {
    window.localStorage.setItem('auth_access_token', 'test-access-token')
    window.localStorage.setItem('auth_refresh_token', 'test-refresh-token')
    window.localStorage.setItem('auth_user', JSON.stringify(authenticatedUser))
  }, user)

  await page.route('**/api/**', async (route) => {
    const request = route.request()
    const path = new URL(request.url()).pathname
    let payload: unknown = {}

    if (path.endsWith('/api/auth/me')) payload = user
    else if (path.includes('/api/opportunities/')) payload = [opportunity]
    else if (path.endsWith('/api/monitor/preferences')) {
      payload = { 'BTC/USDT': { in_portfolio: true, card_mode: 'price', price_timeframe: '1d' } }
    } else if (path.endsWith('/api/user/binance-credentials')) {
      payload = { configured: true, api_key_masked: 'ABCD****WXYZ' }
    } else if (path.endsWith('/api/monitor/spot-market-orders/eligibility')) {
      payload = { items: [{ symbol: 'BTCUSDT', eligible: true, reason: null }] }
    } else if (path.includes('/api/external/binance/spot/balances')) {
      payload = {
        balances: [{ asset: 'BTC', total: 0.01842 }, { asset: 'USDT', total: 1250 }],
        total_usd: 2447,
        as_of: '2026-08-06T20:00:00Z',
      }
    } else if (path.endsWith('/api/monitor/spot-market-orders/preview')) {
      payload = {
        preview_token: 'preview-token-with-more-than-thirty-two-characters',
        idempotency_key: 'idempotency-key-buy-385',
        expires_at: '2026-08-06T20:05:00+00:00',
        symbol: 'BTCUSDT',
        side: 'BUY',
        base_asset: 'BTC',
        quote_asset: 'USDT',
        indicative_price: '65000',
        quote_balance: '1250',
        base_balance: '0.01842',
        requested_quote_amount: '250',
        calculated_base_quantity: null,
        estimated_base_quantity: '0.003846153846',
        estimated_quote_amount: null,
        residual_quantity: '0',
        warning: 'A compra será enviada a mercado e o preço final pode variar.',
      }
    } else if (path.includes('/api/market/candles')) {
      payload = {
        candles: [
          { timestamp_utc: '2026-08-05T00:00:00Z', open: 64000, high: 65500, low: 63800, close: 65000, volume: 1 },
          { timestamp_utc: '2026-08-06T00:00:00Z', open: 65000, high: 66000, low: 64500, close: 65200, volume: 1 },
        ],
      }
    } else if (path.includes('/api/favorites')) payload = []

    await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(payload) })
  })

  await page.goto('/monitor')
  await page.locator('[data-testid="open-spot-trade-btc-usdt"]:visible').first().click()
  await expect(page.getByRole('dialog')).toHaveScreenshot('monitor-spot-market-entry.png', {
    animations: 'disabled',
  })
  await page.getByTestId('spot-buy-amount').fill('250')
  await page.getByTestId('spot-continue-order').click()
  await expect(page.getByRole('heading', { name: 'Confirme sua ordem' })).toBeVisible()

  await expect(page.getByRole('dialog')).toHaveScreenshot('monitor-spot-market-review.png', {
    animations: 'disabled',
  })
})
