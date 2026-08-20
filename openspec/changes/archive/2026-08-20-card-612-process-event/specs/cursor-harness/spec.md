## ADDED Requirements

### Requirement: Agent moves Status only via process_event
While this change is active, the Cursor Agent MUST NOT invoke `gh project item-edit` (or GraphQL `updateProjectV2ItemFieldValue`) to change Project 1 `Status`. Named transitions SHALL go through `scripts/process-fsm/process_event.py`. Chat utterances such as `implemente`, `autorizo`, or `arrastei` MUST NOT be treated as `aprovar_design` / T7.

#### Scenario: Chat implemente is not T7
- **WHEN** the user says `implemente` and `Status` is not `Pronto para Dev`
- **THEN** the Agent MUST NOT call `process_event aprovar_design` as a successful transition
- **AND** MUST NOT `item-edit` Status

#### Scenario: implemente in Pronto para Dev is iniciar_apply
- **WHEN** the user says `implemente` and `Status` is `Pronto para Dev`
- **THEN** the Agent SHALL call `process_event iniciar_apply` (not `aprovar_design`)
- **AND** SHALL NOT `item-edit` Status

#### Scenario: Legal apply uses process_event
- **WHEN** `Status=Pronto para Dev` and the Agent starts implementation
- **THEN** the Agent SHALL call `process_event iniciar_apply` before product Write
- **AND** SHALL NOT treat the function return as a Write allow token
