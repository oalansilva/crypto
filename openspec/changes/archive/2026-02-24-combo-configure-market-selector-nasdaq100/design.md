## Context

Combo Configure currently assumes crypto symbols and timeframes and relies on the backend’s default data source. The backend already supports a free US stocks EOD provider (Stooq) via `data_source=stooq` with a hard constraint of `timeframe=1d`. We want to expose this choice in the Combo Configure UI while keeping the rest of the system unchanged.

## Goals / Non-Goals

**Goals:**
- Add a market selector to Combo Configure: `crypto` (default) and `us-stocks`.
- For `us-stocks`: show NASDAQ-100 tickers, force timeframe `1d`, and include `data_source=stooq` in requests.
- Preserve existing crypto behavior when `crypto` is selected.

**Non-Goals:**
- Intraday US stock timeframes.
- Automatically updating NASDAQ-100 membership from the web.
- Any changes to strategy logic or scoring (only data source selection).

## Decisions

- Store NASDAQ-100 tickers in a versioned file under `backend/config/` and expose them via a small API endpoint.
- Enforce `timeframe=1d` in the UI when `us-stocks` is selected to avoid invalid requests.

## Risks / Trade-offs

- [Risk] NASDAQ-100 list becomes stale → Mitigation: periodic manual update.
- [Risk] Some tickers have missing EOD data → Mitigation: surface provider errors clearly and allow users to choose different tickers.
