## ADDED Requirements

### Requirement: Favorite refresh respects CPU guardrails
The system SHALL throttle the automatic favorite refresh routine so it does not continue starting refresh work while host CPU usage is above the configured ceiling, defaulting to 60 percent.

#### Scenario: CPU is above ceiling before next favorite
- **WHEN** the favorite refresh routine is about to start another due favorite
- **AND** measured CPU usage is above the configured ceiling
- **THEN** it SHALL pause or skip starting that favorite during the current cycle
- **AND** it SHALL record the CPU guard as the reason work was paused or skipped
- **AND** it SHALL keep already refreshed favorites committed

#### Scenario: CPU stays below ceiling
- **WHEN** measured CPU usage is at or below the configured ceiling
- **THEN** the routine SHALL continue processing due favorites up to the configured batch limit

### Requirement: Favorite refresh runs as a daily bounded cycle
The system SHALL run automatic favorite refresh as a bounded background cycle configured to attempt due favorites at least once per day while respecting batch limits and pauses.

#### Scenario: Runtime stack starts
- **WHEN** the standard crypto stack start script runs without explicit overrides
- **THEN** it SHALL enable the runtime worker and favorite refresh routine by default
- **AND** it SHALL keep a daily refresh interval by default
- **AND** it SHALL run the refresh loop more frequently than once per day so bounded batches can cover the due queue
- **AND** it SHALL use a bounded per-cycle favorite limit by default

#### Scenario: More favorites are due than the batch limit
- **WHEN** due favorites exceed the configured per-cycle limit
- **THEN** the routine SHALL process at most the configured number in that cycle
- **AND** it SHALL leave the remaining favorites due for later cycles

### Requirement: Favorite refresh runtime state is observable
The system SHALL expose safe operational state for the automatic favorite refresh routine through backend runtime status.

#### Scenario: Runtime status is requested
- **WHEN** `/api/runtime/status` is requested
- **THEN** the response SHALL include whether favorite refresh is enabled
- **AND** it SHALL include sanitized latest-cycle state including due, success, failed, skipped, CPU threshold, and reason when available

#### Scenario: Refresh cycle completes or pauses
- **WHEN** a favorite refresh cycle completes or stops because of CPU guardrails
- **THEN** the system SHALL update the latest-cycle state before waiting for the next cycle
