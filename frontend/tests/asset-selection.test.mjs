import test from 'node:test'
import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import {
  CLASS_NOTE,
  blockedNotice,
  catalogBanners,
  confirmCopy,
  cryptoOnlyTimeframes,
  emptySearchMessage,
  equityTimeframeBlock,
  formatDate,
  formatDateTime,
  freshnessLine,
  historyText,
  historySummary,
  ON_DEMAND_TEXT_BACKTEST,
  markedNoteText,
  marketDataText,
  markedReasonText,
  mergeSymbols,
  outEntries,
  outLabel,
  outNames,
  outOfSweepTitle,
  outReason,
  outWhy,
  planRun,
  preflightExcludedLabel,
  preflightRestLine,
  refusalMessage,
  resolveSelection,
  runCopy,
  selectionCountText,
  selectionCounts,
  sortedForChips,
  timeframeDisabled,
  urlSymbolNotice,
} from '../src/lib/assetSelection.ts'

const asset = (symbol, asset_class, state = 'tradable', extra = {}) => ({
  asset_id: `${asset_class === 'crypto' ? 'binance:spot:' : 'binance:equity:EQ_'}${symbol}`,
  asset_class,
  symbol,
  name: symbol,
  state,
  state_label:
    { tradable: 'Negociável', suspended: 'Suspenso', off_market: 'Fora de mercado', removed: 'Removido' }[state] ?? state,
  state_reason: state === 'suspended' ? 'Negociação pausada pela Binance (status BREAK).' : null,
  selectable: state === 'tradable',
  analysis_available: asset_class === 'crypto',
  history: { status: 'on_demand', from: null, to: null, timeframes: [], gap_count: 0 },
  ...extra,
})

const KNOWN = new Map(
  [
    asset('BTC/USDT', 'crypto'),
    asset('ETH/USDT', 'crypto'),
    asset('WAVES/USDT', 'crypto', 'suspended'),
    asset('AGLD/USDT', 'crypto', 'removed', { state_reason: 'Saiu da lista spot da Binance em 12 set. 2026.' }),
    asset('NVDA', 'stock'),
    asset('AVB', 'stock', 'off_market', { state_reason: 'A Binance marcou a ação como fora de mercado.' }),
    asset('SPY', 'etf'),
    asset('QQQ', 'etf'),
  ].map((a) => [a.symbol, a]),
)

const ok = { status: 'ok', updated_at: '2026-10-20T09:00:00Z', last_attempt_at: '2026-10-20T09:00:00Z', reason: null, code: null, refreshing: false }
const FRESH_OK = { crypto: ok, stock: ok, etf: ok }

const entries = (symbols, fresh = FRESH_OK) => resolveSelection(symbols, KNOWN, fresh)

test('exemplos de verificação: BTC/USDT roda; NVDA, SPY e QQQ ficam na seleção mas fora da análise', () => {
  const sel = entries(['BTC/USDT', 'NVDA', 'SPY', 'QQQ'])
  assert.deepEqual(sel.map((e) => e.kind), ['runs', 'class', 'class', 'class'])
  const counts = selectionCounts(sel)
  assert.deepEqual(
    { crypto: counts.crypto, stock: counts.stock, etf: counts.etf, out: counts.out, total: counts.total },
    { crypto: 1, stock: 1, etf: 2, out: 3, total: 4 },
  )
  assert.equal(selectionCountText(counts), '4 selecionados · 1 cripto · 1 ação · 2 ETFs')
})

test('ativo marcado nunca roda: aparece como "fica de fora", antes do +N, com o estado', () => {
  const sel = entries(['BTC/USDT', 'ETH/USDT', 'WAVES/USDT', 'AGLD/USDT', 'AVB'])
  assert.deepEqual(sel.map((e) => e.kind), ['runs', 'runs', 'marked', 'marked', 'marked'])
  const chips = sortedForChips(sel).map((e) => e.symbol)
  assert.deepEqual(chips.slice(0, 3), ['WAVES/USDT', 'AGLD/USDT', 'AVB'])
  const counts = selectionCounts(sel)
  assert.equal(counts.marked, 3)
  assert.equal(counts.crypto, 2)
  assert.equal(selectionCountText(counts), '5 selecionados · 2 cripto · 3 marcados ficam de fora')
  assert.equal(outLabel(sel[2]), 'WAVES/USDT (Cripto, Suspenso)')
  assert.equal(
    outReason(sel[2]),
    'Negociação pausada pela Binance (status BREAK); não entra em análise nova',
  )
  const note = markedNoteText(sel)
  assert.match(note.title, /Ativos marcados na seleção salva/)
  assert.match(note.body, /a Binance pausou ou retirou esses ativos/)
  assert.match(note.body, /Remova com ×/)
})

