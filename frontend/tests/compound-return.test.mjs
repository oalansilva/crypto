import test from 'node:test'
import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
import {
  compoundReturnPoints,
  formatBoundedRatioPercent,
  formatCompoundReturn,
} from '../src/lib/compoundReturn.ts'

const __dirname = path.dirname(fileURLToPath(import.meta.url))

test('large compound prefers points and never shrinks ratio > 1', () => {
  assert.equal(compoundReturnPoints({ total_return: 985.9156, total_return_pct: 98591.56 }), 98591.56)
  assert.equal(compoundReturnPoints({ total_return: 985.9156 }), 98591.56)
  assert.equal(formatCompoundReturn({ total_return: 985.9156, total_return_pct: 98591.56 }).text, '+98591.56%')
  assert.equal(formatCompoundReturn({ total_return: 985.9156 }).text, '+98591.56%')
  assert.notEqual(formatCompoundReturn({ total_return: 985.9156 }).text, '+985.92%')
  assert.notEqual(formatCompoundReturn({ total_return: 985.9156 }).text, '985.92%')
})

test('contract 169.51 / 16951 reads as sixteen thousand percent', () => {
  assert.equal(compoundReturnPoints({ total_return: 169.51, total_return_pct: 16951 }), 16951)
  assert.equal(formatCompoundReturn({ total_return: 169.51, total_return_pct: 16951 }).text, '+16951.00%')
  assert.equal(formatCompoundReturn({ total_return: 169.51 }).text, '+16951.00%')
  assert.notEqual(formatCompoundReturn({ total_return: 169.51 }).text, '+169.51%')
})

test('compound under 100% stays around +35% from ratio or points', () => {
  assert.equal(formatCompoundReturn({ total_return: 0.35 }).text, '+35.00%')
  assert.equal(formatCompoundReturn({ total_return_pct: 35 }).text, '+35.00%')
  assert.equal(formatCompoundReturn({ total_return: 0.35, total_return_pct: 35 }).text, '+35.00%')
  assert.notEqual(formatCompoundReturn({ total_return: 0.35 }).text, '+0.35%')
  assert.notEqual(formatCompoundReturn({ total_return: 0.35 }).text, '+3500.00%')
  assert.notEqual(formatCompoundReturn({ total_return_pct: 35 }).text, '+3500.00%')
})

test('|value| > 1 heuristic remains only for win rate and drawdown', () => {
  assert.equal(formatBoundedRatioPercent(0.6875, 2), '68.75%')
  assert.equal(formatBoundedRatioPercent(0.1415, 2), '14.15%')
  assert.equal(formatBoundedRatioPercent(0.467, 2), '46.7%')
  assert.equal(formatBoundedRatioPercent(68.75, 2), '68.75%')
  assert.equal(formatBoundedRatioPercent(14.15, 2), '14.15%')
  assert.notEqual(formatCompoundReturn({ total_return: 985.91 }).text, formatBoundedRatioPercent(985.91, 2))
})

test('grade, resumo and Ver Trades share the compound helper', async () => {
  const favorites = await readFile(path.resolve(__dirname, '../src/pages/FavoritesDashboard.tsx'), 'utf8')
  const results = await readFile(path.resolve(__dirname, '../src/pages/ComboResultsPage.tsx'), 'utf8')
  const trades = await readFile(path.resolve(__dirname, '../src/components/charts/StrategyTradesTable.tsx'), 'utf8')
  assert.match(favorites, /formatCompoundReturn/)
  assert.match(results, /formatCompoundReturn/)
  assert.match(trades, /formatCompoundReturn/)
  assert.doesNotMatch(trades, /displayMetrics\.total_return \* 100\)\.toFixed\(2\)%/)
})
