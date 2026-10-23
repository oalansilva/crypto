import { expect, test, type Page } from '@playwright/test'
import { mockAssetCatalog, type CatalogMock } from './helpers/assetCatalogMock'

/**
 * Card #1117 (4.2): o seletor de ativos nas três telas reais, com a API simulada.
 * Cobre pesquisa de BTC/USDT, NVDA, SPY e QQQ, "Todos do filtro" com confirmação
 * e Esc, marcado sem caixa ativa, seleção antiga, aviso nas três telas, lote da
 * Otimização e falha por classe.
 */

const ADMIN_USER = {
  id: 'discovery-admin',
  email: 'alan@example.com',
  name: 'Alan Silva',
  isAdmin: true,
  mustChangePassword: false,
}

const TEMPLATES = [
  { name: 'multi_ma_crossover', display_name: 'Médias: tendência', description: 'x', is_readonly: true },
  { name: 'ema_rsi', display_name: 'EMA + RSI', description: 'x', is_readonly: true },
]

const pageErrors = new WeakMap<Page, string[]>()

test.beforeEach(({ page }) => {
  const errors: string[] = []
  pageErrors.set(page, errors)
  page.on('pageerror', (error) => errors.push(error.message))
})

test.afterEach(({ page }) => {
  expect(pageErrors.get(page) ?? [], 'sem erro de página não tratado').toEqual([])
})

function json(body: unknown, status = 200) {
  return { status, contentType: 'application/json', body: JSON.stringify(body) }
}

async function baseMocks(page: Page): Promise<CatalogMock> {
  await page.addInitScript((user) => {
    localStorage.setItem('auth_access_token', 'admin-token')
    localStorage.setItem('auth_refresh_token', 'admin-refresh')
    localStorage.setItem('auth_user', JSON.stringify(user))
    localStorage.setItem('cripto-farol-onboarding-dismissed', '1')
  }, ADMIN_USER)
  await page.route('**/api/**', (route) => route.fulfill(json({})))
  await page.route('**/api/auth/me', (route) => route.fulfill(json(ADMIN_USER)))
  await page.route('**/api/combos/templates', (route) =>
    route.fulfill(json({ prebuilt: TEMPLATES, examples: [], custom: [] })),
  )
  return mockAssetCatalog(page)
}

async function discoveryMocks(page: Page) {
  const catalog = await baseMocks(page)
  const preflightBodies: Array<{ symbols: string[] }> = []
  await page.route('**/api/combos/discovery/sweeps/active', (route) => route.fulfill(json({ sweeps: [] })))
  await page.route('**/api/combos/discovery/sweeps/history', (route) => route.fulfill(json({ sweeps: [] })))
  await page.route('**/api/combos/discovery/sweeps/preflight', async (route) => {
    const body = JSON.parse(route.request().postData() || '{}') as {
      templates: string[]
      symbols: string[]
      timeframes: string[]
      directions: string[]
    }
    preflightBodies.push(body)
    const byId = new Map(catalog.assets.map((a) => [a.symbol, a]))
    const per = body.templates.length * body.timeframes.length * body.directions.length
    const excluded = body.symbols
      .map((s) => byId.get(s))
      .filter((a) => a && (a.asset_class !== 'crypto' || a.state !== 'tradable'))
      .map((a) => ({
        symbol: a!.symbol,
        asset_class: a!.asset_class,
        state: a!.state,
        kind: a!.state !== 'tradable' ? 'marked' : 'class',
        reason:
          a!.state !== 'tradable'
            ? `${a!.state_label} na Binance; não entra em análise nova`
            : 'análise ainda não disponível para ações e ETFs',
        combinations: per,
      }))
    const validSymbols = body.symbols.filter((s) => {
      const a = byId.get(s)
      return !a || (a.asset_class === 'crypto' && a.state === 'tradable')
    })
    const valid = validSymbols.length * per
    await route.fulfill(
      json({
        axes: { templates: body.templates, symbols: body.symbols, timeframes: body.timeframes, directions: body.directions },
        raw_total: body.symbols.length * per,
        exclusions: {},
        excluded_assets: excluded,
        excluded_count: (body.symbols.length - validSymbols.length) * per,
        valid_total: valid,
        limits: { max_total: 1000 },
        errors: valid === 0 ? { symbols: 'Nenhuma combinação válida: análise ainda não disponível para ações e ETFs.' } : {},
        expires_at: '2026-10-21T00:00:00Z',
        snapshot_token: 'tok',
        snapshot_hash: 'hash1117',
        period_type: 'all',
      }),
    )
  })
  return { catalog, preflightBodies }
}

