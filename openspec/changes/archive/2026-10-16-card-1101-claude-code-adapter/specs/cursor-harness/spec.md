## MODIFIED Requirements

### Requirement: Cursor hooks.json registers the compiled Write Guard
The Cursor `hooks.json` of the operator account (`~/.cursor/hooks.json`), installed through the `account-hook-shim`, SHALL register a `preToolUse` command hook whose matcher covers `Write`, `StrReplace`, `Delete`, and `EditNotebook`, invoking, through the shim, the process-fsm Guard adapter pinned in the bound consumer (`.cursor/hooks/process-fsm-guard.sh`). The same adapter SHALL be registered on `beforeShellExecution` for mutating shell writes. `failClosed` MUST be `true` on the `preToolUse` Write-family hook and MUST NOT be `true` on `beforeShellExecution`. Existing Impeccable hooks (`afterFileEdit` and `stop` calling `.cursor/hooks/impeccable.sh`) MUST remain. The project `.cursor/hooks.json` SHALL carry these entries only on pins older than account registration; if the rehearsal does not prove Cursor's global mechanism, Cursor follows the `account-hook-shim` rule for hosts reported as `registration=unproven`. The adapter MUST emit valid JSON even if Python/PyYAML fails (bash fallback: deny `product_globs`, allow `design_globs` on `card-<id>-*`).

#### Scenario: Write tools are guarded
- **WHEN** a Cursor Agent issues `Write` or `StrReplace` on a product path
- **THEN** the account `hooks.json` runs, through the shim, the process-fsm Guard pinned in the consumer before the tool executes

#### Scenario: Impeccable is composed not replaced
- **WHEN** the Cursor `hooks.json` that registers the process is loaded
- **THEN** `afterFileEdit` and `stop` still invoke `.cursor/hooks/impeccable.sh`
- **AND** the Guard command is a distinct entry from the Impeccable adapter

#### Scenario: Shell mutating writes use the same Guard
- **WHEN** the Cursor `hooks.json` that registers the process is loaded
- **THEN** `beforeShellExecution` invokes the same Guard adapter as `preToolUse`
- **AND** `failClosed` is not true on that shell hook
