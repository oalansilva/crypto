# health-monitoring Specification

## Purpose
TBD - created by archiving change corrigir-divida-tecnica-openspec. Update Purpose after archive.
## Requirements
### Requirement: System health monitoring
The system SHALL run periodic health checks on backend and frontend services and notify Alan via Telegram when any service is unavailable.

#### Scenario: Backend health check passes
- **WHEN** the health cron runs
- **THEN** it SHALL send a GET request to http://127.0.0.1:8003/api/health and return success if the response is HTTP 200

#### Scenario: Frontend health check passes
- **WHEN** the health cron runs
- **THEN** it SHALL send a GET request to http://127.0.0.1:5173 and return success if the response is HTTP 200

#### Scenario: Backend health check fails
- **WHEN** the health cron runs and http://127.0.0.1:8003/api/health does not return HTTP 200 within the timeout
- **THEN** the system SHALL send a Telegram notification to Alan with the failure details

#### Scenario: Frontend health check fails
- **WHEN** the health cron runs and http://127.0.0.1:5173 does not return HTTP 200 within the timeout
- **THEN** the system SHALL send a Telegram notification to Alan with the failure details

### Requirement: Cron job reliability
The system SHALL ensure that daily cron jobs (crypto-news-daily, monitor diario) run without consecutive errors, either by fixing rate limit issues with backoff or by disabling them with a manual trigger option.

#### Scenario: Cron job succeeds
- **WHEN** a daily cron job runs (crypto-news-daily or monitor diario)
- **THEN** it SHALL complete without HTTP 429 or consecutive errors

#### Scenario: Cron job rate limited
- **WHEN** a daily cron job encounters a rate limit (HTTP 429)
- **THEN** the system SHALL implement exponential backoff and retry, OR disable the job and provide a manual trigger mechanism

### Requirement: OpenSpec validation clean
The system SHALL have 0 OpenSpec validation errors across all specs in `spec/` directory, with any remaining issues documented as known/acknowledged.

#### Scenario: OpenSpec validation runs clean
- **WHEN** `openspec validate --specs` is run
- **THEN** it SHALL return 0 errors across all 14 specs: chart-visualization, combo-optimizer, combo-strategies, database-strategy-config, design, external-balances, favorites, optimization, optimization-engine, performance, performance-metrics, strategy-comparison, strategy-enablement, ui-ux

### Requirement: Legacy coordination docs cleanup
The system SHALL maintain a clean `docs/coordination/` directory containing only the README and active coordination files, with archived/completed change files removed.

#### Scenario: Coordination docs are clean
- **WHEN** `docs/coordination/` is reviewed
- **THEN** it SHALL contain only README.md and active coordination files, with no archived/completed change files present