async function pickTemplate(page: Page) {
  await page.getByTestId('inline-templates-search').fill('Médias')
  await page.locator('[role=group][aria-label="Templates (seleção inline)"] input[type=checkbox]').first().check()
}

async function search(page: Page, text: string) {
  await page.getByTestId('asset-search').fill(text)
  await expect(page.getByTestId('asset-results')).toBeVisible()
}

const row = (page: Page, symbol: string) => page.locator(`.ap-row[data-asset="${symbol}"]`)
const chip = (page: Page, symbol: string) => page.locator(`.ap-chip[data-asset="${symbol}"]`)

test.describe('seletor de ativos na Descoberta', () => {
  test('pesquisa encontra BTC/USDT, NVDA, SPY e QQQ na primeira página e deixa marcar', async ({ page }) => {
    await discoveryMocks(page)
    await page.goto('/combo/discovery')
    await expect(page.getByRole('heading', { name: 'Ativos' })).toBeVisible()
    await expect(page.getByTestId('edit-symbols')).toHaveCount(0)

    for (const [query, symbol, cls] of [
      ['BTC/USDT', 'BTC/USDT', 'Cripto'],
      ['nvda', 'NVDA', 'Ação'],
      ['SPY', 'SPY', 'ETF'],
      ['qqq', 'QQQ', 'ETF'],
    ] as const) {
      await search(page, query)
      const first = page.locator('.ap-row').first()
      await expect(first).toHaveAttribute('data-asset', symbol)
      await expect(first).toContainText(cls)
      await first.locator('input').check()
      await expect(chip(page, symbol)).toBeVisible()
    }
    await expect(page.getByTestId('asset-count')).toContainText('4 selecionados · 1 cripto · 1 ação · 2 ETFs')
    await expect(page.getByTestId('asset-class-note')).toBeVisible()
  })

  test('pesquisa por nome ignora caixa e acento e cada linha separa classe, negociação e histórico', async ({ page }) => {
    await discoveryMocks(page)
    await page.goto('/combo/discovery')
    await search(page, 'NVIDIA')
    const first = page.locator('.ap-row').first()
    await expect(first).toHaveAttribute('data-asset', 'NVDA')
    await expect(first.locator('.ap-fact.cls-stock')).toHaveText('Ação')
    await expect(first.locator('.ap-fact.st-ok')).toHaveText('Negociável')
    await expect(first.locator('.ap-fact.hist')).toHaveText(
      'Histórico sob demanda · a coleta começa quando as análises aceitarem ações',
    )
    await expect(page.getByTestId('asset-select-all')).toHaveText('Todos do filtro (2)')

    await search(page, 'btc')
    await expect(row(page, 'BTC/USDT').locator('.ap-fact.hist')).toHaveText(
      /^Histórico desde 17 ago\. 2017 · 4 timeframes · sem lacunas · atualizado /,
    )
  })

  test('ativo suspenso aparece sem caixa ativa, com motivo, e não entra na seleção', async ({ page }) => {
    await discoveryMocks(page)
    await page.goto('/combo/discovery')
    await search(page, 'waves')
    const waves = row(page, 'WAVES/USDT')
    await expect(waves.locator('input')).toBeDisabled()
    await expect(waves.locator('.ap-fact.st-marked')).toHaveText('Suspenso')
    await expect(waves.getByTestId('asset-marked-reason')).toContainText('Negociação pausada pela Binance (status BREAK).')
    await expect(waves.getByTestId('asset-marked-reason')).toContainText('Não pode ser escolhido para análise nova')
    await waves.click({ force: true })
    await expect(page.getByTestId('asset-count')).toContainText('0 selecionados')
    await expect(page.getByTestId('asset-select-all')).toBeDisabled()
    await expect(page.getByTestId('asset-select-all')).toHaveText('Todos do filtro (0)')
  })

  test('Todos do filtro: confirmação com incluídos e marcados, Esc e Cancelar não mudam nada, Incluir soma', async ({ page }) => {
    const { catalog } = await discoveryMocks(page)
    await page.goto('/combo/discovery')
    await page.getByRole('button', { name: /^ETFs/ }).click()
    await expect(page.getByRole('button', { name: /^ETFs/ })).toHaveAttribute('aria-pressed', 'true')

    const all = page.getByTestId('asset-select-all')
    await expect(all).toHaveText('Todos do filtro (3)')
    await all.click()
    const dialog = page.getByRole('alertdialog')
    await expect(dialog).toContainText('Incluir 3 ETFs negociáveis na seleção?')
    await expect(dialog).toContainText('1 ativo marcado fica de fora')
    await expect(dialog).toContainText('O que já está selecionado continua.')
    await expect(page.getByTestId('asset-confirm-ok')).toBeFocused()

    await page.keyboard.press('Escape')
    await expect(dialog).toHaveCount(0)
    await expect(all).toBeFocused()
    await expect(page.getByTestId('asset-count')).toContainText('0 selecionados')

    await all.click()
    await page.getByTestId('asset-confirm-cancel').click()
    await expect(dialog).toHaveCount(0)
    await expect(all).toBeFocused()
    await expect(page.getByTestId('asset-count')).toContainText('0 selecionados')

    await all.click()
    await page.getByTestId('asset-confirm-ok').click()
    await expect(page.getByTestId('asset-count')).toContainText('3 selecionados · 3 ETFs')
    await expect(chip(page, 'SPY')).toBeVisible()
    await expect(chip(page, 'IBIC')).toHaveCount(0)
    expect(catalog.requests.resolve.length).toBeGreaterThan(0)

    // sem pesquisa e depois com ela: segue somando, e o × remove um item
    await page.getByRole('button', { name: /^Todas/ }).click()
    await search(page, 'nvidia')
    await expect(all).toHaveText('Todos do filtro (2)')
    await all.click()
    await expect(page.getByRole('alertdialog')).toContainText('Incluir 2 (1 novo) ativos negociáveis que correspondem a “nvidia” (todas as classes)')
    await page.getByTestId('asset-confirm-ok').click()
    await expect(page.getByTestId('asset-count')).toContainText('4 selecionados · 1 ação · 3 ETFs')
    await chip(page, 'QQQ').getByRole('button', { name: 'Remover QQQ da seleção' }).click()
    await expect(page.getByTestId('asset-count')).toContainText('3 selecionados')
    await expect(page.getByTestId('asset-search')).toBeFocused()
  })

  test('Incluir usa a seleção atual: remover um ativo enquanto o resolve corre não o traz de volta', async ({ page }) => {
    await discoveryMocks(page)
    await page.goto('/combo/discovery')
    await search(page, 'nvda')
    await row(page, 'NVDA').locator('input').check()
    await expect(chip(page, 'NVDA')).toBeVisible()

    await page.getByTestId('asset-search').fill('')
    await page.getByRole('button', { name: /^ETFs/ }).click()
    await expect(page.getByRole('button', { name: /^ETFs/ })).toHaveAttribute('aria-pressed', 'true')
    await expect(page.getByTestId('asset-select-all')).toHaveText('Todos do filtro (3)')

    // segura o resolve até a seleção mudar depois do clique em Incluir
    let release: () => void = () => undefined
    const gate = new Promise<void>((resolve) => {
      release = resolve
    })
    await page.route('**/api/assets/catalog/resolve', async (route) => {
      await gate
      await route.fallback()
    })

    await page.getByTestId('asset-select-all').click()
    await page.getByTestId('asset-confirm-ok').click()
    await chip(page, 'NVDA').getByRole('button', { name: 'Remover NVDA da seleção' }).click()
    await expect(chip(page, 'NVDA')).toHaveCount(0)

    release()
    await expect(page.getByTestId('asset-count')).toContainText('3 selecionados · 3 ETFs')
    await expect(chip(page, 'SPY')).toBeVisible()
    await expect(chip(page, 'NVDA')).toHaveCount(0)
  })

  test('× dos chips tem alvo de 44x44px', async ({ page }) => {
    await discoveryMocks(page)
    await page.goto('/combo/discovery')
    await search(page, 'btc')
    await row(page, 'BTC/USDT').locator('input').check()
    const box = await chip(page, 'BTC/USDT').getByRole('button').boundingBox()
    expect(box?.width).toBeGreaterThanOrEqual(44)
    expect(box?.height).toBeGreaterThanOrEqual(44)
  })

  test('Preflight: ação, ETF e marcado ficam em "Fora desta varredura" e a varredura segue com cripto', async ({ page }) => {
    const { preflightBodies } = await discoveryMocks(page)
    await page.goto('/combo/discovery')
    await pickTemplate(page)
    for (const symbol of ['BTC/USDT', 'NVDA', 'SPY']) {
      await search(page, symbol)
      await row(page, symbol).locator('input').check()
    }
    await expect(page.getByTestId('preflight-class-out')).toBeVisible()
    await expect(page.getByTestId('preflight-class-out')).toContainText('Fora desta varredura: 2 ativos')
    await expect(page.getByTestId('preflight-class-out')).toContainText('NVDA (Ação) — análise ainda não disponível para ações e ETFs.')
    await expect(page.getByTestId('preflight-class-out')).toContainText('Eles continuam na seleção do rascunho; nada é perdido.')
    await expect(page.getByTestId('preflight-state')).toContainText('Pronto para iniciar · ações e ETFs fora')
    await expect(page.getByTestId('start-sweep')).toBeEnabled()
    await expect.poll(() => preflightBodies.at(-1)?.symbols).toEqual(['BTC/USDT', 'NVDA', 'SPY'])
  })

  test('só ação e ETF bloqueia o Preflight com o motivo', async ({ page }) => {
    await discoveryMocks(page)
    await page.goto('/combo/discovery')
    await pickTemplate(page)
    await search(page, 'nvda')
    await row(page, 'NVDA').locator('input').check()
    await expect(page.getByTestId('preflight-impediments')).toContainText('Nenhuma combinação válida: a análise ainda não está disponível para ações e ETFs')
    await expect(page.getByTestId('preflight-impediments')).toContainText('Inclua ao menos 1 par cripto negociável em USDT.')
    await expect(page.getByTestId('start-sweep')).toBeDisabled()
    await page.getByTestId('asset-clear').click()
    await expect(page.getByTestId('preflight-impediments')).toContainText('Escolha ao menos 1 ativo.')
  })

  test('rascunho antigo com ativo marcado: "fica de fora" antes do +N, com nota e motivo no Preflight', async ({ page }) => {
    await discoveryMocks(page)
    const snapshot = {
      axes: {
        templates: ['multi_ma_crossover'],
        symbols: ['BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'BNB/USDT', 'XRP/USDT', 'DOGE/USDT', 'ADA/USDT', 'LINK/USDT', 'AVAX/USDT', 'WAVES/USDT'],
        timeframes: ['1d'],
        directions: ['long'],
      },
      raw_total: 10,
      exclusions: {},
      excluded_assets: [],
      excluded_count: 0,
      valid_total: 9,
      limits: { max_total: 1000 },
      errors: {},
      expires_at: '2026-10-21T00:00:00Z',
      snapshot_token: 'tok',
      snapshot_hash: 'hash-old',
      period_type: 'all',
    }
    const oldSweep = {
      sweep_id: 'old-sweep',
      state: 'paused',
      total: 10,
      succeeded: 0,
      failed: 0,
      skipped: 0,
      processed: 0,
      terminal_reason: null,
      terminal_code: null,
      draft_key: 'draft-old',
      snapshot,
      updated_at: '2026-10-19T00:00:00Z',
    }
    await page.route('**/api/combos/discovery/sweeps/active', (route) => route.fulfill(json({ sweeps: [oldSweep] })))
    await page.route('**/api/combos/discovery/sweeps/old-sweep', (route) => route.fulfill(json(oldSweep)))
    await page.route('**/api/combos/discovery/sweeps/old-sweep/leaderboard**', (route) =>
      route.fulfill(json({ results: [], total_matched: 0, total_available: 0 })),
    )
    await page.goto('/combo/discovery')
    await page.getByRole('tab', { name: /Montar/ }).click()
    await expect(chip(page, 'WAVES/USDT')).toBeVisible()
    const chips = page.getByTestId('asset-chips').locator('.ap-chip')
    await expect(chips.first()).toHaveAttribute('data-asset', 'WAVES/USDT')
    await expect(chips.first()).toContainText('Suspenso')
    await expect(chips.first()).toContainText('fica de fora')
    await expect(page.getByTestId('asset-chips')).toContainText('+2 ativos')
    await expect(page.getByTestId('asset-count')).toContainText('1 marcado fica de fora')
    await expect(page.getByTestId('asset-marked-note')).toContainText('a Binance pausou ou retirou esse ativo')
    await expect(page.getByTestId('preflight-class-out')).toContainText('WAVES/USDT (Cripto, Suspenso)')
  })

  test('falha de ações e ETFs com lista anterior: aviso com a data e a escolha continua', async ({ page }) => {
    const { catalog } = await discoveryMocks(page)
    catalog.setScenario('equity-stale')
    await page.goto('/combo/discovery')
    const stale = page.getByTestId('catalog-stale')
    await expect(stale).toContainText('Ações e ETFs desatualizados')
    await expect(stale).toContainText('Mostrando a lista válida de 19 out. 2026, 18:00')
    await expect(page.getByTestId('catalog-fresh')).toContainText('Ações e ETFs de 19 out. 2026, 18:00')
    await search(page, 'nvda')
    await row(page, 'NVDA').locator('input').check()
    await expect(chip(page, 'NVDA')).toBeVisible()
  })

  test('cripto indisponível sem lista: um erro só, Tentar de novo, pesquisa culpa a Binance e a seleção fica', async ({ page }) => {
    const { catalog } = await discoveryMocks(page)
    await page.goto('/combo/discovery')
    await search(page, 'nvda')
    await row(page, 'NVDA').locator('input').check()
    await search(page, '')
    catalog.setScenario('crypto-down')
    await page.getByRole('button', { name: /^Todas/ }).click() // força nova leitura
    await page.getByRole('button', { name: /^Cripto/ }).click()

    await expect(page.getByTestId('catalog-down')).toHaveCount(1)
    await expect(page.getByTestId('catalog-down')).toContainText('Cripto indisponível')
    await expect(page.getByRole('button', { name: /^Cripto/ })).toContainText('indisponível')
    await expect(page.getByTestId('asset-crypto-down')).toContainText('Lista de cripto indisponível por falha da Binance')
    await expect(page.locator('.ap-pager')).toHaveCount(0)

    await page.getByRole('button', { name: /^Todas/ }).click()
    await search(page, 'btc')
    await expect(page.getByTestId('asset-empty')).toContainText('Cripto está indisponível agora por falha da Binance')
    await expect(page.getByTestId('asset-empty')).not.toContainText('Confira o símbolo')
    await expect(page.locator('.ap-pager')).toHaveCount(0)
    await expect(chip(page, 'NVDA')).toBeVisible()

    await page.getByRole('button', { name: 'Tentar de novo' }).click()
    await expect(page.getByTestId('catalog-down')).toHaveCount(0)
    await expect(page.getByTestId('catalog-fresh')).toContainText('Catálogo Binance · atualizado 20 out. 2026, 06:00')
    await expect(row(page, 'BTC/USDT')).toBeVisible()
    await expect(chip(page, 'NVDA')).toBeVisible()
  })
})

test('mobile 390x844: o seletor cabe nas três telas, sem rolagem horizontal, com marcado e falha visíveis', async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 })
  const { catalog } = await discoveryMocks(page)
  await page.route('**/api/combos/meta/ema_rsi', (route) =>
    route.fulfill(
      json({
        name: 'ema_rsi',
        description: 'EMA + RSI',
        indicators: [{ type: 'ema', alias: 'ema', params: { length: 21 } }],
        entry_logic: 'close > ema',
        exit_logic: 'close < ema',
        stop_loss: 0.02,
        optimization_schema: { ema_length: { min: 5, max: 20, step: 1 } },
      }),
    ),
  )
  await page.route('**/api/combos/templates/ema_rsi/metadata', (route) =>
    route.fulfill(json({ indicators: [{ type: 'ema', alias: 'ema', params: { length: 21 } }] })),
  )
  const fits = () => page.evaluate(() => document.documentElement.scrollWidth <= document.documentElement.clientWidth)
  for (const path of ['/combo/discovery', '/combo/configure?template=ema_rsi', '/combo/optimize?template=ema_rsi']) {
    await page.goto(path)
    await expect(page.getByTestId('asset-picker')).toBeVisible()
    await search(page, 'waves')
    await expect(row(page, 'WAVES/USDT')).toBeVisible()
    expect(await fits(), `${path} sem rolagem horizontal`).toBe(true)
  }
  catalog.setScenario('crypto-down')
  await page.goto('/combo/discovery')
  await expect(page.getByTestId('catalog-down')).toBeVisible()
  await page.getByRole('button', { name: 'Tentar de novo' }).scrollIntoViewIfNeeded()
  const retry = await page.getByRole('button', { name: 'Tentar de novo' }).boundingBox()
  expect(retry?.height).toBeGreaterThanOrEqual(44)
  expect(await fits()).toBe(true)
})

