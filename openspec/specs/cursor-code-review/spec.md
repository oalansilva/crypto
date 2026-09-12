# cursor-code-review Specification

## Purpose
Contrato do gate `Status=Code Review` no Cripto Farol: reviewers locais versionados (`diff-reviewer` + `code-reviewer`), comparação com `develop` na branch do card, Bugbot pago opcional.
## Requirements
### Requirement: Code Review MUST run the versioned diff reviewer on the uncommitted diff versus HEAD
While `Status=Code Review` and before any implementation commit, the Cursor **parent** SHALL materialize the uncommitted interval versus HEAD (`git diff HEAD` plus untracked files from `git ls-files --others --exclude-standard` as new-file hunks) into `.cursor/tmp/review-diff.patch` and SHALL launch one Task with `model: composer-2.5`, instructed not to edit, whose prompt is the body of `.cursor/agents/diff-reviewer.md` plus `review_diff_path:` pointing at that file (bytes under `## Diff` MAY also be inlined). The parent MAY spawn that reviewer as `generalPurpose` with the agent-file body **or** as named `subagent_type` `diff-reviewer`; destape matcher covers both. The spawn MUST still include `review_diff_path:` and the exact Task `description` in the awaiting sidecar. The spawn MUST be self-contained and MUST NOT inherit the Design or Apply transcript. The spawn MUST NOT inherit the parent picker. The child MUST NOT be instructed to compute the interval with git. A generic Task without that file MUST NOT be the happy-path reviewer. `/review-bugbot` MUST NOT run. `/review-security` MAY run only when Alan explicitly asks. The reviewer output MUST be findings with severity or the exact line `No findings.`

#### Scenario: Pre-commit Code Review
- **WHEN** a card is in `Status=Code Review` and the agent is about to commit implementation changes
- **THEN** the parent MUST materialize the uncommitted diff versus HEAD before spawn
- **AND** the agent MUST run the `diff-reviewer` Task with that materialized interval in the prompt
- **AND** that Task `model` is `composer-2.5`
- **AND** it MUST wait for the subagent result before committing
- **AND** the spawn prompt MUST NOT include the Design or Apply chat
- **AND** the spawn MUST NOT ask the child to run git

#### Scenario: Generic Task is not the default reviewer
- **WHEN** Code Review starts
- **THEN** the agent MUST NOT start with a generic `generalPurpose` Task that lacks the versioned `diff-reviewer` and `code-reviewer` prompts

#### Scenario: Reviewer output is findings or No findings
- **WHEN** `diff-reviewer` finishes with a materialized interval
- **THEN** the published result is findings with severity, or `No findings.`
- **AND** it MUST NOT paste Design Impeccable prose

### Requirement: Closing review MUST cover branch changes versus develop on the card branch
After the implementation commit and before `Status=QA`, the **parent** SHALL materialize `origin/<integration_branch>...HEAD` (overlay `integration_branch`, Cripto: `develop`) into `.cursor/tmp/review-diff.patch` and SHALL run the `diff-reviewer` Task with that interval in the prompt while still on the card branch. The agent MUST NOT run this comparison after squash/merge into `develop` (empty diff). The child MUST NOT compute that interval with git. Reuse is allowed only when that exact SHA already has this versus-`develop` run.

#### Scenario: Closing review versus develop
- **WHEN** the card is closing after an implementation commit
- **THEN** the parent MUST materialize `origin/develop...HEAD` before spawn
- **AND** the agent MUST have a `diff-reviewer` result for that interval on the closing SHA while still on the card branch

#### Scenario: Closing review reused
- **WHEN** the closing SHA already has a recorded `diff-reviewer` versus-`develop` run
- **THEN** the agent MAY reuse that result and MUST record the reuse in the Done evidence

### Requirement: Native Bugbot and Security Review MAY run only when Alan asks
Cursor Bugbot (`/review-bugbot`) MUST NOT run, even if asked as a product path; the Bugbot skill file MUST NOT be shipped. `/review-security` MAY run when Alan explicitly asks. They MUST NOT start from path globs alone. Sensitive paths (auth, credentials, wallet, trading, API) SHALL still be reviewed by the local `diff-reviewer` using `.cursor/agents/diff-reviewer.md` (not `BUGBOT.md`). Local `diff-reviewer` and `code-reviewer` remain the Code Review gate.

#### Scenario: Alan requests Security Review
- **WHEN** Alan explicitly asks for `/review-security` on the card
- **THEN** the agent MAY run that skill in addition to the two local reviewers
- **AND** the local reviewers remain the Code Review gate

