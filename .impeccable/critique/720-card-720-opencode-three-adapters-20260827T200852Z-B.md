# Snapshot — card #720 `card-720-opencode-three-adapters` (Assessment B)

- Card: #720
- Change: `card-720-opencode-three-adapters`
- Critic: isolated Design Critic B (no transcript inherit; no Assessment A)
- UTC: 2026-08-27T20:08:52Z
- Tuple: `q=Design` (board/operator; `resolve()` without GitHub leaves `q=None`) `bound_card=720` `q_git=card-720-opencode-three-adapters`; `enabled_events`: recriticar, submeter_design, cancelar; write produto deny
- UI impact: none (harness/hooks/docs; nenhuma rota, shell, componente ou copy de produto)
- Prototype: N/A confirmed (sem HTML, sem `frontend/public/prototypes/`, Playwright não correu)
- Detector/browser: N/A justificado — sem superfície visual nova ou alterada
- Surfaces lidas (read-only): issue #720 body + 2 comments; change `proposal.md` / `design.md` / `tasks.md`; spec deltas `process-harness`, `cursor-harness`, `developer-tooling`, `process-fsm-guard`, `process-fsm-paging`; live `scripts/process-fsm/guard.py` (`WRITE_TOOLS` / `PATH_KEYS` / `normalize` / `extract_path` / `decide`); `paging.py` + `test_paging.py`; `.grok/hooks/process-fsm.json`; `.cursor/hooks/process-fsm-guard.sh` fallback; `.cursor/hooks/impeccable.sh`; `hook.mjs` / `hook-lib.mjs` stdin contract; `openspec/config.yaml`; `.cursor/process-fsm.yaml` globs; `files_g_design`; `board_status.is_status_edit_command`; mains `openspec/specs/{process-harness,process-fsm-guard,process-fsm-paging,developer-tooling,cursor-harness}/spec.md`

---

## Brief

Kaizen P0: terceiro adapter OpenCode **1.18.18** sobre o mesmo `decide()` / `page()`. Dialeto nativo `{ tool, args }` (`filePath` / `patchText` / `command`); plugin auto-load em `.opencode/plugin/` **sem** `opencode.json`; deny = **throw**; paging = inject `experimental.chat.system.transform`; detector Impeccable nos três via o mesmo `hook.mjs` (Grok `PostToolUse`+`Stop`; OpenCode `after`+`idle`); fail-open no detector; lock machine continua morto; sem Auto OpenCode/Grok; `UI impact: none`.

Audience: operador do harness (Cursor + Grok + OpenCode). Outcome: write ilegal `backend/`/`frontend/src/` com `q_git=develop` no OpenCode é deny/throw, e edição de UI nos três dispara `hook.mjs` sem abortar. Direction: pele/tradução, não segundo processo. Scope: capabilities `process-harness`, `cursor-harness`, `developer-tooling`, `process-fsm-guard`, `process-fsm-paging`.

---

## Critique (contrato)

### Issue ↔ proposal ↔ design ↔ tasks ↔ specs

Issue #720 aceite mapeia 1:1 para o pacote, **exceto o furo de golden de `apply_patch` (P1)**:

| Entra (issue) | Onde no pacote |
| --- | --- |
| Alvo 1.18.18; sem upgrade | D1; Non-Goals; Apply contract |
| `normalize()` / `extract_path()` dialeto `{ tool, args }` | D2; task 1.1; spec `process-fsm-guard` ADDED |
| Tools `write`/`edit`/`apply_patch`/`bash`; `filePath` / `patchText` / `command` | D3; G1–G8; spec scenarios |
| Path vazio / `patchText` sem path **não** allow | D4; G4–G6; task 1.2; spec Empty write path |
| Plugin `.opencode/plugin/` auto-load; sem `opencode.json`; throw no deny | D5–D6; tasks 2.1 / 2.3; spec Plugin throws |
| Paging `experimental.chat.system.transform`; sem hop gitignored | D7; task 2.2; spec `process-fsm-paging` ADDED |
| Stubs ≤8 linhas; sem `/opsx-*`; Impeccable/`design-critic` já em `.agents/skills/` | D8; tasks 3.1 / 2.3; spec OpenCode adapter skin |
| Detector nos três; mesmo `hook.mjs`; fail-open | D9; tasks 4.1–4.3; spec Impeccable detector + `developer-tooling` |
| Specs dois → três; lock machine morto; decision-log revoga só unicidade #562 | D10; tasks 3.3 / 5.1; spec `cursor-harness` lock machine ADDED |
| `AGENTS.md` três clientes; sem Auto OpenCode/Grok; ≤40 | D12; G15; task 3.2 / 6.3 |
| Ensaio deny 1.18.18 bloqueia Auto, não o merge do adapter | D12; task 6.5 |
| bash `tee`/`>` develop deny | G7; spec bash tee; task 1.1 / 6.1 |
| `item-edit` Status → deny (`process_event`) | G8; spec process-harness + plugin throw; task 6.1 |
| OpenSpec Design + `card-<id>-*` allow | G9; spec OpenSpec write; task 6.1 |
| `openspec/config.yaml` “OpenCode is not an active harness” = Apply | D10; task 5.2; proposal Impact |

