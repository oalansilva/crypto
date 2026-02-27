# carteira-pnl-binance-avg-cost

## Status
- PO: in progress
- DEV: not started
- QA: not started
- Alan (Stakeholder): not reviewed

## Decisions (draft)
- Goal: Show Wallet PnL per asset based on Binance Spot avg buy cost.
- Scope: Binance Spot, USDT pairs only.
- Cost basis: buys-only weighted average; ignore sells (phase 1).
- Lookback: TBD (default: last 365 days) to limit API volume.
- Surface: `/external/balances` (Carteira).
- Persistence: none.

## Links
- OpenSpec viewer: http://72.60.150.140:5173/openspec/changes/carteira-pnl-binance-avg-cost/proposal
- PT-BR review (viewer): http://72.60.150.140:5173/openspec/changes/carteira-pnl-binance-avg-cost/review-ptbr

## Next actions
- [ ] PO: Confirm scope/assumptions (buys-only avg cost, USDT pairs only, lookback window) and lock acceptance.
- [ ] DEV: Implement myTrades avg cost + PnL fields on wallet endpoint + UI columns.
- [ ] QA: Add backend mock tests + Playwright E2E for PnL rendering.
- [ ] Alan: Review/approve scope; homologate UI after QA.
