## ADDED Requirements

### Requirement: Combo path runs Entra timeframes with table slippage and VWAP

The Combo optimization and backtest path SHALL run `15m` and `1h` with the same engine path used for `4h` and `1d`, applying `backtest-slippage-by-timeframe` and evaluating templates that reference daily or rolling VWAP. It SHALL NOT add a daily-trend filter, hour-of-day rule, ATR stop, or funding model.

Combo MAY continue to accept 1m, 5m and 30m as it already does; those intervals SHALL NOT gain Discovery acceptance or a new slippage row in this change.

#### Scenario: 1h combination uses the shared optimizer path

- **WHEN** Combo or Discovery optimizes a template on 1h
- **THEN** execution uses the existing combination path
- **AND** 0,03% per-side slippage is applied
- **AND** no 1D trend filter is consulted

#### Scenario: VWAP template runs through Combo

- **WHEN** a template with daily VWAP or rolling VWAP is optimized on 15m, 1h or 4h
- **THEN** signal generation completes without error
