## ADDED Requirements

### Requirement: Monitor explains every trade
The Monitor trades view SHALL provide an “Entenda este trade” explanation for every open or closed trade returned by the favorite analysis contract.

#### Scenario: User expands a closed trade explanation
- **WHEN** the user activates “Entenda este trade” for a closed trade
- **THEN** the UI SHALL show why the entry was confirmed and why the exit occurred
- **AND** SHALL show decision candle, execution time, prices and allowlisted historical evidence
- **AND** SHALL label the exit as strategy rule, stop or real objective as applicable.

#### Scenario: User expands an open trade explanation
- **WHEN** the user activates “Entenda este trade” for an open trade
- **THEN** the UI SHALL show why the entry was confirmed
- **AND** SHALL state why no exit is confirmed
- **AND** SHALL present pending strategy-exit and stop conditions separately.

#### Scenario: Legacy trade has no trustworthy evidence
- **WHEN** an explanation is unavailable for a trade
- **THEN** the UI SHALL state that decision details are unavailable for that historical trade
- **AND** SHALL NOT generate an explanation from current values.

### Requirement: Monitor trade explanation is accessible and responsive
The Monitor SHALL expose trade explanations through a keyboard-operable disclosure that remains readable on desktop and mobile.

#### Scenario: Keyboard user opens explanation
- **WHEN** focus is on the “Entenda este trade” control and the user activates it
- **THEN** the control SHALL expose `aria-expanded` and `aria-controls`
- **AND** the labelled explanation panel SHALL become available in logical reading order
- **AND** focus SHALL remain visibly indicated.

#### Scenario: Mobile user opens explanation
- **WHEN** the viewport is narrower than 768px
- **THEN** the explanation SHALL use stacked content without horizontal page scrolling
- **AND** interactive targets SHALL provide at least a 44px effective target.

### Requirement: Monitor names the measured next trigger
The Monitor SHALL identify what each displayed distance measures instead of using an ambiguous generic “distance to exit” label.

#### Scenario: Strategy exit proximity is displayed
- **WHEN** the distance represents a technical exit rule
- **THEN** the UI SHALL label it as proximity to the strategy exit rule.

#### Scenario: Stop or objective distance is displayed
- **WHEN** a stop or supported objective distance is displayed
- **THEN** the UI SHALL label the specific stop or objective independently
- **AND** SHALL NOT present those distances as the same trigger.
