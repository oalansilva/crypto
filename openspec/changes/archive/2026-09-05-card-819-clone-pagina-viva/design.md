## Context

Card [#819](https://github.com/oalansilva/crypto/issues/819). Briefing = issue grelhado. Q1–Q4=A (2026-09-03); este Design não as reabre.

Factos live (disco): `evaluate_clone_gate` faz `if ui == "none": return True` (skip do proto — furo copy-only #790). `concatenate_proto_html` junta todos os `*.html` (clone em `landing.html` mascara painel `index.html`). Catálogo v1 só `/monitor`, `/favorites`, `/combo/discovery`, `/combo/select`; landing pública ausente. Overlay serve `…/prototypes/<slug>/` → `index.html`. Landing vigente = `frontend/public/prototypes/cripto-farol-landing-v4/` (h1 «Comprar ou vender cripto? O Cripto Farol responde.», CTA «Quero meus 6 meses grátis», `#faq`). #790 live: index-painel (h1 «Copy alinhada ao Spot — telas alteradas», 6× `h2` DEPOIS, link `./landing.html`, 0 `COPIED`); `landing.html` = clone v4. Path live **não** é fixture deste card.

UI impact: none
live_route: N/A harness-only; no product route
surface: new

Harness/processo (skill + G_design + catálogo + testes). Sem rota, shell, copy ou HTML de produto.

## Goals / Non-Goals

**Goals:**

- URL canónico do proto = topologia da página viva + delta dentro (Q2=A).
- Copy visível + Prototype N/A ⇒ T5 recusa; o Design não chega à aprovação (Q1=A, Q4=A).
- Index-painel #790 + `landing.html` clone na pasta ⇒ check falha; clone v4 **não** falha por ser «o path do #790».
- N superfícies ⇒ URL principal = primária clonada; extras à parte.
- Briefing Design-autor: clonar a página viva (rota autenticada **ou** HTML público no catálogo); nunca «6 estados» / painel ANTES/DEPOIS.

**Non-Goals:**

- Reabrir HTML já publicado do #790 / #792 / #799 como Apply (Q3=A).
- Código de produto (`frontend/src/**`, `backend/**`).
- Pixel-perfect de dados live. Auto dsh. Redesenhar landing ou copy do #790. Ensaio/flag/produto Spot.
- Saltar proto em copy visível. Painel com link para clone. Deixar o Design chegar à aprovação para Alan devolver à mão.
- Playwright dentro de `submeter_design`. Σ/evento novo. Rewrite `DESIGN.md`. Proto HTML deste card.

## Decisions

1. **Catálogo landing pública (residual 1).**  
   Semente neste Apply (como #799 semeou quatro rotas). Forma YAML exacta — as quatro chaves `/` mantêm-se; default `kind: authenticated` quando a chave começa por `/` e `kind` omite:

   ```yaml
   landing:
     kind: public
     live_url: https://criptofarol.com.br/
     source: frontend/public/prototypes/cripto-farol-landing-v4/index.html
     selectors: [".faq-section", ".button-primary"]
     texts:
       - "Comprar ou vender cripto? O Cripto Farol responde."
       - "FAQ"
       - "Quero meus 6 meses grátis"
   ```

   `/monitor` (etc.) **não** ganha `kind: public`. `routes_from_catalog`: dicts cuja chave começa por `/` **ou** `kind: public`.  
   `LIVE_ROUTE_RE` cresce (grupo 1): `(\/\S+|landing|N/A)` — `N/A` **antes** de qualquer identificador genérico. Justificação na mesma linha continua no grupo 2.  
   Fail-closed: `live_route: landing` sem chave em HEAD recusa. `/help` e `/profile` **não** são semeados aqui (T5 recusa se declarados sem chave; skill/A/B cobrem copy visível nessas telas). Não tratar `landing` como rota autenticada.

2. **Medir `index.html` (residual 2).**  
   Substituir `concatenate_proto_html` por `canonical_proto_html`: ler só `proto_dir / "index.html"`. Fallback documentado: se `index.html` faltar e existir **exactamente um** `*.html`, ler esse ficheiro (proto de um só arquivo). Se faltar index e houver 0 ou ≥2 HTML → string vazia → landmarks/`copied` falham. Extra `landing.html` **não** satisfaz o index. Overlay: URL canónico = directory index. N superfícies: `--prototype-url` = primária; extras no comentário do card; T5 só mede o index.

3. **Briefing Design-autor (residual 3)** — texto exacto a colar em `.agents/skills/design-critic/SKILL.md` (guardrail + base do proto) **e** na coluna Design de `.cursor/skills/covenant-flow/SKILL.md` (dsh lê o runbook canónico; não dual-write em `.dsh/` nem `.grok/`):

   > **Clone da página viva:** em superfície já existente — rota autenticada no catálogo (`/monitor`, `/favorites`, `/combo/discovery`, `/combo/select`) **ou** HTML público vigente (chave `landing` = landing v4 em `https://criptofarol.com.br/`) — o URL canónico do proto (`…/prototypes/<slug>/` → `index.html`) MUST clonar essa página viva e aplicar só o delta do card. Nunca «6 estados» / painel ANTES/DEPOIS como URL canónico, mesmo com clone noutro ficheiro da pasta. Copy visível (landing / Ajuda / Perfil) = a página mudou; Prototype N/A é recusado. N superfícies existentes: URL principal = página primária clonada; as outras com copy visível têm URLs extra de clone — nunca um painel das N no index.

4. **N superfícies (residual 4).**  
   `index.html` = clone da superfície primária. Demais páginas = ficheiros extra + links extra. T5 ignora extras. Skill/A/B: painel das N no index = P0.

5. **Evasão e UI none (residual 5, Q4=A).**  
   Máquina **não** adivinha mentira `UI impact: none` / `surface: new` em copy visível — skill/A/B. Máquina ainda:  
   - `requires_existing_clone` se `live_route` começa por `/` **ou** é `landing` **ou** `surface == existing`.  
   - `is_new_exempt` é falso quando `live_route` é chave de catálogo (`/` ou `landing`).  
   - Recusar proto ausente / Prototype N/A quando existing ou chave de catálogo (mesmo com `UI impact: none`).  
   - Recusar index-painel mesmo com clone-irmão (D2).  
   - Recusar skip UI none quando há declaração existing **ou** chave de catálogo (com ou sem proto dir).  
   - Este card: `UI impact: none` + `live_route: N/A` justificado + `surface: new` + **sem** proto dir → T5 passa.

6. **`evaluate_clone_gate` (como).**  
   Remover o early-return incondicional `if ui == "none": return True`. Ordem: parse campos → `existing = requires_existing_clone(...)` → se `ui == "none"` e **não** `existing` → True (harness; proto de superfície nova não dispara catálogo) → se `existing` → lookup HEAD + `canonical_proto_html` + landmarks + `copied > 0` (proto ausente ou index vazio ⇒ False). Resto affected/new/`N/A` como hoje, com D1–D2. T5 continua offline.

7. **Fixtures (não paths live).**  
   `scripts/process-fsm/fixtures/790-panel-index.html` — reconstruir painel (h1 copy-spot, ≥6 `h2` DEPOIS, link `./landing.html`, 0 `COPIED`). `scripts/process-fsm/fixtures/790-sibling-landing-clone.html` — clone mínimo v4 com landmarks D1 **e** `COPIED` positivo (para o concatenate antigo passar e o index-only falhar). Opcional `v4-landing-clone.html` = o mesmo clone como único `index.html` ⇒ PASS contra `landing`. MUST NOT copiar/patchar `frontend/public/prototypes/card-790-copy-spot/**`. Clone v4 PASS **não** depende de o path conter `790`.

8. **Σ yaml intacto.** Sem evento/estado/hook novo. `G_design` continua o guard T5; só o helper Python muda.

## Apply contract

Ficheiros exactos (e só estes) neste worktree, após `Status=Pronto para Dev`:

1. `scripts/process-fsm/design_clone_gate.py` — `canonical_proto_html` (D2); `LIVE_ROUTE_RE` com `landing` (D1); `routes_from_catalog` inclui `kind: public`; UI-none skip só se **não** existing (D5–D6).
2. `scripts/process-fsm/route-landmarks.yaml` — semente `landing` (D1); quatro rotas autenticadas intactas.
3. `scripts/process-fsm/test_design_clone_gate.py` — catálogo 4 rotas `/` + `landing`; 790-painel + sibling clone FAIL; clone v4 como index PASS (não por path 790); UI none harness PASS; existing/`landing` sem proto FAIL; UI none + existing recusa.
4. `scripts/process-fsm/fixtures/790-panel-index.html` e `scripts/process-fsm/fixtures/790-sibling-landing-clone.html` (D7). Opcional `scripts/process-fsm/fixtures/v4-landing-clone.html`.
5. `scripts/process-fsm/test_process_event.py` — T5 UI none harness (N/A + new, sem proto) transita; T5 recusa painel-index + sibling com `live_route: landing`; T5 recusa existing sem proto.
6. `.agents/skills/design-critic/SKILL.md` — briefing D3 (substituir operacionalização só-autenticada L16/L63).
7. `.cursor/skills/covenant-flow/SKILL.md` — o mesmo briefing D3 na coluna Design (dsh lê este runbook).
8. Deltas já neste change: `design-route-clone-gate`, `impeccable-design-gate`, `process-fsm-event`, `llm-flow-emission`.

MUST NOT: `backend/**`, `frontend/src/**`, `frontend/public/prototypes/card-790-copy-spot/**`, proto live #792/#799, `DESIGN.md`, `.cursor/process-fsm.yaml` Σ, `CONTEXT.md`, `docs/adr/`, `.dsh/**`, `.grok/**`.

## Risks / Trade-offs

- **[Risk]** Mentira `UI impact: none` / `surface: new` em copy visível. → Mitigation: skill/A/B (Q aceite); máquina recusa só com `existing` ou chave de catálogo.
- **[Risk]** Concatenate antigo vs index-only: proto de um só ficheiro não chamado `index.html`. → Mitigation: fallback D2 (exactamente um `*.html`).
- **[Risk]** Ajuda/Perfil copy visível sem chave no catálogo. → Mitigation: fail-closed T5 se `live_route: /help`; skill recusa Prototype N/A; semente `/help` fica para card futuro de catálogo.
- **[Risk]** Pin dsh/`.grok/` desactualizado. → Mitigation: lei só em `.cursor/skills/covenant-flow` + `.agents/skills/design-critic`; stub dsh já aponta ao canónico.

## Migration Plan

Depois do Apply, o próximo Design de superfície existente MUST clonar a página viva no `index.html`. Cards já em Aprovação/Pronto/Done **não** são reavaliados. Rollback: reverter helper + YAML + skills; Σ yaml não muda.

## Open Questions

Nenhuma Q da grelha aberta. Residuais 1–5 fechados acima.

## UI impact

**none** — harness/processo. Nenhuma rota, shell, componente, token ou copy de produto. Nenhuma superfície visual nova ou alterada.

## Prototype

N/A — `UI impact: none`; aceite = predicado T5 + briefing no próximo Design de superfície existente. Sem HTML deste card. Sem rewrite de `DESIGN.md`. Sem pipeline Impeccable visual. Playwright desta coluna = N/A. Snapshot Impeccable = N/A justificado.

## Prototype Validation

N/A — sem superfície visual. Sem URL, viewport ou assert de UI.

## Impeccable pipeline (esta coluna Design)

N/A — `UI impact: none`. Sem shape/protótipo/crítica/audit/polish/browser de tela de produto. O filho autor não emite secção de crítica neste `design.md`.

## Design Critique

- **P0:** nenhum
- **P1:** nenhum
- **P2 accepted-residual:** mentira `UI impact: none` / `surface: new` em copy visível sem chave de catálogo (máquina não adivinha; skill/A/B). T5 só mede o index nas N superfícies (extras = skill/A/B). Ajuda/Perfil sem semente (`/help` fail-closed se declarado). `LIVE_ROUTE_RE` crava `landing`; outra chave pública sem `/` exige novo regex. D6 «resto como hoje» pode deixar `startswith("/")` no lookup — task 2.1 pina `landing` PASS.
- **P3 accepted-residual:** Context «6× h2 DEPOIS» vs live (6 `h2`, DEPOIS nas tags). `FAQ` é substring do painel; h1+CTA+selectors discriminam. design-critic L65 isenta `surface: new` sem «unless chave»; T5 fecha `landing`. Teste T5 live só pina `UI impact: none` nu — Apply MUST pinar N/A+new. Concatenate live #790 passa landmarks mas `copied` 0; D7 marca `COPIED` no sibling.
- **Prototype:** N/A — `UI impact: none`; aceite = predicado T5 + briefing no próximo Design de superfície existente; sem HTML deste card.
- **Snapshot Impeccable:** `.impeccable/critique/819-card-819-clone-pagina-viva-A.md` e `…-B.md` (r1). Apply/Code Review não lêem. Gist OpenSpec não é a crítica.
- **Design Agent verdict: PASS** — zero P0/P1; A e B isolados; sem superfície visual por classificar; browser N/A justificado.
