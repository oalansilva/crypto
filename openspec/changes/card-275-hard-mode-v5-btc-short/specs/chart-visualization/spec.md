## MODIFIED Requirements

### Requirement: Pine Script exports for Short winners

Every TradingView Pine Script generated for card #275 winners MUST represent the saved Short strategy and preserve the required capital and sizing contract.

#### Scenario: Short Pine export is direction-correct

- **GIVEN** a validated card #275 winner
- **WHEN** its Pine Script is generated
- **THEN** the script includes `initial_capital=100`, `default_qty_type=strategy.percent_of_equity`, `default_qty_value=100`, `pyramiding=0`, and `strategy.entry(..., strategy.short)`
- **AND** exits close or cover 100% of the Short position
