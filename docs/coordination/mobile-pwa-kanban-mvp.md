# mobile-pwa-kanban-mvp

## Status
- PO: done
- DESIGN: done
- Alan approval: approved
- DEV: not started
- QA: not started
- Alan homologation: not reviewed

## Decisions (draft)
- Scope: MVP for mobile only, focused on `/kanban`.
- PC layout must remain unchanged.
- DESIGN will provide an HTML/CSS prototype under `frontend/public/prototypes/mobile-pwa-kanban-mvp/`.

## Acceptance Criteria (PO locked)
- **Mobile-only scope:** Changes must target mobile viewport behavior/UX for `/kanban` only.
- **PC unchanged:** Desktop/PC layout and interactions for `/kanban` must remain unchanged (no visual/layout regressions).
- **Route scope:** No changes required/expected outside `/kanban` (unless strictly necessary for PWA installability).
- **PWA installability (MVP):**
  - App must be installable as a PWA on mobile (Add to Home Screen).
  - After install, launching from the icon must open the app without obvious browser chrome (standalone display).
  - No requirement for offline support in this MVP (unless Alan explicitly wants it).
- **Validation:** QA must validate at least on common mobile viewport sizes (e.g., iPhone + Android) and confirm desktop unchanged.

## Open questions for Alan
1) For this MVP, do you want **offline support** (cached `/kanban`) or is **installable only** enough?
2) Any minimum devices/browsers you care about for validation (iOS Safari / Android Chrome)?

## Links
- Review PT-BR: http://72.60.150.140:5173/openspec/changes/mobile-pwa-kanban-mvp/review-ptbr
- Proposal: http://72.60.150.140:5173/openspec/changes/mobile-pwa-kanban-mvp/proposal
- Prototype (when ready): http://72.60.150.140:5173/prototypes/mobile-pwa-kanban-mvp/index.html

## Next actions
- [x] PO: Lock acceptance criteria and mobile-only constraints.
- [ ] DESIGN: Create prototype for mobile Kanban.
- [ ] Alan: Approve scope + prototype (and answer open questions above).
- [ ] DEV: Implement mobile-only Kanban improvements + PWA installability.
- [ ] QA: Validate on mobile viewport.
