# Snapshot — card #799 `card-799-prototype-clone-rota` (Assessment B)

- Card: #799 — https://github.com/oalansilva/crypto/issues/799
- Change: `openspec/changes/card-799-prototype-clone-rota/`
- Critic: isolated Design Critic B (detector; no transcript inherit; no Assessment A)
- UTC: 2026-08-30T00:02:35Z
- Tuple (sessão unbound): hooks `q=None` `bound_card=⊥` `q_git=develop`. Write produto deny. Esta onda só `.impeccable/critique/**`.
- Board: `oalansilva` Project 1 item `PVTI_lAHOAAHtBM4BV8b2zg4jxi0` — **Status=Design** (`UI impact: none` não saltou coluna).
- UI impact: **none** (harness `G_design` / catálogo / skill; nenhuma rota, shell, componente, token ou copy de ecrã do CriptoFarol)
- Prototype: N/A confirmed (sem HTML desta change; `frontend/public/prototypes/` sem `card-799-*`; Playwright visual **não** correu)
- Detector/browser desta coluna: **N/A (no UI)** — justificado. Sem superfície visual nova ou alterada. Impeccable visual / `DESIGN.md` / Playwright desta coluna = N/A. Q1–Q5=A congeladas; **não** se exige HTML.
- `design.md` sha256: `82798318d659d5764d86e7a185296c7cc74a56258613c752a0f6cef0bdee7e3b` (1765 palavras)
- `files_g_design`: True (`proposal.md` / `design.md` / `tasks.md` + spec deltas `design-route-clone-gate`, `impeccable-design-gate`, `process-fsm-event`, `llm-flow-emission`)
- `openspec validate card-799-prototype-clone-rota --type change --strict`: **valid**
- Sem `## Design Critique` / `Design Agent verdict` na change (filho autor correto).
- Browser gate: **N/A (no UI)**.

---

## Brief

Alan no T7 do #792 abriu o Monitor real e o proto r1 era galeria; A/B + `design.md` passaram com “fidelidade shell”. O teste live de clone ainda é chrome (sidebar 224px, `--bg-*`). Card #799 endurece o harness: fidelidade bloqueante = landmarks da rota viva + `copied` medido + campo parseável; T5 offline (`G_design` composto). `UI impact: none`. Q1–Q5=A (2026-08-29) não reabertas.

Audience: Alan no T7 do **próximo** Design UI affected com rota existente; máquina T5 (`process_event`). Outcome: galeria + 0 bytes `copied` não passa `submeter_design`. Direction: predicado Python + YAML versionado + skill/A/B; sem Playwright autenticado em T5. Scope: harness; zero produto CriptoFarol.

---

## Probes (live, este worktree, pré-Apply)

### `files_g_design` / T5

- `scripts/process-fsm/process_event.py` L165–170: só `proposal.md` + `design.md` + `tasks.md` + algum `specs/**/*.md`. Sem landmarks, `copied`, `live_route`.
- L322–323: `g_design is None` → `files_g_design(resolved_change_dir)` apenas. Proto já resolvido em L318–320 (`frontend/public/prototypes/<inferred_change>`).
- `.cursor/process-fsm.yaml` T5: `guard: G_design`; Σ / `enabled_tools` / eventos intactos. `fsm.py` mapeia `G_design` → `g_design`.
- `test_process_event.py`: T5 legais injectam `g_design=True`. `_change_tree` escreve `design.md` = `# d\n` (sem campo). Catálogo / helper / fixture **ausentes** no disco (esperado pré-Apply).
- Folha de tokens `.agents/skills/impeccable/references/cripto-farol-token-sheet.md`: **ausente** (facto T0).

### Skill `design-critic`

L63 operacionaliza clone de tela existente como sidebar 224px + tokens `--bg-*` / `--accent-primary`. L66 conserva #530 (Apply lê proto no disco). Sem URL viva vs proto; `/login` não nomeado. Byte-identical ao pin `v1.1.4` em `/srv/apps/dev/covenant-flow/.agents/skills/design-critic/SKILL.md` (13875 B).

### Specs main

