# cursor-harness Delta Specification

## ADDED Requirements

### Requirement: Em Refinamento story sharpening uses grill-card

The Cursor harness SHALL load `.cursor/skills/grill-card/SKILL.md` and `.cursor/skills/grilling/SKILL.md` as regular files in `oalansilva/crypto`. `alan-workflow` SHALL describe Em Refinamento as intake **and** story grilling (issue body ledger, T1 Alan-only). `github-project-board` SHALL state the same for the Em Refinamento column. Agents MUST NOT treat `grill-with-docs` or `to-spec` as the project entry skill.

#### Scenario: Fresh clone has adapter and primitive
- **WHEN** a Cursor session starts from a GitHub checkout
- **THEN** `.cursor/skills/grill-card/SKILL.md` and `.cursor/skills/grilling/SKILL.md` exist and are not mode `120000`
- **AND** `alan-workflow` names `grill-card` for Em Refinamento

#### Scenario: Design synthesizes a grilled issue
- **WHEN** `Status=Design` and the bound issue body contains the grill-card DoD sections
- **THEN** `/opsx:new` / `/opsx:ff` SHALL use that issue as briefing and MUST NOT start a new interview
- **AND** MUST NOT invoke `grill-card` or `grill-with-docs` as a step to generate `proposal.md`

#### Scenario: Incomplete DoD in Design
- **WHEN** `Status=Design` and the bound issue body is missing any grill-card DoD section
- **THEN** the agent MUST NOT run `/opsx:ff` and MUST NOT invent story text
- **AND** SHALL comment the missing sections and remain in Design
- **AND** `/opsx:explore` MAY run only for technical codebase questions, not to rewrite product scope

#### Scenario: Em Refinamento page mentions grilling the issue
- **WHEN** a session starts bound to a card with `Status=Em Refinamento`
- **THEN** `context_file[Em Refinamento]` instructs issue clarification / grill-card and that chat is not T1
