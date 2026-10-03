## ADDED Requirements

### Requirement: Backtest applies fixed per-side slippage by timeframe

Every Combo, Discovery, batch and favorite-revalidation backtest whose timeframe is in the Entra table SHALL apply the same per-side slippage in addition to the 0,075% trading fee: 0,02% on `1d` and `4h`; 0,03% on `1h`; 0,05% on `15m`. Buy fills SHALL use price × (1 + slip); sell fills SHALL use price × (1 − slip). The same timeframe SHALL yield the same slip in all four paths.

Timeframes the Combo already runs that are outside that table (`1m`, `5m`, `30m`) SHALL NOT receive a new table row and SHALL NOT inherit 1h or 15m rates. Those runs keep the cost they already had (fee 0,075%; no new slippage from this change).

There SHALL NOT be a UI field to override slippage per run.

#### Scenario: Same 1h strategy cheaper per trade by 0,03% per side

- **GIVEN** a long strategy on 1h over a fixed window
- **WHEN** the backtest runs with this table
- **THEN** return per closed trade is lower than the fee-only path by the 0,03% entry plus 0,03% exit
- **AND** Combo, Discovery, batch and favorite revalidation use 0,03% for that 1h run

#### Scenario: 15m uses 0,05% per side

- **WHEN** a 15m backtest runs on any of the four paths
- **THEN** slippage per side is 0,05%
- **AND** the fee remains 0,075% per side

#### Scenario: 1d and 4h use 0,02% per side

- **WHEN** a 1d or 4h backtest runs on any of the four paths
- **THEN** slippage per side is 0,02%

#### Scenario: Combo 1m 5m 30m get no new table value

- **WHEN** Combo runs a backtest on 1m, 5m or 30m
- **THEN** this change does not apply 0,03% or 0,05% by approximation
- **AND** Discovery still rejects those timeframes
