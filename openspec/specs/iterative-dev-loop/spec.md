# iterative-dev-loop Specification

## Purpose
TBD - created by archiving change iterative-dev-loop. Update Purpose after archive.
## Requirements
### Requirement: dev_adjusts_before_trader
**Description:** The system SHALL, after running a Dev backtest, automatically adjust the template and re-run the backtest when the result is not OK (e.g., zero trades or invalid metrics), before requesting Trader validation.

#### Scenario: Backtest invalid triggers adjustment
Given a Dev backtest result with holdout trades = 0 or metrics invalid
When the system evaluates the result
Then it adjusts the template and re-runs the backtest before invoking the Trader.

### Requirement: adjustment_limit
**Description:** The system MUST cap the number of Dev adjustment attempts per run to a configurable limit (default 3) to avoid infinite loops.

#### Scenario: Max attempts reached
Given repeated invalid backtest results
When the number of adjustments reaches the limit
Then the system stops adjusting and proceeds to Trader (or final rejection) with the latest result.

### Requirement: trace_adjustments
**Description:** The system SHALL record each Dev adjustment in the run trace with the changes applied and the attempt number.

#### Scenario: Adjustment trace recorded
Given the system applies an adjustment
When the adjustment completes
Then a trace event is appended containing the attempt number and summary of changes.

