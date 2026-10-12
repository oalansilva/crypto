## MODIFIED Requirements

### Requirement: Reviewer child MUST NOT fetch the interval via git or transcripts
The versioned reviewer agents SHALL remain readonly without a model pin. Their bodies SHALL forbid fetching the interval with git, listing/Globbing transcripts or inventing the interval from the worktree. The parent SHALL materialize the interval before spawn and pass the client's captured machine execucao selection explicitly. Grelha, Apply and QA MUST NOT receive this diff-paste contract.

#### Scenario: Reviewer launch after local edit
- **WHEN** the parent starts a review wave
- **THEN** each reviewer receives the materialized interval and captured client execution selection without reading git or transcripts

### Requirement: Grok diff reviewer uses execucao.grok
The Grok diff reviewer SHALL use its captured machine execucao selection through explicit spawn_subagent model and supported parameters, never Cursor/Codex values or picker inheritance. grok-4.6 SHALL be a migration choice rather than a permanent operational pin. The exact-diff, readonly and same-wave contracts SHALL remain.

#### Scenario: Grok execution changed locally
- **WHEN** a new review wave starts after a valid local Grok edit
- **THEN** both native reviewers use the new explicit selection without Git changes
