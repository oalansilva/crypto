## ADDED Requirements

### Requirement: OpenCode paging injects the Moore page via system.transform
`page()` SHALL remain the single compiler of the Moore page from `.cursor/process-fsm.yaml` `context_file[q]`. Cursor SHALL keep injecting that page via `sessionStart` stdout `additional_context`. Grok SHALL keep writing the generated gitignored `.grok/rules/process-fsm-page.md` plus MUST Read in `00-harness.md`. OpenCode 1.18.18 SHALL inject the same page body through the plugin hook `experimental.chat.system.transform` (name observed on the 1.18.18 binary: `plugin.trigger("experimental.chat.system.transform", {sessionID, model}, {system})`). The hook MUST `output.system.push` (or equivalent merge into `system[]`) the same text Cursor would put in `additional_context`. The OpenCode adapter MUST NOT version a gitignored Moore file plus a MUST Read hop. The injected page MUST be at most 20 lines, MUST include `(q, bound_card, q_git)` and the yaml stub, and MUST NOT include the release playbook. If the plugin is not loaded this turn, the Guard still live-resolves `q` (missing inject is not an allow token). Homologation paging is: the session system text contains the Moore page; it is not a playbook of release.

#### Scenario: OpenCode transform injects the Todo page
- **WHEN** the OpenCode paging hook runs in a bound worktree with injected `status_provider` returning `Todo`
- **THEN** `experimental.chat.system.transform` receives the `page()` body
- **AND** that body contains the yaml `context_file[Todo]` stub
- **AND** it does not contain `release-guard`, `subir lote`, or `deploy PROD`
- **AND** it has at most 20 lines

#### Scenario: OpenCode does not use the Grok gitignored hop
- **WHEN** the OpenCode adapter is inspected
- **THEN** it does not instruct MUST Read of a gitignored Moore file as the paging delivery
- **AND** there is no second copy of T0–T17 under `.opencode/`

#### Scenario: Missing OpenCode inject does not allow product writes
- **WHEN** the OpenCode plugin is not loaded and a native `edit` targets `backend/` with `q_git=develop`
- **THEN** if the Guard plugin were loaded it would still deny
- **AND** homologation records whether the plugin actually loaded (unloaded plugin is residual allow, same class as Grok without trust)
