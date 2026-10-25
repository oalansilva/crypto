import { expect, test, type Page } from '@playwright/test'
import { covered, defaultCatalog, mockAssetCatalog, tf as coverageFrame } from './helpers/assetCatalogMock'
import { INTRABAR, installLoteApi } from './helpers/lote1120'

/**
 * Card #1120 (tarefa 4.6 e 5.5): compara as três rotas entregues com o protótipo aprovado, em navegador
 * real, a 1440 e a 390 px. O protótipo é a spec de UI (frontend/public/prototypes/card-1120-lote-multiclasse/):
 * mesmos textos, mesmos componentes, mesmos estados e a mesma geometria. Cada comparação registra o
 * resultado no anexo `comparacao-<tela>-<largura>.json` do teste.
 *
 * Desvios aceitos e justificados (detalhe de Apply, design.md "P3 aceitos"): números, datas, ids, tempos e
 * páginas de coleta são amostra; a linha "Otimizando" não tem o contador "tentativa N de M" (o contrato da API
 * só traz o progresso da coleta); o painel Demonstração não vai para o produto.
 */

const PROTO = '/prototypes/card-1120-lote-multiclasse'
const ADMIN_USER = { id: 'discovery-admin', email: 'alan@example.com', name: 'Alan Silva', isAdmin: true, mustChangePassword: false }
const VIEWPORTS = [
  { width: 1440, height: 900 },
  { width: 390, height: 844 },
]
const json = (body: unknown) => ({ status: 200, contentType: 'application/json', body: JSON.stringify(body) })

const norm = (text: string | null | undefined) => (text ?? '').replace(/\s+/g, ' ').trim()

interface Probe {
  text: string
  w: number
  h: number
  fontSize: string
  fontWeight: string
  color: string
  background: string
  radius: string
  display: string
}

async function probe(page: Page, selector: string): Promise<Probe | null> {
  await page.mouse.move(0, 0) // sem :hover vindo do clique anterior
  const el = page.locator(selector).first()
  if ((await el.count()) === 0) return null
  return el.evaluate((node) => {
    const style = getComputedStyle(node)
    const rect = node.getBoundingClientRect()
    return {
      text: (node.textContent ?? '').replace(/\s+/g, ' ').trim(),
      w: Math.round(rect.width),
      h: Math.round(rect.height),
      fontSize: style.fontSize,
      fontWeight: style.fontWeight,
      color: style.color,
      background: style.backgroundColor,
      radius: style.borderRadius,
      display: style.display,
    }
  })
}

interface Pair {
  name: string
  proto: string
  product: string
  /** Largura/altura aceitam diferença de até `tol` px; o texto e o estilo, nenhuma. */
  tol?: number
  skipText?: boolean
  skipStyle?: boolean
}

async function compare(protoPage: Page, productPage: Page, pairs: Pair[], sink: Array<Record<string, unknown>>) {
  for (const pair of pairs) {
    const a = await probe(protoPage, pair.proto)
    const b = await probe(productPage, pair.product)
    expect(a, `protótipo tem ${pair.proto}`).not.toBeNull()
    expect(b, `produto tem ${pair.product}`).not.toBeNull()
    const result: Record<string, unknown> = { name: pair.name, proto: a, product: b }
    sink.push(result)
    if (!pair.skipText) expect(b!.text, `${pair.name}: texto`).toBe(a!.text)
    if (!pair.skipStyle) {
      for (const key of ['fontSize', 'fontWeight', 'color', 'background', 'radius', 'display'] as const) {
        expect(b![key], `${pair.name}: ${key}`).toBe(a![key])
      }
    }
    const tol = pair.tol ?? 2
    expect(Math.abs(b!.w - a!.w), `${pair.name}: largura ${a!.w} x ${b!.w}`).toBeLessThanOrEqual(tol)
    expect(Math.abs(b!.h - a!.h), `${pair.name}: altura ${a!.h} x ${b!.h}`).toBeLessThanOrEqual(tol)
  }
}

