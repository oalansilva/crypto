## ADDED Requirements

### Requirement: Chart modal preserves Monitor decision state
The Monitor chart modal SHALL keep the same primary decision label as the Monitor list for the same opportunity when the payload status is actionable, even when candle freshness or marker visibility requires contextual warning text.

#### Scenario: Holding opportunity remains Compra in chart detail
- **WHEN** the Monitor list shows an opportunity as `Compra`
- **AND** the detailed chart detects a candle or marker context mismatch
- **THEN** the chart modal SHALL keep `Compra` as the primary badge and current marker
- **AND** the chart modal SHALL explain the mismatch in signal context

#### Scenario: Exit opportunity remains Venda in chart detail
- **WHEN** the Monitor list shows an opportunity as `Venda`
- **AND** the detailed chart detects a candle or marker context mismatch
- **THEN** the chart modal SHALL keep `Venda` as the primary badge and current marker
- **AND** the chart modal SHALL explain the mismatch in signal context