// --- Combo -----------------------------------------------------------------------------------

async function comboMocks(page: Page) {
  const catalog = await baseMocks(page)
  const posts: Array<{ url: string; body: any }> = []
  await page.route('**/api/combos/meta/ema_rsi', (route) =>
    route.fulfill(
      json({
        name: 'ema_rsi',
        description: 'EMA + RSI',
        indicators: [{ type: 'ema', alias: 'ema', params: { length: 21 } }],
        entry_logic: 'close > ema',
        exit_logic: 'close < ema',
        stop_loss: 0.02,
        optimization_schema: { ema_length: { min: 5, max: 20, step: 1 } },
      }),
    ),
  )
  await page.route('**/api/combos/backtest/batch', async (route) => {
    posts.push({ url: 'batch', body: JSON.parse(route.request().postData() || '{}') })
    await route.fulfill(json({ job_id: 'job-1117' }))
  })
  await page.route('**/api/combos/backtest/batch/job-1117', (route) =>
    route.fulfill(
      json({
        job_id: 'job-1117',
        status: 'running',
        processed: 0,
        total: 2,
        succeeded: 0,
        failed: 0,
        skipped: 0,
        errors: [],
        started_at: null,
        elapsed_sec: 0,
        estimated_remaining_sec: null,
        current_symbol: 'BTC/USDT',
      }),
    ),
  )
  await page.route('**/api/combos/optimize', async (route) => {
    posts.push({ url: 'optimize', body: JSON.parse(route.request().postData() || '{}') })
    await route.fulfill(
      json({
        job_id: 'o1',
        template_name: 'ema_rsi',
        symbol: 'BTC/USDT',
        timeframe: '1d',
        stages: [{ stage_num: 1, stage_name: 'Fase 1', values: [1, 2] }],
        best_parameters: { ema_length: 10 },
        best_metrics: { total_return: 0.1, win_rate: 0.5, sharpe_ratio: 1.2, total_trades: 12 },
      }),
    )
  })
  await page.route('**/api/favorites/exists**', (route) => route.fulfill(json({ exists: false })))
  return { catalog, posts }
}