async function productMocks(page: Page, options: { nvdaFiveMinutes?: boolean } = {}) {
  await page.addInitScript((user) => {
    localStorage.setItem('auth_access_token', 'admin-token')
    localStorage.setItem('auth_refresh_token', 'admin-refresh')
    localStorage.setItem('auth_user', JSON.stringify(user))
    localStorage.setItem('cripto-farol-onboarding-dismissed', '1')
  }, ADMIN_USER)
  await page.route('**/api/**', (route) => route.fulfill(json({})))
  await page.route('**/api/auth/me', (route) => route.fulfill(json(ADMIN_USER)))
  await page.route('**/api/combos/templates', (route) =>
    route.fulfill(json({ prebuilt: [{ name: 'multi_ma_crossover', display_name: 'Médias: tendência', description: 'x' }], examples: [], custom: [] })),
  )
  await page.route('**/api/combos/meta/multi_ma_crossover', (route) =>
    route.fulfill(
      json({
        name: 'multi_ma_crossover',
        display_name: 'Médias: tendência',
        description: 'Cruzamento de médias',
        indicators: [{ type: 'ema', alias: 'ema', params: { length: 21 } }],
        entry_logic: 'close > ema',
        exit_logic: 'close < ema',
        stop_loss: 0.02,
        optimization_schema: { ema_length: { min: 5, max: 20, step: 1 } },
      }),
    ),
  )
  await page.route('**/api/combos/templates/multi_ma_crossover/metadata', (route) =>
    route.fulfill(json({ indicators: [{ type: 'ema', alias: 'ema', params: { length: 21 } }] })),
  )
  const assets = defaultCatalog()
  if (options.nvdaFiveMinutes) {
    const nvda = assets.find((a) => a.symbol === 'NVDA')!
    nvda.history = covered([coverageFrame('5m', '2026-05-19T08:00:00Z', '2026-10-23T20:00:00Z')], { calendar_timezone: 'America/New_York' })
  }
  await mockAssetCatalog(page, { assets })
}

async function pick(page: Page, symbol: string) {
  await page.getByTestId('asset-search').fill(symbol)
  await expect(page.getByTestId('asset-results')).toBeVisible()
  await page.locator(`.ap-row[data-asset="${symbol}"] input`).check()
}

