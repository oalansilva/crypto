## ADDED Requirements

### Requirement: Moore Design stub names OpenSpec and prototype allow
`.cursor/process-fsm.yaml` `context_file[Design]` SHALL tell the agent to synthesize OpenSpec from the grilled issue and not to re-interview. The stub MUST contain the contiguous substring `OpenSpec/protótipo allow`. The stub MUST still contain `Write produto deny` (product Write only; not a deny of OpenSpec, prototype, or spawning the Design-autor). The stub MUST NOT package only `Write produto deny` without that carve-out. sessionStart paging MUST remain at most 20 lines. This change MUST NOT add a state, event, hook, or `enabled_tools` entry. `enabled_tools[Design]` SHALL remain `[write_openspec, write_prototype, gist, task_critique]`. `guard.py` `decide()` MUST NOT change for this requirement.

#### Scenario: Design stub keeps synthesize and not re-interview
- **WHEN** `.cursor/process-fsm.yaml` `context_file.Design` is read
- **THEN** it contains `sintetizar`
- **AND** it contains `não reentrevistar`

#### Scenario: Design stub names OpenSpec and prototype allow
- **WHEN** `.cursor/process-fsm.yaml` `context_file.Design` is read
- **THEN** it contains `OpenSpec/protótipo allow`
- **AND** it contains `Write produto deny`
- **AND** it is not only `Write produto deny` without the carve-out

#### Scenario: Design tools and delta stay untouched
- **WHEN** `.cursor/process-fsm.yaml` `enabled_tools` for Design is read
- **THEN** it is `[write_openspec, write_prototype, gist, task_critique]`
- **AND** no new state, event, or `enabled_tools` key is added by this change
- **AND** `scripts/process-fsm/guard.py` `decide()` has no new needles for this card
