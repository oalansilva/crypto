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
  assert.match(source, /CCXT \(crypto exchange data\)/)
})
