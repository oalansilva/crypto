/**
 * Card #1121 — Descoberta com cripto, ação e ETF na mesma varredura (funcional, API simulada).
 *
 * Segue o protótipo aprovado (`frontend/public/prototypes/card-1121-descoberta-acoes-etfs/`): Preflight misto,
 * recusa do teto, quadro "Por ativo", foco depois de cancelar, filtro Classe com rank global, bloco do
 * candidato, promoção de NVDA sem nível de estrela e a nota "Sem resultado" com "ver Por ativo".
 */
import { expect, test, type Page } from '@playwright/test'
import {
  ASSETS_COLLECTING,
  ASSETS_DONE,
  ASSETS_FAILED,
  PREFLIGHT_LIMIT,
  SWEEP_ID,
  buildMixedDraft,
  installDiscoveryMulticlassMocks,
  sweepPayload,
} from './helpers/discoveryMulticlassMock'

const BROWSER_ERRORS = new WeakMap<Page, string[]>()

test.beforeEach(async ({ page }) => {
  const errors: string[] = []
  BROWSER_ERRORS.set(page, errors)
  page.on('console', (message) => {
    if (message.type() === 'error') errors.push(`console: ${message.text()}`)
  })
  page.on('pageerror', (error) => errors.push(`pageerror: ${error.message}`))
})

test.afterEach(async ({ page }) => {
  expect(BROWSER_ERRORS.get(page) ?? []).toEqual([])
})

function historyEntry(state: string) {
  return { sweep_id: SWEEP_ID, state, total: 3, processed: 3, succeeded: 2, failed: 0, skipped: 0, snapshot_hash: '1121', created_at: '2026-10-26T12:00:00Z' }
}

test('Preflight misto: vão rodar cripto, ação e ETF com coleta, precisão prevista e viés de sobrevivência', async ({ page }) => {
  await installDiscoveryMulticlassMocks(page)
  await page.goto('/combo/discovery')
  await buildMixedDraft(page)

  await expect(page.getByTestId('asset-class-note')).toHaveText(
    'Cripto, ação e ETF entram na mesma varredura: cada ativo usa a sua fonte, sessão, ajuste e moeda (USDT ou USD). Sem 15m que cubra a janela, ação e ETF rodam em precisão diária, com a marca no resultado.',
  )
  await expect(page.getByTestId('preflight-state')).toHaveText('Pronto para iniciar')
  await expect(page.getByTestId('planned-total')).toHaveText('3')
  await expect(page.getByTestId('preflight-run')).toHaveText(
    'Vão rodar 3 ativos: 1 cripto (USDT) · 1 ação · 1 ETF (USD). Cada um com a sua fonte, sessão, ajuste e moeda.',
  )
  await expect(page.getByTestId('preflight-collect')).toHaveText(
    'Precisam de coleta de histórico: 1 de 3 — SPY (1d e 5m do intrabar). BTC/USDT e NVDA já estão guardados. A coleta acontece no começo do ativo e entra no tempo da varredura.',
  )
  await expect(page.getByTestId('preflight-precision')).toContainText(
    'Precisão diária prevista em 1d: NVDA — o 15m dele começa em 2 jan. 2026, então 2 jan. 2003 a 31 dez. 2025 roda no candle diário.',
  )
  await expect(page.getByTestId('preflight-precision')).toContainText('SPY: sem histórico guardado; a precisão aparece depois da coleta.')
  await expect(page.getByTestId('survivorship-note')).toHaveText(
    'Viés de sobrevivência: a varredura usa só os ativos do catálogo de hoje. Ativos que saíram da Binance antes de hoje não entram, e a janela começa em 2 jan. 2003.',
  )
  await expect(page.getByTestId('cost-note')).toContainText('taxa por lado: cripto 0,075% · ação e ETF 0,10% · slippage do timeframe')
  await expect(page.getByTestId('preflight-class-out')).toHaveCount(0)
  await expect(page.getByTestId('start-sweep')).toBeEnabled()
  await expect(page.getByText(/a Descoberta vem depois|Nesta etapa as análises rodam só com cripto|ações e ETFs fora/)).toHaveCount(0)
})

