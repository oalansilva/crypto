# pnl-use-last-buy-trade

## Status
- PO: done
- DESIGN: skipped
- Alan approval: approved
- DEV: done
- QA: done
- Alan homologation: approved


## Closed

- Homologated by Alan and archived.

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
- Tracking reconciliation 2026-03-12 18:43 UTC: Alan approval was already recorded in the workflow runtime, and DEV + QA had already completed with QA PASS, but this coordination file had not been updated. File status reconciled to match the runtime/Kanban source of truth; next step is Alan homologation.
- Alan homologation 2026-03-12 18:46 UTC: approved in chat. Coordination/runtime prepared for immediate close + archive in the same turn.

## Next actions
- [x] PO: Elaborate proposal/spec/design/tasks.
- [x] Alan: Review and approve the planning for `pnl-use-last-buy-trade`.
- [x] DEV: Implement latest-buy-trade rule for PnL on `/external/balances`.
- [x] QA: Validate PnL behavior and regression coverage.
- [x] Alan: Homologate `pnl-use-last-buy-trade` so it can be closed and archived.
