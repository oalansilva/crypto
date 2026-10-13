## ADDED Requirements

### Requirement: Donchian breakout uses the preceding channel and existing volume confirmation

The Canal Donchian + volume template SHALL compare the evaluated candle's close strictly above the maximum high of the N immediately preceding candles, excluding the evaluated candle. It SHALL retain the existing strict volume confirmation, including the existing volume average period, multiplier and inclusion of the evaluated candle's volume. It SHALL require sufficient history and no open position to open a long trade. Validation SHALL cover 4h, 1h and 15m independently without pinning a template timeframe.

#### Scenario: Valid breakout produces a real long entry

- **WHEN** the template is backtested independently on 4h, 1h and 15m with N preceding candles, no open position, close above the preceding channel and volume confirmation satisfied
- **THEN** each backtest records an actual long trade with entry time and price, rather than merely returning signals or completing without error
- **AND** the decision is confirmed at the evaluated candle's close and execution occurs at the next candle's open using the existing execution convention

#### Scenario: Equal or lower close rejects entry

- **WHEN** volume confirmation is satisfied but the evaluated close equals or is below the preceding upper channel in each of 4h, 1h and 15m
- **THEN** no breakout entry is produced by that candle
- **AND** an intrabar high above the channel does not substitute for a close above it

#### Scenario: Missing volume confirmation rejects entry

- **WHEN** the evaluated close exceeds the preceding channel but volume does not strictly exceed the existing confirmation threshold in each of 4h, 1h and 15m
- **THEN** no breakout entry is produced by that candle

#### Scenario: Insufficient history cannot create entry

- **WHEN** fewer than N preceding candles are available, or the existing volume confirmation is not yet available
- **THEN** the template does not produce a breakout entry from an incomplete reference

#### Scenario: Configured channel length is respected

- **WHEN** the channel period is configured to a valid value other than the default
- **THEN** the comparison uses exactly that many preceding candles and continues to exclude the evaluated candle

### Requirement: Donchian entry decisions are causal and preserve unrelated behavior

The corrected template SHALL use only information available through the evaluated candle to decide entry. It SHALL preserve the existing Donchian indicator bands, exit condition, stop loss, other indicators, other templates, approval thresholds, fees, slippage and favorite promotion behavior.

#### Scenario: Future changes do not rewrite entry decisions

- **WHEN** OHLCV candles after the evaluated candle are changed in each of 4h, 1h and 15m
- **THEN** entry decisions through the evaluated candle and their next-candle entry signals are unchanged
- **AND** execution price remains unchanged when the next candle's opening price is held fixed; later exits and profits are not required to remain equal

#### Scenario: Evaluated high is excluded from its own reference

- **WHEN** only the evaluated candle's high changes while its close, volume and preceding history stay fixed
- **THEN** the preceding upper channel and that candle's breakout decision remain unchanged

#### Scenario: Shared indicator and other templates preserve their behavior

- **WHEN** identical data and parameters are evaluated before and after this correction
- **THEN** the Donchian upper, middle and lower indicator series and the template's exit condition are unchanged
- **AND** the other templates introduced by #1074 and an existing template such as Bollinger_Breakout preserve their indicator and signal outputs

#### Scenario: Existing catalog receives the corrected template

- **WHEN** the existing catalog seed loads the versioned export into an empty catalog or refreshes an already populated catalog
- **THEN** Canal Donchian + volume uses the corrected entry condition
- **AND** repeated loading preserves that condition without changing the other templates' definitions
