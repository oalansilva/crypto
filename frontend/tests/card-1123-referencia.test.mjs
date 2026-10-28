// Card #1123: comparação com referência, seletor, coluna extra do Decidir e tag de Favoritos (lógica pura).
process.env.TZ = 'UTC'

import test from 'node:test'
import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import {
  CURRENCY_NOTE_TEXT,
  SECTION_SUBTITLE,
  annualBr,
  cellView,
  columnChoiceHints,
  columnHeader,
  commonText,
  favoriteRefTag,
  fxPair,
  holdLabel,
  insufficientHelp,
  isPriceNoDividends,
  leftOutText,
  pctDot,
  ppBr,
  ppDot,
  promotionReferenceNote,
  showPromotionReferenceNote,
  recordedTail,
  recordedWhen,
  referenceName,
  resultChoiceHint,
  sampleText,
  sectionNumbers,
  stripSummary,
  COLUMN_HINT,
} from '../src/lib/benchmarkComparison.ts'
import { EXTRA_COLUMN_KEEPS, rowSampleWithColumn } from '../src/lib/sampleState.ts'

const SPY = { kind: 'catalog', symbol: 'SPY', asset_class: 'etf', currency: 'USD', return_kind: 'price_no_dividends', long_only: true }
const BTC_OWN = { kind: 'own', symbol: 'BTC/USDT', asset_class: 'crypto', currency: 'USDT', return_kind: 'price', long_only: true }

const valid = (overrides = {}) => ({
  id: 'c1',
  created_at: '2026-10-27T17:32:00Z',
  trigger: 'choice',
  owner: { kind: 'result' },
  reference: SPY,
  strategy: { symbol: 'BTC/USDT', return: 63.5266, cagr: 1.0037, trades_in: 9, trades_out: 0, window: { start: '2019-01-01', end: '2024-12-31' } },
  reference_result: { return: 1.3426, cagr: 0.1525, first_close: { date: '2019-01-02', price: 1 }, last_close: { date: '2024-12-31', price: 2 } },
  common_window: { start: '2019-01-02', end: '2024-12-31', days: 2190 },
  left_out: [{ start: '2019-01-01', end: '2019-01-01', trades: 0, note: 'no_session' }],
  delta: { cagr_pp: 85.12 },
  currency_note: 'usdt_as_usd',
  status: 'valid',
  reason: null,
  samples: { reference: { snapshot_id: 'snap1', version_label: '5' } },
  ...overrides,
})

const insufficient = (code, text) =>
  valid({
    status: 'insufficient',
    reason: { code, text, short: text },
    reference_result: null,
    delta: null,
    common_window: code === 'short_overlap' ? { start: '2024-12-17', end: '2024-12-31', days: 14 } : null,
    strategy: { symbol: 'BTC/USDT', return: null, cagr: null, trades_in: null, trades_out: null },
  })

test('seção: números no formato do "Retorno total" e diferença em p.p.', () => {
  const n = sectionNumbers(valid())
  assert.equal(n.sRet, '+6352.66%')
  assert.equal(n.sCagr, '+100.37%')
  assert.equal(n.rCagr, '+15.25%')
  assert.equal(n.delta, '+85.1 p.p.')
  assert.equal(n.deltaTone, 'up')
  assert.equal(n.deltaNote, 'a favor da estratégia')
  assert.equal(ppDot(-43.1), '−43.1 p.p.')
  assert.equal(pctDot(-0.1), '−10.00%')
  assert.equal(SECTION_SUBTITLE.endsWith('CAGR com dias corridos ÷ 365,25'), true)
})

test('período comum e o que ficou de fora (feriado de NY e trades fora)', () => {
  assert.equal(commonText(valid().common_window), '02 jan. 2019 – 31 dez. 2024 · 2.190 dias')
  assert.equal(leftOutText(valid()), '01 jan. 2019 (sem pregão em Nova York) · 0 trades')
  const sol = valid({ left_out: [{ start: '2019-01-01', end: '2020-08-10', trades: 3, note: 'no_reference' }] })
  assert.equal(leftOutText(sol), '01 jan. 2019 – 10 ago. 2020 da estratégia · 3 trades fora')
  assert.equal(leftOutText(valid({ left_out: [] })), 'Nada: a referência cobre o período inteiro da estratégia.')
})

test('insuficiente: sem número, sem zero e frase de apoio própria por motivo', () => {
  for (const code of ['no_overlap', 'short_overlap']) {
    const payload = insufficient(code, 'x')
    assert.equal(sectionNumbers(payload), null)
  }
  assert.notEqual(insufficientHelp('no_overlap'), insufficientHelp('short_overlap'))
  assert.match(insufficientHelp('short_overlap'), /anualizar exagera o CAGR/)
  assert.equal(insufficientHelp('no_overlap'), 'Escolha outra referência com histórico no período da estratégia.')
})

