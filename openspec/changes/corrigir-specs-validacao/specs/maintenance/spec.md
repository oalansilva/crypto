## ADDED Requirements

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
- **THEN** it SHALL retry with exponential backoff up to 3 times before failing

## MODIFIED Requirements

### Requirement: OpenSpec specs SHALL pass validation
All OpenSpec specs in the project SHALL pass `openspec validate --specs` with zero errors, including proper Purpose sections and Scenario blocks.

#### Scenario: Spec validation passes
- **WHEN** `openspec validate --specs` is run
- **THEN** all specs SHALL pass with 0 errors
- **AND** each requirement SHALL include at least one Scenario block
