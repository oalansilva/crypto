## ADDED Requirements

### Requirement: Moore QA stub requires same-turn T14
`.cursor/process-fsm.yaml` `context_file[QA]` SHALL tell the parent to leave product source untouched, that the QA child (when the client spawns one) reads checks and MUST NOT call `process_event`, and that the parent MUST invoke `integrar_develop` in the same turn as a green child (or, on dsh, after `qa-gate` success). The stub MUST say the first reject is not the end of the turn: `qa-gate pending` waits and retries T14; `no_pr` and `sync: dirty` are visible causes. The stub MAY still mention T13 returning to Em desenvolvimento. sessionStart paging MUST remain at most 20 lines. This change MUST NOT add a state, event, or `enabled_tools` entry.

#### Scenario: QA stub names same-turn T14
- **WHEN** `.cursor/process-fsm.yaml` `context_file.QA` is read
- **THEN** it tells the parent to call T14 in the same turn as green QA
- **AND** it says the first reject is not the end of the turn
- **AND** it tells the QA child not to call `process_event`

#### Scenario: QA paging stays short
- **WHEN** `page()` compiles a bound card with `q=QA`
- **THEN** `additional_context` is at most 20 lines
- **AND** it contains the yaml `context_file[QA]` stub
