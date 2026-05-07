## Overview

Card #167 split chart candles from saved favorite analysis candles. This card applies the same rule to entry/exit markers:

- saved favorite metrics/trades remain stored evidence;
- current Monitor `signal_history` is the primary operational source for chart markers and the visible trade list opened from Favorites;
- saved trades remain fallback if the Monitor sync fails or has no history.

## Decisions

### Decision: Fetch Monitor opportunities during Favorites analysis open

When a user clicks `Ver análise completa`, Favorites will request `/api/opportunities/?refresh=true&tier=all` and match the selected favorite by `id`, falling back to symbol/timeframe if needed.

Reason:
- This is the source used by the Monitor screen for current operational state.
- `refresh=true` avoids the short-lived opportunities cache when the user explicitly opens analysis to verify current state.
- It avoids adding a new backend contract in this card.

### Decision: Convert Monitor signal history into visible analysis trades

`signal_history` entries are paired as entry followed by exit. Closed pairs become visible trades with calculated profit. A trailing entry without exit remains an open trade marker.

Reason:
- `ComboResultsPage` already draws markers and the trade list from `result.trades`.
- Feeding Monitor-derived trades keeps chart and list consistent without changing the chart component.

### Decision: Preserve protected access constraints

Common users can receive redacted Monitor signal history. The result view still hides parameters, indicators, moving averages, and MA values for protected strategies.

## Fallback

If opportunities refresh fails, no matching opportunity is found, or signal history is empty, Favorites uses existing saved/reconstructed trades.

## Validation

- E2E: saved favorite has old trades, Monitor mock returns current signal history, opening Favorites analysis shows current dates/markers and does not show the stale trade date.
- Existing Favorites protected-user E2E remains green.
