## MODIFIED Requirements

### Requirement: Auto Backtest Orchestration
**Description:** The system SHALL execute the Lab orchestration with a mandatory Combo parameter-optimization stage between seed-template selection and final trader validation.

#### Scenario: Lab run executes Combo before final validation
- **GIVEN** an upstream-approved Lab run with a valid seed template
- **WHEN** the execution phase starts
- **THEN** the system MUST call Combo optimization and apply the best parameters automatically
- **AND** the system MUST run the final backtest before exposing the run for Trader final validation

## ADDED Requirements

### Requirement: Persist Combo Optimization Result in Run
**Description:** The system SHALL persist the Combo optimization outcome in the Lab run payload so it can be consumed by API responses and UI without recomputation.

#### Scenario: Optimization data is stored for the run
- **GIVEN** Combo optimization completes for a Lab run
- **WHEN** the run JSON is updated
- **THEN** the system MUST store status, best parameters, best metrics, and stages under the run backtest payload
- **AND** the system MUST store limits snapshot and applied timestamp under the run backtest payload

### Requirement: Combo Parameter-Only Scope
**Description:** The system MUST use Combo optimization only for parameter adjustment and SHALL NOT allow this stage to rewrite the base strategy structure.

#### Scenario: Base strategy logic is preserved
- **GIVEN** a seed template with indicators and entry/exit logic approved from upstream
- **WHEN** Combo returns best parameters
- **THEN** the system MUST keep indicator set and entry/exit logic unchanged
- **AND** the system MUST apply only parameter values supported by the template

### Requirement: Combo Limit Parity with Existing Product
**Description:** The system SHALL enforce the same optimization limits and guardrails already defined by Combo in standalone flows.

#### Scenario: Lab optimization respects Combo limits
- **GIVEN** a Lab run that triggers Combo optimization
- **WHEN** optimization ranges and execution budget are resolved
- **THEN** the system MUST use the same Combo limits
- **AND** the system MUST NOT expand ranges, stages, or indicator constraints

### Requirement: Template Optimization Schema Compatibility
**Description:** Templates created in the Lab flow MUST use the same `optimization_schema` structure as Combo template `multi_ma_crossover`, making `correlated_groups` mandatory and requiring explicit `min/max/step` ranges.

#### Scenario: Created template follows multi_ma_crossover contract
- **GIVEN** a template created or normalized during Lab execution
- **WHEN** the template optimization schema is persisted or sent to Combo optimization
- **THEN** the schema MUST include `parameters` with `min`, `max`, and `step` for each optimizable parameter
- **AND** the schema MUST include `correlated_groups` referencing only parameter keys defined in `parameters`

#### Scenario: Multi-MA example ranges
- **GIVEN** the Lab creates a multi_ma_crossover-style template
- **WHEN** ranges are defined for optimization
- **THEN** the schema MUST include values equivalent to `sma_medium` (default 21, min 10, max 40, step 1)
- **AND** the schema MUST include values equivalent to `sma_long` (default 50, min 20, max 100, step 1)
- **AND** the schema MUST include values equivalent to `stop_loss` (default 0, min 0.005, max 0.13, step 0.002)
- **AND** the schema MUST include values equivalent to `ema_short` (default 9, min 3, max 20, step 1)