test('teto de 1.000 com ação e ETF: recusa antes de começar e pede para estreitar', async ({ page }) => {
  await installDiscoveryMulticlassMocks(page, { preflight: PREFLIGHT_LIMIT })
  await page.goto('/combo/discovery')
  await buildMixedDraft(page)

  await expect(page.getByTestId('preflight-state')).toHaveText('Bloqueado — veja o que falta')
  await expect(page.getByTestId('planned-total')).toHaveText('2.433')
  const limit = page.getByTestId('preflight-limit')
  await expect(limit).toHaveAttribute('role', 'alert')
  await expect(limit).toContainText('Acima do teto de 1.000 combinações')
  await expect(limit).toContainText(
    '2.433 combinações válidas passam do limite de 1.000: 2.433 ativos (1 cripto · 2.431 ações · 1 ETF) × 1 template × 1 timeframe × Long.',
  )
  await expect(limit).toContainText('Estreite a seleção: menos ativos (filtre antes de usar “Todos do filtro”), menos templates ou menos timeframes. Nenhuma varredura foi criada.')
  await expect(page.getByTestId('preflight-run')).toHaveText('2.433 ativos selecionados: 1 cripto (USDT) · 2.431 ações · 1 ETF (USD).')
  await expect(page.getByTestId('preflight-collect')).toHaveCount(0)
  await expect(page.getByTestId('over-limit-note')).toHaveCount(0)
  await expect(page.getByTestId('start-sweep')).toBeDisabled()
})

test('Acompanhando: "Por ativo" com o ativo em curso no topo, parciais com o bloco do candidato e foco ao cancelar', async ({ page }) => {
  const state = await installDiscoveryMulticlassMocks(page, { assets: ASSETS_COLLECTING })
  await page.goto('/combo/discovery')
  await buildMixedDraft(page)
  await expect(page.getByTestId('start-sweep')).toBeEnabled()
  await page.getByTestId('start-sweep').click()

  const board = page.getByTestId('sweep-assets')
  await expect(board.getByRole('heading', { name: 'Por ativo' })).toBeVisible()
  const items = board.locator('li')
  await expect(items).toHaveCount(3)
  await expect(items.nth(0)).toHaveAttribute('data-asset', 'NVDA')
  await expect(items.nth(0)).toContainText('Coletando histórico · 1d · página 3 de 6')
  await expect(items.nth(0)).toContainText('0 de 1 combinação')
  await expect(board.locator('li[data-asset="BTC/USDT"]')).toContainText('Concluído')
  await expect(board.locator('li[data-asset="BTC/USDT"]')).toContainText('Precisão intrabar (15m) · período efetivo 17 ago. 2017 – 25 out. 2026')
  await expect(board.locator('li[data-asset="SPY"]')).toContainText('Na fila')
  await expect(board.locator('.mc-asset-cols')).toBeVisible() // cabeçalhos de coluna acima de 620 px
  await expect(board.getByTestId('assets-live')).toHaveText('NVDA: coletando histórico · 1d · página 3 de 6')
  await expect(board.getByTestId('assets-more')).toHaveCount(0)

  const partial = page.getByTestId('partials-table').locator('tr.result-row').filter({ hasText: 'NVDA · 1d · Long' })
  await expect(partial.getByTestId('mc-precision')).toHaveAttribute('title', 'Precisão diária · sem 15m de 2 jan. 2003 a 31 dez. 2025')
  await expect(partial.getByTestId('candidate-class-block')).toContainText('Ação USD')
  await expect(partial.getByTestId('candidate-class-block')).toContainText('Binance Ações · NY · split · 252/ano')

  // Pausado: a coleta em curso diz que retoma daqui.
  state.sweepState = 'paused'
  await expect(items.nth(0)).toContainText('Pausado na coleta · 1d · página 3 de 6 · retoma daqui', { timeout: 6000 })
  state.sweepState = 'running'

  await page.getByTestId('cancel-sweep').click()
  await page.getByTestId('confirm-cancel').click()
  await expect(page.locator('#progress-heading')).toBeFocused()
})

