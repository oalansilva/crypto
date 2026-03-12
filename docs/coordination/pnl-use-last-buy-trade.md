# pnl-use-last-buy-trade

## Status
- PO: done
- DESIGN: skipped
- Alan approval: not reviewed
- DEV: not started
- QA: not started
- Alan homologation: not reviewed

## Decisions (draft)
- Rule confirmed by Alan: on `/external/balances`, PnL must use only the latest buy trade for each asset instead of averaging historical buys.
- No UI redesign is required; this is a behavioral/data-rule adjustment with normal DEV -> QA -> Alan homologation flow.

## Links
- Proposal: http://72.60.150.140:5173/openspec/changes/pnl-use-last-buy-trade/proposal
- Review PT-BR: http://72.60.150.140:5173/openspec/changes/pnl-use-last-buy-trade/review-ptbr
- Design: http://72.60.150.140:5173/openspec/changes/pnl-use-last-buy-trade/design
- Tasks: http://72.60.150.140:5173/openspec/changes/pnl-use-last-buy-trade/tasks

## Notes
- Coordination card created automatically in the same turn as the change.
- PO handoff correction 2026-03-12 12:34 UTC: review links were explicitly posted for Alan validation after the missing-card-links issue was caught. Root-cause rule updated in shared memory + PO memory: PO must publish review links in the card/comment thread in the same turn that planning is marked done.

## Next actions
- [x] PO: Elaborate proposal/spec/design/tasks.
- [ ] Alan: Review and approve the planning for `pnl-use-last-buy-trade`.
- [ ] DEV: Implement latest-buy-trade rule for PnL on `/external/balances`.
- [ ] QA: Validate PnL behavior and regression coverage.
