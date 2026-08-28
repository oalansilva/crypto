## MODIFIED Requirements

### Requirement: sessionStart adapter is registered and fail-open
`.cursor/hooks.json` SHALL register a `sessionStart` command hook invoking `.cursor/hooks/process-fsm-session-start.sh`. The hook MUST emit valid JSON with `additional_context`. `failClosed` MUST NOT be true on this hook. Existing Guard (`preToolUse`, `beforeShellExecution`) and Impeccable (`afterFileEdit`, `stop`) entries MUST remain unchanged by this requirement. If Python/PyYAML fails, the adapter MUST still emit a minimal unbound page and MUST NOT dump `AGENTS.md` or the consumer overlay body (`overlay_doc`, Cripto: `docs/crypto-overlay.md`). The fallback MUST NOT hardcode `docs/crypto-overlay.md` as the product overlay path.

#### Scenario: hooks.json lists sessionStart
- **WHEN** `.cursor/hooks.json` is loaded
- **THEN** `sessionStart` invokes the process-fsm session-start adapter
- **AND** Guard and Impeccable hooks are still present as distinct entries

#### Scenario: Python missing still pages unbound
- **WHEN** the session-start adapter cannot import the paging module
- **THEN** stdout is JSON with an unbound `additional_context`
- **AND** the overlay files (`overlay_doc` and `.covenant-flow/overlay.yaml`) are not included
- **AND** the fallback does not dump `docs/crypto-overlay.md` as a hardcoded body
