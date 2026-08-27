# Snapshot — card #720 `card-720-opencode-three-adapters` (Assessment B2)

- Card: #720
- Change: `card-720-opencode-three-adapters`
- Critic: isolated Design Critic B re-run (B2) after author patch of B P1; no transcript inherit; no inherit of A/B1
- UTC: 2026-08-27T20:20:59Z
- Tuple: `.grok/rules/process-fsm-page.md` ausente. `resolve(cwd, cwd, issue_id=720, status="Design")` → `q=Design` `bound_card=720` `q_git=card-720-opencode-three-adapters`. Sem `status` inject: `q=None`. `enabled_events(Design)`: recriticar, submeter_design, cancelar. Write produto deny. Esta onda só `.impeccable/critique/**`.
- UI impact: none (harness/hooks/docs; nenhuma rota, shell, componente ou copy de produto)
- Prototype: N/A confirmed (sem HTML desta change; `frontend/public/prototypes/` não tem slug 720; Playwright não correu)
- Detector/browser desta coluna: N/A justificado — sem superfície visual nova ou alterada
- `openspec validate card-720-opencode-three-adapters --type change --strict`: valid
- `files_g_design`: True (`proposal.md` / `design.md` / `tasks.md` + cinco spec deltas)
- Surfaces lidas (read-only, ficheiros **actuais** — não se assume o patch): issue #720 body + 2 comentários; change `proposal.md` / `design.md` (D1–D12, G1–G18) / `tasks.md`; spec deltas `process-harness`, `cursor-harness`, `developer-tooling`, `process-fsm-guard`, `process-fsm-paging`; live `scripts/process-fsm/guard.py` (`WRITE_TOOLS` / `PATH_KEYS` / `normalize` / `extract_path` / `decide`); `board_status.is_status_edit_command` + `STATUS_FIELD_ID`/`bd47fbe8`; `fsm.CARD_GIT_RE` + `product_globs`/`design_globs`; `.cursor/hooks/process-fsm-guard.sh` fallback; `process_event.files_g_design`

Prior P1 (B1) treated as closed *only if* current goldens/spec/tasks discriminate parse of `patchText` from empty-path deny. Checklist do prompt: G3 `extract_paths()` do path de produto; G17 allow Design+`card-*` só de `patchText`; G18 `*** Move to:` dest + develop deny; G4/G5 empty-path deny; `tasks.md` lista; spec delta exige o parse.

---

## Brief

Kaizen P0: terceiro adapter OpenCode **1.18.18** sobre o mesmo `decide()` / `page()`. Dialeto nativo `{ tool, args }` (`filePath` / `patchText` / `command`); plugin auto-load em `.opencode/plugin/` **sem** `opencode.json`; deny = **throw**; paging = inject `experimental.chat.system.transform`; detector Impeccable nos três via o mesmo `hook.mjs`; fail-open no detector; lock machine continua morto; sem Auto OpenCode/Grok; `UI impact: none`.

B2 só reabre o P1 de B1 se os ficheiros actuais ainda colapsarem G3–G5 com empty-path, ou se o patch introduzir P0/P1 novo. Não herda veredito A nem B1.

Audience: operador do harness (Cursor + Grok + OpenCode). Outcome: write ilegal `backend/`/`frontend/src/` com `q_git=develop` no OpenCode é deny/throw, e `apply_patch` legal de OpenSpec em Design+`card-*` continua allow. Direction: pele/tradução, não segundo processo.

---

## Critique (P1 re-verify)

### Checklist B1 → ficheiros actuais

