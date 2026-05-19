## ADDED Requirements

### Requirement: Monitor separates chart and trades actions
The Monitor UI SHALL expose two explicit Portuguese actions for each visible strategy opportunity: `Abrir Grafico` for chart-only inspection and `Ver Trades` for trade analysis.

#### Scenario: User opens chart-only view
- **WHEN** the user selects `Abrir Grafico` from a Monitor strategy
- **THEN** the system SHALL open the strategy chart
- **AND** the modal SHALL NOT render the strategy summary panel
- **AND** the modal SHALL NOT render the trades list

#### Scenario: User opens trades view
- **WHEN** the user selects `Ver Trades` from a Monitor strategy
- **THEN** the system SHALL open the strategy analysis view
- **AND** the modal SHALL render the strategy summary/context panel
- **AND** the modal SHALL render the trades list and trade metrics when available
