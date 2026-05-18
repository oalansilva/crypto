## Why

The Monitor chart can appear briefly and then disappear or flicker when asynchronous chart context updates after the modal opens. Traders need the chart canvas to remain mounted while candles, markers, and trade context are refreshed.

## What Changes

- Keep the shared strategy chart instance mounted across marker, price-line, and tooltip updates.
- Update chart series data in place instead of destroying and recreating the lightweight chart for routine data changes.
- Verify the Monitor modal remains visible on the public `/monitor` flow after the chart opens.

## Capabilities

### New Capabilities

### Modified Capabilities
- `monitor`: Monitor chart modal rendering remains stable while chart data updates.

## Impact

- Frontend shared chart surface: `frontend/src/components/charts/StrategyChartSurface.tsx`
- Monitor chart modal runtime behavior and E2E/browser validation
- No backend API or database changes
