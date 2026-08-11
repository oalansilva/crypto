## MODIFIED Requirements

### Requirement: Simplified Hold Status Display
The system SHALL display Monitor decisions as binary public states: Compra/Hold or Venda/Exit. `HOLD` MUST require an active entry confirmation from strategy signal history or an explicit buy state. All non-hold strategy states, including neutral, wait, near-entry, exited, stopped, missed, unknown, stale, or uncertain states, MUST remain visible as Venda/Exit when the strategy is starred.

#### Scenario: Opportunity in HOLD state
- **WHEN** the strategy has a confirmed active entry
- **AND** no later exit invalidates that entry
- **THEN** the UI displays it as Compra/Hold

#### Scenario: Starred non-hold strategy
- **WHEN** the strategy is starred
- **AND** the strategy has no active HOLD state
- **THEN** the main Monitor board displays the strategy as Venda/Exit
- **AND** the UI does not display `WAIT` or `Espera`

### Requirement: Simplified Opportunity Monitor Dashboard
The system SHALL provide a dashboard at `/monitor` showing starred favorite strategies. Each visible row/card shows symbol, strategy name, binary decision state (Compra/Hold or Venda/Exit), distance/risk data when available, and current price.

#### Scenario: Existing crypto favorites are unaffected
- **WHEN** the user opens `/monitor` and has multiple starred strategies for `BTC/USDT`
- **THEN** the dashboard lists each starred strategy row independently
- **AND** no row is hidden because another strategy uses the same symbol
- **AND** no row is hidden because its raw status is `WAIT`, `NEUTRAL`, or `BUY_NEAR`
