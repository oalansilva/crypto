import test from 'node:test'
import assert from 'node:assert/strict'
import {
  chipCounts,
  classBreakdown,
  confirmView,
  dailyNote,
  favoritesHref,
  favoritesLinkText,
  filterItems,
  formatDuration,
  formatRemaining,
  groupOutReason,
  itemDetail,
  jobView,
  liveLine,
  metaLine,
  outNamesText,
  parseProgress,
  pausedBlockView,
  savedCount,
  savedSummary,
  visibleChips,
} from '../src/lib/batchLote.ts'
import {
  atrWithCurrency,
  classCounts,
  classFilterOptions,
  favoriteClass,
  favoriteLoteId,
  favoriteRowData,
  loteBannerText,
} from '../src/lib/favoriteClass.ts'
import * as favoriteClassModule from '../src/lib/favoriteClass.ts'

const JOB_ID = '7f3c2a91-0000-4000-8000-000000000001'

const item = (symbol, asset_class, state, extra = {}) => ({
  position: 0,
  symbol,
  asset_class,
  currency: asset_class === 'crypto' ? 'USDT' : 'USD',
  state,
  reason: null,
  progress: null,
  favorite_id: null,
  execution: null,
  snapshot_id: null,
  started_at: null,
  finished_at: null,
  ...extra,
})

const job = (status, items, extra = {}) => ({
  job_id: JOB_ID,
  status,
  processed: items.filter((i) => !['queued', 'collecting', 'optimizing', 'out'].includes(i.state)).length,
  total: items.filter((i) => i.state !== 'out').length,
  succeeded: 0,
  failed: 0,
  errors: [],
  started_at: null,
  elapsed_sec: 48,
  estimated_remaining_sec: 90,
  items,
  ...extra,
})

const intrabar = { precision_requested: 'intrabar', precision_effective: 'intrabar_15m', window: { covered: { start: '2017-08-17T00:00:00Z', end: '2026-10-24T00:00:00Z', candles: 3400 } } }
const daily = {
  precision_requested: 'intrabar',
  precision_effective: 'candle',
  intraday_reason: 'coverage',
  intraday_missing: [{ from: '2014-11-11', to: '2026-05-18' }],
  window: { covered: { start: '2014-11-11T05:00:00Z', end: '2026-10-23T04:00:00Z', candles: 3000 } },
}

// --- painel do lote -------------------------------------------------------------------------------------

test('selo do lote: Rodando, Pausando, Encerrando, Pausado, Encerrado e Concluído', () => {
  const items = [item('BTC/USDT', 'crypto', 'optimizing')]
  assert.equal(jobView(job('running', items)), 'running')
  assert.equal(jobView(job('queued', items)), 'running')
  assert.equal(jobView(job('running', items, { pause_requested: true })), 'pausing')
  assert.equal(jobView(job('running', items, { cancel_requested: true })), 'cancelling')
  assert.equal(jobView(job('paused', items)), 'paused')
  assert.equal(jobView(job('cancelled', items)), 'cancelled')
  assert.equal(jobView(job('completed', items)), 'completed')
})

test('linha viva: só o ativo e a etapa em curso, nunca a lista inteira', () => {
  const items = [item('BTC/USDT', 'crypto', 'success'), item('NVDA', 'stock', 'optimizing'), item('SPY', 'etf', 'queued')]
  assert.equal(liveLine(job('running', items)), 'NVDA: otimizando.')
  assert.equal(liveLine(job('running', [item('SPY', 'etf', 'collecting')])), 'SPY: coletando histórico.')
  assert.equal(
    liveLine(job('running', items, { pause_requested: true })),
    'Pausa pedida: o lote para quando NVDA terminar a etapa em curso (otimização).',
  )
  assert.equal(
    liveLine(job('running', [item('SPY', 'etf', 'collecting')], { pause_requested: true })),
    'Pausa pedida: o lote para quando SPY terminar a etapa em curso (coleta).',
  )
  assert.match(liveLine(job('running', items, { cancel_requested: true })), /^Encerramento pedido: o lote para quando NVDA/)
  const paused = liveLine(job('paused', [item('BTC/USDT', 'crypto', 'success'), item('NVDA', 'stock', 'queued'), item('SPY', 'etf', 'queued')]))
  assert.equal(
    paused,
    'Pausado em 1 de 3. Os concluídos ficam; NVDA, SPY esperam. Retomar continua no mesmo lote; um lote novo só depois de retomar ou encerrar este.',
  )
  assert.match(liveLine(job('paused', [item('NVDA', 'stock', 'queued')])), /NVDA espera\./)
})

