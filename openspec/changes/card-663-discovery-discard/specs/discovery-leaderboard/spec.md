# discovery-leaderboard Delta

## MODIFIED Requirements

### Requirement: Filter and page within one selected sweep

The leaderboard SHALL list persisted results of the selected sweep excluding `discarded` results by default. Filters (symbol, timeframe, direction) and pagination SHALL operate only on the remaining set. Global rank SHALL be computed among remaining eligible (non-discarded) results.

#### Scenario: Discarded rows omitted from default list

- **WHEN** a sweep has a discarded result and the administrator opens the default leaderboard
- **THEN** that `result_id` is absent
- **AND** remaining rows keep stable ordering among themselves

## ADDED Requirements

### Requirement: Action column always exposes promote and discard when allowed

Each visible non-promoted row SHALL show a Promote control (enabled only when unique and eligible; otherwise visible and disabled with reason) **and** a Discard control. An `already_promoted` row SHALL show the promoted state and SHALL NOT show Discard. Promote MUST NOT be hidden solely because eligibility failed.

#### Scenario: Low sample still shows both actions

- **WHEN** a row is `Baixa amostra`
- **THEN** Promote is visible and disabled with the sample reason
- **AND** Excluir is visible and enabled