for (const viewport of VIEWPORTS) {
  test.describe(`comparação com o protótipo · ${viewport.width} px`, () => {
    test.use({ viewport })

    test('Combo: texto da classe, Market Data, tempos, cópia, Confirmar lote e painel do lote', async ({ browser }, testInfo) => {
      const log: Array<Record<string, unknown>> = []
      const protoPage = await (await browser.newContext({ viewport })).newPage()
      const productPage = await (await browser.newContext({ viewport })).newPage()
      await productMocks(productPage)
      const sim = await installLoteApi(productPage)
      await protoPage.goto(`${PROTO}/configure.html`)
      await productPage.goto('/combo/configure?template=multi_ma_crossover')
      await pick(productPage, 'NVDA')
      await pick(productPage, 'SPY')

      await compare(
        protoPage,
        productPage,
        [
          { name: 'nota da classe', proto: '[data-testid="asset-class-note"]', product: '[data-testid="asset-class-note"]' },
          { name: 'Market Data por ativo', proto: '[data-testid="combo-market-data"]', product: '[data-testid="combo-market-data"]' },
          { name: 'texto antes de rodar', proto: '[data-testid="combo-run-copy"]', product: '[data-testid="combo-run-copy"]', tol: 3 },
          { name: 'tempo 1m (só cripto)', proto: '#b20-tf option[value="1m"]', product: 'select option[value="1m"]', skipStyle: true },
          { name: 'tempo 5m (só cripto)', proto: '#b20-tf option[value="5m"]', product: 'select option[value="5m"]', skipStyle: true },
          { name: 'botão Otimizar', proto: '[data-testid="combo-run"]', product: '[data-testid="combo-run"]', skipText: false, tol: 2 },
        ],
        log,
      )
      // sob demanda: SPY e SOL/USDT dizem "coletado ao rodar o backtest ou o lote"
      await productPage.getByTestId('asset-search').fill('spy')
      const onDemand = await productPage.locator('.ap-row[data-asset="SPY"]').innerText()
      expect(norm(onDemand)).toContain('Histórico sob demanda · coletado ao rodar o backtest ou o lote')
      // o protótipo guarda o mesmo texto nas linhas sob demanda do seletor
      expect(norm(await protoPage.content())).toContain('Histórico sob demanda · coletado ao rodar o backtest ou o lote')

      // Confirmar lote: mesma estrutura, mesmos rótulos, mesma largura
      await protoPage.getByTestId('combo-run').click()
      await productPage.getByTestId('combo-run').click()
      await expect(productPage.getByTestId('batch-confirm-panel')).toBeVisible()
      await compare(
        protoPage,
        productPage,
        [
          { name: 'Confirmar: painel', proto: '[data-testid="batch-confirm-panel"]', product: '[data-testid="batch-confirm-panel"]', skipText: true, tol: 40 },
          { name: 'Confirmar: título', proto: '[data-testid="batch-confirm-panel"] h3', product: '[data-testid="batch-confirm-panel"] h3' },
          { name: 'Confirmar: Vão rodar', proto: '[data-testid="batch-confirm-panel"] dl > div:nth-child(1)', product: '[data-testid="batch-confirm-panel"] dl > div:nth-child(1)' },
          { name: 'Confirmar: coleta (rótulo e contagem)', proto: '[data-testid="batch-confirm-panel"] .b20-collect dt', product: '[data-testid="batch-confirm-panel"] .lote-collect dt' },
          { name: 'Confirmar: contagem', proto: '[data-testid="batch-need-count"]', product: '[data-testid="batch-need-count"]' },
          { name: 'Confirmar: Ficam fora', proto: '[data-testid="batch-confirm-panel"] dl > div:nth-child(3)', product: '[data-testid="batch-confirm-panel"] dl > div:nth-child(3)' },
          { name: 'Confirmar: Configuração', proto: '[data-testid="batch-config"]', product: '[data-testid="batch-config"]' },
          { name: 'Confirmar: Favoritos', proto: '[data-testid="batch-confirm-panel"] dl > div:nth-child(5)', product: '[data-testid="batch-confirm-panel"] dl > div:nth-child(5)' },
          { name: 'Confirmar: Confirmar e rodar', proto: '[data-testid="batch-confirm"]', product: '[data-testid="batch-confirm"]' },
          { name: 'Confirmar: Voltar', proto: '[data-testid="batch-back"]', product: '[data-testid="batch-back"]' },
        ],
        log,
      )
      // a coleta cita só o que falta guardar: "1 de 3" nos dois
      expect(norm(await productPage.getByTestId('batch-need-count').innerText())).toBe('1 de 3')
      expect(norm(await protoPage.getByTestId('batch-need-count').innerText())).toBe('1 de 3')
      // o texto da coleta do protótipo e do produto é o mesmo (SPY 1d e 5m do intrabar + quem já está guardado)
      expect(norm(await productPage.locator('[data-testid="batch-confirm-panel"] .lote-collect dd').innerText())).toBe(
        norm(await protoPage.locator('[data-testid="batch-confirm-panel"] .b20-collect dd').innerText()),
      )

      // Confirmar e rodar: o painel do lote
      await protoPage.getByTestId('batch-confirm').click()
      await productPage.getByTestId('batch-confirm').click()
      await expect(productPage.getByTestId('batch-panel')).toBeVisible()
      await compare(
        protoPage,
        productPage,
        [
          { name: 'Painel: caixa', proto: '[data-testid="batch-panel"]', product: '[data-testid="batch-panel"]', skipText: true, tol: 60 },
          { name: 'Painel: título e selo', proto: '[data-testid="batch-panel"] h3', product: '[data-testid="batch-panel"] h3' },
          { name: 'Painel: selo', proto: '[data-testid="batch-status"]', product: '[data-testid="batch-status"]' },
          { name: 'Painel: tempo', proto: '.b20-bmeta', product: '.lote-bmeta' },
          { name: 'Painel: linha viva', proto: '[data-testid="batch-live"]', product: '[data-testid="batch-live"]' },
          { name: 'Painel: barra', proto: '.b20-bar', product: '.lote-bar', skipText: true },
          { name: 'Painel: filtro Todos', proto: '.b20-chip[data-chip="all"]', product: '.lote-chip[data-chip="all"]' },
          { name: 'Painel: filtro Sucesso', proto: '.b20-chip[data-chip="success"]', product: '.lote-chip[data-chip="success"]' },
          { name: 'Painel: BTC/USDT ativo', proto: '.b20-row[data-asset="BTC/USDT"] .b20-asset', product: '.lote-row[data-asset="BTC/USDT"] .lote-asset' },
          { name: 'Painel: BTC/USDT estado', proto: '.b20-row[data-asset="BTC/USDT"] .b20-state', product: '.lote-row[data-asset="BTC/USDT"] .lote-state' },
          { name: 'Painel: NVDA ativo', proto: '.b20-row[data-asset="NVDA"] .b20-asset', product: '.lote-row[data-asset="NVDA"] .lote-asset' },
          { name: 'Painel: NVDA estado', proto: '.b20-row[data-asset="NVDA"] .b20-state', product: '.lote-row[data-asset="NVDA"] .lote-state' },
          { name: 'Painel: SPY ativo', proto: '.b20-row[data-asset="SPY"] .b20-asset', product: '.lote-row[data-asset="SPY"] .lote-asset' },
          { name: 'Painel: SPY estado', proto: '.b20-row[data-asset="SPY"] .b20-state', product: '.lote-row[data-asset="SPY"] .lote-state' },
          { name: 'Painel: SPY detalhe', proto: '.b20-row[data-asset="SPY"] .b20-detail', product: '.lote-row[data-asset="SPY"] .lote-detail', tol: 40 },
          { name: 'Painel: Pausar', proto: '[data-testid="batch-pause"]', product: '[data-testid="batch-pause"]' },
          { name: 'Painel: Encerrar', proto: '[data-testid="batch-cancel"]', product: '[data-testid="batch-cancel"]' },
        ],
        log,
      )

      // a11y: mesmos papéis e atributos
      for (const [protoSel, productSel, attr, value] of [
        ['[data-testid="batch-live"]', '[data-testid="batch-live"]', 'role', 'status'],
        ['[data-testid="batch-live"]', '[data-testid="batch-live"]', 'aria-live', 'polite'],
        ['.b20-bar', '.lote-bar', 'role', 'progressbar'],
        ['.b20-bar', '.lote-bar', 'aria-label', 'Ativos concluídos'],
        ['.b20-chips', '.lote-chips', 'role', 'group'],
        ['.b20-chips', '.lote-chips', 'aria-label', 'Filtrar por estado'],
        ['.b20-list', '.lote-list', 'aria-labelledby', 'b20-batch-title'],
      ] as const) {
        const a = await protoPage.locator(protoSel).first().getAttribute(attr)
        const b = await productPage.locator(productSel).first().getAttribute(attr)
        expect(a === 'b20-batch-title' ? 'lote-batch-title' : a, `${productSel} ${attr}`).toBe(b)
        expect(b).toBe(value === 'b20-batch-title' ? 'lote-batch-title' : value)
      }
      expect(await productPage.locator('.lote-chip').first().getAttribute('aria-pressed')).toBe('true')
      expect(await productPage.getByTestId('batch-panel').locator('h3').getAttribute('tabindex')).toBe('-1')
      expect(await protoPage.getByTestId('batch-panel').locator('h3').getAttribute('tabindex')).toBe('-1')

      // alvos de 44 px nos botões do painel
      for (const id of ['batch-pause', 'batch-cancel']) {
        const box = await productPage.getByTestId(id).boundingBox()
        expect(box!.height).toBeGreaterThanOrEqual(43.5)
      }
      // sem rolagem horizontal
      for (const p of [protoPage, productPage]) {
        expect(await p.evaluate(() => document.documentElement.scrollWidth <= document.documentElement.clientWidth)).toBe(true)
      }
      // lista em colunas a 1440 e em cartões a 390 (container query, 620 px de largura do painel)
      const listhead = await productPage.locator('.lote-listhead').evaluate((el) => getComputedStyle(el).display)
      const protoListhead = await protoPage.locator('.b20-listhead').evaluate((el) => getComputedStyle(el).display)
      expect(listhead).toBe(protoListhead)
      log.push({ name: 'estado final do painel', calls: sim.calls.length, listhead, protoListhead })
      await testInfo.attach(`comparacao-combo-${viewport.width}.json`, { body: JSON.stringify(log, null, 2), contentType: 'application/json' })
    })

    test('Otimização: Confirmar e painel na coluna larga, no lugar de "Ready to Optimize"', async ({ browser }, testInfo) => {
      const log: Array<Record<string, unknown>> = []
      const protoPage = await (await browser.newContext({ viewport })).newPage()
      const productPage = await (await browser.newContext({ viewport })).newPage()
      await productMocks(productPage, { nvdaFiveMinutes: true })
      await installLoteApi(productPage)
      await protoPage.goto(`${PROTO}/optimize.html`)
      await productPage.goto('/combo/optimize?template=multi_ma_crossover&timeframe=1d')
      await pick(productPage, 'NVDA')
      await pick(productPage, 'SPY')
      await compare(
        protoPage,
        productPage,
        [
          { name: 'nota da classe', proto: '[data-testid="asset-class-note"]', product: '[data-testid="asset-class-note"]' },
          { name: 'texto antes de rodar', proto: '[data-testid="opt-run-copy"], #b20-runcopy', product: '[data-testid="opt-run-copy"]', tol: 3 },
          { name: 'tempo 30m (só cripto)', proto: '#b20-tf option[value="30m"]', product: 'select option[value="30m"]', skipStyle: true },
        ],
        log,
      )
      await expect(protoPage.getByText('Ready to Optimize')).toBeVisible()
      await expect(productPage.getByText('Ready to Optimize')).toBeVisible()
      await protoPage.getByTestId('run-optimization').click()
      await productPage.getByTestId('run-optimization').click()
      await expect(productPage.getByTestId('batch-confirm-panel')).toBeVisible()
      await expect(protoPage.getByText('Ready to Optimize')).toBeHidden()
      await expect(productPage.getByText('Ready to Optimize')).toHaveCount(0)
      await compare(
        protoPage,
        productPage,
        [
          { name: 'Confirmar: título', proto: '[data-testid="batch-confirm-panel"] h3', product: '[data-testid="batch-confirm-panel"] h3' },
          { name: 'Confirmar: contagem', proto: '[data-testid="batch-need-count"]', product: '[data-testid="batch-need-count"]' },
          { name: 'Confirmar: Configuração', proto: '[data-testid="batch-config"]', product: '[data-testid="batch-config"]' },
        ],
        log,
      )
      // o Confirmar ocupa a coluna larga: mesma posição horizontal e largura nos dois
      const protoBox = await protoPage.getByTestId('batch-confirm-panel').boundingBox()
      const productBox = await productPage.getByTestId('batch-confirm-panel').boundingBox()
      log.push({ name: 'Confirmar: caixa na coluna larga', proto: protoBox, product: productBox })
      if (viewport.width === 1440) {
        expect(productBox!.width).toBeGreaterThan(620)
        expect(Math.abs(productBox!.width - protoBox!.width)).toBeLessThanOrEqual(40)
        expect(Math.abs(productBox!.x - protoBox!.x)).toBeLessThanOrEqual(40)
      }
      await protoPage.getByTestId('batch-confirm').click()
      await productPage.getByTestId('batch-confirm').click()
      await expect(productPage.getByTestId('batch-panel')).toBeVisible()
      await compare(
        protoPage,
        productPage,
        [
          { name: 'Painel: título e selo', proto: '[data-testid="batch-panel"] h3', product: '[data-testid="batch-panel"] h3' },
          { name: 'Painel: BTC/USDT estado', proto: '.b20-row[data-asset="BTC/USDT"] .b20-state', product: '.lote-row[data-asset="BTC/USDT"] .lote-state' },
          { name: 'Painel: Pausar', proto: '[data-testid="batch-pause"]', product: '[data-testid="batch-pause"]' },
        ],
        log,
      )
      const listhead = await productPage.locator('.lote-listhead').evaluate((el) => getComputedStyle(el).display)
      const protoListhead = await protoPage.locator('.b20-listhead').evaluate((el) => getComputedStyle(el).display)
      expect(listhead).toBe(protoListhead)
      for (const p of [protoPage, productPage]) {
        expect(await p.evaluate(() => document.documentElement.scrollWidth <= document.documentElement.clientWidth)).toBe(true)
      }
      await testInfo.attach(`comparacao-otimizacao-${viewport.width}.json`, { body: JSON.stringify(log, null, 2), contentType: 'application/json' })
    })

    test('Favoritos: lista única, filtro Classe, faixa do lote e blocos novos da linha e do cartão', async ({ browser }, testInfo) => {
      const log: Array<Record<string, unknown>> = []
      const protoPage = await (await browser.newContext({ viewport })).newPage()
      const productPage = await (await browser.newContext({ viewport })).newPage()
      await favoritesMocks(productPage)
      await protoPage.goto(`${PROTO}/index.html`)
      await productPage.goto('/favorites')
      await expect(productPage.getByTestId('favorites-renewal-ok')).toBeVisible()

      const mobile = viewport.width < 768
      const scope = mobile ? '-mobile' : ''
      const pairs: Pair[] = [
        { name: 'filtro Classe: rótulo', proto: '.fav-filters label:nth-child(1) > span', product: '.fav-filters label:nth-child(1) > span' },
        { name: 'filtro Classe: select', proto: '[data-testid="fav-class-filter"]', product: '[data-testid="fav-class-filter"]', skipText: true },
        { name: 'nota das estrelas', proto: '[data-testid="fav-tier-note"]', product: '[data-testid="fav-tier-note"]' },
      ]
      await compare(protoPage, productPage, pairs, log)
      const optionTexts = async (page: Page) => page.locator('[data-testid="fav-class-filter"] option').allTextContents()
      expect(await optionTexts(productPage)).toEqual(await optionTexts(protoPage))
      const columns = (page: Page) => page.locator('.fav-filters').evaluate((el) => getComputedStyle(el).gridTemplateColumns.split(' ').length)
      expect(await columns(productPage)).toBe(await columns(protoPage))

      const blocks: Pair[] = []
      for (const id of [104, 101, 102, 105, 103]) {
        const rowSel = mobile ? `[data-testid="favorite-${id}-mobile"]` : `[data-testid="favorite-${id}"]`
        for (const testid of ['fav-precision', 'fav-conventions', 'fav-effective']) {
          blocks.push({ name: `${id} ${testid}`, proto: `${rowSel} [data-testid="${testid}"]`, product: `${rowSel} [data-testid="${testid}"]`, tol: 3 })
        }
        // P3 de Apply: na tabela o par classe · moeda não se parte em duas linhas (o protótipo quebrava "Ação ·" e "USD")
        blocks.push({
          name: `${id} classe e moeda`,
          proto: mobile ? `${rowSel} .b20-cardline` : `${rowSel} .b20-symline`,
          product: mobile ? `${rowSel} .lote-cardline` : `${rowSel} .lote-symline`,
          tol: mobile ? 3 : 200,
        })
      }
      for (const id of [104, 105]) {
        const rowSel = mobile ? `[data-testid="favorite-${id}-mobile"]` : `[data-testid="favorite-${id}"]`
        blocks.push({ name: `${id} "Limitações e origem"`, proto: `${rowSel} [data-testid="fav-more-info"] summary`, product: `${rowSel} [data-testid="fav-more-info"] summary`, tol: 3 })
        blocks.push({ name: `${id} pendência da classe`, proto: `${rowSel} [data-testid="fav-equity-pending"]`, product: `${rowSel} [data-testid="fav-equity-pending"]`, tol: 6 })
      }
      await compare(protoPage, productPage, blocks, log)

      if (!mobile) {
        // sem o "USD" sozinho na segunda linha: o produto nunca fica mais alto que o protótipo nessa célula
        for (const id of [104, 101, 102, 105, 103]) {
          const a = await probe(protoPage, `[data-testid="favorite-${id}"] .b20-symline`)
          const b = await probe(productPage, `[data-testid="favorite-${id}"] .lote-symline`)
          expect(b!.h, `classe · moeda de ${id} em uma linha`).toBeLessThanOrEqual(a!.h)
          expect(b!.h).toBeLessThanOrEqual(20)
        }
      }

      // ordem das linhas: mesma ordenação por Ret/T %
      const order = (page: Page) =>
        page.locator(mobile ? '.fav-mobile-card' : 'table.fav-strategies tbody tr[data-favorite-id]').evaluateAll((els) => els.map((el) => el.getAttribute('data-favorite-id')))
      await expect.poll(() => order(productPage)).toEqual(await order(protoPage))

      // alturas das linhas/cartões: o produto fica perto do protótipo (descrição e apelido vivos são os mesmos)
      for (const id of [104, 101, 102, 105, 103]) {
        const sel = mobile ? `[data-testid="favorite-${id}-mobile"]` : `[data-testid="favorite-${id}"]`
        const a = await protoPage.locator(sel).boundingBox()
        const b = await productPage.locator(sel).boundingBox()
        log.push({ name: `altura ${id}`, proto: a?.height, product: b?.height })
        expect(Math.abs(b!.height - a!.height), `altura ${id}: ${a!.height} x ${b!.height}`).toBeLessThanOrEqual(mobile ? 70 : 40)
      }

      // controles desabilitados de ação/ETF: mesmos atributos
      for (const id of [104, 105]) {
        const sel = mobile ? `[data-testid="favorite-${id}-mobile"]` : `[data-testid="favorite-${id}"]`
        const protoOff = await protoPage.locator(`${sel} [data-b20-off]`).count()
        const productOff = await productPage.locator(`${sel} [data-lote-off]`).count()
        log.push({ name: `controles desabilitados ${id}`, proto: protoOff, product: productOff })
        expect(productOff).toBe(protoOff)
        const disabled = await productPage.locator(`${sel} [data-lote-off]`).evaluateAll((els) => els.map((el) => el.getAttribute('aria-disabled')))
        expect(disabled.every((v) => v === 'true')).toBe(true)
      }

      // filtro Classe e faixa do lote nos dois
      await protoPage.getByTestId('fav-class-filter').selectOption('stock')
      await productPage.getByTestId('fav-class-filter').selectOption('stock')
      const protoCount = norm(await protoPage.locator('[data-b20-count]').first().textContent())
      await expect(productPage.getByTestId('fav-count').first()).toHaveText(protoCount)
      await protoPage.getByTestId('fav-class-filter').selectOption('all')
      await productPage.getByTestId('fav-class-filter').selectOption('all')
      await protoPage.goto(`${PROTO}/index.html?lote=7f3c2a91`)
      await productPage.goto('/favorites?lote=7f3c2a91')
      await expect(productPage.getByTestId('fav-lote-filter')).toBeVisible()
      const bannerProto = await probe(protoPage, '[data-testid="fav-lote-filter"]')
      const bannerProduct = await probe(productPage, '[data-testid="fav-lote-filter"]')
      log.push({ name: 'faixa do lote', proto: bannerProto, product: bannerProduct })
      expect(bannerProduct!.text).toContain('Mostrando só o lote 7f3c2a91')
      expect(bannerProduct!.text).toContain('os favoritos gravados por ele, de todas as classes.')
      expect(bannerProduct!.text).toContain('Mostrar todos os favoritos')
      expect(bannerProduct!.background).toBe(bannerProto!.background)
      expect(bannerProduct!.radius).toBe(bannerProto!.radius)
      for (const p of [protoPage, productPage]) {
        expect(await p.evaluate(() => document.documentElement.scrollWidth <= document.documentElement.clientWidth)).toBe(true)
      }
      await testInfo.attach(`comparacao-favoritos-${viewport.width}.json`, { body: JSON.stringify(log, null, 2), contentType: 'application/json' })
      expect(scope).toBeDefined()
    })
  })
}

