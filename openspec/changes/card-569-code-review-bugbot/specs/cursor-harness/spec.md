## ADDED Requirements

### Requirement: Native Cursor review products MAY use their managed model
`/review-bugbot` and `/review-security` are Cursor-managed products and MAY run on the product-selected model. Custom process reviewers and generic Task fallbacks MUST still use `inherit` unless Alan selects another model in chat.

#### Scenario: Bugbot uses the product model
- **WHEN** Code Review invokes `/review-bugbot` or `/review-security`
- **THEN** the run MAY use the Cursor-managed reviewer model
- **AND** that MUST NOT be treated as a silent swap of the session LLM for implementation or process review

#### Scenario: Process reviewer still inherits
- **WHEN** the session spawns `.cursor/agents/code-reviewer.md` or a generic Task fallback
- **THEN** the child MUST use `inherit` (same chat model)
