## ADDED Requirements

### Requirement: Authoritative GraphQL quota comes from GraphQL response headers
`scripts/process-fsm/` SHALL parse GraphQL remaining/reset from the GraphQL HTTP response: headers `X-RateLimit-Remaining`, `X-RateLimit-Reset`, and `X-RateLimit-Resource` (when Resource is present it MUST be `graphql`), plus JSON `errors[].type == RATE_LIMIT` even when HTTP status is 200. When the query succeeds and headers are absent, the parser MAY use `data.rateLimit.remaining` / `data.rateLimit.resetAt`. `X-RateLimit-Reset` MUST accept a Unix epoch or an ISO-8601 `Z` timestamp. REST `GET /rate_limit` `.resources.graphql.remaining` (including remaining=5000) MUST NOT authorize GraphQL and MUST NOT be written to the GraphQL quota cache. Unit tests MUST inject headers/body fixtures and MUST NOT call GitHub.

#### Scenario: HTTP 200 RATE_LIMIT with headers remaining 0
- **WHEN** a GraphQL response has HTTP 200, JSON `errors[0].type=RATE_LIMIT`, `X-RateLimit-Remaining: 0`, and `X-RateLimit-Reset` set
- **THEN** the parser reports remaining=0 and that reset time
- **AND** it MUST NOT treat the call as a successful Status read

#### Scenario: REST remaining 5000 does not authorize GraphQL
- **WHEN** REST `GET /rate_limit` reports `resources.graphql.remaining=5000` and GraphQL headers report remaining=0
- **THEN** GraphQL is refused
- **AND** the REST remaining MUST NOT be stored as the authoritative GraphQL quota

#### Scenario: Successful query may use rateLimit field
- **WHEN** a GraphQL query succeeds and headers are absent and `data.rateLimit.remaining` is present
- **THEN** that remaining is the authoritative GraphQL remaining for that response

### Requirement: github_status_provider is pontual and fail-immediate on GraphQL quota
`github_status_provider` SHALL query Project 1 Status for issue N with a pontual GraphQL issue→`projectItems` lookup. It MUST NOT list the whole board (`gh project item-list`) to operate one card. When GraphQL remaining is 0 or the body is RATE_LIMIT (including HTTP 200), it MUST fail immediately with the reset time (Q1=A): MUST NOT sleep until reset, MUST NOT retry GraphQL in a loop, and MUST NOT return silent `None` as if the card were off the board. Before calling GraphQL, it MUST consult the GraphQL quota cache: if remaining=0 and now is before `reset_at`, it MUST NOT call the network and MUST fail immediately with the cached reset. After a GraphQL response, it MUST update the cache from headers. Pytest MUST inject the cache path and provider fixtures and MUST NOT call GitHub.

#### Scenario: RATE_LIMIT is not silent None
- **WHEN** `github_status_provider` receives HTTP 200 with `errors[0].type=RATE_LIMIT` and headers remaining=0
- **THEN** it fails immediately with the reset time
- **AND** it MUST NOT return `None` as a missing Status

#### Scenario: Cache skip until reset
- **WHEN** the cache has remaining=0 and `now < reset_at`
- **THEN** `github_status_provider` does not call GraphQL
- **AND** it fails immediately with that reset time

#### Scenario: Pontual Status never lists the board
- **WHEN** the harness reads Status of bound card N
- **THEN** it queries only that issue's project items
- **AND** it MUST NOT call `gh project item-list` to find the column
