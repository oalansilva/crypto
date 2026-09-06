# Snapshot — card #819 `card-819-clone-pagina-viva` (Assessment B)

- Card: #819 — https://github.com/oalansilva/crypto/issues/819
- Change: `openspec/changes/card-819-clone-pagina-viva/`
- Critic: isolated Design Critic B (detector estático; inherit de modelo; **sem** transcript do pai; **sem** resultados de Assessment A)
- UTC: 2026-09-04T19:16:00Z
- Tuple (sessão unbound): hooks `q=None` `bound_card=⊥` `q_git=develop`. Write produto deny. Esta onda só `.impeccable/critique/**`.
- Worktree: `/srv/apps/dev/criptofarol/crypto-worktrees/card-819-clone-pagina-viva`
- UI impact: **none** (harness/processo: helper T5 + catálogo + skills + testes; nenhuma rota, shell, componente, token ou copy de produto)
- Prototype: **N/A** confirmed (zero HTML desta change; `frontend/public/prototypes/` sem `card-819*`; Playwright visual **não** correu; browser gate **N/A** justificado)
- Detector desta onda: **estático** (gate live vs claims do design vs fixtures vs testes vs skills). Sem sessão, sem URL de produto, sem Playwright.
- `design.md` sha256: `c4277d3b1f9435e414280b11a05087478a0161aa448e98cb44f1b8c9664f91c6` (123 linhas, **1353** palavras, 10380 bytes)
- `files_g_design` (live, pré-Apply): `proposal.md` / `design.md` / `tasks.md` + 4 spec deltas. Gate live ainda faz skip UI none ⇒ predicado composto **passaria** hoje; Apply MUST estreitar o skip.
- `openspec validate card-819-clone-pagina-viva --type change --strict`: **valid**. Nota CLI 1.5.0: `--change` não existe; o item é posicional.
- Sem `## Design Critique` / `Design Agent verdict` na change (filho autor correto; este crítico MUST NOT editar `design.md`)
- Q1–Q4=A congeladas no issue (2026-09-03); não reabrir. Q3=A = MUST NOT patch HTML live `#790`.

---

## Brief

Alan no T7 julga um painel ANTES/DEPOIS (ou Prototype N/A em copy visível) em vez da página viva. Recidiva #799; evidência live #790 (`index.html` painel + `landing.html` clone na mesma pasta; URL canónico = directory index). Este card fecha dois furos de máquina no harness T5: (1) `evaluate_clone_gate` skip incondicional `UI impact: none`; (2) `concatenate_proto_html` junta todos os `*.html`. Semeia chave pública `landing` no catálogo. Briefing Design-autor: clonar a página viva no `index.html`. `UI impact: none` neste card (harness-only; `live_route: N/A`; `surface: new`; sem proto dir).

Audience: Design-autor / T5 / A/B no próximo card de superfície existente. Outcome: painel-index + sibling clone falha; clone v4 como index passa; copy visível não chega à aprovação sem proto. Direction: helper + YAML + skills canónicos; fixtures reconstruídas (não paths live). Scope: harness; zero `frontend/src/` / `backend/` / HTML de produto deste card.

---

## Detector tables (simulação; não implementar)

### D1 — live `evaluate_clone_gate` / `concatenate_proto_html`

