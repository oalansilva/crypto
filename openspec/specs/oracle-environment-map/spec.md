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
DEV card closeout SHALL use the consumer overlay `release.restart` (Cripto overlay MAY name `./restart` in the canonical DEV `source`). Intermediate validation MAY restart only the affected unit from overlay `environments.*.services`. Hermes restarts SHALL be per component **when** overlay lists Hermes services. Temporary path deletion SHALL require explicit Alan authorization.

#### Scenario: Done technical on DEV
- **WHEN** a card is ready for Done technical in a consumer DEV environment
- **THEN** the skill requires the overlay `release.restart` in that consumer's canonical DEV source
- **AND** it MUST NOT require a partial OpenClaw-era restart as the closeout proof

#### Scenario: Release closeout in PROD
- **WHEN** a release is being closed and overlay has `environments.prod` plus non-empty `release.*` hooks
- **THEN** the skill requires inventory, published SHA, migrations, frontend production build, affected PROD services, public URL validation, and recorded evidence before `Pronto` via those overlay hooks

