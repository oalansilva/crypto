# monitor-common-user-table-columns Specification

## Purpose
TBD - created by archiving change monitor-common-user-table-columns. Update Purpose after archive.
## Requirements
### Requirement: Common user Monitor table hides technical columns
The Monitor SHALL hide the `Distância` and `7d` table columns from common users.

#### Scenario: Common user opens Monitor table
- **WHEN** a common user opens the Monitor
- **THEN** the table header does not include `Distância`
- **AND** the table header does not include `7d`

### Requirement: Common user Monitor table uses clear final status label
The Monitor SHALL label the final signal-state column as `Status` instead of `Saída`.

#### Scenario: Common user reads signal state column
- **WHEN** a common user opens the Monitor
- **THEN** the table header includes `Status` for the final signal-state column
- **AND** the table header does not include `Saída`

