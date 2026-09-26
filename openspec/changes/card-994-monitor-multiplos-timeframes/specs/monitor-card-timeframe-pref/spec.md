## ADDED Requirements

### Requirement: Monitor card shows a single strategy timeframe

The Monitor card (row and expanded) SHALL show one timeframe: the strategy's. It MUST NOT show a second price-TF label «Gráfico 1d» or «tf 1d». There is no inspected chart timeframe to save: the chart opened from Monitor has no selector, so the list and card MUST NOT store a looked-at TF.

#### Scenario: Expanded card has one TF

- **WHEN** the operator expands a 4h crypto strategy on `/monitor`
- **THEN** the card shows 4h
- **AND** MUST NOT show «Gráfico 1d»
- **AND** MUST NOT show «tf 1d»

#### Scenario: Last inspected chart TF is not saved

- **WHEN** the operator opens the chart of a 4h strategy from `/monitor`
- **THEN** the chart has no inspection timeframe to pick
- **AND** the list and card still show 4h
- **AND** the Monitor MUST NOT store a looked-at chart TF as the row's timeframe
