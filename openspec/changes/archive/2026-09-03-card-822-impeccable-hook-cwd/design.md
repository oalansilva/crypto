## Context

Card [#822](https://github.com/oalansilva/crypto/issues/822). Status observado: **Design**. Bound `q_git=card-822-impeccable-hook-cwd`. Relacionado e **não** reaberto: #668, #720, #782, #784, #821.

HEAD `9f2bfe97` (comando commitado):

- Grok `.grok/hooks/process-fsm.json`: `PostToolUse` = `./impeccable.sh PostToolUse`; `Stop` = `./impeccable.sh Stop`; `PreToolUse` / `SessionStart` = `./process-fsm-*.sh`.
- Cursor `.cursor/hooks.json`: `afterFileEdit` / `stop` = `.cursor/hooks/impeccable.sh …` (parte se cwd for `.cursor/` ou `.cursor/hooks/`). Guard Cursor continua `.cursor/hooks/process-fsm-guard.sh` (**fora**).
- dsh `.dsh/plugin/impeccable-hook.js`: `const cwd = process.cwd() || REPO_ROOT` — cwd preenchido em `$HOME` nunca cai no `REPO_ROOT`. Guard dsh **fora** (#784).
- OpenCode `.opencode/plugin/impeccable-hook.js`: `input.directory || input.worktree || REPO_ROOT`. Sem 127 desta classe no Grok; Q2 da grelha **entra** o quarto cliente por paridade.

Evidência viva, sessão Grok `01a0685c-4f35-7933-bca7-685cbab0b901`: `post_tool_use` 128×127 `sh: 1: ./impeccable.sh: not found`; `stop` 2× o mesmo; `session_start` 1 sucesso; `pre_tool_use` 25 sucessos + 1 deny real (`status_item_edit`). Reprodução HEAD: cwd raiz → 127; cwd `.grok/hooks/` → 0; cwd `frontend/` → 127. O ficheiro existe em `.grok/hooks/impeccable.sh`. Fail-open: a tool corre; a UI marca `[hooks: 1 failed]`; o detector não corre.

Grelha fechada no comentário https://github.com/oalansilva/crypto/issues/822#issuecomment-5530106068 (body do issue ainda tem as Qs abertas; este Design **não** as reabre):

1. Grok: detector **e** bloqueio de escrita **e** arranque de sessão.
2. OpenCode **entra** (paridade dos quatro).
3. Rascunho local na canónica `develop` (7 ficheiros `M`, não commitado) é o ponto de partida do Apply após Pronto para Dev. Design não o commit. Esta worktree está limpa em `origin/develop`.

Rascunho (leitura only; **não** editado daqui): locator `test -f` repo-relative + sibling `./` + `git rev-parse --show-toplevel` em Grok (quatro eventos) e Cursor (`afterFileEdit`/`stop`); `resolveRepoCwd` no dsh; testes `sh -c` nos três cwd. **Falta OpenCode** nesse rascunho.

UI impact: none

live_route: N/A harness-only; no product route. Clone gate isento (sem HTML, sem catálogo). Sem superfície visual de produto.

## Goals / Non-Goals

**Goals:**

- Grok PostToolUse / Stop / PreToolUse / SessionStart encontram o script na raiz, em `.grok/hooks/` e em `frontend/` (exit 0, não 127).
- Cursor `afterFileEdit` / `stop` encontram o adapter na raiz, em `.cursor/` e em `.cursor/hooks/`.
- dsh Impeccable: `resolveRepoCwd` em vez de `process.cwd() || REPO_ROOT`; cwd `$HOME` → git do consumidor ou `REPO_ROOT`.
- OpenCode: endurecer `input.directory || input.worktree || REPO_ROOT` para cwd `$HOME` não falhar `hook.mjs`.
- Fail-open do detector intacto. Sem segundo detector. Sem dual-write T0–T17.
- Apply parte dos 7 ficheiros do rascunho + OpenCode + testes.

**Non-Goals:**

- Produto `backend/` / `frontend/src/`. UI / HTML / `DESIGN.md` / Playwright desta coluna.
- Trocar `hook.mjs`. Dual-write da lei para `.grok/` / `.dsh/` / `.opencode/`.
- Auto qualquer cliente. T16 / release / deploy PROD.
- Reabrir #668 / #720 / #782 / #784 / #821 como trabalho.
- Guard Cursor (`preToolUse` / `beforeShellExecution` / `sessionStart`). Guard dsh (#784) excepto o cwd do plugin Impeccable.
- `guard.py` `decide()`, envelopes, fail-closed de produto.
- Commit do rascunho na canónica `develop` durante Design. Pin `covenant-flow` (grelha não pediu tag).

## Decisions

1. **Locator Grok = cadeia `test -f` repo-relative + sibling + git toplevel, nos quatro eventos.**  
   Comando (PostToolUse; os outros substituem o script/args):  
   `test -f .grok/hooks/impeccable.sh && exec .grok/hooks/impeccable.sh PostToolUse; test -f ./impeccable.sh && exec ./impeccable.sh PostToolUse; root=\`git rev-parse --show-toplevel 2>/dev/null\`; test -f "$root/.grok/hooks/impeccable.sh" && exec "$root/.grok/hooks/impeccable.sh" PostToolUse; exit 127`  
   Ordem: raiz (`.grok/hooks/…`) → pasta do JSON (`./…`) → outra pasta git (`frontend/`, via toplevel). `exec` preserva stdin. Último `exit 127` só se o ficheiro não existir em lado nenhum (melhor visível do que skip calado). O wrapper `.sh` continua a resolver `ROOT` por `dirname` e a chamar `hook.mjs`; fail-open interno (`exit 0` no detector) não muda. A mesma cadeia em PreToolUse (`process-fsm-guard.sh`) e SessionStart (`process-fsm-session-start.sh`) — Q1. Alternativa rejeitada: só PostToolUse/Stop (Guard fica mudo **se** o cwd alinhar com o do PostToolUse). Alternativa rejeitada: path absoluto hardcoded no JSON.

2. **Cursor = a mesma classe, só `afterFileEdit` / `stop`.**  
   Repo-relative `.cursor/hooks/impeccable.sh` → sibling `./hooks/impeccable.sh` → `./impeccable.sh` → git toplevel. Cobre cwd raiz / `.cursor/` / `.cursor/hooks/`. Guard Cursor e `sessionStart` ficam `.cursor/hooks/process-fsm-guard.sh` / `process-fsm-session-start.sh` (recorte do issue: Guard Cursor fora). Alternativa rejeitada: alargar o locator ao Guard Cursor (não foi Q1).

3. **dsh Impeccable = `resolveRepoCwd(process.cwd())`, não `process.cwd() || REPO_ROOT`.**  
   Helper em `dsh_plugin_lib.js`: `git -C <start> rev-parse --show-toplevel`; status 0 e toplevel não-vazio → esse path; senão `REPO_ROOT` (ficheiro da lib, já cwd-independente). `$HOME` sem git de consumidor → `REPO_ROOT`. Plugin deixa de importar `REPO_ROOT` só para este fallback. `runHookMjs` continua `join(REPO_ROOT, ".agents/…/hook.mjs")`. Guard dsh **não** muda. Alternativa rejeitada: `process.cwd() || REPO_ROOT` (cwd `$HOME` é truthy). Alternativa rejeitada: mexer no Guard dsh (#784).

4. **OpenCode entra: endurecer o cwd do detector, sem cruzar libs.**  
   `runHookMjs` já abre `hook.mjs` via `REPO_ROOT` do ficheiro da lib; o furo é `input.directory` truthy = `$HOME` a virar cwd do spawn (hook a resolver projecto relativo a `$HOME`). Apply MUST: resolver `input.directory || input.worktree` com a **mesma regra** que `resolveRepoCwd` (git toplevel ou `REPO_ROOT`) **dentro** de `opencode_plugin_lib.js` (espelho; MUST NOT `import` de `dsh_plugin_lib.js`). Plugin Impeccable usa esse cwd. Plugin Guard OpenCode **não** é recorte (Q2 foi detector / miss `hook.mjs`). Teste: `directory=$HOME` → cwd passado a `runHookMjs` é `REPO_ROOT` / toplevel, não `$HOME`. Alternativa rejeitada: “já tem `|| REPO_ROOT`” (não cobre directory preenchido). Alternativa rejeitada: só documentar, sem golden.

5. **Apply parte do rascunho canónico; Design não o grava; OpenCode falta no rascunho.**  
   7 ficheiros `M` em `/srv/apps/dev/criptofarol/source` (develop suja, HEAD `9f2bfe97`): `.grok/hooks/process-fsm.json`, `.cursor/hooks.json`, `.dsh/plugin/impeccable-hook.js`, `scripts/process-fsm/dsh_plugin_lib.js`, `test_guard.py`, `test_paging.py`, `test_dsh_adapter.py`. Depois de Pronto para Dev, Apply copia esses deltas **para esta worktree** (hoje limpa) e acrescenta OpenCode + `test_opencode_adapter.py`. Design MUST NOT editar a canónica nem commit/push. Alternativa rejeitada: deitar o rascunho fora (Q3). Alternativa rejeitada: gravar na `develop` agora (T0).

6. **Goldens = `sh -c` do comando JSON, sem GitHub, sem segundo detector.**  
   Pytest em `scripts/process-fsm`. Grok/Cursor: stdin `{}` , timeout 30, assert returncode 0 nos cwd do aceite. dsh: `resolveRepoCwd(homedir()) == REPO_ROOT`. OpenCode: plugin/lib com `directory=homedir`. Assertions de JSON deixam de exigir igualdade exacta `./impeccable.sh PostToolUse`; passam a exigir `test -f` + path repo-relative + sibling + toplevel. `test_hooks_json_composes_impeccable` / `test_hooks_json_session_start` / `test_grok_hooks_json_registers_guard` MUST actualizar-se em conjunto (rascunho já o faz para Grok/Cursor).

### Golden cases (pytest `scripts/process-fsm`, sem GitHub)

| # | Caso | Esperado |
| --- | --- | --- |
| C1 | Grok `PostToolUse` `sh -c` cwd = raiz, `.grok/hooks/`, `frontend/` | exit 0 nas três |
| C2 | Grok `Stop` nas mesmas três cwd | exit 0 |
| C3 | Grok `PreToolUse` (Guard) nas mesmas três cwd | exit 0 (não 127) |
| C4 | Grok `SessionStart` nas mesmas três cwd | exit 0 |
| C5 | Cursor `afterFileEdit` cwd = raiz, `.cursor/`, `.cursor/hooks/` | exit 0 |
| C6 | Cursor `stop` nas mesmas três cwd | exit 0 |
| C7 | Cursor `preToolUse` / `beforeShellExecution` / `sessionStart` | comandos HEAD inalterados |
| C8 | dsh `resolveRepoCwd(homedir())` com `process.cwd()` = `$HOME` | igual a `REPO_ROOT`; plugin sem `process.cwd() \|\| REPO_ROOT` |
| C9 | OpenCode plugin `input.directory` = `$HOME` | cwd de `runHookMjs` = toplevel / `REPO_ROOT`; `hook.mjs` encontrado |
| C10 | JSON Grok/Cursor contém `test -f` repo-relative + sibling + `git rev-parse --show-toplevel` | asserts de string (rascunho) |
| C11 | `hook.mjs` crash no adapter | turno não aborta (fail-open já nos wrappers) |
| C12 | fontes `.grok/hooks/process-fsm.json`, plugins dsh/OpenCode | sem tabela T0–T17 |

## Apply contract

- Ordem, só após `Status=Pronto para Dev` no **mesmo** chat `#822`, filho Apply (pai `iniciar_apply` antes do spawn). Zero produto UI. Design **não** aplica.
- Ponto de partida: copiar o rascunho não commitado da canónica `develop` (7 ficheiros listados em D5) para **esta** worktree. Não editar `/srv/apps/dev/criptofarol/source` a partir do Apply além de ler o diff; a canónica fica suja até o operador a limpar.
- Grok: as quatro chaves de `.grok/hooks/process-fsm.json` ganham a cadeia D1. Cursor: só `afterFileEdit` / `stop` (D2). dsh: `resolveRepoCwd` + plugin (D3). OpenCode: espelho em `opencode_plugin_lib.js` + plugin Impeccable (D4) — **ausente do rascunho**.
- Testes: C1–C12. Actualizar `test_guard.py` / `test_paging.py` (rascunho) e acrescentar OpenCode em `test_opencode_adapter.py`. Sem GitHub nos unitários.
- **Não** alterar `hook.mjs`, `guard.py` `decide()`, `.dsh/plugin/process-fsm-guard.js`, Guard Cursor, `process-fsm.yaml`, `AGENTS.md`. **Não** dual-write T0–T17. **Não** pin `covenant-flow` neste card (residual: próximo `--pin` pode sobrepor peles se o produto não tiver o locator).
- Fail-open: wrappers Impeccable continuam `exit 0` / `next()` / sem throw. Locator `exit 127` só se o script da pele não existir.

## Risks / Trade-offs

- [Grok recarrega JSON só em sessão nova] → 128×127 na sessão viva mesmo com rascunho local. Mitigação: aceite = comando `sh -c` + sessão nova após merge; não “hot reload”.
- [Locator `exit 127` se git falhar e cwd sem o ficheiro] → residual aceite (ficheiro em falta). Os três cwd do aceite têm git de consumidor.
- [Cursor Guard ainda depende de cwd = raiz] → recorte explícito. Residual: se o Cursor passar a correr Guard com cwd `.cursor/`, mute paralelo; **não** neste card.
- [OpenCode Guard ainda usa `input.directory` cru] → Q2 foi miss de `hook.mjs`, não write-block. Residual aceite; C9 não cobre `process-fsm-guard.js` OpenCode.
- [Espelho `resolveRepoCwd` em duas libs] → MUST NOT import dsh←→OpenCode. Drift possível; C8+C9 pinam o contrato. Extract partilhado só se ambos os testes passarem sem cruzar peles.
- [Rascunho na canónica `develop`] → Apply que ignore OpenCode falha C9. Design não commit. Operador MUST não misturar o rascunho com outro card na canónica.
- [Próximo `implantar --pin`] → peles no consumidor podem voltar ao `./impeccable.sh` se o produto `covenant-flow` (pin `v1.1.6`) não tiver o locator. Residual aceite (grelha não pediu tag). Apply MAY notar no PR; MUST NOT inventar `v1.1.7` sem pedido.
- [Fail-open vs badge Grok] → 127 do locator **é** o badge. Depois do conserto o badge desta classe some; crash de `hook.mjs` continua sem abortar o turno.

## Migration Plan

Aditivo sobre HEAD `9f2bfe97`. Ordem Apply: (1) copiar rascunho 7 ficheiros para a worktree do card; (2) OpenCode D4 + C9; (3) C1–C8, C10–C12 verdes; (4) PR da branch `card-822-impeccable-hook-cwd`. Rollback = reverter os JSON/plugins para `./` e `process.cwd() || REPO_ROOT`. Sem migration de banco. Sem rebuild frontend. Homologação = sessão Grok nova sem `[hooks: 1 failed]` nesta classe; não bloqueia T14 se os goldens passarem.

## Open Questions

Nenhuma bloqueante. Q1–Q3 da grelha = fechadas no comentário do Alan (detector+Guard+SessionStart Grok; OpenCode neste card; rascunho = Apply start). Body do issue ainda mostra as Qs — ignorar como abertas.

## UI impact

**none** — harness/hooks de processo. Nenhuma rota, shell, componente ou copy de produto. Nenhuma superfície visual nova ou alterada. O aceite visível é ausência do badge `[hooks: 1 failed]` desta classe e exit 0 dos locators, não uma tela Cripto.

## Prototype

N/A — `UI impact: none`. Não há tela a prototipar; o aceite é locator cwd-independente nas peles Grok/Cursor/dsh/OpenCode. Sem HTML. Sem rewrite de `DESIGN.md`. Sem pipeline Impeccable visual. Playwright desta coluna = N/A (não há UI de produto a exercitar). Snapshot Impeccable = N/A justificado (sem superfície visual).

## Prototype Validation

N/A — sem superfície visual. Não há URL, viewport nem assert de UI.

## Impeccable pipeline (esta coluna Design)

N/A — `UI impact: none`. Sem shape/protótipo/crítica/audit/polish/browser de tela de produto. O detector Impeccable das peles **é** o objecto do card (cwd da pele, não `hook.mjs`).

## Design Critique

- **P0:** nenhum
- **P1:** nenhum — grelha Q1–Q3: Grok detector+Guard+SessionStart; OpenCode entra; Cursor só afterFileEdit/stop; dsh `resolveRepoCwd`; fail-open; sem dual-write T0–T17; sem UI de produto; Apply copia o rascunho de 7 ficheiros e acrescenta OpenCode
- **P2 (aceites):** goldens do rascunho só cobrem parte dos `sh -c`; `$HOME` que seja git alheio ≠ consumidor
- **P3 (aceites):** Guard OpenCode ainda usa directory cru; Guard/sessionStart Cursor ainda cwd=raiz; próximo pin pode reverter `./`; espelho das libs; `develop` canónica suja até o operador

Prototype: N/A — harness-only, sem HTML.
Snapshot visual Impeccable: N/A justificado (`UI impact: none`).
Snapshot da crítica (T7, não é UI): `.impeccable/critique/822-card-822-impeccable-hook-cwd-A.md`

Design Agent verdict: PASS
