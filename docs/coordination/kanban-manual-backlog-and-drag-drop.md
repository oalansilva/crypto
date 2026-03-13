# kanban-manual-backlog-and-drag-drop

## Status
- PO: done
- DESIGN: done
- Alan approval: approved
- DEV: done
- QA: done
- Alan homologation: pending

## Decisions
- `Pending` becomes a first-class pre-PO runtime/Kanban column.
- New cards can be created directly from `/kanban` with title + optional short description.
- Desktop uses drag-and-drop; mobile keeps the current move flow, both backed by the same runtime transition path.
- Runtime/Kanban is the operational source of truth for newly created `Pending` cards.
- OpenSpec artifacts for intake cards are created/updated when PO pulls a card from `Pending` into `PO`, not at raw backlog intake time.

## Links
- Proposal: http://72.60.150.140:5173/openspec/changes/kanban-manual-backlog-and-drag-drop/proposal
- Design: http://72.60.150.140:5173/openspec/changes/kanban-manual-backlog-and-drag-drop/design
- Review PT-BR: http://72.60.150.140:5173/openspec/changes/kanban-manual-backlog-and-drag-drop/review-ptbr
- Tasks: http://72.60.150.140:5173/openspec/changes/kanban-manual-backlog-and-drag-drop/tasks

