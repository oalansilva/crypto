## Context

The preserved dirty branch contains mixed content: useful path fixes, already-integrated runtime/UI changes, local `.env` backups, and QA artifact deletion. The implementation must cherry-pick only the path/endpoint behavior that remains absent from current `develop`.

## Decisions

- Use repo-relative detection for executable scripts when possible, so DEV and PROD checkouts can run from their own directory without editing code.
- Use explicit `/srv/apps/prod/criptofarol/source` paths only in production systemd unit templates, because those units are production-specific.
- Keep `BETA_ACCESS_GOG_ENV_FILE` overridable through environment and only change its default to the repo-local `ops/landing-leads/.env.leads`.
- Treat the landing prototype endpoint change as behaviorally relevant: all `*.criptofarol.com.br` hostnames use `/api/leads`, while local/IP preview keeps the port `5174` development endpoint.
- Do not apply preserved deletions of QA artifacts or preserved local `.env` files.

## Validation

- Focused unit test for beta access path default/import behavior.
- Frontend build to catch landing syntax and TypeScript impact.
- `openspec validate --all`.
- `./restart` on DEV to prove the updated scripts still serve backend/frontend.

## Rollback

Revert the card commit from `develop`. The old behavior is isolated to static defaults and script paths; no data migration is involved.
