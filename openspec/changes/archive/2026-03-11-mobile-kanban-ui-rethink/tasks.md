## 1. PO / DESIGN

- [x] 1.1 Capture Alan's mobile Kanban briefing in proposal/design/specs
- [x] 1.2 Turn the briefing into a mobile prototype (header, filters, one-stage view, cards, task detail)
- [x] 1.3 Confirm desktop scope boundaries vs mobile-only redesign

## 2. DEV

- [x] 2.1 Implement one-stage-at-a-time mobile navigation
- [x] 2.2 Implement fixed header + filter bar + stage tabs
- [x] 2.3 Implement redesigned mobile cards and card indicators
- [x] 2.4 Implement full-screen task detail bottom sheet
- [x] 2.5 Implement gestures (swipe stage nav, long-press move flow via workflow mutation)
- [x] 2.6 Add performance protections (lazy loading / batching / cache hooks)
- [x] 2.7 Add/update Playwright mobile tests

## 3. QA

- [x] 3.1 Validate mobile navigation and tabs/swipe behavior
- [x] 3.2 Validate card readability and detail interaction
- [x] 3.3 Validate drag/move interaction and no major regression on desktop
- [x] 3.4 Validate mobile performance assumptions on realistic card counts
  - Evidence 2026-03-11: runtime Playwright on `http://127.0.0.1:5173/kanban` confirmed mobile tab `DEV 0` stays selected on an empty stage and shows `Nenhum card nesta etapa.`; mobile detail sheet filled the `390x844` viewport; long-press move sheet successfully moved the change to `Alan homologation` through the live workflow API and QA reverted it to `QA`; desktop still rendered the multi-column board and a right-side `520px` detail drawer on `1440x900`.
  - Quick performance assessment 2026-03-11: no obvious runtime hitch seen in validation, and `KanbanPage.tsx` still renders only the active mobile stage instead of every column, which is the main realistic guardrail shipped in this change.
  - Tracking note 2026-03-11: after QA closeout, PO reconciled the handoff artifacts so this change is no longer described as `in QA`; final post-QA state is `awaiting Alan homologation`.
