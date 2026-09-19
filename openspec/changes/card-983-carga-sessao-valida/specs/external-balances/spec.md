## ADDED Requirements

### Requirement: Wallet does not show a false balances error during renewal

On `/external/balances`, during access renewal, the page SHALL show the balances when the snapshot is available. The screen MUST NOT show «Erro ao carregar» / «Falha ao carregar saldos» in that window. A real network failure or invalid response on this screen continues that error. This card SHALL NOT redesign the wallet grid, filters, or credentials form. Exchange-credential failure in the same window stays out of scope.

#### Scenario: Renewal window shows balances

- **WHEN** the operator opens `/external/balances`
- **AND** access is being renewed
- **AND** a balances payload arrived or will arrive successfully
- **THEN** the operator sees the balances
- **AND** MUST NOT see «Erro ao carregar»
- **AND** MUST NOT see «Falha ao carregar saldos»

#### Scenario: Real wallet failure keeps the existing error copy

- **WHEN** the balances request fails by real network error or invalid response
- **AND** the session is not dead
- **THEN** the operator sees «Erro ao carregar»
- **AND** MAY see «Falha ao carregar saldos» as the detail
- **AND** remains on `/external/balances`
