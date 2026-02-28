# mobile-pwa-kanban-mvp

## Status
- PO: done
- DESIGN: done
- Alan approval: approved
- DEV: done (mobile layout delta applied: topbar + sticky headers + hint)
- QA: done (E2E unflaked; sticky headers OK em viewport mobile <640px; desktop unchanged)
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
- QA re-run (2026-02-28): Playwright E2E suite OK (16/16). Fix aplicado no kanban-loads ("Detalhes" agora usa exact:true para evitar strict locator com o swipe hint).
- Mobile check (390x844 + 412x915): topbar OK, swipe hint visible, no page-level horizontal overflow.
- Sticky headers: verificado via Playwright (Chromium) em 390x844: topbar e header da coluna com computed style `position: sticky` e permanecem fixos no scroll vertical. Obs: em >=640px (sm+) o header da coluna fica `position: static` por design (`sm:static`).
- Desktop (1280x800): board renders as before; swipe hint not shown; no horizontal overflow.

## Next actions
- [ ] Alan: Point what exactly is missing vs the approved layout (2–3 bullets or a screenshot).
- [ ] PO: Follow up with Alan requesting the missing-vs-approved bullets/screenshot so we can close homologation.
- [ ] DESIGN: Translate the approved prototype into a minimal delta plan against current `/kanban` UI (what must change; what must stay).
- [x] DEV: Adjust `/kanban` mobile UI to match the approved layout (then re-run QA).
- [x] QA: Re-validate on mobile + confirm desktop unchanged. (E2E suite green; sticky OK em viewport mobile; desktop unchanged)
- [ ] Alan: Homologate (after fixes).
