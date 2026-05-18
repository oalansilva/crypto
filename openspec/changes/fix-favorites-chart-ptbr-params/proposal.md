## Why

Favorite chart detail screens still exposed raw English/internal strategy parameter keys and values such as `direction`, `long`, `ema_short`, `stop_loss`, and `data_source`. This made the trader-facing experience inconsistent with the Portuguese UI.

## What Changes

- Render strategy parameter labels in Portuguese on the Monitor chart modal.
- Render strategy parameter labels in Portuguese on the Favorites result chart (`/combo/results`).
- Translate common parameter values such as `long`/`short` and `ccxt` into trader-facing labels.
- Keep protected strategy behavior intact: protected parameters remain hidden for common users.
- Clarify the operational rule that corrections are only complete after integration in `develop`, restart, and URL verification.

## Capabilities

### New Capabilities

### Modified Capabilities
- `favorites`: Favorites result charts show trader-facing Portuguese parameter labels and values.
- `monitor`: Monitor chart detail shows trader-facing Portuguese parameter labels and values when parameters are visible.

## Impact

- Frontend: shared strategy parameter formatting helper, Monitor chart modal, Combo/Favorites result page.
- Tests: focused E2E coverage for Favorites result parameters and Monitor chart modal parameters.
- Docs: `AGENTS.md` and `rules.md` clarify the completion/integration rule.
