## ADDED Requirements

### Requirement: Consistent Run State
**Description:** The system SHALL keep `status` and `phase` aligned with the actual execution state of a Lab run. A run MUST NOT be marked as running/implementation until execution has started.

#### Scenario: Upstream not yet executed
- **WHEN** the run is in upstream collection or review
- **THEN** `phase` is `upstream` and `status` reflects `needs_user_input`, `ready_for_review`, or `ready_for_execution`

#### Scenario: Execution started
- **WHEN** the execution job starts
- **THEN** `phase` is `execution` and `status` is `running`

### Requirement: Managed Execution Worker
**Description:** The system SHALL execute Lab runs using a managed background worker (job manager or task queue) instead of raw threads, to survive reloads and provide cancellation.

#### Scenario: Worker-managed run
- **WHEN** a Lab run is started
- **THEN** the run is enqueued and executed by the managed worker
- **AND** the run can be cancelled or safely resumed

### Requirement: Retry With Reasons Fallback
**Description:** When the Trader rejects a strategy, the system SHALL use `required_fixes` when present, and fall back to `reasons` if `required_fixes` is empty, to decide whether to retry.

#### Scenario: Required fixes present
- **WHEN** a Trader verdict includes `required_fixes`
- **THEN** retries are based on `required_fixes`

#### Scenario: Required fixes missing
- **WHEN** a Trader verdict omits `required_fixes` but includes `reasons`
- **THEN** retries are based on `reasons`

### Requirement: Output Schema Validation
**Description:** The system SHALL validate Trader and Dev outputs against expected JSON schema. If invalid, it MUST record diagnostics and proceed with safe defaults.

#### Scenario: Valid JSON output
- **WHEN** Trader/Dev returns valid structured output
- **THEN** the system parses and uses it

#### Scenario: Invalid JSON output
- **WHEN** Trader/Dev returns invalid or malformed JSON
- **THEN** the system records a diagnostic error and applies a safe fallback verdict

### Requirement: Run Timeouts
**Description:** The system SHALL enforce per-node timeouts and a total run timeout. On timeout, it MUST mark the run as failed with diagnostic details.

#### Scenario: Node timeout
- **WHEN** a node execution exceeds its timeout
- **THEN** the run is marked failed with `diagnostic.timeout` details

#### Scenario: Total timeout
- **WHEN** the overall run exceeds the configured total timeout
- **THEN** the run is marked failed and execution stops
