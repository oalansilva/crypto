# carteira-pnl-binance-avg-cost

## Status
- PO: done
- DEV: in progress
- QA: not started
- Alan (Stakeholder): approved

## Decisions (locked)
- Goal: Show Wallet PnL per asset based on Binance Spot avg buy cost.
- Scope: Binance Spot, USDT pairs only.
- Cost basis: buys-only weighted average; ignore sells (phase 1).
- Surface: `/external/balances` (Carteira).
- Persistence: none.

## Links
- OpenSpec viewer: http://72.60.150.140:5173/openspec/changes/carteira-pnl-binance-avg-cost/proposal
- PT-BR review (viewer): http://72.60.150.140:5173/openspec/changes/carteira-pnl-binance-avg-cost/review-ptbr

## Next actions
- [x] PO: Done
- [ ] DEV: Implement avg cost + PnL via Binance myTrades and expose in Wallet endpoint
- [ ] QA: Add tests (backend + E2E)
- [ ] Alan: Homologate UI
