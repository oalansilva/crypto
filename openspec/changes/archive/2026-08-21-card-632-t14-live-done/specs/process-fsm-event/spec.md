## RENAMED Requirements

- FROM: `T10-T13 events imply exclusive-group guards; T14 stays reject live`
- TO: `T10-T13 events imply exclusive-group guards`

## MODIFIED Requirements

### Requirement: T10-T13 events imply exclusive-group guards
For `achar_bloqueante`, `aceitar_sha`, `rerun_infra`, and `falha_codigo`, `process_event()` SHALL set the matching yaml guard true from the event name and the other exclusive-group predicates false.

#### Scenario: aceitar_sha from Code Review transitions
- **WHEN** `process_event()` is invoked with `aceitar_sha`, `q=Code Review`, valid card binding, and digest unchanged
- **THEN** the mover is called with `to=QA`

## ADDED Requirements

### Requirement: T14 live compiles checks_green and closes Done atomically
When `checks_green` is not injected, live `process_event integrar_develop` SHALL measure it before `evaluate()`: True only if the pull request from `q_git` into `develop` has GitHub check `qa-gate` in `success` on the head SHA. Pending, skipped, cancelled, failure, missing check, missing PR, or measurement error SHALL yield False. Other checks on the same SHA MUST NOT change this predicate. The CLI MUST NOT accept a `--checks-green` flag. If the live measurer is `None`, `process_event()` MUST `reject` and MUST NOT call the mover. If `evaluate()` rejects, the mover and the T14 runner MUST NOT run. If `evaluate()` accepts, `process_event()` SHALL require a non-`None` T14 runner; a missing runner MUST `reject` with `reason=I8` and MUST NOT call the mover. With a runner present, it SHALL run in order (`squash`, `sync_dev_source`, `restart`, `comment_done`) and the mover SHALL be called with `to=Done` only after every step succeeds. Any runner failure MUST return `reject` with `reason=I8`, MUST NOT call the mover, and MUST leave Status at QA. `--dry-run` MAY measure checks (read-only) and MUST NOT run the runner or the mover. Unit tests MUST inject the measurer and runner and MUST NOT call GitHub or systemd.

`sync_dev_source` MUST run only on `/srv/apps/dev/criptofarol/source`. It MUST first read `git status --porcelain`; a non-empty result (tracked or untracked) MUST be `I8` with no `checkout`, `merge`, `reset --hard`, restart, or Status move. Only a clean tree MAY `fetch` and `merge --ff-only origin/develop`; a non-fast-forward MUST be `I8` without `reset --hard`. `restart` MUST exec `/srv/apps/dev/criptofarol/source/restart` (not a worktree relative path, not PROD, not `stop`/`start` fallback). Failure of `comment_done` MUST be `I8`.

#### Scenario: integrar_develop rejects without checks_green
- **WHEN** `process_event()` is invoked with `integrar_develop` and `checks_green` is unset and the measurer is absent or returns False
- **THEN** the result is `reject` and the mover is not called
- **AND** the T14 runner is not called

#### Scenario: integrar_develop with qa-gate green runs atomic closeout
- **WHEN** `process_event()` is invoked with `integrar_develop`, `q=QA`, valid card binding, and the measurer returns True
- **AND** a T14 runner is injected and succeeds
- **THEN** the mover is called with `to=Done` after the runner finishes
- **AND** the runner ran `squash`, `sync_dev_source`, `restart`, and `comment_done` in that order

#### Scenario: T14 restart failure stays QA
- **WHEN** `process_event()` is invoked with `integrar_develop`, the measurer returns True, and `restart` fails
- **THEN** the result is `reject` with `reason=I8`
- **AND** the mover is not called

#### Scenario: missing T14 runner never moves Done
- **WHEN** `process_event()` is invoked with `integrar_develop`, the measurer returns True, and the runner is omitted
- **THEN** the result is `reject` with `reason=I8`
- **AND** the mover is not called

#### Scenario: dirty canonical DEV source stays QA
- **WHEN** `sync_dev_source` sees non-empty `git status --porcelain` on `/srv/apps/dev/criptofarol/source`
- **THEN** the result is `reject` with `reason=I8`
- **AND** no `checkout`, `merge`, `reset --hard`, restart, or Status move runs

#### Scenario: comment_done failure stays QA
- **WHEN** the T14 runner has completed squash, sync, and restart, and `comment_done` fails
- **THEN** the result is `reject` with `reason=I8`
- **AND** the mover is not called
