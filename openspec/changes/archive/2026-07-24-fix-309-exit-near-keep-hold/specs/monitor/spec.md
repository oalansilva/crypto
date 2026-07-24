## ADDED Requirements

### Requirement: Public binary status keeps EXIT_NEAR as HOLD while in position
The opportunities public contract (`status` HOLD|EXIT and `is_holding`) SHALL treat internal `EXIT_NEAR` as still in position when `is_holding` is true. Public `EXIT` MUST NOT be emitted solely because exit proximity is near.

#### Scenario: Active long position with exit near
- **WHEN** position resolution yields `is_holding=true`
- **AND** exit proximity analysis sets internal status `EXIT_NEAR`
- **THEN** the public opportunity payload MUST use `status=HOLD` and `is_holding=true`
- **AND** the Monitor/chart public badge for a long strategy MUST resolve to `Compra`
- **AND** the public message MUST NOT claim the position is already closed or “fora de posição”

#### Scenario: Confirmed exit signal remains EXIT
- **WHEN** internal status is `EXIT_SIGNAL`, `EXITED`, `EXIT`, or stop-out equivalents
- **THEN** the public payload MUST use `status=EXIT`
- **AND** `is_holding` MUST be false for the public contract
