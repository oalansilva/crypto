## ADDED Requirements

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
