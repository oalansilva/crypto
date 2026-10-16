import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import test from 'node:test'
import ts from 'typescript'
import { comboPeriodHint, customPeriodImpediments, periodPayloadForApi, resolvePeriodDates } from '../src/lib/sweepPeriod.ts'

const comboSource = await readFile(new URL('../src/pages/ComboConfigurePage.tsx', import.meta.url), 'utf8')
const discoverySource = await readFile(new URL('../src/pages/DiscoveryPage.tsx', import.meta.url), 'utf8')

// Execute the production callbacks with their surrounding state injected, without
// mounting unrelated UI or running a backtest. AST extraction keeps the HTTP
// request construction under test rather than duplicating its payload here.
function bindCallback(source, name, bindings) {
  const ast = ts.createSourceFile('page.tsx', source, ts.ScriptTarget.Latest, true, ts.ScriptKind.TSX)
  let expression
  function visit(node) {
    if (ts.isFunctionDeclaration(node) && node.name?.text === name) expression = node
    if (ts.isVariableDeclaration(node) && node.name.getText(ast) === name) {
      expression = ts.isCallExpression(node.initializer) && node.initializer.expression.getText(ast) === 'useCallback'
        ? node.initializer.arguments[0] : node.initializer
    }
    ts.forEachChild(node, visit)
  }
  visit(ast)
  assert.ok(expression, `production callback ${name} exists`)
  const { outputText } = ts.transpileModule(`const callback = (${expression.getText(ast)});`, {
    compilerOptions: { target: ts.ScriptTarget.ES2022, module: ts.ModuleKind.None },
  })
  return new Function(...Object.keys(bindings), `${outputText}\nreturn callback;`)(...Object.values(bindings))
}

for (const [reference, period, start_date] of [
  ['2026-03-31', '1m', '2026-02-28'],
  ['2024-02-29', '1y', '2023-02-28'],
]) {
  test(`consumers preserve UTC window ${reference}/${period}`, async (t) => {
    // In western timezones this instant is still the previous local date.
    t.mock.timers.enable({ apis: ['Date'], now: new Date(`${reference}T00:30:00Z`) })
    const expected = { start_date, end_date: reference }
    assert.equal(comboPeriodHint(period, '', ''),
      `Será usada a janela ${period === '1m' ? '1 mês' : '1 ano'} (${start_date} → ${reference}).`)
    const requests = []
    const bindings = {
      API_BASE_URL: '/api', period, customStartDate: '', customEndDate: '',
      customPeriodImpediments, periodPayloadForApi, resolvePeriodDates,
      selectedTemplates: ['template'], selectedSymbols: ['BTC/USDT'],
      timeframes: ['1d'], directions: ['long'], recoveryStatus: 'ready', draftFrozen: false,
      preflight: null, draftKey: 'calendar-draft', draftMetric: 'calmar', viewSweep: null,
      focusStartedSweepRef: { current: false }, pollRevRef: { current: 0 }, activeSweepRef: { current: null },
      authFetch: async (url, options) => {
        if (options?.body) requests.push({ url, payload: JSON.parse(options.body) })
        return { ok: true, json: async () => ({
          snapshot_token: 'token', snapshot_hash: 'hash', valid_total: 1,
          sweep_id: 'sweep', state: 'running', exists: false, oos_verdict: 'GO',
        }) }
      },
      alert: (message) => assert.fail(message), navigate: () => {},
      apiUrl: (url) => new URL(url, 'https://example.test'),
      templateName: 'template', timeframe: '1d', direction: 'long', params: [],
      batchScope: 'selected', deepBacktest: false, walkForwardEnabled: true, walkForwardTrainRatio: 0.7,
      batchStartTimeRef: { current: null }, getBatchSymbols: () => ['BTC/USDT'],
    }
    for (const name of [
      'setStartError', 'setPreflight', 'setSnapshotStale', 'setPreflightLoading', 'setPreflightError',
      'setBusy', 'setActiveSweep', 'setViewSweep', 'setMetric', 'setDraftFrozen', 'setPage', 'setMode',
      'setExpandedRows', 'setRows', 'setTotalMatched', 'setTotalAvailable', 'showToast', 'loadHistory',
      'loadPartials', 'setRunning', 'setBatchRunning', 'setBatchJobId', 'setBatchProgress', 'setBatchTotal',
      'setBatchPauseCancelRequested', 'setClientElapsedSec',
    ]) bindings[name] = () => {}

    bindings.setPreflight = (value) => { bindings.preflight = value }
    await bindCallback(discoverySource, 'runPreflight', bindings)()
    assert.ok(bindings.preflight)
    await bindCallback(discoverySource, 'startSweep', bindings)()
    bindings.getPeriodDates = bindCallback(comboSource, 'getPeriodDates', bindings)
    await bindCallback(comboSource, 'handleRun', bindings)()
    bindings.getBatchSymbols = () => ['BTC/USDT', 'ETH/USDT']
    await bindCallback(comboSource, 'handleRun', bindings)()

    assert.deepEqual(requests.map(({ url }) => url), [
      '/api/combos/discovery/sweeps/preflight', '/api/combos/discovery/sweeps',
      '/api/combos/optimize', '/api/combos/backtest/batch',
    ])
    for (const { payload } of requests) {
      assert.deepEqual({ start_date: payload.start_date, end_date: payload.end_date }, expected)
      assert.equal(payload.period_type, period)
    }
  })
}
