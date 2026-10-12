## MODIFIED Requirements

### Requirement: Versioned juízo/execução map file
The adapter SHALL version routing policy and forbidden models, including composer-2.5-fast and inherit, while operational selections SHALL come solely from the machine-model-selection contract. The legacy `.cursor/model-map.yaml` SHALL NOT supply spawn choices or fallback. All five clients SHALL have distinct juizo/execucao selections and capability validation. Cursor and Grok migration SHALL preserve their existing choices; Codex SHALL initialize to the choices explicitly requested in this change. Missing/invalid configuration or unsupported host values SHALL cause visible refusal without picker inheritance or substitution.

#### Scenario: New spawn reads local selection
- **WHEN** a parent spawns a child
- **THEN** the selected client's band is resolved from machine configuration and its supported parameters are passed explicitly

#### Scenario: Legacy map only
- **WHEN** only the Git map exists
- **THEN** the parent refuses with a migration diagnostic instead of using it as fallback

### Requirement: Role models by juízo and execução
Juizo SHALL include grill-card, Design-author, Design-critic and Assessments; execucao SHALL include Apply, QA, both reviewers, same-card search and fecho-lote. The client's machine selection SHALL be explicit on every supported native spawn path. No client SHALL inherit the picker. OpenCode/dsh SHALL use their native supported selection paths or refuse visibly. Agent-file YAML SHALL NOT pin an operational model. Parent-picker instructions, unrelated host restrictions and process gates SHALL remain unchanged.

#### Scenario: Client-specific role
- **WHEN** an execution reviewer is spawned on any supported client
- **THEN** it receives that client's execution selection and cannot pass merely by matching a juizo selection

### Requirement: Code Review happy path MUST use Composer execução model
Both diff-reviewer and code-reviewer SHALL use the current client's captured machine execucao selection, with explicit native parameters and no versioned YAML model pin. Composer is a historical migration choice, not a permanent requirement. Grok reviewers SHALL remain supported. Bugbot MUST NOT be a product path; security review only when explicitly requested MUST NOT replace the local gate. Constraints SHALL remain in agent files and optional REVIEW.md without Bugbot.

#### Scenario: Review after operational choice change
- **WHEN** local execucao changes before a new review wave
- **THEN** both reviewers use the new client-specific choice without modifying agent files

### Requirement: Composer destape and resume keep execução slug
Cursor continuation SHALL retain the child's captured execution selection, including billing/runtime identity. Forbidden or divergent continuation SHALL be visibly rejected and MUST NOT count as acceptance or be resumed to repair its model. A new Task SHALL resolve the current machine choice explicitly. Same-card search SHALL use generalPurpose when explore routes to a forbidden model. Fecho-lote SHALL retain its prohibition on sidecar/destape and ignore host auto-resume.

#### Scenario: Local edit during continuation
- **WHEN** local execution selection changes while a child remains alive
- **THEN** continuation retains its birth capture; only a new Task uses the updated choice

### Requirement: Grok execução resume outside grok-4.6 does not count
Grok continuation SHALL retain the execution selection captured at birth. Any different runtime model SHALL fail visibly, regardless of whether it is otherwise host-accepted. A replacement SHALL be a new child with current local selection and a self-contained prompt. grok-4.6 SHALL remain a migration value, not a hardcoded perpetual gate. Cursor forbidden-model restrictions SHALL remain intact.

#### Scenario: Grok continuation diverges
- **WHEN** a continuation uses a different model from its captured request
- **THEN** it does not count and a new explicitly configured child is required
