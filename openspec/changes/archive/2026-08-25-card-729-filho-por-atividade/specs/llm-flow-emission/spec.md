## MODIFIED Requirements

### Requirement: One chat per column without a new FSM gate
The runbook SHALL require one operator chat per card titled `#<id>` covering Em Refinamento through Done técnico on both Cursor and Grok. Homologado and Release/lote MUST stay out of that chat. The parent session MUST NOT execute grill, Design authorship (except writing only `## Design Critique` after A/B as specified in `cursor-harness`), Apply, Code Review, or QA; it SHALL spawn an isolated child (or dual-critic / dual-reviewer wave) whose prompt is only that activity's context. Mixing activities means the parent executing another column, not a missing chat title. When Apply is requested without `Status=Pronto para Dev`, the parent MUST refuse in the **same** chat with current Status plus “Apply só depois de Pronto para Dev (T7 teu)” and MUST NOT ask the operator to open `#<id> Apply`. This SHALL NOT add a state, event, hook, or `enabled_tools` change to `.cursor/process-fsm.yaml`.

#### Scenario: Agent refuses a mixed column chat
- **WHEN** a chat `#<id>` is in `Status=Design` and receives an Apply/Review/Release execution request
- **THEN** the parent refuses to execute that other activity itself
- **AND** it does not tell the operator to open a new chat titled `#<id> <coluna>`
- **AND** if Status is not `Pronto para Dev`, it does not spawn the Apply child
- **AND** `process-fsm.yaml` is unchanged

#### Scenario: New column starts a new chat
- **WHEN** the operator starts Apply after Design in the same `#<id>` chat and `Status=Pronto para Dev`
- **THEN** Apply runs in an isolated child spawned from that same chat
- **AND** the parent does not continue executing Apply in its own transcript
- **AND** the operator is not told to open `#<id> Apply`
