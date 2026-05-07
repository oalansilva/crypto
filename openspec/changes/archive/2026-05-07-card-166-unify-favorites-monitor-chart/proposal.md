## Why

Favorites analysis currently opens `/combo/results` with the older candlestick chart, while Monitor uses a clearer operational chart surface. This creates two visual standards for the same strategy/candle analysis and makes Favorites harder to inspect.

## What Changes

- Replace the legacy Favorites result chart surface with a Monitor-aligned chart experience.
- Keep Favorites analysis on `/combo/results`, but render candles with the same dark operational canvas, readable candle colors, volume, moving averages, trade markers, and explicit zoom controls used by the Monitor pattern.
- Preserve the existing empty-chart state when no candles are available.
- Extend focused E2E coverage so legacy/multi MA Favorites analysis proves the chart is visible and no mismatch warning leaks to users.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `favorites`: Favorites analysis result view must use the Monitor-aligned chart presentation when opening a favorite with candle history.
- `chart-visualization`: Backtest/result chart surfaces must expose Monitor-aligned chart styling and controls where used by Favorites analysis.

## Impact

- Frontend chart components used by `ComboResultsPage`.
- Favorites E2E coverage.
- OpenSpec specs for Favorites and chart visualization.
