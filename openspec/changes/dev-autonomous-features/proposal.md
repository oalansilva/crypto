## Why

The Dev agent currently only rewrites logic to fit existing columns, which blocks strategies that require derived features (e.g., rsi_prev/shift). Giving Dev the autonomy to request or define derived features will reduce failed preflight attempts and improve strategy quality.

## What Changes

- Allow Dev to declare new derived indicator columns (e.g., rsi_prev, ema_slope) when needed.
- Extend the feature/indicator pipeline to support a small set of safe derived transforms.
- Update the Dev prompt and validation to permit/expect derived columns when justified.
- Define autonomy guardrails for Dev tool usage (Codex CLI vs PythonREPLTool) and unsafe operations.

## Capabilities

### New Capabilities
- `dev-autonomous-features`: Dev can propose and register derived columns required by strategy logic.

### Modified Capabilities
- (none)

## Autonomy Guardrails

- **Codex CLI:** Allowed to modify files and run project-local commands within the repo (workspace). Use `--full-auto` but **no full-machine/network access** by default.
- **PythonREPLTool:** Allowed for calculations, prototyping, and preparing transformations/logic to be implemented in the repo; may generate artifacts to guide changes, but production changes still happen via repo edits.
- **Safety gates:** Destructive or system-level operations (e.g., `rm`, package installs outside the repo, service restarts) require explicit human confirmation.
- **Auditability:** Dev must document any new derived column with formula + dependencies and include it in specs/tasks.

## Impact

- Backend indicator/feature pipeline (derived columns).
- Dev prompt/validation rules in Lab run flow.
- No breaking API changes expected.