// ------------------------------------------------------------------------------------------ mocks de Favoritos

async function favoritesMocks(page: Page) {
  // mesmos cinco favoritos do protótipo (NVDA e SPY do lote com precisão diária, BTC/USDT intrabar, ETH/USDT antigo, SOL/USDT 4h)
  const mk = (id: number, symbol: string, cls: string, currency: string, extra: Record<string, unknown>) => ({
    id,
    name: `multi_ma_crossover - ${symbol} ${extra.timeframe ?? '1d'} (batch)`,
    symbol,
    timeframe: '1d',
    strategy_name: 'multi_ma_crossover',
    strategy_display_name: 'Médias: tendência',
    strategy_description: 'Cruzamento de médias a favor da tendência, com stop de 5%.',
    parameters: { direction: 'long', stop_loss: 0.05 },
    notify_telegram: true,
    created_at: '2026-10-24T21:40:00Z',
    start_date: null,
    end_date: null,
    auto_refresh_status: 'SUCCESS',
    auto_refresh_completed_at: '2026-10-24T12:12:00Z',
    asset: { symbol, asset_class: cls, currency },
    ...extra,
  })
  const daily = (first: string, from: string) => ({
    precision_requested: 'intrabar',
    precision_effective: 'candle',
    intraday_reason: 'coverage',
    intraday_missing: [{ from, to: '2026-05-18' }],
    timeframe: '1d',
    window: { covered: { start: first, end: '2026-10-23T04:00:00Z' } },
  })
  const batch = { batch_id: '7f3c2a91-0000-4000-8000-000000000001' }
  const conventions = { fee_confirmed: false, fraction: { simulated: true }, adjusted_prices: true, calendar: { sessions_per_year: 252 } }
  const favorites = [
    mk(104, 'NVDA', 'stock', 'USD', { tier: null, notes: 'gerado em lote (7f3c2a91)', auto_refresh_status: null, metrics: { total_return: 12.845, total_trades: 29, sharpe_ratio: 1.67, ...batch, execution: daily('2014-11-11T05:00:00Z', '2014-11-11'), conventions } }),
    mk(101, 'BTC/USDT', 'crypto', 'USDT', { tier: 3, notes: 'gerado em lote (7f3c2a91)', metrics: { total_return: 4.126, total_trades: 38, sharpe_ratio: 1.42, ...batch, execution: { ...INTRABAR, timeframe: '1d' } } }),
    mk(102, 'ETH/USDT', 'crypto', 'USDT', { tier: 2, notes: null, metrics: { total_return: 2.683, total_trades: 41, sharpe_ratio: 1.11 } }),
    mk(105, 'SPY', 'etf', 'USD', { tier: null, notes: 'gerado em lote (7f3c2a91)', auto_refresh_status: null, metrics: { total_return: 0.612, total_trades: 22, sharpe_ratio: 0.74, ...batch, execution: daily('2015-01-02T05:00:00Z', '2015-01-02'), conventions: { ...conventions, fee_confirmed: false } } }),
    mk(103, 'SOL/USDT', 'crypto', 'USDT', { tier: null, notes: null, timeframe: '4h', metrics: { total_return: 0.974, total_trades: 64, sharpe_ratio: 0.86, execution: { ...INTRABAR, timeframe: '4h', window: { covered: { start: '2020-08-11T00:00:00Z', end: '2026-10-24T00:00:00Z' } } } } }),
  ]
  await page.addInitScript((user) => {
    localStorage.setItem('auth_access_token', 'tok')
    localStorage.setItem('auth_refresh_token', 'ref')
    localStorage.setItem('auth_user', JSON.stringify(user))
    localStorage.setItem('cripto-farol-onboarding-dismissed', '1')
  }, ADMIN_USER)
  await page.route('**/api/**', async (route) => {
    const url = route.request().url()
    if (url.includes('/api/auth/me')) return route.fulfill(json(ADMIN_USER))
    if (/\/api\/favorites\/?(\?|$)/.test(url)) return route.fulfill(json(favorites))
    if (url.includes('/api/opportunities')) return route.fulfill(json([]))
    return route.fulfill(json({}))
  })
}
