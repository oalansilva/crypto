# oracle-environment-map Specification

## Purpose
A skill de ambientes mapeia DEV/PROD reais e Hermes; OpenClaw não é runtime ativo.
## Requirements
### Requirement: Environment skill maps real DEV, PROD, and Hermes
The skill `covenant-flow-environments` SHALL instruct the agent to load topology **values** from overlay `environments.*` (`source`, `url`, `db`, `services[]`). The packaged skill MUST NOT hardcode Cripto Farol / Clara / Hermes filesystem paths, systemd units, or URLs as the only map. A consumer overlay MAY list Hermes components when that project runs Hermes. OpenClaw SHALL NOT appear as an active runtime. A project without `environments.prod` SHALL be treated as DEV-only and MUST refuse production deploy.

#### Scenario: Agent reads the skill before a DEV action
- **WHEN** an agent loads `covenant-flow-environments` for a task that can affect DEV
- **THEN** the skill reads `environments.dev` from `.covenant-flow/overlay.yaml`
- **AND** it SHALL NOT instruct the agent to operate `openclaw-gateway.service` or port `18789` as current runtime
- **AND** it SHALL NOT treat hardcoded `/srv/apps/dev/criptofarol/source` as the only DEV path in the packaged skill

#### Scenario: Agent reads the skill before a PROD action
- **WHEN** an agent loads the skill for a production action and overlay has `environments.prod`
- **THEN** the skill names `environments.prod.source`, units, and url from overlay
- **AND** mutation remains fail-closed unless Alan explicitly authorized production

#### Scenario: Packaged skill is not the Cripto-only map
- **WHEN** the product `covenant-flow-environments` skill is inspected
- **THEN** it does not hardcode Cripto/Clara/Hermes paths or units as the sole topology
- **AND** first consumer Cripto supplies those values in overlay `environments.*`

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