test('aviso de moeda com as duas moedas e retorno de preço de ação/ETF', () => {
  assert.equal(fxPair('BTC/USDT', 'USDT', SPY), 'BTC/USDT em USDT, SPY em USD')
  assert.equal(fxPair('NVDA', 'USD', BTC_OWN), 'NVDA em USD, BTC/USDT em USDT')
  assert.equal(CURRENCY_NOTE_TEXT, 'USDT tratado como USD, sem conversão. A comparação é só em percentual.')
  assert.equal(isPriceNoDividends(SPY), true)
  assert.equal(isPriceNoDividends(BTC_OWN), false)
  assert.equal(referenceName(BTC_OWN, 'BTC/USDT'), 'BTC/USDT (próprio ativo)')
  assert.equal(holdLabel('short'), 'buy-and-hold long-only')
  assert.equal(holdLabel('long'), 'buy-and-hold')
})

test('linha de gravação: rodada nova, troca e favorito (refeita só no refresh)', () => {
  assert.equal(recordedWhen(valid({ trigger: 'run' }), { owner: 'result' }), 'Gravada ao rodar, em 27/10/2026, 14:32.')
  assert.equal(recordedWhen(valid(), { owner: 'result' }), 'Gravada neste resultado em 27/10/2026, 14:32.')
  assert.equal(
    recordedWhen(valid({ owner: { kind: 'favorite' } }), { owner: 'favorite', favoriteName: 'NVDA Trend' }),
    'Gravada no favorito NVDA Trend em 27/10/2026, 14:32.',
  )
  assert.equal(recordedTail({ owner: 'favorite' }), 'Refeita só quando o backtest do favorito é atualizado, com a mesma referência.')
  assert.equal(recordedTail({ owner: 'result' }), 'Ao salvar nos Favoritos, a referência vai junto.')
  assert.equal(sampleText(valid(), 'favorite'), 'SPY versão 5 (fixada pelo favorito)')
  assert.equal(sampleText(valid({ collected: true }), 'result'), 'SPY versão 5 (coletada agora)')
})

const asset = (from, to = '2026-10-27T00:00:00Z') => ({ history: { status: 'covered', from, to, timeframes: [{ timeframe: '1d', from, to }] } })

test('aviso antes da escolha no resultado: sem período comum e "Só N dias"', () => {
  const window = { start: '2019-01-01T00:00:00Z', end: '2024-12-31T00:00:00Z' }
  assert.deepEqual(resultChoiceHint(asset('2025-06-05T04:00:00Z'), window), { tone: 'warn', text: 'Sem período comum com esta estratégia' })
  assert.deepEqual(resultChoiceHint(asset('2024-12-17T00:00:00Z'), window), { tone: 'warn', text: 'Só 14 dias em comum com esta estratégia' })
  assert.equal(resultChoiceHint(asset('2003-01-02T05:00:00Z'), window), null)
  assert.equal(resultChoiceHint({ history: { status: 'on_demand', from: null, to: null } }, window), null)
})

const CANDS = [
  { result_id: 'a', symbol: 'BTC/USDT', start: '2019-01-01', end: '2024-12-31', sample: 'kept' },
  { result_id: 'b', symbol: 'NVDA', start: '2019-01-02', end: '2024-12-31', sample: 'kept' },
  { result_id: 'c', symbol: 'PENGU/USDT', start: '2024-12-17', end: '2024-12-31', sample: 'kept' },
]

test('aviso contado sobre os candidatos (Decidir), com amostra vencida', () => {
  assert.deepEqual(columnChoiceHints(asset('2003-01-02T05:00:00Z'), CANDS), [
    { tone: 'note', text: '1 candidato com período comum curto (PENGU/USDT)' },
  ])
  assert.deepEqual(columnChoiceHints(asset('2025-06-05T04:00:00Z'), CANDS), [
    { tone: 'warn', text: 'Sem período comum com nenhum candidato desta varredura' },
  ])
  const expired = CANDS.map((c, i) => ({ ...c, sample: i === 0 ? 'expired' : 'kept' }))
  assert.deepEqual(columnChoiceHints(asset('2003-01-02T05:00:00Z'), expired).at(-1), { tone: 'note', text: '1 candidato com amostra vencida' })
  const allExpired = CANDS.map((c) => ({ ...c, sample: 'expired' }))
  assert.match(columnChoiceHints(asset('2003-01-02T05:00:00Z'), allExpired)[0].text, /rode a varredura de novo/)
})

