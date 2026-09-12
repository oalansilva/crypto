# developer-tooling Specification

## Purpose
Configuração versionada da ferramenta de desenvolvimento ativa (Cursor Agent, Grok Build, OpenCode 1.18.18) e skills/commands OpenSpec, Impeccable e Kaizen.
## Requirements
### Requirement: Configuração versionada de ferramenta de desenvolvimento
O repositório SHALL conter configuração versionada do Cursor Agent em `.cursor/` (rules, skills, commands, hooks), do Grok Build em `.grok/`, do adapter OpenCode 1.18.18 em `.opencode/plugin/` (auto-load), e do adapter dsh em `.dsh/plugin/` (Cordis `apply(ctx)` + `.dsh/cordis.patch.yml`). `opencode.json` MUST NOT permanecer como contrato ativo de modelo, MCP ou permission. `.opencode/plugins/` MUST NOT ser versionado em paralelo com `.opencode/plugin/`. Lock machine, `opencode.db` no kaizen, lease e attestation continuam proibidos. A ponte Claude `hooks.json` MUST NOT ser o Guard dsh.

#### Scenario: Config presente e válida
- **WHEN** o Cursor Agent inicia no repo
- **THEN** a configuração versionada em `.cursor/` é carregada
- **AND** nenhuma instrução Cursor aponta para `opencode.json` como fonte obrigatória de modelo/MCP/permission

#### Scenario: OpenCode plugin auto-load
- **WHEN** o OpenCode 1.18.18 inicia no repo
- **THEN** os módulos em `.opencode/plugin/` carregam sem `opencode.json`

#### Scenario: Sem segredos no repo
- **WHEN** a configuração versionada é inspecionada
- **THEN** nenhum token, chave ou credencial está presente nos arquivos versionados

### Requirement: Skills e fluxo OpenSpec disponíveis no Cursor
O Cursor SHALL carregar as skills do projeto (OpenSpec `/opsx-*`, design-critic, impeccable, playwright-cli, kaizen, `covenant-flow`, `covenant-flow-environments`, `implantar`) a partir de `.cursor/skills/`, `.cursor/commands/` e `.agents/skills/`, sem duplicar o conteúdo canônico das skills de produto.

#### Scenario: Skills carregadas automaticamente
- **WHEN** o Cursor inicia no repo pinado
- **THEN** as skills `openspec-*`, `design-critic`, `impeccable`, `playwright-cli`, `kaizen`, `covenant-flow`, `covenant-flow-environments` e `implantar` estão disponíveis

#### Scenario: Commands opsx disponíveis
- **WHEN** o usuário invoca `/opsx-new`, `/opsx-ff`, `/opsx-apply`, `/opsx-verify`, `/opsx-archive` ou equivalentes
- **THEN** o command em `.cursor/commands/` executa o fluxo OpenSpec via CLI

### Requirement: Proteção de design system na edição de UI
Edições de arquivos de UI em Cursor, Grok Build, OpenCode 1.18.18 e dsh SHALL acionar a detecção Impeccable no mesmo `.agents/skills/impeccable/scripts/hook.mjs` sem quebrar o turno. A pele só traduz o evento nativo. Não é um segundo detector.

#### Scenario: Hook de UI dispara na edição Cursor
- **WHEN** um arquivo de frontend é editado pelo Cursor
- **THEN** o hook em `.cursor/hooks.json` roda `.agents/skills/impeccable/scripts/hook.mjs` e reporta achados sem interromper a sessão

#### Scenario: Hook de UI dispara na edição Grok
- **WHEN** um arquivo de frontend é editado pelo Grok Build
- **THEN** `PostToolUse` / `Stop` em `.grok/hooks/` rodam o mesmo `hook.mjs` e reportam achados sem interromper a sessão

#### Scenario: Hook de UI dispara na edição OpenCode
- **WHEN** um arquivo de frontend é editado pelo OpenCode 1.18.18
- **THEN** `tool.execute.after` / `session.idle` no plugin rodam o mesmo `hook.mjs` e reportam achados sem interromper a sessão
- **AND** `tool.execute.after` mapeia `args.filePath` para `file_path` no stdin de `hook.mjs` com `hook_event_name=PostToolUse`
- **AND** `session.idle` mapeia `hook_event_name=Stop`

### Requirement: Subagent kaizen e command disponíveis
O Cursor SHALL expor o command `/kaizen` e um fluxo de auditoria read-only equivalente ao subagent kaizen.

