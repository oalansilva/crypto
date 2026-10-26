import test from 'node:test'
import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import {
  ON_DEMAND_TEXT_DISCOVERY,
  assetStateView,
  classEmptyText,
  classOptions,
  classesWithCurrency,
  collectionLine,
  limitText,
  liveAnnouncement,
  modalSampleText,
  multiclassMeta,
  noResultNote,
  orderAssets,
  precisionLine,
  promotionTitle,
  rowBlock,
  runLine,
  survivorshipDecidir,
  survivorshipWindowSuffix,
} from '../src/lib/discoveryMulticlass.ts'

const BY_CLASS = {
  crypto: { assets: 1, combinations: 1, currency: 'USDT' },
  stock: { assets: 1, combinations: 1, currency: 'USD' },
  etf: { assets: 1, combinations: 1, currency: 'USD' },
}

test('Preflight misto: "Vão rodar 3 ativos" com classe e moeda, USD e USDT separados', () => {
  assert.equal(classesWithCurrency(BY_CLASS), '1 cripto (USDT) · 1 ação · 1 ETF (USD)')
  const line = runLine(BY_CLASS, ['1d'], false)
  assert.equal(line.lead, 'Vão rodar 3 ativos:')
  assert.equal(line.rest, '1 cripto (USDT) · 1 ação · 1 ETF (USD). Cada um com a sua fonte, sessão, ajuste e moeda.')
  assert.equal(runLine(BY_CLASS, ['1d', '4h'], false).lead, 'Vão rodar 3 ativos em 1d e 4h:')
  assert.equal(ON_DEMAND_TEXT_DISCOVERY.stock, 'Histórico sob demanda · coletado ao rodar a varredura')
})

test('teto de 1.000 conta ação e ETF e pede para estreitar', () => {
  const big = { crypto: { assets: 1, combinations: 1, currency: 'USDT' }, stock: { assets: 2431, combinations: 2431 }, etf: { assets: 1, combinations: 1 } }
  assert.equal(
    limitText(2433, 1000, big, 1, 1, ['long']),
    '2.433 combinações válidas passam do limite de 1.000: 2.433 ativos (1 cripto · 2.431 ações · 1 ETF) × 1 template × 1 timeframe × Long.',
  )
  assert.equal(runLine(big, ['1d'], true).lead, '2.433 ativos selecionados:')
})

test('coleta e precisão previstas com o texto do protótipo', () => {
  const collect = collectionLine({
    count: 1,
    of: 3,
    assets: [{ symbol: 'SPY', series: ['1d', '5m do intrabar'] }],
    stored: ['BTC/USDT', 'NVDA'],
  })
  assert.equal(collect.lead, 'Precisam de coleta de histórico: 1 de 3')
  assert.equal(
    collect.rest,
    '— SPY (1d e 5m do intrabar). BTC/USDT e NVDA já estão guardados. A coleta acontece no começo do ativo e entra no tempo da varredura.',
  )
  const precision = precisionLine({
    daily: [{ symbol: 'NVDA', timeframe: '1d', from_label: '2 jan. 2003', to_label: '31 dez. 2025', five_from_label: '2 jan. 2026' }],
    no_candles: [],
    unknown: ['SPY'],
  })
  assert.equal(precision.lead, 'Precisão diária prevista em 1d:')
  assert.equal(
    precision.rest,
    'NVDA — o 15m dele começa em 2 jan. 2026, então 2 jan. 2003 a 31 dez. 2025 roda no candle diário. ' +
      'SPY: sem histórico guardado; a precisão aparece depois da coleta. O resultado sempre marca o trecho.',
  )
  const past = precisionLine({
    daily: [],
    no_candles: [
      { symbol: 'NVDA', timeframe: '4h', five_from_label: '2 jan. 2026' },
      { symbol: 'SPY', timeframe: '4h', five_from_label: '2 jan. 2026' },
    ],
    unknown: [],
  })
  assert.equal(past.lead, 'Sem candles prováveis em 4h: NVDA e SPY')
  assert.match(past.rest, /^— o 5m da Binance começa em 2 jan\. 2026, então essas 2 combinações devem terminar como amostra insuficiente/)
})

test('viés de sobrevivência em toda varredura, com a janela', () => {
  assert.equal(survivorshipWindowSuffix({ start_label: '2 jan. 2003' }), ', e a janela começa em 2 jan. 2003')
  assert.equal(survivorshipWindowSuffix({ start_label: '1 jan. 2019', end_label: '31 dez. 2020' }), ', e a janela é 1 jan. 2019 – 31 dez. 2020')
  assert.equal(survivorshipWindowSuffix(null), '')
  assert.equal(
    survivorshipDecidir({ start_label: '2 jan. 2003' }),
    'esta varredura usou só os ativos do catálogo de hoje (janela desde 2 jan. 2003). Ativos que saíram da Binance antes de hoje não estão no ranking.',
  )
})

