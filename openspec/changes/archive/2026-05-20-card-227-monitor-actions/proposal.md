## Why

Monitor users need two explicit ways to inspect a strategy. The current action opens one combined modal, which mixes the quick chart view with deeper trade review and makes the intended workflow unclear.

## What Changes

- Split the Monitor strategy action into two visible Portuguese actions:
  - `Abrir Grafico`: open a chart-only view.
  - `Ver Trades`: open the trades list and strategy summary.
- Keep existing chart, candle, signal, and favorite-trade data behavior.
- Preserve desktop and mobile usability with compact actions that follow `DESIGN.md`.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `monitor`: Monitor strategy rows/cards expose separate chart-only and trade-analysis actions.

## Impact

- Frontend Monitor components:
  - `frontend/src/components/monitor/MonitorStatusTab.tsx`
  - `frontend/src/components/monitor/OpportunityCard.tsx`
  - `frontend/src/components/monitor/ChartModal.tsx`
- Focused Monitor Playwright coverage for both actions.
