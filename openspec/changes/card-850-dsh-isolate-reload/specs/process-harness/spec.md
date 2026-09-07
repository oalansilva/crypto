## ADDED Requirements

### Requirement: Guard dsh homologation requires a live isolate matching pin blobs
After pin or merge that changes `.dsh/plugin/**` or `scripts/process-fsm/dsh_plugin_lib.js`, the process listening on `127.0.0.1:3080` SHALL be a bounce of `dsh_boot.sh` that loaded those blobs. Homologação and Pronto of a Guard dsh card SHALL require a live isolate whose sidecar SHA-256 equals the pin blobs on disk (`dsh_isolate_reload.sh --check` PASS). Git presence of the pin alone SHALL NOT satisfy that gate. This change SHALL NOT reimplement `sanitizeReasoningEffort`, `attachAgentEffortGuards`, or the `#839` Diagnostic formatter; bounce SHALL make that already-pinned plugin take effect. `guard.py` `decide()` MUST NOT gain this logic. `@deepseek-ai/dsh*` / `pi-ai` MUST NOT be vendored. Port 3080 MUST NOT be added to `environments.dev.services`. Homologation MUST NOT be `./restart` of product. Port 3080 MUST NOT become a systemd unit in this card.

#### Scenario: Pin morto fails the isolate check
- **WHEN** overlay `pin` and git blobs match the Guard tag
- **AND** the live sidecar SHA does not equal those blobs (or the sidecar/PID is absent)
- **THEN** `dsh_isolate_reload.sh --check` exits ≠ 0
- **AND** Homologação/Pronto of that Guard dsh card MUST NOT treat git/pin alone as acceptance

#### Scenario: Bounce does not reopen the sanitizer
- **WHEN** a reviewer inspects the diff of this change
- **THEN** `sanitizeReasoningEffort` / `attachAgentEffortGuards` / `formatChildRunFailure` are not reimplemented as the acceptance path
- **AND** `guard.py` `decide()` does not gain isolate-reload needles
- **AND** `@deepseek-ai/dsh*` is not vendored

### Requirement: Authenticated dump of dsh web :3080 remains the human DoD after isolate bounce
Authenticated dump of `http://127.0.0.1:3080` SHALL remain the human definition of done for this class and MUST NOT be replaced by pytest goldens. The dump SHALL show: (1) the **first** root turn of a new session on a model that refuses disabled effort (witness `muse-spark-*`) completing without this-class `INVALID_REQUEST` (`none` / missing field not sent); (2) one isolated spawn whose failure, if any (`turn/end` `kind=error`, witnesses 400 none **and** 401 CreditsError), reaches the parent with `stopReason` and `Diagnostic:` from the provider text — not only `failed before it finished` / `no closing message`. Unrelated 401 billing remains out of scope (MUST NOT be labelled `dsh_reasoning_effort_none`). cwd SHALL be `canonical_paths.dev`. Issues #817, #839, #837, and #793 SHALL NOT be reopened as work of this card.

#### Scenario: Human dump remains mandatory
- **WHEN** this card claims human acceptance
- **THEN** an authenticated dump of `http://127.0.0.1:3080` shows a first root turn without this-class 400 and an isolated spawn whose error, if present, includes `stopReason` and `Diagnostic:`
- **AND** pytest goldens do not replace that dump
- **AND** homologation is not `./restart` of product and port 3080 is not a systemd unit of this card

#### Scenario: Related cards stay closed as work
- **WHEN** this card's tasks are listed
- **THEN** they do not include reopening #817, #839, #837, or #793 as work
- **AND** they do not include paying or managing OpenCode billing
