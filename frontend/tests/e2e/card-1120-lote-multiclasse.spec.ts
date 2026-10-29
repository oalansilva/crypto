import { expect, test, type Page } from '@playwright/test'
import { covered, defaultCatalog, mockAssetCatalog, tf as coverageFrame } from './helpers/assetCatalogMock'
import {
  DAILY_NVDA,
  DAILY_SPY,
  INTRABAR,
  buildJob,
  installLoteApi,
  previewItem,
  previewOf,
  simItem,
} from './helpers/lote1120'

/**
 * Card #1120 (tarefa 4.6): lote multiclasse no Combo e na Otimização, com a API simulada, a 1440 e a 390 px.
 * Lote misto (BTC/USDT, NVDA, SPY), o mesmo em 5m, lote grande, pausa e retomada, encerrar e problemas.
 * O protótipo aprovado (frontend/public/prototypes/card-1120-lote-multiclasse/) é a spec de UI: os textos
 * abaixo são os dele. A comparação campo a campo com o protótipo está em card-1120-prototype-compare.spec.ts.
 */

const ADMIN_USER = {
  id: 'discovery-admin',
  email: 'alan@example.com',
  name: 'Alan Silva',
  isAdmin: true,
  mustChangePassword: false,
}
const TEMPLATES = [{ name: 'ema_rsi', display_name: 'Médias: tendência', description: 'x', is_readonly: true }]
const DESKTOP = { width: 1440, height: 900 }
const PHONE = { width: 390, height: 844 }

const pageErrors = new WeakMap<Page, string[]>()
test.beforeEach(({ page }) => {
  const errors: string[] = []
  pageErrors.set(page, errors)
  page.on('pageerror', (error) => errors.push(error.message))
})
test.afterEach(({ page }) => {
  expect(pageErrors.get(page) ?? [], 'sem erro de página não tratado').toEqual([])
})

const json = (body: unknown, status = 200) => ({ status, contentType: 'application/json', body: JSON.stringify(body) })
const fitsHorizontally = (page: Page) =>
  page.evaluate(() => document.documentElement.scrollWidth <= document.documentElement.clientWidth)

function catalogWithNvdaFiveMinutes() {
  const assets = defaultCatalog()
  const nvda = assets.find((a) => a.symbol === 'NVDA')!
  nvda.history = covered(
    [
      coverageFrame('1d', '2014-11-11T05:00:00Z', '2026-10-23T04:00:00Z'),
      coverageFrame('5m', '2026-05-19T08:00:00Z', '2026-10-23T20:00:00Z'),
    ],
    { calendar_timezone: 'America/New_York', note: 'Binance Ações · pregão regular de Nova York · ajustado por split' },
  )
  return assets
}

