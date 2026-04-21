# mobile-pwa-kanban-mvp

## Status
- PO: done
- DESIGN: done
- Alan approval: approved
- DEV: done (mobile-only: hide global navbar on /kanban + add Filter/Sort row + improve column/card rendering/contrast; added mobile search toggle)
- QA: done (Playwright E2E 16/16; mobile viewports 390x844 + 412x915; desktop unchanged)
- Homologation: approved

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
- QA evidence (2026-02-28): screenshots mobile (Playwright headless) comparando **/kanban atual** vs **prototype aprovado**:
  - Artifacts: `docs/coordination/artifacts/mobile-pwa-kanban-mvp/`:
    - `current-kanban-390x844.png` vs `prototype-390x844.png`
    - `current-kanban-412x915.png` vs `prototype-412x915.png`
    - **Annotated diff (side-by-side):** `docs/coordination/artifacts/mobile-pwa-kanban-mvp/annotated-diff-390x844.png`
  - Mismatches objetivos observados (390x844 e 412x915):
    1) **Topbar / chrome:** no atual aparece a navbar global (“Crypto Backtester / Playground / Favorites…”) ocupando altura; no prototype é uma topbar minimalista (breadcrumb + botões Search/New em cards) sem a navbar global.
    2) **Controls sob o título:** no prototype existe linha de **Filter** + **Sort** logo abaixo do “Opportunity Board”; no atual essa linha não aparece.
    3) **Board/card container:** no prototype o board tem container arredondado e cards visíveis com espaçamento; no atual a área principal fica praticamente vazia (só headers de colunas aparecendo) e o hint de swipe tem estilo/posicionamento diferente (texto PT/sem pill como no prototype).
- @Alan @PO: pra eu destravar a homologação, preciso de **evidência do mismatch** vs o layout/prototype aprovado (mobile `/kanban`). Pode ser **(a)** 1 screenshot do mobile com 2–3 anotações (setas/círculos), **ou (b)** 2–3 bullets bem objetivos tipo:
  - topbar (breadcrumb / ações) deveria ser X
  - headers das colunas (tamanho/spacing/alinhamento) deveria ser Y
  - posição/visibilidade das ações deveria ser Z
  Cola a resposta **aqui nesta card** (seção Notes) ou manda um link/print.
  Obs: **desktop não mudou** — é só mobile.
- PO (2026-02-28): pra facilitar, compara com os prints já gerados em `docs/coordination/artifacts/mobile-pwa-kanban-mvp/`:
  - **Atual (mobile)**: `current-kanban-390x844.png` e `current-kanban-412x915.png`
  - **Prototype aprovado**: `prototype-390x844.png` e `prototype-412x915.png`
  Se você puder mandar **2–3 bullets objetivos** (ou **um print anotado**) apontando exatamente *o que ainda está diferente* do prototype, eu destravo a homologação.
- PO follow-up (2026-02-28): reiterated the request above; blocked pending Alan’s 2–3 bullets or annotated screenshot.
- PO evidence (2026-02-28): **annotated mismatch** (current vs approved prototype) — see `docs/coordination/artifacts/mobile-pwa-kanban-mvp/po-annotated-diff-390x844.png`.
  - Remaining mismatches highlighted:
    1) **Topbar/chrome height:** current still shows the global navbar/chrome (too tall) vs the prototype’s minimal topbar.
    2) **Missing Filter/Sort row:** prototype has Filter + Sort controls under “Opportunity Board”; current does not.
    3) **Board/cards visibility:** prototype shows cards inside the column container; current board area looks mostly empty.
  - @Alan: confirma se esses 3 pontos são exatamente o que você quer ver ajustado pra homologar.
- PO reply (2026-02-28): @Alan, consegue **confirmar se esses 3 mismatch points** (Topbar/chrome height; falta Filter/Sort; board/cards quase vazio vs prototype) são exatamente o que você quer ver ajustado? Com esse OK eu consigo destravar a homologação.
- PO (2026-02-28): @Alan — responde **“OK”** se os 3 pontos (1 topbar sem navbar global, 2 Filter+Sort, 3 cards visíveis) são exatamente o alvo; ou **Yes/No por item**. Aí eu destravar a homologação.
- DEV note (2026-02-28): mobile-only em /kanban alinhado ao prototype: AppNav escondido no mobile; topbar minimal; linha Filter+Sort; colunas/+cards com container e contraste (evita “board vazio”); search toggle abre Localizar.
- QA re-run (2026-02-28): Playwright E2E suite OK (16/16). Fix aplicado no kanban-loads ("Detalhes" agora usa exact:true para evitar strict locator com o swipe hint).
- Mobile check (390x844 + 412x915): topbar OK, swipe hint visible, no page-level horizontal overflow.
- Sticky headers: verificado via Playwright (Chromium) em 390x844: topbar e header da coluna com computed style `position: sticky` e permanecem fixos no scroll vertical. Obs: em >=640px (sm+) o header da coluna fica `position: static` por design (`sm:static`).
- Desktop (1280x800): board renders as before; swipe hint not shown; no horizontal overflow.
- @PO reply (2026-02-28): PO/DEV/QA **já concluíram**. Único passo pendente é **homologação do Alan** (confirmação final / “OK”). Se ainda houver algo diferente vs o prototype aprovado, por favor lista **2–3 bullets objetivos** ou manda **1 print anotado** aqui.

## Closed

- Homologated by Alan and archived.

## Next actions
- [ ] Alan: Homologate / confirm (reply **OK**, or Yes/No per item if anything still differs vs the approved prototype).
- [x] PO: Provided self-contained evidence + asked for final confirmation.
- [x] DEV: Adjust `/kanban` mobile UI to match the approved layout (then re-run QA).
- [x] QA: Re-validate on mobile + confirm desktop unchanged. (E2E suite green; sticky OK em viewport mobile; desktop unchanged)
