## ADDED Requirements

### Requirement: Kaizen reads issue surface over REST and Status pontual
The kaizen skill SHALL read issue body, comments, and labels over REST (`gh api repos/<owner>/<repo>/issues/<n>` and REST comments). It MUST NOT call `gh issue view` (with or without `--json`) for those fields. Status of a single card N on Project 1 MUST be a pontual GraphQL query of that card. `/kaizen card N` MUST NOT list the whole board (`gh project item-list`) to operate that card. A full-board `/kaizen` photograph, when the task is the whole board, remains at most one listing per run and MUST NOT retry on RATE_LIMIT. When GraphQL remaining is 0 or the body is RATE_LIMIT (including HTTP 200), kaizen MUST fail immediately with the reset time from GraphQL headers; MUST NOT wait for reset in the same command; MUST NOT treat unknown Status as the card off the board. REST remaining=5000 MUST NOT authorize GraphQL. Audit remains read-only on product code.

#### Scenario: kaizen card N does not item-list the board
- **WHEN** `/kaizen card N` needs Status of issue N
- **THEN** it uses a pontual issue→Status query
- **AND** MUST NOT call `gh project item-list` for that card

#### Scenario: Issue evidence stays on REST
- **WHEN** kaizen reads body or comments of issue N
- **THEN** it uses REST
- **AND** MUST NOT use `gh issue view --json`

#### Scenario: GraphQL quota 0 fails immediately
- **WHEN** GraphQL headers remaining=0 during a board Status read
- **THEN** kaizen fails immediately with the reset time
- **AND** MUST NOT retry GraphQL in a loop
- **AND** MUST NOT wait for reset in the same command
