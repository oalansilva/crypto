## ADDED Requirements

### Requirement: Issue surface uses REST even when GraphQL quota is 0
While executing `grill-card`, reading and writing issue body, comments, and labels SHALL use the REST API (`gh api repos/<owner>/<repo>/issues/<n>` GET/PATCH, `gh issue edit`, REST comments list/create). The agent MUST NOT call `gh issue view` (with or without `--json`) for those fields. JSON issue view is allowed only for a field REST does not cover. A grill in Em Refinamento that only rewrites the body MUST succeed with GraphQL remaining=0 via REST PATCH. GraphQL quota remaining=0 MUST NOT block that PATCH. Project Status / moving a card remains GraphQL and MUST fail immediately with reset when GraphQL is 0 (no REST bypass for the column). Client skins stay thin MUST Read of the canonical adapter (body at most 8 non-empty lines).

#### Scenario: Body PATCH works with GraphQL quota 0
- **WHEN** Status of issue N is `Em Refinamento` and the child or dsh root only needs to rewrite the issue body and GraphQL headers remaining=0
- **THEN** REST PATCH / `gh issue edit` of that body MUST proceed
- **AND** the actor MUST NOT call `gh issue view`

#### Scenario: Comments and labels stay on REST
- **WHEN** grill-card reads comments or labels of issue N
- **THEN** it uses REST `/issues/N` or `/issues/N/comments`
- **AND** MUST NOT use `gh issue view --json comments`

#### Scenario: Column move has no REST bypass
- **WHEN** GraphQL remaining=0 and the actor would move Project 1 Status
- **THEN** the operation fails immediately with the reset time
- **AND** the skill MUST NOT invent a REST column edit
