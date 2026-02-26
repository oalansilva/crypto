## ADDED Requirements

### Requirement: Turn Scheduler MUST back off when no active changes exist
The system MUST reduce Turn Scheduler executions when there are no active OpenSpec changes (no `.openspec.yaml` under `openspec/changes/*` excluding `openspec/changes/archive`).

#### Scenario: No active changes detected
- **WHEN** the scheduler evaluation determines there are zero active changes
- **THEN** the system MUST switch the Turn Scheduler into an idle/backoff mode
- **AND THEN** the effective run frequency MUST be reduced compared to the normal 15-minute cadence

#### Scenario: Repeated idle state
- **WHEN** the system remains in the zero-active-changes state across multiple checks
- **THEN** the system MUST continue operating in idle/backoff mode without emitting user notifications

### Requirement: Turn Scheduler MUST restore normal cadence when work exists
The system MUST automatically restore the normal Turn Scheduler cadence when at least one active change exists.

#### Scenario: Active change appears
- **WHEN** at least one active change is detected
- **THEN** the system MUST restore the normal Turn Scheduler cadence (15 minutes)
- **AND THEN** the scheduler MUST resume selecting and executing PO/DEV/QA work as before

### Requirement: The change MUST be safe and reversible
The system MUST allow reverting the scheduler to the pre-change behavior without impacting application runtime.

#### Scenario: Revert to normal cadence
- **WHEN** the idle/backoff behavior is disabled (via config/job update)
- **THEN** the Turn Scheduler MUST run at the normal 15-minute cadence
- **AND THEN** no additional state or migrations MUST be required