test('Decidir: cabeçalho multiclasse, bloco do candidato, filtro Classe com rank global e promoção de NVDA', async ({ page }) => {
  await installDiscoveryMulticlassMocks(page, {
    sweepState: 'completed',
    assets: ASSETS_DONE,
    history: [historyEntry('completed')],
  })
  await page.goto('/combo/discovery')
  await page.getByRole('tab', { name: 'Decidir' }).click()

  await expect(page.getByTestId('leaderboard-state')).toHaveText('concluída')
  await expect(page.getByTestId('leaderboard-classes')).toHaveText(
    '3 classes · janela, candles e amostra em cada linha · taxa por lado: cripto 0,075% · ação e ETF 0,10% · slippage do timeframe',
  )
  await expect(page.getByTestId('survivorship-decidir')).toHaveText(
    'Viés de sobrevivência: esta varredura usou só os ativos do catálogo de hoje (janela desde 2 jan. 2003). Ativos que saíram da Binance antes de hoje não estão no ranking.',
  )
  await expect(page.getByTestId('no-result-decidir')).toHaveCount(0)
  await expect(page.getByTestId('class-copy')).toContainText('Cobertura conta as velas esperadas no calendário da classe')

  const nvda = page.getByTestId('decidir-table').locator('tr.result-row').filter({ hasText: 'RS-NVDA1121B2' })
  const block = nvda.getByTestId('candidate-class-block')
  await expect(block).toContainText('NVDA · 1d · Long')
  await expect(block).toContainText('Ação USD')
  await expect(block.getByTestId('mc-precision')).toContainText('Precisão diária (2003–2025)')
  await expect(block.getByTestId('mc-precision')).toHaveAttribute('title', 'Precisão diária · sem 15m de 2 jan. 2003 a 31 dez. 2025')
  await expect(block.locator('.sr-only').filter({ hasText: 'Precisão diária · sem 15m de 2 jan. 2003 a 31 dez. 2025' })).toHaveCount(1)
  await expect(block).toContainText('Binance Ações · NY · split · 252/ano')
  await expect(block).toContainText('2 jan. 2003 – 23 out. 2026')
  const btcBlock = page.getByTestId('decidir-table').locator('tr.result-row').filter({ hasText: 'RS-BTC1121A1' }).getByTestId('candidate-class-block')
  await expect(btcBlock).toContainText('Cripto USDT')
  await expect(btcBlock).toContainText('Precisão intrabar (15m)')
  await expect(btcBlock).toContainText('Binance Spot · 24/7 · 365 dias/ano')

  const classFilter = page.getByTestId('class-filter')
  await expect(classFilter.locator('option')).toHaveText(['Todas (3)', 'Cripto (1)', 'Ações (1)', 'ETFs (1)'])
  await classFilter.selectOption('stock')
  await expect(page.getByTestId('result-count')).toContainText('1 de 3 candidatos')
  const rows = page.getByTestId('decidir-table').locator('tr.result-row')
  await expect(rows).toHaveCount(1)
  await expect(rows.first().locator('.rank-cell-value')).toHaveText('2')

  await page.getByTestId('promote-RS-NVDA1121B2').click()
  const dialog = page.getByRole('dialog', { name: 'Promover a favorito tier 3' })
  await expect(dialog).toBeVisible()
  await expect(page.getByTestId('confirm-promotion')).toBeFocused()
  const identity = dialog.getByTestId('modal-execution-identity')
  await expect(identity).toContainText('Ação · USD')
  await expect(identity).toContainText('Precisão diária · sem 15m de 2 jan. 2003 a 31 dez. 2025')
  await expect(identity).toContainText('Binance Ações · NY · split · 252/ano')
  await expect(identity).toContainText('Período efetivo 2 jan. 2003 – 23 out. 2026')
  await expect(identity).toContainText('Amostra 8b41d7e2 · guardada enquanto o favorito existir · Direção Long')
  // Card #1122: ação e ETF vão para Tier 3, com a nota de "Alertar" e da carteira.
  await expect(dialog.getByTestId('destination-tier3')).toContainText('Tier 3 · observação')
  await expect(dialog.getByTestId('destination-tier3')).toContainText('marque "Alertar" lá e marque o ativo como "No portfólio" no Monitor')
  await expect(dialog).not.toContainText('Monitor, Telegram e Revalidar: ainda não para ações e ETFs')
  await page.keyboard.press('Escape')
  await expect(page.getByTestId('promote-RS-NVDA1121B2')).toBeFocused()
  await page.getByTestId('promote-RS-NVDA1121B2').click()
  await page.getByTestId('confirm-promotion').click()
  const promoted = page.locator('[data-promoted-result="RS-NVDA1121B2"]')
  await expect(promoted).toHaveText('Favorito tier 3')
  await expect(promoted).toBeFocused()
  const link = page.getByTestId('see-favorite-RS-NVDA1121B2')
  await expect(link).toHaveText('Ver em Favoritos')
  expect((await link.boundingBox())?.height ?? 0).toBeGreaterThanOrEqual(44)

  // Cripto segue "Promover a favorito tier 3".
  await classFilter.selectOption('all')
  await page.getByTestId('promote-RS-BTC1121A1').click()
  await expect(page.getByRole('dialog', { name: 'Promover a favorito tier 3' })).toBeVisible()
  await expect(page.getByText('Tier 3 · observação')).toBeVisible()
})

