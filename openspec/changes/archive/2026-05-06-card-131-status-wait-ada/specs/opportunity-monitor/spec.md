## ADDED Requirements

### Requirement: Active entry state remains consistent with fresh market candles
The opportunity monitor SHALL classify a strategy with a confirmed active entry as HOLD or exit-tracking HOLD when fresh candles show no later exit invalidating that entry.

#### Scenario: Fresh ADA-like daily candles include active entry
- **WHEN** the strategy signal history contains an entry after the latest exit
- **AND** fresh daily candles confirm the active trend gate
- **THEN** the opportunity payload MUST set `is_holding=true`
- **AND** the Monitor UI MUST not display the opportunity as WAIT in the list.
