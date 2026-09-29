## ADDED Requirements

### Requirement: Applied prazo sets lookback, barrier window and hold together

When a consumed version records a prazo, the directional scalp SHALL use that prazo as the rolling aggTrade lookback (`horizon_s`), the barrier evaluation window and the hold after fill. The panel SHALL show that prazo as «últimos N min». The Jev consult cadence SHALL remain `JEV_TARGET_MS` (30 s by default). The module SHALL NOT present a 1 / 2 / 5 minute radio. Until a version records a prazo, 15 minutes SHALL remain the geometry in use. Interruptor, T, clip, kill, GTX and the Meu Perfil Spot key SHALL stay as in #1001.

#### Scenario: A promoted hour-long prazo is the lookback fact

- **WHEN** the consumed version records a 60-minute prazo
- **THEN** `horizon_s` SHALL be 3600
- **AND** hold after fill SHALL be 60 minutes
- **AND** the module SHALL present «últimos 60 min» as the lookback fact
- **AND** SHALL NOT offer 1 min, 2 min or 5 min as a choice

#### Scenario: Cadence stays detached from prazo

- **WHEN** the user's scalp is ligado and there is no open position
- **THEN** the loop SHALL follow configured `JEV_TARGET_MS` (30 s by default)
- **AND** SHALL NOT treat `horizon_s` as a sleep

#### Scenario: Fifteen minutes remains until a version pays

- **WHEN** no consumed version records a prazo
- **THEN** lookback and hold SHALL stay at 15 minutes
- **AND** the geometry in use SHALL remain until the backtest promotes a longer prazo
