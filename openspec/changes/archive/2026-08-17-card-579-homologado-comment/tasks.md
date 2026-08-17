# Tasks: card-579-homologado-comment

## Design (este turno)

- [x] 0. OpenSpec superset do issue #579 (crítica + Gist antes de Aprovação de Design)

## Apply (após Pronto para Dev)

- [x] 1. `pre`: `normalize_release_cards`; ramo REST separado (zero `BOARD_STATE`/`card_status`/`item-list`); inválido = blocker sem REST; unset = warn
- [x] 2. `AGENTS.md`: arraste Homologado ⇒ helper no mesmo turno **mesmo sem lote**; snippets de `pre` de lote exportam `RELEASE_CARDS`
- [x] 3. Evidência: FAIL sem marcador; PASS com marcador; warn sem env; FAIL token inválido sem comments; `pre` não consulta Project