test('resumo final: concluídos, favoritos, precisão diária e sem resultado válido', () => {
  const items = [
    item('BTC/USDT', 'crypto', 'success', { execution: intrabar }),
    item('NVDA', 'stock', 'success_daily', { execution: daily }),
    item('SPY', 'etf', 'success_daily', { execution: daily }),
    item('AAPL', 'stock', 'insufficient'),
    item('QQQ', 'etf', 'rejected'),
    item('IBIT', 'etf', 'failed'),
    item('SOL/USDT', 'crypto', 'out', { reason: 'suspenso' }),
  ]
  const done = job('completed', items, { elapsed_sec: 312 })
  assert.equal(done.total, 6)
  assert.equal(
    liveLine(done),
    'Lote concluído: 6 de 6 em 5m 12s · 3 favorito(s) gravado(s) (2 com precisão diária) · sem resultado válido: 3.',
  )
  assert.equal(savedCount(done), 3)
  assert.equal(favoritesLinkText(3), 'Ver os 3 resultados do lote em Favoritos')
  assert.equal(favoritesLinkText(1), 'Ver o resultado do lote em Favoritos')
  assert.equal(favoritesHref(done), '/favorites?lote=7f3c2a91')
  assert.equal(dailyNote(2).title, 'Precisão diária em 2 ativos:')
  assert.equal(dailyNote(1).title, 'Precisão diária em 1 ativo:')
  assert.equal(dailyNote(0), null)
  const cancelled = job('cancelled', [item('BTC/USDT', 'crypto', 'success'), item('NVDA', 'stock', 'not_run'), item('SPY', 'etf', 'not_run')])
  assert.equal(
    liveLine(cancelled),
    'Encerrado pelo usuário em 3 de 3. 1 favorito(s) gravado(s) ficam; não rodaram: NVDA, SPY.',
  )
})

test('"N de M ativos" não conta os que ficam fora; tempo restante só enquanto roda', () => {
  const items = [item('BTC/USDT', 'crypto', 'success'), item('NVDA', 'stock', 'out'), item('SPY', 'etf', 'out')]
  const running = job('running', [...items, item('AAPL', 'stock', 'optimizing')])
  assert.equal(metaLine(running), '1 de 2 ativos · 0m 48s · resta ~1m 30s')
  assert.equal(metaLine(job('completed', items)), '1 de 1 ativos · 0m 48s')
  assert.equal(formatDuration(312), '5m 12s')
  assert.equal(formatRemaining(34800), '9h 40m')
})

test('filtro por estado: só os estados presentes, com contagem; Em curso junta coletando e otimizando', () => {
  const items = [
    item('A', 'stock', 'success'),
    item('B', 'stock', 'success_daily'),
    item('C', 'stock', 'collecting'),
    item('D', 'stock', 'optimizing'),
    item('E', 'stock', 'out'),
    item('F', 'stock', 'queued'),
  ]
  const counts = chipCounts(items)
  assert.deepEqual(visibleChips(counts).map(([key]) => key), ['all', 'success', 'daily', 'out', 'running', 'queued'])
  assert.equal(counts.running, 2)
  assert.deepEqual(filterItems(items, 'running').map((i) => i.symbol), ['C', 'D'])
  assert.equal(filterItems(items, 'all').length, 6)
})

