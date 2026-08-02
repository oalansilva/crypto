## ADDED Requirements

### Requirement: Backend unit-test decisions MUST be auditable
The repository MUST maintain a reproducible inventory of every backend unit-test file with its protected production behavior, current reachability, persistence need, regression risk, decision to keep, refactor/consolidate, or remove, and supporting evidence. A test MUST NOT be removed solely because it is slow, old, rarely used, or named for removed/coverage behavior.

#### Scenario: Every discovered unit-test file is classified
- **WHEN** the audit validator compares the inventory with `backend/tests/unit/test_*.py`
- **THEN** every discovered file has exactly one decision and the inventory contains no stale file entry

#### Scenario: A test file is proposed for removal
- **WHEN** the audit classifies a file as remove
- **THEN** its evidence proves that the production behavior is unreachable or removed, or that equivalent regression coverage remains elsewhere

### Requirement: Backend unit-test performance MUST be measured reproducibly
The backend unit-test workflow MUST produce comparable measurements that include revision/environment, collected cases, total duration, per-file duration aggregation, p95, the ten slowest files, skips, and warning counts.

#### Scenario: A baseline or optimized measurement is recorded
- **WHEN** the documented benchmark command runs against the backend unit suite with PostgreSQL and coverage enabled
- **THEN** it emits machine-readable raw evidence and a deterministic summary containing all required metrics

### Requirement: Pure unit tests MUST NOT pay PostgreSQL reset cost
Tests that do not exercise persistence MUST run without creating application/workflow schemas, opening a PostgreSQL engine, or truncating database tables. Tests that exercise persistence MUST explicitly request isolated PostgreSQL state and MUST retain safeguards against runtime database names.

#### Scenario: A pure test runs
- **WHEN** a unit test without the persistence marker or fixture executes
- **THEN** the shared database-isolation helper performs no engine, schema, or truncate operation

#### Scenario: A persistence test runs
- **WHEN** a marked backend unit test exercises application or workflow persistence
- **THEN** it uses PostgreSQL, validates the dedicated test database name, prepares required schemas, and resets state deterministically

### Requirement: Backend unit tests MUST use a bounded low-overhead runner
The CI workflow MUST avoid starting pytest and coverage once per unit-test file while preserving actionable progress, per-test hang protection, a job-level timeout, failure reporting, and coverage artifact compatibility.

#### Scenario: The backend unit suite runs in CI
- **WHEN** the `backend-unit-tests` job executes
- **THEN** it runs the unit directory in a consolidated bounded coverage session and uploads coverage plus timing evidence

#### Scenario: A test hangs or fails
- **WHEN** a case exceeds its timeout or an assertion fails
- **THEN** the job terminates with a non-success result and identifies the affected test in its logs or report

### Requirement: Optimization MUST preserve regression protection
The optimized backend test workflow MUST keep total backend line coverage and differential coverage at 70% or higher, MUST run unit and integration tests against PostgreSQL, and MUST classify persistent skips and recurring warnings without silently suppressing project failures.

#### Scenario: Optimized tests reach QA
- **WHEN** the reviewed change is validated
- **THEN** unit tests, integration tests, total coverage, differential coverage, and required QA jobs reach successful terminal results with thresholds unchanged or improved

#### Scenario: A persistent skip or warning remains
- **WHEN** the optimized suite reports a repeated skip or warning category
- **THEN** the audit records its cause and disposition, and any suppression is limited to understood non-project noise

### Requirement: Optimization outcome MUST be demonstrated statistically
The implementation MUST compare at least three comparable optimized runs with the five green reference runs. The optimized median MUST improve by at least 30%, or the evidence MUST prove that the measured bottleneck is outside the suite and link a specific follow-up action.

#### Scenario: Performance target is met
- **WHEN** three comparable optimized runs complete
- **THEN** their median `backend-unit-tests` duration is at least 30% lower than the reference median and the evidence records the runs and calculation

#### Scenario: Performance target is not met
- **WHEN** the optimized median improves by less than 30%
- **THEN** the card remains incomplete unless evidence isolates the external bottleneck and a specific tracked follow-up is created
