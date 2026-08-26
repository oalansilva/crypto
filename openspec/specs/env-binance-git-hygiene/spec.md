# env-binance-git-hygiene Specification

## Purpose
TBD - created by archiving change card-687-remove-env-binance. Update Purpose after archive.
## Requirements
### Requirement: Tip of develop has no tracked .env.binance
After the PR of this card merges, the tip of `origin/develop` SHALL NOT contain a tracked blob at path `.env.binance`. History rewrite is out of scope; `origin/main` MAY still list the path until release.

#### Scenario: git ls-tree on develop is empty for the path
- **WHEN** the card PR has merged into `origin/develop`
- **THEN** `git ls-tree origin/develop -- .env.binance` SHALL produce no tree entry
- **AND** Apply SHALL have removed the path from the Git index via `git rm --cached` (or equivalent) without recommitting real secret values

#### Scenario: origin/main may still have the path until release
- **WHEN** `origin/main` still lists `.env.binance` after develop is clean
- **THEN** that SHALL be acceptable for this card
- **AND** Done SHALL NOT require that leaked keys are revoked by the Binance API

### Requirement: gitignore blocks new .env.<name> except allowlisted examples
The repository `.gitignore` SHALL ignore `.env.*` files and SHALL allowlist the already-tracked example files so they remain versionable without real credentials.

#### Scenario: Arbitrary .env.<name> is ignored
- **WHEN** a contributor creates an untracked file matching `.env.<name>` that is not an allowlisted example (e.g. `.env.probe` or a restored `.env.binance`)
- **THEN** Git SHALL treat that path as ignored
- **AND** it SHALL NOT be added by a normal `git add` without force

#### Scenario: Allowlisted examples stay tracked without real values
- **WHEN** the allowlist is applied
- **THEN** `.env.binance.example`, `.env.docker.example`, `backend/.env.example`, and `frontend/.env.example` SHALL remain tracked (or trackable)
- **AND** those examples SHALL NOT contain real `BINANCE_API_KEY` / `BINANCE_API_SECRET` (or other live secrets)
- **AND** `.env.binance.example` MAY document empty placeholders for Binance vars

### Requirement: Canonical ops secret home is root .env
Operational Binance credentials for DEV and PROD SHALL live in the checkout root `.env` (already gitignored). The project SHALL NOT recreate `.env.binance` as the canonical home and SHALL NOT add a runtime loader that reads `.env.binance` by name. Operators SHALL reuse the **current** key material (no new Binance key generation in this card).

#### Scenario: DEV and PROD creds in root .env (reuse current keys)
- **WHEN** operators configure Binance API credentials after this change
- **THEN** `BINANCE_API_KEY` and `BINANCE_API_SECRET` SHALL be present in the root `.env` used by that environment (DEV and PROD), reusing the existing keys if they were previously only in local `.env.binance`
- **AND** operators SHALL stop using `.env.binance` as the local source of truth
- **AND** operators SHALL NOT be required to generate a new Binance key pair for this card

#### Scenario: No explicit .env.binance load in runtime or systemd
- **WHEN** backend `config.py` dotenv loading and `ops/systemd` units are inspected after Apply
- **THEN** they SHALL continue to load only `backend/.env` and/or root `.env` (as today)
- **AND** they SHALL NOT gain an explicit load of `.env.binance` by filename
- **AND** Apply SHALL NOT introduce such a load

### Requirement: No Binance key rotation gate in this card
This card SHALL NOT require generating new Binance API keys, writing rotated credentials, smoking new-key presence (former AC5), revoking old keys, or recording Binance API rejection evidence. Alan T6 (2026-08-26): private repository; keys without withdraw permission. Done is hygiene + ops home migration only.

#### Scenario: Rotation and revoke are out of scope
- **WHEN** Apply and Done criteria for this card are evaluated
- **THEN** there SHALL be no pre-merge gate that requires new Binance keys, revoke of old keys, or API rejection evidence
- **AND** evidence SHALL NOT paste key or secret values into issue, chat, log, or artifact

