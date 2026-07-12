## ADDED Requirements

### Requirement: Universal visible indicator configuration
Every strategy chart SHALL display the functional configuration of every indicator declared by its canonical transparency manifest without requiring the trader to infer it from the strategy name.

#### Scenario: Strategy uses any supported indicators
- **WHEN** an authorized trader opens a strategy chart whose manifest declares one or more indicators
- **THEN** the chart header SHALL show a visible responsive summary of every indicator and its configured public parameters
- **AND** the detailed legend SHALL show type, configuration, semantic color and value for the selected/reference candle

#### Scenario: A new indicator type is added
- **WHEN** a future indicator is represented in the canonical manifest
- **THEN** the chart SHALL render its label and public parameters without strategy-specific UI code

#### Scenario: Configuration is unavailable
- **WHEN** no trustworthy indicator configuration exists in the manifest
- **THEN** the chart SHALL explicitly state that indicator configuration is unavailable
- **AND** SHALL NOT silently hide the section or invent values

### Requirement: Trader-readable risk and direction context
The chart SHALL expose public direction and risk parameters needed to interpret the displayed decision.

#### Scenario: Strategy has stop or direction configuration
- **WHEN** the manifest contains public stop, threshold or direction parameters
- **THEN** the chart SHALL present them using trader-readable labels and formatted values