const NVDA_ROW = {
  symbol: 'NVDA',
  timeframe: '1d',
  direction: 'long',
  asset: { symbol: 'NVDA', asset_class: 'stock', currency: 'USD' },
  execution: {
    precision_requested: 'intrabar',
    precision_effective: 'candle',
    timeframe: '1d',
    intraday_reason: 'coverage',
    intraday_missing: [{ from: '2003-01-02', to: '2025-12-31' }],
    window: { covered: { start: '2003-01-02T05:00:00+00:00', end: '2026-10-23T04:00:00+00:00' } },
  },
  conventions: { adjusted_prices: true, calendar: { sessions_per_year: 252 } },
  snapshot_id: '8b41d7e2aa00bb11cc22dd33ee44ff55',
}

test('bloco do candidato: classe, moeda, precisão em anos com o trecho exato, convenções e período efetivo', () => {
  const block = rowBlock(NVDA_ROW)
  assert.equal(block.cls, 'stock')
  assert.equal(block.currency, 'USD')
  assert.equal(block.lead, 'NVDA · 1d · Long')
  assert.deepEqual(block.precision, {
    tone: 'warn',
    short: 'Precisão diária (2003–2025)',
    full: 'Precisão diária · sem 15m de 2 jan. 2003 a 31 dez. 2025',
  })
  assert.equal(block.conventions, 'Binance Ações · NY · split · 252/ano')
  assert.equal(block.period, '2 jan. 2003 – 23 out. 2026')
  const btc = rowBlock({
    symbol: 'BTC/USDT',
    timeframe: '1d',
    direction: 'long',
    execution: { precision_requested: 'intrabar', precision_effective: 'intrabar_15m', timeframe: '1d' },
  })
  assert.equal(btc.currency, 'USDT')
  assert.equal(btc.precision.short, 'Precisão intrabar (15m)')
  assert.equal(btc.conventions, 'Binance Spot · 24/7 · 365 dias/ano')
  const old = rowBlock({ symbol: 'ETH/USDT', timeframe: '4h', direction: 'long' })
  assert.equal(old.precision.short, 'Precisão: não registrada nesta varredura')
})

test('modal de promoção por classe: título, destino e amostra', () => {
  // Card #1122: ação e ETF também vão para tier 3.
  assert.equal(promotionTitle('stock'), 'Promover a favorito tier 3')
  assert.equal(promotionTitle('crypto'), 'Promover a favorito tier 3')
  assert.equal(modalSampleText(NVDA_ROW), 'Amostra 8b41d7e2 · guardada enquanto o favorito existir · Direção Long')
})

test('filtro Classe: contagem, opção 0 desabilitada e estado vazio', () => {
  const opts = classOptions({ all: 2, crypto: 1, stock: 1, etf: 0 }, 'all')
  assert.deepEqual(
    opts.map((o) => [o.label, o.disabled]),
    [
      ['Todas (2)', false],
      ['Cripto (1)', false],
      ['Ações (1)', false],
      ['ETFs (0)', true],
    ],
  )
  assert.equal(classEmptyText('etf'), 'Nenhum candidato de ETF nesta varredura.')
  assert.equal(
    multiclassMeta(3),
    '3 classes · janela, candles e amostra em cada linha · taxa por lado: cripto 0,075% · ação e ETF 0,10% · slippage do timeframe',
  )
})

const BTC = { symbol: 'BTC/USDT', asset_class: 'crypto', currency: 'USDT', done: 1, total: 1, state: 'done', details: [{ timeframe: '1d', outcome: 'succeeded', precision: { kind: 'intrabar_15m', missing: [] } }] }
const NVDA_COLLECT = { symbol: 'NVDA', asset_class: 'stock', currency: 'USD', done: 0, total: 1, state: 'collecting', stage: '1d', series: '1d', role: 'candles', page: 3, pages: 6, attempt: 1 }
const SPY_QUEUED = { symbol: 'SPY', asset_class: 'etf', currency: 'USD', done: 0, total: 1, state: 'queued' }

