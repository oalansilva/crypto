## Why

ADA can appear as `HOLD` in the Monitor while the chart modal has no confirmed entry signal. This creates conflicting trading guidance: the list says there is an active position, but the detailed chart cannot prove the entry.

## What Changes

- Align Monitor `HOLD` state with confirmed active entry evidence from strategy signal history.
- Downgrade opportunities with no active entry proof to `WAIT`, keeping entry distance visible.
- Preserve existing chart signal history and resolved context behavior.
- Refresh chart candles from CCXT when persisted TimescaleDB candles are stale for the requested timeframe.
- Open Monitor charts on the opportunity strategy timeframe by default, preserving manual timeframe switching after the modal opens.
- Add regression coverage for a trend-up/no-entry case matching card 124.

## Capabilities

### New Capabilities

- `monitor-active-entry-confirmation`: Monitor only exposes `HOLD` as an active position when the strategy payload confirms an open entry.
- `monitor-chart-fresh-candles`: Monitor chart candles use fresh provider data when persisted storage is stale.

### Modified Capabilities

- `opportunity-monitor`: `HOLD` state now requires active entry confirmation instead of trend state alone.

## Impact

- Backend: `backend/app/services/opportunity_service.py` position-state resolution and opportunity payload fields.
- Backend: `backend/app/api.py` market candles endpoint freshness gate before using persisted OHLCV rows.
- Tests: focused unit coverage for active-entry confirmation.
- Frontend: Monitor chart modal opens with the strategy timeframe so the displayed candles match signal-history validation by default.