test('detalhe de cada ativo: coleta com progresso, gravado com janela e precisão, fora com o motivo', () => {
  const j = job('running', [])
  assert.deepEqual(parseProgress('5m do intrabar · página 7 de 20'), { value: 7, max: 20 })
  assert.equal(parseProgress('página 7'), null)
  const collecting = itemDetail(item('SPY', 'etf', 'collecting', { progress: '5m do intrabar · página 7 de 20' }), j)
  assert.deepEqual(collecting, { kind: 'progress', text: '5m do intrabar · página 7 de 20', progress: { value: 7, max: 20 } })
  assert.deepEqual(
    itemDetail(item('SPY', 'etf', 'queued', { needs_collection: [{ series: '1d', role: 'candles', kind: 'missing' }, { series: '5m', role: 'intraday', kind: 'missing' }] }), j),
    { kind: 'text', text: 'precisa de coleta: 1d e 5m do intrabar.' },
  )
  assert.equal(itemDetail(item('BTC/USDT', 'crypto', 'queued', { needs_collection: [] }), j).text, 'histórico já guardado, sem lacunas e atualizado: nada a coletar.')
  assert.equal(itemDetail(item('NVDA', 'stock', 'queued', { progress: 'histórico coletado; otimiza ao retomar, na mesma amostra.' }), j).text, 'histórico coletado; otimiza ao retomar, na mesma amostra.')
  const saved = itemDetail(item('BTC/USDT', 'crypto', 'success', { execution: intrabar }), j)
  assert.equal(saved.kind, 'saved')
  assert.equal(saved.summary, '17 ago. 2017 – 24 out. 2026 · intrabar 15m')
  assert.equal(saved.href, '/favorites?lote=7f3c2a91')
  assert.equal(
    savedSummary(item('NVDA', 'stock', 'success_daily', { execution: daily })),
    '11 nov. 2014 – 23 out. 2026 · precisão diária: sem 15m de 11 nov. 2014 a 18 mai. 2026',
  )
  const out = itemDetail(item('NVDA', 'stock', 'out', { reason: 'ação e ETF não rodam em 5m; para incluí-los, use 15m, 1h, 4h ou 1d' }), j)
  assert.equal(out.text, 'Ação e ETF não rodam em 5m; para incluí-los, use 15m, 1h, 4h ou 1d. Ficou fora antes de começar.')
  assert.equal(itemDetail(item('X', 'stock', 'not_run'), j).text, 'Não rodou: o lote foi encerrado antes deste ativo.')
  assert.equal(itemDetail(item('AAPL', 'stock', 'insufficient', { reason: 'Dados insuficientes.' }), j).text, 'Dados insuficientes.')
})

test('tela de 1 ativo: aviso de combinações puladas só quando houve, com o texto do servidor ou montado', async () => {
  const { combinationErrorsText } = await import('../src/lib/equityExecution.ts')
  assert.equal(combinationErrorsText(null), null)
  assert.equal(combinationErrorsText({ failed: 0 }), null)
  assert.equal(combinationErrorsText({ failed: 3, message: '3 combinações com erro: x (x3)' }), '3 combinações com erro: x (x3)')
  assert.equal(
    combinationErrorsText({ failed: 2, reasons: [{ reason: 'a', count: 1 }, { reason: 'b', count: 1 }] }),
    '2 combinações com erro: a (x1); b (x1)',
  )
})

test('ativo gravado com combinações puladas mostra "N combinações com erro: <motivo>" ao lado da janela', () => {
  const j = job('running', [])
  const note = '12 combinações com erro: a regra usa coluna que a combinação não tem (RSI_14) (x12)'
  const saved = itemDetail(item('BTC/USDT', 'crypto', 'success', { execution: intrabar, reason: note }), j)
  assert.equal(saved.kind, 'saved')
  assert.equal(saved.summary, `17 ago. 2017 – 24 out. 2026 · intrabar 15m · ${note}`)
  const clean = itemDetail(item('BTC/USDT', 'crypto', 'success', { execution: intrabar }), j)
  assert.equal(clean.summary, '17 ago. 2017 – 24 out. 2026 · intrabar 15m')
})

// --- Confirmar lote ------------------------------------------------------------------------------------------

const prev = (symbol, cls, plan, extra = {}) => ({
  symbol,
  asset_class: cls,
  currency: cls === 'crypto' ? 'USDT' : 'USD',
  plan,
  reason: null,
  needs_collection: [],
  collect_kind: 'none',
  ...extra,
})
const totals = (items) => {
  const run = items.filter((i) => i.plan === 'run')
  const needing = run.filter((i) => i.collect_kind !== 'none')
  return {
    total: items.length,
    run: run.length,
    out: items.length - run.length,
    by_class: {},
    collect: {
      count: needing.length,
      of: run.length,
      missing: needing.filter((i) => i.collect_kind === 'missing').length,
      tail: needing.filter((i) => i.collect_kind === 'tail').length,
    },
  }
}

