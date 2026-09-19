## ADDED Requirements

### Requirement: PROD overlay inventory classifies long-running publish restart versus oneshot jobs
Consumer overlay `environments.prod.services` SHALL list every production product unit that keeps product code in memory, including `criptofarol-prod-discovery-worker.service` together with site, API, capture, and runtime-worker. Overlay `environments.prod.oneshot_services` SHALL list the one-shot jobs (`criptofarol-prod-candle-writer.service`, `criptofarol-prod-telegram-alert-scan.service`) and MUST be a subset of `services`. The production publish window SHALL restart `services` minus `oneshot_services`. The day's canonical release note SHALL list restarted units from that overlay window, not from a chat-memorized list. One-shot jobs SHALL be recorded as a single-run job / waiting timer, not as a restart in that window. The publish MUST NOT scan the host for long-running units absent from the overlay.

#### Scenario: Discovery worker is on the PROD overlay list
- **WHEN** an operator reads `.covenant-flow/overlay.yaml` `environments.prod.services`
- **THEN** the list includes `criptofarol-prod-discovery-worker.service`
- **AND** it also includes the other long-running production units (backend, frontend, leads, runtime-worker)

#### Scenario: Oneshot jobs are classified out of the publish window
- **WHEN** the production publish window is derived from overlay
- **THEN** candle-writer and telegram-alert-scan are taken from `oneshot_services`
- **AND** they are not restarted in that window only to match inventory
- **AND** the day's release note records them as a one-shot job / waiting timer

#### Scenario: Release note comes from overlay inventory
- **WHEN** the operator writes `docs/release-<date>.md` after a production deploy
- **THEN** the restarted-services list matches the overlay publish window
- **AND** it MUST NOT copy a services list remembered from chat or from a previous September lote

#### Scenario: Live process outside the overlay is not the publish inventory
- **WHEN** a long-running systemd unit of the product is absent from overlay `environments.prod.services`
- **THEN** the publish window MUST NOT add it by scanning the host
- **AND** a new product unit MUST enter the overlay first

## MODIFIED Requirements

### Requirement: Restart policy distinguishes canonical closeout from targeted checks
DEV card closeout SHALL use the consumer overlay `release.restart` (Cripto overlay MAY name `./restart` in the canonical DEV `source`). Intermediate validation MAY restart only the affected unit from overlay `environments.*.services`. Hermes restarts SHALL be per component **when** overlay lists Hermes services. Temporary path deletion SHALL require explicit Alan authorization. Production release closeout SHALL restart every long-running unit in the overlay publish window (`environments.prod.services` minus `environments.prod.oneshot_services`) in the same deploy window, then validate the public URL. It MUST NOT treat a chat-memorized or "affected-only" subset that omits a long-running overlay unit as sufficient. DEV `release.restart` MUST NOT change as part of this production publish rule.

#### Scenario: Done technical on DEV
- **WHEN** a card is ready for Done technical in a consumer DEV environment
- **THEN** the skill requires the overlay `release.restart` in that consumer's canonical DEV source
- **AND** it MUST NOT require a partial OpenClaw-era restart as the closeout proof

#### Scenario: Release closeout in PROD
- **WHEN** a release is being closed and overlay has `environments.prod` plus non-empty `release.*` hooks
- **THEN** the skill requires inventory, published SHA, migrations, frontend production build, restart of every long-running unit in the overlay publish window, public URL validation, and recorded evidence before `Pronto` via those overlay hooks
- **AND** one-shot jobs in `oneshot_services` MUST NOT be required restarts in that window
- **AND** the restarted-services evidence MUST NOT be a subset that omits a long-running overlay unit
