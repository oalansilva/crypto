// Card #1122: estado do mercado, identidade de configuração e status de atualização (lógica pura).
process.env.TZ = 'UTC'

import test from 'node:test'
import assert from 'node:assert/strict'
import {
  assetIdentityLong,
  assetIdentityShort,
  isOpportunityDataStale,
  marketStateView,
  opportunityRowKey,
  showsAlertTag,
} from '../src/components/monitor/marketState.ts'
import { resolveOpportunitySignal } from '../src/components/monitor/signalResolution.ts'
import { conventionsShort, formatFavoriteRefreshStatus, favoriteRowData } from '../src/lib/favoriteClass.ts'
import { promotionDestinationNote, promotionTitle } from '../src/lib/discoveryMulticlass.ts'

const BINANCE = {
  data_source: 'binance_equity',
  session: 'regular_ny',
  adjustment: 'split',
  label_short: 'Binance Ações · NY · split',
  label_compact: 'Binance · NY · split',
  label_long: 'Binance Ações · pregão regular de NY · ajustado por split',
}
const STOOQ = {
  data_source: 'stooq',
  session: 'eod',
  adjustment: 'legacy',
  label_short: 'Stooq · fonte antiga · diário',
  label_compact: 'Stooq · antiga · diário',
  label_long: 'Stooq · fonte antiga · diário',
}

const opp = (overrides = {}) => ({
  id: 1,
  symbol: 'NVDA',
  timeframe: '1d',
  template_name: 'multi_ma_crossover',
  name: 'NVDA',
  is_holding: true,
  distance_to_next_status: 2.1,
  next_status_label: 'exit',
  status: 'HOLD',
  last_price: 186.1,
  timestamp: '2026-10-23T04:00:00Z',
  asset_class: 'stock',
  currency: 'USD',
  configuration: BINANCE,
  notify_telegram: true,
  ...overrides,
})

test('identidade abreviada na linha e longa no title/detalhe', () => {
  assert.equal(assetIdentityShort(opp()), 'Ação · USD · Binance · NY · split')
  assert.equal(assetIdentityLong(opp()), 'Ação · USD · Binance Ações · pregão regular de NY · ajustado por split')
  assert.equal(assetIdentityShort(opp({ configuration: STOOQ })), 'Ação · USD · Stooq · antiga · diário')
  assert.equal(assetIdentityShort(opp({ asset_class: 'etf', symbol: 'SPY' })), 'ETF · USD · Binance · NY · split')
  assert.equal(assetIdentityShort(opp({ symbol: 'BTC/USDT', asset_class: 'crypto' })), null)
})

test('linhas de NVDA em duas fontes têm chaves distintas', () => {
  assert.equal(opportunityRowKey(opp()), 'nvda')
  assert.equal(opportunityRowKey(opp({ configuration: STOOQ })), 'nvda-legacy')
  assert.equal(opportunityRowKey(opp({ symbol: 'BTC/USDT', asset_class: 'crypto', configuration: null })), 'btc-usdt')
})

test('pregão aberto, fim de semana, feriado e antes da abertura (BRT com NY entre parênteses)', () => {
  const open = marketStateView(opp({ market_state: { state: 'open', reason: 'session', closes_at: '2026-10-26T20:00:00+00:00' } }))
  assert.equal(open.tone, 'open')
  assert.equal(open.short, 'Aberto · fecha 17:00 (16:00 NY)')
  assert.equal(open.full, 'Pregão aberto · fecha 17:00 (16:00 em NY)')
  const saturday = new Date('2026-10-24T14:05:00Z')
  const weekend = marketStateView(
    opp({ market_state: { state: 'closed', reason: 'weekend', next_open: '2026-10-26T13:30:00+00:00' } }),
    saturday,
  )
  assert.equal(weekend.short, 'Fechado · fim de semana · abre seg. 10:30 (09:30 NY)')
  assert.equal(weekend.full, 'Mercado fechado · fim de semana · abre seg., 26 out., 10:30 (09:30 em NY)')
  const holiday = marketStateView(
    opp({ market_state: { state: 'closed', reason: 'holiday', next_open: '2026-11-27T14:30:00+00:00' } }),
    new Date('2026-11-26T15:00:00Z'),
  )
  assert.equal(holiday.short, 'Fechado · feriado em NY · abre sex. 11:30 (09:30 NY)')
  const preOpen = marketStateView(
    opp({ market_state: { state: 'closed', reason: 'pre_open', next_open: '2026-10-27T13:30:00+00:00' } }),
    new Date('2026-10-27T11:05:00Z'),
  )
  assert.equal(preOpen.short, 'Fechado · abre hoje 10:30 (09:30 NY)')
  assert.equal(preOpen.full, 'Mercado fechado · fora do pregão · abre hoje, 10:30 (09:30 em NY)')
})

