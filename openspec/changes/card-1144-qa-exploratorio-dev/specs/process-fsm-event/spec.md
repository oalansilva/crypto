## MODIFIED Requirements

### Requirement: T14 live classifies checks and surfaces structured reject reasons
When `checks_green` is not injected, live `process_event integrar_develop` SHALL classify the GitHub check `qa-gate` on the pull request from `q_git` into `develop` before `evaluate()`. The yaml guard remains the derived bool: True only if that check is `completed` and `conclusion=success` on the head SHA. Other checks on the same SHA MUST NOT change this predicate. The CLI MUST NOT accept a `--checks-green` flag.

If the live classifier or measurer is `None`, `process_event()` MUST `reject` and MUST NOT call the mover. When the derived bool is False, the JSON payload `reason` MUST be the classified token, not the generic `guard:checks_green`:
- no `q_git`, no PR, or no head SHA → `no_pr`
- `qa-gate` present and `status` is not `completed` → `qa-gate pending`
- missing `qa-gate`, skipped, cancelled, failure, API error, timeout, or JSON error → `qa-gate failed`

If `evaluate()` accepts, `process_event()` SHALL require a non-`None` T14 runner; a missing runner MUST `reject` with `reason=I8` and MUST NOT call the mover. With a runner present and overlay `qa_dev.enabled` absent or false, it SHALL run in order (`squash`, `sync_dev_source`, `restart`, `comment_done`) and the mover SHALL be called with `to=Done` only after every step succeeds. `process_event()` MUST NOT poll or retry internally.

With overlay `qa_dev.enabled` true, T14 SHALL have two phases on the same `QA --integrar_develop--> Done` edge, with no new state, event or Project option. Phase 1 (no closeout receipt for this PR) SHALL take the QA test lock, run `squash`, `sync_dev_source` and `restart`, write the receipt, post the integrated-in-DEV comment, and `reject` with `reason=qa_dev_pendente`, Status staying QA. A lock held by another card SHALL `reject` with `reason=qa_dev_ocupado` before `squash`. A failure inside phase 1 SHALL release the lock. Phase 2 (receipt present) SHALL NOT repeat the closeout and SHALL measure `qa_dev_ok` from the latest card comment that carries the marker `<!-- covenant-flow:qa-dev veredito=<V> sha=<SHA> run=<id> -->` and whose author is overlay `qa_dev.autor_relatorio`. Comments from any other author MUST be ignored, and a missing `qa_dev.autor_relatorio` MUST leave the guard false. `qa_dev_ok` is true only when the receipt commit is an ancestor of `SHA` and either `V` is `PASS`, `NAO_TESTADO` or `NADA_PARA_TESTAR`, or `V` is `INCONCLUSIVO` and a later comment from the same author is exactly `/qa-dev-liberar <run>` with that report's `run`. When true, it SHALL run `comment_done` and call the mover with `to=Done`; a release MUST be stated in that comment. With `V=FAIL` it SHALL `reject` with `reason=qa_dev_fail`, and no release applies. With `V=INCONCLUSIVO` and no release it SHALL `reject` with `reason=qa_dev_inconclusivo`. With no valid report it SHALL `reject` with `reason=qa_dev_pendente`. No reject calls the mover.

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

#### Scenario: qa_dev off keeps the single-step closeout
- **WHEN** `process_event()` runs `integrar_develop` with overlay `qa_dev` absent or `enabled: false`, the classifier ok and the runner successful
- **THEN** the mover is called with `to=Done` in the same call
- **AND** no QA test lock is taken

#### Scenario: phase 1 integrates and holds the card in QA
- **WHEN** `process_event()` runs `integrar_develop` with `qa_dev.enabled` true, the classifier ok and no closeout receipt
- **THEN** the runner runs `squash`, `sync_dev_source` and `restart`
- **AND** the result is `reject` with `reason=qa_dev_pendente`
- **AND** the mover is not called
- **AND** `comment_done` does not run

#### Scenario: phase 1 waits for another card's test
- **WHEN** `integrar_develop` phase 1 runs and the QA test lock is held by another card and has not expired
- **THEN** the result is `reject` with `reason=qa_dev_ocupado`
- **AND** the T14 runner is not called

#### Scenario: phase 2 with a passing report moves to Done
- **WHEN** `integrar_develop` runs with the receipt present and the latest report marker has `veredito=PASS` for a SHA that contains the receipt commit
- **THEN** the closeout steps are not repeated
- **AND** `comment_done` runs
- **AND** the mover is called with `to=Done`

#### Scenario: phase 2 with a failed criterion keeps the card out of Done
- **WHEN** `integrar_develop` runs with the receipt present and the latest report marker has `veredito=FAIL`
- **THEN** the result is `reject` with `reason=qa_dev_fail`
- **AND** the mover is not called

#### Scenario: a report for older code does not satisfy the guard
- **WHEN** `integrar_develop` runs with the receipt present and the latest report marker names a SHA that does not contain the receipt commit
- **THEN** the result is `reject` with `reason=qa_dev_pendente`
- **AND** the mover is not called

#### Scenario: phase 2 with an inconclusive report keeps the card in QA
- **WHEN** `integrar_develop` runs with the receipt present, the latest report marker has `veredito=INCONCLUSIVO` and there is no release comment
- **THEN** the result is `reject` with `reason=qa_dev_inconclusivo`
- **AND** the mover is not called

#### Scenario: phase 2 with Alan's release moves to Done
- **WHEN** `integrar_develop` runs with the receipt present, the latest report marker has `veredito=INCONCLUSIVO` and `run=R`, and a later comment from `qa_dev.autor_relatorio` is exactly `/qa-dev-liberar R`
- **THEN** `comment_done` runs and states the release
- **AND** the mover is called with `to=Done`

#### Scenario: a release does not apply to FAIL
- **WHEN** `integrar_develop` runs with the receipt present, the latest report marker has `veredito=FAIL` and a release comment exists
- **THEN** the result is `reject` with `reason=qa_dev_fail`
- **AND** the mover is not called

#### Scenario: a marker from another author is ignored
- **WHEN** a comment from an account other than `qa_dev.autor_relatorio` carries the marker with `veredito=PASS`
- **THEN** that comment does not count as a report
- **AND** the result follows the latest report from `qa_dev.autor_relatorio`

#### Scenario: a release from another author is ignored
- **WHEN** a comment from an account other than `qa_dev.autor_relatorio` is `/qa-dev-liberar <run>`
- **THEN** the result is `reject` with `reason=qa_dev_inconclusivo`
- **AND** the mover is not called

#### Scenario: phase 1 failure releases the lock
- **WHEN** `integrar_develop` phase 1 takes the QA test lock and `restart` fails
- **THEN** the result is `reject` with `reason=I8`
- **AND** the QA test lock is released
