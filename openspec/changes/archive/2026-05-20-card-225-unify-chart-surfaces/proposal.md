## Why

Favorites has the richer chart data and cache path, while Monitor has a newer operational layout and prototype reference. Keeping separate chart implementations creates visual drift, duplicated chart logic, and inconsistent inspection behavior for the same strategy/candle analysis.

## What Changes

- Introduce one shared strategy chart surface used by Favorites results and Monitor graph modal.
- Use Favorites as the functional/data base: candles, volume, markers, zoom and cached result behavior remain intact.
- Adapt Monitor to the shared surface while preserving opportunity-specific context, timeframe switching, signal history, entry/stop lines and existing test identifiers.
- Apply `DESIGN.md` dark Binance tokens and use the provided prototype as structural reference, not as a divergent color system.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `chart-visualization`: Chart surfaces used by Favorites and Monitor must share the same visual/interaction foundation.
- `favorites`: Favorites result charts remain the data-complete base and must keep cached result behavior while using the shared surface.
- `monitor`: Monitor chart modal must use the shared chart surface while keeping Monitor-specific signal context and controls.

## Impact

- Frontend chart components in `frontend/src/components`.
- Monitor chart modal in `frontend/src/components/monitor`.
- Favorites result route through `ComboResultsPage`.
- Focused E2E tests for Favorites result charts and Monitor chart modal.
