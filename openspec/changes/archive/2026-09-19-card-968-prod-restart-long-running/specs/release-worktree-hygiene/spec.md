## ADDED Requirements

### Requirement: Post refuses incomplete long-running deploy evidence
When production deploy evidence is required (`release-guard post`, and `pre` once evidence is already required), `PROD_DEPLOY_EVIDENCE` `services=` SHALL list every long-running unit of the overlay publish window (`environments.prod.services` minus `environments.prod.oneshot_services`). Missing any of those units MUST be a visible blocker; package cards MUST NOT be treated as published. Extra names (one-shot jobs) SHALL warn and MUST NOT block. The guard MUST NOT roll back the published tree or undo restarts already done. Discovery sweep timing MUST NOT be required for this gate.

#### Scenario: Evidence omits the discovery worker
- **WHEN** `post` runs with overlay PROD whose publish window includes `criptofarol-prod-discovery-worker`
- **AND** `PROD_DEPLOY_EVIDENCE` `services=` lists backend, frontend, leads, and runtime-worker only
- **THEN** the guard fails closed with a visible blocker
- **AND** cards MUST NOT move to `Pronto`

#### Scenario: Evidence lists the full long-running window
- **WHEN** `services=` lists every unit in the overlay publish window (with or without `.service` suffix)
- **THEN** this completeness gate passes
- **AND** other existing `post` blockers still apply

#### Scenario: Oneshot names in services are not required
- **WHEN** `services=` includes candle-writer or telegram-alert-scan in addition to the full long-running window
- **THEN** the extra oneshot names are a warning
- **AND** they MUST NOT by themselves fail this gate
- **AND** omitting oneshot names MUST NOT fail this gate

### Requirement: Post refuses a running long-running unit still on old code
When a long-running overlay publish-window unit is **active**, `release-guard post` SHALL refuse if that process started before this deploy window (systemd `ExecMainStartTimestamp` or equivalent). The refuse MUST be visible. The guard MUST NOT undo disk or prior restarts. Timing a Discovery sweep MUST NOT be required.

#### Scenario: Active discovery worker still on the previous boot
- **WHEN** `criptofarol-prod-discovery-worker` is active
- **AND** its process start is before this deploy window
- **THEN** `post` fails closed
- **AND** the published tree is left as-is

#### Scenario: Active long-running units match this deploy window
- **WHEN** every active unit in the overlay publish window started in this deploy window
- **THEN** this stale-code gate passes

### Requirement: Stopped long-running unit does not block closeout when site and API respond
If a long-running overlay publish-window unit is inactive or failed after the restart attempt, `release-guard post` MUST NOT block on that unit remaining down when the overlay `release.health_url` (site and API) responds successfully. That outage is a separate incident. `services=` MUST still list that unit as part of the publish window. The guard MUST NOT require the unit to become active to pass.

#### Scenario: Discovery worker down and public health ok
- **WHEN** `criptofarol-prod-discovery-worker` is not running after the publish restart
- **AND** site and API health succeed
- **AND** `services=` still lists the discovery worker with the rest of the window
- **THEN** this stopped-process gate does not block
- **AND** the outage is not treated as unpublished cards

#### Scenario: Stopped unit omitted from evidence still fails completeness
- **WHEN** a long-running window unit is down
- **AND** `services=` omits that unit
- **THEN** the incomplete-evidence gate still blocks
