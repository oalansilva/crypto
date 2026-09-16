## ADDED Requirements

### Requirement: Zoomed-out history keeps strategy overlays and lower panels

On Favorites analysis (`/combo/results`) and the Monitor chart, price overlays and any lower panels the strategy already draws SHALL remain aligned to the loaded candles when the operator zooms out, uses Menos, drags, or Resetar. The default visible range SHALL stay the recent reading crop (~180 candles when the series is longer). Zoom MUST NOT fetch a wider market period than the candles already loaded.

#### Scenario: Menos reveals older loaded candles with their lines

- **WHEN** the operator clicks Menos or zooms out on a series longer than the opening crop
- **THEN** older loaded candles appear with the strategy overlays (and lower panel, when that strategy has one)
- **AND** the visible bar count increases
- **AND** the screen MUST NOT load the whole market for a 6-month or 2-year favorite

#### Scenario: Resetar restores the recent crop with lines still on the series

- **WHEN** the operator clicks Resetar after zooming out
- **THEN** the visible range returns to the recent reading crop (~180 candles when the series is longer)
- **AND** strategy lines remain calculated on the loaded series (not only on the restored crop)

#### Scenario: Synchronized lower panel follows the same crop

- **WHEN** the chart has a lower panel already drawn for that strategy
- **AND** the operator zooms or drags
- **THEN** the lower panel keeps the same visible time range as the price pane
- **AND** its series covers the same loaded candle history
