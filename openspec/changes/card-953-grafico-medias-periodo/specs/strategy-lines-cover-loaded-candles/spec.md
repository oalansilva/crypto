## ADDED Requirements

### Requirement: Strategy lines cover the loaded candle history

On `/combo/results` (Favorites full analysis) and on the Monitor chart, every strategy line the chart already draws for that strategy — price moving averages **and** the other declared series, including a lower panel when the strategy has one — SHALL be calculated on the same candle history that screen has already loaded. The chart MUST NOT leave candles covering the period while those lines exist only on a recent crop, stop in the middle, or disappear on older bars of the loaded series.

The crop of the lines SHALL be the loaded candles. A favorite whose period is 6 months or 2 years MUST NOT widen to the whole market to complete indicators. Warmup (the first N−1 candles of a length-N line have no value) MUST NOT be treated as a missing-line hole. Lines MUST NOT paint ahead of the last loaded candle.

#### Scenario: Analysis of a 2-year favorite has lines on the loaded history

- **WHEN** the operator opens full analysis of a 2-year favorite whose candles run 16/09/2024 → 16/09/2026
- **THEN** the strategy lines on that chart (price averages and any other series that strategy already draws) are calculated on that same history
- **AND** the chart MUST NOT show 17/08/2017 as the start only to complete indicators
- **AND** the last line point MUST NOT sit ahead of the last loaded candle

#### Scenario: Visible crop at open already has a line

- **WHEN** the analysis or Monitor chart opens with the recent reading crop (~180 candles when the series is longer)
- **THEN** after warmup the visible candles already have the strategy lines
- **AND** the operator MUST NOT need to guess the value: the line is there

#### Scenario: Zooming out keeps lines on older loaded candles

- **WHEN** the operator uses Menos, zooms out, or drags into older candles that were already in the loaded series
- **THEN** those older candles also have the strategy lines
- **AND** Resetar returns to the recent crop without deleting the lines from the series

#### Scenario: Monitor chart uses the same crop

- **WHEN** the operator reads the Monitor chart for a loaded series
- **THEN** candles and strategy lines share that loaded crop
- **AND** the Monitor MUST NOT hide the strategy lines
- **AND** a 15m / 1h / 4h / 1d series MUST NOT expand to the whole market to complete lines

#### Scenario: Other lines including the lower panel

- **WHEN** the open strategy's chart already draws series besides price moving averages (including a lower panel)
- **THEN** those series SHALL cover the same loaded candle history
- **AND** the product MUST NOT invent a line that strategy does not use

#### Scenario: Another asset and timeframe

- **WHEN** the operator opens analysis or Monitor on another crypto pair or interval of those screens
- **THEN** candles and strategy lines still share the loaded crop
- **AND** this MUST NOT be a hole of a single pair

#### Scenario: 917 and 921 stay closed

- **WHEN** the operator opens analysis after this card
- **THEN** list↔arrow 1:1 of #917 still holds
- **AND** a strategy line MUST NOT advance ahead of the last loaded candle (#921)
- **AND** the favorite's operational period MUST NOT change (#949)
