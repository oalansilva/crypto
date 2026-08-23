## ADDED Requirements

### Requirement: Grok paging is a generated Moore file not SessionStart stdout
`page()` SHALL remain the single compiler of the Moore page from `.cursor/process-fsm.yaml` `context_file[q]`. Cursor SHALL keep injecting that page via `sessionStart` stdout `additional_context`. Grok `SessionStart` MUST NOT depend on stdout (the product ignores it). The Grok adapter SHALL write the same page body to `.grok/rules/process-fsm-page.md` as a SessionStart side effect. That generated file MUST be gitignored (Grok skips gitignored files in rules discovery, so it is NOT auto-injected always-on). A committed static `.grok/rules/00-harness.md` MUST tell the agent that always-on δ is `AGENTS.md` and MUST instruct the agent to Read `.grok/rules/process-fsm-page.md` when the file exists and treat it as the Moore page. `00-harness.md` MUST NOT copy columns or I1–I9. The generated page MUST be at most 20 lines, MUST include `(q, bound_card, q_git)` and the yaml stub, and MUST NOT include the release playbook. If the generated file is missing this turn, the Guard still live-resolves `q` (missing or gitignored page is not an allow token). Homologation paging is: agent follows `00-harness.md` and Reads the generated file; it is not a claim of auto-injection.

#### Scenario: Grok SessionStart writes the page file
- **WHEN** the Grok SessionStart adapter runs in a bound worktree with injected `status_provider` returning `Todo`
- **THEN** `.grok/rules/process-fsm-page.md` is written
- **AND** its contents contain the yaml `context_file[Todo]` stub
- **AND** it does not contain `release-guard`, `subir lote`, or `deploy PROD`
- **AND** it has at most 20 lines

#### Scenario: Generated page is gitignored
- **WHEN** `.gitignore` is inspected
- **THEN** `.grok/rules/process-fsm-page.md` is ignored
- **AND** `.grok/rules/00-harness.md` is not ignored

#### Scenario: 00-harness instructs Read of the generated page
- **WHEN** `.grok/rules/00-harness.md` is read
- **THEN** it tells the agent to Read `.grok/rules/process-fsm-page.md` when present
- **AND** it does not contain a T0–T17 table or I1–I9 list

#### Scenario: Missing page does not allow product writes
- **WHEN** `.grok/rules/process-fsm-page.md` is absent and a Grok `write` targets `backend/` with `q_git=develop`
- **THEN** the Guard still returns `decision: deny`

#### Scenario: Cursor sessionStart is unchanged in shape
- **WHEN** the Cursor `sessionStart` adapter runs
- **THEN** stdout is JSON with `additional_context`
- **AND** `failClosed` is not true on that hook
