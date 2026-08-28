## MODIFIED Requirements

### Requirement: Process FSM table is versioned YAML
The repository SHALL contain `.cursor/process-fsm.yaml` as the compilable source of the 12-column EFSM defined in issue #608. The file MUST declare `states`, `transitions` matching the T0–T17 matrix in `design.md` (including T17a and T17b), `illegal_events`, `illegal_edges`, `enabled_tools` per state, `enabled_events` per state, `context_file` stub per state, invariants I1 through I9, and `fail_closed_asymmetric: true`. The packaged yaml MUST NOT declare `product_globs` or `design_globs` as law; those lists SHALL live in `.covenant-flow/overlay.yaml`. Column **names** in the yaml remain the law for the 12 statuses.

Legal event alphabet Σ SHALL be exactly: `criar_card`, `priorizar`, `cancelar`, `iniciar_design`, `recriticar`, `submeter_design`, `devolver_design`, `aprovar_design`, `iniciar_apply`, `pedir_review`, `achar_bloqueante`, `aceitar_sha`, `rerun_infra`, `falha_codigo`, `integrar_develop`, `homologar`, `fechar_release`, `invalidar_aprovacao`.

#### Scenario: Table lists legal transitions
- **WHEN** the yaml is loaded by the validator
- **THEN** transitions T0–T16 plus T17a and T17b are present with `from`, `event`, `actor`, `actions`, and `to` matching the design.md matrix
- **AND** T17a is Pronto para Dev -- invalidar_aprovacao --> Design
- **AND** T17b is Em desenvolvimento -- invalidar_aprovacao --> Design

#### Scenario: request_implement is not a transition
- **WHEN** the validator inspects `transitions[]`
- **THEN** no transition has event `request_implement`
- **AND** `request_implement` is listed under `illegal_events` (not `illegal_edges` alone) and yields `reject`

#### Scenario: Packaged yaml does not declare globs as law
- **WHEN** the product `process-fsm.yaml` is validated
- **THEN** it does not declare `product_globs` or `design_globs` as yaml law keys
- **AND** it still declares T0–T17, I1–I9, 12 column names, events, and `enabled_tools`
- **AND** `product_globs` and `design_globs` are read from `.covenant-flow/overlay.yaml`
