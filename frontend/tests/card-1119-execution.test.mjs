// Fuso do processo diferente de Nova York: os textos têm de vir no fuso da classe, não no do navegador.
process.env.TZ = 'America/Sao_Paulo'

import test from 'node:test'
import assert from 'node:assert/strict'
import * as equityExecution from '../src/lib/equityExecution.ts'
import {
  annualizationText,
  buildExecutionTexts,
  candleName,
  coverageNote,
  currencyOf,
  nyStamp,
  precisionView,
  provenanceLine,
  timeframeFact,
  toggleMeta,
} from '../src/lib/equityExecution.ts'

/**
 * Card #1119 (tarefas 7.1, 7.2 e 7.5): textos do bloco "Dados e execução", moeda da classe e hora
 * de Nova York. Os cenários são os do protótipo aprovado (NVDA 1d, SPY 1h short, BTC/USDT 4h).
 */

const NVDA = { symbol: 'NVDA', asset_class: 'stock', name: 'NVIDIA Corp', currency: 'USD' }
const SPY = { symbol: 'SPY', asset_class: 'etf', name: 'SPDR S&P 500 ETF Trust', currency: 'USD' }
const BTC = { symbol: 'BTC/USDT', asset_class: 'crypto', name: 'BTC', currency: 'USDT' }

const nvdaMissing = {
  precision_requested: 'intrabar',
  precision_effective: 'candle',
  timeframe: '1d',
  intraday_reason: 'coverage',
  intraday_missing: [{ from: '2014-11-11', to: '2026-05-18' }],
  gap_stops: 1,
  window: { requested: { start: null, end: null }, covered: { start: '2014-11-11T05:00:00Z', end: '2026-10-22T04:00:00Z', candles: 2990 } },
}
const equityConventions = {
  fee: 0.001,
  fee_confirmed: true,
  slippage: 0.0002,
  fraction: { simulated: true, confirms_account: false },
  short: null,
  adjusted_prices: true,
}
const provenance = { adjustment: 'adjusted', version_label: '3', kept_until: '2026-11-22T12:00:00Z' }

test('moeda da classe: USDT em cripto, USD em ação e ETF', () => {
  assert.equal(currencyOf(NVDA), 'USD')
  assert.equal(currencyOf(SPY), 'USD')
  assert.equal(currencyOf(BTC), 'USDT')
  assert.equal(currencyOf(null, 'ETH/USDT'), 'USDT')
  assert.equal(currencyOf({ symbol: 'AAPL', asset_class: 'stock' }), 'USD')
})

test('proveniência por classe', () => {
  assert.equal(provenanceLine(NVDA, provenance), 'Binance Ações · pregão regular de Nova York · ajustado por split · USD')
  assert.equal(provenanceLine(BTC, null), 'Binance Spot · 24/7 · ajuste não se aplica · USDT')
})

test('precisão diária só no 1d; nos outros tempos o candle tem o nome do tempo', () => {
  assert.equal(candleName('1d').title, 'Precisão diária')
  assert.equal(candleName('4h').title, 'Precisão do candle de 4h')
  assert.equal(candleName('4h').fact, 'Candle de 4h')
  assert.equal(candleName('1h').title, 'Precisão do candle de 1h')
})

test('NVDA todo o histórico: cai para o candle diário e diz o trecho sem intradiário', () => {
  const view = precisionView(nvdaMissing, { asset: NVDA })
  assert.equal(view.tone, 'warn')
  assert.equal(view.title, 'Precisão diária')
  assert.match(view.text, /O intradiário de 15m faltou de 11 nov\. 2014 a 18 mai\. 2026\./)
  assert.match(view.text, /Você pediu precisão intrabar/)
  assert.match(view.text, /o stop foi simulado no candle diário em toda a janela/)
  assert.equal(view.fact, 'Diária')
})

test('na Otimização quem pede o intrabar é a tela', () => {
  const view = precisionView(nvdaMissing, { asset: NVDA, page: 'optimize' })
  assert.match(view.text, /A Otimização pede precisão intrabar/)
})

test('cripto 4h sem 15m: "Precisão do candle de 4h", nunca "diária"', () => {
  const view = precisionView(
    { ...nvdaMissing, timeframe: '4h', intraday_missing: [{ from: '2026-08-01', to: '2026-08-20' }] },
    { asset: BTC },
  )
  assert.equal(view.title, 'Precisão do candle de 4h')
  assert.equal(view.fact, 'Candle de 4h')
  assert.doesNotMatch(`${view.title} ${view.text} ${view.fact}`, /\bdiári[ao]\b/i)
  assert.match(view.text, /candle de 4h em toda a janela/)
})

