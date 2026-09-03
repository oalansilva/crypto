## ADDED Requirements

### Requirement: dsh paging injects the AGENTS.md stub via systemPrompt.section
`page()` SHALL remain the single compiler of the Moore page. dsh SHALL keep injecting that page through `ctx.systemPrompt.section` named `covenant-flow:moore` with order 50. The same Guard plugin SHALL also register `ctx.systemPrompt.section` named `covenant-flow:agents` with order 40 (after deployment persona order 0, before Moore order 50, before first-party tool sections at 1000). The agents section `text` MUST be a function evaluated on each assemble that returns the UTF-8 contents of `REPO_ROOT/AGENTS.md`. It MUST compile that file and MUST NOT interpolate T0–T17, I1–I9, or the 12-column runbook in plugin source. If the file is missing or unreadable, `text` MUST return an empty string (fail-open). The section MUST NOT set `complete: true`. The adapter MUST NOT use `agent/session-start` as the only delivery. Native `agent-instructions` duplication when cwd is the repo MUST be accepted. The plugin `inject` array MUST include `systemPrompt` (already) and MUST also include `skills`.

#### Scenario: dsh agents section sits before Moore
- **WHEN** the Guard plugin `apply(ctx)` runs
- **THEN** `ctx.systemPrompt.section` is called for `covenant-flow:agents` with order 40 and `text` a function
- **AND** `ctx.systemPrompt.section` is still called for `covenant-flow:moore` with order 50 and `text` a function
- **AND** `export const inject` includes `systemPrompt` and `skills`
- **AND** goldens locate those sections by `name` and `order`, not by `sections[0]`

#### Scenario: agents section compiles the stub file
- **WHEN** the agents section `text` function runs and `REPO_ROOT/AGENTS.md` exists
- **THEN** the returned string contains the stub always-on wording from that file
- **AND** it does not contain a T0–T17 table
- **AND** it does not contain `release-guard pre`

#### Scenario: missing stub file is empty not a throw
- **WHEN** the agents section `text` function runs and `REPO_ROOT/AGENTS.md` is absent
- **THEN** the returned string is empty
- **AND** plugin `apply` does not throw from that read
