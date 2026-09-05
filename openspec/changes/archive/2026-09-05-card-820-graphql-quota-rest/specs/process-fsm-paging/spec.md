## MODIFIED Requirements

### Requirement: sessionStart injects only the Moore page for q
`scripts/process-fsm/` SHALL expose a paging module that, given cwd/path and an injectable `status_provider` / `resolve_fn` / `fsm`, returns `additional_context` for the Cursor `sessionStart` hook. The page MUST include the resolved tuple `(q, bound_card, q_git)`, the verbatim `context_file[q]` stub from `.cursor/process-fsm.yaml` when `q` is a known state, and MUST NOT include the release playbook (`release-guard pre`/`post`, `subir lote`, deploy PROD). The page MUST be at most 20 lines. When `bound_card` is `⊥`, the page MUST use a fixed unbound stub that denies product Write and MUST NOT use the Homologado or release frames. When `bound_card` is issue N and `q` is missing (GraphQL quota remaining=0, RATE_LIMIT including HTTP 200, timeout, JSON failure, or empty Status nodes), the page MUST keep `bound_card=N`, MUST set `q` to missing, MUST NOT use the unbound stub, MUST NOT treat the card as off the Project, and MUST include the GraphQL reset time when the provider reports a quota error with reset. Unit tests MUST inject `status_provider` (the production path: provider result becomes `q`) and MUST NOT call GitHub, Cursor hooks, or the live Project board.

#### Scenario: Todo page omits the release playbook
- **WHEN** `page()` is invoked with injected `status_provider` returning `Todo` and a bound card on `card-<id>-*`
- **THEN** `additional_context` contains the yaml `context_file[Todo]` stub
- **AND** it does not contain `release-guard`, `subir lote`, or `deploy PROD`
- **AND** it has at most 20 lines

#### Scenario: Homologado page is still not the release playbook
- **WHEN** `page()` is invoked with injected `status_provider` returning `Homologado` and a bound card
- **THEN** `additional_context` contains the yaml `context_file[Homologado]` stub
- **AND** it does not contain `release-guard pre`, `release-guard post`, or `deploy PROD`

#### Scenario: Unbound does not load Homologado
- **WHEN** `page()` is invoked with `bound_card=⊥`
- **THEN** `additional_context` uses the unbound stub
- **AND** it does not contain the Homologado `context_file` stub nor the release playbook
- **AND** it contains `bound_card=⊥`

#### Scenario: Bound card with GraphQL quota 0 is not unbound
- **WHEN** `page()` is invoked with bound card N and the status provider fails immediately with GraphQL remaining=0 and a reset time
- **THEN** `additional_context` keeps `bound_card=N`
- **AND** it MUST NOT use the unbound stub
- **AND** it MUST NOT contain `bound_card=⊥`
- **AND** it includes the reset time
- **AND** it has at most 20 lines
- **AND** it does not contain the Homologado `context_file` stub nor the release playbook

#### Scenario: Bound card with unread Status is not unbound
- **WHEN** `page()` is invoked with bound card N and `status_provider` returning `None` without a quota reset (timeout or empty nodes)
- **THEN** `additional_context` keeps `bound_card=N`
- **AND** it MUST NOT use the unbound stub
- **AND** it MUST NOT treat the card as off the board
- **AND** it does not contain the Homologado `context_file` stub nor the release playbook

#### Scenario: Pytest without GitHub
- **WHEN** a contributor runs `pytest scripts/process-fsm -q` at the repo root
- **THEN** paging fixtures execute with injected status/resolve
- **AND** no network call to GitHub is made
