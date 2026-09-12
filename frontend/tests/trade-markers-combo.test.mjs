import assert from 'node:assert/strict'
import test from 'node:test'

import {
  applyMarkerLabelDensity,
  buildComboResultsChartMarkers,
  buildTradeMarkers,
} from '../src/lib/tradeMarkers.ts'

const longTrades = [
  {
    entry_time: '2017-10-05T00:00:00.000Z',
    entry_price: 4200,
    exit_time: '2017-11-01T00:00:00.000Z',
    exit_price: 6400,
    profit: 0.05,
  },
  {
    entry_time: '2026-05-10T00:00:00.000Z',
    entry_price: 90000,
    exit_time: '2026-07-10T00:00:00.000Z',
    exit_price: 95000,
    profit: 0.04,
  },
]

test('buildComboResultsChartMarkers prefers the trade list over monitor recorte', () => {
  const shortMonitorHistory = [
    { timestamp: '2026-05-10T00:00:00.000Z', signal: 1, type: 'entry', price: 90000 },
    { timestamp: '2026-07-10T00:00:00.000Z', signal: -1, type: 'exit', price: 95000 },
  ]
  const fromList = buildTradeMarkers(longTrades, { direction: 'long', timeframe: '1d' })
  const merged = buildComboResultsChartMarkers(longTrades, shortMonitorHistory, {
    direction: 'long',
    timeframe: '1d',
  })
  assert.equal(fromList.length, 4)
  assert.equal(merged.length, 4)
})

test('buildComboResultsChartMarkers skips supplemental when closed trade shares entry candle', () => {
  const closedSameCandleTrades = [
    {
      entry_time: '2026-07-29T00:00:00.000Z',
      entry_price: 98000,
      exit_time: '2026-08-01T00:00:00.000Z',
      exit_price: 99000,
      profit: 0.01,
    },
  ]
  const openMonitorHistory = [
    { timestamp: '2026-07-29T12:00:00.000Z', signal: 1, type: 'entry', price: 98100 },
  ]
  const fromList = buildTradeMarkers(closedSameCandleTrades, { direction: 'long', timeframe: '1d' })
  const merged = buildComboResultsChartMarkers(closedSameCandleTrades, openMonitorHistory, {
    direction: 'long',
    timeframe: '1d',
  })
  assert.equal(fromList.length, merged.length)
  const entryMarkers = merged.filter((m) => m.signalType === 'entry')
  assert.equal(entryMarkers.length, 1)
})

test('buildComboResultsChartMarkers appends only the current open monitor operation', () => {
  const openMonitorHistory = [
    { timestamp: '2026-05-10T00:00:00.000Z', signal: 1, type: 'entry', price: 90000 },
    { timestamp: '2026-07-10T00:00:00.000Z', signal: -1, type: 'exit', price: 95000 },
    { timestamp: '2026-07-29T00:00:00.000Z', signal: 1, type: 'entry', price: 98000 },
  ]
  const merged = buildComboResultsChartMarkers(longTrades, openMonitorHistory, {
    direction: 'long',
    timeframe: '1d',
  })
  assert.equal(merged.length, 5)
})

test('applyMarkerLabelDensity hides labels when zoomed out', () => {
  const markers = buildTradeMarkers(longTrades, { direction: 'long', timeframe: '1d' })
  const dense = applyMarkerLabelDensity(markers, 400)
  assert.ok(dense.every((marker) => marker.text === ''))
  const labeled = applyMarkerLabelDensity(markers, 180)
  assert.ok(labeled.some((marker) => marker.text.includes('COMPRA')))
})