#### Scenario: Bugbot is not a product path
- **WHEN** Alan asks for `/review-bugbot` or Code Review runs without that ask
- **THEN** `/review-bugbot` MUST NOT run
- **AND** no `BUGBOT.md` is read
- **AND** the Bugbot skill file is not shipped in the product

#### Scenario: Docs-only harness card skips paid Bugbot
- **WHEN** Alan has not asked for Bugbot
- **THEN** `/review-bugbot` MUST NOT run

### Requirement: Reviewer spawn failure MUST be explicit before any principal-session fallback
If either local reviewer Task fails to spawn or returns zero messages/parts, the handoff SHALL record `ERROR: subagent spawn failed/empty` after one retry. The principal session MAY complete the review itself only after that explicit error. Silent fallback is forbidden.

#### Scenario: Empty reviewer spawn
- **WHEN** a `diff-reviewer` or `code-reviewer` Task returns 0 messages, 0 parts, missing session or a creation error
- **THEN** the Code Review stage remains incomplete until a successful local review or an explicit fallback after the error is recorded

### Requirement: Process reviewer MUST stay read-only and use Composer execução model
The versioned `.cursor/agents/code-reviewer.md` file SHALL declare `readonly: true` and `model: composer-2.5` (redundant pin). During Code Review the primary session SHALL materialize the interval under review (uncommitted patch versus HEAD before the commit; `origin/<integration_branch>...HEAD` after it exists) and SHALL launch one Task with `model: composer-2.5` instructed not to edit, whose prompt is that file's body plus `review_diff_path:` (and optional `## Diff` bytes). The parent MAY spawn that reviewer as `generalPurpose` with the agent-file body **or** as named `subagent_type` `code-reviewer`; destape matcher covers both. The spawn MUST still include `review_diff_path:` and the exact Task `description` in the awaiting sidecar. The spawn MUST NOT inherit the Design or Apply transcript. The spawn MUST NOT inherit the parent picker and MUST NOT use Grok or `composer-2.5-fast`. The child MUST NOT run git to obtain the interval. It SHALL review process/contract (OpenSpec vs implementation, Design approval evidence, status non-regression). It MUST NOT duplicate diff-reviewer defect hunting and MUST NOT edit files. It MUST NOT read `.impeccable/critique/`. The versus-`develop` comparison is owned by `diff-reviewer` after the commit and before `Status=QA`. Published output MUST be findings or `No findings.` Review constraints SHALL be in these two agent files (optional consumer `REVIEW.md` without Bugbot), not in `BUGBOT.md`. The law is the Task `model` parameter on both spawn paths.

#### Scenario: Process reviewer does not mutate
- **WHEN** the process reviewer Task runs during Code Review
- **THEN** it reports findings only
- **AND** it MUST NOT write files, commit, push or change board status
- **AND** it MUST NOT load the Impeccable snapshot

#### Scenario: Process reviewer has no parent Design chat
- **WHEN** `code-reviewer` is spawned
- **THEN** the prompt is the versioned file plus the parent-materialized interval
- **AND** it does not include the Design or Apply transcript
- **AND** it MUST NOT ask the child to run git
- **AND** the Task `model` is `composer-2.5`

### Requirement: Pre-commit reviewers are a same-turn wave
While `Status=Code Review` and before any implementation commit, after the parent has materialized the uncommitted interval, the parent SHALL launch `diff-reviewer` and `code-reviewer` in the **same** parent turn, both read-only, both with `review_diff_path:` (optional `## Diff` bytes). MAY spawn each as `generalPurpose` with the agent-file body **or** as named `subagent_type`. Host serialization of the two Tasks MUST NOT fail this requirement. Destape of the first MUST NOT spawn the second. Closing review versus `develop` after the commit remains **one** wave and is outside this card's pingue-pongue. This requirement MUST NOT change `process-fsm.yaml` and MUST NOT reopen destape matching (#879).

#### Scenario: Wave not series
- **WHEN** pre-commit Code Review starts
- **THEN** the parent turn includes both reviewer Tasks
- **AND** the happy path is not Apply→review→Apply→review
- **AND** both children receive the same materialized interval

#### Scenario: First destape does not skip the pair
- **WHEN** destape fires after `diff-reviewer` completes and `code-reviewer` has already been spawned in that wave
- **THEN** the parent waits for the second child
- **AND** MUST NOT commit before both have returned
- **AND** MUST NOT spawn a duplicate `code-reviewer`

