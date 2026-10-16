## ADDED Requirements

### Requirement: Process hooks are registered in the operator account for Claude Code, Cursor, Codex and OpenCode
The Covenant Flow hook registration SHALL live in the operator account, not in consumer repositories, for Claude Code, Cursor, Codex and OpenCode, each through the host's native global hook or plugin mechanism. Grok Build and dsh are out of scope of this change (Alan's decision of 2026-10-14): their project registration (`.grok/hooks/process-fsm.json`, `.dsh/cordis.patch.yml`), stubs and behavior SHALL stay exactly as before this change, with no account registration, no shim, no new digest review and no shim-related refusal. The `covenant-flow` product SHALL distribute one thin shim and the per-host registration entries. Each account registration SHALL carry the same events, matchers, blocking flags and timeouts that the client's adapter required in its project registration. Consumer repositories pinned at or after the first pin that declares account registration MUST NOT contain a Covenant Flow hook registration for those four clients; handler scripts and adapter logic SHALL stay in the consumer, versioned by the pin. Where an existing requirement names a client's project registration file (`.claude/settings.json`, `.cursor/hooks.json`, `.codex/hooks.json`, `.opencode/plugin/`), the same entries SHALL apply to the account registration installed by the shim. The adapter manifest SHALL declare the registration per client: `account` for each of the four clients whose global mechanism the rehearsal proved, `project` for Grok Build and dsh. A client among the four whose global mechanism is not proven in the rehearsal SHALL keep only the visible failure: it MUST be reported as `registration=unproven` by the account installer status check and recorded in the card, the adapter manifest MUST NOT declare it `registration: account`, no page, check or handoff SHALL present it as protected, and no project registration or other mechanism SHALL be kept or invented for it.

#### Scenario: Pinned repository carries no hook registration
- **WHEN** a consumer is pinned with the account-registration pin
- **THEN** no Covenant Flow hook entry exists in its project registration files
- **AND** a product write on the integration branch is denied in each account-registered client through the account registration

#### Scenario: Grok Build and dsh stay as they are
- **WHEN** a consumer is pinned with the account-registration pin
- **THEN** its Grok Build and dsh project registrations, stubs and behavior are the same as before this change
- **AND** the account installer registers no shim in those hosts and the trust record has no entry for them

#### Scenario: Host without a proven global mechanism
- **WHEN** the rehearsal cannot prove a global hook or plugin mechanism for Claude Code, Cursor, Codex or OpenCode
- **THEN** `install.sh --account --check` reports that host as `registration=unproven`, the adapter manifest does not declare it `registration: account`, and the gap is recorded in the card
- **AND** no session of that client in a new-pin consumer is presented as protected, and its dependent `process_event` is refused visibly

### Requirement: Account registration without the shim is refused visibly in every account-registered client
When the bound consumer is on the account-registration pin, `process_event` SHALL, in Claude Code, Cursor, Codex and OpenCode, refuse the transitions that today require the Codex evidence preflight (`iniciar_design`, `recriticar`, `submeter_design`, `iniciar_apply`, `pedir_review`, `aceitar_sha`, `integrar_develop`) with `hooks_inactive` when the calling session has no shim heartbeat, when the shim or that client's account registration is not installed, or when that client is `registration=unproven`. The refusal SHALL name the client, the missing piece and the recovery (`install.sh --account`, then a new session), and Status SHALL stay unchanged. A client whose session cannot be matched to a heartbeat MUST NOT be accepted on the absence of a check: at least the shim and that client's account registration SHALL be required installed and reviewed. `install.sh --account --check` SHALL report, per host, a missing account registration or a missing shim. Consumers on pins older than account registration, and Grok Build and dsh on any pin, SHALL keep today's behavior. This refusal is a precondition of existing events, like the Codex preflight; it MUST NOT add a state, event, edge or human gate, and it MUST NOT change the Guard, paging or model selection of any client.

#### Scenario: New-pin consumer on an account without the shim
- **WHEN** a consumer on the account-registration pin is used from Cursor, OpenCode, Codex or Claude Code on an account where `install.sh --account` was never run, or was removed
- **THEN** a dependent `process_event` is refused with `hooks_inactive` naming the client and the recovery, and Status is unchanged
- **AND** `install.sh --account --check` reports that host without account registration

#### Scenario: Older pin keeps today's preflight
- **WHEN** a consumer whose pin predates account registration calls `process_event` from Cursor or OpenCode, or any consumer calls it from Grok Build or dsh
- **THEN** no shim heartbeat is required and the transition behaves as before this change