test('Confirmar lote: 1 de 3 precisa de coleta, e diz quem já está guardado', () => {
  const items = [
    prev('BTC/USDT', 'crypto', 'run'),
    prev('NVDA', 'stock', 'run'),
    prev('SPY', 'etf', 'run', {
      collect_kind: 'missing',
      needs_collection: [{ series: '1d', role: 'candles', kind: 'missing' }, { series: '5m', role: 'intraday', kind: 'missing' }],
    }),
  ]
  const view = confirmView({ items, totals: totals(items), config: {} })
  assert.equal(view.title, 'Confirmar lote de 3 ativos')
  assert.deepEqual(view.run, { count: 3, classes: '1 cripto (USDT), 1 ação (USD), 1 ETF (USD)', names: 'BTC/USDT, NVDA, SPY' })
  assert.equal(view.collect.headline, '1 de 3')
  assert.equal(
    view.collect.detail,
    '— SPY (1d e 5m do intrabar). BTC/USDT e NVDA já estão guardados, sem lacunas e atualizados. Conta só o que a Binance tem para a janela e ainda não está guardado. A coleta acontece dentro do lote, ativo por ativo, com progresso, e pode ser pausada ou encerrada.',
  )
  assert.equal(view.out, null)
})

test('Confirmar lote: a Binance sem candles na janela não conta e o conselho vem do servidor', () => {
  const items = [
    prev('BTC/USDT', 'crypto', 'run'),
    prev('SPY', 'etf', 'run', {
      collect_kind: 'missing',
      collect_note: 'O 5m de SPY não entra: a Binance não tem 5m dele em jan. 2024.',
      needs_collection: [{ series: '1d', role: 'candles', kind: 'missing' }],
    }),
  ]
  const view = confirmView({ items, totals: totals(items), config: {} })
  assert.match(view.collect.detail, /^— SPY \(1d\)\. BTC\/USDT já está guardado, sem lacunas e atualizado\. O 5m de SPY não entra: a Binance não tem 5m dele em jan\. 2024\./)
  const none = confirmView({ items: [prev('BTC/USDT', 'crypto', 'run')], totals: totals([prev('BTC/USDT', 'crypto', 'run')]), config: {} })
  assert.equal(none.collect.headline, '0 de 1')
  assert.match(none.collect.detail, /^— BTC\/USDT já está guardado, sem lacunas e atualizado\. Conta só o que a Binance/)
})

test('Confirmar lote grande: sem histórico guardado, só o trecho desde a última coleta e os que já estão', () => {
  const missing = Array.from({ length: 2351 }, (_, i) =>
    prev(`AA${i}`, 'stock', 'run', {
      collect_kind: 'missing',
      needs_collection: [{ series: '1d', role: 'candles', kind: 'missing' }, { series: '5m', role: 'intraday', kind: 'missing' }],
    }),
  )
  const tail = Array.from({ length: 37 }, (_, i) =>
    prev(`BB${i}`, 'stock', 'run', { collect_kind: 'tail', needs_collection: [{ series: '1d', role: 'candles', kind: 'tail' }] }),
  )
  const ready = Array.from({ length: 43 }, (_, i) => prev(`CC${i}`, 'stock', 'run'))
  const items = [...missing, ...tail, ...ready]
  const view = confirmView({ items, totals: totals(items), config: {} })
  assert.equal(view.title, 'Confirmar lote de 2.431 ativos')
  assert.equal(view.run.count, 2431)
  assert.equal(view.run.classes, '2.431 ações (USD)')
  assert.equal(view.run.names, 'AA0, AA1, AA2 e mais 2.428')
  assert.equal(view.collect.headline, '2.388 de 2.431')
  assert.match(view.collect.detail, /^— 2\.351 sem histórico guardado \(1d e 5m do intrabar\) e 37 só com o trecho desde a última coleta\. Os outros 43 já estão guardados, sem lacunas e atualizados\./)
})

test('Confirmar lote: quem fica fora e por quê, com os motivos distintos', () => {
  const tfReason = 'ação e ETF não rodam em 5m; para incluí-los, use 15m, 1h, 4h ou 1d'
  const items = [
    prev('BTC/USDT', 'crypto', 'run'),
    prev('NVDA', 'stock', 'out', { reason: tfReason, out_kind: 'timeframe' }),
    prev('SPY', 'etf', 'out', { reason: tfReason, out_kind: 'timeframe' }),
  ]
  const view = confirmView({ items, totals: totals(items), config: {} })
  assert.deepEqual(view.out.map((o) => o.label), ['NVDA (Ação)', 'SPY (ETF)'])
  assert.equal(`${outNamesText(view.out)} — ${view.outReason}.`, `NVDA (Ação), SPY (ETF) — ${tfReason}.`)
  const coverage = [
    prev('NVDA', 'stock', 'out', { out_kind: 'coverage', reason: 'o 5m de NVDA começa em 19 mai. 2026 e não cobre 1 a 31 jan. 2024, o período fixo desta tela; use 1d aqui ou o Combo, que tem período' }),
    prev('SPY', 'etf', 'out', { out_kind: 'coverage', reason: 'o 5m de SPY começa em 19 mai. 2026 e não cobre 1 a 31 jan. 2024, o período fixo desta tela; use 1d aqui ou o Combo, que tem período' }),
  ]
  assert.equal(
    groupOutReason(coverage),
    'o 5m deles começa em 19 mai. 2026 e não cobre 1 a 31 jan. 2024, o período fixo desta tela; use 1d aqui ou o Combo, que tem período',
  )
  const marked = prev('WAVES/USDT', 'crypto', 'out', { out_kind: 'marked', reason: 'Negociação pausada pela Binance; não entra em análise nova' })
  assert.equal(groupOutReason([coverage[0], marked]).split('; ').length > 2, true)
  assert.equal(classBreakdown([prev('A', 'stock', 'run'), prev('B', 'stock', 'run')]), '2 ações (USD)')
})