## Notes
- Coordination card created automatically in the same turn as the change.
- Reconciled DESIGN from `skipped` to `done`: the change already has a design artifact at `openspec/changes/kanban-manual-backlog-and-drag-drop/design.md`, and this artifact now explicitly covers create-card UX, desktop drag-and-drop UX, and mobile move-flow behavior.
- Tracking reconciliation 2026-03-12 22:57 UTC: Alan approval was already recorded in the workflow runtime/Kanban (`approved`, chat + approval record), while this coordination card still showed `not reviewed`. Card status updated to match runtime; DEV/QA tracking stays pending here until their runtime handoffs are explicitly reconciled in a dedicated turn.
- DEV 2026-03-12 23:16 UTC: implemented Pending-first Kanban intake and shared move flow end-to-end. Backend now supports Pending create + structured move validation errors, frontend Kanban shows Pending first, creates cards inline, refreshes after create/move, and desktop drag/drop/mobile move use the same runtime transition path. Validation covered by `backend/tests/integration/test_workflow_kanban_manual_backlog.py` and `frontend/tests/e2e/kanban-manual-backlog-and-drag-drop.spec.ts`.
- QA handoff: validate real runtime behavior in the app for (1) create card into Pending, (2) desktop drag/drop respecting gate-by-gate forward moves plus backward rework moves, (3) mobile long-press move sheet using the same backend path, and (4) actionable 409 errors for invalid jumps.
- QA 2026-03-12 23:30 UTC: targeted backend integration test passed (`backend/tests/integration/test_workflow_kanban_manual_backlog.py`, 3 passed), targeted frontend E2E passed (`frontend/tests/e2e/kanban-manual-backlog-and-drag-drop.spec.ts`), and runtime Playwright revalidation passed for desktop drag/drop persistence plus mobile long-press move parity (`frontend/qa_revalidate_kanban_dnd.mjs`, evidence in `qa_artifacts/playwright/kanban-manual-backlog-and-drag-drop-revalidation/`).
- QA blocker 2026-03-12 23:30 UTC: create-card into Pending works in the running `/kanban` UI (`qa-pending-card-1773358162264` created successfully), but the running backend at `127.0.0.1:8003` did **not** return the expected actionable `409` for an invalid jump. The same runtime accepted `PATCH /api/workflow/projects/crypto/changes/qa-pending-card-1773358162264 {"status":"DEV"}` with `200 OK`, moving the card directly from `Pending` to `DEV` instead of rejecting it. Evidence: `qa_artifacts/runtime/kanban-manual-backlog-and-drag-drop/invalid-pending-to-dev-response.txt` and `qa_artifacts/runtime/kanban-manual-backlog-and-drag-drop/board-after-create-and-invalid-move.json`.
- DEV runtime reconciliation 2026-03-12 23:43 UTC: root cause was stale uvicorn/runtime code on `:8003`, not missing guard logic in the repository. Local code path and tests already rejected `Pending -> DEV`; restarting with `./stop.sh && ./start.sh` brought the running backend back in sync. Revalidation against the live runtime now returns actionable `409` for fresh invalid `Pending -> DEV` moves, matching the documented guard rails. Evidence: `qa_artifacts/runtime/kanban-manual-backlog-and-drag-drop/invalid-pending-to-dev-after-restart.json` and `qa_artifacts/runtime/kanban-manual-backlog-and-drag-drop/board-after-runtime-fix.json`.
- QA handoff 2026-03-12 23:43 UTC: blocker cleared; change is ready for QA to re-run the runtime invalid-jump check plus the already-passed create/move flows on the refreshed app.
- QA runtime recheck 2026-03-12 23:58 UTC: **PASS** for the live invalid-jump guard. Fresh runtime card `qa-pending-card-runtime-recheck-pending-1773359905` on the running backend rejected `Pending -> DEV` with actionable HTTP `409` and `allowed_targets=["PO"]`, matching the documented guard rails. Clickable evidence: response http://72.60.150.140:5173/qa-artifacts/runtime/kanban-manual-backlog-and-drag-drop/live-recheck-invalid-pending-to-dev-live.json | create result http://72.60.150.140:5173/qa-artifacts/runtime/kanban-manual-backlog-and-drag-drop/live-recheck-create-pending.json | metadata http://72.60.150.140:5173/qa-artifacts/runtime/kanban-manual-backlog-and-drag-drop/live-recheck-metadata-pending.json | board snapshot http://72.60.150.140:5173/qa-artifacts/runtime/kanban-manual-backlog-and-drag-drop/live-recheck-board-pending.json.
- QA reconciliation 2026-03-12 23:59 UTC: product blocker is cleared, but the change could **not** be promoted from `DEV` to `Alan homologation` in runtime/Kanban yet because the upstream publish guard still fails for this repo state (`./scripts/verify_upstream_published.py --for-status "Alan homologation"`). Registered runtime work item `bug` `9769f19b-9b55-4844-b5e6-8bbd17e5f8db` (`Publish/reconcile change before promoting to Alan homologation`) and handed off to DEV/owner for publish-reconciliation. Until that guard passes, runtime source of truth remains `DEV` even though QA evidence is now green.
- DEV publish reconciliation 2026-03-13 00:10 UTC: root cause of the remaining publish block was simply that the delivery for this change still existed only as local tracked/untracked repo work. The actual guard failure was cleared by committing/pushing the real implementation/test/docs files for this change (`fd42480`, `origin/main`) and discarding only local scratch artifacts. After publish, `./scripts/verify_upstream_published.py --for-status "Alan homologation"` returned `OK` and the runtime/Kanban item now reads `PO/DESIGN/Alan approval/DEV/QA=approved`, `Alan homologation=pending`, column `Alan homologation`.
- Handoff 2026-03-13 00:10 UTC: DEV unblock is complete. Change is now waiting only for Alan homologation; no further DEV/QA action is required unless Alan requests follow-up.

## Next actions
- [x] DEV: Implement Pending intake, shared move transitions, desktop drag-and-drop, and board auto-refresh after approval.
- [x] QA: Validate Pending creation, desktop drag/drop, mobile move parity, invalid-jump errors, and runtime synchronization after DEV.
- [x] DEV: reconcile the running backend/runtime so invalid Kanban jumps return the documented actionable `409` payload in practice, not only in tests/code.
- [x] QA: re-run the runtime invalid-jump check on the refreshed app and confirm the live `409` behavior holds.
- [ ] Alan: homologate the delivered Pending-first Kanban flow now that runtime/Kanban is already sitting in `Alan homologation` with QA evidence attached.