test('seleção antiga com um marcado reidrata como está e a nota fala no singular', () => {
  const sel = entries(['BTC/USDT', 'WAVES/USDT'])
  assert.match(markedNoteText(sel).title, /^Ativo marcado/)
  assert.match(markedNoteText(sel).body, /Ele aparece .* fica de fora/)
  assert.equal(outNames(sel), 'WAVES/USDT (Cripto, Suspenso)')
})

test('símbolo desconhecido: "fora do catálogo" só com lista válida; sem lista fica neutro', () => {
  assert.equal(entries(['XYZ/USDT'])[0].kind, 'missing')
  const cryptoDown = { ...FRESH_OK, crypto: { ...ok, status: 'unavailable' } }
  assert.equal(entries(['XYZ/USDT'], cryptoDown)[0].kind, 'runs')
  assert.equal(resolveSelection(['XYZ/USDT'], KNOWN, FRESH_OK, new Set())[0].kind, 'runs') // ainda não consultado
})

test('plano de rodar: nada, bloqueado, 1 ativo (caminho de 1 ativo) ou lote (mais de 1 ativo é sempre lote)', () => {
  assert.equal(planRun(entries([])).mode, 'none')
  // Card #1119: 1 ação/ETF sozinha roda (backtest de 1 ativo, sem lote).
  const oneEquity = planRun(entries(['NVDA']))
  assert.equal(oneEquity.mode, 'single')
  assert.deepEqual(oneEquity.runnable, ['NVDA'])
  assert.equal(oneEquity.equityRun.symbol, 'NVDA')
  // Card #1120: duas ações/ETFs são um lote; cripto com ação/ETF também.
  const twoEquities = planRun(entries(['NVDA', 'SPY']))
  assert.equal(twoEquities.mode, 'batch')
  assert.deepEqual(twoEquities.runnable, ['NVDA', 'SPY'])
  assert.equal(twoEquities.equityRun, null)
  const mixed = planRun(entries(['BTC/USDT', 'NVDA', 'SPY']))
  assert.equal(mixed.mode, 'batch')
  assert.deepEqual(mixed.runnable, ['BTC/USDT', 'NVDA', 'SPY'])
  assert.deepEqual(mixed.selected, ['BTC/USDT', 'NVDA', 'SPY'])
  assert.equal(planRun(entries(['WAVES/USDT'])).mode, 'blocked')
  // 1 par com um marcado: continua sendo lote (para o marcado aparecer como "Fora" com o motivo)
  const withMarked = planRun(entries(['BTC/USDT', 'WAVES/USDT']))
  assert.equal(withMarked.mode, 'batch')
  assert.deepEqual(withMarked.runnable, ['BTC/USDT'])
  assert.equal(withMarked.out.length, 1)
  assert.equal(planRun(entries(['BTC/USDT', 'ETH/USDT', 'QQQ'])).mode, 'batch')
})

test('plano por tempo: 1m e 5m tiram ação/ETF do lote e deixam a cripto', () => {
  for (const tf of ['1m', '5m']) {
    const plan = planRun(entries(['BTC/USDT', 'NVDA', 'SPY']), { timeframe: tf, page: 'combo' })
    assert.equal(plan.mode, 'batch')
    assert.deepEqual(plan.runnable, ['BTC/USDT'])
    assert.deepEqual(plan.out.map((a) => a.outKind), ['timeframe', 'timeframe'])
    assert.equal(plan.out[0].reason, `ação e ETF não rodam em ${tf}; para incluí-los, use 15m, 1h, 4h ou 1d`)
  }
  // Otimização: também 30m, com o conselho "1d aqui ou o Combo"
  const opt = planRun(entries(['BTC/USDT', 'NVDA']), { timeframe: '30m', page: 'optimize' })
  assert.equal(opt.out[0].reason, 'ação e ETF não rodam em 30m; para incluí-los, use 1d aqui ou o Combo, que tem período')
  // 15m, 1h, 4h e 1d servem a ação/ETF no Combo
  for (const tf of ['15m', '1h', '4h', '1d']) {
    assert.deepEqual(planRun(entries(['BTC/USDT', 'NVDA']), { timeframe: tf, page: 'combo' }).runnable, ['BTC/USDT', 'NVDA'])
  }
})

