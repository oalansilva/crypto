import test from 'node:test'
import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)
const appPath = path.resolve(__dirname, '../src/App.tsx')

test('Playground primary action label is exactly "New Backtest2"', async () => {
  const source = await readFile(appPath, 'utf8')
  assert.match(source, /<span className="gradient-text">New Backtest2<\/span>/)
  assert.doesNotMatch(source, /<span className="gradient-text">New Backtest<\/span>/)
})
