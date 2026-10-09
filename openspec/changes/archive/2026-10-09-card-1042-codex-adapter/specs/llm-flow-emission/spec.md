## ADDED Requirements

### Requirement: Codex handoffs prove isolated role routing
For Codex local Design, Apply, Review, and QA, the parent SHALL record the selected band, requested model and effort, observed child result, and stage evidence without copying the parent transcript into the child. Each Design, Apply, and Review handoff SHALL keep the existing `proxy modelo: <papel> → <rótulo> (<slug>)` line and add effort for Codex in a parseable adjacent field. Review handoff SHALL include two separate read-only verdicts over the same parent-materialized exact diff. An unobserved model/effort or missing child result MUST NOT be reported as success.

#### Scenario: Codex Design proxy includes effort
- **WHEN** a Codex Design-author or critic child returns
- **THEN** the handoff includes its role, band, label, slug, effort, host completion, and result
- **AND** the child prompt did not include the parent transcript

#### Scenario: Reviewer proxy and verdicts are separate
- **WHEN** the Codex review wave returns
- **THEN** the handoff contains one proxy and verdict per reviewer
- **AND** both identify the same materialized diff digest
- **AND** neither reviewer modified the worktree

#### Scenario: Unproven routing is not success
- **WHEN** the host rejects a model/effort or does not expose sufficient child evidence
- **THEN** the stage is visibly blocked or classified as unproven
- **AND** the handoff does not assert the requested pair was used merely because it appeared in a prompt
