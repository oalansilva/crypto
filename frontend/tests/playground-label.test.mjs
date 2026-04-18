import test from 'node:test'
import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)
const homePagePath = path.resolve(__dirname, '../src/pages/HomePage.tsx')

test('Home dashboard keeps the primary backtest CTA wired to combo selection', async () => {
  const source = await readFile(homePagePath, 'utf8')
  assert.match(source, /navigate\('\/combo\/select'\)/)
  assert.match(source, /Rodar um backtest/)
})
