## REMOVED Requirements

### Requirement: Every record carries the model version that answered
**Reason**: The directional BTCUSDT scalper is removed from the product (#1075). This capability no longer applies.
**Migration**: Authenticated `/monitor` keeps Em posição, Saída/cobertura, KPIs, filters and Operar. `/api/scalp/*` returns 404. A new Alembic migration drops the five scalp tables; old migrations stay in history. Operar, Carteira, Spot key, candles and the runtime-worker remain.

#### Scenario: Capability no longer in the product
- **WHEN** an authenticated user uses the Farol after this change
- **THEN** this requirement SHALL no longer apply
- **AND** the Farol SHALL NOT run the scalper, show its module, or call Jev for it

### Requirement: The call requests a fixed model version, never the moving alias
**Reason**: The directional BTCUSDT scalper is removed from the product (#1075). This capability no longer applies.
**Migration**: Authenticated `/monitor` keeps Em posição, Saída/cobertura, KPIs, filters and Operar. `/api/scalp/*` returns 404. A new Alembic migration drops the five scalp tables; old migrations stay in history. Operar, Carteira, Spot key, candles and the runtime-worker remain.

#### Scenario: Capability no longer in the product
- **WHEN** an authenticated user uses the Farol after this change
- **THEN** this requirement SHALL no longer apply
- **AND** the Farol SHALL NOT run the scalper, show its module, or call Jev for it

### Requirement: Pinning the version does not change the question
**Reason**: The directional BTCUSDT scalper is removed from the product (#1075). This capability no longer applies.
**Migration**: Authenticated `/monitor` keeps Em posição, Saída/cobertura, KPIs, filters and Operar. `/api/scalp/*` returns 404. A new Alembic migration drops the five scalp tables; old migrations stay in history. Operar, Carteira, Spot key, candles and the runtime-worker remain.

#### Scenario: Capability no longer in the product
- **WHEN** an authenticated user uses the Farol after this change
- **THEN** this requirement SHALL no longer apply
- **AND** the Farol SHALL NOT run the scalper, show its module, or call Jev for it