Não-entra (lock machine, segundo Guard/detector, T0–T17 em `.opencode/`, `opencode.json`, `/opsx-*`, produto, upgrade, artigo #614, reabrir yaml/`decide()` dual emit do #668) está em Non-Goals, Apply contract e tasks 1.4 / 2.3 / 4.3 / 5.1. Sem drift de vocabulário.

`## Open Questions` = nenhuma bloqueante. Residual #5894 (subagent `task`) e “plugin carregou” ficam no ensaio humano — alinhado ao issue.

### Dois módulos: throw vs fail-open

D5 nomeia dois arquivos:

- `.opencode/plugin/process-fsm-guard.js` — `tool.execute.before` → **throw** no deny
- `.opencode/plugin/impeccable-hook.js` — `after` + `session.idle` → **nunca throw**

Tasks batem: 2.1 throw; 4.2 catch-all nunca throw. Não há task que junte detector e Guard no mesmo módulo. Task 2.2 (“paging no mesmo plugin **ou** módulo irmão”) refere-se ao inject Moore no plugin Guard, não ao detector. Spec Guard: “Detector hooks MUST NOT share this throw path.” Mix throw/fail-open num único plugin **não** está no contrato de Apply.

### `normalize()` nativo vs plugin serializando

D2/D6: envelope nativo entra em `normalize()`; plugin serializa `{ tool, args }` e lê JSON `permission`/`decision` antes do throw. G1–G12 são goldens do núcleo (`decide()`), não do throw. Plugin throw está em D11 + task 6.2 (“plugin throw no deny (não JSON permission)”), sem número G. Split correto: ouro nativo prova o dialeto; 6.2 prova a pele. O furo é outro: G3 não prova parse de `patchText` (P1).

### Live `*** Move to:` vs issue `Move File:`

Parse **está** especificado: spec Guard “issue shorthand ‘Move File’ maps to live `*** Move to:`”; task 1.1 lista só marcadores live; D3/Risks: goldens usam o live; parse extra de `Move File` é barato e não reabre decisão. Não há golden com `*** Move to:` / `*** Add File:` / `*** Delete File:` (G3 é só `*** Update File:`). Ver P1/P2.

### Grok `PostToolUse`/`Stop` vs “não reabrir #668”

Task 4.1 + Apply contract: registrar detector em `.grok/hooks/`; **não** relitigar Guard/paging. Live `.grok/hooks/process-fsm.json` hoje só tem `PreToolUse` (Guard) + `SessionStart` (paging). Apply **vai editar o mesmo JSON do Guard** para acrescentar eventos. Isso é pele de detector, não relitigação, se matchers/timeout/`process-fsm-guard.sh` / `SessionStart` ficarem intactos. Task 4.1 não manda mudar `process-fsm-guard.sh` nem o gerador de página. Grok wrapper continua `exec` do sh Cursor. Não reabre o núcleo #668 (yaml / dual emit). Residual: same-file edit (P3).

### `openspec/config.yaml` deferred — Design glob leak?

`design_globs` = `openspec/changes/**` + `frontend/public/prototypes/**`. `openspec/config.yaml` **não** está no glob de Design (kind `other` → Guard allow, comportamento já existente). A change **não** inclui patch desse arquivo; D10/task 5.2/proposal adiam para Apply. Sem leak do glob de Design para o yaml de config neste turno.

### Paging inject vs playbook / orçamento ≤20

`page()` já é o compilador: wrapper + `context_file[q]` + footer. `test_paging.py` afirma ≤20 linhas e ausência de `release-guard` / `subir lote` / `deploy PROD` (Todo e Homologado). Stubs yaml são 1–2 linhas; Homologado cita `fechar_release`/`M_lote`, não o playbook. Task 2.2 injeta `page().additional_context`; G13/spec: Todo, ≤20, sem `release-guard`. **Não** injeta overlay/`release-guard pre` se Apply não empilhar texto extra. Residual: 6.2 testa o body de `page()`, não o `system[]` já mesclado pelo binário (P3).

### Aceite (bash tee, item-edit, empty patchText, Design+card-*)

Presentes: G7/G8/G4–G5/G9 + spec scenarios + tasks 1.1–1.2 / 6.1. G8 está **subespecificado** frente a `is_status_edit_command` (P2). G9 é `edit`, não `apply_patch` (P1).

### `files_g_design`

`proposal.md` + `design.md` + `tasks.md` + `specs/**/*.md` (cinco deltas) existem. `files_g_design(change_dir)` passará. T5 não exige `## Design Critique` nesse predicado.

### Design Critique pré-preenchido PASS?

**Não.** Grep na change: zero matches de `Design Critique`. `design.md` tem Prototype N/A + Impeccable pipeline N/A, sem heading de crítica e sem `Design Agent verdict: PASS`. Correto: o filho autor MUST NOT escrever essa seção; o pai preenche só depois de A/B. Não há PASS inventado.

### P0 live no `guard.py` (o card existe para fechar)

Confirmado neste worktree, envelope nativo OpenCode:

- `WRITE_TOOLS` tem `write`/`Edit`, **não** `edit` nem `apply_patch`
- `SHELL_TOOLS` **não** tem `bash`
- `PATH_KEYS` **não** tem `filePath`
- `normalize()` só lê `tool_name`/`toolName` + `tool_input`/`toolInput` — `{ tool, args }` → `tool_name=""`, `tool_input={}`
- `extract_path` nativo = `None`; `decide()` early-return **allow** (`if not path: return _allow()`)

O pacote **especifica** o fecho (D2–D4, tasks 1.1–1.3, spec ADDED). O P0 de produto não é achado de Design; o P1 é que os goldens de `apply_patch` não testemunham o parse.

---

## Audit

- A11y / responsive / browser / detector visual: N/A (`UI impact: none`). Prototype N/A confirmed. Playwright não correu.
- Dual critic / T7: não enfraquecidos; browser N/A aqui. Snapshot desta coluna = este arquivo, não tela.
- FSM yaml: sem task de estado/evento/`enabled_tools`. T1 Alan; T7 Alan; T5 parent `submeter_design`. I1–I9 / T0–T17 não reabertos.
- Package: `proposal.md`, `design.md`, `tasks.md`, cinco spec deltas. `files_g_design` OK. `openspec validate` é task 6.4 (Apply), não deste turno.
- Product UI: zero `frontend/src/` / produto `backend/` no Apply contract.
- Dois plugins vs um: tasks 2.1 ≠ 4.2.
- Grok Guard files: task 4.1 toca `.grok/hooks/` (JSON aninhado); proíbe relitigar PreToolUse/SessionStart.

---

## Trace

1. Issue #720 — terceiro adapter 1.18.18; detector nos três; aceite nativo + throw + inject + empty path deny + tee + item-edit + Design allow; fronteira vazia.
2. proposal What Changes / Capabilities — MODIFY cinco specs; New Capabilities nenhuma (pele, não segundo processo); config.yaml = Apply.
3. design D1–D12 + G1–G16 + Apply contract; Open Questions vazias; UI none; Prototype N/A; Impeccable pipeline N/A; **sem** `## Design Critique`.
4. tasks 1.x núcleo dialeto; 2.x plugin Guard + paging; 3.x stubs/AGENTS/decision-log; 4.x detector dois módulos; 5.x specs + config Apply; 6.x G1–G16 + throw + homologação.
5. spec Guard ADDED: dialeto, empty path deny, plugin throw. Paging ADDED: transform inject. Harness: dois→três; detector nos três; Auto gated.
6. Live Guard ainda fail-open no dialeto nativo (esperado pré-apply).
7. `.grok/hooks/process-fsm.json` ainda sem `PostToolUse`/`Stop` (esperado pré-apply).
8. `page()` live já ≤20 e sem playbook — inject reusa isso.

---

## Findings (para emissão curta)

### P0

(nenhum)

### P1

- **Goldens de `apply_patch` são todos deny — colapsam com o novo empty-path deny e não provam parse de `patchText`.** G3 (Update File de produto na `develop` → deny), G4 (`patchText=""` → deny) e G5 (Begin/End sem path → deny) devolvem o mesmo token. Implementação que mete `apply_patch` no conjunto “sem path extraível = deny” e **nunca** parseia `*** Update File:` / `*** Move to:` passa G3–G5: path vazio → deny. G9 (o único allow OpenSpec) é `edit` + `filePath`, não `apply_patch`. Aceite: envelope OpenCode em OpenSpec/protótipo Design+`card-*` **allow** — cobre `apply_patch` de `design.md`, não só `edit`. Sem discriminator, Apply pode (a) fechar o P0 live (write ilegal deixa de allow) à custa de **deny de todo `apply_patch` legal**, ou (b) deixar o parse do marcador live `*** Move to:` por implementar. Spec/task 1.1 já listam os quatro marcadores; a tabela G não tem allow-case nem `assert extract_path(...)`. Disposition: acrescentar golden allow `apply_patch` de `openspec/changes/…` com `status=Design` + `q_git=card-<id>-*`; e/ou G3 afirmar path extraído `backend/app/main.py` (reason I6/`develop-write`, não empty-path); mais um caso `*** Move to:` (marcador que o issue chamou `Move File`).

### P2

- **G8 como escrito não dispara `is_status_edit_command`.** O classificador exige `item-edit` **e** `PVTSSF_lAHOAAHtBM4BV8b2zhRUdMM` (ou option id). A linha G8 `"gh project item-edit … Status field"` falha o predicado → path vazio → allow, o oposto do aceite. Fixtures #668 usam `STATUS_FIELD_ID`. Disposition: G8 copiar o comando canônico com field/option id; não enfraquecer o classificador para qualquer `item-edit`.
- **G12 (fallback bash) não está no caminho live do plugin OpenCode.** Task 2.1 chama `guard.py`/`decide()`. Grok `exec` `.cursor/hooks/process-fsm-guard.sh` (fallback sem PyYAML + parse de envelope). G12 testa esse sh com JSON OpenCode, não o plugin JS. Se Python falhar na sessão 1.18.18, o plugin não herda o fallback (fail-open residual, classe “plugin não carregado”). Disposition: plugin invocar o mesmo `process-fsm-guard.sh` (irmão Grok) ou documentar fail-closed explícito se `spawn` falhar.
- **Detector OpenCode: G14 só afirma `hook_event_name=PostToolUse`.** `hook.mjs` / `resolveTargetFiles` lê `tool_input.file_path` / `path` / `event.file_path`; harness default não lê `args.filePath`. Cursor `impeccable.sh` já mapeia `filePath`→`file_path` e `stop`→`Stop`. Task 4.2 não nomeia o mapa `session.idle`→`Stop` nem a tradução de path. Disposition: 4.2/G14 exigir o mesmo stdin contract que `impeccable.sh` (path keys + idle=Stop).

### P3

- Task 2.2 “mesmo plugin ou módulo irmão” para paging vs D5 (só dois arquivos nomeados). Apply lê D5+Apply contract: paging no Guard plugin.
- Task 4.1 edita o JSON que também é Guard/paging; contrato diz “não relitigar” — risco de rewrite de matcher/timeout.
- Requirement heading `Process law has one nucleus and two adapters` mantido (identidade OpenSpec MODIFIED); corpo já diz three. Correto; não renomear.
- Spec Guard main “live Cursor envelope” não é MODIFIED; o ADDED OpenCode convive. Archive fica Cursor-cêntrico no requisito velho.
- `write` minúsculo é tool Grok **e** OpenCode; empty-path deny pode aplicar ao Grok `write` vazio (fail-closed, não reabre write real).
- Parse extra `*** Move File:` (wording do issue) fica residual barato (Risks); não é SHALL.
- 6.2/G13 testam `page()` isolado, não `system[]` concatenado pelo 1.18.18. Residual D Risks (inject vs merge bloco 0).
- `## Design Critique` ausente (não pré-PASS). Pai preenche depois desta onda.
- Task 6.4 `openspec validate` sem `--strict`.
- #5894 `tool.execute.before` em subagent `task` não live-testado — residual explícito, ensaio 6.5, não upgrade.
- Stubs OpenCode sem gerador CI (Grok tem `grok_stubs.py`); Apply contract “se extraído”. Drift possível.

### Disposition

Um P1: a suíte G3–G5 não testemunha parse de `apply_patch`/`*** Move to:` porque empty-path deny devolve o mesmo deny. Issue/design/tasks/specs cobrem aceite (tee, item-edit, empty patchText, Design allow, dois módulos, detector Grok sem relitigar Guard, config.yaml no Apply, paging ≤20 sem playbook). `files_g_design` passará. Design Critique **não** foi pré-preenchido PASS (seção inexistente). P0 live no `guard.py` é real e o pacote o fecha na spec — o ouro de `apply_patch` é que não prova o fecho. P2 = G8 sem field id, fallback sh fora do plugin, mapa detector. Detector/browser N/A. Prototype N/A confirmed.

### Verdict

**BLOCKED**