| Probe | Live (este worktree) | Design claim | Disposition |
| --- | --- | --- | --- |
| Early-return UI none | `design_clone_gate.py` L208–209: `if ui == "none": return True` (incondicional; **antes** de parse útil para existing) | Furo copy-only #790; Apply MUST remover | **CONFIRMED hole** — Apply D5–D6 |
| `concatenate_proto_html` | L87–91: `sorted(proto_dir.glob("*.html"))` → `"".join(parts)` | Junta todos os `*.html`; clone irmão mascara painel | **CONFIRMED hole** — Apply D2 `canonical_proto_html` |
| `canonical_proto_html` | **ausente** | Substituir concatenate; só `index.html` + fallback 1 ficheiro | Pré-Apply esperado |
| `LIVE_ROUTE_RE` | `(\/\S+|N/A)` | Cresce para `(\/\S+|landing\|N/A)` | Pré-Apply; landing **não** parseia hoje |
| `routes_from_catalog` | só `str(key).startswith("/")` | incluir `kind: public` | Pré-Apply; `landing` seria filtrado hoje |
| `requires_existing_clone` | `/` **ou** `surface == existing` | também `live_route == landing` | Pré-Apply |
| `is_new_exempt` | `surface == new` ganha se a rota **não** começa por `/` | falso quando a rota é chave de catálogo (`/` ou `landing`) | Pré-Apply; `landing` + `new` **isenta hoje** |
| Lookup existing | `route = live_route if live_route and live_route.startswith("/") else None` | D6: se existing → lookup HEAD + canonical | Ver P2 (choke `startswith("/")`) |
| Playwright / network | Módulo: «No Playwright. No network.» `process_event.py` sem import Playwright. T5 yaml: `guard: G_design` only | T5 continua offline (Non-Goal) | **CONFIRMED** |

### D2 — catálogo HEAD / worktree

`scripts/process-fsm/route-landmarks.yaml` `version: 1`:

| Key | Presente hoje | kind |
| --- | --- | --- |
| `/monitor` | sim | omitido → autenticado |
| `/favorites` | sim | omitido |
| `/combo/discovery` | sim | omitido |
| `/combo/select` | sim | omitido |
| `landing` | **não** | D1 seed = **Apply** |

`test_seeded_catalog_has_four_routes_and_monitor_landmarks` crava exactamente o set de 4 rotas `/`. Nenhuma chave `landing`. D1 YAML (selectors `.faq-section` / `.button-primary` + texts h1/FAQ/CTA) **não** está no disco. **CONFIRMED**: semente é Apply.

### D3 — landmarks D1 vs live v4

Ficheiro: `frontend/public/prototypes/cripto-farol-landing-v4/index.html`

| Landmark D1 | Live v4 | Resultado |
| --- | --- | --- |
| selector `.faq-section` | `<section class="section faq-section" id="faq">` (L220) | **MATCH** (`faq-section` é token de `class`; `selector_matches` aceita) |
| selector `.button-primary` | `<a class="button button-primary" href="#lista">` (L53) + botões form | **MATCH** |
| text h1 «Comprar ou vender cripto? O Cripto Farol responde.» | `<h1 id="hero-title">…</h1>` (L48) | **MATCH exacto** |
| text `FAQ` | nav `<a href="#faq">FAQ</a>` (L32) e `<p class="section-kicker">FAQ</p>` (L222) | **MATCH** |
| text «Quero meus 6 meses grátis» | CTA L53 | **MATCH exacto** |
| Context `#faq` (não é selector D1) | `id="faq"` na mesma `<section>` | Facto extra; D1 usa classe — **não é mismatch de selector** |
| `COPIED:start/end` | 0 | Esperado: v4 é fonte, não proto de card. Fixture PASS MUST **adicionar** markers (D7) |

**Nenhum selector D1 errado vs live v4.** Apply MAY semear exactamente o YAML D1.

### D4 — live #790 panel vs concatenate (path **não** é fixture)

Pasta: `frontend/public/prototypes/card-790-copy-spot/` (`index.html` + `landing.html`). Q3=A: MUST NOT patch.

| Probe | `index.html` (painel) | `landing.html` (clone v4) | Concatenate `sorted(*.html)` = index+landing |
| --- | --- | --- | --- |
| `h2` count | **6** | 7 | — |
| `COPIED:start/end` | **0 / 0** (`copied` sum 0) | **0 / 0** | **0** |
| link `./landing.html` | **sim** (L25) | n/a | — |
| h1 «Copy alinhada ao Spot — telas alteradas» | **sim** (L23) | não (h1 landing) | — |
| tags ANTES/DEPOIS | sim (`.tag.depois`, `<b>DEPOIS</b>`); **não** dentro do texto do `<h2>`) | n/a | — |
| `.faq-section` | **não** | sim | sim (via sibling) |
| `.button-primary` | **não** | sim | sim |
| h1 landing | **não** | sim | sim |
| `FAQ` | **sim** (h2 «3 · Landing v4 — FAQ») | sim | sim |
| CTA 6 meses | **não** | sim | sim |
| `landmarks_match` D1 | **FAIL** (falta selectors + h1 + CTA) | **PASS** | **PASS** (furo landmarks) |
| `copied > 0` | FAIL | FAIL | **FAIL** (live sem markers) |
| `evaluate_clone_gate` hoje com `UI impact: none` | — | — | **True** (skip L208; **não lê HTML**) |

