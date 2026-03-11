# mobile-kanban-ui-rethink

## Status
- PO: done
- DESIGN: done
- Alan approval: approved
- DEV: done
- QA: done
- Alan homologation: approved


## Closed

- Homologated by Alan and archived.

## Decisions (draft)
- Change driven by Alan's detailed mobile Kanban briefing.
- Mobile should show one stage at a time.
- Stage switching should support swipe and tabs.
- Cards and detail view should be redesigned for touch-first use.
- Desktop scope boundary is already defined in the change: this redesign is mobile-only for this change, and desktop is explicitly out of scope.
- Alan approved the delivered DESIGN prototype in chat; DEV completed implementation, QA validated the delivery, and the change is now awaiting Alan homologation.

## Links
- Proposal: http://72.60.150.140:5173/openspec/changes/mobile-kanban-ui-rethink/proposal
- Review PT-BR: http://72.60.150.140:5173/openspec/changes/mobile-kanban-ui-rethink/review-ptbr
- Prototype: http://72.60.150.140:5173/prototypes/mobile-kanban-ui-rethink/index.html

## Notes
- Alan supplied a detailed mobile-first briefing for Kanban.
- This is a product/UI redesign proposal, approved to proceed into the DESIGN stage.
- DESIGN prototype delivered with: fixed header, fixed filter bar, swipe + tabs (one stage at a time), mobile cards, FAB, and full-screen bottom sheet task detail + filters sheet.
- Alan approved the prototype in chat; PO reconciled runtime workflow tracking and handed off to DEV.
- Workflow DB seeding had to be run manually once after creation; future creation should become automatic.
- DEV implemented the mobile-only stage tabs/header/filter shell, one-stage rendering, swipe gesture for stage change, redesigned mobile cards, and a full-screen mobile detail sheet in `frontend/src/pages/KanbanPage.tsx` while preserving the desktop board path.
- DEV also added a basic performance guardrail by rendering only the active mobile stage instead of all columns on small screens, and updated the Playwright Kanban smoke test to exercise the mobile tab/sheet flow.
- DEV finished the remaining mobile move flow: long-press on a mobile card now opens a move sheet and patches the real workflow change status through `/api/workflow/projects/crypto/changes/:id`, then refreshes the DB-backed Kanban state. This preserves desktop unchanged while making mobile card moves real instead of static.
- QA 2026-03-11: runtime tracking was reconciled before validation (workflow DB/Kanban and OpenSpec agreed on column `QA`, gate states `PO/DESIGN/Alan approval/DEV=approved`, QA pending, Alan homologation pending).
- Historical blocker 2026-03-11: mobile stage navigation initially bounced away from empty stages; DEV fixed this by stopping the post-init auto-reset of `activeMobileColumn` in `frontend/src/pages/KanbanPage.tsx`.
- QA pass 2026-03-11 (runtime Playwright against `http://127.0.0.1:5173/kanban` + live workflow API): tapping mobile tab `DEV 0` stayed on `DEV` and showed `Nenhum card nesta etapa.`; detail sheet opened full-screen on mobile (`aside` bbox matched viewport at `390x844`); long-press opened the move sheet, move to `Alan homologation` persisted via workflow PATCH and rendered the card there, then QA reverted the change back to `QA` to preserve runtime tracking.
- QA desktop non-regression 2026-03-11: desktop Kanban header/board still rendered and the detail drawer remained right-sided instead of full-screen (`aside` bbox `520x900` at the right edge on `1440x900`).
- QA performance note 2026-03-11: no obvious quick regression seen during runtime validation, and the implemented guardrail is real — on mobile the page renders only the active stage column instead of all columns, which is an appropriate fast-path for realistic board sizes.
- DEV smoke 2026-03-11: updated `frontend/tests/e2e/kanban-loads.spec.ts` to assert that tapping mobile tab `DEV 0` keeps the board on the empty DEV stage and shows the empty-state message; targeted Playwright smoke passed.

## Next actions
- [x] PO: Formalize the mobile Kanban UI rethink proposal from Alan's briefing.
- [x] DESIGN: Build prototype for Alan review.
- [x] Alan: Review prototype and approve before DEV.
- [x] DEV: Finish the remaining move interaction work (long-press drag / real card move flow) for the mobile redesign.
- [x] QA: Validate after DEV handoff, with emphasis on mobile swipe/tabs, detail sheet, move flow, and desktop non-regression.

## Handoff
- PO reconciled tracking after QA closeout: QA is complete, the runtime handoff moves from `QA` to `Alan homologation`, and gate states now read `PO/DESIGN/Alan approval/DEV/QA=approved`, `Alan homologation=pending`.
- Acceptance evidence: mobile tabs can stay on empty stages, swipe no longer bounces away from empty stages, the mobile detail sheet is still full-screen, and the long-press move flow persists through the workflow API.
- Desktop path did not regress in quick validation, and the targeted Playwright smoke test still passes.
- Next step: @Alan homologar em runtime; sem novo trabalho de produto pendente antes disso.
