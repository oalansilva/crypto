# monitor-dark-green-theme

## Status
- PO: in progress
- DEV: not started
- QA: not started
- Alan (Stakeholder): not reviewed

## Decisions (locked)
- Goal: Change Monitor palette from black to dark green (aesthetic refresh).
- Surface (mobile/desktop): Monitor only (mobile-first).
- Defaults: Default theme = dark-green.
- Persistence: Save in backend (per Alan).
- Performance limits: No impact expected; must not reduce contrast/readability.
- Non-goals: Full site theming; only /monitor.

## Links
- OpenSpec viewer: http://72.60.150.140:5173/openspec/changes/monitor-dark-green-theme/proposal
- PT-BR review (viewer): http://72.60.150.140:5173/openspec/changes/monitor-dark-green-theme/review-ptbr
- PR: (pending)
- CI run: (pending)

## Notes
- OpenSpec change artifacts already present under `openspec/changes/monitor-dark-green-theme/` (proposal/design/specs/tasks + PT-BR review).
- Acceptance criteria captured in OpenSpec specs:
  - Default theme = `dark-green` when no preference exists.
  - Theme persists across reload/devices.
  - `/monitor` background is dark-green (not pure black) and readability preserved.

## Next actions
- [x] PO: Create OpenSpec change artifacts (EN) + review-ptbr + viewer links; lock acceptance criteria.
- [ ] DEV: Implement Monitor dark-green theme + backend preference persistence.
- [ ] QA: Add/update tests (E2E visual smoke + preference persistence) and ensure CI green.
- [ ] Alan: Review artifacts and approve to implement; final homologation after QA.
