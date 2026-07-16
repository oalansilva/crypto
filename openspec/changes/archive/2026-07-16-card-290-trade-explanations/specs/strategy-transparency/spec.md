## ADDED Requirements

### Requirement: Every active strategy explains entry exit and risk
The canonical strategy transparency manifest SHALL provide trader-readable and strategy-specific explanations of entry, exit and risk for every active strategy without exposing source code or raw internal expressions.

#### Scenario: Active strategy manifest is built
- **WHEN** an active strategy is serialized from its executed template and effective parameters
- **THEN** its manifest SHALL contain non-empty public rule summaries for entry and exit
- **AND** SHALL describe configured stop/risk behavior when it exists
- **AND** SHALL preserve the meaningful all/any/sequence structure of the executed rule.

#### Scenario: Rule cannot be translated safely
- **WHEN** part of an executed rule cannot be represented from allowlisted public metadata
- **THEN** the manifest SHALL mark that explanation partial or unavailable
- **AND** SHALL NOT invent a condition or expose raw diagnostic/source content.

### Requirement: Trade explanations use event-time evidence
The system SHALL explain each trade from the strategy configuration and historical values tied to that trade event.

#### Scenario: Closed trade has trustworthy context
- **WHEN** a closed trade has entry and exit timestamps compatible with the manifest series
- **THEN** the response SHALL include entry and exit explanations with public action, trigger, decision candle, execution time, execution price and historical evidence
- **AND** the exit trigger SHALL distinguish strategy rule, stop loss and real take profit when supported.

#### Scenario: Open trade has trustworthy context
- **WHEN** a trade has a confirmed entry and no confirmed exit
- **THEN** the response SHALL explain the entry
- **AND** SHALL state that the position remains open
- **AND** SHALL describe the configured exit and stop conditions without claiming they were met.

#### Scenario: Historical context is missing
- **WHEN** the event cannot be aligned to trustworthy historical series and configuration
- **THEN** the explanation SHALL be unavailable with a public reason
- **AND** SHALL NOT substitute current indicator values for historical evidence.

### Requirement: Trade explanations are direction aware
Every trade explanation SHALL use actions and risk semantics that match the executed strategy direction.

#### Scenario: Long trade is explained
- **WHEN** direction is `long`
- **THEN** entry SHALL use Compra and exit SHALL use Venda
- **AND** stop SHALL be described below the entry when applicable.

#### Scenario: Short trade is explained
- **WHEN** direction is `short`
- **THEN** entry SHALL use Venda/Short and exit SHALL use Compra/Cobertura
- **AND** stop SHALL be described above the entry when applicable.

### Requirement: Strategy explanation catalog prevents drift
The repository SHALL test explanation coverage for every active strategy template.

#### Scenario: Active strategy catalog changes
- **WHEN** a strategy is added or its executable entry/exit configuration changes
- **THEN** automated coverage SHALL fail if public entry, exit, risk participation or event evidence cannot be resolved safely.
