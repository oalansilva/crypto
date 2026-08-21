## MODIFIED Requirements

### Requirement: Validator rejects an incomplete or nondeterministic table
`scripts/process-fsm/` SHALL validate schema completeness, expansion of `from: Vivo` for T2, and that at most one transition is enabled for a given `(state, event, guard)` tuple. Determinism checks MUST cover Design (T4 vs T5), Code Review (T10 vs T11), and QA (T12/T13/T14). T1 (`priorizar`), T7 (`aprovar_design`), and T15 (`homologar`) MUST include actor Alan. T16 (`fechar_release`) MUST include actor Agent and MUST NOT be validated as an Alan-only gate.

#### Scenario: Missing T7 actor Alan
- **WHEN** a yaml omits Alan as actor on `aprovar_design`
- **THEN** validation MUST fail

#### Scenario: Missing Alan on other human gates
- **WHEN** a yaml omits Alan as actor on `priorizar` or `homologar`
- **THEN** validation MUST fail

#### Scenario: T16 requires Agent not Alan-only
- **WHEN** a yaml sets T16 `fechar_release` actor to Alan only, or omits Agent
- **THEN** validation MUST fail

#### Scenario: Overlapping QA guards
- **WHEN** two transitions from QA share an event with non-exclusive guards
- **THEN** validation MUST fail

## ADDED Requirements

### Requirement: T16 actor is Agent with M_lote
Transition T16 in `.cursor/process-fsm.yaml` SHALL be `Homologado --fechar_release, Agent, guard M_lote--> Pronto` with actions including `release_guard` and `set_status`. Invariant I2 SHALL list Alan-only as T1, T7, and T15 (not T16). Invariant I9 SHALL remain: T16 requires `M_lote`. `enabled_tools` for Homologado SHALL include `process_event`. `evaluate()` with actor Agent, state Homologado, event `fechar_release`, and `M_lote` true SHALL `transition` to Pronto with reason `T16`.

#### Scenario: Agent fechar_release with M_lote transitions
- **WHEN** `evaluate` runs `fechar_release` from Homologado with actor Agent and `M_lote` true
- **THEN** the result is `transition` to Pronto with reason `T16`

#### Scenario: T16 without M_lote is still rejected
- **WHEN** `evaluate` runs `fechar_release` from Homologado with actor Agent and `M_lote` false
- **THEN** the result is `reject`
