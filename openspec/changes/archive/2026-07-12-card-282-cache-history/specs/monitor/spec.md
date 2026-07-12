## ADDED Requirements

### Requirement: Partial candle caches preserve valid trade history
The favorite read model MUST treat saved candles as a potentially partial window and MUST NOT discard a historical trade only because its entry predates the first saved candle.

#### Scenario: Saved candles contain only recent context
- **WHEN** a cached trade entry predates the first saved analysis candle and its exit is not beyond the known coverage end
- **THEN** the read model MUST preserve that trade

#### Scenario: Trades were never generated
- **WHEN** saved metrics do not contain a `trades` list
- **THEN** the read model MUST preserve that absence so the regeneration path can execute
