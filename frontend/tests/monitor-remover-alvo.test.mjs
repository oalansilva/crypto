import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import test from 'node:test'

const read = (path) => readFileSync(new URL(`../${path}`, import.meta.url), 'utf8')

const HOLD_ORDER = [
  'distância até saída',
  'distância até stop',
  'stop',
  'entrada',
  'preço atual',
]
const UNAVAILABLE = 'indisponível — dado não confiável'
const EXIT_EMPTY = 'posição encerrada segundo a estratégia — sem risco residual mapeado'
const ALVO_RE = /alvoPrice|alvoStr|chartAlvoPrice|<dt>\s*alvo\s*<\/dt>|>Alvo<|>alvo</
const DERIVED_ALVO_RE = /last_price\s*\*\s*\(1\s*[+-]\s*dist\s*\/\s*100\)/

function dts(source) {
  return [...source.matchAll(/<dt>([^<]+)<\/dt>/g)].map((m) => m[1].trim().toLowerCase())
}

function cardHoldLabels(source) {
  const labels = dts(source)
  const start = labels.indexOf('distância até saída')
  assert.notEqual(start, -1, 'HOLD kv missing distância até saída')
  return labels.slice(start, start + HOLD_ORDER.length)
}

function cardExitLabels(source) {
  const labels = dts(source)
  const start = labels.indexOf('distância até saída')
  return labels.slice(start + HOLD_ORDER.length)
}

function modalHoldLabels(source) {
  const startToken = '<span className="text-[#929aa5]">distância até saída</span>'
  const endToken = '<span className="text-[#929aa5]">Preço atual</span>'
  const start = source.indexOf(startToken)
  const end = source.indexOf(endToken, start)
  assert.ok(start !== -1 && end !== -1, 'ChartModal HOLD kv markers missing')
  const block = source.slice(start, end + endToken.length)
  return [...block.matchAll(/text-\[#929aa5\]">([^<]+)</g)].map((m) => m[1].trim().toLowerCase())
}

function modalExitBlock(source) {
  const idx = source.lastIndexOf('>Preço atual<')
  assert.ok(idx !== -1, 'ChartModal EXIT preço atual missing')
  return source.slice(idx)
}

test('4.1 product sources no longer declare alvo fields or derived calculation', () => {
  const card = read('src/components/monitor/OpportunityCard.tsx')
  const modal = read('src/components/monitor/ChartModal.tsx')

  for (const source of [card, modal]) {
    assert.doesNotMatch(source, ALVO_RE)
    assert.doesNotMatch(source, DERIVED_ALVO_RE)
    assert.doesNotMatch(source, /alvo indisponível/i)
    assert.doesNotMatch(source, /data-alvo-row/)
  }
})

test('HOLD confiável: card order without alvo matches aceite', () => {
  const card = read('src/components/monitor/OpportunityCard.tsx')
  const labels = cardHoldLabels(card)

  assert.deepEqual(labels, HOLD_ORDER)
  assert.ok(!labels.includes('alvo'))
  assert.match(card, /Se o preço cruzar/)
})

test('HOLD stale: unavailable copy remains; no alvo line', () => {
  const card = read('src/components/monitor/OpportunityCard.tsx')
  const modal = read('src/components/monitor/ChartModal.tsx')

  for (const source of [card, modal]) {
    assert.match(source, /indisponível — dado não confiável/)
    assert.doesNotMatch(source, /alvo indisponível/i)
  }
  assert.equal(UNAVAILABLE, 'indisponível — dado não confiável')
  assert.ok(!cardHoldLabels(card).includes('alvo'))
  assert.ok(!modalHoldLabels(modal).includes('alvo'))
})

test('EXIT: preço atual + Risco residual, sem alvo', () => {
  const card = read('src/components/monitor/OpportunityCard.tsx')
  const modal = read('src/components/monitor/ChartModal.tsx')

  assert.deepEqual(cardExitLabels(card), ['preço atual'])
  assert.match(card, /Risco residual/)
  assert.match(card, new RegExp(EXIT_EMPTY))
  assert.doesNotMatch(card, ALVO_RE)

  const exit = modalExitBlock(modal)
  assert.match(exit, /Preço atual/)
  assert.match(exit, /Risco residual/)
  assert.match(modal, new RegExp(EXIT_EMPTY))
  assert.doesNotMatch(exit, ALVO_RE)
  assert.doesNotMatch(exit, />Stop</)
  assert.doesNotMatch(exit, />Entrada</)
})

test('coerência card↔modal: mesmo recorte HOLD e EXIT sem alvo', () => {
  const card = read('src/components/monitor/OpportunityCard.tsx')
  const modal = read('src/components/monitor/ChartModal.tsx')

  assert.deepEqual(cardHoldLabels(card), modalHoldLabels(modal))
  assert.deepEqual(cardHoldLabels(card), HOLD_ORDER)
  assert.match(card, /residual-block/)
  assert.match(modal, /residual-block/)
  assert.match(card, /Risco residual/)
  assert.match(modal, /Risco residual/)
})

test('proto after-variant HOLD order matches product card (layout spec)', () => {
  const proto = read('public/prototypes/card-803-monitor-remover-alvo/index.html')
  const after = proto.match(/sol:\s*\{[\s\S]*?after:\s*"([^"]+)"/)
  assert.ok(after, 'expected SOL after kv in prototype')
  const protoLabels = [...after[1].matchAll(/<dt>([^<]+)<\/dt>/g)].map((m) => m[1].trim().toLowerCase())
  const card = read('src/components/monitor/OpportunityCard.tsx')

  assert.deepEqual(protoLabels, HOLD_ORDER)
  assert.deepEqual(cardHoldLabels(card), protoLabels)
  assert.ok(!protoLabels.includes('alvo'))
})