| Exigido | Onde (actual) | Fecha? |
| --- | --- | --- |
| G3 assert `extract_paths()` do path de produto (não empty-path deny) | `design.md` G3: deny **e** `extract_paths()==["backend/app/main.py"]` (não empty-path). Spec Guard scenario *OpenCode apply_patch of product on develop is denied*: `extract_paths()` equals that list **AND** deny **AND** deny is `write_produto`, not empty-path. Task 6.1: G3 deny **e** `extract_paths()==["backend/app/main.py"]`. | **sim** |
| G17 `apply_patch` allow Design+`card-*` só de `patchText` | `design.md` G17: `*** Add File: openspec/changes/card-720-opencode-three-adapters/design.md`, path **só** de `patchText`, sem `filePath`; Design + `card-720-*`; allow **e** `extract_paths()` dessa lista. Spec *OpenCode apply_patch OpenSpec path from patchText is allowed*: no `filePath`, status Design, `q_git` matches `card-720-*`, allow, `evaluate(write_produto)` not invoked. Task 6.1: G17 allow (path só de `patchText`). | **sim** |
| G18 `*** Move to:` dest extraído + develop deny | `design.md` G18: `*** Update File: docs/note.md` + `*** Move to: backend/app/moved.py`; develop; deny **e** `extract_paths()` contém dest (se o parse ignorasse dest, `docs/note.md` seria other → allow). Spec *OpenCode apply_patch Move to product dest is denied*: contains dest **AND** deny **AND** parse that only kept `docs/note.md` MUST NOT pass. Task 1.1: destino do Move; `decide()` qualquer `product_globs`. Task 6.1: G18 dest em `extract_paths()`. | **sim** |
| G4/G5 ainda empty-path deny | `design.md` G4 `patchText=""` deny + `extract_paths()` vazio; G5 Begin/End sem path deny + `extract_paths()` vazio. Spec *Empty OpenCode write path is not allow* + scenarios empty `patchText` / no extractable path. Task 1.2 + 6.1: G4/G5 empty-path deny. | **sim** |
| `tasks.md` lista estes goldens | Task 6.1: G1–G12 e G17–G18; G3 extract_paths produto; G17 allow `*** Add File:` OpenSpec; G18 `*** Move to:`; G4/G5 empty-path; G8 field id. Task 1.1: `extract_paths()` + quatro marcadores live + any-path `write_produto`. Apply contract: G3/G17/G18 MUST assert `extract_paths()`. | **sim** |
| Spec delta exige o parse | `process-fsm-guard` ADDED: parse `*** Add File:` / `*** Update File:` / `*** Delete File:` / `*** Move to:` (dest); `extract_paths()` every marker path in order; `decide()` any `product_globs` → `write_produto`. | **sim** |

Discriminadores que o P1 pedia (G3–G5 já não devolvem o mesmo token):

- Empty-path deny **sozinho** passa G4/G5 e **falha** G17 (precisa allow + path extraído).
- Parse sem usar dest falha G18 (docs = other → allow).
- `decide()` só no primeiro path (`extract_path()` compat) falha G18 deny (primeiro = `docs/note.md`).
- Blanket deny de todo `apply_patch` falha G17.
- `extract_paths()` sem ligar a `decide()` falha G17 allow (empty-path deny no envelope) **ou** G18 deny.

`docs/note.md` não está em `product_globs` (`backend/**`, `frontend/src/**`) nem em `design_globs` (`openspec/changes/**`, `frontend/public/prototypes/**`) — o dest `backend/app/moved.py` é o único produto no envelope G18. `design_globs` cobre o path G17.

D3 agora SHALL: goldens de `apply_patch` com path extraível MUST assert `extract_paths()` (não só deny). G9 (`edit` + `filePath` OpenSpec) permanece; o allow `apply_patch` que faltava é G17.

### G8 / G14 (eram P2 em B1 — não reabertos como P1)

- G8 agora traz `--field-id PVTSSF_lAHOAAHtBM4BV8b2zhRUdMM --single-select-option-id bd47fbe8`, iguais a `board_status.STATUS_FIELD_ID` e option Design. `is_status_edit_command` dispara. Task 6.1 cita os ids. **P2 B1 fechado.**
- Task 4.2 + G14 + spec *OpenCode after maps filePath* / *idle maps to Stop* + `developer-tooling` AND: `args.filePath` → `file_path` + `PostToolUse`; `session.idle` → `Stop`. **P2 B1 fechado.**