test('intrabar cobrindo a janela é informação, não aviso', () => {
  const view = precisionView(
    { precision_requested: 'intrabar', precision_effective: 'intrabar_15m', timeframe: '1h', intraday_missing: [] },
    { asset: SPY },
  )
  assert.equal(view.tone, 'info')
  assert.equal(view.title, 'Precisão intrabar 15m')
  assert.equal(view.fact, 'Intrabar 15m')
})

test('intrabar desligado é precisão escolhida, sem aviso', () => {
  const view = precisionView(
    { precision_requested: 'daily', precision_effective: 'candle', timeframe: '1d', intraday_missing: [] },
    { asset: NVDA },
  )
  assert.equal(view.tone, 'info')
  assert.match(view.title, /escolhida/)
})

test('erro ao ler o intradiário é aviso com o motivo', () => {
  const view = precisionView(
    { ...nvdaMissing, intraday_reason: 'read_error', intraday_missing: [{ from: '2026-01-02', to: '2026-10-22' }] },
    { asset: NVDA },
  )
  assert.equal(view.tone, 'warn')
  assert.match(view.text, /Não foi possível ler o intradiário/)
})

test('resultado antigo sem execution não tem precisão', () => {
  assert.equal(precisionView(null, { asset: NVDA }), null)
  assert.equal(precisionView({}, { asset: NVDA }), null)
})

test('coleta que parou no meio vira a nota "Janela coberta menor que a pedida"', () => {
  const note = coverageNote({
    collection: {
      status: 'partial',
      kind: 'tail',
      series: '1d',
      symbol: 'NVDA',
      reason: 'limite de requisições da Binance',
      stopped_after: '2026-10-02T04:00:00Z',
      covered: { start: '2014-11-11T05:00:00Z', end: '2026-10-02T04:00:00Z' },
      requested: { start: null, end: '2026-10-22' },
      left_out: [{ from: '2026-10-05', to: '2026-10-22' }],
    },
  })
  assert.equal(note.title, 'Janela coberta menor que a pedida')
  assert.match(note.text, /A coleta do 1d de NVDA parou depois de guardar até 02 out\. 2026/)
  assert.match(note.text, /de 05 out\. 2026 a 22 out\. 2026 ficou fora/)
  assert.equal(coverageNote({ collection: null }), null)
})

test('tempo gráfico de ação/ETF: montado do 5m no pregão', () => {
  assert.deepEqual(timeframeFact(NVDA, '1d'), { value: '1d nativo', note: '1 candle por pregão' })
  assert.equal(timeframeFact(SPY, '1h').value, '1h montado do 5m')
  assert.match(timeframeFact(SPY, '1h').note, /15:30–16:00; nenhum candle atravessa o fechamento/)
  assert.match(timeframeFact(SPY, '4h').note, /09:30–13:30 e 13:30–16:00 \(meio-pregão: 09:30–13:00\)/)
  assert.match(timeframeFact(SPY, '15m').note, /15:45–16:00/)
  assert.deepEqual(timeframeFact(BTC, '4h'), { value: '4h nativo', note: null })
})

test('anualização: Sharpe e Sortino por operação, sem anualização, em qualquer classe', () => {
  assert.equal(
    annualizationText(),
    'Anos pelo calendário (dias corridos ÷ 365). Sharpe e Sortino por operação, sem anualização.',
  )
  assert.doesNotMatch(annualizationText(), /252|pregões|candles/)
})

test('NVDA 1d: 8 fatos, 6 convenções e os avisos do celular', () => {
  const texts = buildExecutionTexts({
    asset: NVDA,
    provenance,
    execution: nvdaMissing,
    conventions: { ...equityConventions, fee_confirmed: false, fee: 0.00075 },
    timeframe: '1d',
    periodAll: true,
    gapTrades: [{ exit_reason: 'stop_loss_gap', exit_time: '2026-02-26T05:00:00Z', exit_price: 172.1, stop_price: 181.74 }],
  })
  assert.deepEqual(texts.facts.map((f) => f.key), ['asset', 'source', 'adjustment', 'timeframe', 'requested', 'covered', 'sample', 'precision'])
  assert.equal(texts.facts.find((f) => f.key === 'requested').value, 'Todo o histórico')
  assert.deepEqual(texts.conventions.map((c) => c.key), ['gap', 'costs', 'fraction', 'calendar', 'annualization', 'adjusted'])
  assert.equal(toggleMeta(texts), '8 fatos · 6 convenções')
  assert.deepEqual(texts.alerts, ['1 saída com gap', 'taxa assumida', 'posição com fração'])
  const gap = texts.conventions.find((c) => c.key === 'gap').text
  assert.match(gap, /Nesta execução: 1 saída com gap \(26 fev\. 2026: stop 181,74, abertura 172,10\)\./)
  assert.match(texts.conventions.find((c) => c.key === 'costs').text, /assumida/)
})

