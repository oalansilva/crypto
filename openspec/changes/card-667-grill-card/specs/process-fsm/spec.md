# process-fsm Delta Specification

## ADDED Requirements

### Requirement: Moore stubs describe grill-card without new states

`.cursor/process-fsm.yaml` `context_file` stubs SHALL describe the grill-card ritual without adding states or changing T0/T1. `context_file[Em Refinamento]` SHALL tell the agent to clarify the card and grill the GitHub issue, that chat is not T1, and not to write `CONTEXT.md` on develop. `context_file[Todo]` SHALL contain the exact substring `Próximo evento = iniciar_design. Não apply. Não /opsx:new ainda.` `context_file[Design]` SHALL tell the agent to synthesize OpenSpec from the grilled issue and not to re-interview. sessionStart paging MUST remain ≤20 lines. `enabled_tools` for Em Refinamento SHALL remain `[issue_edit, comment]` and MUST NOT add `write_openspec`.

#### Scenario: Todo stub keeps paging contract
- **WHEN** `.cursor/process-fsm.yaml` `context_file.Todo` is read
- **THEN** it contains `Próximo evento = iniciar_design. Não apply. Não /opsx:new ainda.`

#### Scenario: Em Refinamento stub names issue grilling
- **WHEN** `.cursor/process-fsm.yaml` `context_file['Em Refinamento']` is read
- **THEN** it mentions clarifying the card and that chat is not T1
- **AND** it mentions grill-card or grilling the issue

#### Scenario: T0 and T1 unchanged
- **WHEN** the compiled transition table is inspected
- **THEN** T0 still targets Em Refinamento
- **AND** T1 `priorizar` remains Alan-only from Em Refinamento to Todo

#### Scenario: Em Refinamento tools stay issue-only
- **WHEN** `.cursor/process-fsm.yaml` `enabled_tools` for Em Refinamento is read
- **THEN** it is `[issue_edit, comment]`
- **AND** it does not include `write_openspec`
