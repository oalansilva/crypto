# carteira-pnl-binance-avg-cost

## Status
- PO: done
- DEV: done
- QA: unblocked (needs regression pass after DEV safeguards)
- Alan (Stakeholder): approved

> Gate order: PO must be **done** before Alan approves to implement.

## Decisions (locked)
- Goal: Show Wallet PnL per asset based on Binance Spot avg buy cost.
- Scope: Binance Spot, USDT pairs only.
- Cost basis: buys-only weighted average; ignore sells (phase 1).
- Lookback: Default 365 days to limit API volume.
- Surface: `/external/balances` (Carteira).
- Persistence: none.

## Backend safeguards (implemented)
- HTTP timeouts (env `BINANCE_HTTP_TIMEOUT_SECONDS`, clamped)
- Max symbols per request with trade-history lookups (env `BINANCE_MAX_TRADE_SYMBOLS`)
- Total time budget for trade-history lookups (env `BINANCE_TRADE_LOOKUPS_BUDGET_SECONDS`)
- Optional lookback window for avg cost via query param: `GET /api/external/binance/spot/balances?lookback_days=365`

## Required Binance API key permissions
- Enable **Reading** (required for `/api/v3/account` and general account endpoints)
- Enable **Spot & Margin Trading** (Binance requirement to access Spot trade history via `/api/v3/myTrades`)
- Do **NOT** enable withdrawals; futures not required
- Recommended: IP whitelist the server and keep key read-only where possible

## Links
- OpenSpec viewer: http://72.60.150.140:5173/openspec/changes/carteira-pnl-binance-avg-cost/proposal
- PT-BR review (viewer): http://72.60.150.140:5173/openspec/changes/carteira-pnl-binance-avg-cost/review-ptbr

## Next actions
- [x] PO: Confirm scope/assumptions (buys-only avg cost, USDT pairs only, lookback window) and lock acceptance.
- [x] DEV: Implement myTrades avg cost + PnL fields on wallet endpoint + UI columns.
- [x] QA: Regression pass covering safeguards (max symbols/time budget + lookback_days param).
- [ ] Alan: Homologate UI (Carteira PnL)
