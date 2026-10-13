import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
import test from 'node:test'
import {
  customPeriodImpediments,
  DISCOVERY_DEFAULT_PERIOD,
  isPeriodKey,
  PERIOD_OPTIONS,
  periodDisplayLabel,
  periodPayloadForApi,
  resolvePeriodDates,
} from '../src/lib/sweepPeriod.ts'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const discoveryPath = path.resolve(__dirname, '../src/pages/DiscoveryPage.tsx')
const comboConfigurePath = path.resolve(__dirname, '../src/pages/ComboConfigurePage.tsx')
const calendarCases = JSON.parse(await readFile(
  path.resolve(__dirname, '../../backend/tests/fixtures/sweep-calendar-parity.json'), 'utf8',
))

for (const { reference, starts } of calendarCases) {
  for (const [period, start_date] of Object.entries(starts)) {
    test(`UTC calendar ${reference} minus ${period}`, () => {
      assert.deepEqual(resolvePeriodDates(period, '', '', reference), {
        start_date,
        end_date: reference,
      })
    })
  }
}

test('shared period list order and labels', () => {
  assert.deepEqual(
    PERIOD_OPTIONS,
    [
      { value: '15d', label: '15 dias' }, { value: '1m', label: '1 mês' },
      { value: '3m', label: '3 meses' }, { value: '6m', label: '6 meses' },
      { value: '1y', label: '1 ano' }, { value: '2y', label: '2 anos' },
      { value: 'custom', label: 'Personalizado' }, { value: 'all', label: 'Todo o histórico' },
    ],
  )
  for (const { value, label } of PERIOD_OPTIONS) {
    assert.equal(isPeriodKey(value), true)
    assert.equal(periodDisplayLabel(value), label)
  }
  for (const value of [null, undefined, '', '30d']) assert.equal(isPeriodKey(value), false)
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

test('other modes retain nulls, custom dates, omissions and impediments', (t) => {
  t.mock.timers.enable({ apis: ['Date'], now: new Date('2026-08-15T00:30:00Z') })
  assert.deepEqual(periodPayloadForApi('15d', '', ''), {
    period_type: '15d', start_date: '2026-07-31', end_date: '2026-08-15',
  })
  assert.deepEqual(periodPayloadForApi('all', '2026-01-01', '2026-06-01'), { period_type: 'all' })
  for (const [start, end, issues] of [
    ['', '', ['Seleccione Data Inicial e Data Final.']],
    ['', '2026-06-01', ['Seleccione Data Inicial.']],
    ['2026-01-01', '', ['Seleccione Data Final.']],
    ['2026-06-01', '2026-01-01', ['Data Inicial não pode ser depois da Data Final.']],
    ['2026-01-01', '2026-08-16', ['Data Final não pode ser depois de hoje.']],
    ['2026-01-01', '2026-08-15', []],
    ['2026-08-15', '2026-08-15', []],
  ]) {
    assert.deepEqual(resolvePeriodDates('custom', start, end), { start_date: start || null, end_date: end || null })
    const payload = periodPayloadForApi('custom', start, end)
    assert.deepEqual(payload, { period_type: 'custom', start_date: start || undefined, end_date: end || undefined })
    assert.deepEqual(JSON.parse(JSON.stringify(payload)), {
      period_type: 'custom', ...(start ? { start_date: start } : {}), ...(end ? { end_date: end } : {}),
    })
    assert.deepEqual(customPeriodImpediments('custom', start, end), issues)
  }
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
