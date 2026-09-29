## MODIFIED Requirements

### Requirement: Target and stop are recalibrated from the ruler; the waiting window follows the applied prazo

`EXIT_TARGET_BP`, `EXIT_STOP_BP` and `HOLD_AFTER_FILL_S` SHALL be taken from the consumed version when the offline backtest has promoted that set with net return per trade whose 95% interval lower bound is above zero. The 15-minute waiting window of the 23/09 grid SHALL remain the geometry in use until that promotion. Changing the 15 minutes SHALL be the explicit apply of this card, never an implicit side effect of a report that did not promote. When the report is missing or the interval is not above zero the current target, stop and prazo SHALL stay.

#### Scenario: Geometry follows a paying backtest version

- **WHEN** the consumed version records target, stop and prazo after a backtest with interval above zero
- **THEN** `EXIT_TARGET_BP`, `EXIT_STOP_BP` and `HOLD_AFTER_FILL_S` SHALL be those values
- **AND** the delivery evidence SHALL show the net return and the interval the choice is based on

#### Scenario: No geometry change without a paying report

- **WHEN** the backtest is missing or the 95% interval lower bound is not above zero
- **THEN** the geometry in use SHALL stay unchanged
- **AND** the waiting window SHALL stay at the in-use prazo
- **AND** the reason SHALL be recorded

#### Scenario: Fifteen minutes is no longer an unchangeable ceiling

- **WHEN** the backtest shows net profit only on a prazo longer than 15 minutes
- **THEN** that longer prazo SHALL be writable on the promoted version
- **AND** the change SHALL be the apply of this card, not a silent env edit
