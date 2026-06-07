## Purpose

Keep runtime and maintenance entry points aligned with the current Oracle DEV/PROD checkout layout.

## ADDED Requirements

### Requirement: Runtime scripts avoid retired workspace paths
Operational scripts and service templates SHALL avoid hardcoded references to the retired `/root/.openclaw/workspace/crypto` workspace for active DEV/PROD runtime paths.

#### Scenario: Init starts from current checkout
- **WHEN** `init.sh` needs to start the app because the backend is offline
- **THEN** it SHALL change directory to the repository checkout that contains `init.sh`
- **AND** it SHALL NOT require `/root/.openclaw/workspace/crypto` to exist

#### Scenario: Beta access loads repo-local lead environment by default
- **WHEN** `BETA_ACCESS_GOG_ENV_FILE` is not set
- **THEN** beta access SHALL default to `ops/landing-leads/.env.leads` under the active repository checkout
- **AND** explicit `BETA_ACCESS_GOG_ENV_FILE` overrides SHALL continue to work

#### Scenario: Production systemd templates point at production checkout
- **WHEN** the production frontend or leads systemd unit templates are installed
- **THEN** their working directories and file paths SHALL point at `/srv/apps/prod/criptofarol/source`
- **AND** they SHALL NOT point at `/root/.openclaw/workspace/crypto`
