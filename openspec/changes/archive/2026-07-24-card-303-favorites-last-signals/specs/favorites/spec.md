## ADDED Requirements

### Requirement: Favorites shows Monitor last signals
When the user opens strategy analysis from Favorites, the results view SHALL show the same recent confirmed signals available for that strategy/symbol/timeframe on the Monitor.

#### Scenario: Monitor has recent signals
- **WHEN** the matching Monitor opportunity has a non-empty `signal_history`
- **THEN** Favorites results SHALL display those last signals ordered from newest to oldest
- **AND** SHALL use Compra/Venda semantics consistent with strategy direction (`long`/`short`)
- **AND** SHALL NOT invent signals absent from the Monitor history.

#### Scenario: Same strategy on both surfaces
- **WHEN** the same strategy, symbol and timeframe are open on Monitor and Favorites
- **THEN** the Favorites last-signal events SHALL match the Monitor history for that recorte
- **AND** SHALL preserve timestamp/type/price enough for the trader to recognize each event.

#### Scenario: No trustworthy history
- **WHEN** the Monitor match has no signal history
- **THEN** Favorites SHALL show an explicit empty state
- **AND** SHALL NOT imply that signals exist.

#### Scenario: Monitor sync fails or times out
- **WHEN** Favorites cannot obtain Monitor signal history in time or the match is missing
- **THEN** Favorites SHALL expose an explicit failure/unavailable state for last signals
- **AND** SHALL NOT silently present an empty history as if none existed.

### Requirement: Favorites last-signal sync uses Monitor cache first
Favorites SHALL prefer the Monitor opportunities cache when loading last signals for “Ver resultados”, instead of forcing a full refresh that commonly times out.

#### Scenario: Opening favorite analysis
- **WHEN** the user opens analysis from Favorites
- **THEN** the client SHALL attempt to load matching Monitor `signal_history` without requiring a full opportunities refresh by default
- **AND** SHALL propagate `signal_history` into the results view state for rendering.
