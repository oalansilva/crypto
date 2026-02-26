## Context

The Monitor UI shows a single list of opportunities that can include both crypto pairs (e.g., `BTC/USDT`) and stock tickers (e.g., `AAPL`) depending on data source usage. Users want to focus on one universe at a time.

## Goals / Non-Goals

**Goals:**
- Add a simple UI filter (All/Crypto/Stocks) near the existing Monitor filters.
- Apply filtering locally in the frontend.

**Non-Goals:**
- Persisting this preference in backend monitor preferences.
- Changing the backend opportunities endpoint.

## Decisions

- Identify crypto vs stocks by symbol shape:
  - Crypto: contains `/`.
  - Stocks: does not contain `/`.
- Keep default = All.

## Risks / Trade-offs

- Symbol-shape heuristic assumes stocks never contain `/` and crypto always does, which matches current project conventions.