#### Scenario: Command kaizen carregado
- **WHEN** o Cursor inicia no repo
- **THEN** `/kaizen` (e modos `card`/`release`) está disponível

#### Scenario: Auditoria sem mutação
- **WHEN** a auditoria kaizen é usada
- **THEN** ela não edita arquivos de produto, não altera board/Git/PRs e não reinicia serviços

### Requirement: Global environments skill is part of developer tooling
Developer tooling SHALL keep `covenant-flow-environments` aligned with overlay `environments.*`. A stale OpenClaw gateway map is a tooling defect, not an acceptable default. Packaged skill text MUST NOT hardcode Cripto unit names as the only topology; those values live in the consumer overlay.

#### Scenario: Skill content is audited
- **WHEN** the environments skill is reviewed
- **THEN** it does not list `openclaw-gateway.service` as an active service
- **AND** it reads Hermes and Cripto/Clara DEV/PROD units from overlay when present
- **AND** a project without `environments.prod` is treated as DEV-only

### Requirement: OpenSpec apply skill loads the approved prototype for UI cards
The `/opsx:apply` skill SHALL include a mandatory step for `UI impact: affected`: read `design.md` and the approved HTML prototype before editing product UI files. API specs remain integration contracts only.

#### Scenario: Apply skill lists the prototype step
- **WHEN** an agent runs `/opsx:apply` on a UI-affected change
- **THEN** the skill instructs loading `frontend/public/prototypes/<slug>/` before coding UI

### Requirement: Versioned local reviewer subagents exist
The repository SHALL contain `.cursor/agents/diff-reviewer.md` and `.cursor/agents/code-reviewer.md`, each with `readonly: true` and `model: composer-2.5`. The YAML `model` is a redundant pin; the law is the Task `model` parameter of the spawn. Neither file SHALL declare `model: inherit`.

#### Scenario: Reviewer files are versioned
- **WHEN** a Cursor Agent session starts in the repo
- **THEN** both agent files are available for delegation during Code Review
- **AND** each MUST declare `readonly: true` and `model: composer-2.5`
- **AND** neither MUST declare `model: inherit`

### Requirement: Review stance lives in local reviewer agents
The repository SHALL contain `.cursor/agents/diff-reviewer.md` and `.cursor/agents/code-reviewer.md`, each with `readonly: true` and `model: composer-2.5`, and those files SHALL carry review constraints (Design/`Pronto para Dev` not skippable, no secrets in commits, consumer overlay `runtime.database` when present, tests when backend changes, Playwright visual when UI changes). `REVIEW.md` MAY exist and MUST NOT mention Bugbot. `BUGBOT.md` MUST NOT exist. Cursor Bugbot MUST NOT be the Code Review path.

#### Scenario: Reviewer files carry the stance
- **WHEN** a local `diff-reviewer` run starts
- **THEN** `.cursor/agents/diff-reviewer.md` exists and encodes the review constraints
- **AND** `.cursor/BUGBOT.md` does not exist

#### Scenario: Nested BUGBOT.md is gone
- **WHEN** the reviewed diff includes `backend/` or `frontend/` files
- **THEN** no nested `BUGBOT.md` is required
- **AND** the same agent files apply

### Requirement: Consumer git commits materialized harness skins
A pinned consumer SHALL keep `.cursor/`, `.grok/`, `.opencode/`, `scripts/process-fsm/`, `.agents/skills/` (impeccable, design-critic, playwright-cli), and generated `AGENTS.md` as committed trees produced by `implantar --pin`. Those paths MUST NOT be gitignored as the install method and MUST NOT be a submodule as the v1 channel.

#### Scenario: Pinned consumer shows skins in git
- **WHEN** Cripto is pinned in the card worktree
- **THEN** `git ls-files` includes `.cursor/hooks.json`, `.grok/` adapter files, `.opencode/plugin/`, `scripts/process-fsm/`, `.agents/skills/impeccable/`, and `AGENTS.md`
- **AND** overlay `.covenant-flow/overlay.yaml` contains `pin` matching the product tag

