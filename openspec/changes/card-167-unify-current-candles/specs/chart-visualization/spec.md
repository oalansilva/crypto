## MODIFIED Requirements

### Requirement: Result charts opened from saved items use the shared current candle source
Result chart surfaces opened from saved favorites SHALL prefer the same current market candle source used by Monitor for UI chart rendering.

#### Scenario: Favorites and Monitor align on latest candle
- **WHEN** Monitor and Favorites display the same symbol and timeframe
- **THEN** both chart surfaces use the current market candle source
- **AND** their newest candle date is aligned when the source has current data
