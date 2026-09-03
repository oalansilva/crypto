## ADDED Requirements

### Requirement: Grok PreToolUse Guard command is cwd-independent
The Grok write-block Guard SHALL remain the compiled `decide()` adapter invoked by `.grok/hooks/process-fsm-guard.sh` (thin wrapper onto the Cursor Guard script). The `PreToolUse` command strings in `.grok/hooks/process-fsm.json` MUST locate that script with the same repo-relative + sibling + git-toplevel chain used for PostToolUse: `.grok/hooks/process-fsm-guard.sh`, then `./process-fsm-guard.sh`, then `$root/.grok/hooks/process-fsm-guard.sh` where `$root` is `git rev-parse --show-toplevel`. Running that command with cwd at the repo root, at `.grok/hooks/`, or at `frontend/` MUST exit 0 and MUST NOT exit 127 `not found`. SessionStart MUST use the same locator class for `.grok/hooks/process-fsm-session-start.sh` so the Moore page write is not muted when cwd is the repo root. This requirement MUST NOT change `scripts/process-fsm/guard.py` `decide()`, envelopes, fail-closed product writes, Cursor Guard commands, or the dsh Guard plugin. Dual-write of T0–T17 remains forbidden.

#### Scenario: Grok PreToolUse finds the Guard from three cwds
- **WHEN** a Grok `PreToolUse` command from `.grok/hooks/process-fsm.json` runs via `sh -c` with cwd at the repo root, at `.grok/hooks/`, and at `frontend/`
- **THEN** each invocation exits 0
- **AND** none exits 127 because `./process-fsm-guard.sh` was not in the cwd

#### Scenario: Grok SessionStart finds the paging adapter from three cwds
- **WHEN** the Grok `SessionStart` command from `.grok/hooks/process-fsm.json` runs via `sh -c` with those same three cwds
- **THEN** each invocation exits 0

#### Scenario: decide() and Cursor/dsh Guards stay out of this card
- **WHEN** a reviewer inspects the diff of this change
- **THEN** `scripts/process-fsm/guard.py` is not required to change for the locator
- **AND** `.cursor/hooks.json` `preToolUse` / `beforeShellExecution` remain `.cursor/hooks/process-fsm-guard.sh`
- **AND** `.dsh/plugin/process-fsm-guard.js` is not required to change for this locator
