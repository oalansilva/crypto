import assert from 'node:assert/strict'
import test from 'node:test'

import {
  buildSignalHistoryMarkers,
  getSignalHistoryLabel,
  sortSignalHistoryNewestFirst,
} from '../src/lib/signalHistory.ts'

test('sortSignalHistoryNewestFirst orders recent signals first', () => {
  const sorted = sortSignalHistoryNewestFirst([
    { timestamp: '2026-05-10T00:00:00.000Z', signal: 1, type: 'entry', price: 100 },
    { timestamp: '2026-05-20T00:00:00.000Z', signal: -1, type: 'exit', price: 110 },
    { timestamp: '2026-05-15T00:00:00.000Z', signal: 1, type: 'entry', price: 105 },
  ])
  assert.equal(sorted[0].timestamp, '2026-05-20T00:00:00.000Z')
  assert.equal(sorted[1].timestamp, '2026-05-15T00:00:00.000Z')
})

test('getSignalHistoryLabel respects long and short semantics', () => {
  const entry = { timestamp: '2026-05-10T00:00:00.000Z', signal: 1, type: 'entry' }
  const exit = { timestamp: '2026-05-11T00:00:00.000Z', signal: -1, type: 'exit' }
  assert.equal(getSignalHistoryLabel(entry, 'long'), 'Compra')
  assert.equal(getSignalHistoryLabel(exit, 'long'), 'Venda')
  assert.equal(getSignalHistoryLabel(entry, 'short'), 'Venda')
  assert.equal(getSignalHistoryLabel(exit, 'short'), 'Compra')
})

test('buildSignalHistoryMarkers creates compra/venda markers', () => {
  const markers = buildSignalHistoryMarkers([
    { timestamp: '2026-05-10T00:00:00.000Z', signal: 1, type: 'entry', price: 100 },
    { timestamp: '2026-05-20T00:00:00.000Z', signal: -1, type: 'exit', price: 110 },
  ], 'long')
  assert.equal(markers.length, 2)
  assert.equal(markers[0].text, 'Compra')
  assert.equal(markers[1].text, 'Venda')
})
