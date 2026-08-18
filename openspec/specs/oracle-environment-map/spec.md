# oracle-environment-map Specification

## Purpose
A skill de ambientes mapeia DEV/PROD reais e Hermes; OpenClaw não é runtime ativo.

## Requirements
### Requirement: Environment skill maps real DEV, PROD, and Hermes
The global skill `alan-workflow-ambientes` SHALL describe the live Oracle topology: Cripto Farol DEV and PROD paths/ports/services/databases, Clara DEV and PROD, and Hermes components (Telegram, SemParar, Clara DEV API, dashboard, Second Brain). OpenClaw SHALL NOT appear as an active runtime.

#### Scenario: Agent reads the skill before a DEV action
- **WHEN** an agent loads `alan-workflow-ambientes` for a Cripto Farol DEV task
- **THEN** the skill names `/srv/apps/dev/criptofarol/source`, the live DEV units, and `https://dev.criptofarol.com.br`
- **AND** it SHALL NOT instruct the agent to operate `openclaw-gateway.service` or port `18789` as current runtime

#### Scenario: Agent reads the skill before a PROD action
- **WHEN** an agent loads the skill for Cripto Farol PROD
- **THEN** the skill names `/srv/apps/prod/criptofarol/source`, the live PROD units, and `https://criptofarol.com.br`
- **AND** mutation remains fail-closed unless Alan explicitly authorized production

### Requirement: Restart policy distinguishes canonical closeout from targeted checks
DEV card closeout SHALL use the canonical `./restart`. Intermediate validation MAY restart only the affected unit. Hermes restarts SHALL be per component. Temporary path deletion SHALL require explicit Alan authorization.

#### Scenario: Done technical on DEV
- **WHEN** a card is ready for Done technical in Cripto Farol DEV
- **THEN** the skill requires `./restart` in the canonical DEV source, not a partial OpenClaw-era restart as the closeout proof

#### Scenario: Release closeout in PROD
- **WHEN** a release is being closed
- **THEN** the skill requires inventory, published SHA, migrations, frontend production build, affected PROD services, public URL validation, and recorded evidence before `Pronto`

