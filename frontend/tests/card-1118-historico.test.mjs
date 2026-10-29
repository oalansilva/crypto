// Fuso fixo antes de qualquer Date: os textos de atualização usam o fuso do navegador.
process.env.TZ = 'America/Sao_Paulo'

import test from 'node:test'
import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import {
  coverageNote,
  coverageRows,
  formatShortDateTime,
  gapLabel,
  gapsCountText,
  hasCoverageDetail,
  historySummary,
  historyText,
  onDemandHistory,
  sinceText,
  zoneLabel,
} from '../src/lib/assetSelection.ts'
import { NOT_REPRODUCIBLE, evidenceSample, rowSample, seriesLine } from '../src/lib/sampleState.ts'

/**
 * Card #1118 (6.4): textos do fato de histórico, da tabela de cobertura e do estado da amostra.
 * Os dados são os do protótipo aprovado (NVDA, SPY, QQQ, IBIT, AAPL, WAVES, BTC/USDT).
 */

const NOW = new Date('2026-10-23T15:00:00Z')
const NY = 'America/New_York'
const NOTE_EQUITY = 'Binance Ações · pregão regular de Nova York · ajustado por split'
const NOTE_CRYPTO = 'Binance Spot · 24/7 · ajuste não se aplica'

const frame = (timeframe, from, to, extra = {}) => ({
  timeframe,
  from,
  to,
  gap_count: 0,
  gaps: [],
  updated_at: '2026-10-22T21:12:00Z',
  origin: 'native',
  derived_from: null,
  state: 'idle',
  ...extra,
})

const asset = (symbol, asset_class, history, state_label = 'Negociável') => ({
  asset_id: `x:${symbol}`,
  asset_class,
  symbol,
  name: symbol,
  state: 'tradable',
  state_label,
  state_reason: null,
  selectable: true,
  analysis_available: asset_class === 'crypto',
  history,
})

const NVDA = asset('NVDA', 'stock', {
  status: 'covered',
  from: '2014-11-11T05:00:00Z',
  to: '2026-10-22T20:00:00Z',
  updated_at: '2026-10-22T20:12:00Z',
  gap_count: 0,
  note: NOTE_EQUITY,
  calendar_timezone: NY,
  timeframes: [
    frame('1d', '2014-11-11T05:00:00Z', '2026-10-22T04:00:00Z'),
    frame('5m', '2026-05-19T13:30:00Z', '2026-10-22T19:55:00Z'),
    frame('15m', '2026-05-19T13:30:00Z', '2026-10-22T19:45:00Z', { origin: 'derived', derived_from: '5m' }),
  ],
})

const SPY = asset('SPY', 'etf', {
  status: 'covered',
  from: '2014-11-11T05:00:00Z',
  to: '2026-10-22T20:00:00Z',
  updated_at: '2026-10-22T20:12:00Z',
  gap_count: 1,
  note: NOTE_EQUITY,
  calendar_timezone: NY,
  timeframes: [
    frame('1d', '2014-11-11T05:00:00Z', '2026-10-22T04:00:00Z'),
    frame('5m', '2026-07-01T13:30:00Z', '2026-10-22T19:55:00Z', {
      gap_count: 1,
      gaps: [{ start: '2026-10-14T14:05:00Z', end: '2026-10-14T14:40:00Z', count: 8 }],
    }),
    frame('15m', '2026-07-01T13:30:00Z', '2026-10-22T19:45:00Z', {
      origin: 'derived',
      derived_from: '5m',
      gap_count: 0,
      gaps: [
        {
          start: '2026-10-14T14:00:00Z',
          end: '2026-10-14T14:30:00Z',
          block_end: '2026-10-14T14:45:00Z',
          count: 4,
          inherited_from: '5m',
        },
      ],
    }),
  ],
})

const BTC = asset('BTC/USDT', 'crypto', {
  status: 'covered',
  from: '2017-08-17T00:00:00Z',
  to: '2026-10-22T21:00:00Z',
  updated_at: '2026-10-22T21:00:00Z',
  gap_count: 0,
  note: NOTE_CRYPTO,
  calendar_timezone: null,
  timeframes: ['1d', '4h', '1h', '15m'].map((tf) => frame(tf, '2017-08-17T00:00:00Z', '2026-10-22T21:00:00Z', { updated_at: '2026-10-22T21:00:00Z' })),
})

test('sob demanda: o texto diz a classe e nenhuma tela promete botão', () => {
  const texts = {
    crypto: 'Histórico sob demanda · coletado quando uma análise pedir',
    stock: 'Histórico sob demanda · a coleta começa quando as análises aceitarem ações',
    etf: 'Histórico sob demanda · a coleta começa quando as análises aceitarem ETFs',
  }
  for (const cls of Object.keys(texts)) {
    const text = historyText(asset('X', cls, onDemandHistory()), NOW)
    assert.equal(text, texts[cls])
    assert.doesNotMatch(text, /não coletado/i)
    assert.doesNotMatch(text, /botão|clique|iniciar a coleta/i)
  }
  assert.equal(hasCoverageDetail(onDemandHistory()), false)
})