### Requirement: The shim discovers the consumer from the session cwd and calls the pinned adapter
On every registered hook event the shim SHALL resolve the consumer from the event's working directory (hook input `cwd`, workspace root or process cwd, in that order): the Git top-level that contains `.covenant-flow/overlay.yaml`. Without an overlay, or with an overlay without `pin`, the shim MUST do nothing: no page, no deny, no adapter execution and no output that changes the session. With a pin that declares project registration (older pins), the shim MUST do nothing for that host so that the project registration is the only one that runs. With a pin that declares account registration, the shim SHALL read the pinned adapter manifest, check the shim protocol, verify the adapter digest against the account trust record and execute the client's adapter from that worktree with the original event payload. A missing manifest or adapter file, files that differ from the manifest, an unreviewed adapter digest, an incompatible shim protocol or an ambiguous consumer MUST fail visibly: gating events deny product writes and spawns in the host's native deny format with the reason and the recovery, and session-start events show the reason on the page. The shim MUST NOT contain FSM, Guard, paging or model-selection logic.

#### Scenario: Folder without pin
- **WHEN** a session in Claude Code, Cursor, Codex or OpenCode opens in a folder without `.covenant-flow/overlay.yaml` or without `pin` and edits a file
- **THEN** no Covenant Flow page appears and no tool call is denied or delayed by the process

#### Scenario: Pinned repository with a missing adapter
- **WHEN** the pinned manifest lists an adapter file that is absent from the worktree
- **THEN** product writes and spawns are denied with `adapter_missing` and the recovery to re-run the pin

#### Scenario: Pinned repository with a divergent adapter
- **WHEN** an adapter file differs from the manifest, or its digest was not reviewed by the operator
- **THEN** the shim does not execute it, and product writes and spawns are denied with `adapter_divergent` or `hooks_unreviewed`

#### Scenario: Older pin keeps its project registration
- **WHEN** a session works in a worktree whose pin predates account registration and still has the project registration
- **THEN** the shim does nothing there and each hook runs exactly once, from the project registration

### Requirement: The process follows the session into the card worktree
A session opened in the integration checkout (for example `/source`) or in any other folder and then moved into a card worktree (`EnterWorktree` in Claude Code, or the equivalent of each client) SHALL have the process active in the card worktree without depending on the launch directory. The shim SHALL record, at session start, a private session heartbeat in the operator account with the session identity, transcript locator, host version and registration digest, with no effect on the session when the launch folder is not pinned. On the first hook event after the working directory changes to another consumer or worktree, the adapter of the new worktree SHALL be used and the Moore page of the newly bound card SHALL be injected into the session context.

#### Scenario: Session from /source enters the card worktree
- **WHEN** a Claude Code session titled `#<id>` is launched in `/source` and enters the `card-<id>-*` worktree
- **THEN** the page shows `bound_card=<id>`, `process_event --client claude --card <id> --dry-run` is not rejected for inactive hooks, and a product write outside the allowed stage is denied

#### Scenario: Session launched in an unpinned folder
- **WHEN** a session launched in an unpinned folder enters a pinned card worktree
- **THEN** the process becomes active there, with the heartbeat recorded at session start

### Requirement: Account installer merges registrations without loss and never grants trust
The `covenant-flow` account installer SHALL install or update the shim under the operator's Covenant Flow config directory and merge one registration per in-scope host (Claude Code, Cursor, Codex, OpenCode) found on the machine into that host's global configuration, without touching Grok Build or dsh configuration, preserving every foreign key and handler. Malformed configuration or a conflict that cannot be merged without loss MUST be refused visibly with the path, without partial writes in any host. The installer SHALL be idempotent, SHALL offer a status check and a removal that restores the foreign entries, and MUST NOT read or write the model selection or record trust. The consumer pin channel SHALL stay "copy and commit" for everything except the hook registration.

#### Scenario: Foreign hooks survive installation
- **WHEN** the operator's global Claude Code or Cursor configuration already has unrelated hooks
- **THEN** after installation those hooks are unchanged and the Covenant Flow entry was added once

#### Scenario: Conflict refuses without partial write
- **WHEN** one host configuration is malformed
- **THEN** the installer reports that path and leaves every host configuration unchanged

### Requirement: Trust review uses a registration digest and an adapter digest
Trust SHALL be recorded by the operator per digest in one account record shared by Claude Code, Cursor, Codex and OpenCode, in two parts: the registration digest (account hook entries plus shim files) and the adapter digest (every file the client's adapter can execute, as listed by the pinned manifest, including the full Impeccable scripts tree). Installation and pinning MUST NOT record trust. A registration digest different from the one in the session heartbeat SHALL require a new session. An adapter digest that is reviewed SHALL be accepted on the next hook call without reopening the session, also after a worktree switch between different reviewed adapters. The agent's ability to run the record command remains a cooperative limit accepted by Alan.

#### Scenario: Worktree switch between reviewed adapters
- **WHEN** the session moves from a worktree with one reviewed adapter digest to a worktree with another reviewed adapter digest
- **THEN** hooks keep working without reopening the session

#### Scenario: Installation is not trust
- **WHEN** the account installer or the pin completes
- **THEN** the trust status still reports the new digests as unreviewed until the operator records them
