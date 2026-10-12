## ADDED Requirements

### Requirement: Shared period list on Discovery and Combo

The period control on `/combo/discovery` (Montar) and `/combo/configure` SHALL offer the same options, in this order, with these labels: `15 dias`, `1 mês`, `3 meses`, `6 meses`, `1 ano`, `2 anos`, `Personalizado`, `Todo o histórico`. The control SHALL NOT be limited to the previous three options (`Todo o histórico`, `Últimos 2 anos`, `Últimos 6 meses`). Fixed options (15 dias through 2 anos) SHALL mean a «últimos X» window counted from today, in the same spirit as the current 6 months and 2 years. Exact calendar dates SHALL be chosen only under `Personalizado`.

#### Scenario: Discovery shows the shared list

- **WHEN** the operator opens the period control on `/combo/discovery`
- **THEN** the options are 15 dias, 1 mês, 3 meses, 6 meses, 1 ano, 2 anos, Personalizado, Todo o histórico
- **AND** the previous three-option-only list is gone

#### Scenario: Combo shows the same list

- **WHEN** the operator opens the period control on `/combo/configure`
- **THEN** the options are the same list, in the same order, with the same labels
- **AND** Combo no longer offers only Últimos 6 meses, Últimos 2 anos and Todo o período

### Requirement: Custom range uses Data Inicial and Data Final

When the operator selects `Personalizado`, the surface SHALL show Data Inicial and Data Final. Preflight and the sweep SHALL evaluate combinations in that interval. Custom without both dates, or with Data Inicial after Data Final, SHALL NOT start; Preflight SHALL name what is missing. Data Final after today SHALL be blocked by Preflight.

#### Scenario: Custom with both dates in order

- **WHEN** the operator selects Personalizado and fills Data Inicial and Data Final with Inicial on or before Final and Final on or before today
- **THEN** Preflight and the sweep use that interval
- **AND** start is not blocked by the period control

#### Scenario: Custom missing dates names the gap

- **WHEN** Personalizado is selected and one or both dates are empty
- **THEN** start is disabled
- **AND** Preflight names the missing date(s)

#### Scenario: Custom inverted range is blocked

- **WHEN** Personalizado is selected and Data Inicial is after Data Final
- **THEN** start is disabled
- **AND** Preflight says Data Inicial cannot be after Data Final

#### Scenario: Custom end after today is blocked

- **WHEN** Personalizado is selected and Data Final is after today
- **THEN** start is disabled
- **AND** Preflight says Data Final cannot be after today

### Requirement: Chosen period is the evaluation window

Given a period chosen on the draft, when the operator runs Preflight or starts the sweep, the combinations SHALL be evaluated in that window, not in one of the three former options by default. Preflight and the draft SHALL show the chosen period (label plus date window when there is one). Todo o histórico SHALL remain in the list and SHALL keep using the available history of the chosen symbols.

#### Scenario: Draft period drives Preflight and start

- **WHEN** the operator chooses a period on the draft and runs Preflight or starts the sweep
- **THEN** combinations are evaluated in that window
- **AND** the run does not silently fall back to Todo o histórico, Últimos 2 anos or Últimos 6 meses

#### Scenario: Preflight shows label and window

- **WHEN** a fixed period or a valid custom range is selected
- **THEN** Preflight and the draft show the option label
- **AND** they show the date window when dates exist

#### Scenario: Full history still uses available candles

- **WHEN** the operator selects Todo o histórico
- **THEN** Preflight and the sweep use the available history of the chosen symbols
