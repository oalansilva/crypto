## ADDED Requirements

### Requirement: Favorites analysis has one decision-first reading hierarchy
The full analysis opened from Favorites SHALL present information in the order identity and decision summary, permanent strategy rules, chart evidence, technical configuration, signal history when applicable, and trades. Summary content SHALL prioritize symbol, strategy name, timeframe, direction, return, win rate, drawdown and trade count without repeating the full effective configuration.

#### Scenario: Trader opens a complete favorite analysis
- **WHEN** an authorized trader opens full analysis from Favorites
- **THEN** the first viewport SHALL identify the strategy and expose its primary performance and risk context
- **AND** permanent entry and exit rules SHALL appear before the detailed technical configuration
- **AND** the chart SHALL remain the primary evidence surface.

#### Scenario: Analysis has a long strategy description
- **WHEN** the public strategy description exceeds the available width on desktop or mobile
- **THEN** the analysis SHALL wrap the complete description without clipping or horizontal scrolling
- **AND** SHALL preserve the strategy identity and summary hierarchy.

### Requirement: Favorites analysis uses progressive disclosure for technical detail
The full analysis SHALL keep the technical configuration available through an explicit accessible disclosure while keeping the essential decision context visible by default. Indicator definitions, effective parameters and unavailability explanations SHALL NOT be repeated in multiple page sections.

#### Scenario: Trader needs technical configuration
- **WHEN** the trader activates the technical-details disclosure
- **THEN** the analysis SHALL expose every public indicator and effective parameter available in the canonical manifest
- **AND** each indicator or parameter SHALL appear once within the analysis presentation outside the chart legend's point-in-time values.

#### Scenario: Technical evidence is unavailable
- **WHEN** an indicator series or effective configuration cannot be proven
- **THEN** the analysis SHALL present one explicit unavailable explanation in the relevant technical-detail context
- **AND** SHALL keep the chart, summary, rules and trades usable.

### Requirement: Favorites analysis remains usable across responsive layouts
The analysis SHALL preserve its information hierarchy, actions and complete readable content on desktop and mobile without requiring horizontal page scrolling.

#### Scenario: Trader opens analysis on mobile
- **WHEN** the viewport width is below 768 pixels
- **THEN** summary metrics and strategy rules SHALL reflow into a linear, scannable composition
- **AND** chart controls and technical disclosure SHALL remain keyboard and touch accessible
- **AND** labels, descriptions and values SHALL not be clipped.
