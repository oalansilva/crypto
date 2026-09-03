## ADDED Requirements

### Requirement: Cursor Impeccable afterFileEdit and stop are cwd-independent
`.cursor/hooks.json` SHALL keep `afterFileEdit` and `stop` as distinct Impeccable entries that invoke `.cursor/hooks/impeccable.sh` (event names `afterFileEdit` and `stop`). Those command strings MUST locate the script with the same class as the Grok JSON locator: repo-relative `.cursor/hooks/impeccable.sh`, sibling `./hooks/impeccable.sh` or `./impeccable.sh`, then `git rev-parse --show-toplevel` + `.cursor/hooks/impeccable.sh`. Running each command with cwd at the repo root, at `.cursor/`, or at `.cursor/hooks/` MUST exit 0. Cursor `preToolUse` (failClosed Write-family), `beforeShellExecution`, and `sessionStart` MUST remain the existing Guard / paging commands and MUST NOT be rewritten by this requirement. The adapter MUST still emit fail-open for the detector (a finding or crash of `hook.mjs` MUST NOT abort the turn). Dual-write of T0–T17 into `.cursor/rules/` remains forbidden.

#### Scenario: afterFileEdit resolves from three Cursor cwds
- **WHEN** the `afterFileEdit` command in `.cursor/hooks.json` runs via `sh -c` with cwd at the repo root, at `.cursor/`, and at `.cursor/hooks/`
- **THEN** each invocation exits 0
- **AND** `.cursor/hooks/impeccable.sh` is the script that runs

#### Scenario: stop resolves from three Cursor cwds
- **WHEN** the `stop` command in `.cursor/hooks.json` runs via `sh -c` with those same three cwds
- **THEN** each invocation exits 0

#### Scenario: Guard and sessionStart stay composed not replaced
- **WHEN** `.cursor/hooks.json` is loaded after this change
- **THEN** `preToolUse` command is still `.cursor/hooks/process-fsm-guard.sh` with `failClosed` true
- **AND** `beforeShellExecution` command is still `.cursor/hooks/process-fsm-guard.sh` without `failClosed` true
- **AND** `sessionStart` command is still `.cursor/hooks/process-fsm-session-start.sh`
- **AND** `afterFileEdit` and `stop` remain distinct from the Guard entries