### Requirement: Versioned hook commands find Impeccable adapters off the JSON directory
Versioned developer-tooling skins SHALL invoke the same `.agents/skills/impeccable/scripts/hook.mjs` when the client working directory is the repo root, the JSON/plugin directory, or another directory inside the consumer git. Grok commands in `.grok/hooks/process-fsm.json` MUST NOT be a bare `./impeccable.sh` / `./process-fsm-*.sh` that only works when cwd is `.grok/hooks/`. Cursor `.cursor/hooks.json` `afterFileEdit` / `stop` MUST NOT be a path that only works when cwd is the repo root. dsh `.dsh/plugin/impeccable-hook.js` MUST resolve the consumer git (or `REPO_ROOT`) instead of trusting a filled-in `process.cwd()`. OpenCode `.opencode/plugin/impeccable-hook.js` MUST harden `input.directory || input.worktree || REPO_ROOT` so cwd `$HOME` does not miss `hook.mjs`. The pele only translates the native event. This is not a second detector. `git ls-files` of the four skins MUST still include those adapter files. Cursor Guard / dsh Guard / `hook.mjs` internals stay out of this requirement.

#### Scenario: Grok JSON no longer depends on JSON-dir cwd
- **WHEN** `.grok/hooks/process-fsm.json` is loaded
- **THEN** `PostToolUse` and `Stop` command strings contain `.grok/hooks/impeccable.sh` and a `test -f` of that repo-relative path
- **AND** they still mention `./impeccable.sh` as the sibling fallback
- **AND** they mention `git rev-parse --show-toplevel`
- **AND** `PreToolUse` and `SessionStart` use the same locator class for `process-fsm-guard.sh` and `process-fsm-session-start.sh`

#### Scenario: Cursor hooks.json Impeccable is the same locator class
- **WHEN** `.cursor/hooks.json` is loaded
- **THEN** `afterFileEdit` and `stop` command strings contain `.cursor/hooks/impeccable.sh` and a `test -f` of that repo-relative path
- **AND** they mention `git rev-parse --show-toplevel`
- **AND** `preToolUse` / `beforeShellExecution` remain `.cursor/hooks/process-fsm-guard.sh`
- **AND** `sessionStart` remains `.cursor/hooks/process-fsm-session-start.sh`

#### Scenario: dsh plugin exports resolveRepoCwd
- **WHEN** `scripts/process-fsm/dsh_plugin_lib.js` and `.dsh/plugin/impeccable-hook.js` are inspected
- **THEN** the lib exports `resolveRepoCwd`
- **AND** the plugin calls `resolveRepoCwd(process.cwd())` as the detector cwd
- **AND** the plugin does not contain `process.cwd() || REPO_ROOT`

#### Scenario: OpenCode plugin does not take $HOME as detector root
- **WHEN** `.opencode/plugin/impeccable-hook.js` loads with `directory` `$HOME`
- **THEN** `runHookMjs` receives the consumer git toplevel or `REPO_ROOT`, not `$HOME`
- **AND** `hook.mjs` exists at `.agents/skills/impeccable/scripts/hook.mjs` relative to that root

#### Scenario: UI edit still fail-open on four clients
- **WHEN** a frontend file is edited in Cursor, Grok, OpenCode 1.18.18, or dsh
- **THEN** the same `hook.mjs` is the detector
- **AND** a detector finding does not abort the session

### Requirement: dsh boot fails closed when canonical_paths.dev is set and is not a directory
`scripts/process-fsm/dsh_boot.sh` SHALL still prefer overlay `canonical_paths.dev` as `LAUNCH_DIR` when that value is a non-empty path **and** that path is an existing directory (then `dsh web --patch` from there). When the overlay key is missing or empty, `LAUNCH_DIR` MUST be `REPO_ROOT`. When the key is non-empty and the path is **not** a directory, the helper MUST exit non-zero and MUST print the path in the error message. The boot helper MUST NOT set the dsh GUI session workspace/cwd; always-on ingest MUST remain the Guard plugin's responsibility. `dsh plugin add` remains not the v1 pin channel. Absolute plugin `name`s in the materialized patch are unchanged.

#### Scenario: Empty canonical_paths.dev launches from REPO_ROOT
- **WHEN** overlay `canonical_paths.dev` is absent or an empty string and `dsh_boot.sh` runs
- **THEN** `LAUNCH_DIR` is the consumer `REPO_ROOT`
- **AND** the process does not exit solely because the key is empty

#### Scenario: Non-directory canonical_paths.dev fails
- **WHEN** overlay `canonical_paths.dev` is a non-empty path that does not exist or is not a directory
- **THEN** `dsh_boot.sh` exits with status ≠ 0
- **AND** stderr names that path

#### Scenario: Directory canonical_paths.dev still preferred
- **WHEN** overlay `canonical_paths.dev` is an existing directory
- **THEN** `LAUNCH_DIR` is that directory
- **AND** `dsh web --patch` is still invoked with absolute plugin names