- `impeccable-design-gate`: “clone the current shell/nav/tokens/density” — chrome basta.
- `llm-flow-emission`: SHALL da folha de tokens; proxy handoff copied-vs-generated (não soma `COPIED:*`).
- `process-fsm-event`: **não** menciona `files_g_design` (o delta ADDED desta change é o que passa a exigir o composto).

### #792 r1 / r2

| Artefacto | sha256 | bytes | `table.signals` | `COPIED:*` |
| --- | --- | ---: | --- | --- |
| Live path `frontend/public/prototypes/card-792-monitor-risco-explicito/index.html` (r2) | `1a1ff265162784ca5708a76de22e6565ae85fb2832b90daec73cc40ac12f90c3` | 95314 | sim (`<table class="signals">` + CSS `table.signals`) | sim |
| PR #802 commit `0576fd37` (r1; **não** no `develop` squash) | `068581d6b9b2171b7534cb1250575bf4a61ea9b0e428047ffff387e98341efd7` | 21275 | **não** | **não** |

`git log --all -- <path>` neste worktree = só `80166268` (r2). Zero blob local de 21275 B. Archive `openspec/changes/archive/2026-08-29-card-792-monitor-risco-explicito/design.md` declara `/monitor` em prosa; **sem** `live_route:` parseável.

### Landmarks D6 vs produto live

| Rota | Chave D6 | Live |
| --- | --- | --- |
| `/monitor` | `table.signals`; texts Status / Preço / Distância / 7d / Risco até stop / Tags / Operar / Par / Estratégia | `MonitorStatusTab.tsx` L1219–1230 `className="signals"`; Distância/7d sob `showTechnicalColumns`; Operar é **botão** L1392, não `<th>` |
| `/favorites` | `table.fav-strategies`; Estratégias favoritas / Symbol / Estratégia / Ações | `FavoritesDashboard.tsx` L1442 `className="fav-strategies"`; CSS `table.fav-strategies` em `index.css` |
| `/combo/discovery` | selectors `[]`; Descoberta de estratégias swing / Preflight / Rascunho de varredura | `DiscoveryPage.tsx` h1 + “Preflight do servidor” + h2 rascunho; App `Route path="/combo/discovery"` |
| `/combo/select` | `.combo-page`; Available Templates | `ComboSelectPage.tsx` `combo-page` + h2; CSS `.combo-page` |

### Relacionados (board ≠ `gh issue close`)

| Card | Board | GitHub issue |
| --- | --- | --- |
| #792 | **Pronto** | OPEN |
| #673 | **Pronto** | OPEN |
| #530 | **Pronto** | OPEN (título issue ≠ título do item) |

---

## Hunt (furos pedidos) — contrato vs live

| Furo | Contrato | Live | Disposition |
| --- | --- | --- | --- |
| Contradição vs código/specs | D1–D12 + Q1–Q5=A; spec ADDED/MODIFIED; Apply 1–7 | L165–170 só 3 md; critic L63 chrome; catálogo ausente; r2 hash T0; r1 só no PR #802; D6 alinhado às 4 rotas | **CLOSED** (P2 residual: path de recovery + match de selector) |
| Apply files em falta | 7 paths: helper, YAML, `process_event.py`, testes, fixture r1, skill | Novos ainda não existem (pré-Apply). Fixture **não** está em `develop`; bytes exactos em `0576fd37`. Skill / `process_event` / `test_process_event` existem para editar | **CLOSED** |
| Dual-write | D11 Σ yaml intacto; Q3 `copied` ≠ proxy handoff; #673 sem dump HTML | T5 yaml inalterado; change não edita `openspec/specs/*` main; `design.md` sem HTML | **CLOSED** |
| Scope creep UI produto | MUST NOT `backend/**` `frontend/src/**` proto live #792 `DESIGN.md` | Apply contract = harness; zero `card-799-*` em `prototypes/`; `surface: new` + `live_route: N/A` só documentam Q5 | **CLOSED** |
| Reabrir #792 / #673 / #530 | Non-Goals; fixture ≠ path live; Apply ainda lê proto (#530); sem HTML no `design.md` (#673) | Três **Pronto**; D9 MUST NOT escrever no path r2; spec MODIFIED conserva disco-como-layout | **CLOSED** |
| `UI impact: none` bypass de coluna | Anti-bypass; Prototype N/A; T7 permanece | Status **Design**; sem HTML; `## Design Critique` ausente (autor); T5 é do pai após PASS | **CLOSED** |
| Q1–Q5 reabertas | Todas A; Open Questions vazias | design D1–D5 = A; Q2 rejeitou Playwright em T5; Q4 fail-closed; Q5 campo parseável | **CLOSED** |

