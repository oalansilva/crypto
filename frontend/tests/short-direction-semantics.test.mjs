import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { test } from 'node:test';

const read = (path) => readFileSync(new URL(`../${path}`, import.meta.url), 'utf8');

test('trade markers carry explicit entry and exit phases for short semantics', () => {
  const source = read('src/lib/tradeMarkers.ts');

  assert.match(source, /export type MarkerSignalType = 'entry' \| 'exit'/);
  assert.match(source, /signalType: 'entry'/);
  assert.match(source, /signalType: 'exit'/);
  assert.match(source, /marker\.signalType/);
});

test('monitor signal resolution maps short hold to venda and short exit to compra', () => {
  const source = read('src/components/monitor/signalResolution.ts');

  assert.match(source, /direction === 'short'/);
  assert.match(source, /badgeText: 'Venda'/);
  assert.match(source, /badgeText: 'Compra'/);
  assert.match(source, /const entry = direction === 'short' \? 'Venda' : 'Compra'/);
  assert.match(source, /const exit = direction === 'short' \? 'Compra' : 'Venda'/);
});

test('chart modal renders signal history markers and entry line by opportunity direction', () => {
  const source = read('src/components/monitor/ChartModal.tsx');

  assert.match(source, /getSignalHistoryMarker\(item, opportunityDirection\)/);
  assert.match(source, /signalType: item\.type/);
  assert.match(source, /Venda\/Short/);
  assert.match(source, /opportunity\.direction \?\? opportunity\.parameters\?\.direction/);
});

test('monitor section headings are neutral because rows may mix long and short strategies', () => {
  const tab = read('src/components/monitor/MonitorStatusTab.tsx');
  const resolution = read('src/components/monitor/signalResolution.ts');

  assert.match(tab, /boardStateLabel/);
  assert.match(resolution, /section === 'hold' \? 'Em posição' : 'Saída \/ cobertura'/);
  assert.doesNotMatch(tab, /Em posição · Compra/);
  assert.doesNotMatch(tab, /Em saída · Venda/);
  assert.doesNotMatch(tab, /Estado Compra/);
});
