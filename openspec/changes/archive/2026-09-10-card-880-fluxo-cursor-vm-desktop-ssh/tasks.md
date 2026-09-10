Só após `Status=Pronto para Dev` no chat `#880`. Pai `iniciar_apply` (T8) antes do spawn. Filho Apply neste worktree. Zero produto. Sem `process_event` neste ficheiro.

## 1. Runbook Cursor

- [x] 1.1 Em `.cursor/skills/covenant-flow/SKILL.md`: os dois modos (terminal VM vs Desktop Windows + SSH a esta VM) ficam; cada etapa grelha/Design/Apply/review/QA/Done técnico passa nos dois; não abandonar um modo
- [x] 1.2 No mesmo skill: no Desktop+SSH Windows desta VM o pai MUST NOT chamar `move_agent_to_root`; bind da raiz visível = janela Remote-SSH nova no worktree `card-<id>-*` com título `#<id>` (não `#<id> Apply`); operador MUST NOT File > Open; `working_directory` sozinho não satisfaz Q2
- [x] 1.3 No mesmo skill: Shell do fluxo (git do runbook, `process_event`, pytest do harness) no worktree pede `required_permissions: ["all"]` no primeiro attempt do turno; MUST NOT `workspace_readwrite` + clique extra; falha Landlock/`uid_map` visível
- [x] 1.4 No mesmo skill: filho da etapa sucesso só com host `completed`; `Task was interrupted by the user` sem Stop visível = kill do host (falha deste card); pai MUST NOT executar a etapa no Desktop; operador MUST NOT retomar cadáver; Stop explícito = aborto + spawn novo
- [x] 1.5 No mesmo skill: prova viva pasta+comando+filho só no par Windows+esta VM; grelha/Design/review/QA por ensaio; Grok/OpenCode/dsh fora; destape #879 e hang S2 continuam #879

## 2. Prompts do pai (lista fechada)

- [x] 2.1 Prompts autocontidos grill / Design-autor / Apply / review / QA: filho MUST NOT `move_agent_to_root`; `working_directory` = worktree quando a árvore existir; Shell do fluxo com `["all"]` à primeira neste par Desktop+SSH
- [x] 2.2 MUST NOT dual-write lei em `.dsh/` nem `.grok/` nem `.opencode/` só por este card

## 3. Ensaio pytest

- [x] 3.1 Criar `scripts/process-fsm/test_cursor_host_modes.py` com C1–C8 do `design.md` (needles no runbook; classificação `completed` vs interrupt sem Stop; recusa pai-substituto e resume; sem GitHub)
- [x] 3.2 Helper de classificação de interrupt (módulo de teste ou função mínima no mesmo ficheiro de teste) — P3 aceite no Design, resolvido aqui
- [x] 3.3 `pytest scripts/process-fsm/test_cursor_host_modes.py -q` verde

## 4. Specs e validate

- [x] 4.1 Spec deltas já em `openspec/changes/card-880-fluxo-cursor-vm-desktop-ssh/specs/` (`cursor-host-modes`, `cursor-harness`, `llm-flow-emission`) — Apply não os reescreve fora do que o runbook/testes exigirem
- [x] 4.2 `openspec validate --change card-880-fluxo-cursor-vm-desktop-ssh` verde

## 5. Fora de escopo (confirmação)

- [x] 5.1 Diff sem `backend/`, `frontend/src/`, `.cursor/process-fsm.yaml`, `AGENTS.md` always-on a crescer, overlay `clients.*.auto`, pin novo, HTML de protótipo, `CONTEXT.md`, `docs/adr/`
- [x] 5.2 `UI impact: none` + `live_route: N/A` justificado + `surface: new`; sem pasta `frontend/public/prototypes/`
- [ ] 5.3 Prova viva (QA deste card, não card inteiro): pasta visível = worktree; comando do fluxo no mesmo turno sem clique; um filho de etapa `completed` no Windows + SSH a esta VM
