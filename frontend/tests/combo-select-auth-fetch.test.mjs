import test from 'node:test'
import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)
const comboSelectPath = path.resolve(__dirname, '../src/pages/ComboSelectPage.tsx')
const comboConfigurePath = path.resolve(__dirname, '../src/pages/ComboConfigurePage.tsx')
const comboEditPath = path.resolve(__dirname, '../src/pages/ComboEditPage.tsx')
const comboResultsPath = path.resolve(__dirname, '../src/pages/ComboResultsPage.tsx')

test('Combo selection uses authenticated fetch for protected combo template routes', async () => {
  const source = await readFile(comboSelectPath, 'utf8')
  assert.match(source, /import \{ authFetch \} from ['"]\.\.\/lib\/authFetch['"]/)
  assert.match(source, /authFetch\(`\$\{API_BASE_URL\}\/combos\/templates`\)/)
  assert.match(source, /authFetch\(`\$\{API_BASE_URL\}\/combos\/meta\/\$\{templateToClone\}\/clone`/)
  assert.doesNotMatch(source, /await fetch\(`\$\{API_BASE_URL\}\/combos\//)
})

test('Combo selection renders catalog display_name instead of Title-Case technical name', async () => {
  const source = await readFile(comboSelectPath, 'utf8')
  assert.match(source, /function publicTemplateTitle\(/)
  assert.match(source, /data-testid="combo-select-strategy-title"/)
  assert.doesNotMatch(source, /split\('_'\)\.map\(w => w\.charAt\(0\)\.toUpperCase/)
})

test('Combo configuration uses authenticated fetch for protected combo execution routes', async () => {
  const source = await readFile(comboConfigurePath, 'utf8')
  assert.match(source, /import \{ authFetch \} from ['"]@\/lib\/authFetch['"]/)
  assert.match(source, /authFetch\(`\$\{API_BASE_URL\}\/combos\/meta\/\$\{templateName\}`/)
  assert.match(source, /authFetch\(`\$\{API_BASE_URL\}\/combos\/optimize`/)
  assert.match(source, /authFetch\(`\$\{API_BASE_URL\}\/combos\/backtest\/batch`/)
  assert.doesNotMatch(source, /await fetch\(`\$\{API_BASE_URL\}\/combos\//)
})

test('Combo editor uses authenticated fetch for protected template read and save routes', async () => {
  const source = await readFile(comboEditPath, 'utf8')
  assert.match(source, /import \{ authFetch \} from ['"]@\/lib\/authFetch['"]/)
  assert.match(source, /authFetch\(`\$\{API_BASE_URL\}\/combos\/meta\/\$\{templateName\}`\)/)
  assert.match(source, /\/identity/)
  assert.match(source, /data-testid="combo-identity-title-input"/)
  assert.doesNotMatch(source, /Read-Only Template/)
  assert.doesNotMatch(source, /await fetch\(`\$\{API_BASE_URL\}\/combos\//)
})

test('Combo select Edit always opens the template editor', async () => {
  const source = await readFile(comboSelectPath, 'utf8')
  assert.match(source, /navigate\(`\/combo\/edit\/\$\{encodeURIComponent\(template\.name\)\}`\)/)
  assert.doesNotMatch(source, /If read-only, open clone modal/)
})

test('Combo results does not edit catalog identity', async () => {
  const source = await readFile(comboResultsPath, 'utf8')
  assert.doesNotMatch(source, /combo-edit-identity/)
  assert.doesNotMatch(source, /\/identity/)
  assert.match(source, /data-testid="combo-result-title"/)
})