Conclusão check 4:

- Index-only **falharia** landmarks de `landing` (painel não é a página viva). **CONFIRMED**.
- Concatenate **passaria landmarks** D1 (sibling mascara o painel). **CONFIRMED hole**.
- Concatenate **não** passaria o gate completo em bytes live (`copied` 0 em ambos). O T5 do #790 passou pelo **skip UI none**, não pelo concatenate+copied. D7 reconstruirá sibling **com** `COPIED` positivo precisamente «para o concatenate antigo passar e o index-only falhar». Isso é o teste do furo, não o path live.

### D5 — `LIVE_ROUTE_RE` ordem / brittle key

| Hoje | Planeado (D1 / spec) |
| --- | --- |
| `(\/\S+|N/A)` | `(\/\S+|landing|N/A)` |

- `landing` vs `N/A`: tokens disjuntos; ordem no alternation **não** quebra parse de `N/A` nem de `landing`.
- «`N/A` antes de identificador genérico»: o plano **não** introduz classe genérica; só a chave `landing`. Sem colisão com `N/A`.
- Brittle: chave pública **sem** `/` fica hardcoded no regex **e** em `requires_existing_clone` / `is_new_exempt`. `routes_from_catalog` via `kind: public` é genérico, mas `live_route: docs` / `help` **não parseia** sem outro patch do regex. `/help` já parseia (`\/\S+`) e é fail-closed se a chave HEAD faltar (D1).
- Não quebra Q (semente = `landing` só). **P2** (não P0/P1).

### D6 — Apply contract files vs MUST NOT

Ficheiros listados para **editar/criar** (existem hoje os alvos de patch; fixtures 819 **ainda não** — Apply):

| Path no contrato | Disco agora |
| --- | --- |
| `scripts/process-fsm/design_clone_gate.py` | EXISTS |
| `scripts/process-fsm/route-landmarks.yaml` | EXISTS (sem `landing`) |
| `scripts/process-fsm/test_design_clone_gate.py` | EXISTS (4 rotas `/`; sem casos 790/landing) |
| `scripts/process-fsm/test_process_event.py` | EXISTS (`test_t5_default_g_design_ui_none_transitions` usa só `UI impact: none\n`) |
| `scripts/process-fsm/fixtures/790-panel-index.html` | **ausente** (Apply D7) |
| `scripts/process-fsm/fixtures/790-sibling-landing-clone.html` | **ausente** |
| `scripts/process-fsm/fixtures/v4-landing-clone.html` | **ausente** (opcional) |
| `.agents/skills/design-critic/SKILL.md` | EXISTS — L16 / L63 **só rotas autenticadas**; sem briefing D3 |
| `.cursor/skills/covenant-flow/SKILL.md` | EXISTS — coluna Design = célula da tabela + síntese OpenSpec; sem D3 |
| Deltas OpenSpec já neste change | 4 specs presentes |

MUST NOT no contrato: `backend/**`, `frontend/src/**`, `frontend/public/prototypes/card-790-copy-spot/**`, proto live #792/#799, `DESIGN.md`, Σ yaml, `CONTEXT.md`, `docs/adr/`, `.dsh/**`, `.grok/**`.

**Nenhum path live de proto está na lista de escrita.** Fixtures = `scripts/process-fsm/fixtures/`, não `frontend/public/prototypes/card-790*`. **CONFIRMED**.

### D7 — zero HTML de produto deste card

`frontend/public/prototypes/` **não** contém `card-819*`. Change não adiciona proto. **CONFIRMED** zero `frontend/public/prototypes/card-819*`.

### D8 — `## Design Critique`

Grep na change: **nenhum** `## Design Critique` / `Design Agent verdict`. Pai escreve depois de A/B. **CONFIRMED**.

### D9 — spec main vs delta (inversão)