### Requirement: Happy path after the verify wave is residual and continue
After the single correction Apply and the single verify wave, remaining P1 or a **new** P1 on that wave SHALL be classified residual. The parent SHALL record that residual on the Done handoff and the card issue comment, SHALL continue (commit, closing wave versus `develop`, PR, QA), and MUST NOT open a third cycle. The parent MUST NOT ask the operator to authorize extra work or to accept residual. Homologation remains Alan's once, on the package (findings + residual + SHA). Extra automatic tests MUST NOT be the Done criterion.

#### Scenario: Leftover or new P1 does not start a third cycle
- **WHEN** the verify wave still reports P1, or reports a P1 that was not on the pre-correction list
- **THEN** the parent records residual on the Done handoff and the card comment
- **AND** the parent MUST NOT spawn another Apply or another judgment wave
- **AND** the parent MUST NOT ask «autorizar extra / aceitar residual»
- **AND** the card continues to commit, PR, and QA

#### Scenario: Clean verify wave still commits
- **WHEN** the verify wave returns `No findings.` (or only classified P3 residual)
- **THEN** the parent commits and continues the closing path
- **AND** this requirement does not invent a third cycle

### Requirement: Correction ceiling then visible block
The local reviewers SHALL NOT apply fixes. The parent SHALL NOT apply fixes in its own transcript. Each finding SHALL already carry `classe` (`mecanico` | `juizo`) in the dump; the parent SHALL copy that class and MUST NOT reclassify by re-reading prose. Mechanical P1/P2 SHALL be collected into one list and handed to **at most one** correction Apply child for the column, followed by **one** wave on the new interval, with no operator Ask. Judgment SHALL go straight to residual and MUST NOT occupy that correction slot. Remaining P1/P2 after that cycle, **or a new P1** on the verify wave, SHALL be residual on the Done handoff and the card issue comment; the card SHALL continue (commit, PR, QA); the parent MUST NOT open a third cycle and MUST NOT ask «autorizar extra / aceitar residual». P0 from a reviewer classifies as a column block (not a correction-list cycle). P3 stays classified residual. A `bloqueia_merge: sim` field on a non-P0 nit MUST NOT authorize a third cycle. Extra automatic tests MUST NOT be the Done criterion of the change that introduced this silent ceiling.

#### Scenario: One correction Apply then one wave
- **WHEN** either reviewer reports mechanical P1/P2
- **THEN** the parent spawns at most one Apply child with the combined mechanical list
- **AND** after that Apply returns, the parent spawns one wave in the same turn
- **AND** the parent does not re-run a single reviewer per finding as the happy path
- **AND** the parent MUST NOT ask to authorize that correction

#### Scenario: Third cycle is refused
- **WHEN** P1/P2 remain after that correction Apply and wave, or a new P1 appears on that wave
- **THEN** the parent records residual on the Done handoff and the card comment
- **AND** MUST NOT spawn another Apply or another wave for those findings
- **AND** MUST NOT ask «autorizar extra / aceitar residual»
- **AND** the card continues (commit, PR, QA) instead of remaining stuck in Code Review

### Requirement: Principal session applies reviewer findings
The local reviewers SHALL NOT apply fixes. The parent session SHALL NOT apply fixes in its own transcript. The parent SHALL copy each finding's dumped `classe` and `gravidade` and MUST NOT reclassify by re-reading prose and MUST NOT raise severity. For mechanical P1/P2, the parent SHALL spawn **at most one** correction Apply child with the combined list, then **one** wave, without an operator Ask; it MUST NOT re-run the affected reviewer per finding as the happy path. Judgment MUST NOT enter that correction Apply. Remaining P1/P2 after that cycle, or a new P1 on the verify wave, stay residual on Done while the card continues. A reviewer P0 classifies as a column block.

#### Scenario: Blocking finding
- **WHEN** `diff-reviewer` or `code-reviewer` reports a blocking finding
- **THEN** the parent MUST copy its dumped class (mechanical into the correction list, judgment into residual) before committing
- **AND** the reviewer MUST NOT edit the working tree
- **AND** the parent MUST NOT implement the fix in the orchestrator transcript
- **AND** the parent MUST NOT ask the operator to authorize extra or accept residual in order to proceed
- **AND** the parent MUST NOT raise the dumped gravidade

### Requirement: Done evidence MUST cite the local reviewers
The Done evidence comment SHALL include the `diff-reviewer` outcome (uncommitted and versus `develop`) and the `code-reviewer` outcome: findings, `no findings`, classified residuals, or spawn-failed plus fallback. It MUST NOT require a `/review-bugbot` line. It MAY cite `/review-security` only when Alan asked for that run.

