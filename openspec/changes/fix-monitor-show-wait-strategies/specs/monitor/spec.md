## MODIFIED Requirements

### Requirement: Common-user Monitor follows Favorites star tiers
The Monitor page MUST show strategies marked with 1, 2, or 3 stars by default. The Monitor UI MUST classify visible strategy decisions only as Compra/Hold or Venda/Exit; it MUST NOT expose or hide starred strategies through a WAIT/Espera state.

#### Scenario: Common user opens Monitor
- **WHEN** a non-admin user opens `/monitor`
- **THEN** the Monitor request MUST ask the backend for `tier=1,2,3`
- **AND** visible opportunities MUST exclude unstarred strategies (`tier=null`)
- **AND** opportunities with `tier=1`, `tier=2`, or `tier=3` MUST remain visible as either Compra/Hold or Venda/Exit
- **AND** the UI MUST NOT require the strategy to be in portfolio or in local Monitor favorites to appear
- **AND** the UI MUST NOT expose a Monitor-local favorite action, filter, or count

### Requirement: Monitor chart current marker matches active position state
The Monitor chart modal MUST represent an active `HOLD` opportunity as an open long position, not as an executed exit/sell marker. Non-hold opportunities MUST resolve to Venda/Exit in the public Monitor UI instead of a visible or hidden `WAIT` decision.

#### Scenario: Non-hold opportunity exists
- **WHEN** a Monitor opportunity is not an active `HOLD`
- **THEN** the main Monitor board MUST display it as Venda/Exit
- **AND** the Monitor UI MUST NOT show `WAIT` or `Espera`

### Requirement: Monitor public signal language uses Compra and Venda
The Monitor SHALL present public decision labels only as `Compra` and `Venda`. Internal raw statuses MAY remain unchanged for classification, API compatibility, logs, and tests.

#### Scenario: User views Monitor summary and sections
- **WHEN** the user opens `/monitor`
- **THEN** the visible summary tags and actionable section headers SHALL use `Compra` for active buy/position state
- **AND** the visible summary tags and actionable section headers SHALL use `Venda` for sell/non-hold state
- **AND** the user SHALL NOT see `HOLD`, `EXIT`, `WAIT`, or `Espera` as primary Monitor decision labels.
