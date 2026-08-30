## ADDED Requirements

### Requirement: dsh closeout reaches the root through Moore
A change of `context_file[QA]` MUST be made once in `.cursor/process-fsm.yaml`. The dsh plugin SHALL keep injecting that page via its existing Moore section (`runPage` / `covenant-flow:moore`) so the dsh runtime root receives the same-turn T14 / no-QA-child closeout without a second copy of the law in `.dsh/plugin/` or a long stub. Skill text MAY explain the dsh loop; it MUST NOT be the only carrier. Adapters MUST NOT dual-write T0–T17. This requirement MUST NOT add a `decide()` matcher that would deny Cursor `Task` or OpenCode `task`.

#### Scenario: dsh Moore page carries the QA stub
- **WHEN** the dsh plugin builds `covenant-flow:moore` for a bound card with `q=QA`
- **THEN** the injected text contains the yaml `context_file[QA]` stub
- **AND** the plugin source does not contain a second T0–T17 table

#### Scenario: no new decide matcher for QA spawn
- **WHEN** `guard.py` `decide()` is invoked with a Cursor `Task` whose prompt mentions QA or T14
- **THEN** this change MUST NOT add a deny for that tool name
