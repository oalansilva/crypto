## Why

Na sessão Grok Build `01a0685c-4f35-7933-bca7-685cbab0b901`, cada tool mostrou `[hooks: 1 failed]`: o PostToolUse Impeccable corre `./impeccable.sh` com cwd na raiz do repo e sai `exit 127: sh: 1: ./impeccable.sh: not found`. O ficheiro vive em `.grok/hooks/impeccable.sh`. Fail-open: a tool corre; o detector fica mudo e a UI marca o fail. Cursor e dsh têm a mesma classe de dependência da pasta de trabalho; OpenCode entra por paridade dos quatro (grelha fechada).

## What Changes

- Grok: o locator do comando JSON deixa de assumir a pasta do JSON. PostToolUse / Stop (detector), PreToolUse (bloqueio de escrita / Guard) e SessionStart (arranque) encontram o script na raiz do repo, em `.grok/hooks/` e noutra pasta dentro do git (`frontend/`). Nenhum fica mudo se a pasta mudar.
- Cursor: `afterFileEdit` / `stop` encontram `.cursor/hooks/impeccable.sh` na raiz, em `.cursor/` e em `.cursor/hooks/`. Guard Cursor (`preToolUse` / `beforeShellExecution`) **não** muda.
- dsh: o plugin Impeccable deixa de usar `process.cwd() || REPO_ROOT` (cwd preenchido em `$HOME` nunca cai no `REPO_ROOT`). Passa a `resolveRepoCwd` (git toplevel do consumidor, senão `REPO_ROOT`). Guard dsh **não** muda (#784).
- OpenCode: verificar/endurecer `input.directory || input.worktree || REPO_ROOT` para cwd de sessão = `$HOME` não falhar `hook.mjs`. Quarto cliente **entra** neste card.
- Fail-open do detector mantém-se: crash/127 de `hook.mjs` não aborta o turno. 127 do **locator** (script da pele em falta) é o que a UI Grok marca hoje; depois do conserto, cwd raiz / `.grok/hooks/` / `frontend/` saem 0.
- Apply, depois de Pronto para Dev, parte do rascunho local não commitado na worktree canónica `develop` (7 ficheiros `M` em HEAD `9f2bfe97`). Design **não** o commit. Worktree deste card está limpa em `origin/develop`.
- Sem dual-write da lei T0–T17 para `.grok/` / `.dsh/` / `.opencode/`. Sem segundo detector. Sem trocar `hook.mjs`. Sem produto `backend/` / `frontend/src/`. Sem Auto. Sem reabrir #668 / #720 / #782 / #784 / #821. Sem T16.

Grelha (comentário https://github.com/oalansilva/crypto/issues/822#issuecomment-5530106068) **fechada**; o body do issue ainda tem as Qs abertas — Design sintetiza daqui:

1. Recorte Grok: detector **e** Guard **e** arranque de sessão.
2. Quarto cliente OpenCode **entra** (paridade dos quatro).
3. Rascunho local = ponto de partida do Apply após Pronto para Dev.

## Capabilities

### New Capabilities

- (nenhuma) — o detector continua o mesmo `hook.mjs`; este card só torna a pele cwd-independente nos quatro adapters já descritos em `process-harness`.

### Modified Capabilities

- `process-harness`: peles Grok/Cursor/dsh/OpenCode localizam o adapter Impeccable (e, no Grok, Guard + SessionStart) sem depender da pasta de trabalho da sessão; fail-open do detector intacto; dual-write T0–T17 continua proibido; sem segundo detector.
- `developer-tooling`: comandos/plugins versionados encontram `.grok/hooks/*.sh`, `.cursor/hooks/impeccable.sh`, `.dsh/plugin/impeccable-hook.js` e `.opencode/plugin/impeccable-hook.js` quando o cwd não é a pasta do JSON/plugin; `git ls-files` das peles inalterado.
- `cursor-harness`: `afterFileEdit` / `stop` em `.cursor/hooks.json` usam a mesma classe de locator (repo-relative + sibling + git toplevel); Guard Cursor e `sessionStart` fora do recorte; Impeccable continua composto, não substituído.
- `process-fsm-guard`: comando Grok `PreToolUse` (write-block) é cwd-independente — o mesmo `./process-fsm-guard.sh` na raiz deixa de sair 127 e ficar mudo. `decide()` / envelope / fail-closed de produto **não** mudam. Guard dsh / Cursor fora.

## Impact

- Altera (Apply, após Pronto para Dev): `.grok/hooks/process-fsm.json` (PostToolUse, Stop, PreToolUse, SessionStart), `.cursor/hooks.json` (`afterFileEdit`, `stop`), `.dsh/plugin/impeccable-hook.js` + `scripts/process-fsm/dsh_plugin_lib.js` (`resolveRepoCwd`), `.opencode/plugin/impeccable-hook.js` (+ lib se o endurecimento cair aí), testes em `scripts/process-fsm/test_guard.py`, `test_paging.py`, `test_dsh_adapter.py`, `test_opencode_adapter.py`.
- Ponto de partida Apply: rascunho **não** commitado na canónica `develop` (7 ficheiros). Falta OpenCode nesse rascunho — Apply MUST acrescentá-lo. Design não toca `/srv/apps/dev/criptofarol/source`.
- Não toca `backend/` / `frontend/src/`, `hook.mjs`, `guard.py` `decide()`, Guard Cursor, Guard dsh (#784), `process-fsm.yaml`, `AGENTS.md`, pin `covenant-flow`, T16/release.
- `UI impact: none`. Prototype N/A. Impeccable/`DESIGN.md`/Playwright desta coluna = N/A. Snapshot N/A.
- Origem: issue #822. Relacionado e **não** reaberto: #668, #720, #782, #784, #821.
