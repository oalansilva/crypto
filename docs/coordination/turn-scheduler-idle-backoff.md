# turn-scheduler-idle-backoff

## Status
- PO: in progress
- DEV: not started
- QA: not started
- Alan (Stakeholder): not reviewed

> Gate order: PO must be **done** before Alan approves to implement.

## Decisions (locked)
- Goal: Reduce Turn Scheduler executions when there are **no active OpenSpec changes**.
- Surface (mobile/desktop): N/A (ops-only).
- Defaults: Normal cadence remains 15m when active changes exist.
- Persistence: N/A.
- Performance limits: Keep controller lightweight and idempotent.
- Non-goals: Changing PO/DEV/QA selection algorithm.

## Links
- OpenSpec viewer: http://72.60.150.140:5173/openspec/changes/turn-scheduler-idle-backoff/proposal
- PT-BR review (viewer): http://72.60.150.140:5173/openspec/changes/turn-scheduler-idle-backoff/review-ptbr
- PR: (none)
- CI run: (n/a)

## Notes
- Change introduces an idle/backoff mode for the OpenClaw Turn Scheduler cron.

## Next actions
- [ ] PO: Confirm desired idle behavior + target idle interval (e.g., 1h vs 4h) and whether to disable or just slow cadence.
- [ ] DEV: Implement the controller and update cron schedule idempotently.
- [ ] QA: Validate schedule changes in both idle and active-change scenarios.
- [ ] Alan: Review/approve proposed idle/backoff behavior.
