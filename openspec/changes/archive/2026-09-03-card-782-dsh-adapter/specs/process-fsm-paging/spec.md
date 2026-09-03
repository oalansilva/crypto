## ADDED Requirements

### Requirement: dsh paging injects the Moore page via systemPrompt.section
`page()` SHALL remain the single compiler of the Moore page from `.cursor/process-fsm.yaml` `context_file[q]`. Cursor SHALL keep injecting that page via `sessionStart` stdout `additional_context`. Grok SHALL keep writing the generated gitignored `.grok/rules/process-fsm-page.md` plus MUST Read in `00-harness.md`. OpenCode 1.18.18 SHALL keep injecting through `experimental.chat.system.transform`. dsh SHALL inject the same page body through Cordis `ctx.systemPrompt.section` whose `text` is a function evaluated on each assemble (section name `covenant-flow:moore`). The hook MUST supply the same text Cursor would put in `additional_context`. The dsh adapter MUST NOT version a gitignored Moore file plus a MUST Read hop. The dsh adapter MUST NOT rely on `agent/session-start` + `inject` as the only delivery (that seam can miss the first request). The injected page MUST be at most 20 lines, MUST include `(q, bound_card, q_git)` and the yaml stub, and MUST NOT include the release playbook. If the plugin is not loaded this turn, the Guard still live-resolves `q` (missing inject is not an allow token). Homologation paging is: the session system text contains the Moore page; it is not a playbook of release.

#### Scenario: dsh section injects the Todo page
- **WHEN** the dsh paging section runs in a bound worktree with injected `status_provider` returning `Todo`
- **THEN** `ctx.systemPrompt.section` `covenant-flow:moore` receives the `page()` body
- **AND** that body contains the yaml `context_file[Todo]` stub
- **AND** it does not contain `release-guard`, `subir lote`, or `deploy PROD`
- **AND** it has at most 20 lines

#### Scenario: dsh does not use the Grok gitignored hop
- **WHEN** the dsh adapter is inspected
- **THEN** it does not instruct MUST Read of a gitignored Moore file as the paging delivery
- **AND** there is no second copy of T0–T17 under `.dsh/`

#### Scenario: Missing dsh inject does not allow product writes
- **WHEN** the dsh plugin is not loaded and a native `edit` targets `backend/` with `q_git=develop`
- **THEN** if the Guard plugin were loaded it would still deny
- **AND** homologation records whether the plugin actually loaded (unloaded plugin is residual allow, same class as Grok without trust)
