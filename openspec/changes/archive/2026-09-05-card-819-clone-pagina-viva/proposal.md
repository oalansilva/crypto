## Why

Alan no T7 não consegue julgar a página como vai ficar: em superfície já existente o Design salta o protótipo («copy-only» / `UI impact: none` skip) ou entrega um painel ANTES/DEPOIS, e a aprovação gasta-se a olhar um mock — ou a reaprovar porque o clone chegou tarde. Recidiva #799, evidência live #790 (index-painel + `landing.html` clone na mesma pasta; URL canónico = directory index).

## What Changes

- O URL canónico do proto (`…/prototypes/<slug>/` → `index.html`) MUST ser a **página viva + delta**, não um painel ANTES/DEPOIS nem uma galeria de estados. Clone noutro ficheiro da pasta **não** conta.
- Superfície já existente inclui rota autenticada **e** HTML público vigente (landing v4). Copy visível (landing / Ajuda / Perfil) = a página mudou; Prototype N/A é recusado.
- Q4=A: o Design **não** chega à aprovação se o proto de superfície existente for painel/galeria, ou se copy visível vier sem proto.
- Catálogo semeia a landing pública (chave não autenticada) sem tratar HTML público como rota `/monitor`. Fail-closed: declarar landing/copy sem a chave continua a recusar.
- T5 mede **só** o `index.html` canónico (não concatenar `*.html` da pasta). Extra clones = URLs extra no comentário; T5 não os mede.
- Briefing do Design-autor (Cursor `design-critic` e covenant-flow que o dsh também lê): clonar a página viva, nunca «6 estados» / painel ANTES/DEPOIS.
- N superfícies existentes: URL principal = página primária clonada; extras à parte — nunca um painel das N no index.
- **BREAKING** para o predicado `G_design`: `UI impact: none` deixa de skippar o gate quando `surface: existing` ou `live_route` é chave de catálogo; painel-index + clone-irmão MUST falhar; UI none harness (sem proto, `live_route: N/A`, `surface: new`) continua a passar.

Não é BREAKING para produto: nenhuma rota, shell ou copy de Cripto muda. Não reabre HTML publicado do #790 / #792 / #799 como Apply.

## Capabilities

### New Capabilities

- (nenhuma)

### Modified Capabilities

- `design-route-clone-gate`: UI none harness (sem proto, `N/A` / `surface: new`) ainda passa; copy visível / superfície existente não skippa; leitura canónica `index.html`; chave pública `landing` com `kind: public`; painel #790 + sibling clone falha; clone v4 não falha por path #790.
- `impeccable-design-gate`: superfície existente inclui HTML público (landing v4); painel ANTES/DEPOIS é P0 mesmo com clone-irmão; copy visível ≠ Prototype N/A; N superfícies ⇒ URL principal = primária clonada.
- `process-fsm-event`: T5 ainda aceita UI none harness; T5 recusa UI none + superfície existente sem proto, e recusa index-painel mesmo com clone-irmão.
- `llm-flow-emission`: folha de tokens / chrome não substitui clone da página viva autenticada **nem** do HTML público no catálogo (`landing`).

## Impact

- Apply (após Pronto para Dev), só harness: `scripts/process-fsm/design_clone_gate.py`, `route-landmarks.yaml`, testes/fixtures reconstruídas (não os paths live #790/#792), `.agents/skills/design-critic/SKILL.md`, `.cursor/skills/covenant-flow/SKILL.md` (briefing Design-autor), deltas OpenSpec das capabilities acima.
- Não toca `backend/`, `frontend/src/`, HTML live `frontend/public/prototypes/card-790-copy-spot/**` / #792 / #799, `DESIGN.md`, `.cursor/process-fsm.yaml` Σ, `CONTEXT.md`, `docs/adr/`.
- `UI impact: none`. Prototype N/A. Snapshot N/A. Sem HTML de produto deste card.
- Origem: issue #819 (DoD grelhado; Q1–Q4=A, 2026-09-03). Relacionado e **não** reaberto como Apply: #790, #792 Pronto, #799 Pronto (lote 2026-08-30).
