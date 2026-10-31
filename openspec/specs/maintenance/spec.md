# maintenance Specification

## Purpose
TBD - created by archiving change corrigir-testes-workflow-e-branches. Update Purpose after archive.
## Requirements
### Requirement: Maintenance operations for test, branch, and file hygiene
The system SHALL perform maintenance operations to keep the project in a clean, operational state.

#### Scenario: Integration tests pass
- **WHEN** `pytest backend/tests/integration` is run
- **THEN** all tests pass or failures are documented as known issues with timestamps and issue references

#### Scenario: No stale feature branches remain
- **WHEN** `git branch -a` is run
- **THEN** no merged feature branches remain (feature/long-change, feature/monitor-candles-async-ui, feature/remover-locked-only-tela-carteira, feature/repemsar-layout, feature/workflow-backend-enforcement)

#### Scenario: test-results do not block upstream guard
- **WHEN** the upstream guard runs
- **THEN** `frontend/test-results/` is either ignored via .gitignore or committed, with no untracked files blocking the guard

### Requirement: Maintenance includes beta access hygiene
The system SHALL include repeatable maintenance tooling to verify closed-beta active users.

#### Scenario: Verify active user allowlist
- **WHEN** maintenance checks beta user access
- **THEN** the output SHALL identify whether only allowed beta emails remain active
- **AND** the check SHALL be runnable without mutating data

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

