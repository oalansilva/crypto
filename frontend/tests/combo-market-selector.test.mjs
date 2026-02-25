import test from 'node:test'
import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)
const pagePath = path.resolve(__dirname, '../src/pages/ComboConfigurePage.tsx')

test('Combo Configure includes market selector and NASDAQ-100 source', async () => {
  const source = await readFile(pagePath, 'utf8')

  assert.match(source, /US Stocks \(NASDAQ-100\)/)
  assert.match(source, /\/markets\/us\/nasdaq100/)
  assert.match(source, /data_source:\s*'stooq'/)
  assert.match(source, /timeframe is fixed to 1D/)
})