test('Otimização: 15m, 1h e 4h deixam ação/ETF fora quando o 5m dele não cobre o período fixo', () => {
  const five = { timeframe: '5m', from: '2026-05-19T08:00:00Z', to: '2026-10-23T20:00:00Z', gap_count: 0, gaps: [], updated_at: null, origin: 'native' }
  const known = new Map(KNOWN)
  known.set('NVDA', asset('NVDA', 'stock', 'tradable', { history: { status: 'covered', from: five.from, to: five.to, timeframes: [five], gap_count: 0 } }))
  const sel = (symbols) => resolveSelection(symbols, known, FRESH_OK)
  for (const tf of ['15m', '1h', '4h']) {
    const plan = planRun(sel(['BTC/USDT', 'NVDA', 'SPY']), { timeframe: tf, page: 'optimize' })
    assert.deepEqual(plan.runnable, ['BTC/USDT'])
    const nvda = plan.out.find((a) => a.entry.symbol === 'NVDA')
    assert.equal(nvda.outKind, 'coverage')
    assert.equal(
      nvda.reason,
      'o 5m de NVDA começa em 19 mai. 2026 e não cobre 1 a 31 jan. 2024, o período fixo desta tela; use 1d aqui ou o Combo, que tem período',
    )
    // SPY sob demanda: o começo do 5m da classe vem do ativo que já tem série guardada
    assert.equal(plan.out.find((a) => a.entry.symbol === 'SPY').outKind, 'coverage')
    // o mesmo tempo no Combo (com período) não tira ninguém
    assert.deepEqual(planRun(sel(['BTC/USDT', 'NVDA', 'SPY']), { timeframe: tf, page: 'combo' }).runnable, ['BTC/USDT', 'NVDA', 'SPY'])
  }
  assert.deepEqual(planRun(sel(['BTC/USDT', 'NVDA', 'SPY']), { timeframe: '1d', page: 'optimize' }).runnable, ['BTC/USDT', 'NVDA', 'SPY'])
})

test('tempos "(só cripto)": escolhíveis na seleção mista, indisponíveis só com ação/ETF', () => {
  const mixed = planRun(entries(['BTC/USDT', 'NVDA']), { timeframe: '1d', page: 'combo' })
  assert.deepEqual(cryptoOnlyTimeframes(mixed), ['1m', '5m'])
  assert.equal(timeframeDisabled(mixed, '5m'), false)
  const onlyEquity = planRun(entries(['NVDA']), { timeframe: '1d', page: 'combo' })
  assert.equal(timeframeDisabled(onlyEquity, '5m'), true)
  assert.equal(timeframeDisabled(onlyEquity, '1d'), false)
  const opt = planRun(entries(['BTC/USDT', 'NVDA']), { timeframe: '1d', page: 'optimize' })
  assert.deepEqual(cryptoOnlyTimeframes(opt), ['1m', '5m', '30m'])
  assert.deepEqual(cryptoOnlyTimeframes(planRun(entries(['BTC/USDT', 'ETH/USDT']))), [])
})

