## ADDED Requirements

### Requirement: Frontend preserves the permanent directional rule pair
The frontend strategy-transparency contract SHALL preserve the canonical entry and exit logic blocks together for every active strategy, independently of the current trade event or position.

#### Scenario: Long strategy rule pair is built
- **WHEN** a manifest is normalized and displayed for a `long` strategy
- **THEN** the permanent entry rule SHALL identify Compra and summarize the canonical entry condition
- **AND** the permanent exit rule SHALL identify Venda and summarize the canonical exit condition.

#### Scenario: Short strategy rule pair is built
- **WHEN** a manifest is normalized and displayed for a `short` strategy
- **THEN** the permanent entry rule SHALL identify Venda/Short and summarize the canonical entry condition
- **AND** the permanent exit rule SHALL identify Compra/Cobertura and summarize the canonical exit condition.

#### Scenario: Public rule pair cannot be translated safely
- **WHEN** either canonical logic block is absent or cannot be translated from allowlisted metadata
- **THEN** the contract SHALL mark the pair partial or unavailable
- **AND** SHALL NOT substitute current indicator values, raw expressions or invented conditions.

### Requirement: Existing active strategy catalog feeds the permanent rule pair
The UI SHALL derive its permanent rule overview from the canonical logic blocks already covered for every active strategy template.

#### Scenario: Active template changes
- **WHEN** an active template is added or its entry/exit logic changes
- **THEN** existing catalog coverage SHALL fail if public entry/exit summaries are absent
- **AND** frontend tests SHALL fail if those summaries cannot be preserved and displayed as a pair.
