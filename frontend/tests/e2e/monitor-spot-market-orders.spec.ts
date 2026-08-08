import { expect, test, type Page, type Route } from '@playwright/test'

const USER = {
  id: 'spot-market-user',
  email: 'spot.market@example.com',
  name: 'Spot Market',
  isAdmin: false,
  mustChangePassword: false,
}

const OPPORTUNITY = {
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

const BUY_PREVIEW = {
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

const SELL_PREVIEW = {
  ...BUY_PREVIEW,
  preview_token: 'sell-preview-token-with-more-than-thirty-two-characters',
  idempotency_key: 'idempotency-key-sell-385',
  side: 'SELL',
  requested_quote_amount: null,
  calculated_base_quantity: '0.0184',
  estimated_base_quantity: null,
  estimated_quote_amount: '1196',
  residual_quantity: '0.00002',
  warning: 'A venda usará 100% do saldo livre possível; filtros da Binance podem deixar resíduo.',
}

function orderResult(side: 'BUY' | 'SELL', state: 'filled' | 'partial' | 'reconciling' | 'rejected' = 'filled') {
  const terminal = state !== 'reconciling'
  return {
    idempotency_key: side === 'BUY' ? BUY_PREVIEW.idempotency_key : SELL_PREVIEW.idempotency_key,
    symbol: 'BTCUSDT',
    side,
    state,
    requested_quote_amount: side === 'BUY' ? '250' : null,
    calculated_base_quantity: side === 'SELL' ? '0.0184' : null,
    executed_base_quantity: terminal ? (state === 'partial' ? '0.00153846' : side === 'BUY' ? '0.00384' : '0.0184') : null,
    executed_quote_amount: terminal ? (state === 'partial' ? '100' : side === 'BUY' ? '249.6' : '1195.5') : null,
    average_price: terminal ? '65000' : null,
    fees: state === 'partial' ? [{ asset: 'BTC', amount: '0.0000015' }] : [],
    binance_status: state === 'filled' ? 'FILLED' : state === 'partial' ? 'PARTIALLY_FILLED' : null,
    residual_quantity: side === 'SELL' ? '0.00002' : '0',
    error_code: state === 'reconciling' ? 'ORDER_STATUS_UNKNOWN' : null,
    message: state === 'reconciling' ? 'Resultado ainda não confirmado.' : null,
    created_at: '2026-08-06T20:00:00',
    updated_at: '2026-08-06T20:00:01',
  }
}

async function fulfillJson(route: Route, body: unknown, status = 200) {
  await route.fulfill({ status, contentType: 'application/json', body: JSON.stringify(body) })
}

async function setup(page: Page, options?: {
  configured?: boolean
  abortSubmit?: boolean
  submitStatus?: number
  opportunity?: typeof OPPORTUNITY
  opportunities?: Array<typeof OPPORTUNITY>
  submitState?: 'filled' | 'partial' | 'rejected'
  liveEligible?: boolean
  terminalRefreshDelayMs?: number
  balanceRefreshFails?: boolean
  resumePending?: boolean
  statusCredentialError?: boolean
  statusNotFound?: boolean
  priorOrderConflict?: boolean
}) {
  await page.addInitScript(({ authenticatedUser, pendingOrderKey }) => {
    window.localStorage.setItem('auth_access_token', 'test-access-token')
    window.localStorage.setItem('auth_refresh_token', 'test-refresh-token')
    window.localStorage.setItem('auth_user', JSON.stringify(authenticatedUser))
    if (pendingOrderKey) {
      window.sessionStorage.setItem('monitor-spot-order:BTCUSDT', pendingOrderKey)
    }
  }, {
    authenticatedUser: USER,
    pendingOrderKey: options?.resumePending === true ? BUY_PREVIEW.idempotency_key : null,
  })

  const previewBodies: Array<Record<string, unknown>> = []
  const submitBodies: Array<Record<string, unknown>> = []
  let statusQueries = 0
  let balanceQueries = 0
  const eligibilityBatchSizes: number[] = []
  const opportunities = options?.opportunities ?? [options?.opportunity ?? OPPORTUNITY]

  await page.route('**/api/**', async (route) => {
    const request = route.request()
    const url = new URL(request.url())
    const path = url.pathname

    if (path.endsWith('/api/auth/me')) return fulfillJson(route, USER)
    if (path.includes('/api/opportunities/')) return fulfillJson(route, opportunities)
    if (path.endsWith('/api/monitor/preferences')) {
      return fulfillJson(route, Object.fromEntries(opportunities.map(({ symbol }) => [
        symbol,
        { in_portfolio: true, card_mode: 'price', price_timeframe: '1d' },
      ])))
    }
    if (path.endsWith('/api/user/binance-credentials')) {
      return fulfillJson(route, { configured: options?.configured !== false, api_key_masked: 'ABCD****WXYZ' })
    }
    if (path.endsWith('/api/monitor/spot-market-orders/eligibility')) {
      const body = request.postDataJSON() as { symbols?: string[] }
      eligibilityBatchSizes.push(body.symbols?.length ?? 0)
      return fulfillJson(route, {
        items: (body.symbols ?? []).map((symbol) => ({
          symbol: symbol.replace(/[^a-zA-Z0-9]/g, '').toUpperCase(),
          eligible: options?.liveEligible !== false,
          reason: options?.liveEligible === false ? 'Ativo indisponível para negociação Spot' : null,
        })),
      })
    }
    if (path.includes('/api/external/binance/spot/balances')) {
      balanceQueries += 1
      if (balanceQueries > 1 && options?.balanceRefreshFails) return route.abort('connectionreset')
      if (balanceQueries > 1 && options?.terminalRefreshDelayMs) {
        await new Promise((resolve) => setTimeout(resolve, options.terminalRefreshDelayMs))
      }
      return fulfillJson(route, {
        balances: [{ asset: 'BTC', total: 0.01842 }, { asset: 'USDT', total: 1250 }],
        total_usd: 2447,
        as_of: '2026-08-06T20:00:00Z',
      })
    }
    if (path.endsWith('/api/monitor/spot-market-orders/preview')) {
      const body = request.postDataJSON() as Record<string, unknown>
      previewBodies.push(body)
      if (body.side === 'SELL') return fulfillJson(route, SELL_PREVIEW)
      return fulfillJson(route, {
        ...BUY_PREVIEW,
        requested_quote_amount: String(body.quote_amount_usdt ?? ''),
      })
    }
    if (path.endsWith('/api/monitor/spot-market-orders') && request.method() === 'POST') {
      submitBodies.push(request.postDataJSON() as Record<string, unknown>)
      if (options?.abortSubmit) return route.abort('connectionreset')
      if (options?.submitStatus) {
        return fulfillJson(route, { detail: { message: 'Falha temporária no gateway.' } }, options.submitStatus)
      }
      if (options?.priorOrderConflict) {
        return fulfillJson(route, {
          detail: {
            code: 'PRIOR_ORDER_RECONCILED',
            message: 'Uma operação anterior deste ativo acabou de ser reconciliada. Revise o resultado no Monitor e gere uma nova prévia antes de confirmar outra ordem.',
          },
        }, 409)
      }
      const side = submitBodies.at(-1)?.idempotency_key === SELL_PREVIEW.idempotency_key ? 'SELL' : 'BUY'
      return fulfillJson(route, orderResult(side, options?.submitState))
    }
    if (path.includes('/api/monitor/spot-market-orders/')) {
      statusQueries += 1
      if (options?.statusCredentialError) {
        return fulfillJson(route, {
          detail: {
            code: 'BINANCE_VALIDATION_ERROR',
            message: 'A Binance recusou a credencial ou assinatura. Revise a conexão em Meu Perfil.',
          },
        }, 403)
      }
      if (options?.statusNotFound) {
        return fulfillJson(route, { detail: { code: 'ORDER_NOT_FOUND' } }, 404)
      }
      return fulfillJson(route, orderResult('BUY'))
    }
    if (path.includes('/api/market/candles')) {
      return fulfillJson(route, {
        candles: [
          { timestamp_utc: '2026-08-05T00:00:00Z', open: 64000, high: 65500, low: 63800, close: 65000, volume: 1 },
          { timestamp_utc: '2026-08-06T00:00:00Z', open: 65000, high: 66000, low: 64500, close: 65200, volume: 1 },
        ],
      })
    }
    if (path.includes('/api/favorites')) return fulfillJson(route, [])
    return fulfillJson(route, {})
  })

  return {
    previewBodies,
    submitBodies,
    get statusQueries() { return statusQueries },
    get balanceQueries() { return balanceQueries },
    eligibilityBatchSizes,
  }
}

function visibleTradeTrigger(page: Page) {
  return page.locator('[data-testid="open-spot-trade-btc-usdt"]:visible').first()
}

test('compra usa valor em USDT, confirmação explícita e um único submit', async ({ page }) => {
  const calls = await setup(page)
  await page.goto('/monitor')

  await expect(visibleTradeTrigger(page)).toBeVisible()
  await visibleTradeTrigger(page).click()
  await expect(page.getByRole('dialog')).toContainText('Saldo livreConfirmado pela Binance na próxima etapa')
  await expect(page.getByRole('dialog')).not.toContainText('1.250,00 USDT')
  await page.getByTestId('spot-buy-amount').fill('250')
  await page.getByTestId('spot-continue-order').click()

  await expect(page.getByRole('heading', { name: 'Confirme sua ordem' })).toBeFocused()
  await expect(page.getByTestId('spot-confirm-order')).toBeDisabled()
  await expect(page.getByRole('dialog')).toContainText('250,00 USDT')
  await expect(page.getByRole('dialog')).toContainText('Saldo USDT disponível')
  await expect(page.getByRole('dialog')).toContainText('1.250,00 USDT')
  await expect(page.getByRole('dialog')).toContainText('TaxasDefinidas na execução')
  await page.getByRole('checkbox').check()
  await page.getByTestId('spot-confirm-order').dblclick()

  await expect(page.getByRole('heading', { name: 'Compra executada' })).toBeVisible()
  expect(calls.previewBodies).toEqual([{ symbol: 'BTC/USDT', side: 'BUY', quote_amount_usdt: 250 }])
  expect(calls.submitBodies).toEqual([{
    preview_token: BUY_PREVIEW.preview_token,
    idempotency_key: BUY_PREVIEW.idempotency_key,
  }])
  expect(calls.balanceQueries).toBeGreaterThanOrEqual(2)
})

test('valor em USDT com casas decimais não é multiplicado por mil', async ({ page }) => {
  const calls = await setup(page)
  await page.goto('/monitor')
  await visibleTradeTrigger(page).click()

  await page.getByTestId('spot-buy-amount').fill('250.125')
  await page.getByTestId('spot-continue-order').click()
  await expect(page.getByRole('heading', { name: 'Confirme sua ordem' })).toBeVisible()
  await expect(page.getByRole('dialog')).toContainText('250,125 USDT')
  expect(calls.previewBodies).toEqual([{ symbol: 'BTC/USDT', side: 'BUY', quote_amount_usdt: 250.125 }])
})

test('valor em USDT pequeno com vírgula decimal é preservado', async ({ page }) => {
  const calls = await setup(page)
  await page.goto('/monitor')
  await visibleTradeTrigger(page).click()

  await page.getByTestId('spot-buy-amount').fill('0,001')
  await page.getByTestId('spot-continue-order').click()
  await expect(page.getByRole('heading', { name: 'Confirme sua ordem' })).toBeVisible()
  expect(calls.previewBodies).toEqual([{ symbol: 'BTC/USDT', side: 'BUY', quote_amount_usdt: 0.001 }])
})

test('valor em USDT no formato pt-BR com milhar é normalizado', async ({ page }) => {
  const calls = await setup(page)
  await page.goto('/monitor')
  await visibleTradeTrigger(page).click()

  await page.getByTestId('spot-buy-amount').fill('1.250,50')
  await page.getByTestId('spot-continue-order').click()
  await expect(page.getByRole('heading', { name: 'Confirme sua ordem' })).toBeVisible()
  expect(calls.previewBodies).toEqual([{ symbol: 'BTC/USDT', side: 'BUY', quote_amount_usdt: 1250.5 }])
})

test('venda envia sempre 100% calculado no servidor e exibe possível residual', async ({ page }) => {
  const calls = await setup(page)
  await page.goto('/monitor')
  await visibleTradeTrigger(page).click()
  await page.getByRole('tab', { name: 'Comprar' }).focus()
  await page.keyboard.press('ArrowRight')
  await expect(page.getByRole('tab', { name: 'Vender 100%' })).toBeFocused()
  await page.getByTestId('spot-continue-order').click()

  await expect(page.getByRole('dialog')).toContainText('100% · 0,01842 BTC')
  await expect(page.getByRole('dialog')).toContainText('0,0184 / 0,00002 BTC')
  await page.getByRole('checkbox').check()
  await page.getByTestId('spot-confirm-order').click()
  await expect(page.getByRole('heading', { name: 'Venda executada' })).toBeVisible()

  expect(calls.previewBodies).toEqual([{ symbol: 'BTC/USDT', side: 'SELL', quote_amount_usdt: null }])
  expect(calls.submitBodies[0]).toEqual({
    preview_token: SELL_PREVIEW.preview_token,
    idempotency_key: SELL_PREVIEW.idempotency_key,
  })
  expect(calls.submitBodies[0]).not.toHaveProperty('quantity')
})

test('falha de rede preserva reconciliação e reabrir consulta sem reenviar', async ({ page }) => {
  const calls = await setup(page, { abortSubmit: true })
  await page.goto('/monitor')
  await visibleTradeTrigger(page).click()
  await page.getByTestId('spot-buy-amount').fill('100')
  await page.getByTestId('spot-continue-order').click()
  await page.getByRole('checkbox').check()
  await page.getByTestId('spot-confirm-order').click()

  await expect(page.getByRole('heading', { name: 'Verificando execução' })).toBeVisible()
  await expect(page.getByRole('dialog')).toContainText('Não reenvie')
  await expect(page.getByRole('dialog')).toContainText('Valores executadosAguardando confirmação')
  await expect(page.getByRole('dialog')).not.toContainText('Quantidade executada0')
  await expect(page.getByRole('dialog')).not.toContainText('Valor executado0,00')
  await page.getByRole('button', { name: 'Fechar', exact: true }).click()
  await visibleTradeTrigger(page).click()

  await expect(page.getByRole('heading', { name: 'Compra executada' })).toBeVisible()
  expect(calls.submitBodies).toHaveLength(1)
  expect(calls.statusQueries).toBeGreaterThanOrEqual(1)
})

test('HTTP 502 após confirmação preserva a chave e reconcilia sem segundo envio', async ({ page }) => {
  const calls = await setup(page, { submitStatus: 502 })
  await page.goto('/monitor')
  await visibleTradeTrigger(page).click()
  await page.getByTestId('spot-buy-amount').fill('100')
  await page.getByTestId('spot-continue-order').click()
  await page.getByRole('checkbox').check()
  await page.getByTestId('spot-confirm-order').click()

  await expect(page.getByRole('heading', { name: 'Verificando execução' })).toBeVisible()
  await page.getByRole('button', { name: 'Fechar', exact: true }).click()
  await visibleTradeTrigger(page).click()

  await expect(page.getByRole('heading', { name: 'Compra executada' })).toBeVisible()
  expect(calls.submitBodies).toHaveLength(1)
  expect(calls.statusQueries).toBeGreaterThanOrEqual(1)
})

test('sem credencial orienta conexão e mantém foco preso no diálogo', async ({ page }) => {
  await setup(page, { configured: false })
  await page.goto('/monitor')
  const trigger = visibleTradeTrigger(page)
  await trigger.click()

  const dialog = page.getByRole('dialog')
  await expect(page.locator('#root')).toHaveAttribute('inert', '')
  await expect(dialog).toContainText('Operação indisponível')
  await expect(page.getByRole('link', { name: 'Revisar conexão Binance' })).toHaveAttribute('href', '/profile')
  await page.keyboard.press('Shift+Tab')
  await expect(page.getByRole('link', { name: 'Revisar conexão Binance' })).toBeFocused()
  await page.keyboard.press('Escape')
  await expect(dialog).toBeHidden()
  await expect(page.locator('#root')).not.toHaveAttribute('inert')
  await expect(trigger).toBeFocused()
})

test('resultado terminal persistido continua visível após remover credenciais', async ({ page }) => {
  const calls = await setup(page, { configured: false, resumePending: true })
  await page.goto('/monitor')
  await visibleTradeTrigger(page).click()

  await expect(page.getByRole('heading', { name: 'Compra executada' })).toBeVisible()
  await expect(page.getByRole('dialog')).not.toContainText('Operação indisponível')
  expect(calls.statusQueries).toBeGreaterThanOrEqual(1)
})

test('execução parcial mostra valor restante e taxas confirmadas', async ({ page }) => {
  await setup(page, { submitState: 'partial' })
  await page.goto('/monitor')
  await visibleTradeTrigger(page).click()
  await page.getByTestId('spot-buy-amount').fill('250')
  await page.getByTestId('spot-continue-order').click()
  await page.getByRole('checkbox').check()
  await page.getByTestId('spot-confirm-order').click()

  const dialog = page.getByRole('dialog')
  await expect(page.getByRole('heading', { name: 'Execução parcial' })).toBeVisible()
  await expect(dialog).toContainText('Restante não executado150,00 USDT')
  await expect(dialog).toContainText('Taxas cobradas0,0000015 BTC')
})

test('par de cripto fora de USDT explica por que a operação direta está indisponível', async ({ page }) => {
  await setup(page, {
    opportunity: { ...OPPORTUNITY, id: 386, symbol: 'ETH/BTC', name: 'ETH/BTC Long' },
  })
  await page.goto('/monitor')

  const unavailable = page.getByRole('button', {
    name: 'Operação direta disponível apenas para pares Spot cotados em USDT.',
  }).first()
  await expect(unavailable).toBeVisible()
  await expect(unavailable).toBeDisabled()
  await expect(unavailable).toContainText('Operação direta disponível apenas para pares Spot cotados em USDT.')
})

test('par USDT indisponível no exchangeInfo não oferece a ação Operar', async ({ page }) => {
  await setup(page, { liveEligible: false })
  await page.goto('/monitor')

  const unavailable = page.getByRole('button', {
    name: 'Ativo indisponível para negociação Spot',
  }).first()
  await expect(unavailable).toBeVisible()
  await expect(unavailable).toBeDisabled()
  await expect(unavailable).toContainText('Ativo indisponível para negociação Spot')
  await expect(page.locator('[data-testid="open-spot-trade-btc-usdt"]:visible')).toHaveCount(0)
})

test('elegibilidade é consultada em lotes de no máximo 100 símbolos', async ({ page }) => {
  const opportunities = Array.from({ length: 101 }, (_, index) => ({
    ...OPPORTUNITY,
    id: 1000 + index,
    symbol: `COIN${index}/USDT`,
    name: `COIN${index} Long`,
  }))
  const calls = await setup(page, { opportunities })
  await page.goto('/monitor')

  await expect.poll(() => calls.eligibilityBatchSizes.length).toBeGreaterThanOrEqual(2)
  expect(calls.eligibilityBatchSizes.every((size) => size > 0 && size <= 100)).toBe(true)
  expect(new Set(calls.eligibilityBatchSizes)).toEqual(new Set([100, 1]))
})

test('execução parcial bloqueia nova operação até atualizar saldos', async ({ page }) => {
  await setup(page, { submitState: 'partial', terminalRefreshDelayMs: 800 })
  await page.goto('/monitor')
  await visibleTradeTrigger(page).click()
  await page.getByTestId('spot-buy-amount').fill('250')
  await page.getByTestId('spot-continue-order').click()
  await page.getByRole('checkbox').check()
  await page.getByTestId('spot-confirm-order').click()

  await expect(page.getByRole('heading', { name: 'Execução parcial' })).toBeVisible()
  await expect(page.getByRole('button', { name: 'Atualizando saldos…' })).toBeDisabled()
  await expect(page.getByRole('button', { name: 'Nova operação' })).toBeEnabled()
})

test('falha ao atualizar saldos não informa sucesso nem libera nova operação', async ({ page }) => {
  await setup(page, { balanceRefreshFails: true })
  await page.goto('/monitor')
  await visibleTradeTrigger(page).click()
  await page.getByTestId('spot-buy-amount').fill('250')
  await page.getByTestId('spot-continue-order').click()
  await page.getByRole('checkbox').check()
  await page.getByTestId('spot-confirm-order').click()

  const dialog = page.getByRole('dialog')
  await expect(page.getByRole('heading', { name: 'Compra executada' })).toBeVisible()
  await expect(dialog).toContainText('não foi possível atualizar os saldos')
  await expect(dialog).not.toContainText('Os saldos do Monitor foram atualizados')
  await expect(page.getByRole('button', { name: 'Tentar atualizar saldos' })).toBeEnabled()
  await expect(page.getByRole('button', { name: 'Nova operação' })).toHaveCount(0)
  await expect(page.getByRole('button', { name: 'Fechar', exact: true })).toBeEnabled()

  await page.getByRole('button', { name: 'Fechar', exact: true }).click()
  await visibleTradeTrigger(page).click()
  await expect(page.getByRole('heading', { name: 'Compra executada' })).toBeVisible()
  await expect(page.getByRole('button', { name: 'Nova operação' })).toHaveCount(0)
})

test('rejeição definitiva libera nova prévia sem depender do refresh de saldos', async ({ page }) => {
  const calls = await setup(page, { submitState: 'rejected', balanceRefreshFails: true })
  await page.goto('/monitor')
  await visibleTradeTrigger(page).click()
  await page.getByTestId('spot-buy-amount').fill('250')
  await page.getByTestId('spot-continue-order').click()
  await page.getByRole('checkbox').check()
  const balanceQueriesBeforeSubmit = calls.balanceQueries
  await page.getByTestId('spot-confirm-order').click()

  await expect(page.getByRole('heading', { name: 'Ordem não executada' })).toBeVisible()
  await expect(page.getByRole('button', { name: 'Nova operação' })).toBeEnabled()
  await expect(page.getByRole('button', { name: 'Tentar atualizar saldos' })).toHaveCount(0)
  expect(calls.balanceQueries).toBe(balanceQueriesBeforeSubmit)
})

test('ordem anterior reconciliada exige nova prévia sem atribuir o fill à confirmação atual', async ({ page }) => {
  const calls = await setup(page, { priorOrderConflict: true })
  await page.goto('/monitor')
  await visibleTradeTrigger(page).click()
  await page.getByTestId('spot-buy-amount').fill('250')
  await page.getByTestId('spot-continue-order').click()
  await page.getByRole('checkbox').check()
  await page.getByTestId('spot-confirm-order').click()

  await expect(page.getByTestId('spot-buy-amount')).toBeVisible()
  await expect(page.getByRole('dialog')).toContainText('gere uma nova prévia')
  await expect(page.getByRole('heading', { name: 'Compra executada' })).toHaveCount(0)
  expect(calls.submitBodies).toHaveLength(1)

  await page.getByTestId('spot-buy-amount').fill('250')
  await page.getByTestId('spot-continue-order').click()
  await expect(page.getByRole('heading', { name: 'Confirme sua ordem' })).toBeVisible()
  expect(calls.previewBodies).toHaveLength(2)
  expect(calls.submitBodies).toHaveLength(1)
})

test('erro de credencial na reconciliação fica visível e mantém a ordem bloqueada', async ({ page }) => {
  await setup(page, { abortSubmit: true, statusCredentialError: true })
  await page.goto('/monitor')
  await visibleTradeTrigger(page).click()
  await page.getByTestId('spot-buy-amount').fill('100')
  await page.getByTestId('spot-continue-order').click()
  await page.getByRole('checkbox').check()
  await page.getByTestId('spot-confirm-order').click()

  const dialog = page.getByRole('dialog')
  await expect(page.getByRole('heading', { name: 'Verificando execução' })).toBeVisible()
  await expect(dialog).toContainText('Revise a conexão em Meu Perfil', { timeout: 8_000 })
  await expect(dialog).toContainText('Não envie novamente')
  await expect(page.getByRole('button', { name: 'Nova operação' })).toHaveCount(0)
})

test('404 repetido na reconciliação libera nova prévia sem manter estado infinito', async ({ page }) => {
  const calls = await setup(page, { abortSubmit: true, statusNotFound: true })
  await page.goto('/monitor')
  await visibleTradeTrigger(page).click()
  await page.getByTestId('spot-buy-amount').fill('100')
  await page.getByTestId('spot-continue-order').click()
  await page.getByRole('checkbox').check()
  await page.getByTestId('spot-confirm-order').click()

  await expect(page.getByRole('heading', { name: 'Verificando execução' })).toBeVisible()
  await expect(page.getByRole('dialog')).toContainText('A operação não foi localizada após novas consultas', {
    timeout: 12_000,
  })
  await expect(page.getByTestId('spot-buy-amount')).toBeVisible()
  expect(calls.statusQueries).toBeGreaterThanOrEqual(3)
})
