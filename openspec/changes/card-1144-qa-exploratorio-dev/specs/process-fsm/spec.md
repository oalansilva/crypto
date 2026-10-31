## MODIFIED Requirements

### Requirement: Moore QA stub requires same-turn T14
`.cursor/process-fsm.yaml` `context_file[QA]` SHALL tell the parent to leave product source untouched. The stub MUST name both client paths in one short Moore page: Cursor/Grok — the QA child (when the client spawns one) reads checks and MUST NOT call `process_event`; dsh — the runtime root MUST NOT spawn a QA child and MUST wait for `qa-gate` in the same turn (`job_output wait`, without `continue`). The parent MUST invoke `integrar_develop` in the same turn as a green child (or, on dsh, after `qa-gate` success). The stub MUST say the first reject is not the end of the turn: `qa-gate pending` waits and retries T14; `no_pr` and `sync: dirty` are visible causes. The stub MAY still mention T13 returning to Em desenvolvimento. The stub MUST also say that, with `qa_dev` on, `qa_dev_pendente` after the first T14 means running the DEV test and calling T14 again; `qa_dev_fail` means stopping to ask Alan, with T13 only after he confirms the defect and a retest without diff if he disagrees; `qa_dev_inconclusivo` means stopping and showing Alan the options; and the test agent MUST NOT call `process_event`. The agent MUST NOT post `/qa-dev-liberar`. sessionStart paging MUST remain at most 20 lines. This change MUST NOT add a state, event, or `enabled_tools` entry.

#### Scenario: QA stub names same-turn T14
- **WHEN** `.cursor/process-fsm.yaml` `context_file.QA` is read
- **THEN** it tells the parent to call T14 in the same turn as green QA
- **AND** it says the first reject is not the end of the turn
- **AND** it tells the QA child not to call `process_event`

#### Scenario: QA paging stays short
- **WHEN** `page()` compiles a bound card with `q=QA`
- **THEN** `additional_context` is at most 20 lines
- **AND** it contains the yaml `context_file[QA]` stub

#### Scenario: QA stub names dsh root closeout
- **WHEN** `.cursor/process-fsm.yaml` `context_file.QA` is read
- **THEN** it says the dsh root MUST NOT spawn a QA child
- **AND** it says to wait for `qa-gate` in the turn without `continue`
- **AND** it still tells a Cursor/Grok QA child not to call `process_event`

#### Scenario: QA stub names the DEV test phases
- **WHEN** `.cursor/process-fsm.yaml` `context_file.QA` is read
- **THEN** it says `qa_dev_pendente` means running the DEV test and calling T14 again
- **AND** it says `qa_dev_fail` means stopping to ask Alan before T13
- **AND** it says `qa_dev_inconclusivo` means stopping and showing Alan the options
- **AND** it says the agent does not post `/qa-dev-liberar`