async function commonMocks(page: Page, options: { nvdaFiveMinutes?: boolean } = {}) {
  await page.addInitScript((user) => {
    localStorage.setItem('auth_access_token', 'admin-token')
    localStorage.setItem('auth_refresh_token', 'admin-refresh')
    localStorage.setItem('auth_user', JSON.stringify(user))
    localStorage.setItem('cripto-farol-onboarding-dismissed', '1')
  }, ADMIN_USER)
  await page.route('**/api/**', (route) => route.fulfill(json({})))
  await page.route('**/api/auth/me', (route) => route.fulfill(json(ADMIN_USER)))
  await page.route('**/api/combos/templates', (route) => route.fulfill(json({ prebuilt: TEMPLATES, examples: [], custom: [] })))
  await page.route('**/api/combos/meta/ema_rsi', (route) =>
    route.fulfill(
      json({
        name: 'ema_rsi',
        display_name: 'Médias: tendência',
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
  await mockAssetCatalog(page, { assets: options.nvdaFiveMinutes ? catalogWithNvdaFiveMinutes() : defaultCatalog() })
}

const row = (page: Page, symbol: string) => page.locator(`.ap-row[data-asset="${symbol}"]`)
async function pick(page: Page, symbol: string) {
  await page.getByTestId('asset-search').fill(symbol)
  await expect(page.getByTestId('asset-results')).toBeVisible()
  await row(page, symbol).locator('input').check()
}
const timeframeSelect = (page: Page) => page.locator('select').filter({ has: page.locator('option[value="1m"]') }).first()
const itemRow = (page: Page, symbol: string) => page.locator(`.lote-row[data-asset="${symbol}"]`)

const NOTE_COMBO =
  'Cripto, ação e ETF rodam juntos no lote: cada ativo usa a sua fonte, sessão, ajuste e moeda, e o melhor resultado de cada um vira favorito. Ação e ETF não rodam em 1m e 5m: nesses tempos ficam fora com o motivo. 1 ação ou ETF sozinha abre o resultado, sem salvar.'
const COPY_MIXED =
  'Lote de 3 ativos (1 cripto, 1 ação, 1 ETF): otimiza cada um com esta configuração e grava o melhor de cada em favoritos (nota "gerado em lote"). Antes de começar, você confirma o lote.'

async function mixedSelection(page: Page) {
  await pick(page, 'NVDA')
  await pick(page, 'SPY')
  await expect(page.getByTestId('asset-count')).toContainText('3 selecionados · 1 cripto · 1 ação · 1 ETF')
}

// ---------------------------------------------------------------------------------------------------- Combo

test.describe('Combo: lote multiclasse', () => {
  for (const viewport of [DESKTOP, PHONE]) {
    test(`lote misto de ponta a ponta: confirmar no fluxo, andamento, pausa, retomada e encerrar (${viewport.width} px)`, async ({ page }) => {
      await page.setViewportSize(viewport)
      await commonMocks(page)
      const sim = await installLoteApi(page)
      await page.goto('/combo/configure?template=ema_rsi')
      await mixedSelection(page)

      // texto da classe, fonte por ativo, tempos "(só cripto)" e o texto antes de rodar
      await expect(page.getByTestId('asset-class-note')).toHaveText(NOTE_COMBO)
      await expect(page.getByTestId('combo-market-data')).toHaveText('Por ativo: CCXT (cripto) · Binance Ações (ação e ETF)')
      await expect(timeframeSelect(page).locator('option[value="1m"]')).toHaveText('1 minute (só cripto)')
      await expect(timeframeSelect(page).locator('option[value="5m"]')).toHaveText('5 minutes (só cripto)')
      await expect(timeframeSelect(page).locator('option[value="1m"]')).toBeEnabled()
      await expect(page.getByTestId('combo-run-copy')).toHaveText(COPY_MIXED)
      await expect(page.getByTestId('combo-run-copy')).not.toContainText('o lote vem depois')
      await expect(page.getByTestId('combo-timeframe-hint')).toHaveCount(0) // seleção mista: sem o aviso de 1 ação sozinha

      // Otimizar abre o Confirmar no fluxo (sem modal), com o foco no título
      await page.getByTestId('combo-run').click()
      const panel = page.getByTestId('batch-confirm-panel')
      await expect(panel).toBeVisible()
      await expect(panel.getByRole('heading', { name: 'Confirmar lote de 3 ativos' })).toBeFocused()
      await expect(panel).toHaveAttribute('aria-labelledby', 'lote-confirm-title')
      await expect(page.locator('[role="dialog"]')).toHaveCount(0)
      await expect(panel).toContainText('3 — 1 cripto (USDT), 1 ação (USD), 1 ETF (USD): BTC/USDT, NVDA, SPY')
      await expect(page.getByTestId('batch-need-count')).toHaveText('1 de 3')
      await expect(panel).toContainText('SPY (1d e 5m do intrabar). BTC/USDT e NVDA já estão guardados, sem lacunas e atualizados.')
      await expect(panel).toContainText('Conta só o que a Binance tem para a janela e ainda não está guardado.')
      await expect(page.getByTestId('batch-out')).toHaveText('nenhum')
      await expect(page.getByTestId('batch-config')).toHaveText('Médias: tendência · 1d · todo o histórico · Long · Deep Backtest (15m)')
      await expect(panel).toContainText('o melhor de cada ativo, com a nota "gerado em lote"; ativo que já tem favorito no mesmo período e direção é pulado.')
      expect(sim.calls.filter((c) => c.path === 'preview')).toHaveLength(1)
      expect(sim.calls.find((c) => c.path === 'preview')!.body).toMatchObject({
        template_name: 'ema_rsi',
        symbols: ['BTC/USDT', 'NVDA', 'SPY'],
        timeframe: '1d',
        page: 'combo',
      })
      expect(sim.calls.some((c) => c.path === 'batch')).toBe(false) // nada começou ainda

      // Voltar fecha e devolve o foco ao botão de rodar
      await panel.getByTestId('batch-back').click()
      await expect(panel).toHaveCount(0)
      await expect(page.getByTestId('combo-run')).toBeFocused()

      // trocar o Período muda a Configuração do Confirmar
      await page.getByTestId('sel-period').selectOption('15d')
      await page.getByTestId('combo-run').click()
      await expect(page.getByTestId('batch-config')).toHaveText('Médias: tendência · 1d · 15 dias · Long · Deep Backtest (15m)')
      await page.getByTestId('batch-back').click()
      await page.getByTestId('sel-period').selectOption('all')

      // Confirmar e rodar: o painel do lote aparece no lugar, com o foco no título
      await page.getByTestId('combo-run').click()
      await page.getByTestId('batch-confirm').click()
      await expect(panel).toHaveCount(0)
      const batch = page.getByTestId('batch-panel')
      await expect(batch).toBeVisible()
      await expect(batch.getByRole('heading', { name: /Lote 7f3c2a91/ })).toBeFocused()
      expect(sim.calls.find((c) => c.path === 'batch')!.body).toMatchObject({ symbols: ['BTC/USDT', 'NVDA', 'SPY'], page: 'combo' })
      await expect(page.getByTestId('batch-status')).toHaveText('Rodando')
      await expect(page.getByTestId('batch-live')).toHaveAttribute('role', 'status')
      await expect(page.getByTestId('batch-live')).toHaveText('NVDA: otimizando.')
      await expect(page.getByRole('progressbar', { name: 'Ativos concluídos' })).toHaveAttribute('aria-valuenow', '1')
      await expect(itemRow(page, 'BTC/USDT')).toContainText('Sucesso')
      await expect(itemRow(page, 'BTC/USDT')).toContainText('Favorito gravado · 17 ago. 2017 – 24 out. 2026 · intrabar 15m · abrir em Favoritos')
      await expect(itemRow(page, 'BTC/USDT').locator('.lote-cls')).toHaveText('Cripto')
      await expect(itemRow(page, 'BTC/USDT').locator('.lote-cur')).toHaveText('USDT')
      await expect(itemRow(page, 'NVDA')).toContainText('Otimizando')
      await expect(itemRow(page, 'SPY')).toContainText('Na fila')
      await expect(itemRow(page, 'SPY')).toContainText('precisa de coleta: 1d e 5m do intrabar.')
      expect(await fitsHorizontally(page)).toBe(true)

      // etapas: NVDA grava com precisão diária e SPY coleta o 5m do intrabar, página 7 de 20
      sim.job!.items = [
        sim.job!.items[0],
        simItem(1, 'NVDA', 'success_daily', { execution: DAILY_NVDA, favorite_id: 104 }),
        simItem(2, 'SPY', 'collecting', { progress: '5m do intrabar · página 7 de 20', collect_kind: 'missing' }),
      ]
      Object.assign(sim.job!, buildJob(sim.job!.items, 'running'))
      await expect(itemRow(page, 'SPY')).toContainText('Coletando histórico')
      await expect(itemRow(page, 'SPY')).toContainText('5m do intrabar · página 7 de 20')
      await expect(itemRow(page, 'SPY').locator('progress')).toHaveAttribute('value', '7')
      await expect(page.getByTestId('batch-live')).toHaveText('SPY: coletando histórico.')
      await expect(itemRow(page, 'NVDA')).toContainText('Sucesso · precisão diária')
      await expect(page.getByTestId('batch-daily-note')).toContainText('Precisão diária em 1 ativo:')

      // Pausar → Pausando… (aria-disabled, foco fica) → Pausado → Retomar
      await page.getByTestId('batch-pause').focus()
      await page.getByTestId('batch-pause').click()
      const pausing = page.getByTestId('batch-pause')
      await expect(pausing).toHaveText('Pausando…')
      await expect(pausing).toHaveAttribute('aria-disabled', 'true')
      await expect(pausing).not.toHaveAttribute('disabled', /.*/)
      await expect(pausing).toBeFocused()
      await expect(page.getByTestId('batch-cancel')).toHaveAttribute('aria-disabled', 'true')
      await expect(page.getByTestId('batch-status')).toHaveText('Pausando')
      await expect(page.getByTestId('batch-live')).toContainText('Pausa pedida: o lote para quando SPY terminar a etapa em curso (coleta).')
      await page.getByTestId('batch-cancel').click({ force: true })
      expect(sim.calls.filter((c) => c.path === 'cancel')).toHaveLength(0) // aria-disabled: o clique não faz nada
      await pausing.click({ force: true })
      expect(sim.calls.filter((c) => c.path === 'pause')).toHaveLength(1) // o segundo clique em Pausando… não pede de novo
      sim.settle()
      await expect(page.getByTestId('batch-status')).toHaveText('Pausado')
      await expect(page.getByTestId('batch-resume')).toBeFocused()
      await expect(itemRow(page, 'SPY')).toContainText('Na fila')
      await expect(itemRow(page, 'SPY')).toContainText('histórico coletado; otimiza ao retomar, na mesma amostra.')
      await expect(page.getByTestId('batch-live')).toContainText('Pausado em 2 de 3. Os concluídos ficam; SPY espera.')

      // lote pausado bloqueia um lote novo (decisão 16)
      await page.getByTestId('combo-run').click()
      const blocked = page.getByTestId('batch-confirm-panel')
      await expect(blocked.getByRole('heading', { name: 'Há um lote pausado' })).toBeFocused()
      await expect(page.getByTestId('batch-paused-block')).toHaveText(
        'Retome ou encerre o lote 7f3c2a91 antes de começar outro. Encerrar mantém os 2 favoritos já gravados e marca o resto "Não rodou".',
      )
      await expect(blocked).not.toContainText('Confirmar e rodar')
      await expect(page.getByTestId('batch-confirm')).toHaveCount(0)
      await expect(page.getByTestId('batch-panel')).toBeVisible() // o painel do lote pausado segue visível
      for (const id of ['batch-block-resume', 'batch-block-cancel', 'batch-back']) {
        const box = await page.getByTestId(id).boundingBox()
        expect(box!.height).toBeGreaterThanOrEqual(43.5)
      }
      expect(sim.calls.filter((c) => c.path === 'preview')).toHaveLength(3) // o aviso nasce do estado local, sem novo plano
      await page.getByTestId('batch-back').click()
      await expect(page.getByTestId('combo-run')).toBeFocused()

      // Retomar: o mesmo lote volta a Rodando e o foco vai para Pausar
      await page.getByTestId('batch-resume').click()
      await expect(page.getByTestId('batch-status')).toHaveText('Rodando')
      await expect(page.getByTestId('batch-pause')).toBeFocused()
      expect(sim.calls.filter((c) => c.path === 'resume')).toHaveLength(1)

      // Encerrar: Encerrando… e depois Encerrado, com o foco no título do lote
      await page.getByTestId('batch-cancel').click()
      await expect(page.getByTestId('batch-cancel')).toHaveText('Encerrando…')
      sim.settle()
      await expect(page.getByTestId('batch-status')).toHaveText('Encerrado')
      await expect(page.getByRole('heading', { name: /Lote 7f3c2a91/ })).toBeFocused()
      await expect(itemRow(page, 'SPY')).toContainText('Não rodou')
      await expect(page.getByTestId('batch-live')).toHaveText(
        'Encerrado pelo usuário em 3 de 3. 2 favorito(s) gravado(s) ficam; não rodaram: SPY.',
      )
      const link = page.getByTestId('batch-open-favorites')
      await expect(link).toHaveText('Ver os 2 resultados do lote em Favoritos')
      await expect(link).toHaveAttribute('href', '/favorites?lote=7f3c2a91')
      await expect(page.getByTestId('batch-discovery')).toHaveText('Descoberta sistemática (varredura)')
      expect(await fitsHorizontally(page)).toBe(true)
    })
  }

  test('lote concluído: Concluído, 2 resultados, precisão diária e link para Favoritos', async ({ page }) => {
    await commonMocks(page)
    const sim = await installLoteApi(page)
    await page.goto('/combo/configure?template=ema_rsi')
    await mixedSelection(page)
    await page.getByTestId('combo-run').click()
    await page.getByTestId('batch-confirm').click()
    sim.job!.items = [
      simItem(0, 'BTC/USDT', 'success', { execution: INTRABAR, favorite_id: 101 }),
      simItem(1, 'NVDA', 'success_daily', { execution: DAILY_NVDA, favorite_id: 104 }),
      simItem(2, 'SPY', 'success_daily', { execution: DAILY_SPY, favorite_id: 105 }),
    ]
    Object.assign(sim.job!, buildJob(sim.job!.items, 'completed', { elapsed_sec: 133 }))
    await expect(page.getByTestId('batch-status')).toHaveText('Concluído')
    await expect(page.getByTestId('batch-live')).toHaveText('Lote concluído: 3 de 3 em 2m 13s · 3 favorito(s) gravado(s) (2 com precisão diária).')
    await expect(page.getByTestId('batch-daily-note')).toContainText('Precisão diária em 2 ativos:')
    await expect(itemRow(page, 'SPY')).toContainText('2 jan. 2015 – 23 out. 2026 · precisão diária: sem 15m de 2 jan. 2015 a 18 mai. 2026')
    await expect(page.getByTestId('batch-open-favorites')).toHaveText('Ver os 3 resultados do lote em Favoritos')
    // Pausar/Encerrar somem no fim
    await expect(page.getByTestId('batch-pause')).toHaveCount(0)
    await expect(page.getByTestId('combo-run')).toBeEnabled() // concluído não bloqueia
  })

  test('o mesmo lote em 5m: NVDA e SPY ficam fora com o motivo e BTC/USDT roda', async ({ page }) => {
    await commonMocks(page)
    const reason = 'ação e ETF não rodam em 5m; para incluí-los, use 15m, 1h, 4h ou 1d'
    const sim = await installLoteApi(page, {
      previewResponse: previewOf(
        [
          previewItem('BTC/USDT', 'run'),
          previewItem('NVDA', 'out', { reason, out_kind: 'timeframe' }),
          previewItem('SPY', 'out', { reason, out_kind: 'timeframe' }),
        ],
        { timeframe: '5m' },
      ),
      startItems: () => [
        simItem(0, 'BTC/USDT', 'optimizing'),
        simItem(1, 'NVDA', 'out', { reason }),
        simItem(2, 'SPY', 'out', { reason }),
      ],
    })
    await page.goto('/combo/configure?template=ema_rsi')
    await mixedSelection(page)
    await timeframeSelect(page).selectOption('5m')
    await expect(timeframeSelect(page)).toHaveValue('5m')
    const copy = page.getByTestId('combo-run-copy')
    await expect(copy).toHaveText(
      'Lote de 3 ativos: roda 1 (BTC/USDT). Fora antes de começar: NVDA (Ação), SPY (ETF) — ação e ETF não rodam em 5m; para incluí-los, use 15m, 1h, 4h ou 1d.',
    )
    await expect(copy.locator('.lote-out')).toContainText('Fora antes de começar: NVDA (Ação), SPY (ETF)')
    await page.getByTestId('combo-run').click()
    await expect(page.getByTestId('batch-out')).toHaveText(`NVDA (Ação), SPY (ETF) — ${reason}.`)
    await expect(page.getByTestId('batch-confirm-panel')).toContainText('1 — 1 cripto (USDT): BTC/USDT')
    await page.getByTestId('batch-confirm').click()
    // o pedido leva todos os selecionados; é o servidor que decide e devolve NVDA e SPY como "Fora"
    expect(sim.calls.find((c) => c.path === 'batch')!.body).toMatchObject({ symbols: ['BTC/USDT', 'NVDA', 'SPY'], timeframe: '5m' })
    await expect(page.getByTestId('batch-live')).toHaveText('BTC/USDT: otimizando.')
    await expect(page.getByTestId('batch-panel').locator('.lote-bmeta')).toContainText('0 de 1 ativos')
    await expect(itemRow(page, 'NVDA')).toContainText('Fora')
    await expect(itemRow(page, 'NVDA')).toContainText(`${reason[0].toUpperCase()}${reason.slice(1)}. Ficou fora antes de começar.`)
    await expect(itemRow(page, 'NVDA').locator('.lote-cls')).toHaveText('Ação')
    await expect(itemRow(page, 'SPY').locator('.lote-cls')).toHaveText('ETF')
  })

  test('só ações e ETFs em tempo que não serve: nada será executado, com o mesmo motivo', async ({ page }) => {
    await commonMocks(page)
    const sim = await installLoteApi(page)
    await page.goto('/combo/configure?template=ema_rsi')
    await mixedSelection(page)
    // com a cripto na seleção 5m é escolhível; ao tirá-la, o valor fica em 5m e a tela avisa antes de rodar
    await timeframeSelect(page).selectOption('5m')
    await page.locator('.ap-chip[data-asset="BTC/USDT"]').getByRole('button').click()
    await expect(timeframeSelect(page)).toHaveValue('5m')
    await expect(timeframeSelect(page).locator('option[value="1m"]')).toBeDisabled() // só ação/ETF: indisponível
    await expect(page.getByTestId('combo-run-copy')).toHaveText(
      'Nada será executado: NVDA (Ação), SPY (ETF) — ação e ETF não rodam em 5m; para incluí-los, use 15m, 1h, 4h ou 1d.',
    )
    await page.getByTestId('combo-run').click()
    const warning = page.getByTestId('run-warning')
    await expect(warning).toContainText('Ação e ETF não rodam em 5m')
    await expect(warning).toContainText('Nada foi executado. A seleção foi mantida.')
    expect(sim.calls.some((c) => c.path === 'preview')).toBe(false)
  })

  test('lote grande: lista de 50 em 50, filtro por estado e problemas em todos os estados', async ({ page }) => {
    await page.setViewportSize(PHONE)
    await commonMocks(page)
    const sim = await installLoteApi(page)
    const items = Array.from({ length: 120 }, (_, i) =>
      simItem(i, `AA${String(i).padStart(3, '0')}`, i < 3 ? 'success_daily' : i === 3 ? 'collecting' : 'queued', {
        asset_class: 'stock',
        execution: i < 3 ? DAILY_NVDA : null,
        progress: i === 3 ? '1d · página 1 de 3' : null,
        favorite_id: i < 3 ? 200 + i : null,
        collect_kind: 'missing',
        needs_collection: [{ series: '1d', role: 'candles', kind: 'missing' }],
      } as never),
    )
    sim.setJob(buildJob(items, 'running', { elapsed_sec: 48, estimated_remaining_sec: 34800 }))
    await page.goto('/combo/configure?template=ema_rsi')
    // painel do lote ativo ao reabrir a página (GET /batch/active)
    const batch = page.getByTestId('batch-panel')
    await expect(batch).toBeVisible()
    await expect(page.getByTestId('batch-panel').locator('.lote-bmeta')).toHaveText('3 de 120 ativos · 0m 48s · resta ~9h 40m')
    await expect(page.locator('.lote-row')).toHaveCount(50)
    await page.getByRole('button', { name: /Mostrar mais 50/ }).click()
    await expect(page.locator('.lote-row')).toHaveCount(100)
    await page.getByRole('button', { name: /Mostrar mais 50/ }).click()
    await expect(page.locator('.lote-row')).toHaveCount(120)
    await expect(page.getByRole('button', { name: /Mostrar mais 50/ })).toHaveCount(0)
    // filtro por estado: botões com aria-pressed e contagem, só os estados presentes
    const chips = page.locator('.lote-chip')
    await expect(chips).toHaveCount(4) // Todos, Precisão diária, Em curso e Na fila: só os estados presentes
    await page.locator('.lote-chip[data-chip="daily"]').click()
    await expect(page.locator('.lote-chip[data-chip="daily"]')).toHaveAttribute('aria-pressed', 'true')
    await expect(page.locator('.lote-row')).toHaveCount(3)
    // abaixo de 620 px de largura do painel, cada ativo vira cartão
    const header = await page.locator('.lote-listhead').evaluate((el) => getComputedStyle(el).display)
    expect(header).toBe('none')
    expect(await fitsHorizontally(page)).toBe(true)
  })

  test('lote com problemas: sucesso, precisão diária, insuficiente, rejeitado, falha, pulado e fora, com ícone e texto', async ({ page }) => {
    await commonMocks(page)
    const sim = await installLoteApi(page)
    sim.setJob(
      buildJob(
        [
          simItem(0, 'BTC/USDT', 'success', { execution: INTRABAR }),
          simItem(1, 'NVDA', 'success_daily', { execution: DAILY_NVDA }),
          simItem(2, 'AAPL', 'insufficient', { reason: 'Dados insuficientes: a janela coberta tem 120 candles de 1d e a estratégia precisa de pelo menos 201 (média de 200). Nenhum favorito gravado.' }),
          simItem(3, 'QQQ', 'rejected', { reason: 'Reprovado no walk-forward (NO-GO no holdout): retorno do holdout −8,2%. Nenhum favorito gravado.' }),
          simItem(4, 'SPY', 'failed', { reason: 'Histórico de SPY indisponível agora: limite de requisições da Binance. Nenhum favorito gravado; rode de novo mais tarde.' }),
          simItem(5, 'ETH/USDT', 'skipped', { reason: 'Já está nos favoritos com o mesmo período e direção.' }),
          simItem(6, 'SOL/USDT', 'out', { reason: 'suspenso pela Binance; não entra em análise nova' }),
        ],
        'completed',
        { elapsed_sec: 312, succeeded: 2, failed: 1 },
      ),
    )
    // concluído não aparece em /active: o teste abre o lote final como se tivesse acabado de terminar
    sim.job!.status = 'running'
    await page.goto('/combo/configure?template=ema_rsi')
    sim.job!.status = 'completed'
    await expect(page.getByTestId('batch-status')).toHaveText('Concluído', { timeout: 10_000 })
    await expect(page.getByTestId('batch-live')).toHaveText(
      'Lote concluído: 6 de 6 em 5m 12s · 2 favorito(s) gravado(s) (1 com precisão diária) · sem resultado válido: 3.',
    )
    for (const [symbol, label] of [
      ['BTC/USDT', 'Sucesso'],
      ['NVDA', 'Sucesso · precisão diária'],
      ['AAPL', 'Insuficiente'],
      ['QQQ', 'Rejeitado'],
      ['SPY', 'Falha'],
      ['ETH/USDT', 'Pulado'],
      ['SOL/USDT', 'Fora'],
    ] as const) {
      const state = itemRow(page, symbol).locator('.lote-state')
      await expect(state).toContainText(label)
      await expect(state.locator('svg')).toHaveCount(1) // ícone + texto: o estado nunca é só cor
      await expect(state.locator('svg')).toHaveAttribute('aria-hidden', 'true')
    }
    await expect(itemRow(page, 'AAPL')).toContainText('precisa de pelo menos 201')
    await expect(page.locator('.lote-chip[data-chip="out"]')).toContainText('Fora 1')
  })

  test('um lote em andamento reaparece ao reabrir a página, com o botão de rodar bloqueado', async ({ page }) => {
    await commonMocks(page)
    const sim = await installLoteApi(page)
    sim.setJob(
      buildJob([
        simItem(0, 'BTC/USDT', 'success', { execution: INTRABAR }),
        simItem(1, 'NVDA', 'optimizing'),
        simItem(2, 'SPY', 'queued'),
      ]),
    )
    await page.goto('/combo/configure?template=ema_rsi')
    await expect(page.getByTestId('batch-panel')).toBeVisible()
    await expect(page.getByTestId('batch-status')).toHaveText('Rodando')
    await expect(page.getByTestId('combo-run')).toBeDisabled()
    expect(sim.calls.some((c) => c.path === 'active')).toBe(true)
    // pausa feita em outra sessão: o painel reabre Pausado e Otimizar pede para retomar ou encerrar
    sim.job!.pause_requested = true
    sim.settle()
    await page.reload()
    await expect(page.getByTestId('batch-status')).toHaveText('Pausado')
    await expect(page.getByTestId('combo-run')).toBeEnabled()
    await pick(page, 'NVDA')
    await page.getByTestId('combo-run').click()
    await expect(page.getByTestId('batch-paused-block')).toContainText('Retome ou encerre o lote 7f3c2a91 antes de começar outro.')
    await page.getByTestId('batch-block-cancel').click()
    await expect(page.getByTestId('batch-status')).toHaveText('Encerrado')
    await expect(page.getByRole('heading', { name: /Lote 7f3c2a91/ })).toBeFocused()
    await page.getByTestId('combo-run').click()
    await expect(page.getByTestId('batch-confirm-panel').getByRole('heading', { name: /Confirmar lote/ })).toBeVisible() // encerrado não bloqueia
  })

  test('o servidor devolve 409 com o lote pausado: o Confirmar nunca abre', async ({ page }) => {
    await commonMocks(page)
    const sim = await installLoteApi(page)
    await page.goto('/combo/configure?template=ema_rsi')
    await mixedSelection(page)
    // o lote pausado existe só no servidor (outra aba): o preview devolve 409 batch_paused
    const paused = buildJob([simItem(0, 'BTC/USDT', 'success', { execution: INTRABAR }), simItem(1, 'NVDA', 'queued'), simItem(2, 'SPY', 'queued')], 'paused')
    sim.setJob(paused)
    await page.getByTestId('combo-run').click()
    await expect(page.getByTestId('batch-paused-block')).toContainText('Retome ou encerre o lote 7f3c2a91 antes de começar outro.')
    await expect(page.getByTestId('batch-confirm')).toHaveCount(0)
    await expect(page.getByTestId('batch-panel')).toBeVisible()
  })
})

// ------------------------------------------------------------------------------------------------ Otimização

const NOTE_OPT =
  'Cripto, ação e ETF rodam juntos no lote, no período fixo desta tela: cada ativo usa a sua fonte, sessão, ajuste e moeda, e o melhor resultado de cada um vira favorito. Ação e ETF não rodam em 1m, 5m e 30m, nem em 15m, 1h e 4h quando o 5m deles não cobre o período fixo: ficam fora com o motivo; use 1d aqui ou o Combo, que tem período. 1 ação ou ETF sozinha mostra o resultado ao lado.'
const COVERAGE = 'o 5m deles começa em 19 mai. 2026 e não cobre 1 a 31 jan. 2024, o período fixo desta tela; use 1d aqui ou o Combo, que tem período'

test.describe('Otimização: lote multiclasse', () => {
  for (const viewport of [DESKTOP, PHONE]) {
    test(`Confirmar e painel na coluna larga no lugar de "Ready to Optimize" (${viewport.width} px)`, async ({ page }) => {
      await page.setViewportSize(viewport)
      await commonMocks(page, { nvdaFiveMinutes: true })
      const sim = await installLoteApi(page, {
        previewResponse: previewOf(
          [
            previewItem('BTC/USDT', 'run'),
            previewItem('NVDA', 'run'),
            previewItem('SPY', 'run', { collect_kind: 'missing', needs_collection: [{ series: '1d', role: 'candles', kind: 'missing' }], collect_note: 'O 5m de SPY não entra: a Binance não tem 5m dele em jan. 2024.' }),
          ],
          { timeframe: '1d', page: 'optimize', start_date: '2024-01-01', end_date: '2024-01-31' },
        ),
      })
      await page.goto('/combo/optimize?template=ema_rsi&timeframe=1d')
      await mixedSelection(page)
      await expect(page.getByTestId('asset-class-note')).toHaveText(NOTE_OPT)
      await expect(page.getByTestId('opt-run-copy')).toHaveText(
        'Lote de 3 ativos (1 cripto, 1 ação, 1 ETF): otimiza cada um com esta configuração, no período fixo desta tela, e grava o melhor de cada em favoritos (nota "gerado em lote"). Antes de começar, você confirma o lote.',
      )
      for (const value of ['1m', '5m', '30m']) {
        await expect(timeframeSelect(page).locator(`option[value="${value}"]`)).toHaveText(`${value} (só cripto)`)
        await expect(timeframeSelect(page).locator(`option[value="${value}"]`)).toBeEnabled()
      }
      await expect(page.getByText('Ready to Optimize')).toBeVisible()

      await page.getByTestId('run-optimization').click()
      const confirm = page.getByTestId('batch-confirm-panel')
      await expect(confirm.getByRole('heading', { name: 'Confirmar lote de 3 ativos' })).toBeFocused()
      await expect(page.getByText('Ready to Optimize')).toHaveCount(0)
      await expect(page.getByTestId('batch-need-count')).toHaveText('1 de 3')
      await expect(confirm).toContainText('SPY (1d). BTC/USDT e NVDA já estão guardados, sem lacunas e atualizados. O 5m de SPY não entra: a Binance não tem 5m dele em jan. 2024.')
      await expect(page.getByTestId('batch-config')).toHaveText('Médias: tendência (ema_rsi) · 1d · 1 a 31 jan. 2024 (fixo nesta tela) · Long · intrabar 15m')
      expect(sim.calls.find((c) => c.path === 'preview')!.body).toMatchObject({ page: 'optimize', start_date: '2024-01-01', end_date: '2024-01-31' })
      // Confirmar e o painel ocupam a coluna larga (mais de 620 px a 1440; a coluna toda no celular)
      const wide = await confirm.evaluate((el) => el.getBoundingClientRect().width)
      if (viewport.width === 1440) expect(wide).toBeGreaterThan(620)
      // Voltar traz "Ready to Optimize" de volta e devolve o foco ao botão de rodar
      await page.getByTestId('batch-back').click()
      await expect(page.getByText('Ready to Optimize')).toBeVisible()
      await expect(page.getByTestId('run-optimization')).toBeFocused()

      await page.getByTestId('run-optimization').click()
      await page.getByTestId('batch-confirm').click()
      await expect(page.getByTestId('batch-status')).toHaveText('Rodando')
      await expect(page.getByText('Ready to Optimize')).toHaveCount(0)
      const panelWidth = await page.getByTestId('batch-panel').evaluate((el) => el.getBoundingClientRect().width)
      if (viewport.width === 1440) {
        expect(panelWidth).toBeGreaterThan(620)
        expect(await page.locator('.lote-listhead').evaluate((el) => getComputedStyle(el).display)).not.toBe('none') // lista em colunas
      } else {
        expect(await page.locator('.lote-listhead').evaluate((el) => getComputedStyle(el).display)).toBe('none') // cartões
      }
      expect(await fitsHorizontally(page)).toBe(true)
      // pausa, bloqueio e retomada valem como no Combo
      await page.getByTestId('batch-pause').click()
      sim.settle()
      await expect(page.getByTestId('batch-status')).toHaveText('Pausado')
      await page.getByTestId('run-optimization').click()
      await expect(page.getByTestId('batch-paused-block')).toContainText('Retome ou encerre o lote 7f3c2a91 antes de começar outro.')
      await page.getByTestId('batch-block-resume').click()
      await expect(page.getByTestId('batch-status')).toHaveText('Rodando')
    })
  }

  for (const timeframe of ['15m', '1h', '4h']) {
    test(`${timeframe}: ação e ETF ficam fora pela cobertura do 5m, com o motivo antes de rodar`, async ({ page }) => {
      await commonMocks(page, { nvdaFiveMinutes: true })
      const reasonFor = (symbol: string) =>
        `o 5m de ${symbol} começa em 19 mai. 2026 e não cobre 1 a 31 jan. 2024, o período fixo desta tela; use 1d aqui ou o Combo, que tem período`
      const sim = await installLoteApi(page, {
        previewResponse: previewOf(
          [
            previewItem('BTC/USDT', 'run'),
            previewItem('NVDA', 'out', { reason: reasonFor('NVDA'), out_kind: 'coverage' }),
            previewItem('SPY', 'out', { reason: reasonFor('SPY'), out_kind: 'coverage' }),
          ],
          { timeframe, page: 'optimize' },
        ),
      })
      await page.goto(`/combo/optimize?template=ema_rsi&timeframe=${timeframe}`)
      await mixedSelection(page)
      await expect(page.getByTestId('opt-run-copy')).toHaveText(
        `Lote de 3 ativos: roda 1 (BTC/USDT). Fora antes de começar: NVDA (Ação), SPY (ETF) — ${COVERAGE}.`,
      )
      await page.getByTestId('run-optimization').click()
      const confirm = page.getByTestId('batch-confirm-panel')
      await expect(page.getByTestId('batch-out')).toHaveText(`NVDA (Ação), SPY (ETF) — ${COVERAGE}.`)
      await expect(page.getByTestId('batch-config')).toContainText(`${timeframe} · 1 a 31 jan. 2024 (fixo nesta tela)`)
      await expect(page.getByTestId('batch-config')).not.toContainText('1d')
      await expect(confirm).toContainText('1 — 1 cripto (USDT): BTC/USDT')
      expect(sim.calls.filter((c) => c.path === 'batch')).toHaveLength(0)
    })
  }

  for (const timeframe of ['1m', '5m', '30m']) {
    test(`${timeframe}: o conselho é "use 1d aqui ou o Combo, que tem período"`, async ({ page }) => {
      await commonMocks(page, { nvdaFiveMinutes: true })
      await installLoteApi(page)
      await page.goto(`/combo/optimize?template=ema_rsi&timeframe=${timeframe}`)
      await mixedSelection(page)
      const copy = page.getByTestId('opt-run-copy')
      await expect(copy).toContainText(`ação e ETF não rodam em ${timeframe}; para incluí-los, use 1d aqui ou o Combo, que tem período.`)
      await expect(copy).not.toContainText('15m, 1h, 4h')
    })
  }

  test('Otimização sem lote não mostra o painel, e 1 ativo segue o caminho de hoje', async ({ page }) => {
    await commonMocks(page)
    const sim = await installLoteApi(page)
    await page.goto('/combo/optimize?template=ema_rsi&timeframe=1d')
    await expect(page.getByText('Ready to Optimize')).toBeVisible()
    await expect(page.getByTestId('opt-run-copy')).toHaveText('1 ativo: otimiza e mostra o resultado ao lado.')
    await expect(page.getByTestId('batch-panel')).toHaveCount(0)
    expect(sim.calls.some((c) => c.path === 'preview')).toBe(false)
  })
})

