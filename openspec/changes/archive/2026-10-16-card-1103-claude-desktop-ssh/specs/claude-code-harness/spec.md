## ADDED Requirements

### Requirement: Synthetic final turns fail only on API errors
A child whose last `assistant` turn is `<synthetic>` SHALL be classified `failed` only when that turn records an API error; a final `<synthetic>` turn without error SHALL be left out of the model comparison and the status SHALL come from the last real turn (R13).

#### Scenario: Final synthetic without error
- **WHEN** the child's last turn is `<synthetic>` without an error and the previous real turn completed with the captured pair
- **THEN** the child is `completed` with the observed pair of the last real turn

#### Scenario: Final synthetic with API error
- **WHEN** the child's last turn is `<synthetic>` recording an HTTP 429
- **THEN** the child is `failed` and the proxy records an unsuccessful attempt

### Requirement: Closeout parent check applies at the event
For the `claude` client, `process_event fechar_release` SHALL itself check that the parent session's observed model and effort match the captured `claude/execucao` pair before T16, refusing visibly when divergent or unavailable; the check SHALL NOT depend on the runbook being followed (R26). This applies the existing #1101 rule where the event happens and adds no gate.

#### Scenario: T16 from a judgment-model parent
- **WHEN** a Claude Code parent observed on Opus calls `process_event fechar_release`
- **THEN** the event is refused naming the observed and captured pairs, and Status is unchanged

### Requirement: First write of a real child is proven on a real transcript
The check before a child's first write (model and effort of the child's transcript against the capture) SHALL be proven in the live rehearsal with a real child transcript, not only with synthetic fixtures (R27).

#### Scenario: Real child first write
- **WHEN** a real execução child born in the rehearsal makes its first write
- **THEN** the receipt is marked verified when the pair matches, and a divergent pair is denied with `model_mismatch`

### Requirement: Batch closeout rehearsal only on Alan's request
The batch closeout rehearsal in Claude Code (#1101 task 9.6) SHALL run in this change only if Alan asks for it; otherwise his answer SHALL be recorded on the card and the task closed without the rehearsal (R35).

#### Scenario: Alan declines the closeout rehearsal
- **WHEN** Alan answers that he does not want the closeout rehearsal
- **THEN** the card records his answer and no closeout runs

### Requirement: Background child handback is recognized
Evidence collection (`claude_evidence.py collect`/`extract` and `claude_proxy.py`) SHALL recognize two forms of a child's return in the parent transcript: `<agent-message from="{agentId}">` and a `queue-operation` `enqueue` record carrying `<task-notification>`. A `<task-notification>` SHALL be accepted only when its `<task-id>` equals the child's `agentId` and its `<tool-use-id>` equals the spawn `call.id`. Its `<status>` SHALL map `completed` to `completed` with the `<result>` content as payload, `failed` to `failed` and `killed` to `interrupted`. A spawn returning `status="async_launched"` SHALL be accepted when its `resolvedModel` equals the captured model, or, when the spawn carries no `resolvedModel`, the model SHALL be checked on the return or on the child's turns. An unknown return form SHALL yield a visible `unsupported_schema` naming the field and SHALL NOT remain `terminal_unavailable` forever.

#### Scenario: Background child completed
- **WHEN** a child spawned with `async_launched` finishes and the parent transcript has a `<task-notification>` with matching `<task-id>` and `<tool-use-id>`, `<status>completed</status>` and a `<result>`, and the child's turns match the capture
- **THEN** the evidence is `completed` with the `<result>` content as payload and the proxy line shows the observed pair

#### Scenario: Background child failed
- **WHEN** the matching `<task-notification>` has `<status>failed</status>`
- **THEN** the evidence is `failed` and the proxy records an unsuccessful attempt

#### Scenario: Notification for another tool call
- **WHEN** a `<task-notification>` has the child's `<task-id>` but a `<tool-use-id>` different from the spawn `call.id`
- **THEN** it is not accepted as this child's return

#### Scenario: Unknown return form
- **WHEN** the parent transcript returns the child in a form that is neither `<agent-message>` nor a recognizable `<task-notification>`
- **THEN** collection fails with `unsupported_schema` naming the field, not `terminal_unavailable`
