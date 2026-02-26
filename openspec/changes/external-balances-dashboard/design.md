## Context

We already validated that a read-only Binance Spot API key works from the VPS. We now need to productize it into the app so balances can be viewed in the UI.

## Goals / Non-Goals

**Goals:**
- Backend endpoint that fetches Binance Spot balances using env-configured secrets.
- Frontend page that displays the snapshot.
- Minimal, safe, read-only integration.

**Non-Goals:**
- Trading, withdrawals, transfers.
- Historical P/L or trade history.
- Full portfolio valuation in USD (can be added later).

## Decisions

- Credentials are provided via server env vars (e.g., `BINANCE_API_KEY`, `BINANCE_API_SECRET`).
- Backend performs the Binance API call; frontend never sees secrets.
- UI shows balances sorted by asset; visually marks `locked` > 0.

## Risks / Trade-offs

- Secrets management: must keep keys out of git and logs.
- Rate limits: keep calls on-demand (no aggressive polling) and cache briefly if needed.
