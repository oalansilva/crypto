# prod-discovery-workers Specification

## Purpose
PROD hospeda dispatcher e worker Celery de Discovery nos sources canônicos.

## Requirements
### Requirement: PROD hosts discovery dispatcher and Celery worker
Production SHALL run a discovery outbox dispatcher (`RUN_DISCOVERY_OUTBOX_DISPATCHER=1`) and a Celery worker on queue `discovery` (`criptofarol-prod-discovery-worker`). Both units SHALL be installed, enabled, and active after the authorized PROD rollout of this card. Favorite-refresh already active on the PROD runtime worker SHALL remain enabled.

#### Scenario: PROD units are active
- **WHEN** an operator inspects systemd on the PROD host after install
- **THEN** the discovery dispatcher path and `criptofarol-prod-discovery-worker` are enabled and active
- **AND** favorite backtest refresh on the PROD runtime worker is still enabled

#### Scenario: Sweep is consumed in PROD
- **WHEN** an admin starts a discovery sweep on `https://criptofarol.com.br/discovery`
- **THEN** the sweep leaves `pending`/`queued` and is processed (progress/counters move on the live page)
- **AND** `/api/health` returns 200
- Queue consume without that visible lifecycle MUST NOT close the card.

### Requirement: Installer accepts the canonical DEV and PROD sources
The discovery-worker installer SHALL accept `/srv/apps/dev/criptofarol/source` (DEV units) and `/srv/apps/prod/criptofarol/source` (PROD units) and SHALL refuse any other path. Backend, frontend, and leads PROD services SHALL NOT be redesigned, dropped-in, or restarted by this change; only affected discovery workers restart.

#### Scenario: Install from PROD source
- **WHEN** the installer runs from `/srv/apps/prod/criptofarol/source`
- **THEN** it installs PROD discovery units instead of exiting because the path is not DEV

#### Scenario: Install from DEV source still works
- **WHEN** the installer runs from `/srv/apps/dev/criptofarol/source`
- **THEN** it continues to install the existing DEV discovery units

#### Scenario: Non-canonical path is refused
- **WHEN** the installer runs from any other directory
- **THEN** it exits non-zero and installs nothing

#### Scenario: PROD API/UI units stay untouched
- **WHEN** discovery workers are installed in PROD
- **THEN** `criptofarol-prod-backend`, `criptofarol-prod-frontend`, and `criptofarol-prod-leads` are not rewritten or restarted by the installer

