## ADDED Requirements

### Requirement: Antigravity skill stubs discover canonical skills with zero dual-write
The repository SHALL provide lightweight skill stubs under `.agents/skills/` for all canonical skills defined in `.cursor/skills/`. Each stub SHALL include canonical frontmatter (`name`, `description`) extracted from the canonical source and an operational directive requiring the Antigravity CLI agent to read `.cursor/skills/<name>/SKILL.md` as the authoritative runbook. The stub generator and validator in `scripts/process-fsm/antigravity_stubs.py` SHALL verify stub presence, content freshness, body length (<= 8 non-empty lines), pointer presence, and absence of full runbook duplication. Local canonical skills in `.agents/skills/` (`impeccable`, `playwright-cli`) SHALL NOT be overwritten by stubs.

#### Scenario: Stubs are generated for canonical skills
- **WHEN** `antigravity_stubs.write_stubs()` is executed
- **THEN** a stub `SKILL.md` SHALL be created under `.agents/skills/<name>/SKILL.md` for each canonical skill in `.cursor/skills/`
- **AND** the stub body SHALL contain an explicit directive requiring the agent to read `.cursor/skills/<name>/SKILL.md`
- **AND** the non-empty body lines of each generated stub SHALL NOT exceed 8 lines

#### Scenario: Local canonical skills under .agents/skills are preserved
- **WHEN** stubs are generated or validated
- **THEN** `.agents/skills/impeccable/SKILL.md` and `.agents/skills/playwright-cli/SKILL.md` SHALL remain intact as local canonical files
- **AND** `stub_errors()` SHALL NOT report errors for those canonical skills

#### Scenario: Stub validator reports missing, stale, or oversized stubs
- **WHEN** any generated stub is missing from `.agents/skills/`, diverges from expected content, exceeds 8 body lines, or lacks the pointer to the canonical runbook
- **THEN** `antigravity_stubs.stub_errors()` SHALL return a list describing each defect

### Requirement: PreToolUse hook intercepts mutation and shell execution tools
The repository SHALL configure `.agents/hooks.json` to register an `fsm-guard` hook for the `PreToolUse` event with a matcher pattern matching `write_to_file`, `replace_file_content`, and `run_command`. The hook handler SHALL invoke `scripts/process-fsm/antigravity_guard.py` to evaluate the pending tool call against the Covenant Flow Write Guard before execution.

#### Scenario: Hook configuration registers PreToolUse handler
- **WHEN** `.agents/hooks.json` is loaded by the Antigravity CLI
- **THEN** it SHALL define the top-level hook `fsm-guard`
- **AND** it SHALL configure `PreToolUse` with matcher `write_to_file|replace_file_content|run_command`
- **AND** it SHALL invoke `scripts/process-fsm/antigravity_guard.py`

#### Scenario: PreToolUse hook returns allow or deny decision
- **WHEN** `antigravity_guard.py` receives a valid JSON tool call payload on stdin
- **THEN** it SHALL output a JSON object on stdout containing `decision` (`allow` or `deny`) and `reason`
- **AND** it SHALL terminate with exit code 0

#### Scenario: Fail-closed on invalid JSON or unexpected runtime error
- **WHEN** `antigravity_guard.py` receives malformed input or encounters an unexpected exception
- **THEN** it SHALL output `{"decision": "deny", "reason": "..."}`
- **AND** it SHALL terminate with exit code 0 to reliably block tool execution

### Requirement: Write Guard supports Antigravity tool names and argument signatures
The Write Guard (`scripts/process-fsm/guard.py`) SHALL treat `write_to_file` and `replace_file_content` as write tools in `WRITE_TOOLS`, and `run_command` as a shell execution tool in `SHELL_TOOLS`. Path extraction SHALL recognize `TargetFile` and `targetFile`, and payload normalization SHALL extract the shell command string from `CommandLine`.

#### Scenario: Write tools recognized by guard
- **WHEN** a tool call payload with tool name `write_to_file` or `replace_file_content` is evaluated
- **THEN** `guard.py` SHALL classify the operation as a file write subject to product path gating

#### Scenario: Shell tool recognized by guard
- **WHEN** a tool call payload with tool name `run_command` is evaluated
- **THEN** `guard.py` SHALL classify the operation as a shell execution subject to redirect and mutation checks

#### Scenario: Argument normalization for TargetFile and CommandLine
- **WHEN** a payload contains `TargetFile` or `targetFile` in its arguments
- **THEN** `extract_path()` SHALL extract the target file path
- **AND** WHEN a payload contains `CommandLine` in its arguments
- **THEN** `normalize()` SHALL set `command` to the specified command string

#### Scenario: Product write denied in Todo and Design states
- **WHEN** an Antigravity tool call attempts to write or replace content in a product file (`backend/**` or `frontend/src/**`) while the card status is `Todo` or `Design`
- **THEN** `guard.py` and `antigravity_guard.py` SHALL return `decision: "deny"`

#### Scenario: Dangerous shell mutations denied
- **WHEN** an Antigravity `run_command` attempts a file redirect (`>`) or `tee` targeting a product file
- **THEN** `guard.py` and `antigravity_guard.py` SHALL return `decision: "deny"`

#### Scenario: Product write permitted in Pronto para Dev
- **WHEN** an Antigravity tool call attempts to write to a product file on the card branch while status is `Pronto para Dev`
- **THEN** `guard.py` and `antigravity_guard.py` SHALL return `decision: "allow"`

#### Scenario: Design changes permitted during Design state
- **WHEN** an Antigravity tool call writes to `openspec/changes/` or `frontend/public/prototypes/` while the card is on its branch in `Design`
- **THEN** `guard.py` and `antigravity_guard.py` SHALL return `decision: "allow"`

### Requirement: Antigravity CLI is cataloged as a cooperative client in AGENTS.md
The project instructions in `AGENTS.md` SHALL explicitly document `Antigravity CLI (agy)` alongside Cursor Agent, Grok Build, OpenCode, and dsh as cooperative clients, and prohibit claiming Auto mode in `agy`.

#### Scenario: Client list includes Antigravity CLI
- **WHEN** `AGENTS.md` is inspected
- **THEN** it SHALL enumerate `Antigravity CLI (agy)` among the cooperative clients
- **AND** it SHALL explicitly forbid claiming Auto mode in `agy`

### Requirement: Adapter test suite verifies all Antigravity integration points
The test suite `scripts/process-fsm/test_antigravity_adapter.py` SHALL validate stub synchronization, guard blocking in non-dev states, shell mutation prohibitions, dev state permissions, and adapter command-line invocation.

#### Scenario: Antigravity adapter test suite passes completely
- **WHEN** `pytest scripts/process-fsm/test_antigravity_adapter.py` is executed
- **THEN** all test cases SHALL pass with 0 errors and 0 failures
- **AND** full `pytest scripts/process-fsm` SHALL pass with no regressions
