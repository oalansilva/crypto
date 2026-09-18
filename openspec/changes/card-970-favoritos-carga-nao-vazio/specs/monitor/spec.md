## ADDED Requirements

### Requirement: Monitor does not treat favorites-list failure as empty catalog

`/monitor` SHALL show a load failure of the favorites-derived list as a load failure. The first paint after a failed load MUST NOT use «Nenhum ativo disponível no monitor». Layout, KPIs, and Monitor flow stay as they are; only this empty-vs-error treatment changes.

#### Scenario: Opportunities first fetch fails

- **WHEN** the operator opens `/monitor`
- **AND** the request that fills the board from favorites (`GET /opportunities/` on the live MonitorStatusTab) fails
- **THEN** the operator sees that the load failed
- **AND** MUST NOT see «Nenhum ativo disponível no monitor»

#### Scenario: Monitor catalog is truly empty after success

- **WHEN** that request succeeds
- **AND** there is no row to show
- **THEN** the existing empty catalog copy MAY appear
