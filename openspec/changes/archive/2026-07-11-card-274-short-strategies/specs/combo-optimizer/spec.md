## ADDED Requirements

### Requirement: Modern Combo Execution Supports Direction

The combo optimizer SHALL execute modern combo strategies through a direction-aware trade extraction path that supports `long` and `short`.

#### Scenario: Short trade profit follows inverse price movement

- **GIVEN** a combo strategy emits `signal == 1` as entry and `signal == -1` as exit
- **AND** the execution direction is `short`
- **WHEN** exit price is below entry price
- **THEN** the resulting trade profit SHALL be positive

#### Scenario: Short stop loss is above entry

- **GIVEN** a short combo trade entered at a price
- **WHEN** a later candle high reaches the configured stop above entry
- **THEN** the trade SHALL close as a stop loss

#### Scenario: Long default is preserved

- **GIVEN** a combo request omits direction
- **WHEN** the optimizer executes the strategy
- **THEN** direction SHALL default to `long`
- **AND** existing long stop/profit behavior SHALL remain unchanged

### Requirement: Combo Signal Generation Must Not Apply Long-Only Stops To Shorts

`ComboStrategy.generate_signals` SHALL NOT emit a short exit merely because candle low moved below entry as a long-style stop.

#### Scenario: Falling price does not stop a short

- **GIVEN** a strategy is evaluated with direction `short`
- **AND** the active entry price is above a later candle low
- **WHEN** the low movement would be profitable for a short
- **THEN** signal generation SHALL NOT create a stop-loss exit for that low movement
