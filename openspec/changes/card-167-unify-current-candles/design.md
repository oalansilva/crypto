## Overview

Favorites should separate two concepts that are currently coupled:

- saved favorite evidence: trades, metrics, and historical analysis payload used to reproduce the favorite summary;
- chart visualization context: the current market candle window used by UI chart surfaces.

The chart visualization context should come from `/api/market/candles` whenever possible, matching the Monitor path. Saved `metrics.analysis_candles` remains useful as a fallback and for legacy audit context, but it should not be the first source used to draw a Favorites chart.

## Decisions

### Decision: Fetch current candles in Favorites before opening result view

`FavoritesDashboard` will load current candles for the selected favorite via the same market candles endpoint used by Monitor, then pass those candles to `/combo/results`.

Reason:
- The user action starts in Favorites, so this is the smallest point where stale saved analysis candles can be replaced before rendering.
- `/combo/results` already receives a result object through navigation state, so no route contract change is needed.
- Common protected users can still receive current candles without receiving protected strategy internals.

### Decision: Keep saved trades and metrics unchanged

The favorite summary, trades, and metrics stay sourced from the saved favorite/trades endpoint. This avoids silent recalculation or changing favorite performance history when the user only wants to inspect the chart.

### Decision: Fallback to saved analysis candles only on current-candle failure

If `/api/market/candles` fails or returns no rows, the system can still render the saved analysis candles. This avoids blanking legacy favorites, while ensuring the normal path uses current data.

## Risks

- Current candles can cover a shorter window than old all-history `analysis_candles`. This is acceptable for UI visualization because Monitor already uses a bounded current window.
- Trade markers from old saved trades may be outside the current window. The chart component already renders markers only when timestamps match candle data.

## Validation

- E2E test with stale saved `analysis_candles` ending earlier than mocked `/market/candles`.
- Build and targeted Favorites E2E suite.
- Live evidence comparing BTC/USDT current market candles against Favorites chart payload behavior.
