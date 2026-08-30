## ADDED Requirements

### Requirement: T5 G_design measures the clone gate
When `process_event()` measures `g_design` (argument omitted), it SHALL set the predicate from `files_g_design` composed with the design-route-clone-gate: OpenSpec files present **and** clone-gate pass. `submeter_design` from Design with actor Agent MUST `reject` with `reason` starting with `guard:` when that predicate is false. The YAML transition T5 (`guard: G_design`) MUST stay unchanged. T5 MUST remain offline: no authenticated Playwright and no production credentials inside `process_event`.

#### Scenario: T5 refuses a gallery proto for an existing route
- **WHEN** `process_event submeter_design` runs with `g_design` unset, `q=Design`, valid card binding, `design.md` declaring `UI impact: affected` and `live_route: /monitor`, and the prototype HTML is the r1 gallery fixture (no `table.signals`, `copied` 0)
- **THEN** the result is `reject`
- **AND** the mover is not called
- **AND** `reason` starts with `guard:`

#### Scenario: T5 still accepts UI none OpenSpec package
- **WHEN** `process_event submeter_design` runs with `g_design` unset, `q=Design`, valid card binding, and `design.md` declaring `UI impact: none` plus the three Markdown files and a spec
- **THEN** the result is `transition` to Aprovação de Design when other T5 preconditions hold
- **AND** catalog/`copied` are not required