`openspec/specs/design-route-clone-gate/spec.md` (main, pós-#799):

| Main (ainda vigente até archive) | Delta desta change |
| --- | --- |
| UI none + 3 md + spec ⇒ pass; T5 **não** exige landmarks/`copied` (incondicional) | MODIFIED: pass só com `N/A` justificado + `surface: new` (ou sem existing). ADDED: UI none **não** skippa se existing / chave de catálogo |
| «substring in the **concatenated** HTML» | MODIFIED: HTML **canónico** `index.html` (ou fallback 1 ficheiro). ADDED: MUST NOT concatenar; sibling `landing.html` MUST NOT satisfazer |
| Catálogo semeia 4 rotas `/` | MODIFIED + ADDED: também `landing` `kind: public` |
| `live_route` que **começa por `/`** ⇒ existing | MODIFIED: chave de catálogo = `/` **ou** `landing` |
| T5 offline, sem Playwright | PRESERVED (process-fsm-event MODIFIED reitera offline + mede só index) |

`openspec/specs/process-fsm-event/spec.md` cenário «T5 still accepts UI none» ainda é UI none incondicional; delta acrescenta `N/A`+`new` e recusa painel/existing sem proto.

`openspec/specs/llm-flow-emission/spec.md` aponta só rotas autenticadas `/`; delta acrescenta HTML público `landing`.

**Não há contradição não invertida:** o delta ADDED+MODIFIED substitui concatenate e o skip UI none. Gallery r1 / fail-closed HEAD permanecem.

### D10 — T5 offline / Non-Goal Playwright

- Design Non-Goals: «Playwright dentro de `submeter_design`».
- Task 2.2: «Sem Playwright dentro de T5».
- Spec process-fsm-event: «T5 MUST remain offline».
- Live: `process_event.py` sem Playwright; helper estático; yaml T5 = `guard: G_design` (D8 Σ intacto).

**CONFIRMED**. Browser desta coluna Design = N/A (no product UI). Detector = estas sondas.

### D11 — validate / hash

- sha256 `design.md`: `c4277d3b1f9435e414280b11a05087478a0161aa448e98cb44f1b8c9664f91c6`
- palavras: 1353
- `openspec validate card-819-clone-pagina-viva --type change --strict`: **valid**

---

## Grilled acceptance (testável no Apply)

| Aceite grelhado | Onde está pinado | Live hoje | Apply MUST |
| --- | --- | --- | --- |
| 790 panel index + sibling clone FAIL mesmo se concatenate passasse | spec cenário «Panel index plus sibling…»; tasks 2.1 / 2.2; D2; D7 fixtures com `COPIED` no sibling | Live concat: landmarks PASS, copied 0; UI none skip = True | Fixture **reconstruída** (não cp do path live); index-only FAIL; concatenate antigo **não** é o predicado |
| v4 clone como index PASS **não** porque o path contém `790` | spec «V4 clone as index passes…»; task 2.1; D7 opcional `v4-landing-clone.html` | v4 live: landmarks D1 PASS, copied 0 (não é o teste) | Fixture com landmarks **e** `COPIED` > 0; path `scripts/process-fsm/fixtures/`, não `card-790-copy-spot` |
| UI none harness `N/A`+`new` sem proto PASS | spec «UI none harness without proto»; task 2.2; **este** `design.md` | Skip incondicional já passa até `UI impact: none` nu | Estreitar skip **e** pinar o caso N/A+new (teste live 2.2 hoje é mais fraco) |
| existing / `landing` sem proto FAIL mesmo com UI none | spec «Existing surface without proto»; tasks 2.1 / 2.2; D5–D6 | UI none ⇒ True **sempre** | Remover early-return; `requires_existing_clone(landing)` |
| Q3=A: não patchar HTML live #790 | Apply contract MUST NOT + task 1.3 / 4.1 | Path live intocado nesta change | Diff Apply sem `frontend/public/prototypes/card-790-copy-spot/**` |

---

## Skills listed (pré-Apply)

`.agents/skills/design-critic/SKILL.md`:

- Guardrail 5 (L16): clone da «página autenticada da rota viva» — lista `/monitor` `/favorites` `/combo/discovery` `/combo/select`. **Sem** HTML público / `landing`.
- Base do proto (L63): «partir da página autenticada». Tela nova: «não usar landing genérica». Isenção `surface: new` / `N/A` **sem** excepções para chave de catálogo pública.

`.cursor/skills/covenant-flow/SKILL.md`: célula Status=Design (síntese OpenSpec + Gist + proto se UI). **Sem** o parágrafo D3. dsh lê este runbook; dual-write `.dsh/` / `.grok/` continua MUST NOT (task 3.2).

Isto é o buraco de briefing que o Apply cola — não um defeito do pacote Design.

---

## Critique (contrato vs live)

Issue #819 sintetizado (Q1–Q4=A). Pacote OpenSpec MODIFY de 4 capabilities. Prototype N/A justificado. Zero HTML deste card. Sem rewrite `DESIGN.md`. Sem `## Design Critique` pré-preenchido. T7 humana permanece.

Os dois furos de máquina que o Design nomeia **existem no disco**. Selectors D1 **batem** na landing v4 viva. Catálogo **não** tem `landing`. Fixtures 790 **ainda não** existem (correcto). Delta **inverte** concatenate e skip UI none. Aceites grelhados estão em spec+tasks de forma observável.

Residuais = regex/`landing` hardcoded (P2), choke `startswith("/")` no lookup se Apply copiar «resto como hoje» (P2; testes 2.1 ainda pinam o PASS), precisão de wording no painel live (P3).

---

## Findings

### P0

(nenhum)

### P1

(nenhum)

### P2

- **`LIVE_ROUTE_RE` crava uma chave pública.** Planeado `(\/\S+|landing|N/A)`. `kind: public` no YAML deixa semear outra chave sem `/`, mas o parse de `live_route:` e `requires_existing_clone` / `is_new_exempt` não a reconhecem sem **outro** patch de regex/helper. `/help` já entra por `\/\S+` (fail-closed sem chave HEAD). Não quebra Q (semente = `landing`). Disposition: Apply MAY deixar `landing` literal neste card; card futuro de catálogo (`/help`, `/profile`, ou outra chave `kind: public` sem `/`) MUST alargar o grupo 1. Não tratar isto como Q aberta.

- **D6 «resto como hoje» vs choke `startswith("/")`.** Live L222–224: `route = live_route if … startswith("/") else None` → `landing` nunca chega ao lookup. Task 1.2 nomeia regex, `routes_from_catalog`, `requires_existing_clone` / `is_new_exempt`, early-return — **não** esta linha. Se Apply seguir D6 «resto affected… como hoje» depois do skip, `live_route: landing` + proto v4 **falha** o aceite «clone como index PASS». Task 2.1 / spec V4 ainda pinam o PASS. Disposition: Apply MUST usar a rota parseada (`/` **ou** `landing`) como chave de `routes_from_catalog` / HEAD lookup; MUST NOT filtrar existing só com `startswith("/")`.

### P3

- Context do `design.md` cita `#faq`; D1 semeia `.faq-section`. Ambos existem no v4 (`id="faq"` na mesma section). Não é selector errado.
- Context / D7: «6× `h2` DEPOIS». Live: 6 `<h2>` numerados **sem** a palavra DEPOIS no heading; DEPOIS vive em `.tag.depois`. Fixture MAY usar tags ou o token no h2; o predicado de FAIL é landmarks D1 no **index**, não o literal DEPOIS.
- Spec do painel: «no landing h1/FAQ/CTA». Live index **contém** substring `FAQ` no h2. `landmarks_match` mesmo assim FAIL (faltam selectors, h1, CTA). Fixture que copie o h2 com «FAQ» continua a falhar o conjunto. Apply SHOULD não exigir ausência de `FAQ` se os outros landmarks faltarem.
- Concatenate live #790 **não** é um PASS completo do gate (`copied` 0). O furo de concatenate é landmarks; o furo que deixou #790 chegar a T7 é o skip UI none. D7 já reconstrói `COPIED` no sibling — manter essa distinção no teste (não assertar bytes live).
- `test_t5_default_g_design_ui_none_transitions` hoje grava só `UI impact: none\n`. Depois de D6, `none` ∧ ¬existing **ainda** passa o skip (mentira sem campos = residual skill/A/B, Q4=A). Task 2.2 MUST **adicionar** o pin N/A+new; MUST NOT apagar o regresso de harness. SHOULD não tratar o teste nu como o aceite grelhado.
- Inserção D3 em covenant-flow: não há L16/L63 equivalente; a «coluna Design» é uma célula. Apply SHOULD colar o briefing onde o Design-autor lê o runbook (célula Design e/ou passo «Design refina em OpenSpec»), sem dual-write `.dsh/` / `.grok/`.
- CLI OpenSpec 1.5.0: `openspec validate --change …` falha (`unknown option`); forma válida = `openspec validate card-819-clone-pagina-viva --type change --strict`. Task 4.2 omite `--change` — OK.

---

## Audit

- A11y / responsive / browser / detector visual: **N/A (`UI impact: none`)**. Prototype N/A confirmed. Playwright visual não correu. **Browser gate: N/A (no product UI).** Justificativa: aceite = predicado T5 + briefing no próximo Design de superfície existente; este card não cria nem altera ecrã.
- Dual critic / T7: snapshot desta coluna = este arquivo (não vazio). Gist OpenSpec não é a crítica. `design.md` declara Snapshot Impeccable N/A para o **pipeline visual** — correcto; este ficheiro é a evidência A/B do harness.
- FSM: sem task de estado/evento/`enabled_tools`. T5 yaml intacto. T7 Alan. T5 parent / Non-Goal Playwright. `UI impact: none` não pulou Design nem Aprovação de Design.
- Product UI Cripto: zero `frontend/src/` / `backend/` / `frontend/public/prototypes/card-819*` no Apply contract.
- Q1=A / Q4=A: copy visível + Prototype N/A recusado na máquina quando existing/catálogo declarado; mentira `none`+`new` = skill/A/B.
- Q2=A: URL canónico = `index.html` da página viva; concatenate fechado.
- Q3=A: MUST NOT path live #790; fixtures em `scripts/process-fsm/fixtures/`.
- Selectors D1 vs v4: **alinhados** (sem finding de selector).
- Spec main concatenate / UI none skip: **invertidos** no delta (sem contradição residual bloqueante).

---

## Trace

1. Live helper: skip UI none L208; concatenate glob `*.html`; catálogo 4 rotas `/`; sem `landing`; `LIVE_ROUTE_RE` sem `landing`; lookup existing só `/`.
2. v4 `index.html`: `.faq-section`, `.button-primary`, h1, `FAQ`, CTA — todos presentes. `#faq` também. `COPIED` 0.
3. #790 `index.html`: h1 copy-spot, 6× h2, link `./landing.html`, 0 `COPIED`; landmarks landing FAIL. `landing.html`: clone v4, landmarks PASS, 0 `COPIED`. Concatenate: landmarks PASS, copied 0. Skip UI none: True.
4. Change OpenSpec: proposal/design/tasks + 4 deltas; `design.md` 1353 palavras; sha256 `c4277d3b…4f91c6`; sem Design Critique.
5. `openspec validate … --type change --strict`: valid.
6. Apply contract: alvos de patch existem; fixtures 819 ausentes; MUST NOT não inclui escrita em proto live.
7. Skills: D3 ainda não colado (L16/L63 autenticado-only).
8. Achados: zero P0/P1; P2 regex + choke lookup; P3 wording/teste nu/CLI.

---

## Verdict

**PASS** — zero P0/P1 abertos. Browser N/A justificado (`UI impact: none`; sem superfície de produto). Snapshot não vazio.

Prototype: **N/A** — harness/processo; aceite observável em T5 + briefing; zero HTML `card-819*`.

Próximo (pai, não este crítico): sintetizar A/B em `## Design Critique`; T5 só o pai.

---

## Metadata

- Critic: Assessment B (isolated, inherit model, no parent transcript, no Assessment A)
- Detector: static (gate / catalog / v4 / #790 / specs / tasks / skills)
- Browser: N/A
- Snapshot path: `.impeccable/critique/819-card-819-clone-pagina-viva-B.md`
