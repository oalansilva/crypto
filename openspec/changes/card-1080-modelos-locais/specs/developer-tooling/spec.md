## MODIFIED Requirements

### Requirement: Versioned local reviewer subagents exist
The repository SHALL retain diff-reviewer.md and code-reviewer.md with readonly: true and no operational YAML model pin. Their runtime models SHALL come from explicit captured machine execucao parameters, never inherit. Tooling SHALL NOT require a Git edit when the operator changes models.

#### Scenario: Inspect reviewer files
- **WHEN** reviewer agent files are inspected after migration
- **THEN** both exist and remain readonly, with no fixed model or inherit value

### Requirement: Review stance lives in local reviewer agents
Readonly reviewer files SHALL retain constraints on Design/Pronto para Dev, secrets, consumer database requirements, backend tests and visual checks for UI. They SHALL NOT pin operational model values; spawns SHALL use machine selections. Optional REVIEW.md MUST NOT mention Bugbot; BUGBOT.md and Cursor Bugbot MUST NOT be the review path.

#### Scenario: Model changes without constraint changes
- **WHEN** execution model changes locally
- **THEN** reviewer constraints remain versioned and active without rewriting the files
