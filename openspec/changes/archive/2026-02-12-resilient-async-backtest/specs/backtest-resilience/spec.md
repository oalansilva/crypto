# Capability: Resilient Async Backtest (Dev Stage)

## ADDED Requirements

### Requirement: Async backtest job in Dev stage
**Description:** The Dev stage MUST trigger backtest execution asynchronously and return control without blocking the main flow.

#### Scenario: Start async job
Given the Dev stage has a valid template
When it starts a backtest
Then it MUST enqueue a job and update the run with job_id/status.

### Requirement: Job failure resilience
**Description:** The system MUST capture job failures and allow the Dev stage to retry with adjusted templates without blocking the system.

#### Scenario: Backtest job fails
Given a backtest job fails
When the run is updated
Then the run MUST store an error/diagnostic and allow Dev to retry.

### Requirement: Consistent run state
**Description:** The run state MUST remain consistent when jobs fail (status, step, backtest_job fields).

#### Scenario: Failed job state
Given a backtest job fails
When the run is persisted
Then status/step MUST reflect failure while preserving previous context.