test('Market Data por ativo e nota da classe', () => {
  assert.equal(marketDataText(planRun(entries(['BTC/USDT', 'NVDA', 'SPY']))), 'Por ativo: CCXT (cripto) · Binance Ações (ação e ETF)')
  assert.equal(marketDataText(planRun(entries(['BTC/USDT', 'ETH/USDT']))), 'CCXT (crypto exchange data)')
  assert.equal(marketDataText(planRun(entries(['NVDA']))), 'Binance Ações · pregão regular de Nova York · ajustado por split')
  assert.match(CLASS_NOTE.combo, /^Cripto, ação e ETF rodam juntos no lote: cada ativo usa a sua fonte, sessão, ajuste e moeda/)
  assert.match(CLASS_NOTE.combo, /1 ação ou ETF sozinha abre o resultado, sem salvar\.$/)
  assert.match(CLASS_NOTE.optimize, /no período fixo desta tela/)
  assert.match(CLASS_NOTE.optimize, /nem em 15m, 1h e 4h quando o 5m deles não cobre o período fixo/)
  assert.doesNotMatch(`${CLASS_NOTE.combo} ${CLASS_NOTE.optimize}`, /o lote vem depois/)
})

test('Combo: cópia antes do clique diz o que roda e o que fica fora', () => {
  const combo = (symbols, timeframe = '1d') => runCopy(planRun(entries(symbols), { timeframe, page: 'combo' }), 'combo')
  assert.equal(combo(['BTC/USDT']).text, '1 ativo selecionado: otimiza, salva em favoritos e abre a página de favoritos.')
  const one = combo(['NVDA'])
  assert.equal(one.blocked, false)
  assert.equal(one.text, '1 ação (NVDA): otimiza e abre o resultado, sem salvar em favoritos: ações e ETFs ainda não podem ser favoritados.')
  assert.equal(combo(['SPY']).text.slice(0, 15), '1 ETF (SPY): ot')
  const lote = combo(['BTC/USDT', 'NVDA', 'SPY'])
  assert.equal(lote.blocked, false)
  assert.equal(
    lote.text,
    'Lote de 3 ativos (1 cripto, 1 ação, 1 ETF): otimiza cada um com esta configuração e grava o melhor de cada em favoritos (nota "gerado em lote"). Antes de começar, você confirma o lote.',
  )
  assert.equal(
    combo(['BTC/USDT', 'ETH/USDT', 'NVDA']).text.slice(0, 40),
    'Lote de 3 ativos (2 cripto, 1 ação): oti',
  )
  const fiveMin = combo(['BTC/USDT', 'NVDA', 'SPY'], '5m')
  assert.equal(
    fiveMin.text,
    'Lote de 3 ativos: roda 1 (BTC/USDT). Fora antes de começar: NVDA (Ação), SPY (ETF) — ação e ETF não rodam em 5m; para incluí-los, use 15m, 1h, 4h ou 1d.',
  )
  assert.equal(fiveMin.parts.lead, 'Lote de 3 ativos: roda 1')
  assert.match(fiveMin.parts.out, /^Fora antes de começar: NVDA \(Ação\), SPY \(ETF\) — /)
  const only = combo(['NVDA', 'SPY'], '5m')
  assert.equal(only.blocked, true)
  assert.equal(only.text, 'Nada será executado: NVDA (Ação), SPY (ETF) — ação e ETF não rodam em 5m; para incluí-los, use 15m, 1h, 4h ou 1d.')
  const withMarked = combo(['BTC/USDT', 'WAVES/USDT']).text
  assert.match(withMarked, /^Lote de 2 ativos: roda 1 \(BTC\/USDT\)\. Fora antes de começar: WAVES\/USDT \(Cripto, Suspenso\) — /)
  assert.match(withMarked, /não entra em análise nova\.$/)
  assert.doesNotMatch(only.text + lote.text + withMarked, /o lote vem depois/)
})

