## ADDED Requirements

### Requirement: Discovery workers are documented for PROD
The runtime architecture runbook SHALL document PROD discovery dispatcher and Celery worker units, flags, logs, and verification commands, not only the DEV path.

#### Scenario: Operator follows the runbook for PROD discovery
- **WHEN** the operator reads `docs/runtime-architecture.md` for discovery in production
- **THEN** the document names the PROD units, `RUN_DISCOVERY_OUTBOX_DISPATCHER`, the `discovery` queue, and how to confirm they are active
