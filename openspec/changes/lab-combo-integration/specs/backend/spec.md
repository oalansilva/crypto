## MODIFIED Requirements

### Requirement: Auto Backtest Orchestration
**Description:** The system SHALL execute the Lab orchestration with a mandatory Combo parameter-optimization stage between seed-template selection and final trader validation.

#### Scenario: Lab run executes Combo before final validation
Given an upstream-approved Lab run with a valid seed template  
When the execution phase starts  
Then the system MUST call Combo optimization, apply the best parameters automatically, run the final backtest, and only then expose the run for Trader final validation

## ADDED Requirements

### Requirement: Persist Combo Optimization Result in Run
**Description:** The system SHALL persist the Combo optimization outcome in the Lab run payload so it can be consumed by API responses and UI without recomputation.

#### Scenario: Optimization data is stored for the run
Given Combo optimization completes for a Lab run  
When the run JSON is updated  
Then the system MUST store status, best parameters, best metrics, stages, limits snapshot, and applied timestamp under the run backtest payload

### Requirement: Combo Parameter-Only Scope
**Description:** The system MUST use Combo optimization only for parameter adjustment and SHALL NOT allow this stage to rewrite the base strategy structure.

#### Scenario: Base strategy logic is preserved
Given a seed template with indicators and entry/exit logic approved from upstream  
When Combo returns best parameters  
Then the system MUST keep indicator set and entry/exit logic unchanged and MUST apply only parameter values supported by the template

### Requirement: Combo Limit Parity with Existing Product
**Description:** The system SHALL enforce the same optimization limits and guardrails already defined by Combo in standalone flows.

#### Scenario: Lab optimization respects Combo limits
Given a Lab run that triggers Combo optimization  
When optimization ranges and execution budget are resolved  
Then the system MUST use the same Combo limits without expanding ranges, stages, or indicator constraints

### Requirement: Template Optimization Schema Compatibility
**Description:** Templates created in the Lab flow MUST use the same `optimization_schema` structure as Combo template `multi_ma_crossover`, making `correlated_groups` mandatory and requiring explicit `min/max/step` ranges.

#### Scenario: Created template follows multi_ma_crossover contract
Given a template created or normalized during Lab execution  
When the template optimization schema is persisted or sent to Combo optimization  
Then the schema MUST include `parameters` with `min`, `max`, and `step` for each optimizable parameter  
And the schema MUST include `correlated_groups` referencing only parameter keys defined in `parameters`

#### Scenario: Multi-MA example ranges
Given the Lab creates a multi_ma_crossover-style template  
When ranges are defined for optimization  
Then the schema MUST include values equivalent to:
- `sma_medium`: default 21, min 10, max 40, step 1
- `sma_long`: default 50, min 20, max 100, step 1
- `stop_loss`: default 0, min 0.005, max 0.13, step 0.002
- `ema_short`: default 9, min 3, max 20, step 1