test('Otimização: cópia de 1 ativo, de lote e de nada roda', () => {
  const opt = (symbols, timeframe = '1d') => runCopy(planRun(entries(symbols), { timeframe, page: 'optimize' }), 'optimize')
  assert.equal(opt(['BTC/USDT']).text, '1 ativo: otimiza e mostra o resultado ao lado.')
  assert.equal(
    opt(['BTC/USDT', 'ETH/USDT', 'QQQ']).text,
    'Lote de 3 ativos (2 cripto, 1 ETF): otimiza cada um com esta configuração, no período fixo desta tela, e grava o melhor de cada em favoritos (nota "gerado em lote"). Antes de começar, você confirma o lote.',
  )
  assert.equal(
    opt(['BTC/USDT', 'NVDA', 'SPY'], '5m').text,
    'Lote de 3 ativos: roda 1 (BTC/USDT). Fora antes de começar: NVDA (Ação), SPY (ETF) — ação e ETF não rodam em 5m; para incluí-los, use 1d aqui ou o Combo, que tem período.',
  )
  const none = opt(['QQQ', 'SPY'], '30m')
  assert.equal(none.blocked, true)
  assert.equal(none.text, 'Nada será executado: QQQ (ETF), SPY (ETF) — ação e ETF não rodam em 30m; para incluí-los, use 1d aqui ou o Combo, que tem período.')
  assert.equal(
    opt(['NVDA'], '1d').text,
    '1 ação (NVDA): otimiza em 1d, de 1 a 31 jan. 2024, e mostra o resultado ao lado.',
  )
  assert.equal(runCopy(planRun(entries([])), 'optimize').text, 'Nenhum ativo selecionado: escolha ao menos 1 par cripto em USDT.')
})

test('1 ação/ETF num tempo que não serve: o valor fica e a tela avisa antes de rodar', () => {
  const plan = planRun(entries(['NVDA']), { timeframe: '5m', page: 'combo' })
  assert.equal(plan.mode, 'blocked')
  const block = equityTimeframeBlock(plan, '5m', 'combo')
  assert.equal(block.copy, 'Nada será executado: NVDA (Ação) não roda em 5m. Escolha 15m, 1h, 4h ou 1d.')
  assert.equal(block.notice.title, 'Escolha 15m, 1h, 4h ou 1d')
  assert.equal(runCopy(plan, 'combo').text, block.copy)
  assert.equal(equityTimeframeBlock(planRun(entries(['NVDA']), { timeframe: '1d' }), '1d', 'combo'), null)
  assert.equal(equityTimeframeBlock(planRun(entries(['BTC/USDT', 'NVDA']), { timeframe: '5m' }), '5m', 'combo'), null)
})

test('aviso ao rodar quando nada roda: só ação ou ETF, só marcado e os dois', () => {
  const eq = blockedNotice(planRun(entries(['NVDA', 'SPY']), { timeframe: '5m', page: 'combo' }), 'combo')
  assert.equal(eq.title, 'Ação e ETF não rodam em 5m')
  assert.equal(eq.body, 'NVDA (Ação), SPY (ETF): ação e ETF não rodam em 5m; para incluí-los, use 15m, 1h, 4h ou 1d. Nada foi executado. A seleção foi mantida.')
  const marked = blockedNotice(planRun(entries(['WAVES/USDT']), { page: 'optimize' }), 'optimize')
  assert.equal(marked.title, 'Ativo marcado pela Binance não entra em análise nova')
  assert.match(marked.body, /Nada foi executado\. A seleção foi mantida\.$/)
  const both = blockedNotice(planRun(entries(['WAVES/USDT', 'SPY', 'QQQ']), { timeframe: '5m', page: 'optimize' }), 'optimize')
  assert.equal(both.title, 'Nenhum ativo da seleção pode rodar agora')
  assert.ok(both.body.includes('ação e ETF não rodam em 5m; para incluí-los, use 1d aqui ou o Combo, que tem período; ativo marcado pela Binance'))
})

test('"Todos do filtro": confirmação mostra incluídos e marcados de fora, e os novos quando já há seleção', () => {
  const full = confirmCopy('etf', '', 3112, 16, null)
  assert.equal(full.prefix + full.count + full.middle, 'Incluir 3.112 ETFs negociáveis na seleção?')
  assert.equal(full.marked, '16')
  assert.match(full.markedText, /ativos marcados ficam de fora: suspensos, fora de mercado, sem negociação, sem regras ou removidos não podem ser escolhidos para análise nova\./)
  assert.equal(full.suffix, ' O que já está selecionado continua.')

  const search = confirmCopy('all', 'nvidia', 3, 0, 1)
  assert.equal(search.count, '3 (1 novo)')
  assert.match(search.middle, /ativos negociáveis que correspondem a “nvidia” \(todas as classes\) na seleção\?/)
  assert.equal(search.marked, null)
  assert.equal(confirmCopy('crypto', '', 1, 1, 1).middle, ' par cripto negociável na seleção?')
  assert.equal(confirmCopy('all', '', 5, 0, 2).count, '5 (2 novos)')
})