test('taxa confirmada tira o "assumida" dos custos e dos avisos', () => {
  const texts = buildExecutionTexts({
    asset: NVDA,
    provenance,
    execution: { ...nvdaMissing, gap_stops: 0 },
    conventions: equityConventions,
    timeframe: '1d',
  })
  const costs = texts.conventions.find((c) => c.key === 'costs').text
  assert.match(costs, /Taxa de 0,1% por lado, confirmada na Binance Ações\./)
  assert.match(costs, /Slippage de 0,02% por lado no 1d\./)
  assert.doesNotMatch(costs, /assumida/)
  assert.deepEqual(texts.alerts, ['posição com fração'])
})

test('ETF short avisa que o short é só simulação e lista os preços ajustados', () => {
  const texts = buildExecutionTexts({
    asset: SPY,
    provenance,
    execution: { precision_requested: 'intrabar', precision_effective: 'intrabar_15m', timeframe: '1h', gap_stops: 0 },
    conventions: { ...equityConventions, short: { simulated: true, confirms_account: false } },
    timeframe: '1h',
  })
  const keys = texts.conventions.map((c) => c.key)
  assert.ok(keys.includes('short') && keys.includes('adjusted'))
  assert.equal(
    texts.conventions.find((c) => c.key === 'adjusted').text,
    'Entrada, saída e stop usam a série ajustada por split e podem diferir do preço negociado na época.',
  )
  assert.match(texts.conventions.find((c) => c.key === 'short').text, /não indica que a sua conta/)
  assert.ok(texts.alerts.includes('short simulado'))
})

test('cripto: sem fração, sem preços ajustados, calendário 24/7, tudo em USDT', () => {
  const texts = buildExecutionTexts({
    asset: BTC,
    provenance: { version_label: '12' },
    execution: { precision_requested: 'intrabar', precision_effective: 'candle', timeframe: '4h', intraday_reason: 'coverage', intraday_missing: [{ from: '2026-08-01', to: '2026-08-20' }], gap_stops: 0 },
    conventions: { fee: 0.00075, fee_confirmed: true, slippage: 0.0002, fraction: null, short: null },
    timeframe: '4h',
  })
  const keys = texts.conventions.map((c) => c.key)
  assert.deepEqual(keys, ['gap', 'costs', 'calendar', 'annualization'])
  assert.equal(texts.facts.find((f) => f.key === 'adjustment').note, 'USDT')
  assert.equal(texts.facts.find((f) => f.key === 'precision').value, 'Candle de 4h')
  assert.match(texts.facts.find((f) => f.key === 'sample').note, /Favoritos guarda a amostra do último refresh/)
  assert.doesNotMatch(texts.alerts.join(' '), /taxa assumida|fração/)
})

test('hora de Nova York no intradiário: EDT no verão, EST no inverno, fuso do navegador ignorado', () => {
  assert.deepEqual(nyStamp('2026-08-27T13:30:00Z'), { date: 'Aug 27, 2026', time: '09:30 EDT' })
  assert.deepEqual(nyStamp('2026-12-01T14:30:00Z'), { date: 'Dec 1, 2026', time: '09:30 EST' })
  // virada do horário de verão (8 mar. 2026): o pregão continua abrindo às 09:30 de Nova York
  assert.equal(nyStamp('2026-03-06T14:30:00Z').time, '09:30 EST')
  assert.equal(nyStamp('2026-03-09T13:30:00Z').time, '09:30 EDT')
  assert.equal(nyStamp(undefined), null)
  assert.equal(nyStamp('lixo'), null)
})

test('card #1122: ação e ETF são favoritáveis; o motivo da recusa saiu', () => {
  assert.equal('FAVORITE_REFUSED_REASON' in equityExecution, false)
})
