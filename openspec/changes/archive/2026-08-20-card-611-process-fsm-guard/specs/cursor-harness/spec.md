## ADDED Requirements

### Requirement: Cursor hooks.json registers the compiled Write Guard
`.cursor/hooks.json` SHALL register a `preToolUse` command hook whose matcher covers `Write`, `StrReplace`, `Delete`, and `EditNotebook`, invoking the process-fsm Guard adapter. The same adapter SHALL be registered on `beforeShellExecution` for mutating shell writes. `failClosed` MUST be `true` on the `preToolUse` Write-family hook and MUST NOT be `true` on `beforeShellExecution`. Existing Impeccable hooks (`afterFileEdit` and `stop` calling `.cursor/hooks/impeccable.sh`) MUST remain. The adapter MUST emit valid JSON even if Python/PyYAML fails (bash fallback: deny `product_globs`, allow `design_globs` on `card-<id>-*`).

#### Scenario: Write tools are guarded
- **WHEN** a Cursor Agent issues `Write` or `StrReplace` on a product path
- **THEN** `.cursor/hooks.json` runs the process-fsm Guard before the tool executes

#### Scenario: Impeccable is composed not replaced
- **WHEN** `.cursor/hooks.json` is loaded
- **THEN** `afterFileEdit` and `stop` still invoke `.cursor/hooks/impeccable.sh`
- **AND** the Guard command is a distinct entry from the Impeccable adapter

#### Scenario: Shell mutating writes use the same Guard
- **WHEN** `.cursor/hooks.json` is loaded
- **THEN** `beforeShellExecution` invokes the same Guard adapter as `preToolUse`
- **AND** `failClosed` is not true on that shell hook