### Live `guard.py` (esperado pré-apply — não é achado de Design)

Confirmado neste worktree: `WRITE_TOOLS` sem `edit`/`apply_patch`; `SHELL_TOOLS` sem `bash`; `PATH_KEYS` sem `filePath`; `normalize()` só `tool_name`/`toolName` + `tool_input`/`toolInput`; sem `extract_paths()`; `decide()` `if not path: return _allow()`. O pacote **especifica** o fecho (D2–D4, G3/G17/G18, spec ADDED, tasks 1.1–1.2 / 6.1). P0 live de produto ≠ P0 de Design.

### `## Design Critique` pré-PASS?

**Não.** Zero matches na change. `design.md` termina em Prototype / Validation / Impeccable pipeline N/A. Filho autor não escreveu a seção. Correcto.

---

## Critique (resto do contrato — UI none)

### Issue ↔ proposal ↔ design ↔ tasks ↔ specs

Issue #720 (grelha vazia; comentário canónico exacto) continua 1:1. Vocabulário do issue não inventado. Não-entra (lock machine, segundo Guard/detector, T0–T17 em `.opencode/`, `opencode.json`, `/opsx-*`, produto, upgrade, #614) em Non-Goals + Apply contract + tasks 1.4 / 2.3 / 4.3 / 5.1.

Aceite OpenSpec/protótipo Design+`card-<id>-*` **allow** agora cobre `apply_patch` (G17) além de `edit` (G9). `bash` tee = G7; `item-edit` Status = G8 (com field id). Empty `patchText` = G4/G5.

Dois módulos: task 2.1 throw ≠ task 4.2 never-throw. Paging task 2.2 no Guard plugin ou irmão, não no detector.

`openspec/config.yaml` continua Apply (D10 / task 5.2). Sem leak do glob de Design neste turno.

Paging: G13/`page()` ≤20 sem `release-guard`. Inject reusa o compilador. Residual: 6.2 testa `page()`, não `system[]` mesclado pelo 1.18.18 (P3).

### Escopo vs recorte

Terceiro adapter + detector nos três; sem lock / json / opsx / produto / dual-write T0–T17. Implementável na ordem D11 (agora G1–G12 **e** G17–G18 no passo 1).

### Regressão #668

Dialeto acresce; `emit()` dual permanece. Empty-path deny no conjunto OpenCode `{write,edit,apply_patch}` aperta Grok `write` vazio (fail-closed). Cursor `Write` intacto. Detector Grok = JSON aditivo `PostToolUse`+`Stop`; task 4.1 não relitiga PreToolUse/SessionStart. Sem aresta FSM nova. T1/T7/T15 Alan-only.

### Riscos operacionais

Plugin não carregado = write passa; #5894 subagent `task`; tool nova → allow (#611); Python-down no plugin OpenCode (task 2.1 chama `guard.py` directo, G12 é o sh Cursor/Grok) — residuais do issue / B1 P2, não recorte. Auto claims / AGENTS.md >40 / throw-vs-JSON / inject-vs-hop: fechados no desenho.

### Superfície visual

Nenhuma superfície de produto nova/alterada sem classificação: `frontend/src/**` / produto `backend/` = none; Prototype N/A; detector `hook.mjs` = pele de harness, não tela; TUI vendor = Non-Goal. `UI impact: none` justificado.

---

## Audit

- A11y / responsive / browser / detector visual: N/A (`UI impact: none`). Prototype N/A confirmed. Playwright não correu.
- Dual critic / T7: não enfraquecidos. Snapshot desta coluna = este arquivo.
- FSM yaml: sem task de estado/evento/`enabled_tools`. T1 Alan; T7 Alan; T5 parent `submeter_design`.
- Package: `files_g_design` True. `openspec validate --strict` valid.
- Product UI: zero `frontend/src/` / produto `backend/` no Apply contract.
- Dois plugins vs um: tasks 2.1 ≠ 4.2.
- Sem `## Design Critique` pré-preenchido.

