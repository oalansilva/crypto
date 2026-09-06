## 1. Catálogo e helper

- [x] 1.1 Em `scripts/process-fsm/route-landmarks.yaml`, semear chave `landing` com `kind: public`, `live_url`, `source`, selectors `.faq-section` / `.button-primary` e texts h1/FAQ/CTA (D1). Manter as quatro rotas `/` autenticadas; default `kind: authenticated` quando a chave começa por `/`
- [x] 1.2 Em `scripts/process-fsm/design_clone_gate.py`: substituir `concatenate_proto_html` por `canonical_proto_html` (só `index.html`; fallback = exactamente um `*.html`); alargar `LIVE_ROUTE_RE` para `(\/\S+|landing|N/A)`; `routes_from_catalog` incluir `kind: public`; `requires_existing_clone` / `is_new_exempt` tratarem `landing`; remover early-return incondicional de `UI impact: none` (D5–D6)
- [x] 1.3 Materializar fixtures `scripts/process-fsm/fixtures/790-panel-index.html` e `790-sibling-landing-clone.html` (D7). Opcional `v4-landing-clone.html`. MUST NOT escrever em `frontend/public/prototypes/card-790-copy-spot/**`

## 2. Testes

- [x] 2.1 `scripts/process-fsm/test_design_clone_gate.py`: catálogo 4 chaves `/` + `landing`; painel-index + sibling clone FAIL contra `landing`; clone v4 como `index.html` PASS (não por path 790); UI none harness (`N/A` + `surface: new`, sem proto) PASS; `surface: existing` / `live_route: landing` sem proto FAIL; UI none + existing recusa
- [x] 2.2 `scripts/process-fsm/test_process_event.py`: T5 UI none harness transita; T5 recusa painel + sibling com `live_route: landing`; T5 recusa existing sem proto. `pytest scripts/process-fsm -q` verde. Sem Playwright dentro de T5

## 3. Skills

- [x] 3.1 Em `.agents/skills/design-critic/SKILL.md`, colar o briefing D3 (clone da página viva autenticada **ou** HTML público `landing`; nunca «6 estados» / painel ANTES/DEPOIS como URL canónico; copy visível ⇒ proto obrigatório). Substituir a operacionalização só-rotas-autenticadas (L16/L63)
- [x] 3.2 Em `.cursor/skills/covenant-flow/SKILL.md` (coluna Design), o mesmo briefing D3. MUST NOT dual-write lei em `.dsh/` nem `.grok/`

## 4. Fora de escopo (confirmação)

- [x] 4.1 Diff deste card sem `backend/`, `frontend/src/`, proto live #790/#792/#799, `DESIGN.md`, `.cursor/process-fsm.yaml` Σ, `CONTEXT.md`, `docs/adr/`
- [x] 4.2 `openspec validate --change card-819-clone-pagina-viva` verde; `UI impact: none` — zero HTML de protótipo de produto deste card