---

## Critique (contrato vs live)

Issue #799 sintetizado (Q1–Q5=A no body). Pacote OpenSpec: ADDED `design-route-clone-gate` + ADDED/MODIFIED nas três capabilities nomeadas.

| Entra | Onde |
| --- | --- |
| Q1=A skill + A/B **e** `G_design` | D1/D7; spec `files_g_design` composto; tasks 2.1 / 4.1 |
| Q2=A catálogo + HTML estático; T5 offline | D2/D6; spec static HTML; tasks 1.1 / 1.2 / 2.1 |
| Q3=A soma `COPIED:start`/`COPIED:end` | D3/D8; spec copied; tasks 1.2 / 3.1 |
| Q4=A fail-closed sem chave HEAD; sem self-service na mesma change de produto | D4; spec catalog HEAD; tasks 1.2 / 3.1 |
| Q5=A `live_route:` / `surface:`; existing exige; new/`N/A` isenta; sem campo + proto affected ⇒ recusa | D5; spec parseable; tasks 1.2 / 3.1; este `design.md` já tem os campos (none + N/A + new) |
| Galeria = P0; A/B URL viva; `/login` ≠ rota; toggle morto = P0 (T5 não vê toggle) | D10; spec impeccable-design-gate ADDED; task 4.1 |
| Fixture r1 `068581d6…` BLOCKED; r2 `1a1ff265…` não é a fixture | D9; spec gallery fixture; tasks 1.3 / 3.1 / 3.2 |
| Sem produto / sem #792 Apply / sem fork vendor / sem credencial / sem Σ novo | Non-Goals; D11; tasks 5.1 |

`## Open Questions` = nenhuma Q da grelha. Prototype N/A justificado. Sem HTML. Sem rewrite `DESIGN.md`. Sem `## Design Critique` pré-preenchido. T7 humana permanece.

Aceite observável pós-Apply: T5 `g_design is None` recusa r1 + `live_route: /monitor`; UI none + 3 md + specs transita; `classify(r1, /monitor)` BLOCKED com sha256 exacto; worktree-only key não passa; affected + proto sem campo recusa; new/`N/A` isenta; skill deixa de tratar 224px/`--bg-*` como prova de clone.

---

## Findings

### P0

(nenhum)

### P1

(nenhum)

### P2

- **D9 “histórico git” no clone local é falso.** `develop` squash (`80166268`) só tem r2. Bytes r1 (21275 B, sha256 `068581d6…`, sem `table.signals` / sem `COPIED:*`) estão no commit `0576fd37` do PR #802. Disposition: Apply MUST `git show 0576fd37:frontend/public/prototypes/card-792-monitor-risco-explicito/index.html` (ou `gh api …?ref=0576fd37`) **para** `scripts/process-fsm/fixtures/792-r1-gallery.html` e verificar o sha256. MUST NOT `git checkout` nesse path live (reabriria #792).
- **Spec “selector como substring” vs D6 “aceitar `class="signals"`”.** Markup live é `className="signals"` / `fav-strategies` / `combo-page`. CSS de `index.css` **contém** `table.signals`, `table.fav-strategies`, `.combo-page` — um clone estilo r2 (CSS copiado) passa o literal. Um dump só do DOM falha. Disposition: Apply MUST implementar o parêntese D6 (token de classe conta), não só a frase “appear as substring” do spec.
- **D7 furo proto-sem-`UI impact`.** Campo ausente + proto presente não está na árvore (none-by-default só sem proto; Q5 só dispara com `affected`). Disposition: fail-closed se houver proto e faltar `UI impact:` parseável (tratar como affected para Q5), ou documentar none. Não é o DoD deste card.
- **Proposal Impact lista “delta em `openspec/specs/…`” como Apply.** O Apply contract não. Disposition: Apply MUST NOT editar specs main; deltas já estão na change; archive no lote.

