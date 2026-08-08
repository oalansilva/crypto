# strategy-transparency Specification

## Purpose
TBD - created by archiving change card-278-strategy-transparency. Update Purpose after archive.
## Requirements
### Requirement: Canonical strategy transparency manifest
The system SHALL derive one public strategy transparency manifest from the configuration and logic actually used by execution.

#### Scenario: Active strategy resolves a specific manifest
- **WHEN** an active visible strategy is serialized
- **THEN** its manifest SHALL contain a unique PT-BR display name and description
- **AND** SHALL contain the indicators used, effective public parameters, function, panel, scale and participation in entry, exit or risk
- **AND** SHALL NOT contain IDs, dates, `WINNER`, `chain`, versions or generic fallback identity.

#### Scenario: Configuration cannot be proven
- **WHEN** the system cannot resolve the executed configuration for a strategy
- **THEN** it SHALL return an explicit unavailable state
- **AND** SHALL NOT invent a manifest, indicator or generic public identity.

### Requirement: Public identity matches executed behavior
The public name, description and manifest MUST describe only indicators and logic present in the executed strategy.

#### Scenario: EMA RSI legacy key is resolved
- **WHEN** `ema_rsi_fibonacci` is visible and its execution contains EMA and RSI but no Fibonacci calculation
- **THEN** its public identity SHALL describe EMA + RSI
- **AND** SHALL NOT mention Fibonacci.

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

### Requirement: Timestamped indicator series
The system SHALL expose only indicator series actually produced by the strategy as timestamped points.

#### Scenario: Series is available
- **WHEN** execution produces an indicator series
- **THEN** every public point SHALL include `timestamp_utc` and a finite value
- **AND** series SHALL be joined to candles by timestamp rather than array position.

#### Scenario: Legacy series lacks trustworthy timestamps
- **WHEN** an indicator array cannot be tied to source timestamps
- **THEN** the API SHALL mark that indicator series unavailable
- **AND** SHALL NOT align it to candle positions by index.

### Requirement: Indicator aliases and diagnostics are filtered
The public manifest and series SHALL contain one canonical entry for each used indicator and SHALL exclude diagnostic-only columns.

#### Scenario: Execution returns aliases and helper columns
- **WHEN** multiple output columns represent one configured indicator or internal calculation helpers
- **THEN** the public response SHALL select the declared canonical series
- **AND** SHALL omit duplicate aliases and diagnostic helpers.

### Requirement: Non-plottable strategy logic remains understandable
The manifest SHALL describe non-plottable conditions in trader language.

#### Scenario: Strategy uses candle pattern or previous-high breakout
- **WHEN** a rule cannot be represented as a continuous indicator series
- **THEN** the manifest SHALL include it in an explanatory logic block
- **AND** SHALL identify whether it participates in entry, exit or risk.

### Requirement: Strategy transparency drift is tested
The repository SHALL maintain an auditable matrix and automated coverage for every active template/strategy.

#### Scenario: Active template catalog changes
- **WHEN** a template is added or its configuration changes
- **THEN** tests SHALL fail if identity is generic, metadata announces an unused indicator, configured indicators are missing, or panel/participation metadata is absent.

### Requirement: Public series and candles share one temporal cutoff
When current OHLCV is available, the backend SHALL derive public indicator points and returned candles from the same ordered timestamp snapshot.

#### Scenario: Current history extends beyond a saved analysis
- **WHEN** canonical OHLCV contains candles newer than the favorite's saved analysis arrays
- **THEN** the backend SHALL calculate the declared indicators over the current snapshot
- **AND** SHALL return each available series through the last candle timestamp after its normal warm-up
- **AND** SHALL NOT change saved trades, metrics or effective parameters.

#### Scenario: Public payload is redacted
- **WHEN** the current manifest is returned to a common trader
- **THEN** only allowlisted timestamped series SHALL be included
- **AND** raw calculation columns and diagnostic arrays SHALL remain excluded.

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

### Requirement: Frontend preserves the permanent directional rule pair
The frontend strategy-transparency contract SHALL preserve the canonical entry and exit logic blocks together for every active strategy, independently of the current trade event or position.

#### Scenario: Long strategy rule pair is built
- **WHEN** a manifest is normalized and displayed for a `long` strategy
- **THEN** the permanent entry rule SHALL identify Compra via the heading “Quando compra” and summarize the canonical entry condition
- **AND** the permanent exit rule SHALL identify Venda via the heading “Quando vende” and summarize the canonical exit condition
- **AND** SHALL NOT repeat tautological action lines such as “Compra para entrar” or “Venda para sair”.

#### Scenario: Short strategy rule pair is built
- **WHEN** a manifest is normalized and displayed for a `short` strategy
- **THEN** the permanent entry rule SHALL keep the heading “Quando compra” and clarify that entry opens by selling (short)
- **AND** the permanent exit rule SHALL keep the heading “Quando vende” and clarify that exit closes by buying (cobertura)
- **AND** each rule SHALL summarize the canonical entry or exit condition.

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

#### Scenario: Timestamped indicator series is available
- **WHEN** the timestamped series is available for the active timeframe
- **THEN** the chart and technical detail SHALL expose the available evidence without rendering `Série disponível para o timeframe atual.`
- **AND** explicit series-status copy SHALL be limited to unavailable, absent, or incompatible states.

#### Scenario: Trader inspects the operation list
- **WHEN** the trader reviews open or closed operations
- **THEN** the list SHALL present the operation facts without an additional decision disclosure or nested explanation
- **AND** SHALL rely on the permanent strategy-rule overview and chart evidence already presented in the analysis.

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

#### Scenario: Shared operation list renders in Favorites or Monitor
- **WHEN** any trader-facing surface renders the shared operation list
- **THEN** it SHALL NOT render `Ver decisão da operação` or any per-operation explanation disclosure
- **AND** SHALL preserve the visible dates, prices, signals, results and open-position state.