test('falha por classe: lista anterior com aviso e data; sem lista, um erro com Tentar de novo', () => {
  const stale = {
    ...FRESH_OK,
    stock: { ...ok, status: 'stale', updated_at: '2026-10-19T21:00:00Z', last_attempt_at: '2026-10-20T09:00:00Z', reason: 'timeout' },
    etf: { ...ok, status: 'stale', updated_at: '2026-10-19T21:00:00Z' },
  }
  const [banner] = catalogBanners(stale)
  assert.equal(banner.kind, 'stale')
  assert.equal(banner.title, 'Ações e ETFs desatualizados')
  assert.match(banner.body, /A Binance não respondeu na atualização de 20 out\. 2026, 06:00\. Mostrando a lista válida de 19 out\. 2026, 18:00; pesquisa e escolha continuam\./)
  assert.equal(banner.retry, false)
  assert.equal(freshnessLine(stale), 'Cripto atualizado 20 out. 2026, 06:00 · Ações e ETFs de 19 out. 2026, 18:00')

  const down = { ...FRESH_OK, crypto: { ...ok, status: 'unavailable', updated_at: null } }
  const banners = catalogBanners(down)
  assert.equal(banners.length, 1)
  assert.equal(banners[0].kind, 'down')
  assert.equal(banners[0].title, 'Cripto indisponível')
  assert.equal(banners[0].retry, true)
  assert.match(banners[0].body, /não há lista salva de cripto\. Ações e ETFs continuam disponíveis/)
  assert.equal(freshnessLine(down), 'Cripto sem lista · Ações e ETFs atualizados 20 out. 2026, 06:00')

  const both = { ...down, stock: { ...ok, status: 'unavailable' }, etf: { ...ok, status: 'unavailable' } }
  assert.equal(catalogBanners(both).filter((b) => b.kind === 'down').length, 1)
  assert.deepEqual(catalogBanners(FRESH_OK), [])
  assert.equal(freshnessLine(FRESH_OK), 'Catálogo Binance · atualizado 20 out. 2026, 06:00')
})

test('pesquisa vazia durante a falha culpa a Binance, não o símbolo', () => {
  const down = { ...FRESH_OK, crypto: { ...ok, status: 'unavailable' } }
  const msg = emptySearchMessage('btc', 'all', down)
  assert.match(msg, /^Nenhuma ação ou ETF para “btc”\. Cripto está indisponível agora por falha da Binance/)
  assert.doesNotMatch(msg, /Confira o símbolo/)
  assert.match(emptySearchMessage('', 'crypto', down), /^Lista de cripto indisponível por falha da Binance\./)
  assert.match(emptySearchMessage('zzzz', 'all', FRESH_OK), /^Nenhum ativo para “zzzz” em todas as classes\. Confira o símbolo ou troque a classe\./)
  assert.match(emptySearchMessage('zzzz', 'etf', FRESH_OK), /em ETFs\./)
})

