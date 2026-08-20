## Why

O Agent ainda move coluna com `gh project item-edit` solto; o chat vira autorização. O Guard Write (#611) já barra `Write` de produto, mas **não** barra T1/T7/T15/T16 nem o atalho `request_implement`. Sem a ferramenta SMAG `process_event`, δ continua prosa e o Auto fura o board.

## What Changes

- Introduzir CLI `scripts/process-fsm/process_event.py <evento>`: resolve `(q, bound_card, q_git)`, avalia δ (ator, guarda nomeada, `bound_card`) e **só então** move o Status no Project 1. Unitários injetam o mover; sem GitHub no pytest.
- Agent **não** faz `item-edit` de Status. O Guard `beforeShellExecution` deny `gh project item-edit` / GraphQL de Status. **Não** existe `PROCESS_FSM_MOVE` nem allow por env. Exceção: comando que é **somente** a CLI `process_event.py`. `item-edit` no mesmo `command` (encadeado) = deny.
- Actor **não** é flag. CLI e função `process_event()` hardcodam `Agent`. `Guard` só no compile interno de I4/T17 depois do predicado `digest_changed` medido nos arquivos. T1/T7/T15/T16 com Agent = reject; Alan arrasta no board.
- T8 em duas fases (I3): `iniciar_apply` move Status **primeiro**; o retorno **não** é token de Write. Write produto continua deny enquanto `q` ainda for Pronto para Dev.
- T17/I4: `evaluate(iniciar_apply|pedir_review)` com digest mudado/ausente = reject I4; `process_event` então avalia `invalidar_aprovacao` com ator interno Guard e move para Design. Sidecar `.design-digest` só o script grava no T5; Write Agent do sidecar = deny.
- T16: predicado `M_lote` **não** é o autômato de release. Se não aceitar, reject e a mensagem aponta `alan-workflow-ambientes` + `release-guard`. Spec completa de lote permanece fora.
- `request_implement` continua em `illegal_events` (já no yaml #609): `process_event request_implement` = reject, `q` inalterado, lista `enabled_events(q)`.
- Não alterar código de produto. Não paging `sessionStart` / encolher `AGENTS.md` (#613). Não implementar squash/`./restart`/deploy PROD dentro do script.

## Capabilities

### New Capabilities

- `process-fsm-event`: ferramenta SMAG que é a única via do Agent para transições de Status; valida δ e então move o board (ou reject).

### Modified Capabilities

- `process-fsm`: `evaluate()` honra `guard:` do yaml e I4 em T8/T9 (`digest_changed` True/None ⇒ reject, não T8).
- `process-fsm-guard`: deny de Status item-edit/GraphQL (antes do allow sem path); deny de Write em `.design-digest`; sem allow por env.
- `cursor-harness`: o Agent usa `process_event` para mover coluna; chat `implemente`/`autorizo` não é T7.

## Impact

- Novos paths: `scripts/process-fsm/process_event.py` + `test_process_event.py` (e predicados/digest helpers no mesmo pacote).
- Altera `scripts/process-fsm/fsm.py` (`evaluate` + `EvalContext` para guardas).
- Altera `scripts/process-fsm/guard.py` (classificar comando de Status no shell).
- Consome yaml #609, resolver #610, Guard #611 já em `develop`. Job CI `process-fsm` existente cobre os testes novos.
- Sem API, banco, UI de produto. `UI impact: none`. Prototype N/A.
- Lote 2 P1. Homologação: Agent não dispara T7; `iniciar_apply` com Status ainda Pronto para Dev não libera Write.
