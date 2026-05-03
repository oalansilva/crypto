## Why

Common users need enough strategy context in Monitor to choose which operational setups they prefer, but current non-admin redaction hides the strategy name entirely. Monitor also has a favorite star, but the preference is browser-local instead of a user-level product choice.

## What Changes

- Show a safe public strategy display name to common users in Monitor, for example `Multi MA Crossover`, while keeping strategy code, parameters, indicator values, details, and admin notes redacted.
- Add user-level Monitor strategy preference storage so a user can like/unlike Monitor strategies and later filter to preferred setups.
- Keep current Monitor favorite behavior backward-compatible during load while making the API the source of truth after login.

## Capabilities

### New Capabilities
- `monitor-strategy-preferences`: Users can like/unlike Monitor strategies and retrieve their liked strategy IDs.

### Modified Capabilities
- `opportunity-monitor`: Non-admin Monitor opportunity payloads expose a safe public strategy display name while preserving secret redaction.

## Impact

- Backend: opportunity redaction helper, Monitor routes, SQLAlchemy model, runtime schema creation.
- Frontend: Monitor strategy labels, favorite-star persistence, filter behavior.
- Tests: backend route/redaction tests and frontend E2E API mock expectations.