### Requirement: dsh developer tooling publishes process skills from the plugin provider
A pinned consumer's dsh adapter SHALL register a `ctx.skills` provider from `.dsh/plugin/process-fsm-guard.js` over `REPO_ROOT/.dsh/skills` so process skill stubs are in the model catalog when session cwd is not the git root. The provider's `list`/`get` MUST be thenables and MUST satisfy live `validateCandidate` (`candidate.provider` equals the provider `name`). Versioned `.dsh/cordis.patch.yml` MUST NOT gain skill directory paths or `customSkillDirs`. Host row `skill-filesystem` `disabled: true` MUST NOT be modified. Native preset skill discovery MUST stay. Goldens in `pytest scripts/process-fsm` MUST cover the agents paging section (looked up by name, not `sections[0]`), the skill provider listing `covenant-flow` with lookup cwd ≠ repo **and** a non-aborted `signal` via a fake `waitWithAbort`/`validateCandidate` path, and the boot exit on a bad `canonical_paths.dev`.

#### Scenario: Golden covers catalog provider off-repo cwd
- **WHEN** a contributor runs `pytest scripts/process-fsm -q` at the repo root
- **THEN** a fixture lists `covenant-flow` from the plugin provider with lookup cwd outside the consumer git
- **AND** that fixture passes a `signal` into `list`/`get` and asserts each candidate `provider` field
- **AND** no network call to GitHub is made

#### Scenario: Patch yaml has no skill roots
- **WHEN** `.dsh/cordis.patch.yml` is inspected after this change
- **THEN** it still only inserts the Guard and Impeccable plugin modules
- **AND** it does not mention `.dsh/skills` as a loader path

### Requirement: dsh boot replaces the live isolate on 127.0.0.1:3080
`scripts/process-fsm/dsh_boot.sh` SHALL invoke a sibling helper `scripts/process-fsm/dsh_isolate_reload.sh` in the same directory **before** materializing a new tmp patch. Occupant classification SHALL use `/proc/<pid>/cmdline`: the listener is dsh if and only if that cmdline contains the token `dsh` **and** the subcommand `web` (live witness: `node …/.bin/dsh web --patch … --no-open --port 3080`, `comm=MainThread`). Classification by `comm`, by `ss` name, or by `argv0==dsh` / `basename(argv0)==dsh` SHALL NOT be the acceptance path. If the pair matches, the sibling SHALL SIGTERM that listener, wait, SIGKILL if it still listens, and confirm the port is free; if nothing listens, it SHALL proceed (cold start); if the cmdline lacks that pair, it SHALL exit non-zero, name the occupant on stderr, and MUST NOT steal the port. After reload, boot SHALL materialize a **new** tmp patch from `.dsh/cordis.patch.yml` with absolute plugin `name`s (MUST NOT reuse a previous tmp path). Boot SHALL parse `host:port` from `DSH_ISOLATE_LISTEN` (default `127.0.0.1:3080`) and launch `dsh web --patch <tmp> --no-open --port <port>` so kill, TCP wait, and bind use the **same** port. Boot SHALL background `dsh web` only long enough to observe TCP listen on that address, write the sidecar, and `wait` that PID. Trap INT/TERM/EXIT SHALL SIGTERM/SIGKILL `$DSH_PID`, confirm the port is free, **then** `rm` the tmp patch; it MUST NOT `rm` the patch while the listener still lives and MUST NOT `disown`/`setsid`. `dsh plugin add` remains not the v1 pin channel. ESM cache-bust SHALL NOT be the acceptance path. This change SHALL NOT create a systemd unit; card #793 MAY `ExecStart` this helper later.

#### Scenario: Node-wrapper cmdline with dsh and web is replaced
- **WHEN** a listener occupies the test listen address whose cmdline contains `dsh` and `web` as in `node …/dsh web --patch` (not `argv0=dsh`)
- **AND** `dsh_boot.sh` runs with `DSH_ISOLATE_LISTEN` pointing at that address and a fake `dsh` on `PATH`
- **THEN** the occupant receives SIGTERM (or SIGKILL after timeout) and is gone before the new `dsh web --patch`
- **AND** the new invocation uses a tmp patch path different from the previous patch file
- **AND** this scenario MUST NOT pass by matching only `argv0=dsh` or `comm=dsh`
- **AND** this scenario MUST NOT pass by sending a cache-bust query string to an ESM import

#### Scenario: Cold start when the port is free
- **WHEN** nothing listens on `DSH_ISOLATE_LISTEN`
- **AND** `dsh_boot.sh` runs with a fake `dsh` on `PATH`
- **THEN** no kill is required
- **AND** `dsh web --patch` still runs from `LAUNCH_DIR`