test('lote pausado bloqueia um lote novo: o aviso diz o id e quantos favoritos ficam', () => {
  const view = pausedBlockView({ job_id: JOB_ID }, 2)
  assert.equal(view.title, 'Há um lote pausado')
  assert.equal(view.body, 'Retome ou encerre o lote 7f3c2a91 antes de começar outro. Encerrar mantém os 2 favoritos já gravados e marca o resto "Não rodou".')
  assert.equal(view.resume, 'Retomar o lote 7f3c2a91')
  assert.equal(view.cancel, 'Encerrar o lote 7f3c2a91')
  assert.match(pausedBlockView({ job_id: JOB_ID }, 1).body, /Encerrar mantém o favorito já gravado e marca/)
  assert.match(pausedBlockView({ job_id: JOB_ID }, 0).body, /^Retome ou encerre o lote 7f3c2a91 antes de começar outro\. Encerrar marca o resto "Não rodou"\.$/)
})

// --- Favoritos: lista única ------------------------------------------------------------------------------------

const fav = (symbol, extra = {}) => ({
  symbol,
  timeframe: '1d',
  created_at: '2026-10-24T21:40:00Z',
  notes: null,
  metrics: {},
  ...extra,
})

test('classe e moeda por linha: da API, de metrics.asset ou do formato do símbolo', () => {
  assert.equal(favoriteClass(fav('BTC/USDT')), 'crypto')
  assert.equal(favoriteClass(fav('NVDA')), 'stock')
  assert.equal(favoriteClass(fav('SPY', { asset: { symbol: 'SPY', asset_class: 'etf', currency: 'USD' } })), 'etf')
  assert.equal(favoriteClass(fav('SPY', { metrics: { asset: { asset_class: 'etf' } } })), 'etf')
  const counts = classCounts([fav('BTC/USDT'), fav('ETH/USDT'), fav('NVDA'), fav('SPY', { asset: { asset_class: 'etf' } })])
  assert.deepEqual(counts, { all: 4, crypto: 2, stock: 1, etf: 1 })
  assert.deepEqual(
    classFilterOptions(counts).map((o) => o.label),
    ['Todas (4)', 'Cripto (2)', 'Ações (1)', 'ETFs (1)'],
  )
})

test('linha de NVDA: precisão diária com o trecho, convenções, período efetivo e "Limitações e origem"', () => {
  const row = favoriteRowData(
    fav('NVDA', {
      notes: 'gerado em lote (7f3c2a91)',
      metrics: {
        batch_id: '7f3c2a91-0000-4000-8000-000000000001',
        execution: daily,
        conventions: { fee: 0.001, fee_confirmed: false, fraction: { simulated: true }, adjusted_prices: true, calendar: { sessions_per_year: 252 } },
        asset: { symbol: 'NVDA', asset_class: 'stock', currency: 'USD' },
      },
    }),
  )
  assert.equal(row.cls, 'stock')
  assert.equal(row.currency, 'USD')
  assert.deepEqual(row.precision, { tone: 'warn', text: 'Precisão diária · sem 15m de 11 nov. 2014 a 18 mai. 2026' })
  assert.equal(row.conventions, 'Binance Ações · NY · split · 252/ano')
  assert.equal(row.effective, 'Período efetivo 11 nov. 2014 – 23 out. 2026')
  assert.equal(row.effectiveRange, '11 nov. 2014 – 23 out. 2026')
  assert.equal(row.details.summary, 'Limitações e origem')
  assert.equal(row.details.conventionsFull, 'Convenções: Binance Ações · pregão regular de Nova York · ajustado por split · 252 pregões/ano')
  assert.equal(row.details.limitations, 'Limitações: simulação com fração · taxa assumida · preços ajustados podem diferir do negociado')
  assert.equal(row.details.lote, 'Gerado em lote 7f3c2a91 · 24 out. 2026')
  assert.equal(row.lote, '7f3c2a91')
  // taxa confirmada: a limitação "taxa assumida" some
  const confirmed = favoriteRowData(fav('SPY', { asset: { asset_class: 'etf' }, metrics: { execution: intrabar, conventions: { fee_confirmed: true } } }))
  assert.doesNotMatch(confirmed.details.limitations, /taxa assumida/)
  assert.deepEqual(confirmed.precision, { tone: 'info', text: 'Precisão intrabar (15m)' })
})

