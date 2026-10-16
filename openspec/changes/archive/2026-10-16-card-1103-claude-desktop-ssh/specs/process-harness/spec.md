## ADDED Requirements

### Requirement: Design submission checks the gate tokens
`process_event submeter_design` (T5) SHALL parse the bound change's `design.md` with the same parser used by the precommit checklist and SHALL refuse when any of `UI impact`, `live_route` or `surface` is missing or invalid, naming the token (R28, findings 27/28 of #1101). This brings forward a check that already exists; it adds no transition or actor.

#### Scenario: design.md without live_route
- **WHEN** the parent calls `submeter_design` and `design.md` has no parseable `live_route` line
- **THEN** T5 is refused naming `live_route` and Status stays `Design`

#### Scenario: No-screen design with tokens
- **WHEN** `design.md` starts with `UI impact: none`, `live_route: N/A — <justification>` and `surface: none`
- **THEN** the token check passes

### Requirement: Rules and runbook describe the account registration
`.cursor/rules/harness.mdc`, the nucleus `rules.md` and the `covenant-flow` skill SHALL describe hooks as "account registration (`install.sh --account`) → shim → pinned adapter" and SHALL NOT cite project `.cursor/hooks.json` or `.codex/hooks.json` as the active registration (R25, R31). The runbook SHALL say that commands for the operator are pasted in plain bash without `!` and without `cd … &&` (R29), that after an account review a new session is needed before `prepare` stops reporting `hooks_inactive` (R30), and how to work through the desktop app (open in `/source` with the app's worktree option off, `#<id>` → `EnterWorktree`, app folder = no card). `host-mechanisms.md` of #1101 SHALL list page reinjection per host (R17). A session opened in `/source` SHALL receive the page (R34).

#### Scenario: Rules no longer point to project hook files
- **WHEN** a test scans the rule files and the skill
- **THEN** no active-registration text cites `.cursor/hooks.json` or `.codex/hooks.json` of the project

#### Scenario: Session opened in /source
- **WHEN** a Claude Code session, in the terminal or the app, starts in `/source` on the current pin
- **THEN** the page is injected with `q_git=develop` and the `EnterWorktree` instruction

### Requirement: Residual tests prove what they claim
The Impeccable-through-shim Guard test SHALL use a logging stub and assert it ran with empty stderr (R22); the design clone gate test SHALL require `/combo/results` in the Cripto catalog (R23); the release closeout test SHALL `pytest.skip` explicitly when `docs/crypto-overlay.md` is absent (R24).

#### Scenario: Impeccable stub did not run
- **WHEN** the shim route to `impeccable.sh` is broken
- **THEN** the Guard test fails because the stub log is empty

#### Scenario: Overlay doc missing
- **WHEN** `docs/crypto-overlay.md` is absent
- **THEN** the release closeout test reports an explicit skip

### Requirement: The #1101 OpenSpec records its supersessions before archive
Before the #1101 change is archived, its artifacts SHALL carry supersession notes: tasks 3.2 and 7.1 "superseded by 11.4/11.5" (R32); 6.5 without the gate declaration, 2.4 with the old window and 9.3 with `implemente` in `Todo` without live proof (R36); and the Impeccable requirement citing `hook.mjs` (R26).

#### Scenario: Archive check
- **WHEN** the #1101 change is validated for archive
- **THEN** each listed task and requirement carries its supersession note