test('linhas do seletor: classe, negociação e histórico separados, e motivo do marcado', () => {
  const frame = (timeframe, from, to) => ({ timeframe, from, to, gap_count: 0, gaps: [], updated_at: '2026-10-22T21:00:00Z', origin: 'native' })
  const covered = (frames, extra = {}) => ({ status: 'covered', from: frames[0].from, to: frames[0].to, updated_at: '2026-10-22T21:00:00Z', gap_count: 0, timeframes: frames, ...extra })
  assert.match(
    historyText(asset('BTC/USDT', 'crypto', 'tradable', { history: covered(['1d', '4h', '1h', '15m'].map((tf) => frame(tf, '2017-08-17T00:00:00Z', '2026-10-22T18:00:00Z'))) })),
    /^Histórico desde 17 ago\. 2017 · 4 timeframes · sem lacunas · atualizado 22 out\.(?: 2026)?, \d{2}:\d{2}$/,
  )
  assert.equal(historyText(asset('ETH/USDT', 'crypto')), 'Histórico sob demanda · coletado quando uma análise pedir')
  assert.equal(historyText(asset('NVDA', 'stock')), 'Histórico sob demanda · a coleta começa quando as análises aceitarem ações')
  // Combo e Otimização (card #1119): a coleta acontece ao rodar o backtest de 1 ativo; a Descoberta mantém o texto acima.
  assert.equal(historySummary(asset('NVDA', 'stock'), new Date(), ON_DEMAND_TEXT_BACKTEST).text, 'Histórico sob demanda · coletado ao rodar o backtest ou o lote')
  // Card #1120 (decisão 6): vale para toda linha sob demanda, inclusive a cripto
  assert.equal(historySummary(asset('ETH/USDT', 'crypto'), new Date(), ON_DEMAND_TEXT_BACKTEST).text, 'Histórico sob demanda · coletado ao rodar o backtest ou o lote')
  assert.equal(historyText(asset('SPY', 'etf')), 'Histórico sob demanda · a coleta começa quando as análises aceitarem ETFs')
  for (const symbol of ['ETH/USDT', 'NVDA', 'SPY']) assert.doesNotMatch(historyText(asset(symbol, symbol.includes('/') ? 'crypto' : 'stock')), /não coletado/)
  assert.equal(
    historyText(asset('WAVES/USDT', 'crypto', 'suspended', { history: covered([frame('1d', '2018-01-01T00:00:00Z', '2024-05-31T00:00:00Z')], { status: 'frozen', from: '2018-01-01T00:00:00Z', to: '2024-05-31T00:00:00Z' }) })),
    'Histórico 01 jan. 2018 – 31 mai. 2024 · sem atualização: ativo suspenso',
  )
  assert.equal(historyText(asset('X/USDT', 'crypto', 'removed', { history: { status: 'none', from: null, to: null } })), 'Sem histórico local')
  const reason = markedReasonText(KNOWN.get('WAVES/USDT'), true)
  assert.match(reason, /Negociação pausada pela Binance \(status BREAK\)\. Não pode ser escolhido para análise nova; aparece para explicar resultados e favoritos antigos\. Está na seleção salva e fica de fora ao rodar\.$/)
  assert.doesNotMatch(markedReasonText(KNOWN.get('WAVES/USDT'), false), /Está na seleção salva/)
})

test('datas em pt-BR no fuso de São Paulo', () => {
  assert.equal(formatDate('2017-08-17T12:00:00Z'), '17 ago. 2017')
  assert.equal(formatDateTime('2026-10-20T09:00:00Z'), '20 out. 2026, 06:00')
  assert.equal(formatDate(null), '')
  assert.equal(formatDateTime('lixo'), '')
})

test('mergeSymbols soma sem repetir e preserva a ordem', () => {
  assert.deepEqual(mergeSymbols(['BTC/USDT'], ['eth/usdt', 'BTC/USDT', ' nvda ', '']), ['BTC/USDT', 'ETH/USDT', 'NVDA'])
})

test('Preflight da Descoberta: bloco "Fora desta varredura" com os 3 primeiros e o resto', () => {
  const assets = [
    { symbol: 'NVDA', asset_class: 'stock', state: 'tradable', kind: 'class', reason: 'análise ainda não disponível para ações e ETFs', combinations: 2 },
    { symbol: 'SPY', asset_class: 'etf', state: 'tradable', kind: 'class', reason: 'análise ainda não disponível para ações e ETFs', combinations: 2 },
    { symbol: 'QQQ', asset_class: 'etf', state: 'tradable', kind: 'class', reason: 'análise ainda não disponível para ações e ETFs', combinations: 2 },
    { symbol: 'VOO', asset_class: 'etf', state: 'tradable', kind: 'class', reason: 'análise ainda não disponível para ações e ETFs', combinations: 2 },
  ]
  assert.equal(outOfSweepTitle(assets), 'Fora desta varredura: 4 ativos (8 combinações)')
  assert.equal(outOfSweepTitle(assets.slice(0, 1)), 'Fora desta varredura: 1 ativo (2 combinações)')
  assert.equal(preflightExcludedLabel(assets[1]), 'SPY (ETF)')
  assert.equal(preflightRestLine(assets, 3), 'e mais 1 ações e ETFs, pelo mesmo motivo.')
  assert.equal(preflightRestLine(assets.slice(0, 3), 3), null)
  const marked = { symbol: 'WAVES/USDT', asset_class: 'crypto', state: 'suspended', kind: 'marked', reason: 'x', combinations: 1 }
  assert.equal(preflightExcludedLabel(marked), 'WAVES/USDT (Cripto, Suspenso)')
  assert.equal(preflightRestLine([...assets.slice(0, 3), marked], 3), 'e mais 1 ativos, pelos mesmos motivos.')
})