test.describe('seletor de ativos no Combo', () => {
  test('padrão BTC/USDT, sem rádio Todos/Seleciona, Top 10 só com negociáveis e Limpar (1 ativo)', async ({ page }) => {
    await comboMocks(page)
    await page.goto('/combo/configure?template=ema_rsi')
    await expect(page.getByTestId('asset-picker')).toBeVisible()
    await expect(page.locator('input[type=radio][name=scope]')).toHaveCount(0)
    await expect(page.getByTestId('asset-count')).toContainText('1 selecionado · 1 cripto')
    await expect(chip(page, 'BTC/USDT')).toBeVisible()
    await expect(page.getByTestId('combo-run-copy')).toHaveText('1 ativo selecionado: otimiza, salva em favoritos e abre a página de favoritos.')

    await page.getByTestId('combo-top10').click()
    // MATIC/USDT não existe como negociável na amostra: entram os 9 negociáveis do Top 10
    await expect(page.getByTestId('asset-count')).toContainText('9 selecionados · 9 cripto')
    await expect(chip(page, 'ETH/USDT')).toBeVisible()
    await expect(chip(page, 'MATIC/USDT')).toHaveCount(0)
    await expect(page.getByTestId('asset-clear')).toHaveText('Limpar (1 ativo)')
    await page.getByTestId('asset-clear').click()
    await expect(page.getByTestId('asset-count')).toContainText('1 selecionado · 1 cripto')
    await expect(chip(page, 'BTC/USDT')).toBeVisible()

    // remover o último chip volta ao padrão
    await chip(page, 'BTC/USDT').getByRole('button').click()
    await expect(chip(page, 'BTC/USDT')).toBeVisible()
  })

  test('só ação: a cópia sob Otimizar avisa antes do clique e Otimizar não executa nem salva', async ({ page }) => {
    const { posts } = await comboMocks(page)
    await page.goto('/combo/configure?template=ema_rsi')
    await search(page, 'nvda')
    await row(page, 'NVDA').locator('input').check()
    await row(page, 'NVDA').scrollIntoViewIfNeeded()
    await chip(page, 'BTC/USDT').getByRole('button').click()
    await expect(page.getByTestId('combo-run-copy')).toContainText(
      'Nada será executado nem salvo: NVDA (Ação) — a análise ainda não está disponível para ações e ETFs.',
    )
    await expect(page.getByTestId('combo-run-copy')).not.toContainText('favoritos')
    await page.getByTestId('combo-run').click()
    const warning = page.getByTestId('run-warning')
    await expect(warning).toContainText('Análise ainda não disponível para ações e ETFs')
    await expect(warning).toContainText('Nada foi executado nem salvo. A seleção foi mantida.')
    expect(posts).toEqual([])
    await expect(chip(page, 'NVDA')).toBeVisible()
  })

  test('lote misto roda só os pares cripto e o aviso lista o que ficou fora', async ({ page }) => {
    const { posts } = await comboMocks(page)
    await page.goto('/combo/configure?template=ema_rsi')
    for (const symbol of ['ETH/USDT', 'NVDA', 'SPY']) {
      await search(page, symbol)
      await row(page, symbol).locator('input').check()
    }
    await expect(page.getByTestId('combo-run-copy')).toContainText('2 pares cripto: batch. Cada resultado é salvo em favoritos. Fora: NVDA (Ação), SPY (ETF)')
    await page.getByTestId('combo-run').click()
    await expect(page.getByTestId('run-warning')).toContainText('Lote iniciado com 2 pares cripto')
    await expect(page.getByTestId('run-warning')).toContainText('Fora do lote: NVDA (Ação), SPY (ETF)')
    await expect(page.getByTestId('batch-progress')).toContainText('0 de 2 ativos')
    expect(posts).toHaveLength(1)
    expect(posts[0].body.symbols).toEqual(['BTC/USDT', 'ETH/USDT'])
  })

  test('ativo marcado não entra pela pesquisa nem pelo Top 10 e Otimizar roda só o BTC', async ({ page }) => {
    const { posts } = await comboMocks(page)
    await page.goto('/combo/configure?template=ema_rsi')
    await search(page, 'waves')
    await expect(row(page, 'WAVES/USDT').locator('input')).toBeDisabled()
    await row(page, 'WAVES/USDT').click({ position: { x: 40, y: 10 } })
    await expect(chip(page, 'WAVES/USDT')).toHaveCount(0)
    await page.getByTestId('combo-top10').click()
    await expect(chip(page, 'WAVES/USDT')).toHaveCount(0)
    await page.getByTestId('asset-clear').click()
    await page.getByTestId('combo-run').click()
    await expect.poll(() => posts.length).toBe(1)
    expect(posts[0].url).toBe('optimize')
    expect(posts[0].body.symbol).toBe('BTC/USDT')
  })
})

