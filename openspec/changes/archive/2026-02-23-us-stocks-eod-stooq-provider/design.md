## Context

The current backtest and monitoring pipeline primarily targets crypto pairs with 24/7 data availability, typically fetched via exchange APIs. To support US stocks/ETFs without paid market data subscriptions, we need a free end-of-day (1D) provider and minimal changes to the existing strategy/analyzer pipeline.

Key constraints:
- US market data is not 24/7; weekends/holidays exist.
- The initial scope is EOD-only (1D). Intraday (1h/15m) is explicitly out of scope.
- Existing crypto behavior must remain unchanged.

## Goals / Non-Goals

**Goals:**
- Add a Stooq-based provider for US stocks/ETFs EOD OHLCV.
- Normalize symbol representation so the pipeline can handle both `BTC/USDT` and `AAPL`.
- Add a config parameter (e.g., `data_source`) to select provider for backtests and monitoring.
- Implement caching (TTL) to reduce provider calls and improve stability.

**Non-Goals:**
- Real-time quotes/trades, Level 1/2 data, or WebSocket streaming.
- Intraday US stock candles.
- Portfolio accounting for dividends/splits beyond basic adjusted/unadjusted handling.

## Decisions

1) Provider abstraction
- Decision: Introduce a provider interface (e.g., `MarketDataProvider`) with `fetch_ohlcv(symbol, timeframe, since, until)`.
- Rationale: Enables adding paid providers later (Polygon, IBKR) without rewriting strategies.

2) Symbol mapping
- Decision: Keep user-facing symbols as common tickers (`AAPL`, `SPY`) and map to provider symbols (`aapl.us`) inside the Stooq provider.
- Alternative: Force users to type provider symbols directly.
- Rationale: Better UX and keeps provider-specific conventions isolated.

3) EOD-only enforcement
- Decision: The Stooq provider validates timeframe and rejects non-1D requests.
- Rationale: Prevents silently wrong backtests.

4) Caching
- Decision: Use existing caching capability (if present) or add a simple file/db cache keyed by `(source, symbol, timeframe)` with TTL tuned for EOD.
- Rationale: Improves reliability and prevents rate limiting.

5) Market calendar handling
- Decision: Treat EOD candles as discrete bars; do not attempt to fabricate missing days. Strategy computation uses available bars.
- Rationale: Minimizes complexity while staying correct.

## Risks / Trade-offs

- [Risk] Free sources can change or become unstable → Mitigation: caching, retries/backoff, clear error messages.
- [Risk] Corporate actions (splits/dividends) can impact returns → Mitigation: document that initial version focuses on raw OHLCV; add adjusted series later.
- [Risk] Mixing crypto (24/7) and stocks (market hours) in the same monitor can confuse users → Mitigation: add labels/filters by `asset_class` in UI if needed.

## Migration Plan

- Add provider code behind `data_source` defaulting to current crypto source.
- Deploy and verify crypto paths unchanged.
- Enable US stocks only when `data_source=stooq` and `timeframe=1d`.
- Rollback: revert provider additions; crypto pipeline remains intact.

## Open Questions

- Do we want adjusted close for Stooq by default (if available), or raw close?
- Should the monitor UI explicitly display the data source/asset class?