test('recusa estruturada da API vira a mensagem em português; texto antigo segue como estava', () => {
  assert.equal(refusalMessage({ code: 'asset_class_not_supported', message: 'Análise ainda não disponível para ações e ETFs.' }, 'x'), 'Análise ainda não disponível para ações e ETFs.')
  assert.equal(refusalMessage('Batch queue is unavailable', 'x'), 'Batch queue is unavailable')
  assert.equal(refusalMessage(undefined, 'Falha na otimização'), 'Falha na otimização')
  assert.equal(urlSymbolNotice('XYZ/USDT').title, 'XYZ/USDT não está no catálogo da Binance')
})

test('o texto de por que fica fora muda com a mistura', () => {
  assert.equal(outWhy(selectionCounts(entries(['NVDA']))), 'ação e ETF por enquanto rodam no Combo e na Otimização (1 ativo ou lote); a Descoberta vem depois')
  assert.match(outWhy(selectionCounts(entries(['WAVES/USDT']))), /^ativo marcado pela Binance \(suspenso, fora de mercado/)
  assert.ok(outWhy(selectionCounts(entries(['WAVES/USDT', 'NVDA']))).startsWith('ação e ETF por enquanto rodam no Combo e na Otimização (1 ativo ou lote); a Descoberta vem depois, e ativos marcados'))
  assert.equal(outEntries(entries(['BTC/USDT', 'NVDA'])).length, 1)
})

// --- Contrato das telas (texto-fonte): sem texto livre, sem "Edição avançada" de símbolos ------------

test('Descoberta: eixo Ativos com o seletor, sem Edição avançada de símbolos nem catálogo antigo', async () => {
  const source = await readFile(new URL('../src/pages/DiscoveryPage.tsx', import.meta.url), 'utf8')
  assert.match(source, /<AssetPicker/)
  assert.match(source, /title="Ativos"/)
  assert.doesNotMatch(source, /data-testid="edit-symbols"/)
  assert.doesNotMatch(source, /\/exchanges\/binance\/symbols/)
  assert.doesNotMatch(source, /inline-symbols-search/)
  assert.match(source, /data-testid="edit-templates"/)
  assert.match(source, /data-testid="preflight-class-out"/)
})

test('Combo: seletor no lugar do rádio Todos/Seleciona e da lista dupla, com Top 10 e Limpar (1 ativo)', async () => {
  const source = await readFile(new URL('../src/pages/ComboConfigurePage.tsx', import.meta.url), 'utf8')
  assert.match(source, /<AssetPicker/)
  assert.match(source, /clearLabel="Limpar \(1 ativo\)"/)
  assert.match(source, /data-testid="combo-top10"/)
  assert.doesNotMatch(source, /name="scope"/)
  assert.doesNotMatch(source, /Seleciona<\/span>/)
  assert.doesNotMatch(source, /\/exchanges\/binance\/symbols/)
})

test('Otimização: sem texto livre, com o seletor, authFetch e o lote do Combo', async () => {
  const source = await readFile(new URL('../src/pages/ComboOptimizePage.tsx', import.meta.url), 'utf8')
  assert.match(source, /<AssetPicker/)
  assert.doesNotMatch(source, /type="text"/)
  assert.match(source, /batch\.requestPreview\(/)
  assert.match(source, /<BatchPanel/)
  assert.match(source, /authFetch\(`\$\{API_BASE_URL\}\/combos\/optimize`/)
  assert.doesNotMatch(source, /[^h]fetch\(`\$\{API_BASE_URL\}/)
  assert.match(source, /urlSymbolNotice/)
})
