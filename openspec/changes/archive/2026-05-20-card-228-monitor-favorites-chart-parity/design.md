## Overview

The bug persists because Monitor and Favorites have separate chart data assembly paths. Favorites opens `/combo/results` using saved favorite analysis trades and candles. Monitor opens `ChartModal` from an opportunity payload and can render markers from `signal_history`, fallback markers, or data loaded after the chart is already shown.

## Design Decisions

1. Use favorite analysis as the canonical chart source for saved favorite opportunities.
   - For a Monitor opportunity with a favorite id, load `/api/favorites/{id}/trades`.
   - Use returned `trades` to build Portuguese `COMPRA`/`VENDA` markers.
   - Use returned `candles` as the strategy-timeframe chart candle source when available.

2. Keep Monitor signal history as fallback, not primary source.
   - If `/favorites/{id}/trades` fails or returns no trades, the existing `signal_history` marker path remains available.
   - This avoids blank charts for protected or temporarily unavailable favorites.

3. Avoid showing stale marker state while favorite analysis is loading.
   - When the canonical favorite analysis request is in flight, the Monitor chart must not permanently settle on only the summarized opportunity markers if favorite analysis later provides different markers.
   - The marker count and current marker label must update from the canonical payload.

4. Preserve current UX boundaries.
   - No indicators are added back to Monitor.
   - Existing zoom/timeframe controls remain.
   - Protected strategy details remain hidden for common users.

## Validation

- Add/adjust E2E coverage for Monitor opening the chart button and receiving `/favorites/{id}/trades`.
- Validate frontend build.
- Validate OpenSpec change.
- Restart runtime and verify `/monitor` serves the updated bundle.
