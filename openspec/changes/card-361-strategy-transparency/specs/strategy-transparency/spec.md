## MODIFIED Requirements

### Requirement: Safe functional transparency

The common authenticated trader SHALL receive a functional strategy manifest that exposes the behavior required to understand the decision while excluding technical secrets unrelated to that understanding.

#### Scenario: Authenticated trader receives manifest

- **WHEN** an authenticated trader requests a visible strategy used by Favoritos or Monitor
- **THEN** the response SHALL include the canonical display name, description, timeframe, direction, configured indicator periods and thresholds, indicator functions, participation in entry/exit/risk, effective parameters, and trader-readable entry/exit/risk explanations when they can be proven from the executed configuration
- **AND** the response SHALL set the strategy as unprotected for the authenticated functional view, even when the user is not an administrator

#### Scenario: Complex executed rule remains fully auditable

- **WHEN** an executed entry or exit rule contains more than eight conditions or uses candle-shape, rolling-window or shifted-price expressions
- **THEN** the authenticated manifest SHALL preserve every public condition, comparator, threshold and boolean grouping in trader-readable form
- **AND** SHALL NOT replace the rule with only a condition count or a generic `partial` summary

#### Scenario: Secrets and diagnostics remain excluded

- **WHEN** the authenticated functional manifest is serialized
- **THEN** it SHALL exclude source code, credentials, tokens, raw diagnostic columns, internal IDs, mutation controls, and private operational metadata
- **AND** unavailable configuration SHALL be represented explicitly instead of being replaced with a generic or invented rule

#### Scenario: Unauthenticated or public surface requests strategy data

- **WHEN** a request is not associated with an authenticated trader
- **THEN** the functional manifest SHALL not be exposed through the authenticated Favoritos/Monitor contract
- **AND** existing authentication and authorization controls SHALL remain unchanged

### Requirement: Public identity matches executed behavior

The public name, description and manifest MUST describe only indicators and logic present in the executed strategy, and each active strategy identity SHALL be distinguishable from its neighboring catalog entries.

#### Scenario: EMA RSI legacy key is resolved

- **WHEN** `ema_rsi_fibonacci` is visible and its execution contains EMA and RSI but no Fibonacci calculation
- **THEN** its public identity SHALL describe EMA + RSI
- **AND** SHALL NOT mention Fibonacci

#### Scenario: Similar chain strategies have distinct identities

- **WHEN** two active strategies share a family, asset and timeframe but differ in indicator, direction, guard, or exit configuration
- **THEN** their display names and descriptions SHALL state the differentiating behavior
- **AND** neither identity SHALL use a duplicated generic phrase as the sole distinction

#### Scenario: Direction follows executed configuration

- **WHEN** direction is present in the effective parameters or the selected template configuration
- **THEN** the manifest SHALL expose that exact `long` or `short` direction
- **AND** risk text and action semantics SHALL use the same direction

### Requirement: Strategy explanation catalog prevents drift

The repository SHALL test explanation and identity coverage for every active strategy template.

#### Scenario: Active template catalog changes

- **WHEN** a template is added or its configuration changes
- **THEN** tests SHALL fail if identity is generic or duplicated, metadata announces an unused indicator, configured indicators are missing, panel/participation metadata is absent, or public entry, exit and risk explanations cannot be resolved safely

#### Scenario: Runtime catalog grows beyond the previous versioned export

- **WHEN** PostgreSQL contains active templates not yet represented in the versioned template export
- **THEN** the versioned auditable inventory SHALL still cover those runtime strategy configurations
- **AND** tests SHALL exercise every inventory entry, including direction and complete rule status

### Requirement: Authenticated strategy identity is consistent across surfaces

Favoritos and Monitor SHALL consume the same canonical strategy transparency manifest for an equivalent strategy/timeframe and SHALL present the same identity, rules and effective technical configuration.

#### Scenario: Monitor and Favoritos show the same strategy

- **WHEN** an authenticated trader opens a strategy in Monitor and opens the corresponding favorite analysis
- **THEN** both surfaces SHALL show the same display name, description, direction, timeframe, indicator configuration, entry/exit rules and risk details
- **AND** neither surface SHALL replace those details with `Estratégia protegida`, `Protegido`, `Oculto` or a generic protected message

#### Scenario: Manifest details are unavailable

- **WHEN** either surface cannot prove the executed configuration or the requested series belongs to another timeframe
- **THEN** the surface SHALL show an explicit unavailable or timeframe-mismatch state
- **AND** SHALL not invent indicator values, parameters or rule text