test('refresh diário atualizou analysis_execution: a linha mostra o valor novo, não o congelado', () => {
  const stale = { ...daily, precision_effective: 'daily' }
  const refreshed = favoriteRowData(
    fav('NVDA', { metrics: { execution: stale, analysis_execution: intrabar, conventions: { adjusted_prices: true }, analysis_conventions: { adjusted_prices: false } } }),
  )
  assert.deepEqual(refreshed.precision, { tone: 'info', text: 'Precisão intrabar (15m)' })
  assert.equal(refreshed.effective, 'Período efetivo 16 ago. 2017 – 23 out. 2026') // ação: fuso de Nova York
  assert.equal(refreshed.conventions, 'Binance Ações · NY · sem ajuste · 252/ano')
  // favorito antigo, só com a chave sem prefixo: segue lido
  const legacy = favoriteRowData(fav('NVDA', { metrics: { execution: intrabar } }))
  assert.deepEqual(legacy.precision, { tone: 'info', text: 'Precisão intrabar (15m)' })
  assert.equal(favoriteClass(fav('SPY', { metrics: { asset: { asset_class: 'stock' }, analysis_asset: { asset_class: 'etf' } } })), 'etf')
})

test('linha de cripto do lote só tem "Origem"; favorito antigo diz quando os dados aparecem', () => {
  const lote = favoriteRowData(
    fav('BTC/USDT', { metrics: { batch_id: '7f3c2a91-0000-4000-8000-000000000001', execution: intrabar } }),
  )
  assert.equal(lote.conventions, 'Binance Spot · 24/7 · 365 dias/ano')
  assert.deepEqual(lote.precision, { tone: 'info', text: 'Precisão intrabar (15m)' })
  assert.equal(lote.effective, 'Período efetivo 17 ago. 2017 – 24 out. 2026')
  assert.equal(lote.details.summary, 'Origem')
  assert.equal(lote.details.conventionsFull, null)
  const old = favoriteRowData(fav('ETH/USDT'))
  assert.deepEqual(old.precision, { tone: 'muted', text: 'Precisão e período efetivo: aparecem na próxima atualização diária' })
  assert.equal(old.effective, 'Período efetivo: na próxima atualização')
  assert.equal(old.effectiveRange, null)
  assert.equal(old.details, null)
  assert.equal(favoriteLoteId(fav('SOL/USDT', { notes: 'gerado em lote (ab12cd34)' })), 'ab12cd34')
  assert.equal(favoriteLoteId(fav('SOL/USDT')), null)
})

test('ATR na moeda, faixa do lote e nota das estrelas', () => {
  assert.equal(atrWithCurrency(4.871, 'USD'), '4.87 USD')
  assert.equal(atrWithCurrency(1834.2, 'USDT'), '1834.20 USDT')
  assert.equal(atrWithCurrency(undefined, 'USD'), '-')
  const favs = [
    fav('BTC/USDT', { created_at: '2026-10-24T21:41:00Z', metrics: { batch_id: '7f3c2a91-x' } }),
    fav('NVDA', { created_at: '2026-10-24T21:40:00Z', notes: 'gerado em lote (7f3c2a91)' }),
  ]
  assert.equal(
    loteBannerText('7f3c2a91', favs),
    'Mostrando só o lote 7f3c2a91 (24 out. 2026, 18:40): os favoritos gravados por ele, de todas as classes.',
  )
  // Card #1122: a nota "ainda não para ações e ETFs" saiu (ação e ETF entram nos níveis).
  assert.equal('tierNoteText' in favoriteClassModule, false)
})