test('falha de coleta: "Sem resultado" no Decidir, ETFs (0) desabilitado e "ver Por ativo"', async ({ page }) => {
  const state = await installDiscoveryMulticlassMocks(page, {
    sweepState: 'partial_failure',
    assets: ASSETS_FAILED,
    history: [historyEntry('partial_failure')],
  })
  state.results = state.results.filter((r) => r.result_id !== 'RS-SPY1121C3')
  await page.goto('/combo/discovery')
  await page.getByRole('tab', { name: 'Decidir' }).click()

  await expect(page.getByTestId('leaderboard-state')).toHaveText('falha parcial')
  const note = page.getByTestId('no-result-decidir')
  await expect(note).toHaveAttribute('data-kind', 'failed')
  await expect(note).toContainText('Sem resultado: SPY — Falha: a Binance não respondeu ao histórico nas 3 tentativas.')
  const etfs = page.getByTestId('class-filter').locator('option[value="etf"]')
  await expect(etfs).toHaveText('ETFs (0)')
  await expect(etfs).toHaveAttribute('disabled', '')

  await note.getByRole('button', { name: 'ver Por ativo' }).click()
  await expect(page.getByRole('heading', { name: 'Por ativo' })).toBeFocused()
  const first = page.getByTestId('sweep-assets').locator('li').first()
  await expect(first).toHaveAttribute('data-asset', 'SPY')
  await expect(first).toContainText('Falha: a Binance não respondeu ao histórico de SPY nas 3 tentativas')
})