// --- Otimização ---------------------------------------------------------------------------------

async function optimizeMocks(page: Page) {
  const { catalog, posts } = await comboMocks(page)
  await page.route('**/api/combos/templates/ema_rsi/metadata', (route) =>
    route.fulfill(json({ indicators: [{ type: 'ema', alias: 'ema', params: { length: 21 } }] })),
  )
  return { catalog, posts }
}

test.describe('seletor de ativos na Otimização', () => {
  test('sem campo de texto livre, com vários ativos e Todos do filtro', async ({ page }) => {
    await optimizeMocks(page)
    await page.goto('/combo/optimize?template=ema_rsi')
    await expect(page.locator('input[type=text]')).toHaveCount(0)
    await expect(page.getByTestId('asset-picker')).toBeVisible()
    await expect(page.getByTestId('asset-select-all')).toBeVisible()
    await expect(chip(page, 'BTC/USDT')).toBeVisible()
    await search(page, 'eth')
    await row(page, 'ETH/USDT').locator('input').check()
    await expect(page.getByTestId('asset-count')).toContainText('2 selecionados · 2 cripto')
    await expect(page.getByTestId('opt-run-copy')).toContainText('2 ativos: lote, uma otimização por ativo')
  })

  test('1 par roda como hoje: POST /combos/optimize e resultado no painel', async ({ page }) => {
    const { posts } = await optimizeMocks(page)
    await page.goto('/combo/optimize?template=ema_rsi')
    await expect(page.getByTestId('opt-run-copy')).toHaveText('1 ativo: otimiza e mostra o resultado ao lado.')
    await expect(page.getByTestId('run-optimization')).toBeEnabled()
    await page.getByTestId('run-optimization').click()
    await expect(page.getByText('Optimization Complete')).toBeVisible()
    expect(posts.map((p) => p.url)).toEqual(['optimize'])
    expect(posts[0].body.symbol).toBe('BTC/USDT')
  })

  test('BTC+ETH+QQQ roda o lote com 2 pares, QQQ fora e progresso 0 de 2 ativos', async ({ page }) => {
    const { posts } = await optimizeMocks(page)
    await page.goto('/combo/optimize?template=ema_rsi')
    for (const symbol of ['ETH/USDT', 'QQQ']) {
      await search(page, symbol)
      await row(page, symbol).locator('input').check()
    }
    await page.getByTestId('run-optimization').click()
    await expect(page.getByTestId('run-warning')).toContainText('Lote iniciado com 2 pares cripto')
    await expect(page.getByTestId('run-warning')).toContainText('Fora do lote: QQQ (ETF)')
    await expect(page.getByTestId('batch-progress')).toContainText('0 de 2 ativos')
    await expect(page.getByRole('button', { name: 'Pausar' })).toBeVisible()
    await expect(page.getByRole('button', { name: 'Encerrar' })).toBeVisible()
    expect(posts.map((p) => p.url)).toEqual(['batch'])
    expect(posts[0].body.symbols).toEqual(['BTC/USDT', 'ETH/USDT'])
    expect(posts[0].body.template_name).toBe('ema_rsi')
  })

  test('só QQQ: nada roda e a tela explica', async ({ page }) => {
    const { posts } = await optimizeMocks(page)
    await page.goto('/combo/optimize?template=ema_rsi&symbol=QQQ')
    await expect(chip(page, 'QQQ')).toBeVisible()
    await expect(page.getByTestId('opt-run-copy')).toContainText('Nada será executado: QQQ (ETF)')
    await page.getByTestId('run-optimization').click()
    await expect(page.getByTestId('run-warning')).toContainText('Análise ainda não disponível para ações e ETFs')
    await expect(page.getByTestId('run-warning')).toContainText('Nada foi executado. A seleção foi mantida.')
    expect(posts).toEqual([])
  })

  test('?symbol= fora do catálogo não marca nada e avisa; ?symbol= marcado entra como "fica de fora"', async ({ page }) => {
    const { posts } = await optimizeMocks(page)
    await page.goto('/combo/optimize?template=ema_rsi&symbol=XYZ/USDT')
    await expect(page.getByTestId('asset-not-found')).toContainText('XYZ/USDT não está no catálogo da Binance')
    await expect(page.getByTestId('asset-count')).toContainText('0 selecionados')
    await expect(page.getByTestId('asset-chips')).toContainText('Nenhum ativo selecionado.')

    await page.goto('/combo/optimize?template=ema_rsi&symbol=WAVES/USDT')
    await expect(chip(page, 'WAVES/USDT')).toContainText('fica de fora')
    await expect(page.getByTestId('opt-run-copy')).toContainText('Nada será executado: WAVES/USDT (Cripto, Suspenso)')
    await page.getByTestId('run-optimization').click()
    await expect(page.getByTestId('run-warning')).toContainText('Ativo marcado pela Binance não entra em análise nova')
    expect(posts).toEqual([])

    await page.goto('/combo/optimize?template=ema_rsi&symbol=NVDA')
    await expect(chip(page, 'NVDA')).toBeVisible()
    await expect(chip(page, 'NVDA')).not.toContainText('fica de fora')
  })

  test('Cripto → Todos do filtro soma só os negociáveis e a confirmação mostra os marcados', async ({ page }) => {
    await optimizeMocks(page)
    await page.goto('/combo/optimize?template=ema_rsi')
    await page.getByRole('button', { name: /^Cripto/ }).click()
    await expect(page.getByTestId('asset-select-all')).toHaveText('Todos do filtro (12)')
    await page.getByTestId('asset-select-all').click()
    await expect(page.getByRole('alertdialog')).toContainText('2 ativos marcados ficam de fora')
    await page.keyboard.press('Escape')
    await expect(page.getByTestId('asset-select-all')).toBeFocused()
    await page.getByTestId('asset-select-all').click()
    await page.getByTestId('asset-confirm-ok').click()
    await expect(page.getByTestId('asset-count')).toContainText('12 selecionados · 12 cripto')
    await expect(page.getByTestId('opt-run-copy')).toContainText('12 ativos: lote')
  })
})
