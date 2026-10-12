## ADDED Requirements

### Requirement: Montar shows 4h 1h 15m and 1d timeframes

The Discovery Montar surface SHALL offer swing timeframe checkboxes for `15m`, `1h`, `4h` and `1d` on `/combo/discovery`. The heading SHALL say that templates are compared in 4h, 1h, 15m and 1d. The empty-axis impediment SHALL name those four values. Default selection on a new draft SHALL remain `1d` only. The surface SHALL NOT show 1m, 5m or 30m. The surface SHALL NOT show a daily-trend filter. The surface SHALL NOT show a field to change slippage.

#### Scenario: Operator sees four swing timeframes

- **WHEN** the operator opens Montar on a new draft
- **THEN** the Timeframes swing axis shows 15 minutos, 1 hora, 4 horas and 1 dia
- **AND** 1 dia is selected
- **AND** 1m, 5m and 30m are absent

#### Scenario: Heading names the four intervals

- **WHEN** the operator reads the page heading
- **THEN** the copy names 4h, 1h, 15m and 1d
- **AND** it does not promise a 1D trend filter

#### Scenario: Read-only cost, no slippage field

- **WHEN** the operator looks at Preflight or the draft
- **THEN** there is no control to edit slippage
- **AND** any cost note is read-only (taxa 0,075% and slippage of the timeframe)

### Requirement: Decidir filter and rows include 1h and 15m

The leaderboard timeframe filter SHALL include `1h` and `15m` in addition to `4h` and `1d`. Ranked rows MAY show those timeframes. Selo GO/NO-GO, Promover à mão and the Discovery placar SHALL remain the same rule as today.

#### Scenario: Filter lists 1h and 15m

- **WHEN** the operator opens the timeframe filter after a sweep that included 1h and 15m
- **THEN** the filter options include 1h and 15m as well as 4h and 1d
