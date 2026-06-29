import test from 'node:test'
import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)
const comboSelectPath = path.resolve(__dirname, '../src/pages/ComboSelectPage.tsx')
const comboConfigurePath = path.resolve(__dirname, '../src/pages/ComboConfigurePage.tsx')

test('Combo selection uses authenticated fetch for protected combo template routes', async () => {
  const source = await readFile(comboSelectPath, 'utf8')
  assert.match(source, /import \{ authFetch \} from ['"]\.\.\/lib\/authFetch['"]/)
  assert.match(source, /authFetch\(`\$\{API_BASE_URL\}\/combos\/templates`\)/)
  assert.match(source, /authFetch\(`\$\{API_BASE_URL\}\/combos\/meta\/\$\{templateToClone\}\/clone`/)
  assert.doesNotMatch(source, /await fetch\(`\$\{API_BASE_URL\}\/combos\//)
})

test('Combo configuration uses authenticated fetch for protected combo execution routes', async () => {
  const source = await readFile(comboConfigurePath, 'utf8')
  assert.match(source, /import \{ authFetch \} from ['"]@\/lib\/authFetch['"]/)
  assert.match(source, /authFetch\(`\$\{API_BASE_URL\}\/combos\/meta\/\$\{templateName\}`/)
  assert.match(source, /authFetch\(`\$\{API_BASE_URL\}\/combos\/optimize`/)
  assert.match(source, /authFetch\(`\$\{API_BASE_URL\}\/combos\/backtest\/batch`/)
  assert.doesNotMatch(source, /await fetch\(`\$\{API_BASE_URL\}\/combos\//)
})
