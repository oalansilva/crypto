## Context

Combo Optimize currently assumes crypto symbols and timeframes, and uses the backend’s default data source (ccxt/Binance-style). The backend now supports a free US stocks EOD provider (Stooq) via `data_source=stooq` with a hard constraint of `timeframe=1d`. We want to expose this in the UI with a simple market selector and a NASDAQ-100 symbol universe.

## Goals / Non-Goals

**Goals:**
- Add a market selector to Combo Optimize: `crypto` (default) and `us-stocks`.
- When `us-stocks` is selected: show NASDAQ-100 tickers, force timeframe `1d`, and submit requests with `data_source=stooq`.
- Keep existing crypto UX and API calls unchanged when `crypto` is selected.

**Non-Goals:**
- Intraday US stock timeframes.
- Automatically updating NASDAQ-100 membership from the web.
- Expanding this selector to other pages (only Combo Optimize in this change).

## Decisions

1) Universe source
- Store NASDAQ-100 tickers in a versioned file under `backend/config/` (or similar) and expose via a small API endpoint.
- Rationale: stable, reviewable, and works without paid data.

2) UI enforcement for timeframe
- When `us-stocks` is selected, lock the timeframe UI to `1d` (disable other options) and show a hint.
- Rationale: prevents invalid requests and matches backend constraints.

3) Backward compatibility
- Default market is `crypto` and requests do not include `data_source`.
- Rationale: zero behavior change for current users.

## Risks / Trade-offs

- [Risk] NASDAQ-100 list becomes outdated over time → Mitigation: explicit periodic update task; keep list versioned.
- [Risk] Some tickers may not exist in Stooq format or have missing data → Mitigation: handle provider errors gracefully and allow filtering/removing tickers.
- [Risk] UI complexity increases → Mitigation: minimal toggle + clear labels.

## Migration Plan

- Add NASDAQ-100 universe endpoint + config file.
- Update Combo Optimize UI to switch symbol lists and request payload.
- Deploy; verify crypto flow unchanged.
- Rollback: revert UI toggle and endpoint; backend still supports stooq but is unused.

## Open Questions

- Do we want to display market labels in Favorites/Monitor later, or keep this only in Combo Optimize?
