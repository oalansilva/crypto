## MODIFIED Requirements

### Requirement: QA closeout runbook is client-labeled
`.cursor/skills/covenant-flow/SKILL.md` SHALL document QA closeout without adding a FSM state or event. Under the Cursor/Grok path it SHALL say: one isolated QA child reads checks and MUST NOT call `process_event`; the parent calls `aceitar_sha` only after a PR `q_git`→develop exists, then calls `integrar_develop` in the same turn as a green child, waits and retries on `qa-gate pending`, and treats `no_pr` / `sync: dirty` as visible causes. Under a dsh-labeled path it SHALL say: the runtime root MUST NOT spawn a QA child; the same turn MUST open the PR before T11, wait for `qa-gate` **in the turn** (`job_output wait`, without `continue`), and call T14 (Moore/plugin, not skill text alone). Stubs under `.dsh/skills/` and `.grok/skills/` MUST remain thin and MUST NOT copy the 12-column runbook. With `qa_dev` on, the runbook SHALL say: T14 phase 1 returns `qa_dev_pendente`, the parent runs the test in blocks with `qa-dev` children in Claude Code, posts the report, and calls T14 again. `qa_dev_fail` MUST pause: the parent MUST NOT call T13 in that turn and asks Alan; if he confirms the defect, T13 and the post-T18 branch path follow, and if he disagrees, the parent retests the failed criteria without diff, using his reading. `qa_dev_inconclusivo` MUST stop with the three options: new test, T13, or Alan's own exact comment `/qa-dev-liberar <run>`, which the agent MUST NOT post. The `qa-dev` child MUST NOT call `process_event`. Other clients stop at `qa_dev_pendente` with a visible message. `AGENTS.md` MUST NOT grow for this rule.

#### Scenario: Cursor path keeps the QA child off process_event
- **WHEN** `covenant-flow` is read for the Cursor client
- **THEN** it says the QA child reads checks and MUST NOT call `process_event`
- **AND** it says the parent calls T14 in the same turn as a green child

#### Scenario: dsh path does not spawn a QA child
- **WHEN** `covenant-flow` is read for the dsh client
- **THEN** it says the root MUST NOT spawn a QA child
- **AND** it says the same turn opens the PR before T11, waits for `qa-gate`, and calls T14

#### Scenario: dsh path waits in the turn without continue
- **WHEN** `covenant-flow` is read for the dsh client
- **THEN** it says to wait for `qa-gate` in the turn
- **AND** it says not to use `continue` for that wait

#### Scenario: Runbook names the DEV test steps
- **WHEN** `covenant-flow` is read with `qa_dev` on
- **THEN** it says the parent runs the `qa-dev` blocks, posts the report and calls T14 again
- **AND** it says `qa_dev_fail` pauses for Alan before T13
- **AND** it says the `qa-dev` child MUST NOT call `process_event`

#### Scenario: Runbook names the contested FAIL path
- **WHEN** `covenant-flow` is read with `qa_dev` on
- **THEN** it says the parent does not call T13 in the turn of `qa_dev_fail`
- **AND** it says a disagreement from Alan leads to a retest without diff

#### Scenario: Runbook names the inconclusive path
- **WHEN** `covenant-flow` is read with `qa_dev` on
- **THEN** it says `qa_dev_inconclusivo` stops with three options
- **AND** it says the agent does not post `/qa-dev-liberar`
