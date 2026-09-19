## ADDED Requirements

### Requirement: PROD overlay lists the discovery worker for release closeout
Production overlay `environments.prod.services` SHALL include `criptofarol-prod-discovery-worker.service` so the authorized production publish window restarts the long-running Celery discovery worker together with the other in-memory product processes. The installer path and unit templates remain the existing PROD discovery worker; this requirement MUST NOT create a new production restart command outside release closeout and MUST NOT change DEV `./restart`.

#### Scenario: Overlay inventory includes the PROD discovery worker
- **WHEN** an operator reads `.covenant-flow/overlay.yaml` `environments.prod`
- **THEN** `services` contains `criptofarol-prod-discovery-worker.service`

#### Scenario: Publish window restarts the discovery worker with the other long-running units
- **WHEN** production release closeout restarts the overlay publish window
- **THEN** `criptofarol-prod-discovery-worker` is restarted in the same window as backend, frontend, leads, and runtime-worker
- **AND** the installer MUST NOT be the only way that worker returns to the published code

#### Scenario: DEV restart path stays unchanged
- **WHEN** this change is applied
- **THEN** canonical DEV `./restart` continues to restart DEV discovery workers as today
- **AND** no new production restart entrypoint is added outside release closeout
