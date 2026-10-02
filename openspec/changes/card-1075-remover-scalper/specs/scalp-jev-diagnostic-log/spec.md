## REMOVED Requirements

### Requirement: Each Jev call logs its entry and return
**Reason**: The directional BTCUSDT scalper is removed from the product (#1075). This capability no longer applies.
**Migration**: Authenticated `/monitor` keeps Em posição, Saída/cobertura, KPIs, filters and Operar. `/api/scalp/*` returns 404. A new Alembic migration drops the five scalp tables; old migrations stay in history. Operar, Carteira, Spot key, candles and the runtime-worker remain.

#### Scenario: Capability no longer in the product
- **WHEN** an authenticated user uses the Farol after this change
- **THEN** this requirement SHALL no longer apply
- **AND** the Farol SHALL NOT run the scalper, show its module, or call Jev for it

### Requirement: Account in the log is summarized and no secret is ever logged
**Reason**: The directional BTCUSDT scalper is removed from the product (#1075). This capability no longer applies.
**Migration**: Authenticated `/monitor` keeps Em posição, Saída/cobertura, KPIs, filters and Operar. `/api/scalp/*` returns 404. A new Alembic migration drops the five scalp tables; old migrations stay in history. Operar, Carteira, Spot key, candles and the runtime-worker remain.

#### Scenario: Capability no longer in the product
- **WHEN** an authenticated user uses the Farol after this change
- **THEN** this requirement SHALL no longer apply
- **AND** the Farol SHALL NOT run the scalper, show its module, or call Jev for it

### Requirement: A cycle refused by a gate logs its skip_reason
**Reason**: The directional BTCUSDT scalper is removed from the product (#1075). This capability no longer applies.
**Migration**: Authenticated `/monitor` keeps Em posição, Saída/cobertura, KPIs, filters and Operar. `/api/scalp/*` returns 404. A new Alembic migration drops the five scalp tables; old migrations stay in history. Operar, Carteira, Spot key, candles and the runtime-worker remain.

#### Scenario: Capability no longer in the product
- **WHEN** an authenticated user uses the Farol after this change
- **THEN** this requirement SHALL no longer apply
- **AND** the Farol SHALL NOT run the scalper, show its module, or call Jev for it

### Requirement: Configurable log level with trading behavior unchanged
**Reason**: The directional BTCUSDT scalper is removed from the product (#1075). This capability no longer applies.
**Migration**: Authenticated `/monitor` keeps Em posição, Saída/cobertura, KPIs, filters and Operar. `/api/scalp/*` returns 404. A new Alembic migration drops the five scalp tables; old migrations stay in history. Operar, Carteira, Spot key, candles and the runtime-worker remain.

#### Scenario: Capability no longer in the product
- **WHEN** an authenticated user uses the Farol after this change
- **THEN** this requirement SHALL no longer apply
- **AND** the Farol SHALL NOT run the scalper, show its module, or call Jev for it

### Requirement: The log file is a single file with a 200 MB ceiling and drops the oldest records
**Reason**: The directional BTCUSDT scalper is removed from the product (#1075). This capability no longer applies.
**Migration**: Authenticated `/monitor` keeps Em posição, Saída/cobertura, KPIs, filters and Operar. `/api/scalp/*` returns 404. A new Alembic migration drops the five scalp tables; old migrations stay in history. Operar, Carteira, Spot key, candles and the runtime-worker remain.

#### Scenario: Capability no longer in the product
- **WHEN** an authenticated user uses the Farol after this change
- **THEN** this requirement SHALL no longer apply
- **AND** the Farol SHALL NOT run the scalper, show its module, or call Jev for it

### Requirement: Diagnostic logging ships DEV-only in this delivery
**Reason**: The directional BTCUSDT scalper is removed from the product (#1075). This capability no longer applies.
**Migration**: Authenticated `/monitor` keeps Em posição, Saída/cobertura, KPIs, filters and Operar. `/api/scalp/*` returns 404. A new Alembic migration drops the five scalp tables; old migrations stay in history. Operar, Carteira, Spot key, candles and the runtime-worker remain.

#### Scenario: Capability no longer in the product
- **WHEN** an authenticated user uses the Farol after this change
- **THEN** this requirement SHALL no longer apply
- **AND** the Farol SHALL NOT run the scalper, show its module, or call Jev for it

### Requirement: Diagnostic output is a log file only (no product surface)
**Reason**: The directional BTCUSDT scalper is removed from the product (#1075). This capability no longer applies.
**Migration**: Authenticated `/monitor` keeps Em posição, Saída/cobertura, KPIs, filters and Operar. `/api/scalp/*` returns 404. A new Alembic migration drops the five scalp tables; old migrations stay in history. Operar, Carteira, Spot key, candles and the runtime-worker remain.

#### Scenario: Capability no longer in the product
- **WHEN** an authenticated user uses the Farol after this change
- **THEN** this requirement SHALL no longer apply
- **AND** the Farol SHALL NOT run the scalper, show its module, or call Jev for it
