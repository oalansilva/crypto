## 1. evaluate() honra guardas e I4

- [x] 1.1 Estender `EvalContext`; `q_git_card` deriva de `q_git` via `CARD_GIT_RE`; `guard:` False/None ⇒ reject fail-closed
- [x] 1.2 `evaluate(iniciar_apply|pedir_review)` com `digest_changed` True/None ⇒ reject `I4` (não T8/T9)
- [x] 1.3 Ajustar `test_fsm.py`: predicados True nas transições legais; T8 e T9 legais com `digest_changed=false`
- [x] 1.4 Fixtures: T8 `q_git=develop` reject; T8 `digest_changed=true` reject I4; T16 `M_lote=false` reject; T17 Agent reject actor / Guard transition

## 2. process_event

- [x] 2.1 Implementar `process_event.py`: CLI `<evento> [--card] [--change] [--dry-run]`; função **sem** `actor=`; mover injetável; stdout JSON; `--dry-run` não grava sidecar
- [x] 2.2 Reject: `aprovar_design` / `priorizar` / `homologar` / `fechar_release`; `request_implement` lista `enabled_events(q)`; unbound/`--card` mismatch; toda rejeição de `fechar_release` cita `alan-workflow-ambientes` e `release-guard`; sem deploy
- [x] 2.3 T8: mover para Em desenvolvimento; **não** emitir token de Write; fixture Guard Write ainda Pronto para Dev ⇒ deny I3
- [x] 2.4 I4/T17: `iniciar_apply` e `pedir_review` + digest mudado ⇒ um mover Design (`reason=I4`), nunca Em desenvolvimento/Code Review; `invalidar_aprovacao` sem digest change ⇒ reject (actor Agent)
- [x] 2.5 T5 grava sidecar `.design-digest` só no processo do script; `--dry-run` não grava
- [x] 2.6 T10–T13: evento nomeado liga a guarda do `exclusive_group`; T14 `integrar_develop` live reject (`checks_green` unset)
- [x] 2.7 `test_process_event.py` sem GitHub (FakeMover); testes **não** injetam ator na função

## 3. Guard Status item-edit e sidecar

- [x] 3.1 Em `guard.py`, **antes** do glob-first #611 e **antes** de `if not path: allow`: deny path que termina em `.design-digest` (`preToolUse` Write/StrReplace/Delete e shell mutante, qualquer `q`); deny Status item-edit/GraphQL **mesmo** se o command também tiver `process_event.py`; allow só comando **unicamente** a CLI; **não** ler `PROCESS_FSM_MOVE`
- [x] 3.2 Fallback bash do adapter: a mesma ordem (sidecar + Status deny antes do allow sem path e antes de design_globs)
- [x] 3.3 Fixtures envelope: deny item-edit Status sem path; deny command encadeado; deny `Write`/`StrReplace`/`Delete` de `openspec/changes/.../.design-digest` com `status=Design`; allow CLI pura; allow `gh issue view`; `PROCESS_FSM_MOVE=1` + item-edit ⇒ deny

## 4. Verificação e fora de escopo

- [x] 4.1 `pytest scripts/process-fsm -q` verde (job CI existente)
- [x] 4.2 Diff NÃO altera `backend/` nem `frontend/src/`
- [x] 4.3 Diff NÃO substitui `.cursor/hooks/impeccable.sh`
- [x] 4.4 Sem paging `sessionStart`, sem gate de `git commit`/`./restart`, sem autômato de release, sem `PROCESS_FSM_MOVE`
