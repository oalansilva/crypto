## MODIFIED Requirements

### Requirement: The ruler declares the state of the realized measurement

The read-only Jev ruler (`scripts/scalp_jev_eval.py`) SHALL declare, in its report, the **state of the realized measurement** as one of `medido` (measured), `medição parcial` (partially measured), `não medido` (not measured) or `não aplicável` (not applicable — no decisions to join), together with the **real reason** of the state. The state SHALL be derived from the result of reading the real price path (aggTrades or complete 1-second candles), not inferred from free text and not from gappy OHLCV. The state SHALL be declared on its own, distinct from the sample sufficiency of the ruler.

#### Scenario: A fully covered read is declared measured

- **WHEN** the ruler can price every window it needs to measure from aggTrades or complete 1-second candles
- **THEN** the report SHALL declare the realized measurement as `medido`
- **AND** the report SHALL declare the connection or archive used by the measurement

#### Scenario: A read that failed to price every needed window is declared not measured

- **WHEN** the realized side is needed (there are decisions to join) and no window receives a price because the real price path could not be read or does not cover the window
- **THEN** the report SHALL declare the realized measurement as `não medido`
- **AND** the report SHALL declare the real reason of the failure

#### Scenario: A run without decisions is declared not applicable

- **WHEN** the log is absent or empty, so there is no realized side to measure
- **THEN** the report SHALL declare the realized measurement as `não aplicável`
- **AND** the report SHALL NOT treat it as a measurement failure

#### Scenario: Gappy OHLCV is not a successful measurement

- **WHEN** the only available series for a window is gappy or ambiguous OHLCV
- **THEN** that window SHALL NOT be declared `medido` from that series
- **AND** the report SHALL name the missing real price path
