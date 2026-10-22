import { expect, test, type Page } from '@playwright/test'

/**
 * Card #1117 (4.3): gate do protótipo canônico aprovado.
 * `index.html` (`/combo/discovery`) e os extras `combo.html` e `optimize.html`.
 */

const BASE = '/prototypes/card-1117-catalogo-ativos/'
const VIEWPORTS = [
  { name: 'desktop', width: 1440, height: 900 },
  { name: 'mobile', width: 390, height: 844 },
]

function watchErrors(page: Page) {
  const errors: string[] = []
  page.on('console', (message) => {
    if (message.type() === 'error') errors.push(`console: ${message.text()}`)
  })
  page.on('pageerror', (error) => errors.push(`page: ${error.message}`))
  return errors
}

async function noHorizontalScroll(page: Page) {
  const fits = await page.evaluate(() => document.documentElement.scrollWidth <= document.documentElement.clientWidth)
  expect(fits).toBe(true)
}

const picker = (page: Page) => page.getByTestId('asset-picker')
const search = (page: Page, text: string) => page.getByTestId('asset-search').fill(text)
const row = (page: Page, symbol: string) => page.locator(`.ap-row[data-asset="${symbol}"]`)

for (const viewport of VIEWPORTS) {
  test.describe(`protótipo #1117 · ${viewport.name}`, () => {
    test.use({ viewport: { width: viewport.width, height: viewport.height } })

    test('index.html: landmarks da Descoberta, seletor e Preflight com cripto e ação', async ({ page }) => {
      const errors = watchErrors(page)
      await page.goto(BASE, { waitUntil: 'load' })
      await expect(page.getByRole('heading', { name: 'Descoberta de estratégias swing' })).toBeVisible()
      await expect(page.getByRole('heading', { name: 'Rascunho de varredura' })).toBeVisible()
      await expect(page.getByRole('heading', { name: 'Preflight' })).toBeVisible()
      await expect(page.getByRole('heading', { name: 'Ativos' })).toBeVisible()
      await expect(picker(page)).toBeVisible()
      await expect(page.getByTestId('asset-count')).toContainText('2 selecionados · 1 cripto · 1 ação')
      await expect(page.getByTestId('preflight-class-out')).toContainText('Fora desta varredura: 1 ativo')
      await expect(page.getByTestId('edit-symbols')).toHaveCount(0)
      await expect(page.getByTestId('edit-templates')).toBeVisible()
      await noHorizontalScroll(page)
      expect(errors).toEqual([])
    })

    test('index.html: pesquisa dos exemplos, Todos do filtro com confirmação e Esc, marcado sem caixa ativa', async ({ page }) => {
      const errors = watchErrors(page)
      await page.goto(BASE, { waitUntil: 'load' })

      for (const [query, symbol] of [['BTC/USDT', 'BTC/USDT'], ['NVDA', 'NVDA'], ['SPY', 'SPY'], ['QQQ', 'QQQ']] as const) {
        await search(page, query)
        await expect(row(page, symbol)).toBeVisible()
      }
      await search(page, 'nvidia')
      await expect(page.locator('.ap-row').first()).toHaveAttribute('data-asset', 'NVDA')
      await expect(page.getByTestId('asset-select-all')).toHaveText('Todos do filtro (3)')

      await search(page, '')
      await picker(page).getByRole('button', { name: /^ETFs/ }).click()
      await page.getByTestId('asset-select-all').click()
      const dialog = picker(page).getByRole('alertdialog')
      await expect(dialog).toContainText('3.112')
      await expect(dialog).toContainText('16')
      await page.keyboard.press('Escape')
      await expect(dialog).toBeHidden()
      await expect(page.getByTestId('asset-select-all')).toBeFocused()
      await expect(page.getByTestId('asset-count')).toContainText('2 selecionados')

      await page.getByTestId('asset-select-all').click()
      await page.getByRole('button', { name: 'Incluir' }).click()
      await expect(page.getByTestId('asset-count')).toContainText('3.114 selecionados')

      await picker(page).getByRole('button', { name: /^Todas/ }).click()
      await search(page, 'waves')
      const waves = row(page, 'WAVES/USDT')
      await expect(waves.locator('input')).toBeDisabled()
      await expect(waves).toContainText('Suspenso')
      await expect(waves.getByTestId('asset-marked-reason')).toContainText('Não pode ser escolhido para análise nova')
      await expect(page.getByTestId('asset-select-all')).toHaveText('Todos do filtro (0)')

      await search(page, 'zzzz')
      await expect(page.getByTestId('asset-empty')).toBeVisible()
      await expect(page.locator('[data-ap="pager"]')).toBeHidden()
      await noHorizontalScroll(page)
      expect(errors).toEqual([])
    })

    test('index.html: Limpar bloqueia, só ação bloqueia e rascunho antigo mostra "fica de fora" com motivo', async ({ page }) => {
      const errors = watchErrors(page)
      await page.goto(BASE, { waitUntil: 'load' })
      await page.getByTestId('asset-clear').click()
      await expect(page.getByTestId('preflight-impediments')).toContainText('Escolha ao menos 1 ativo.')

      await search(page, 'nvda')
      await row(page, 'NVDA').locator('input').check()
      await expect(page.getByTestId('preflight-impediments')).toContainText('Nenhuma combinação válida')
      await expect(page.getByTestId('start-sweep')).toBeDisabled()

      await page.getByText('Demonstração · catálogo').click()
      await page.getByTestId('demo-legacy').click()
      const chips = page.getByTestId('asset-chips').locator('.ap-chip')
      await expect(chips.first()).toContainText('fica de fora')
      await expect(page.getByTestId('asset-marked-note')).toBeVisible()
      await expect(page.getByTestId('preflight-class-out')).toContainText('WAVES/USDT')
      expect(errors).toEqual([])
    })

    test('index.html: falha de ações e ETFs com lista anterior e falha de cripto sem lista', async ({ page }) => {
      const errors = watchErrors(page)
      await page.goto(BASE, { waitUntil: 'load' })
      await page.getByText('Demonstração · catálogo').click()
      await page.getByLabel('Falha ao atualizar ações e ETFs (lista anterior)').check()
      await expect(page.getByTestId('catalog-stale')).toContainText('Mostrando a lista válida de 19 out. 2026, 18:00')

      await page.getByLabel('Falha de cripto sem lista salva').check()
      await expect(page.getByTestId('catalog-down')).toHaveCount(1)
      await expect(page.getByTestId('catalog-down').getByRole('button', { name: 'Tentar de novo' })).toBeVisible()
      await search(page, 'btc')
      await expect(page.getByTestId('asset-empty')).toContainText('Cripto está indisponível agora por falha da Binance')
      await expect(page.getByTestId('asset-empty')).not.toContainText('Confira o símbolo')
      await expect(page.locator('[data-ap="pager"]')).toBeHidden()
      await page.getByTestId('catalog-down').getByRole('button', { name: 'Tentar de novo' }).click()
      await expect(page.getByTestId('catalog-down')).toHaveCount(0)
      await noHorizontalScroll(page)
      expect(errors).toEqual([])
    })

    test('combo.html: padrão BTC/USDT, sem rádio Todos/Seleciona, cópia e aviso de classe', async ({ page }) => {
      const errors = watchErrors(page)
      await page.goto(`${BASE}combo.html`, { waitUntil: 'load' })
      await expect(page.getByTestId('asset-count')).toContainText('1 selecionado · 1 cripto')
      await expect(page.locator('input[type=radio][name=scope]')).toHaveCount(0)
      await expect(page.getByTestId('asset-clear')).toHaveText('Limpar (1 ativo)')
      await expect(page.getByTestId('combo-run-copy')).toContainText('1 ativo selecionado')

      await search(page, 'nvda')
      await row(page, 'NVDA').locator('input').check()
      await page.getByTestId('combo-top10').click()
      await expect(page.getByTestId('combo-run-copy')).toContainText('Fora: NVDA (Ação)')
      await page.getByTestId('combo-run').click()
      await expect(page.getByTestId('run-warning')).toContainText('Fora do lote: NVDA (Ação)')
      await noHorizontalScroll(page)
      expect(errors).toEqual([])
    })

    test('optimize.html: sem texto livre, lote com QQQ fora e ?symbol= validado', async ({ page }) => {
      const errors = watchErrors(page)
      await page.goto(`${BASE}optimize.html`, { waitUntil: 'load' })
      await expect(page.locator('input[type=text], textarea')).toHaveCount(0)
      await expect(page.getByTestId('asset-select-all')).toBeVisible()
      for (const symbol of ['ETH/USDT', 'QQQ']) {
        await search(page, symbol)
        await row(page, symbol).locator('input').check()
      }
      await page.getByTestId('run-optimization').click()
      await expect(page.getByTestId('run-warning')).toContainText('Lote iniciado com 2 pares cripto')
      await expect(page.getByTestId('run-warning')).toContainText('QQQ')
      await expect(page.getByTestId('opt-batch-progress')).toContainText('0 de 2 ativos')

      await page.goto(`${BASE}optimize.html?symbol=XYZ/USDT`, { waitUntil: 'load' })
      await expect(page.getByTestId('asset-not-found')).toContainText('XYZ/USDT não está no catálogo da Binance')
      await page.goto(`${BASE}optimize.html?symbol=WAVES/USDT`, { waitUntil: 'load' })
      await expect(page.getByTestId('asset-chips')).toContainText('fica de fora')
      await page.getByTestId('run-optimization').click()
      await expect(page.getByTestId('run-warning')).toContainText('Ativo marcado pela Binance não entra em análise nova')
      await noHorizontalScroll(page)
      expect(errors).toEqual([])
    })
  })
}
