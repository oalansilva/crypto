## ADDED Requirements

### Requirement: Favorite trade payloads preserve same-candle trade details
Favorite trade responses SHALL preserve entry and exit timestamps for trades that open and close on the same candle so chart rendering can represent the round trip without losing trade-list detail.

#### Scenario: Saved favorite has same-candle trade
- **WHEN** `/api/favorites/{favorite_id}/trades` returns a saved trade with same-candle entry and exit
- **THEN** the response SHALL keep both `entry_time` and `exit_time`
- **AND** the frontend SHALL not need to infer or discard either side of the trade

#### Scenario: Regenerated favorite has same-candle trade
- **WHEN** trade regeneration returns a same-candle trade
- **THEN** the persisted `metrics.trades` payload SHALL keep both timestamps
- **AND** later chart opens SHALL render from the saved payload consistently
