## Why

Quem opera o Covenant Flow no Cursor nesta VM sofre se mudar de sítio: no **modo terminal** o card anda do grelhar ao Done técnico; no **modo Desktop+SSH** (Windows + SSH a esta VM) a sessão não continua na pasta do card, comandos do fluxo pedem clique extra ou falham, e o filho da etapa morre a meio. Testemunha 2026-09-09 no #879: T8 passou; `move_agent_to_root` 2× `InstantiationService has been disposed`; Shell `workspace_readwrite` Landlock/`uid_map`; filho Apply `Task was interrupted`. Não é produto Cripto nem aresta FSM — é o mesmo cliente Cursor em dois modos de hospedagem.

## What Changes

- Os dois modos ficam: (1) Cursor Agent / CLI no terminal da VM; (2) Cursor Desktop Windows + SSH a esta VM. Não se abandona um deles.
- Cada etapa do mesmo chat do card (grelha → Design → Apply → review → QA → Done técnico) passa **nos dois modos**. Não vale grelhar num sítio e Apply no outro.
- Depois do Apply arrancar, a sessão continua na pasta do card sem o operador abrir à mão. *Como* (Design): no Desktop+SSH Windows desta VM o pai MUST NOT chamar MCP `move_agent_to_root`; liga a raiz visível por janela Remote-SSH nova no worktree (título `#<id>`, não `#<id> Apply`).
- No Desktop o comando do fluxo acaba no mesmo turno sem clique extra; falha de tool/MCP não passa em silêncio. *Como*: Shell do fluxo no worktree pede `required_permissions: ["all"]` no primeiro attempt do turno (não `workspace_readwrite` + clique).
- O filho da etapa tem de terminar nos dois modos; host derrubar a meio é falha deste card (destape #879 S2 continua #879). *Como*: sucesso = `completed`; `Task was interrupted` sem Stop visível do operador = kill do host.
- Aceite escrito por etapa; prova viva = pasta + comando + filho no par que partiu; resto por ensaio (teste / rubrica / harness), sem card inteiro vivo e sem só runbook.
- Aceite Desktop+SSH = só o par Windows + SSH a esta VM.

## Capabilities

### New Capabilities

- `cursor-host-modes`: contrato dos dois modos de hospedar o mesmo cliente Cursor nesta VM — cada etapa do chat passa nos dois; pasta do card sem abrir à mão; comando sem clique extra; filho termina; prova viva do que partiu + ensaio do resto; Q6 só Windows + esta VM.

### Modified Capabilities

- `cursor-harness`: o pai (não o filho) liga a raiz visível; no Desktop+SSH Windows desta VM MUST NOT `move_agent_to_root`; filho isolado não chama essa MCP; comando do fluxo no worktree acaba no mesmo turno com `required_permissions: ["all"]` no primeiro Shell (Landlock/`uid_map` não exige clique extra); interrupt do host no filho não conta como sucesso.
- `llm-flow-emission`: o filho da etapa (grelha, Design, Apply, review, QA) tem de terminar no modo em que foi spawnado; pai não executa a etapa no Desktop em substituição.

## Impact

- Apply (após Pronto para Dev), só harness Cursor: runbook `covenant-flow`, peles `.cursor/` que o locator precisar, pytest `scripts/process-fsm` (ensaio), spec deltas acima.
- MUST NOT: `backend/`, `frontend/src/`, `.cursor/process-fsm.yaml` (lei/aresta), `AGENTS.md` always-on a crescer, overlay `clients.*.auto`, pin novo só por isto, dual-write lei em `.dsh/`, HTML de protótipo, `CONTEXT.md`, `docs/adr/`.
- Grok / OpenCode / dsh fora salvo prova do mesmo bug de hospedagem (este Design não a tem: InstantiationService e Landlock/`uid_map` são do workbench/Shell Cursor).
- Não reabre #879, #864, #822, #729 como o mesmo trabalho. Homologado / Release / lote fora deste chat.
- UI impact: none
- live_route: N/A harness-only; Cursor Desktop Windows + SSH a esta VM vs Agent/CLI no terminal da mesma VM; no product route
- surface: new
- Origem: issue #880 (Q1–Q6 fechadas; este Design não as reabre).
