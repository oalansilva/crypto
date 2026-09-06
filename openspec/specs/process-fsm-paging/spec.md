# process-fsm-paging Specification

## Purpose
Paging Moore do `sessionStart`: injeta só `context_file[q]` (≤20 linhas) e o stub unbound. Sem playbook de release.
## Requirements
### Requirement: sessionStart injects only the Moore page for q
`scripts/process-fsm/` SHALL expose a paging module that, given cwd/path and an injectable `status_provider` / `resolve_fn` / `fsm`, returns `additional_context` for the Cursor `sessionStart` hook. The page MUST include the resolved tuple `(q, bound_card, q_git)`, the verbatim `context_file[q]` stub from `.cursor/process-fsm.yaml` when `q` is a known state, and MUST NOT include the release playbook (`release-guard pre`/`post`, `subir lote`, deploy PROD). The page MUST be at most 20 lines. When `bound_card` is `⊥`, the page MUST use a fixed unbound stub that denies product Write and MUST NOT use the Homologado or release frames. When `bound_card` is issue N and `q` is missing (GraphQL quota remaining=0, RATE_LIMIT including HTTP 200, timeout, JSON failure, or empty Status nodes), the page MUST keep `bound_card=N`, MUST set `q` to missing, MUST NOT use the unbound stub, MUST NOT treat the card as off the Project, and MUST include the GraphQL reset time when the provider reports a quota error with reset. Unit tests MUST inject `status_provider` (the production path: provider result becomes `q`) and MUST NOT call GitHub, Cursor hooks, or the live Project board.

#### Scenario: Todo page omits the release playbook
- **WHEN** `page()` is invoked with injected `status_provider` returning `Todo` and a bound card on `card-<id>-*`
- **THEN** `additional_context` contains the yaml `context_file[Todo]` stub
- **AND** it does not contain `release-guard`, `subir lote`, or `deploy PROD`
- **AND** it has at most 20 lines

#### Scenario: Homologado page is still not the release playbook
- **WHEN** `page()` is invoked with injected `status_provider` returning `Homologado` and a bound card
- **THEN** `additional_context` contains the yaml `context_file[Homologado]` stub
- **AND** it does not contain `release-guard pre`, `release-guard post`, or `deploy PROD`

#### Scenario: Unbound does not load Homologado
- **WHEN** `page()` is invoked with `bound_card=⊥`
- **THEN** `additional_context` uses the unbound stub
- **AND** it does not contain the Homologado `context_file` stub nor the release playbook
- **AND** it contains `bound_card=⊥`

#### Scenario: Bound card with GraphQL quota 0 is not unbound
- **WHEN** `page()` is invoked with bound card N and the status provider fails immediately with GraphQL remaining=0 and a reset time
- **THEN** `additional_context` keeps `bound_card=N`
- **AND** it MUST NOT use the unbound stub
- **AND** it MUST NOT contain `bound_card=⊥`
- **AND** it includes the reset time
- **AND** it has at most 20 lines
- **AND** it does not contain the Homologado `context_file` stub nor the release playbook

#### Scenario: Bound card with unread Status is not unbound
- **WHEN** `page()` is invoked with bound card N and `status_provider` returning `None` without a quota reset (timeout or empty nodes)
- **THEN** `additional_context` keeps `bound_card=N`
- **AND** it MUST NOT use the unbound stub
- **AND** it MUST NOT treat the card as off the board
- **AND** it does not contain the Homologado `context_file` stub nor the release playbook

#### Scenario: Pytest without GitHub
- **WHEN** a contributor runs `pytest scripts/process-fsm -q` at the repo root
- **THEN** paging fixtures execute with injected status/resolve
- **AND** no network call to GitHub is made

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

