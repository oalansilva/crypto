## MODIFIED Requirements

### Requirement: Monitor provides controls for In Portfolio and card mode
The UI MUST provide controls on the Monitor screen to:
- filter the list by In Portfolio vs All
- toggle per-card mode (Price vs Strategy)
- select per-card timeframe in Price mode

#### Scenario: Filter toggle exists
- **WHEN** the user opens Monitor
- **THEN** the UI provides a control to switch between In Portfolio and All

#### Scenario: Per-card toggle exists
- **WHEN** the user views a symbol card
- **THEN** the card provides a toggle control to switch between Price and Strategy modes

#### Scenario: Per-card timeframe selector exists
- **WHEN** the card is in Price mode
- **THEN** the card provides a timeframe selector with allowed options for the asset type

## REMOVED Requirements

### Requirement: Monitor includes tabs for Status and Dashboard
**Reason**: Monitor is unified into a single cards-based view; separate tabs are redundant.
**Migration**: Use the per-card Price/Strategy toggle and the single Monitor view.
