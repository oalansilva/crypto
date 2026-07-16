import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import test from 'node:test'

const read = (path) => readFileSync(new URL(`../${path}`, import.meta.url), 'utf8')

test('trade explanation disclosure exposes the accessible disclosure contract', () => {
  const source = read('src/components/trades/TradeExplanationDisclosure.tsx')

  assert.match(source, /Entenda este trade/)
  assert.match(source, /aria-expanded=\{expanded\}/)
  assert.match(source, /aria-controls=\{panelId\}/)
  assert.match(source, /min-h-11/)
  assert.match(source, /focus-visible:ring-2 focus-visible:ring-\[#3b82f6\]/)
})

test('trade explanation distinguishes event timing, evidence and safe legacy fallback', () => {
  const source = read('src/components/trades/TradeExplanationDisclosure.tsx')

  assert.match(source, /Candle que confirmou/)
  assert.match(source, /Preço executado/)
  assert.match(source, /exit_rule: 'Regra de saída'/)
  assert.match(source, /stop_loss: 'Stop de perda'/)
  assert.match(source, /Confirmada/)
  assert.match(source, /Pendente/)
  assert.match(source, /Saída técnica/)
  assert.match(source, /Stop de proteção/)
  assert.match(source, /Detalhes da decisão não estão disponíveis para este trade histórico/)
})

test('frontend contract mirrors the additive public API fields', () => {
  const source = read('src/types/tradeExplanation.ts')

  assert.match(source, /'available' \| 'partial' \| 'unavailable' \| 'inconsistent'/)
  assert.match(source, /'entry_rule' \| 'exit_rule' \| 'stop_loss' \| 'take_profit' \| 'open_position'/)
  assert.match(source, /decision_candle_time\?: string/)
  assert.match(source, /execution_time\?: string/)
  assert.match(source, /evidence\?: TradeEvidenceItem\[\]/)
})

test('trade list integrates explanations without adding another table header', () => {
  const source = read('src/components/charts/StrategyTradesTable.tsx')

  assert.match(source, /entry_explanation\?: TradeExplanation/)
  assert.match(source, /exit_explanation\?: TradeExplanation/)
  assert.match(source, /current_state_explanation\?: TradeExplanation/)
  assert.match(source, /<TradeExplanationDisclosure/)
  assert.doesNotMatch(source, /<th[^>]*>Entenda este trade<\/th>/)
})

test('monitor trade builders preserve entry, exit and open-position explanations', () => {
  const chartModal = read('src/components/monitor/ChartModal.tsx')
  const favorites = read('src/pages/FavoritesDashboard.tsx')

  for (const source of [chartModal, favorites]) {
    assert.match(source, /entry_explanation: activeEntry\.explanation/)
    assert.match(source, /exit_explanation: item\.explanation/)
    assert.match(source, /current_state_explanation: currentStateExplanation/)
  }
})
