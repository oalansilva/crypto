# mobile-pwa-kanban-mvp

## Status
- PO: done
- DESIGN: done
- Alan approval: approved
- DEV: done (mobile layout delta applied: topbar + sticky headers + hint)
- QA: pending re-run (after mobile layout adjustment)
- Alan homologation: reviewed (not approved: layout mismatch; target: match prototype layout while keeping current content)

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

## Notes
- Alan feedback (2026-02-28): “Não vi diferença e não está no layout aprovado”.
- DEV note (2026-02-28): ajuste mobile-only em /kanban para ficar alinhado ao prototype aprovado: topbar (breadcrumb + actions), headers das colunas sticky (offset do topbar) e hint de swipe.
- QA validated build/E2E, but UX approval is blocked until we align implementation with the approved mobile prototype expectations.

## Next actions
- [ ] Alan: Point what exactly is missing vs the approved layout (2–3 bullets or a screenshot).
- [ ] DESIGN: Translate the approved prototype into a minimal delta plan against current `/kanban` UI (what must change; what must stay).
- [x] DEV: Adjust `/kanban` mobile UI to match the approved layout (then re-run QA).
- [ ] QA: Re-validate on mobile + confirm desktop unchanged.
- [ ] Alan: Homologate (after fixes).
