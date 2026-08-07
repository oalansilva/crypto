import assert from 'node:assert/strict'
import { existsSync, readFileSync } from 'node:fs'
import test from 'node:test'

const read = (path) => readFileSync(new URL(`../${path}`, import.meta.url), 'utf8')

test('operation list has no per-operation decision disclosure', () => {
  const source = read('src/components/charts/StrategyTradesTable.tsx')
  const disclosurePath = new URL('../src/components/trades/TradeExplanationDisclosure.tsx', import.meta.url)

  assert.doesNotMatch(source, /TradeExplanationDisclosure/)
  assert.doesNotMatch(source, /Ver decisão da operação/)
  assert.equal(existsSync(disclosurePath), false)
})

test('frontend contract mirrors the additive public API fields', () => {
  const source = read('src/types/tradeExplanation.ts')

  assert.match(source, /'available' \| 'partial' \| 'unavailable' \| 'inconsistent'/)
  assert.match(source, /'entry_rule' \| 'exit_rule' \| 'stop_loss' \| 'take_profit' \| 'open_position'/)
  assert.match(source, /decision_candle_time\?: string/)
  assert.match(source, /execution_time\?: string/)
  assert.match(source, /evidence\?: TradeEvidenceItem\[\]/)
})

test('trade list preserves explanation payload fields without rendering another control', () => {
  const source = read('src/components/charts/StrategyTradesTable.tsx')

  assert.match(source, /entry_explanation\?: TradeExplanation/)
  assert.match(source, /exit_explanation\?: TradeExplanation/)
  assert.match(source, /current_state_explanation\?: TradeExplanation/)
  assert.doesNotMatch(source, /<TradeExplanationDisclosure/)
  assert.doesNotMatch(source, /Ver decisão da operação/)
  assert.doesNotMatch(source, /<th[^>]*>Entenda este trade<\/th>/)
  assert.doesNotMatch(source, /strategyTransparency=/)
})

test('results page keeps permanent rules without per-operation decisions', () => {
  const source = read('src/pages/ComboResultsPage.tsx')
  const rules = read('src/components/trades/StrategyRuleOverview.tsx')
  const trades = read('src/components/charts/StrategyTradesTable.tsx')

  assert.match(source, /id="combo-result-strategy-rules"/)
  assert.match(rules, /Regras da estratégia/)
  assert.match(rules, /Condições usadas para entrada, saída e proteção da operação\./)
  assert.doesNotMatch(trades, /TradeExplanationDisclosure/)
  assert.doesNotMatch(trades, /Ver decisão da operação/)
})

test('permanent rule overview separates strategy contract from current event', () => {
  const source = read('src/components/trades/StrategyRuleOverview.tsx')
  const card = read('src/components/monitor/OpportunityCard.tsx')

  assert.match(source, /Regras da estratégia/)
  assert.match(source, /Condições usadas para entrada, saída e proteção da operação\./)
  assert.doesNotMatch(source, /Como funciona a estratégia/)
  assert.doesNotMatch(source, /Estas regras não mudam com a posição atual do trade/)
  assert.match(source, /lg:grid-cols-3/)
  assert.match(source, /rules\.risk/)
  assert.doesNotMatch(source, /sm:grid-cols-2/)
  assert.match(source, /aria-labelledby/)
  assert.match(card, /monitor-strategy-rules-/)
  assert.match(card, /O que aconteceu agora/)
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
