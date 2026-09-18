## ADDED Requirements

### Requirement: First opportunities GET computes or fails when the user has crypto favorites

`GET /api/opportunities/` on the first Monitor visit (without an operator `refresh=true`) SHALL NOT return a successful empty catalog when the requesting user has crypto favorites. A cache miss, a cached `[]`, or a stale `[]` MUST recompute or fail visibly. The endpoint MUST NOT persist a successful empty payload as the catalog answer while those favorites exist.

#### Scenario: Cached empty is not served as catalog

- **WHEN** the user has at least one crypto favorite
- **AND** the in-memory opportunities cache is missing, fresh-empty, or stale-empty
- **AND** the client calls `GET /api/opportunities/` without `refresh=true`
- **THEN** the service recomputes or fails
- **AND** MUST NOT return 200 `[]` as a catalog-empty success from that cache entry

#### Scenario: Recompute with analyzed subset returns the rows

- **WHEN** the user has crypto favorites
- **AND** analysis produces a non-empty subset (incident: 11 of 18)
- **THEN** `GET /api/opportunities/` returns those analyzed opportunities
- **AND** MUST NOT require a separate operator refresh to stop returning `[]`

#### Scenario: Skip-all or compute failure is not a successful empty catalog

- **WHEN** the user has crypto favorites
- **AND** analysis skips every favorite or the compute fails
- **THEN** the API MUST NOT present that result to `/monitor` as a successful empty catalog
- **AND** the operator-visible outcome is the existing Monitor load error

#### Scenario: Non-empty cache remains reusable

- **WHEN** the cache holds a non-empty opportunities payload within TTL
- **THEN** `refresh=false` callers (including Favorites reading signal_history) MAY reuse that payload
- **AND** this card SHALL NOT strip candles or trades from chart/analysis flows