test('coberto: início comum diz "Histórico desde"; inícios diferentes dizem de qual timeframe é cada "desde"', () => {
  assert.equal(
    historySummary(BTC, NOW).text,
    'Histórico desde 17 ago. 2017 · 4 timeframes · sem lacunas · atualizado 22 out., 18:00',
  )
  assert.equal(sinceText(BTC.history), 'Histórico desde 17 ago. 2017 · 4 timeframes')
  assert.equal(
    historySummary(NVDA, NOW).text,
    '1d desde 11 nov. 2014 · 5m e 15m desde 19 mai. 2026 · sem lacunas · atualizado 22 out., 17:12',
  )
  assert.doesNotMatch(historySummary(NVDA, NOW).text, /^Histórico desde/)
})

test('lacuna do 5m conta uma vez só: o 15m derivado herda e não soma', () => {
  assert.equal(historySummary(SPY, NOW).text, '1d desde 11 nov. 2014 · 5m e 15m desde 01 jul. 2026 · 1 lacuna · atualizado 22 out., 17:12')
  assert.equal(historySummary(SPY, NOW).tone, 'gap')
  assert.equal(gapsCountText(0), 'sem lacunas')
  assert.equal(gapsCountText(1), '1 lacuna')
  assert.equal(gapsCountText(3), '3 lacunas')
})

test('tabela de cobertura: lacuna no horário de Nova York, 15m "montado do 5m" e "herdada do 5m"', () => {
  const rows = coverageRows(SPY.history, NOW)
  assert.deepEqual(rows.map((r) => r.timeframe), ['1d', '5m', '15m'])
  assert.equal(rows[1].gaps, '1 lacuna: 14 out. 2026, 10:05–10:40, horário de Nova York (8 candles que a Binance não tem)')
  assert.equal(rows[2].origin, 'montado do 5m')
  assert.equal(rows[2].derived, true)
  assert.equal(
    rows[2].gaps,
    'herdada do 5m: 14 out. 2026, 10:00–10:45, horário de Nova York (bloco incompleto; não soma no resumo)',
  )
  assert.equal(rows[0].origin, 'nativo')
  assert.equal(rows[0].gaps, 'sem lacunas')
  assert.equal(rows[1].period, '01 jul. 2026 – 22 out. 2026')
  assert.equal(coverageNote(SPY.history), `${NOTE_EQUITY}. Mercado fechado não conta como lacuna.`)
  assert.equal(zoneLabel('America/Sao_Paulo'), 'Brasília')
})

test('lacuna de cripto vai no horário local do navegador, sem dizer Nova York', () => {
  const label = gapLabel({ start: '2026-10-14T14:00:00Z', end: '2026-10-14T16:00:00Z', count: 3 }, '1h', BTC.history)
  assert.match(label, /^14 out\. 2026, 11:00–13:00, horário local$/)
})

test('coleta em andamento, falha com "já coletado" e parcial', () => {
  const collecting = asset('QQQ', 'etf', {
    status: 'collecting',
    from: '2023-01-05T05:00:00Z',
    to: '2026-10-22T04:00:00Z',
    note: NOTE_EQUITY,
    calendar_timezone: NY,
    collecting: { timeframe: '1d', page: 2, requested_at: '2026-10-22T21:06:00Z' },
    timeframes: [frame('1d', '2023-01-05T05:00:00Z', '2026-10-22T04:00:00Z', { state: 'collecting' })],
  })
  assert.equal(historySummary(collecting, NOW).text, 'Coletando histórico · 1d, página 2 · pedido às 18:06')
  assert.equal(historySummary(collecting, NOW).tone, 'busy')
  assert.equal(coverageRows(collecting.history, NOW)[0].gaps, 'em coleta')

  const failed = asset('QQQ', 'etf', {
    status: 'failed',
    from: '2023-01-05T05:00:00Z',
    to: '2026-10-22T04:00:00Z',
    note: NOTE_EQUITY,
    calendar_timezone: NY,
    error: { timeframe: '1d', code: 'binance_rate_limited', message: 'limite de requisições da Binance', at: '2026-10-22T21:06:00Z' },
    timeframes: [frame('1d', '2023-01-05T05:00:00Z', '2026-10-22T04:00:00Z', { state: 'failed', incomplete: true })],
  })
  assert.equal(
    historySummary(failed, NOW).text,
    'Coleta falhou 22 out., 18:06 · limite de requisições da Binance · já coletado: 1d desde 05 jan. 2023',
  )
  assert.equal(historySummary(failed, NOW).tone, 'fail')
  assert.doesNotMatch(historySummary(failed, NOW).text, /488006/)

  const partial = asset('IBIT', 'etf', {
    status: 'partial',
    from: '2024-01-11T05:00:00Z',
    to: '2026-10-21T04:00:00Z',
    updated_at: '2026-10-21T13:30:00Z',
    note: NOTE_EQUITY,
    calendar_timezone: NY,
    partial: { timeframe: '1d', requested_since: '2021-10-22T04:00:00Z', starts_at: '2024-01-11T05:00:00Z', insufficient: true },
    timeframes: [frame('1d', '2024-01-11T05:00:00Z', '2026-10-21T04:00:00Z', { insufficient: true, requested_since: '2021-10-22T04:00:00Z', starts_at: '2024-01-11T05:00:00Z' })],
  })
  assert.equal(
    historySummary(partial, NOW).text,
    'Parcial: pedido desde 22 out. 2021; a Binance tem desde 11 jan. 2024 · atualizado 21 out., 10:30',
  )
  assert.match(coverageRows(partial.history, NOW)[0].gaps, /^insuficiente para o último pedido \(desde 22 out\. 2021\)/)
})

