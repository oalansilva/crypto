## MODIFIED Requirements

### Requirement: Runtime scripts avoid retired workspace paths
Operational scripts and service templates SHALL avoid hardcoded references to the retired `/root/.openclaw/workspace/crypto` workspace for active DEV/PROD runtime paths.

#### Scenario: Init starts from current checkout
- **WHEN** `init.sh` needs to start the app because the backend is offline
- **THEN** it SHALL change directory to the repository checkout that contains `init.sh`
- **AND** it SHALL NOT require `/root/.openclaw/workspace/crypto` to exist

#### Scenario: Beta access lead environment is explicit
- **WHEN** `BETA_ACCESS_GOG_ENV_FILE` is not set
- **THEN** beta access SHALL NOT load any environment file by default, and SHALL NOT point at `ops/landing-leads/`, which left the repository with the Node lead service (card #1160)
- **AND** explicit `BETA_ACCESS_GOG_ENV_FILE` overrides SHALL continue to work

#### Scenario: Production systemd templates point at production checkout
- **WHEN** the production frontend systemd unit template is installed
- **THEN** its working directory and file paths SHALL point at `/srv/apps/prod/criptofarol/source`
- **AND** it SHALL NOT point at `/root/.openclaw/workspace/crypto`

## REMOVED Requirements

### Requirement: Leads systemd template does not use OpenClaw HOME
**Reason**: The Node lead service (`ops/landing-leads/`, `criptofarol-prod-leads.service`) and its unit template leave the repository in card #1160; `POST /api/leads` goes straight to the backend, which saves the lead in `landing_leads`.
**Migration**: None in the repository. In production, the unit is disabled in phase F4 and deleted from systemd (with its drop-ins) and from the PROD deploy service list before phase F6 of the card #1160 cut.
