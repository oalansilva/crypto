# Capability: Log Monitoring & Proactive Error Classification

## ADDED Requirements

### Requirement: Detect runtime download errors
**Description:** The system MUST detect download/runtime errors for lab runs (e.g., exchange download failures) and classify them into a known error type.

#### Scenario: Invalid interval from exchange
Given a lab run enters execution and the exchange client returns an "Invalid interval" error
When the system processes the error
Then the run diagnostic MUST include type "invalid_interval" and a human-readable message.

### Requirement: Expose run diagnostic via API
**Description:** The system MUST include a diagnostic object in the lab run API response when a classified error is detected.

#### Scenario: API returns diagnostic
Given a run has a classified error
When the client requests `/api/lab/runs/{run_id}`
Then the response MUST include `diagnostic.type` and `diagnostic.message`.

### Requirement: Persist diagnostic in run log
**Description:** The system MUST persist the diagnostic summary in the run log for later inspection.

#### Scenario: Diagnostic persisted
Given a classified error occurred for a run
When the system writes run logs
Then the diagnostic summary MUST be stored with the run data.
