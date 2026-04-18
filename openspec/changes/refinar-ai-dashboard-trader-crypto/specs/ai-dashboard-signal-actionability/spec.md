## ADDED Requirements

### Requirement: Unified signals must expose minimum actionability with explicit fallback
The system SHALL return an `actionability` object for every unified signal so the client can distinguish actionable setups from informational-only signals even when only partial trading context exists.

#### Scenario: Minimum actionability is populated from available source data
- **WHEN** the unified signal includes source data with enough trading context to distinguish an actionable setup from a contextual signal
- **THEN** the response MUST populate the minimum `actionability` fields required for that asset

#### Scenario: Actionability degrades explicitly when data is missing
- **WHEN** the unified signal does not have enough source data to produce a safe operational view
- **THEN** the response MUST keep the `actionability` object present and mark unavailable fields as null with an `unavailable_reason`

#### Scenario: UI shows minimum execution context for actionable signals
- **WHEN** a unified signal has minimum populated `actionability` fields
- **THEN** the dashboard MUST show a trader-facing actionable summary without fabricating unsupported execution levels

#### Scenario: UI shows informative fallback for non-actionable signals
- **WHEN** a unified signal has an `actionability.unavailable_reason`
- **THEN** the dashboard MUST communicate that the signal is informational and MUST NOT display synthetic entry, stop or target values

### Requirement: Detailed actionability must only appear when supported and remain backward compatible
The system SHALL expose detailed operational fields only when backed by source data and the dashboard SHALL remain compatible with partial or legacy payloads.

#### Scenario: Detailed actionability fields are populated only with explicit backing
- **WHEN** the unified signal includes source data with explicit `timeframe`, `entry_zone`, `invalidation_level`, `target_level` or `risk_label`
- **THEN** the response MUST populate only the detailed `actionability` fields that are supported for that asset

#### Scenario: UI shows detailed execution context without fabrication
- **WHEN** a unified signal has populated detailed `actionability` fields
- **THEN** the dashboard MUST show trader-facing execution context, including `timeframe`, `entry_zone`, `invalidation_level`, `target_level` or `risk_label`, without inventing missing values

#### Scenario: Dashboard remains compatible with partial or legacy payloads
- **WHEN** the dashboard receives a payload missing some or all of the newer `actionability` fields
- **THEN** the UI MUST preserve a safe contextual rendering path and MUST NOT break or fabricate missing values