test('varredura que termina na tela: "ver Por ativo" deixa a aba Acompanhando habilitada, com o id e as setas', async ({ page }) => {
  const state = await installDiscoveryMulticlassMocks(page, { assets: ASSETS_COLLECTING })
  state.results = state.results.filter((r) => r.result_id !== 'RS-SPY1121C3')
  await page.goto('/combo/discovery')
  await buildMixedDraft(page)
  await expect(page.getByTestId('start-sweep')).toBeEnabled()
  await page.getByTestId('start-sweep').click()
  await expect(page.getByTestId('sweep-assets').getByRole('heading', { name: 'Por ativo' })).toBeVisible()

  // A varredura termina: a tela salta para o Decidir da mesma varredura.
  state.sweepState = 'partial_failure'
  state.assets = ASSETS_FAILED
  state.history = [historyEntry('partial_failure')]
  const decidir = page.getByRole('tab', { name: 'Decidir' })
  await expect(decidir).toHaveAttribute('aria-selected', 'true', { timeout: 8000 })

  await page.getByTestId('no-result-decidir').getByRole('button', { name: 'ver Por ativo' }).click()
  await expect(page.getByRole('heading', { name: 'Por ativo' })).toBeFocused()
  const acomp = page.locator('[data-mode-tab="acomp"]')
  await expect(acomp).toHaveText(`Acompanhando #${SWEEP_ID.slice(0, 8)}`)
  await expect(acomp).toBeEnabled()
  await expect(acomp).toHaveAttribute('aria-selected', 'true')

  // As setas partem do Acompanhando (não de um modo fora da lista).
  await acomp.focus()
  await page.keyboard.press('ArrowRight')
  await expect(decidir).toHaveAttribute('aria-selected', 'true')
  await expect(decidir).toBeFocused()
  await page.keyboard.press('ArrowLeft')
  await expect(acomp).toHaveAttribute('aria-selected', 'true')
  await expect(acomp).toBeFocused()
  await expect(page.getByTestId('sweep-assets').locator('li').first()).toHaveAttribute('data-asset', 'SPY')
})

test('classe sem candidato mostra o estado vazio com "Limpar filtros"', async ({ page }) => {
  const state = await installDiscoveryMulticlassMocks(page, {
    sweepState: 'completed',
    assets: ASSETS_DONE,
    history: [historyEntry('completed')],
  })
  await page.goto('/combo/discovery')
  await page.getByRole('tab', { name: 'Decidir' }).click()
  await expect(page.getByTestId('class-filter').locator('option[value="etf"]')).not.toHaveAttribute('disabled', '')
  // O ETF sai do ranking depois de escolhido (resultado excluído em outra aba): a tabela explica e limpa.
  await page.getByTestId('class-filter').selectOption('etf')
  state.results = state.results.filter((r) => r.result_id !== 'RS-SPY1121C3')
  await page.getByTestId('sort-filter').selectOption('delta_cagr_vs_bh')
  const empty = page.getByTestId('class-empty')
  await expect(empty).toContainText('Nenhum candidato de ETF nesta varredura.')
  await empty.getByRole('button', { name: 'Limpar filtros' }).click()
  await expect(page.getByTestId('class-filter')).toHaveValue('all')
  await expect(page.getByTestId('decidir-table').locator('tr.result-row')).toHaveCount(2)
})

test.describe('390 px', () => {
  test.use({ viewport: { width: 390, height: 844 } })

  test('filtro Classe com 44 px e "Por ativo" em cartão, sem rolagem horizontal', async ({ page }) => {
    const state = await installDiscoveryMulticlassMocks(page, {
      sweepState: 'partial_failure',
      assets: ASSETS_FAILED,
      history: [historyEntry('partial_failure')],
    })
    expect(sweepPayload(state).assets).toHaveLength(3)
    await page.goto('/combo/discovery')
    await page.getByRole('tab', { name: 'Decidir' }).click()
    const box = await page.getByTestId('class-filter').boundingBox()
    expect(box?.height ?? 0).toBeGreaterThanOrEqual(44)
    await page.getByTestId('no-result-decidir').getByRole('button', { name: 'ver Por ativo' }).click()
    await expect(page.getByTestId('sweep-assets').locator('.mc-asset-cols')).toBeHidden()
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= document.documentElement.clientWidth)).toBe(true)
  })
})
