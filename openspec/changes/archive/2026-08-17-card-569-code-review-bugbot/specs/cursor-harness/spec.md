## ADDED Requirements

### Requirement: Code Review happy path MUST inherit the chat model
The versioned `diff-reviewer` and `code-reviewer` Tasks MUST use `inherit` unless Alan selects another model in chat. `/review-bugbot` and `/review-security` MAY use the Cursor-managed product model only when Alan explicitly requests those skills.

#### Scenario: Local reviewers inherit
- **WHEN** Code Review spawns `.cursor/agents/diff-reviewer.md` or `.cursor/agents/code-reviewer.md`
- **THEN** the child MUST use `inherit` (same chat model)

#### Scenario: Optional Bugbot uses the product model
- **WHEN** Alan asks for `/review-bugbot` or `/review-security`
- **THEN** that optional run MAY use the Cursor-managed reviewer model
- **AND** that MUST NOT be treated as a silent swap of the session LLM for implementation or the local reviewers