test('formatShortDateTime omite o ano só no ano corrente', () => {
  assert.equal(formatShortDateTime('2026-10-22T21:00:00Z', 'America/Sao_Paulo', NOW), '22 out., 18:00')
  assert.equal(formatShortDateTime('2025-10-22T21:00:00Z', 'America/Sao_Paulo', NOW), '22 out. 2025, 18:00')
})

test('Decidir: série na evidência e estado da amostra (guardada, vencida, favorita)', () => {
  const kept = {
    timeframe: '1d',
    candle_source: 'Binance Spot',
    candle_version: '7',
    provenance: { data_source: 'Binance Spot', timeframe_origin: 'native', data_version: 7 },
    sample: { state: 'kept', retain_until: '2026-11-21T12:00:00Z' },
    dedup_state: 'unique',
  }
  assert.equal(seriesLine(kept), 'Binance Spot · 1d nativo · v7')
  assert.equal(seriesLine({ timeframe: '1d', candle_source: 'ccxt', candle_version: 'abc' }), 'ccxt vabc')
  assert.equal(seriesLine({ ...kept, timeframe: '15m', provenance: { ...kept.provenance, timeframe_origin: 'derived' } }), 'Binance Spot · 15m montado do 5m · v7')

  const evidence = evidenceSample([kept])
  assert.equal(evidence.text, 'amostra guardada até 21 nov. 2026; favoritos guardam a amostra do último refresh')
  assert.equal(evidence.tone, 'plain')
  assert.deepEqual(rowSample(kept), { sample: 'amostra até 21 nov. 2026', sampleTone: 'plain', favorite: null })

  const favorite = { ...kept, dedup_state: 'already_promoted' }
  assert.equal(rowSample(favorite).favorite, 'favorito: Favoritos guarda a amostra do último refresh')

  const expired = { ...kept, sample: { state: 'expired', retain_until: '2026-11-21T12:00:00Z' } }
  const expiredEvidence = evidenceSample([expired])
  assert.equal(expiredEvidence.text, `amostra expirada em 21 nov. 2026: ${NOT_REPRODUCIBLE}`)
  assert.equal(expiredEvidence.tone, 'expired')
  assert.equal(rowSample(expired).sample, NOT_REPRODUCIBLE)
  assert.equal(rowSample(expired).sampleTone, 'expired')
  const expiredFavorite = evidenceSample([{ ...expired, dedup_state: 'already_promoted' }])
  assert.equal(expiredFavorite.text, `amostra expirada em 21 nov. 2026: ${NOT_REPRODUCIBLE}`)
  assert.equal(expiredFavorite.suffix, ' · favoritos guardam a amostra do último refresh')

  // Resultado de varredura antiga: sem amostra guardada, sem prometer reprodução.
  assert.equal(rowSample({ timeframe: '1d', sample: { state: 'none', retain_until: null } }).sample, 'sem amostra guardada')
  assert.equal(evidenceSample([]), null)
})

test('"Histórico não coletado" não existe em nenhum arquivo do seletor', async () => {
  for (const file of ['../src/components/AssetPicker.tsx', '../src/lib/assetSelection.ts', '../src/lib/sampleState.ts']) {
    const source = await readFile(new URL(file, import.meta.url), 'utf8')
    const code = source
      .split('\n')
      .filter((line) => !/^\s*(\/\/|\/\*|\*)/.test(line))
      .join('\n')
    assert.doesNotMatch(code, /Histórico não coletado/, file)
  }
})

test('o botão "Cobertura" fica fora do <label> e o estado da amostra usa 11 px', async () => {
  const picker = await readFile(new URL('../src/components/AssetPicker.tsx', import.meta.url), 'utf8')
  assert.match(picker, /<label className="ap-id" htmlFor=\{pickId\}>/)
  assert.match(picker, /aria-expanded=\{isOpen\}/)
  assert.match(picker, /aria-controls=\{panelId\}/)
  const css = await readFile(new URL('../src/pages/DiscoveryPage.css', import.meta.url), 'utf8')
  assert.match(css, /\.sample-state \{ font-size: 11px; \}/)
})
