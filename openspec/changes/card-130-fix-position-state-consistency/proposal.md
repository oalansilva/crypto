## Why

The Monitor list can correctly classify an opportunity as `HOLD`, while the chart modal still draws the current status marker as `EXIT` with a sell-style arrow. This makes an active long position look sold and conflicts with the TradeView interpretation.

## What Changes

- Split the chart's current position marker from the next-decision label.
- Render active `HOLD` opportunities as a current `LONG` marker with an entry-style green arrow.
- Keep the distance panel focused on the next decision (`exit`) while avoiding sell-looking current-state markers.
- Add focused E2E coverage for a HOLD chart without historical markers.

## Capabilities

### New Capabilities

### Modified Capabilities
- `monitor`: Monitor chart current marker must represent active position state consistently with the Monitor list.

## Impact

- `frontend/src/components/monitor/signalResolution.ts`
- `frontend/src/components/monitor/ChartModal.tsx`
- `frontend/tests/e2e/monitor-mobile-cards-timeframe.spec.ts`
