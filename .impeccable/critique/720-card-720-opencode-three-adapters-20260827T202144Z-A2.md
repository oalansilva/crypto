# Snapshot — Assessment A2 · card #720 `card-720-opencode-three-adapters`

- Card: #720 P0 kaizen — Harness: terceiro adapter OpenCode — uma lei, três clientes
- Change: `card-720-opencode-three-adapters`
- Critic: Assessment A re-run (A2) após patch do P1 B; isolado; sem transcript do pai; sem partilha com B
- Modelo: inherit
- UTC: 2026-08-27T20:21:44Z
- Tuple: `.grok/rules/process-fsm-page.md` ausente. `scripts/process-fsm/resolve.py` → `bound_card=720` `q_git=card-720-opencode-three-adapters` `q=None` (board não injectado neste isolado). Issue + prompt do pai: `Status=Design`. Write produto deny. Esta onda só `.impeccable/critique/**`.
- UI impact: **none** (justificado: harness/hooks/docs/specs/testes de processo; nenhuma rota, shell, componente ou copy de produto)
- Prototype: N/A (sem HTML em `frontend/public/prototypes/` ligado a #720; `openspec validate card-720-opencode-three-adapters --type change --strict` = valid; `files_g_design` True)
- Impeccable visual / Playwright / detector-de-tela desta coluna: N/A justificado. Detector automático como **pele de harness** (Grok+OpenCode → `hook.mjs`) entra no card, não nesta crítica de tela.
- Method: body grelhado #720 (fronteira vazia) + 2 comentários live; `proposal.md` / `design.md` (D1–D12, G1–G18) / `tasks.md` 1.1 / 4.2 / 6.1 / 6.2; change spec `process-fsm-guard` (G3/G17/G18 scenarios) + `process-harness` `cursor-harness` `developer-tooling` `process-fsm-paging`; live `guard.py` `extract_path`/`decide` (pré-Apply); `board_status.is_status_edit_command`; `CARD_GIT_RE`; binário live `/home/ubuntu/.opencode/bin/opencode` `--version 1.18.18` (`*** Move to:` após `*** Update File:`).

---

## Brief

**Problema (inalterado):** o núcleo #668 já é lei com dois adapters. Abrir o repo no OpenCode **1.18.18** não é contrato: `normalize()` não vê `{ tool, args }` e write ilegal em `backend/` + `q_git=develop` cai no early-return allow.

**Patch desta onda:** o P1 B era goldens de `apply_patch` deny-only (G3–G5 colapsavam com empty-path deny; sem `extract_paths`; sem allow OpenSpec via `patchText`; sem `*** Move to:`). Autor afirma G3 agora afirma `extract_paths`, G17 allow (OpenSpec path só de `patchText`, Design+`card-*`), G18 deny com dest `*** Move to: backend/app/moved.py`.

**Outcome / Direction / Scope:** inalterados (terceiro adapter = tradução sobre o mesmo `decide()` / `page()`; sem dual-write; sem lock machine; sem `opencode.json`; sem `/opsx-*`; sem produto).

---

## Re-check do P1 B

**P1 B (aberto na onda anterior):** goldens `apply_patch` eram todos deny; implementação que mete `apply_patch` no conjunto empty-path-deny e **nunca** parseia `*** Update File:` / `*** Move to:` passava G3–G5; G9 (único allow OpenSpec) era `edit`+`filePath`, não `apply_patch`. Pedido: golden allow `apply_patch` de `openspec/changes/…` Design+`card-<id>-*` **e/ou** G3 afirmar path extraído; mais um caso `*** Move to:`.

**Estado actual — FECHADO.** O autor fez os três discriminadores, não só um:

| Pedido B | Onde agora |
| --- | --- |
| G3 afirma path extraído, não só deny | Tabela G3: deny **e** `extract_paths()==["backend/app/main.py"]` (não empty-path). Spec scenario `OpenCode apply_patch of product on develop is denied`: `extract_paths()` equals that list **AND** deny is `write_produto`, not empty-path. Task 6.1: «G3 deny **e** `extract_paths()==["backend/app/main.py"]`». |
| Allow `apply_patch` OpenSpec Design+`card-*` path só de `patchText` | G17: `*** Add File: openspec/changes/card-720-opencode-three-adapters/design.md`, sem `filePath`, Design + `card-720-*` → allow **e** `extract_paths()` equals that path. Spec scenario `OpenCode apply_patch OpenSpec path from patchText is allowed` (+ `evaluate(write_produto)` not invoked). Task 6.1. |
| Caso live `*** Move to:` dest produto | G18: `*** Update File: docs/note.md` + `*** Move to: backend/app/moved.py`, develop → deny **e** `extract_paths()` contém dest. Spec: parse that only kept `docs/note.md` MUST NOT pass. Task 1.1: dest do Move; `decide()` any `product_globs` path = `write_produto`. Task 6.1. D3: `extract_path()` primeiro path (compat); goldens com path extraível MUST assert `extract_paths()`. |

**Porque o colapso G3–G5 não volta:**

- Empty-path deny de **todo** `apply_patch` passa G3–G5/G18 no token deny, mas **falha G17** (allow).
- Parse só do primeiro `*** Update File:` passa G3/G17, mas **falha G18** (`docs/note.md` é `other` → allow hoje; dest produto é o que força deny).
- `extract_paths()` só para o teste, `decide()` ainda no first-path: G18 decide falha.
- G4/G5 agora também dizem `extract_paths()` vazio — Begin/End sem path não pode inventar path e ainda assim empty-deny.

Binário 1.18.18: parser live é `*** Update File:` e linha seguinte opcional `*** Move to:` (destino = `movePath`). G18 é exactamente esse formato. `*** Move File:` continua 0 hits. Marcador do issue continua mapeado, não inventado.

Apply contract + Migration (1) exigem G1–G12 **e** G17–G18 no núcleo; G3/G17/G18 MUST assert `extract_paths()`.

Não reabrir este P1.

(Nota lateral, não o P1 B: G8 ganhou field/option id `PVTSSF_…` / `bd47fbe8`, o que fecha o P2 B do classificador `is_status_edit_command`. G14/task 4.2/6.2 agora mapeiam `filePath`→`file_path` e `session.idle`→`Stop`. Fora do P1; P2 detector parcialmente fechado.)

---

## Critique

### 1. Fidelidade ao #720 grelhado

Body live (2026-08-27T19:49:50Z; grelha: fronteira vazia). Comentário canónico exacto: `grill-card: fronteira vazia; história no body; à espera de T1 (Alan).` Design não reentrevista. Patch G17/G18 é o aceite «OpenSpec/protótipo Design+`card-<id>-*` allow» no envelope `apply_patch`, que o P1 B mostrou faltar.

| Entra do issue | Onde no Design / spec / tasks |
| --- | --- |
| Alvo fixo 1.18.18; sem upgrade | D1; Non-Goals; lista canónica = golden + ensaio |
| Terceiro dialeto `{ tool, args }` (`filePath` / `patchText` / `command`); tools `write`/`edit`/`apply_patch`/`bash` | D2–D3; spec `process-fsm-guard` ADDED; tasks 1.1–1.2 |
| Path vazio / `patchText` sem path **não** vira allow | D4; G4–G6; spec Empty OpenCode write path |
| `apply_patch` + path de produto + develop → deny | G3 + `extract_paths`; spec write_produto not empty-path |
| OpenSpec Design + `card-<id>-*` allow (envelope OpenCode) | G9 `edit`; **G17 `apply_patch` patchText-only** |
| Plugin `.opencode/plugin/` singular (#395); auto-load; **sem** `opencode.json`; throw no deny | D5–D6; spec plugin throw; tasks 2.1 / 2.3 |
| Paging `experimental.chat.system.transform`; inject, não hop Grok | D7; spec `process-fsm-paging` ADDED; task 2.2 |
| Pele irmão #668; **sem** `/opsx-*` | D8; spec No opsx; task 2.3 |
| Stubs ≤8 linhas MUST Read; 1.18.18 não descobre `.cursor/skills/` | D8; spec OpenCode stub is a bridge; task 3.1 |
| Detector nos três; mesmo `hook.mjs`; fail-open | D9; spec Impeccable detector is on all three; tasks 4.1–4.3; G14 mapa |
| Specs dois → três; lock machine / `opencode.db` / lease / attestation / `opencode.json` continuam proibidos | D10; `process-harness` / `cursor-harness` / `developer-tooling` |
| `AGENTS.md` três clientes; sem Auto OpenCode/Grok; ≤40 | D12; G15; task 3.2 |
| Decision log: revoga unicidade #562; **não** a morte do lock machine | D10; task 3.3 |
| Ensaio deny + detector = homologação / Auto, não merge | D11–D12; vocab do issue; task 6.5 |
| bash `tee`/`>` develop deny; `item-edit` Status → deny | G7; G8 com field id live; spec |
| `UI impact: none`; sem produto | UI impact / Prototype / pipeline N/A; task 6.4 |

**Vocabulário** do issue intacto. `_Avoid` nos Non-Goals + Apply contract.

**Não entra — não reaberto:** lock machine, segundo Guard/detector, T0–T17 em `.opencode/`, `opencode.json`, `/opsx-*`, produto, upgrade, hop Grok no OpenCode, Auto sem ensaio, artigo #614.

`Open Questions: Nenhuma bloqueante` bate com fronteira vazia. Residuais (#5894, plugin carregou) ficam no ensaio.

Proposal «New Capabilities: (nenhuma)» continua correcto. Proposal ainda diz só `extract_path()` (não `extract_paths`/G17/G18) — nit, o contrato de Apply vive em design/tasks/spec.

### 2. Escopo vs recorte

Terceiro adapter + detector; sem lock / json / opsx / produto. Patch G17/G18 **não** alarga recorte: é o aceite de `apply_patch` que o issue já pedia. Pele = dois módulos (Guard throw vs detector never-throw). Task 2.2 paging no Guard plugin ou irmão — não mistura throw do detector. Implementável.

### 3. Regressão de produto/processo (#668)

- Terceiro envelope ao lado; `emit()` dual permanece. Spec velha Cursor/Grok **não** é REMOVE.
- P0 live em `guard.py` (confirmado neste worktree): `WRITE_TOOLS` sem `edit`/`apply_patch`; `SHELL_TOOLS` sem `bash`; `PATH_KEYS` sem `filePath`; `normalize()` ignora `{ tool, args }` → `extract_path` None → `decide()` allow. O pacote **especifica** o fecho; o ouro G3/G17/G18 agora **prova** parse. Não é achado de Design.
- Empty-path deny no conjunto OpenCode `{write, edit, apply_patch}` aperta Grok `write` vazio (hoje allow). Fail-closed, não autoriza write legal. Aceitável.
- Fallback bash (task 1.3 / G12) continua o wrapper Cursor/Grok; plugin OpenCode (task 2.1) chama `guard.py`/`decide()`. Python-down no OpenCode = fail-open residual (P2, não novo).
- Detector Grok: `PostToolUse`+`Stop` aditivos no JSON que já tem `PreToolUse`+`SessionStart`. Apply contract: não relitigar Guard/paging.
- Auto: Cursor Auto permanece; Grok/OpenCode cooperativos. G15 + `test_agents_md_is_stub`.
- Dual-write: G16 + spec Dual-write forbidden alarga a `.opencode/`.
- `process_event`: G8 deny Status item-edit (agora com field id que o classificador live exige). Sem aresta nova.
- `openspec/config.yaml` continua Apply (task 5.2). Sem leak do glob de Design.

### 4. Riscos operacionais (rubrica)

**Plugin não carregado = write passa.** Residual explícito. **accepted-residual.**

**#5894 `tool.execute.before` em subagent `task`.** Residual explícito; ensaio 6.5; sem upgrade. **accepted-residual.**

**Tool desconhecida → allow (#611).** D3 + G10. **accepted-residual.**

**Auto claims / AGENTS.md >40 / throw-vs-JSON / inject-vs-hop:** fechados no desenho (G15, D6, D7, spec).

**`extract_path` first vs `decide` any-path:** D3/task 1.1/G18 fecham o rename other→produto. Inverse (produto→other) cai no `*** Update File:` de G3 se o parse dos quatro marcadores existir. Sem golden `*** Delete File:` — residual P3, spec/task 1.1 já listam o marcador.

**G12 fora do plugin OpenCode:** P2 aceite (fail-open, classe plugin não carregado).

### 5. Specs / tasks vs design.md (G1–G18 vs 6.1/6.2)

| Golden | Task |
| --- | --- |
| G1–G12 + **G17–G18** (dialeto, empty path, parse `patchText`, Move to, OpenSpec allow, três clientes, fallback, G8 field id) | **6.1** (texto actualizado) |
| G13 paging ≤20; G14 detector adapter (`filePath`→`file_path`, idle→Stop); plugin throw | **6.2** |
| G15 AGENTS.md; G16 `.opencode/` | 6.3 |

Split 6.1/6.2/6.3 espelha #668. 6.1 não esquece G17–G18. Spec Guard ADDED tem scenarios 1:1 com G3/G17/G18. D3 SHALL `extract_paths()` ordem + dest do Move + any-path `write_produto`.

P3 de clareza (não furo): task 6.1 não cita o reason `write_produto` do G3 (a spec cita); G18 é `contains dest` não equality da lista ordenada `[source, dest]` (a spec SHALL «every marker path in order»); proposal não nomeia `extract_paths`.

Títulos OpenSpec MODIFIED conservam `one nucleus and two adapters` com corpo “three” — correcto para apply. Heading stale = P3.

`cursor-harness` “Column gate is always-on” main continua Cursor+Grok; inject OpenCode em `process-fsm-paging`. P3.

### 6. Superfície visual — classificação

Nenhuma superfície de produto nova/alterada ficou sem classificação.

| Superfície | Classificação |
| --- | --- |
| `frontend/src/**`, rotas, shell, copy | **none** — fora (task 1.4 / 6.4) |
| `backend/` de produto | **none** |
| Protótipo HTML / Playwright | **N/A** — sem pasta `prototypes/*720*` |
| Rubrica Impeccable (fidelidade/carga/a11y/viewport) | **N/A** — sem UI de produto |
| Detector `hook.mjs` em Grok/OpenCode | pele de harness; não é tela; fail-open |
| TUI OpenCode / Grok | **vendor** — Non-Goal |

`UI impact: none` + Prototype N/A + pipeline Impeccable *desta coluna* N/A justificados. `## Design Critique` **ausente** em `design.md` (filho autor MUST NOT pré-preencher PASS).

### 7. Apply contract implementável?

Sim. Ordem D11/Migration: (1) `normalize`/`extract_path`/`extract_paths` + G1–G12 e G17–G18 (2) fallback bash `{tool, args}` (3) plugin Guard throw (4) transform paging (5) stubs + zero opsx (6) detector Grok + plugin impeccable (G14 mapa) (7) `AGENTS.md` + decision-log + `openspec/config.yaml` + specs main.

Pontos de Apply (não BLOCKED): `decide()` **tem** de iterar `extract_paths()` (não só `extract_path()` first); parse dos quatro marcadores live; empty-path deny **antes** do early-return só no conjunto write OpenCode; plugin throw vs detector never-throw em módulos separados.

`openspec validate --strict` já verde neste turno.

---

## Achados

- P0: (nenhum)
- P1: (nenhum) — P1 B goldens `apply_patch` deny-only / sem parse / sem `Move to:` **fechado** por G3 `extract_paths` + G17 allow patchText-only + G18 dest `*** Move to:`.
- P2: `#5894` — `tool.execute.before` no 1.18.18 observa-se no spawn `task`, não nas writes do subagent. Residual explícito + 6.5. Disposition: **accepted-residual**.
- P2: Plugin não carregado / folder untrusted = write passa. Homologação registra load. Disposition: **accepted-residual**.
- P2: Task 2.1 chama `guard.py` directo; G12/task 1.3 são o fallback do wrapper Cursor/Grok. Python-down no OpenCode pode fail-open salvo Apply ligar o wrapper. Disposition: **accepted-residual**.
- P2: Tool nova fora da lista canónica → allow (#611 / G10). Upgrade = filho. Disposition: **accepted-residual**.
- P2: Stubs OpenCode sem gerador/CI stale (Grok tem `grok_stubs.py`). G16 cobre ≤8 / sem T0–T17. Disposition: **accepted-residual**.
- P3: Sem golden `*** Delete File:` (spec/task 1.1 listam os quatro marcadores; G3/G17/G18 cobrem Update/Add/Move). Disposition: **accepted-residual**.
- P3: Task 6.1 não exige assert do reason `write_produto` no G3 (spec exige); G18 é `contains dest` não lista ordenada. G17 já impede empty-path-deny de todo `apply_patch`. Disposition: **false** como furo; nit.
- P3: `proposal.md` / Goals ainda dizem `extract_path()` sem `extract_paths`/G17/G18. Contrato vive em design/tasks/spec. Disposition: **accepted-residual**.
- P3: Requirement title `one nucleus and two adapters` com corpo “three”. Disposition: **accepted-residual**.
- P3: `cursor-harness` “Column gate is always-on” main cita só paging Cursor+Grok. Disposition: **accepted-residual**.
- P3: D9 manda copiar paths de `patchText` no detector `after`; G14/task 4.2 só afirmam `filePath` de UI. Detector fail-open; Guard já deny produto. Disposition: **accepted-residual**.
- Auto claims / AGENTS.md >40 / throw-vs-JSON / inject-vs-hop / dual-write T0–T17 / regressão Guard #668 / superfície visual sem classificar / Design Critique pré-PASS: **false**.

## Disposition

Zero P0/P1 abertos. O P1 B está fechado nos três sítios (tabela G, spec Guard, task 6.1) com discriminadores que não colapsam com empty-path deny. P2 = residuais do issue (plugin load, #5894, #611, Python-down, stubs sem CI) já nomeados para ensaio/Apply. Não editar `design.md` por estes P2/P3.

## Verdict

**PASS** (zero P0/P1 aberto; Prototype N/A justificado; `openspec validate --strict` valid)

## Snapshot

`.impeccable/critique/720-card-720-opencode-three-adapters-20260827T202144Z-A2.md`

Visual/Playwright: N/A (`UI impact: none`).