test('Por ativo: estados com texto, ativo em curso no topo e linha viva', () => {
  assert.deepEqual(orderAssets([BTC, NVDA_COLLECT, SPY_QUEUED]).map((a) => a.symbol), ['NVDA', 'BTC/USDT', 'SPY'])
  assert.equal(assetStateView(NVDA_COLLECT, 'running').label, 'Coletando histórico · 1d · página 3 de 6')
  assert.equal(assetStateView(NVDA_COLLECT, 'paused').label, 'Pausado na coleta · 1d · página 3 de 6 · retoma daqui')
  assert.equal(assetStateView(BTC, 'running').label, 'Concluído')
  assert.equal(assetStateView(SPY_QUEUED, 'running').label, 'Na fila')
  assert.equal(assetStateView({ ...SPY_QUEUED, state: 'collecting', series: '5m', role: 'intraday', page: 7, pages: 16 }, 'running').label, 'Coletando histórico · 5m do intrabar · página 7 de 16')
  assert.equal(liveAnnouncement([NVDA_COLLECT, BTC], 'running'), 'NVDA: coletando histórico · 1d · página 3 de 6')
  assert.equal(assetStateView(SPY_QUEUED, 'cancelled').label, 'Não rodou · varredura cancelada')
})

test('Por ativo: desfecho misto mostra as duas contagens e o motivo por tempo, nunca "Concluído" sozinho', () => {
  const mixed = {
    symbol: 'NVDA',
    asset_class: 'stock',
    currency: 'USD',
    done: 2,
    total: 2,
    state: 'mixed',
    outcomes: { succeeded: 1, daily: 1, insufficient: 1, failed: 0, skipped: 0 },
    details: [
      { timeframe: '1d', outcome: 'succeeded', precision: { kind: 'daily', missing: [{ from: '2019-01-02', to: '2020-12-31' }] }, period: { start_label: '2 jan. 2019', end_label: '31 dez. 2020' } },
      { timeframe: '4h', outcome: 'insufficient', reason: 'sem candles de 4h de NVDA nessa janela (o 5m da Binance começa em 2 jan. 2026)' },
    ],
  }
  const view = assetStateView(mixed, 'completed')
  assert.equal(view.label, '1 concluída · 1 amostra insuficiente')
  assert.equal(
    view.detail,
    '1d: Precisão diária · sem 15m de 2 jan. 2019 a 31 dez. 2020 · período efetivo 2 jan. 2019 – 31 dez. 2020 · ' +
      '4h: Amostra insuficiente — sem candles de 4h de NVDA nessa janela (o 5m da Binance começa em 2 jan. 2026)',
  )
  assert.deepEqual(orderAssets([BTC, mixed]).map((a) => a.symbol), ['NVDA', 'BTC/USDT'])
  const note = noResultNote([BTC, mixed], 'completed')
  assert.equal(note.kind, 'insufficient')
  assert.equal(note.parts[0].text, 'NVDA 4h — sem candles nessa janela; as linhas ficam sem rank e sem Promover.')
})

test('Decidir: falha e "não rodou" ficam visíveis na nota "Sem resultado"', () => {
  const failed = {
    symbol: 'SPY',
    asset_class: 'etf',
    done: 1,
    total: 1,
    state: 'failed',
    reason: 'a Binance não respondeu ao histórico de SPY nas 3 tentativas',
    outcomes: { succeeded: 0, daily: 0, insufficient: 0, failed: 1, skipped: 0 },
    details: [{ timeframe: '1d', outcome: 'failed', reason: 'a Binance não respondeu ao histórico de SPY nas 3 tentativas' }],
  }
  const note = noResultNote([BTC, failed], 'partial_failure')
  assert.equal(note.kind, 'failed')
  assert.equal(note.parts[0].text, 'SPY — Falha: a Binance não respondeu ao histórico nas 3 tentativas.')
  assert.equal(assetStateView(failed, 'partial_failure').label, 'Falha: a Binance não respondeu ao histórico de SPY nas 3 tentativas')
  const notRun = [
    BTC,
    { symbol: 'NVDA', done: 1, total: 1, state: 'not_run', outcomes: { succeeded: 0, daily: 0, insufficient: 0, failed: 0, skipped: 1 } },
    { symbol: 'SPY', done: 1, total: 1, state: 'not_run', outcomes: { succeeded: 0, daily: 0, insufficient: 0, failed: 0, skipped: 1 } },
  ]
  const cancelled = noResultNote(notRun, 'cancelled')
  assert.equal(cancelled.kind, 'cancelled')
  assert.equal(cancelled.parts[0].text, 'NVDA e SPY — Não rodou · varredura cancelada.')
  assert.equal(noResultNote([BTC], 'running'), null)
})

test('Descoberta: textos que saem e o seletor com a nota das três classes', async () => {
  const source = await readFile(new URL('../src/pages/DiscoveryPage.tsx', import.meta.url), 'utf8')
  assert.doesNotMatch(source, /Nesta etapa as análises rodam só com cripto/)
  assert.doesNotMatch(source, /ações e ETFs fora/)
  assert.doesNotMatch(source, /a Descoberta vem depois/)
  assert.match(source, /classNote=\{DISCOVERY_CLASS_NOTE\}/)
  assert.match(source, /useSelectionView\(selectedSymbols, \{ equitiesRun: true \}\)/)
})