### P3

- Task 3.3 (“Design → Pronto para Dev já ocorreu”) é boilerplate de Apply; hoje Status=Design. No Apply torna-se verdadeira.
- Spec A/B agrupa `Operar` com headers; live é botão de linha. Catálogo `texts` ainda casa por substring.
- `Distância` / `7d` dependem de `showTechnicalColumns`; D6 assume a vista admin (como o r2).
- `/combo/selectCrypto` e rotas menores (`/profile`, `/help`) sem chave — fail-closed (já em Open Questions).
- Pin `v1.1.4` volta a copiar `design-critic`; edição só no consumidor. Issue pede esse path; próximo pin pode sobrescrever (não é card de produto).
- Folha de tokens continua SHALL na spec main e ausente no disco; D12/Non-Goal = não criar. Residual pré-existente.
- `declare_ui_impact` (T3) continua sem predicado em `process_event.py` (facto T0; fora de escopo).

---

## Audit

- A11y / responsive / browser / detector visual: **N/A (`UI impact: none`)**. Prototype N/A confirmed. Playwright visual não correu. **Browser gate: N/A (no UI).** Q1–Q5=A: não se exige HTML nesta coluna.
- Dual critic / T7: snapshot desta coluna = este arquivo. Gist OpenSpec não é a crítica.
- FSM: sem task de estado/evento/`enabled_tools`. Status já Design; T7 Alan; T5 parent. `UI impact: none` não pulou Design nem Aprovação de Design.
- Product UI Cripto: zero `frontend/src/` / `backend/` / HTML de produto no Apply contract.
- #792 Pronto / path r2 intacto neste worktree. #673 (sem dump HTML) e #530 (Apply lê proto) não reabertos no texto.
- Pin `v1.1.4` inalterado. Catálogo ainda não existe (seed = Apply).

---

## Trace

1. Live: `files_g_design` = 3 md + specs; critic L63 = chrome; catálogo ⊥; r2 `1a1ff265…` 95314 B com landmarks + `COPIED`; r1 `068581d6…` 21275 B no PR #802, não em `develop`.
2. Issue #799 DoD 1–9 = clone+landmarks, P0 galeria, T5 recusa landmarks/`copied`/sem chave/sem campo, new isenta, fixture r1 BLOCKED, Q1–Q5=A.
3. Design D1–D12 + Apply contract 1–7 pinam o DoD; seed D6 das quatro rotas bate no React/CSS live.
4. Spec ADDED `design-route-clone-gate` + ADDED/MODIFIED nas três capabilities; `openspec validate --strict` verde.
5. Tasks 1.1–1.3 / 2.1–2.2 / 3.1–3.2 / 4.1 / 5.1–5.2 são o ouro que o Apply falha se deixar T5 só com 3 md, pachar o proto #792, meter Playwright em `submeter_design`, ou tratar r2 como fixture.

---

## Disposition

Zero P0/P1 abertos. Os furos pedidos estão fechados no contrato (contradições vs live mapeadas e corrigidas pelo DoD; Apply files nomeados; dual-write yaml/HTML/main-specs fechado; zero UI produto; #792/#673/#530 Non-Goal + MUST NOT no path r2). Residuais P2 (recovery r1 via `0576fd37` e não checkout no path live; match de selector D6 vs substring do spec; proto sem `UI impact:`; proposal vs Apply contract nas specs main) não colapsam o DoD se Apply seguir D4–D10 / tasks 1.3 / 5.1. Detector/browser visual **N/A (no UI)**. Prototype N/A. `files_g_design` passa. Design Critique **não** pré-preenchido. Q1–Q5=A intactas.

Pai: com A também PASS e zero P0/P1, colar `## Design Critique` e `process_event submeter_design`. Sem polish neste transcript. MUST NOT editar `design.md` daqui. MUST NOT `process_event` neste filho.

### Verdict

**PASS**