---

## Trace

1. B1 P1: G3–G5 all deny colapsados com empty-path; G9 só `edit`; sem `Move to:`; sem allow `apply_patch` de `patchText`.
2. Patch do autor (ficheiros actuais): D3 `extract_paths()` + any-path `write_produto`; G3/G17/G18; G4/G5 intactos; task 1.1/6.1; spec Guard scenarios de parse/allow/Move.
3. G8 field id + G14 mapa detector (P2 B1) também patched; não eram o P1.
4. Live Guard ainda fail-open no dialeto nativo (esperado pré-apply).
5. `## Design Critique` ausente (não pré-PASS).

---

## Findings

### P0

(nenhum)

### P1

(nenhum — P1 B1 fechado nos goldens + spec + tasks; sem P0/P1 novo)

### P2

- **G12 (fallback bash) continua fora do caminho live do plugin OpenCode.** Task 2.1 chama `guard.py`/`decide()`. G12 testa `.cursor/hooks/process-fsm-guard.sh` com JSON OpenCode. Python-down na sessão 1.18.18 não herda o fallback (fail-open, classe “plugin não carregado”). Disposition: **accepted-residual** (mesmo P2 B1; Apply pode invocar o sh irmão).
- **Plugin não carregado / folder untrusted = write passa.** Residual do issue. Homologação 6.5 registra load. Disposition: **accepted-residual**.
- **#5894 `tool.execute.before` em subagent `task`.** Não live-testado em TUI; ensaio 6.5; sem upgrade. Disposition: **accepted-residual**.
- **Tool nova fora da lista canónica → allow (#611 / G10).** Upgrade = filho. Disposition: **accepted-residual**.
- **Stubs OpenCode sem gerador/CI stale** (Grok tem `grok_stubs.py`). Issue não exige gerador; G16 cobre ≤8 / sem T0–T17. Disposition: **accepted-residual**.

### P3

- `proposal.md` What Changes ainda cita só `extract_path()`, não `extract_paths()` / G17–G18. Design + spec + tasks carregam o parse. Disposition: **accepted-residual**.
- Sem golden de `*** Delete File:` (spec lista os quatro marcadores; Add/Update/Move cobertos). Disposition: **accepted-residual**.
- Sem golden do rename inverso (produto → `docs/`); spec “every marker path” + any `product_globs` já obriga deny se Apply cumprir o SHALL. Disposition: **accepted-residual**.
- Task 2.2 “mesmo plugin ou módulo irmão” vs D5 (dois arquivos nomeados). Apply lê D5+contrato: paging no Guard. Disposition: **accepted-residual**.
- Requirement heading `one nucleus and two adapters` (identidade OpenSpec MODIFIED); corpo three. Disposition: **accepted-residual**.
- 6.2/G13 testam `page()` isolado, não `system[]` concatenado pelo 1.18.18. Disposition: **accepted-residual**.
- Task 6.4 `openspec validate` sem `--strict` (esta onda correu `--strict` = valid). Disposition: **accepted-residual**.
- `## Design Critique` ausente (não pré-PASS). Pai preenche depois desta onda.

### Disposition

P1 B1 **fechado**: G3 testemunha `extract_paths()` do produto e deny `write_produto` (não empty-path); G17 é o allow `apply_patch` Design+`card-*` só de `patchText`; G18 extrai dest `*** Move to:` e deny develop; G4/G5 continuam empty-path deny; task 6.1 lista; spec delta exige o parse. Zero P0/P1 aberto. P2 = residuais do issue / plugin path (não recorte). Não editar `design.md` por estes P2. Prototype N/A confirmed. `files_g_design` True. Design Critique **não** pré-PASS.

### Verdict

**PASS**
