import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
import test from 'node:test'
import {
  customPeriodImpediments,
  DISCOVERY_DEFAULT_PERIOD,
  PERIOD_OPTIONS,
  periodDisplayLabel,
  periodPayloadForApi,
  resolvePeriodDates,
} from '../src/lib/sweepPeriod.ts'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const discoveryPath = path.resolve(__dirname, '../src/pages/DiscoveryPage.tsx')
const comboConfigurePath = path.resolve(__dirname, '../src/pages/ComboConfigurePage.tsx')

test('shared period list order and labels', () => {
  assert.deepEqual(
    PERIOD_OPTIONS.map((o) => o.value),
    ['15d', '1m', '3m', '6m', '1y', '2y', 'custom', 'all'],
  )
  assert.equal(periodDisplayLabel('15d'), '15 dias')
  assert.equal(periodDisplayLabel('all'), 'Todo o histórico')
  assert.equal(DISCOVERY_DEFAULT_PERIOD, '15d')
})

test('resolvePeriodDates fixed and custom', () => {
  const today = '2026-08-15'
  assert.deepEqual(resolvePeriodDates('all', '', '', today), {
    start_date: null,
    end_date: null,
  })
  assert.deepEqual(resolvePeriodDates('15d', '', '', today), {
    start_date: '2026-07-31',
    end_date: today,
  })
  assert.deepEqual(
    periodPayloadForApi('custom', '2026-01-01', '2026-06-01'),
    { period_type: 'custom', start_date: '2026-01-01', end_date: '2026-06-01' },
  )
})

test('customPeriodImpediments copy', () => {
  assert.deepEqual(customPeriodImpediments('custom', '', '', '2026-08-15'), [
    'Seleccione Data Inicial e Data Final.',
  ])
  assert.deepEqual(customPeriodImpediments('custom', '2026-02-01', '2026-01-01', '2026-08-15'), [
    'Data Inicial não pode ser depois da Data Final.',
  ])
  assert.equal(customPeriodImpediments('15d', '', '', '2026-08-15').length, 0)
})

test('newDraft repõe período default da Descoberta', async () => {
  const source = await readFile(discoveryPath, 'utf8')
  const block = source.slice(source.indexOf('const newDraft = useCallback'))
  assert.match(block, /setPeriod\(DISCOVERY_DEFAULT_PERIOD\)/)
  assert.match(block, /setCustomStartDate\(''\)/)
  assert.match(block, /setCustomEndDate\(''\)/)
})

test('Combo exists check inclui intervalo Personalizado', async () => {
  const source = await readFile(comboConfigurePath, 'utf8')
  assert.match(
    source,
    /if \(period === 'custom'\)[\s\S]*searchParams\.set\('start_date', start_date\)/,
  )
  assert.match(
    source,
    /if \(period === 'custom'\)[\s\S]*searchParams\.set\('end_date', end_date\)/,
  )
})