test('célula do Decidir em pt-BR; calculando e sem comparação sem número', () => {
  const view = cellView({ state: 'valid', delta_cagr_pp: 66.84, reference_cagr: 0.1525, common_window: { start: '2019-01-02', end: '2024-12-31', days: 2190 }, currency_note: 'usdt_as_usd' }, 'SPY', false)
  assert.equal(view.delta, '+66,8 p.p.')
  assert.equal(view.refLine, 'SPY +15,25% a.a.')
  assert.equal(view.period, '2 jan. 2019 – 31 dez. 2024')
  assert.equal(view.fx, true)
  const busy = cellView({ state: 'pending' }, 'SPY', true)
  assert.deepEqual(busy, { kind: 'busy', text: 'Calculando…' })
  // Fora do cálculo, a célula não gravada não fica "Calculando…".
  assert.deepEqual(cellView({ state: 'pending' }, 'SPY', false), { kind: 'no_sample', text: 'Não calculada' })
  assert.deepEqual(cellView(null, 'SPY', false), { kind: 'no_sample', text: 'Não calculada' })
  const noCagr = cellView({ state: 'insufficient', reason_code: 'no_cagr', reason: 'Sem CAGR gravado do candidato.' }, 'SPY', false)
  assert.deepEqual(noCagr, { kind: 'off', title: 'Sem comparação', reason: 'Sem CAGR gravado do candidato.', code: 'no_cagr' })
  const off = cellView({ state: 'insufficient', reason_code: 'short_overlap', reason: 'Período comum de 14 dias: o mínimo é 30.' }, 'SPY', false)
  assert.equal(off.kind, 'off')
  assert.equal(off.title, 'Sem comparação')
  assert.doesNotMatch(JSON.stringify(off), /%|p\.p\.|0,00/)
  assert.deepEqual(cellView({ state: 'no_sample' }, 'SPY', false), { kind: 'no_sample', text: 'Sem amostra' })
  assert.equal(ppBr(-3.2), '−3,2 p.p.')
  assert.equal(annualBr(0.7057), '+70,57% a.a.')
  assert.equal(columnHeader('SPY'), 'Contra SPY')
  assert.equal(COLUMN_HINT, 'Δ CAGR · período comum · não ordena')
})

test('resumo da faixa conta a varredura e diz o motivo, inclusive amostra vencida', () => {
  assert.equal(
    stripSummary({ valid: 4, short_overlap: 1, computed: 5, total: 5 }, 'SPY'),
    '4 de 5 candidatos desta varredura com comparação; 1 sem comparação (período comum curto).',
  )
  assert.equal(
    stripSummary({ valid: 3, short_overlap: 1, sample_expired: 1, computed: 5, total: 5 }, 'SPY'),
    '3 de 5 candidatos desta varredura com comparação; 1 sem comparação (período comum curto); 1 sem comparação (amostra vencida).',
  )
  assert.match(stripSummary({ valid: 0, no_overlap: 5, computed: 5, total: 5 }, 'CRCL'), /^Nenhum candidato desta varredura tem período comum com CRCL/)
})

test('cripto sem amostra: refazível pelo caminho antigo não é aviso; sem as velas ou trades que não batem dizem o motivo, nunca "vencida"', () => {
  const legacy = CANDS.map((c, i) => ({ ...c, sample: i === 0 ? 'legacy' : 'kept' }))
  assert.deepEqual(columnChoiceHints(asset('2003-01-02T05:00:00Z'), legacy), [
    { tone: 'note', text: '1 candidato com período comum curto (PENGU/USDT)' },
  ])
  const unavailable = CANDS.map((c, i) => ({ ...c, sample: i === 0 ? 'unavailable' : 'kept' }))
  const hints = columnChoiceHints(asset('2003-01-02T05:00:00Z'), unavailable)
  assert.deepEqual(hints.at(-1), { tone: 'note', text: '1 candidato sem as velas da varredura' })
  assert.doesNotMatch(JSON.stringify(hints), /vencida/)
  const allUnavailable = CANDS.map((c) => ({ ...c, sample: 'unavailable' }))
  assert.deepEqual(columnChoiceHints(asset('2003-01-02T05:00:00Z'), allUnavailable), [
    { tone: 'warn', text: 'Todos os 3 candidatos sem as velas da varredura: rode a varredura de novo para comparar' },
  ])
  const mixed = CANDS.map((c, i) => ({ ...c, sample: i === 0 ? 'expired' : 'unavailable' }))
  assert.match(columnChoiceHints(asset('2003-01-02T05:00:00Z'), mixed)[0].text, /^Nenhum dos 3 candidatos tem amostra ou velas da varredura/)
  assert.equal(
    stripSummary({ valid: 3, short_overlap: 1, sample_unavailable: 1, computed: 5, total: 5 }, 'SPY'),
    '3 de 5 candidatos desta varredura com comparação; 1 sem comparação (período comum curto); 1 sem comparação (sem os trades da varredura).',
  )
  const off = cellView({ state: 'insufficient', reason_code: 'sample_unavailable', reason: 'Trades refeitos não batem com a varredura.' }, 'SPY', false)
  assert.deepEqual(off, { kind: 'off', title: 'Sem comparação', reason: 'Trades refeitos não batem com a varredura.', code: 'sample_unavailable' })
})

