## ADDED Requirements

### Requirement: dsh always-on stub is ingested when session cwd is not the consumer git root
The short always-on law SHALL remain the consumer root `AGENTS.md` file (compile the file; adapters MUST NOT copy T0–T17 into `.dsh/` or `cordis.yml`). The dsh Guard plugin SHALL inject that file's text through Cordis `ctx.systemPrompt.section` even when the session cwd is not the consumer git root (homologation replay: session `306d48f7-d893-471e-ba4c-8fe7a5153fda`, cwd `/home/ubuntu`). The plugin SHALL resolve the file from adapter `REPO_ROOT` (the git tree that contains `.dsh/plugin/process-fsm-guard.js`), not from `process.cwd()` or `session.header.cwd`. Native `agent-instructions` MAY still load `AGENTS.md` when cwd *is* the repo; that duplication MUST be accepted. The native loader MUST NOT be disabled. Missing or unreadable `AGENTS.md` MUST yield empty section text (fail-open), matching Moore's empty page body. The Guard deny path MUST remain fail-closed. `AGENTS.md` MUST still name Cursor Agent, Grok Build, OpenCode, and dsh, MUST NOT claim Auto dsh, and MUST remain at most 40 non-empty lines. Auto dsh MUST stay gated on a deny essay; this requirement's human essay is the first-request dump containing stub text, not a `skill` tool call.

#### Scenario: Four-client always-on with dsh session cwd not the consumer git
- **WHEN** a Cursor session, a Grok session, and an OpenCode session start in the consumer repo **and** a dsh session starts with session cwd ≠ the consumer git root, plugin loaded via the versioned `--patch` helper, preset `standard`
- **THEN** Cursor, Grok, and OpenCode still ingest root `AGENTS.md` by their existing loaders
- **AND** the dsh first-request system/prompt dump contains the consumer `AGENTS.md` stub text (always-on δ: chat wording is not δ, `Todo` is not implementation)
- **AND** that dump does not contain a T0–T17 table copied into `.dsh/`
- **AND** docs still MUST NOT claim dsh Auto is active

#### Scenario: Replay 306d48f7 injects the stub
- **WHEN** dsh starts as in session `306d48f7-d893-471e-ba4c-8fe7a5153fda` (cwd is not the consumer git, preset `standard`, Guard plugin loaded)
- **THEN** the first-request dump contains the stub file text
- **AND** Moore paging from `covenant-flow:moore` remains present
- **AND** Guard deny of illegal product writes still holds

#### Scenario: Missing AGENTS.md does not fail-open the Guard
- **WHEN** `AGENTS.md` is missing at `REPO_ROOT` and a dsh `write` targets `backend/` with `q_git=develop`
- **THEN** the agents section text is empty
- **AND** if the Guard plugin is loaded it still returns `{ kind: 'deny' }`

### Requirement: dsh process skill catalog is published from the Guard plugin provider
The dsh Guard plugin SHALL publish the process skill catalog from `REPO_ROOT/.dsh/skills` through `ctx.skills.registerProvider` so `dsh-tool-skill` can render `<available_skills>` even when session cwd is not the consumer git root. The provider MUST scan that directory (one level, `<name>/SKILL.md`) regardless of lookup `cwd`. `list(options)` and `get(candidate, options)` MUST return a Promise (thenable). `get` MUST accept the `SkillCandidate` returned by `list`, not a skill name string. Every candidate MUST set `provider` to the provider's `name` (`covenant-flow-process`), plus kebab `name`, non-empty `description`, string `source`, finite `rank`, and boolean `invocation.modelInvocable` / `userInvocable`. A missing skills directory MUST resolve to an empty list (not throw). Invalid frontmatter MUST be skipped in `list`, not thrown. Skill paths MUST NOT appear in `.dsh/cordis.patch.yml`. The host composition row `id: skill-filesystem` that is `disabled: true` MUST NOT be edited by this change. The preset-mounted native `skill-filesystem` MUST remain enabled. Duplicate catalog entries when cwd=repo MUST be accepted. Stubs under `.dsh/skills/` remain bridges (body at most 8 non-empty lines after frontmatter, MUST Read canonical `.cursor/skills/<name>/SKILL.md`, no T0–T17). Human essay for this catalog is first-request `<available_skills>` containing `covenant-flow`; invoking the `skill` tool is not the DoD. Preset `minimal` is out of scope. Unit goldens MUST exercise `list`/`get` through a thenable+`signal` path equivalent to live `waitWithAbort` and `validateCandidate` (not only a synchronous `list()` without `signal`).

#### Scenario: available_skills lists covenant-flow when cwd is not the repo
- **WHEN** a dsh session uses preset `standard`, plugin loaded, session cwd ≠ consumer git root
- **THEN** the first-request dump contains an `<available_skills>` block
- **AND** that block includes `covenant-flow`
- **AND** `.dsh/cordis.patch.yml` does not list `.dsh/skills` or `customSkillDirs`

#### Scenario: Plugin provider lists from REPO_ROOT not session cwd
- **WHEN** the plugin skill provider `list()` runs with lookup `cwd` equal to the user home directory
- **THEN** candidates include `covenant-flow` whose path is under the consumer `REPO_ROOT/.dsh/skills`
- **AND** the provider name is not `filesystem` and is not `runtime`

#### Scenario: Provider thenables survive signal and validateCandidate
- **WHEN** a unit golden calls `list({ cwd, signal })` and `get(candidate, { signal })` with a non-aborted `AbortSignal`
- **THEN** both calls return thenables that fulfill (they MUST NOT return a bare array)
- **AND** each listed candidate has `provider` equal to `"covenant-flow-process"`
- **AND** `validateCandidate` equivalent checks do not throw
- **AND** `get` returns a definition whose `content` is a string and whose `name` matches the candidate

#### Scenario: Native filesystem loader stays
- **WHEN** a reviewer inspects the dsh adapter and the host patch this change ships
- **THEN** the adapter does not disable native project skill discovery
- **AND** it does not change host row `skill-filesystem` from `disabled: true`