test('atraso real e dado insuficiente', () => {
  const stale = marketStateView(opp({
    market_state: {
      state: 'stale',
      last_candle: '2026-10-23T04:00:00+00:00',
      expected_candle: '2026-10-26T04:00:00+00:00',
    },
  }))
  assert.equal(stale.tone, 'stale')
  assert.equal(stale.short, 'Dados atrasados · falta seg. 26/10')
  assert.equal(stale.full, 'Dados atrasados · último candle sex., 23 out.; esperado seg., 26 out.')
  assert.equal(stale.holdShort, 'Sinal em espera')
  const insufficient = marketStateView(opp({ symbol: 'QQQ', market_state: { state: 'insufficient', available: 40, required: 200 } }))
  assert.equal(insufficient.short, 'Dados insuficientes · 40 de 200 candles')
  assert.equal(insufficient.holdFull, 'Sem sinal até completar o histórico')
})

test('cripto só mostra estado quando o servidor diz atraso; "Dados atrasados" substitui "Sem candle válido"', () => {
  const crypto = opp({ symbol: 'BTC/USDT', asset_class: 'crypto', currency: 'USDT', configuration: null })
  assert.equal(marketStateView({ ...crypto, market_state: { state: 'open', reason: '24x7' } }), null)
  const staleCrypto = {
    ...crypto,
    indicator_values_candle_time: '2026-10-23T00:00:00Z',
    market_state: { state: 'stale', last_candle: '2026-10-23T00:00:00+00:00', expected_candle: '2026-10-24T00:00:00+00:00' },
  }
  const resolved = resolveOpportunitySignal(staleCrypto, { selectedTimeframe: '1d' })
  assert.match(resolved.freshnessReason, /Dados atrasados · último candle sex\., 23 out\.; esperado sáb\., 24 out\./)
  assert.doesNotMatch(resolved.freshnessReason, /Sem candle válido/)
  // Ação 1d na segunda de manhã: candle de sexta, sem atraso pelo calendário.
  const monday = opp({ indicator_values_candle_time: '2020-01-03T05:00:00Z', market_state: { state: 'closed', reason: 'pre_open' } })
  assert.equal(isOpportunityDataStale(monday), false)
  assert.equal(resolveOpportunitySignal(monday, { selectedTimeframe: '1d' }).freshnessReason, null)
})

test('tag Alerta só no favorito marcado e nunca na vitrine', () => {
  assert.equal(showsAlertTag(opp()), true)
  assert.equal(showsAlertTag(opp({ notify_telegram: false })), false)
  assert.equal(showsAlertTag(opp({ is_curated_fallback: true })), false)
})

test('Favoritos: status com o último pregão, "Aguardando dados" e a fonte antiga', () => {
  const nvda = {
    symbol: 'NVDA',
    timeframe: '1d',
    asset: { symbol: 'NVDA', asset_class: 'stock', currency: 'USD' },
    metrics: { analysis_last_session: '2026-10-23' },
    auto_refresh_status: 'SUCCESS',
    auto_refresh_completed_at: '2026-10-24T11:12:00Z',
  }
  assert.equal(formatFavoriteRefreshStatus(nvda).label, 'Backtest atualizado: 24/10, 08:12 · último pregão 23/10')
  const waiting = formatFavoriteRefreshStatus({ ...nvda, auto_refresh_status: 'INSUFFICIENT', auto_refresh_error: '40 de 200 candles' })
  assert.equal(waiting.label, 'Aguardando dados: 40 de 200 candles')
  assert.equal(waiting.className, 'waiting')
  assert.equal(conventionsShort('stock', null, STOOQ), 'Stooq · fonte antiga · diário')
  assert.equal(favoriteRowData({ ...nvda, configuration: STOOQ }).conventions, 'Stooq · fonte antiga · diário')
  assert.equal(favoriteRowData({ ...nvda, configuration: BINANCE }).conventions, 'Binance Ações · NY · split · 252/ano')
})

test('Descoberta: ação e ETF vão para Tier 3 com a nota de "Alertar" e da carteira', () => {
  assert.equal(promotionTitle('stock'), 'Promover a favorito tier 3')
  assert.match(promotionDestinationNote('etf'), /marque "Alertar" lá e marque o ativo como "No portfólio" no Monitor/)
  assert.doesNotMatch(promotionDestinationNote('crypto'), /No portfólio/)
})
