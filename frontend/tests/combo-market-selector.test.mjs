import test from 'node:test'
import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)
const pagePath = path.resolve(__dirname, '../src/pages/ComboConfigurePage.tsx')

test('Combo Configure is crypto-only in MVP', async () => {
  const source = await readFile(pagePath, 'utf8')

  assert.doesNotMatch(source, /US Stocks \(NASDAQ-100\)/)
  assert.doesNotMatch(source, /\/markets\/us\/nasdaq100/)
  assert.doesNotMatch(source, /data_source:\s*'stooq'/)
  // Campo Market Data por ativo (card #1120): a fonte de cripto segue CCXT; ação e ETF usam a Binance Ações.
  assert.match(source, /marketDataText\(plan\)/)
  const selection = await readFile(path.resolve(__dirname, '../src/lib/assetSelection.ts'), 'utf8')
  assert.match(selection, /'CCXT \(crypto exchange data\)'/)
  assert.match(selection, /Por ativo: CCXT \(cripto\) · Binance Ações \(ação e ETF\)/)
})
