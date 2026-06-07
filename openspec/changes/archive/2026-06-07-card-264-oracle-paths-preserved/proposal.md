## Why

The DEV/PROD Oracle migration left preserved path fixes outside `develop`; keeping the old `/root/.openclaw/workspace/crypto` defaults makes local scripts, beta lead email delivery, and systemd templates point at the retired workspace.

This change applies only the reusable path and endpoint hunks from `origin/preserve/release-source-dirty-20260607T032453Z`, leaving QA artifacts, `.env` backups, and already-integrated UI/runtime changes untouched.

## What Changes

- Replace stale workspace paths in operational examples and scripts with repo-relative or Oracle DEV/PROD paths.
- Make beta access load its default GOG/lead env file from `ops/landing-leads/.env.leads` relative to the checked-out repo.
- Make the landing prototype use the relative `/api/leads` endpoint for any `criptofarol.com.br` subdomain.
- Keep the existing override environment variables and runtime ports unchanged.
- Do not reintroduce preserved `.env` files, backups, QA screenshots, or deleted artifacts.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `maintenance`: operational scripts and service templates must not depend on the retired OpenClaw workspace path.
- `landing-conversion-copy`: the landing lead form endpoint resolution must work on production subdomains without hardcoded alternate ports.

## Impact

- Affected files: `backend/.env.example`, `backend/app/services/beta_access.py`, `frontend/public/prototypes/cripto-farol-landing-v4/index.html`, `init.sh`, `ops/systemd/cripto-farol-frontend.service`, `ops/systemd/cripto-farol-leads.service`.
- No database migration.
- No production release in this card; completion target is `develop` Done tecnico.