#### Scenario: Non-dsh occupant cmdline fails closed
- **WHEN** a process whose cmdline does **not** contain both `dsh` and `web` listens on `DSH_ISOLATE_LISTEN`
- **AND** `dsh_boot.sh` or `dsh_isolate_reload.sh` runs
- **THEN** the helper exits with status ≠ 0
- **AND** that occupant is still listening
- **AND** stderr names the occupant

#### Scenario: Listen address maps to dsh web --port
- **WHEN** `DSH_ISOLATE_LISTEN` is `127.0.0.1:<ephemeral>`
- **AND** `dsh_boot.sh` launches `dsh web`
- **THEN** the invocation includes `--no-open --port <ephemeral>`
- **AND** TCP wait and occupant kill use that same port

#### Scenario: SIGINT on boot kills the listener then removes the tmp patch
- **WHEN** `dsh_boot.sh` has a live fake listener child and a materialized tmp patch
- **AND** the boot process receives SIGINT
- **THEN** the listener is gone and is not reparented as an orphan holding the port
- **AND** the tmp patch is removed only after that kill

#### Scenario: Pytest A8 A9 and R-star do not kill the operator isolate on 3080
- **WHEN** goldens A8, A9, and R1–R9 run
- **THEN** they set `DSH_ISOLATE_LISTEN` to an ephemeral test address
- **AND** they set `DSH_ISOLATE_SIDECAR` to an ephemeral path
- **AND** they MUST NOT SIGTERM the operator listener on `127.0.0.1:3080`
- **AND** they MUST NOT overwrite `/tmp/covenant-flow-dsh-isolate.json`

### Requirement: dsh isolate sidecar records pid epoch and blob SHA256
The bounce helper SHALL write a sidecar with `pid`, `start_epoch`, `listen`, `guard_sha256`, `lib_sha256`, `launch_dir`, and `patch`. The sidecar path SHALL be `DSH_ISOLATE_SIDECAR` when that env is set; otherwise `/tmp/covenant-flow-dsh-isolate.json`. The default path is for live bounce and human homologation only. Pytest goldens (including A8/A9) SHALL set `DSH_ISOLATE_SIDECAR` to an ephemeral file and MUST NOT overwrite the live default. `guard_sha256` and `lib_sha256` SHALL be the SHA-256 hex of `REPO_ROOT/.dsh/plugin/process-fsm-guard.js` and `REPO_ROOT/scripts/process-fsm/dsh_plugin_lib.js` at bounce time. The sidecar MUST NOT live under `.dsh/` (pin copies that tree) and MUST NOT be committed in the consumer git. `dsh_isolate_reload.sh --check` SHALL exit 0 only when a listener exists on `DSH_ISOLATE_LISTEN`, the sidecar exists at the resolved path, sidecar `pid` is that listener, and both SHA fields equal the blobs currently on disk; otherwise it SHALL exit non-zero (missing sidecar, dead PID, or SHA mismatch = pin morto). Goldens in `pytest scripts/process-fsm` SHALL cover replace of a `node …/dsh web` cmdline (R1), cold start (R2), sidecar fields (R3), `--check` mismatch (R4), `--check` missing sidecar (R5), non-dsh occupant (R5b), `--port` mapping (R8), SIGINT trap (R7), and A8/A9 isolation from `:3080` (R9), without calling GitHub and without binding the operator `:3080`.

#### Scenario: Sidecar matches the new isolate and on-disk blobs
- **WHEN** `dsh_boot.sh` completes a successful fake launch with `DSH_ISOLATE_SIDECAR` set to a test path
- **THEN** that test path exists
- **AND** it contains `pid`, `start_epoch`, `guard_sha256`, and `lib_sha256`
- **AND** those SHA fields equal the SHA-256 of the Guard plugin and `dsh_plugin_lib.js` used in that tree
- **AND** `/tmp/covenant-flow-dsh-isolate.json` is not overwritten by that golden

#### Scenario: Check fails closed on SHA mismatch
- **WHEN** the sidecar SHA fields differ from the blobs on disk
- **AND** `dsh_isolate_reload.sh --check` runs against that sidecar path
- **THEN** the helper exits with status ≠ 0

#### Scenario: Check fails closed when sidecar is missing
- **WHEN** a listener may or may not exist
- **AND** the sidecar file is absent
- **AND** `dsh_isolate_reload.sh --check` runs
- **THEN** the helper exits with status ≠ 0

