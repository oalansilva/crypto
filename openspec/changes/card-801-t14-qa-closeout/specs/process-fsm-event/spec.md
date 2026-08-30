## RENAMED Requirements

- FROM: `T10-T13 events imply exclusive-group guards; T14 stays reject live`
- TO: `T10-T13 events imply exclusive-group guards`

## MODIFIED Requirements

### Requirement: T10-T13 events imply exclusive-group guards
For `achar_bloqueante`, `aceitar_sha`, `rerun_infra`, and `falha_codigo`, `process_event()` SHALL set the matching yaml guard true from the event name and the other exclusive-group predicates false. `reviewers_ok` for `aceitar_sha` remains true from the event name (not a measured review). Before `evaluate()`, `aceitar_sha` MUST list a pull request from `q_git` into `develop`. If that list is empty, `process_event()` MUST `reject` with `reason=no_pr`, MUST NOT call the mover, MUST NOT create a pull request, and Status MUST remain Code Review.

#### Scenario: aceitar_sha from Code Review transitions when a PR exists
- **WHEN** `process_event()` is invoked with `aceitar_sha`, `q=Code Review`, valid card binding, digest unchanged, and a PR from `q_git` into `develop` exists
- **THEN** the mover is called with `to=QA`

#### Scenario: aceitar_sha without PR stays Code Review
- **WHEN** `process_event()` is invoked with `aceitar_sha`, `q=Code Review`, valid card binding, and no PR from `q_git` into `develop` exists
- **THEN** the result is `reject` with `reason=no_pr`
- **AND** the mover is not called
- **AND** no pull request is created
- **AND** Status remains Code Review

## ADDED Requirements

### Requirement: T14 live classifies checks and surfaces structured reject reasons
When `checks_green` is not injected, live `process_event integrar_develop` SHALL classify the GitHub check `qa-gate` on the pull request from `q_git` into `develop` before `evaluate()`. The yaml guard remains the derived bool: True only if that check is `completed` and `conclusion=success` on the head SHA. Other checks on the same SHA MUST NOT change this predicate. The CLI MUST NOT accept a `--checks-green` flag.

If the live classifier or measurer is `None`, `process_event()` MUST `reject` and MUST NOT call the mover. When the derived bool is False, the JSON payload `reason` MUST be the classified token, not the generic `guard:checks_green`:
- no `q_git`, no PR, or no head SHA → `no_pr`
- `qa-gate` present and `status` is not `completed` → `qa-gate pending`
- missing `qa-gate`, skipped, cancelled, failure, API error, timeout, or JSON error → `qa-gate failed`

If `evaluate()` accepts, `process_event()` SHALL require a non-`None` T14 runner; a missing runner MUST `reject` with `reason=I8` and MUST NOT call the mover. With a runner present, it SHALL run in order (`squash`, `sync_dev_source`, `restart`, `comment_done`) and the mover SHALL be called with `to=Done` only after every step succeeds. `process_event()` MUST NOT poll or retry internally.

`sync_dev_source` MUST run only on overlay `environments.dev.source`. Non-empty `git status --porcelain` MUST `reject` with `reason=sync: dirty` and a `message` that contains that path and the porcelain text, with no `checkout`, `merge`, `reset --hard`, restart, or Status move (I8: Status stays QA). Other runner failures MUST `reject` with `reason=I8` and `message` set to the exception text. `--dry-run` MAY classify (read-only) and MUST NOT run the runner or the mover. Unit tests MUST inject the classifier/measurer and runner and MUST NOT call GitHub.

#### Scenario: integrar_develop without PR is no_pr
- **WHEN** `process_event()` is invoked with `integrar_develop`, `q=QA`, valid card binding, and there is no PR from `q_git` into `develop`
- **THEN** the result is `reject` with `reason=no_pr`
- **AND** the mover is not called
- **AND** the T14 runner is not called

#### Scenario: integrar_develop with qa-gate pending is visible
- **WHEN** `process_event()` is invoked with `integrar_develop`, `q=QA`, a PR exists, and `qa-gate` is not `completed`
- **THEN** the result is `reject` with `reason=qa-gate pending`
- **AND** the mover is not called
- **AND** the T14 runner is not called

#### Scenario: integrar_develop with qa-gate failed is visible
- **WHEN** `process_event()` is invoked with `integrar_develop`, `q=QA`, a PR exists, and `qa-gate` is missing, skipped, cancelled, failed, or the Checks API errors
- **THEN** the result is `reject` with `reason=qa-gate failed`
- **AND** the mover is not called
- **AND** the T14 runner is not called

#### Scenario: integrar_develop with qa-gate green runs atomic closeout
- **WHEN** `process_event()` is invoked with `integrar_develop`, `q=QA`, valid card binding, and the classifier returns ok
- **AND** a T14 runner is injected and succeeds
- **THEN** the mover is called with `to=Done` after the runner finishes
- **AND** the runner ran `squash`, `sync_dev_source`, `restart`, and `comment_done` in that order

#### Scenario: dirty canonical DEV source stays QA with visible cause
- **WHEN** `sync_dev_source` sees non-empty `git status --porcelain` on overlay `environments.dev.source`
- **THEN** the result is `reject` with `reason=sync: dirty`
- **AND** `message` contains the canonical path and the porcelain text
- **AND** no `checkout`, `merge`, `reset --hard`, restart, or Status move runs

#### Scenario: T14 restart failure stays QA
- **WHEN** `process_event()` is invoked with `integrar_develop`, the classifier returns ok, and `restart` fails
- **THEN** the result is `reject` with `reason=I8`
- **AND** the payload includes a non-empty `message`
- **AND** the mover is not called

#### Scenario: missing T14 runner never moves Done
- **WHEN** `process_event()` is invoked with `integrar_develop`, the classifier returns ok, and the runner is omitted
- **THEN** the result is `reject` with `reason=I8`
- **AND** the mover is not called