test('linha do candidato: só a amostra que existe fica "guardada pela coluna extra"', () => {
  const row = (sample) => ({ timeframe: '1d', candle_source: 'ccxt', sample })
  assert.equal(rowSampleWithColumn(row({ state: 'none', retain_until: null }), true).sample, 'sem amostra guardada')
  assert.equal(rowSampleWithColumn(row(null), true).sample, 'sem amostra guardada')
  assert.equal(rowSampleWithColumn(row({ state: 'kept', retain_until: '2026-11-25T00:00:00Z' }), true).sample, EXTRA_COLUMN_KEEPS)
  assert.equal(rowSampleWithColumn(row({ state: 'pinned', retain_until: null }), true).sample, EXTRA_COLUMN_KEEPS)
  const expired = rowSampleWithColumn(row({ state: 'expired', retain_until: '2026-09-30T00:00:00Z' }), true)
  assert.equal(expired.sampleTone, 'expired')
  assert.notEqual(expired.sample, EXTRA_COLUMN_KEEPS)
  assert.equal(rowSampleWithColumn(row({ state: 'kept', retain_until: '2026-11-25T00:00:00Z' }), false).sample, 'amostra até 25 nov. 2026')
})

test('Favoritos: Ref. só fora do padrão; promoção diz o que leva', () => {
  assert.equal(
    favoriteRefTag({ id: 'x', status: 'valid', created_at: '2026-10-27T12:14:00Z', reference: { kind: 'catalog', symbol: 'SPY' } }),
    'Ref.: SPY · comparação gravada 27/10',
  )
  assert.equal(favoriteRefTag({ id: 'x', status: 'valid', created_at: '2026-10-27T12:14:00Z', reference: { kind: 'own', symbol: 'NVDA' } }), null)
  assert.equal(favoriteRefTag(null), null)
  assert.match(promotionReferenceNote({ state: 'valid' }, 'SPY'), /^Leva a comparação com SPY gravada/)
  assert.match(promotionReferenceNote({ state: 'insufficient' }, 'SPY'), /referência padrão \(próprio ativo\)/)
  // O backend herda a célula de qualquer coluna ativa: com a coluna calculando, a nota aparece se a célula já é válida.
  assert.equal(showPromotionReferenceNote('done', { state: 'insufficient' }), true)
  assert.equal(showPromotionReferenceNote('computing', { state: 'valid' }), true)
  assert.equal(showPromotionReferenceNote('computing', { state: 'pending' }), false)
  assert.equal(showPromotionReferenceNote('computing', null), false)
  assert.equal(showPromotionReferenceNote(null, { state: 'valid' }), false)
})

test('seletor: modal de escolha única com foco preso, Esc e ativo marcado desabilitado com motivo', async () => {
  const src = await readFile(new URL('../src/components/results/ReferencePicker.tsx', import.meta.url), 'utf8')
  assert.match(src, /role="dialog"/)
  assert.match(src, /aria-modal="true"/)
  assert.match(src, /event\.key === 'Escape'/)
  assert.match(src, /event\.key !== 'Tab'/)
  assert.match(src, /aria-describedby=\{marked \? `\$\{id\}-why` : undefined\}/)
  assert.match(src, /Não pode ser escolhido como referência\./)
  assert.match(src, /target\?\.focus\(\)/)
  const section = await readFile(new URL('../src/components/results/BenchmarkComparison.tsx', import.meta.url), 'utf8')
  // Gravando/coletando: a grade de números só existe no estado válido.
  assert.match(section, /state === 'valid' && numbers && comparison \?/)
  assert.match(section, /role="alert"/)
  const fav = await readFile(new URL('../src/pages/FavoritesDashboard.tsx', import.meta.url), 'utf8')
  assert.doesNotMatch(fav, /from 'xlsx'/)
  assert.match(fav, /favorites\/export\?ids=/)
})
