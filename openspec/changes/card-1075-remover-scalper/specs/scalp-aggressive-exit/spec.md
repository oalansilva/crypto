## REMOVED Requirements

### Requirement: An aggressive exit closes any position the passive exit did not fill
**Reason**: The directional BTCUSDT scalper is removed from the product (#1075). This capability no longer applies.
**Migration**: Authenticated `/monitor` keeps Em posição, Saída/cobertura, KPIs, filters and Operar. `/api/scalp/*` returns 404. A new Alembic migration drops the five scalp tables; old migrations stay in history. Operar, Carteira, Spot key, candles and the runtime-worker remain.

#### Scenario: Capability no longer in the product
- **WHEN** an authenticated user uses the Farol after this change
- **THEN** this requirement SHALL no longer apply
- **AND** the Farol SHALL NOT run the scalper, show its module, or call Jev for it

### Requirement: No position crosses the waiting window without an exit attempt, and the aggressive exit is visible
**Reason**: The directional BTCUSDT scalper is removed from the product (#1075). This capability no longer applies.
**Migration**: Authenticated `/monitor` keeps Em posição, Saída/cobertura, KPIs, filters and Operar. `/api/scalp/*` returns 404. A new Alembic migration drops the five scalp tables; old migrations stay in history. Operar, Carteira, Spot key, candles and the runtime-worker remain.

#### Scenario: Capability no longer in the product
- **WHEN** an authenticated user uses the Farol after this change
- **THEN** this requirement SHALL no longer apply
- **AND** the Farol SHALL NOT run the scalper, show its module, or call Jev for it
