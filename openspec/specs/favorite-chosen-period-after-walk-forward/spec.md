# favorite-chosen-period-after-walk-forward Specification

## Purpose
TBD - created by archiving change card-949-favorito-historico-inteiro. Update Purpose after archive.
## Requirements
### Requirement: New favorite after 70/30 stores the complete chosen period

When the operator promotes from Discovery or saves from Combo **after** a walk-forward 70/30 validation, the system SHALL persist the favorite on the **complete period chosen on screen**, not on the training window. Period «todo» SHALL mean first available candle → now. Period 6 months or 2 years SHALL mean those months/years in full and SHALL NOT expand to all-history. The Discovery Decide grid SHALL keep split 70/30 (ranking, coverage, Calmar, GO/NO-GO unchanged). Only new promote/save operations SHALL change; favorites already on the list with a training window SHALL stay until someone saves again.

#### Scenario: Promote after 70/30 with period todo uses full history

- **GIVEN** a Discovery candidate validated on 70/30 with period «todo» (training witness 17/08/2017 → 24/12/2023)
- **WHEN** the administrator confirms promotion
- **THEN** the created favorite's operational period is first candle → now (e.g. 17/08/2017 → 15/09/2026)
- **AND** the favorite SHALL NOT keep 17/08/2017 → 24/12/2023 as its period
- **AND** the Decide grid of that sweep still shows the training window, Calmar and GO/NO-GO

#### Scenario: Combo save after 70/30 with 2 years stays 2 years complete

- **GIVEN** a Combo run with walk-forward 70/30 and period 2 years
- **WHEN** the operator saves to Favorites
- **THEN** the favorite covers those 2 years complete (e.g. 15/09/2024 → 15/09/2026)
- **AND** it SHALL NOT use the training slice as the favorite period
- **AND** it SHALL NOT become all-history / first candle of the asset

#### Scenario: Existing favorite is not migrated

- **GIVEN** a favorite already on the list with training window 17/08/2017 → 24/12/2023
- **WHEN** this change ships
- **THEN** that row SHALL keep 17/08/2017 → 24/12/2023
- **AND** it SHALL change only if someone saves that strategy again

### Requirement: List, summary, chart and refresh of a new favorite show the complete period

For a favorite created by this card, `/favorites` list, analysis summary, chart and automatic/manual refresh SHALL display the numbers of the **complete chosen period**. The 70/30 training portrait SHALL remain on Discovery as search evidence and SHALL NOT be presented as the live favorite's performance. Combo without 70/30 SHALL keep its current save behavior.

#### Scenario: Favorites list of a new todo favorite is not the training window

- **WHEN** the operator opens `/favorites` after promoting the 70/30 «todo» candidate
- **THEN** the row period and metrics are the full history
- **AND** the list SHALL NOT show 17/08/2017 → 24/12/2023 as that new row's period
- **AND** the list SHALL NOT show the grid Calmar as if it were the full-period result

#### Scenario: Analysis of the new favorite is not the Discovery training summary

- **WHEN** the operator opens summary/chart of that new favorite from `/favorites`
- **THEN** window label and numbers are the complete period
- **AND** the UI SHALL NOT title the summary as the Discovery training window (17/08/2017 → 24/12/2023)

#### Scenario: Discovery grid unchanged when the operator has not saved

- **WHEN** the operator views Decide without promoting
- **THEN** ranking, coverage, Calmar and GO/NO-GO remain the 70/30 training values

