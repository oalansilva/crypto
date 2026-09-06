## ADDED Requirements

### Requirement: GraphQL quota exhaustion fails immediately and is not unbound
When `process_event` needs Project item id or Status via GraphQL (`_item_id_for_issue`, live mover, or `github_status_provider`) and GraphQL remaining is 0 or the body is RATE_LIMIT (including HTTP 200), it MUST fail immediately with the reset time from GraphQL headers (Q1=A). It MUST NOT sleep until reset in the same command, MUST NOT retry GraphQL in a loop, MUST NOT reject as `unbound` / card off the board, and MUST NOT call `item-edit`. Before GraphQL, it MUST honor the GraphQL quota cache: remaining=0 and `now < reset_at` skips the network. After a GraphQL response, it MUST update that cache from headers. REST `GET /rate_limit` remaining=5000 MUST NOT authorize the call. Unit tests MUST inject quota errors and the cache path and MUST NOT call GitHub.

#### Scenario: item-id RATE_LIMIT is not not-on-project
- **WHEN** `_item_id_for_issue` receives HTTP 200 with `errors[0].type=RATE_LIMIT` and headers remaining=0
- **THEN** `process_event` rejects with the reset time
- **AND** the mover is not called
- **AND** the reason MUST NOT be unbound or issue-not-on-Project

#### Scenario: Periodic aceitar_sha does not storm GraphQL at 0
- **WHEN** the cache has remaining=0 and `now < reset_at` and `process_event` is invoked with `aceitar_sha`
- **THEN** it fails immediately with that reset time
- **AND** it MUST NOT call GraphQL
- **AND** it MUST NOT sleep until reset

#### Scenario: REST remaining 5000 does not authorize mover GraphQL
- **WHEN** REST `resources.graphql.remaining=5000` and GraphQL headers remaining=0
- **THEN** `_item_id_for_issue` / Status read refuse GraphQL
- **AND** issue body/comments MAY still use REST