#### Scenario: Done comment records local reviewers
- **WHEN** the card moves to `Status=Done`
- **THEN** the evidence comment MUST cite both local reviewers for the reviewed SHA
- **AND** it MUST NOT require a `/review-bugbot` line

### Requirement: dsh this-class reasoning-effort 400 MUST NOT consume the empty-spawn retry
On the dsh client, after the first this-class reasoning-effort rejection (400 / `INVALID_REQUEST` sending effort off / `none`) on an isolated Apply or reviewer **child** in the turn, the runtime root MUST NOT spawn another `subagent` / `subagent_fork` with the same preset, including the one-retry empty-spawn path from #518. The handoff SHALL record `ERROR: subagent spawn failed/empty` and the root MAY finish the step with an explicit residual. Silent fallback remains forbidden. Happy path remains: each isolated Apply and each of `diff-reviewer` and `code-reviewer` enters `turn/start`, runs at least one tool, and leaves a closing message, with zero this-class rejections on that spawn. Cursor and Grok keep the existing one-retry empty-spawn rule unchanged. This requirement MUST NOT reopen #518 / #569 as work, MUST NOT deny every `subagent`, and MUST NOT change `process-fsm.yaml`.

#### Scenario: First dead dsh reviewer does not birth the pair via retry
- **WHEN** the dsh root's first isolated Apply or reviewer child in the turn dies from this-class reasoning-effort 400
- **THEN** the root MUST NOT spawn a retry of that child or the other reviewer with the same preset
- **AND** the handoff records `ERROR: subagent spawn failed/empty`
- **AND** the root MAY complete the review itself only after that explicit residual

#### Scenario: Cursor empty-spawn retry is unchanged
- **WHEN** the client is Cursor or Grok and a reviewer Task returns 0 messages or 0 parts without this-class reasoning-effort 400
- **THEN** the existing one-retry empty-spawn rule still applies
- **AND** this requirement does not alter that path

### Requirement: Reviewer child MUST NOT fetch the interval via git or transcripts
The versioned files `.cursor/agents/diff-reviewer.md` and `.cursor/agents/code-reviewer.md` SHALL remain `readonly: true` and SHALL declare `model: composer-2.5` instead of `inherit`. Their bodies SHALL forbid the child from running git, from listing or Globbing `agent-transcripts` (or any agent transcript path), and from inventing the review interval by reading the working tree. The parent session SHALL materialize the interval before spawn and SHALL pass `model: composer-2.5` on both spawn paths. Grelha, Apply, and QA MUST NOT receive this diff-paste contract.

#### Scenario: Reviewer does not run git
- **WHEN** `diff-reviewer` or `code-reviewer` runs with a materialized interval in the prompt
- **THEN** the child MUST NOT invoke git
- **AND** it MUST NOT Glob or list agent transcripts
- **AND** it reports findings or `No findings.` from the supplied interval only

#### Scenario: Diff contract is Code Review only
- **WHEN** the parent spawns grill, Apply, or QA
- **THEN** those children are not required to receive `review_diff_path` or `## Diff`
- **AND** this requirement does not apply to them

#### Scenario: Agent header pins role model not inherit
- **WHEN** the two agent files are read
- **THEN** each declares `readonly: true`
- **AND** each declares `model: composer-2.5`
- **AND** neither declares `model: inherit`

### Requirement: Missing review interval MUST fail visibly and stop
If a Code Review spawn prompt contains neither a readable non-empty path after `review_diff_path:` nor non-empty bytes under a `## Diff` heading, the reviewer child SHALL print exactly `ERROR: review-diff missing` and SHALL stop. It MUST NOT continue the review by reading the repository, running git, or listing transcripts. Silent improvisation is forbidden.

#### Scenario: Spawn without interval stops
- **WHEN** `diff-reviewer` or `code-reviewer` starts without `review_diff_path` and without `## Diff` bytes
- **THEN** the child output contains `ERROR: review-diff missing`
- **AND** the review does not proceed
- **AND** the child does not read the working tree as a substitute interval

### Requirement: Reviewer dump SHALL emit finding schema
The versioned files `.cursor/agents/diff-reviewer.md` and `.cursor/agents/code-reviewer.md` SHALL instruct each child to emit every finding as a labeled `FINDING` block with `gravidade` (P0–P3), `classe` (`mecanico` | `juizo`), `conserto_obvio` (`sim` | `nao`), `conserto_proposto`, `bloqueia_merge` (`sim` | `nao`), `file`, and `summary`. If there are no findings the dump MUST be exactly `No findings.` The dump MUST NOT be a free paragraph that the parent has to classify. This SHALL NOT add a third reviewer and SHALL NOT be a JSON API schema.

