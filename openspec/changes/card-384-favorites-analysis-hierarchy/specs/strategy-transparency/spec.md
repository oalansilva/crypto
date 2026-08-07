## ADDED Requirements

### Requirement: Strategy transparency has coordinated visual ownership
Each full strategy analysis SHALL coordinate the canonical manifest between a concise rule overview, a chart legend for point-in-time evidence and one technical-detail disclosure. The page SHALL NOT render competing complete copies of indicators, effective parameters, participation, functions or availability messages.

#### Scenario: Canonical manifest contains indicators and parameters
- **WHEN** the full strategy analysis renders a canonical transparency manifest
- **THEN** the permanent overview SHALL summarize entry, exit and risk behavior without repeating parameter cards
- **AND** the chart legend SHALL identify plotted series and values for the selected or reference candle
- **AND** one technical-detail disclosure SHALL own indicator functions, participation, configuration and effective parameters.

#### Scenario: Same parameter supports more than one rule
- **WHEN** one effective parameter participates in entry, exit or risk in multiple places
- **THEN** the parameter SHALL be listed once in technical details
- **AND** the rule summaries MAY refer to its trader-readable meaning without restating a second parameter definition.

#### Scenario: Trader inspects a specific operation
- **WHEN** the trader activates the operation-decision disclosure
- **THEN** the disclosure SHALL present only the entry, exit or current-state evidence for that operation
- **AND** SHALL NOT repeat the permanent strategy-rule overview already presented above the chart.

### Requirement: Strategy transparency uses consistent trader-facing language
Visible labels and actions in the full analysis SHALL use consistent Portuguese terminology while preserving canonical technical names such as EMA and SMA where they are the recognized indicator identity.

#### Scenario: Full analysis renders mixed legacy labels
- **WHEN** legacy presentation labels such as `Winning Configuration`, `List of trades`, `Type`, or `Date and time` would otherwise be shown
- **THEN** the analysis SHALL render approved Portuguese equivalents
- **AND** technical acronyms and numeric values SHALL remain unchanged.

#### Scenario: Shared rule overview renders in Favorites or Monitor
- **WHEN** any trader-facing surface renders the shared permanent-rule overview
- **THEN** it SHALL use `Regras da estratégia` and `Condições usadas para entrada, saída e proteção da operação.`
- **AND** SHALL NOT render the legacy copy `Como funciona a estratégia` or `Estas regras não mudam com a posição atual do trade.`.

#### Scenario: Shared operation disclosure renders in Favorites or Monitor
- **WHEN** any trader-facing surface renders an operation-decision disclosure
- **THEN** its action SHALL be labeled `Ver decisão da operação`
- **AND** the expanded content SHALL contain event-specific evidence without another permanent-rule overview.
