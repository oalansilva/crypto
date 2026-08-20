# process-fsm Specification

## Purpose
Tabela EFSM compilável das 12 colunas do processo (`T0`–`T17` + fixtures), versionada em `.cursor/process-fsm.yaml`. Consumida pelo resolver (#610) e pelo Guard Write (#611).

## Requirements

### Requirement: Process FSM table is versioned YAML
The repository SHALL contain `.cursor/process-fsm.yaml` as the compilable source of the 12-column EFSM defined in issue #608. The file MUST declare `states`, `transitions` matching the T0–T17 matrix in `design.md` (including T17a and T17b), `illegal_events`, `illegal_edges`, `enabled_tools` per state, `enabled_events` per state, `context_file` stub per state, `product_globs`, `design_globs`, invariants I1 through I9, and `fail_closed_asymmetric: true`.

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

### Requirement: Product write is gated by I1 not banned globally
`write_produto` MUST NOT appear in `illegal_events`. It SHALL be modeled as a Moore/tool action allowed only when invariant I1 holds (`q` in Em desenvolvimento or Code Review, `q_git=card-<id>`, `bound_card=id`, path in that worktree). Combinations that violate I1 MUST appear in `illegal_edges` and yield `reject`.

#### Scenario: Write allowed under I1
- **WHEN** the fixture applies `write_produto` in Em desenvolvimento with `bound_card` set and `q_git=card-<id>`
- **THEN** the expected result is `allow`

#### Scenario: Illegal Write in Todo
- **WHEN** the fixture applies `write_produto` in state Todo
- **THEN** the expected result is `reject` and the state is unchanged

#### Scenario: Agent cannot approve design
- **WHEN** the fixture applies `aprovar_design` with actor Agent
- **THEN** the expected result is `reject`

#### Scenario: Unbound product write
- **WHEN** the fixture applies `write_produto` with `bound_card` unset
- **THEN** the expected result is `reject`

### Requirement: Validator rejects an incomplete or nondeterministic table
`scripts/process-fsm/` SHALL validate schema completeness, expansion of `from: Vivo` for T2, and that at most one transition is enabled for a given `(state, event, guard)` tuple. Determinism checks MUST cover Design (T4 vs T5), Code Review (T10 vs T11), and QA (T12/T13/T14).

#### Scenario: Missing T7 actor Alan
- **WHEN** a yaml omits Alan as actor on `aprovar_design`
- **THEN** validation MUST fail

#### Scenario: Missing Alan on other human gates
- **WHEN** a yaml omits Alan as actor on `priorizar`, `homologar`, or `fechar_release`
- **THEN** validation MUST fail

#### Scenario: Overlapping QA guards
- **WHEN** two transitions from QA share an event with non-exclusive guards
- **THEN** validation MUST fail

### Requirement: Fixtures live under scripts/process-fsm and run without GitHub
The change SHALL include pytest modules matching `scripts/process-fsm/test_*.py` that exercise the design.md matrix and the illegal edges Todo+Write, develop+Write, Done+Write, Agent+T7, and unbound+Write. Tests MUST NOT call GitHub, Cursor hooks, or the Project board. Continuous integration MUST run `pytest scripts/process-fsm -q`.

#### Scenario: Pytest path
- **WHEN** a contributor runs `pytest scripts/process-fsm -q` at the repo root
- **THEN** the legal and illegal fixtures execute and the command exits 0 for a valid yaml

### Requirement: Card 609 does not enable Cursor write hooks
This change MUST NOT register `preToolUse` or `beforeShellExecution` guards and MUST NOT modify product code under `backend/` or `frontend/src/`.

#### Scenario: hooks.json unchanged by this card
- **WHEN** the #609 diff is reviewed
- **THEN** `.cursor/hooks.json` is unmodified
- **AND** no `Write` of product paths is introduced