#### Scenario: Wave dump carries class and obvious-fix
- **WHEN** `diff-reviewer` or `code-reviewer` finishes with at least one finding on a materialized interval
- **THEN** each finding in the dump includes `gravidade`, `classe`, and `conserto_obvio`
- **AND** the parent does not have to infer class from prose

#### Scenario: Empty dump stays No findings
- **WHEN** either reviewer has nothing to report
- **THEN** the dump is `No findings.`
- **AND** it does not invent a destape-completeness finding to fill the dump

### Requirement: Stable severity rubric for harness review
Both local reviewers SHALL use this observable rubric: P3 = copy / needle / Apply detail; P2 = incomplete contract that does **not** change acceptance; P1 = the patch **breaks** observable acceptance (Ask in the middle of the column, a third cycle, DEV talking to a PROD bot); P0 = the column stops. A destape «falta esta frase» item is not a finding. A destape table that is wrong about operator-visible behavior (P0 no longer stops the column) is P1 of acceptance.

#### Scenario: Copy nit is P3 and broken acceptance is P1
- **WHEN** one finding is a needle/copy tweak and another is that the patch would emit an Ask or a third cycle
- **THEN** the copy nit is dumped as P3
- **AND** the broken acceptance is dumped as P1

#### Scenario: Missing destape sentence is not scored
- **WHEN** the destape table is present with the five operator-visible rows
- **THEN** `code-reviewer` MUST NOT dump «falta esta frase» as P1/P2/P3
- **AND** completeness of that paragraph is not a finding

### Requirement: Process reviewer MUST NOT recaça the mechanical checklist
After the parent mechanical process checklist has run (or as part of the same Code Review turn), `.cursor/agents/code-reviewer.md` SHALL instruct the process reviewer not to re-score: tasks all done, Design tokens present, two reviewers in the same turn, pasted interval, or board state machine with no new edge. The process reviewer SHALL only ask whether the supplied diff punctures Entra/não entra of the bound change. Split of roles remains: `diff-reviewer` hunts defects in the interval; `code-reviewer` hunts contract. Independence still holds. This requirement MUST NOT merge the two reviewers.

#### Scenario: Checklist items are not process findings
- **WHEN** `code-reviewer` reviews a harness diff whose tasks, Design tokens, same-turn wave, pasted interval, and process-fsm.yaml edge are already confirmed
- **THEN** those items are not dumped as findings
- **AND** the dump either is `No findings.` or only Entra/não entra punctures with schema fields

#### Scenario: Roles stay split
- **WHEN** Code Review runs
- **THEN** `diff-reviewer` still hunts defects in the interval
- **AND** `code-reviewer` still hunts contract
- **AND** the parent MUST NOT fuse them into one Task

### Requirement: Closing review MUST NOT relitigate residual nor raise its severity
Closing review versus `develop` SHALL hunt only a defect new relative to the pre-commit interval, or reuse the SHA when that exact SHA already has this versus-`develop` run. The parent SHALL paste residual already on the card comment under `## Residual já no card`. Reviewers MUST NOT re-emit those items and MUST NOT raise their `gravidade`. The parent MUST NOT inflate dumped severity on that wave. This requirement MUST NOT add a third cycle and MUST NOT reopen #893's silent ceiling.

#### Scenario: Residual on the card is not re-emitted as a new P1
- **WHEN** closing review runs and `## Residual já no card` lists a destape-wording P2
- **THEN** the reviewer dump MUST NOT reopen that item
- **AND** MUST NOT dump it as P1

#### Scenario: New closing defect is allowed
- **WHEN** closing review finds a defect that is not in `## Residual já no card` and is new versus the pre-commit interval
- **THEN** the dump MAY include it as a `FINDING` at the rubric gravidade
- **AND** the parent still MUST NOT raise that gravidade

### Requirement: blocks_merge on a nit MUST NOT authorize a third cycle
A `bloqueia_merge: sim` field on a P3 or other non-P0 finding SHALL be residual for the T15 package. It MUST NOT authorize a third Apply+review cycle, MUST NOT emit an Ask, and MUST NOT override the #893 ceiling. A reviewer P0 still stops the column.

#### Scenario: Nit with blocks_merge still follows the ceiling
- **WHEN** a verify wave dumps `gravidade: P3` with `bloqueia_merge: sim` after the one correction cycle
- **THEN** the parent records it as residual
- **AND** MUST NOT spawn another Apply or wave for it
- **AND** MUST NOT ask «autorizar extra / aceitar residual»

