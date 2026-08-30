## ADDED Requirements

### Requirement: QA closeout runbook is client-labeled
`.cursor/skills/covenant-flow/SKILL.md` SHALL document QA closeout without adding a FSM state or event. Under the Cursor/Grok path it SHALL say: one isolated QA child reads checks and MUST NOT call `process_event`; the parent calls `aceitar_sha` only after a PR `q_git`→develop exists, then calls `integrar_develop` in the same turn as a green child, waits and retries on `qa-gate pending`, and treats `no_pr` / `sync: dirty` as visible causes. Under a dsh-labeled path it SHALL say: the runtime root MUST NOT spawn a QA child; the same turn MUST open the PR before T11, wait for `qa-gate`, and call T14 (Moore/plugin, not skill text alone). Stubs under `.dsh/skills/` and `.grok/skills/` MUST remain thin and MUST NOT copy the 12-column runbook. `AGENTS.md` MUST NOT grow for this rule.

#### Scenario: Cursor path keeps the QA child off process_event
- **WHEN** `covenant-flow` is read for the Cursor client
- **THEN** it says the QA child reads checks and MUST NOT call `process_event`
- **AND** it says the parent calls T14 in the same turn as a green child

#### Scenario: dsh path does not spawn a QA child
- **WHEN** `covenant-flow` is read for the dsh client
- **THEN** it says the root MUST NOT spawn a QA child
- **AND** it says the same turn opens the PR before T11, waits for `qa-gate`, and calls T14
