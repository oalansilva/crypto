import test from 'node:test'
import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)
const configurePath = path.resolve(__dirname, '../src/pages/ComboConfigurePage.tsx')
const resultsPath = path.resolve(__dirname, '../src/pages/ComboResultsPage.tsx')
const modalPath = path.resolve(__dirname, '../src/components/SaveFavoriteModal.tsx')

test('walk-forward optimization opens results before favorite promotion', async () => {
  const source = await readFile(configurePath, 'utf8')

  assert.match(source, /if \(walkForwardEnabled \|\| oosVerdict\)/)
  assert.match(source, /navigate\('\/combo\/results', \{[\s\S]*isOptimization: true/)
  assert.match(source, /oos_verdict: oosVerdict/)
  assert.match(source, /oos_metrics: result\.oos_metrics \?\? null/)
  assert.match(source, /oos_proof: result\.oos_proof \?\? null/)
  assert.match(source, /start_date: start_date \?\? null/)
  assert.match(source, /end_date: end_date \?\? null/)
  assert.match(source, /period_type: period/)
})

test('favorite promotion action is limited to optimization results', async () => {
  const source = await readFile(resultsPath, 'utf8')

  assert.match(source, /const isOptimization = location\.state\?\.isOptimization === true/)
  assert.match(source, /\{isOptimization \? \([\s\S]*data-testid="save-favorite-button"/)
  assert.match(source, /\{isOptimization \? \([\s\S]*<SaveFavoriteModal/)
  assert.match(source, /start_date: result\.start_date \?\? null/)
  assert.match(source, /period_type: result\.period_type \?\? null/)
  assert.match(source, /oos_proof: result\.oos_proof \?\? null/)
  assert.match(source, /navigate\('\/favorites'\)/)
})

test('NO-GO override is visible only to admins', async () => {
  const source = await readFile(modalPath, 'utf8')

  assert.match(source, /const isAdmin = Boolean\(user\?\.isAdmin\)/)
  assert.match(source, /if \(isBlocked && !isAdmin\)/)
  assert.match(source, /\{isBlocked && isAdmin && \(/)
  assert.match(source, /disabled=\{isSaving \|\| !name\.trim\(\) \|\| \(isBlocked && \(!isAdmin \|\| !overrideOos\)\)\}/)
  assert.match(source, /start_date: backtestResult\.start_date \?\? null/)
  assert.match(source, /period_type: backtestResult\.period_type \?\? null/)
  assert.match(source, /oos_proof: backtestResult\.oos_proof \?\? null/)
})
