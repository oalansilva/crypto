## ADDED Requirements

### Requirement: Supported chart surfaces expose explicit zoom controls
Chart surfaces covered by this change SHALL provide explicit zoom-in and zoom-out controls in addition to gesture-based scaling.

#### Scenario: Explicit controls complement existing scaling
- **WHEN** a supported chart surface already allows mouse wheel or trackpad scaling
- **THEN** the UI also provides explicit zoom-in and zoom-out controls

#### Scenario: Explicit controls do not require new data fetch
- **WHEN** the user zooms the chart with explicit controls
- **THEN** the chart updates its visible range without requiring a new candle request by default

### Requirement: Explicit zoom keeps synchronized panels aligned
When a chart surface uses more than one synchronized panel, the system MUST keep the panels aligned after zoom actions.

#### Scenario: Price and RSI panels stay synchronized
- **WHEN** the user zooms a chart that has a main price panel and an RSI panel
- **THEN** both panels keep the same visible time range after the zoom action

#### Scenario: Crosshair context remains coherent after zoom
- **WHEN** the user moves the cursor after a zoom action
- **THEN** tooltip and crosshair data continue to map to the currently visible candle positions
