## ADDED Requirements

### Requirement: Expanded trade always shows buy and sell rules
The Monitor trade disclosure SHALL show the strategy's permanent buy and sell rules simultaneously, independently of the current position or event explanation.

#### Scenario: User expands an open trade
- **WHEN** the user expands a trade whose position remains open
- **THEN** the panel SHALL show “Quando compra” and “Quando vende” before the current-position explanation
- **AND** SHALL keep stop/risk context separate from the permanent exit rule.

#### Scenario: User expands a closed or out-of-position trade
- **WHEN** the user expands a closed trade or a strategy that is currently out of position
- **THEN** the panel SHALL show both permanent rules
- **AND** SHALL show the actual entry/exit event explanations separately when available.

#### Scenario: User expands a short trade
- **WHEN** the trade direction is `short`
- **THEN** the two permanent rule cards SHALL retain the headings “Quando compra” and “Quando vende”
- **AND** SHALL clarify that entry opens by selling (short) and exit closes by buying (cobertura)
- **AND** SHALL show the canonical condition summaries under those clarifications.

#### Scenario: Long strategy avoids tautological action copy
- **WHEN** the trade direction is `long`
- **THEN** the permanent rule cards SHALL show “Quando compra” and “Quando vende” with the condition summaries
- **AND** SHALL NOT show redundant lines such as “Compra para entrar” or “Venda para sair”.

#### Scenario: Legacy payload has no permanent rule pair
- **WHEN** the expanded trade does not include the new permanent rule contract
- **THEN** both rule cards SHALL remain visible with a safe unavailable message
- **AND** SHALL NOT infer rules from the current event.

### Requirement: Permanent rule overview remains accessible and responsive
The permanent rule overview SHALL preserve the existing disclosure's keyboard semantics and remain readable without horizontal page scrolling.

#### Scenario: Keyboard user expands the rule overview
- **WHEN** the user activates the disclosure using the keyboard
- **THEN** the labelled strategy overview SHALL appear in logical reading order before event details
- **AND** the disclosure SHALL preserve `aria-expanded`, `aria-controls` and visible focus.

#### Scenario: Mobile user reads both rules
- **WHEN** the viewport is narrower than 768px
- **THEN** the buy and sell rule cards SHALL stack within the available width
- **AND** SHALL NOT introduce a new table column or horizontal page overflow.
