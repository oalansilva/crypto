## MODIFIED Requirements

### Requirement: Process reviewer MUST stay read-only and use Composer execução model
The versioned `.cursor/agents/code-reviewer.md` file SHALL declare `readonly: true` and `model` equal to the Cursor `execucao.slug` from `.cursor/model-map.yaml` (redundant pin). That pin MUST remain `composer-2.5` and MUST NOT become `grok-4.6`. During Code Review the Cursor primary session SHALL materialize the interval under review (uncommitted patch versus HEAD before the commit; `origin/<integration_branch>...HEAD` after it exists) and SHALL launch one Task with that `execucao.slug` instructed not to edit, whose prompt is that file's body plus `review_diff_path:` (and optional `## Diff` bytes). The parent MAY spawn that reviewer as `generalPurpose` with the agent-file body **or** as named `subagent_type` `code-reviewer`; destape matcher covers both. The spawn MUST still include `review_diff_path:` and the exact Task `description` in the awaiting sidecar. The spawn MUST NOT inherit the Design or Apply transcript. On Cursor, the spawn MUST NOT inherit the parent picker and MUST NOT use a Grok slug or `composer-2.5-fast`. On Grok Build, `code-reviewer` MUST be spawned with `spawn_subagent` `model` equal to `execucao.grok.slug` (`grok-4.6`), MUST NOT omit `model`, and MUST NOT inherit the picker. The child MUST NOT run git to obtain the interval. It SHALL review process/contract (OpenSpec vs implementation, Design approval evidence, status non-regression). It MUST NOT duplicate diff-reviewer defect hunting and MUST NOT edit files. It MUST NOT read `.impeccable/critique/`. The versus-`develop` comparison is owned by `diff-reviewer` after the commit and before `Status=QA`. Published output MUST be findings or `No findings.` Review constraints SHALL be in these two agent files (optional consumer `REVIEW.md` without Bugbot), not in `BUGBOT.md`. The law is the spawn `model` parameter on both spawn paths plus the map file.

#### Scenario: Process reviewer does not mutate
- **WHEN** the process reviewer Task runs during Code Review
- **THEN** it reports findings only
- **AND** it MUST NOT write files, commit, push or change board status
- **AND** it MUST NOT load the Impeccable snapshot

#### Scenario: Process reviewer has no parent Design chat
- **WHEN** `code-reviewer` is spawned on Cursor
- **THEN** the prompt is the versioned file plus the parent-materialized interval
- **AND** it does not include the Design or Apply transcript
- **AND** it MUST NOT ask the child to run git
- **AND** the Task `model` is the `execucao.slug` from `.cursor/model-map.yaml`

#### Scenario: Grok process reviewer uses grok-4.6
- **WHEN** `code-reviewer` is spawned on Grok Build
- **THEN** `spawn_subagent` `model` is `grok-4.6`
- **AND** the spawn MUST NOT omit `model` or inherit the picker
- **AND** the child remains read-only

## ADDED Requirements

### Requirement: Grok diff reviewer uses execucao.grok
On Grok Build, `diff-reviewer` SHALL be spawned with `model` equal to `execucao.grok.slug` (`grok-4.6`). The parent MUST NOT omit `model` and MUST NOT inherit the picker. The reviewer MUST NOT be refused because it runs on Grok. On Cursor, `diff-reviewer` SHALL keep using top-level `execucao.slug` and MUST NOT switch to `grok-4.6`. Interval materialization, read-only behavior, and the same-turn wave MUST remain as already specified.

#### Scenario: Grok diff reviewer is grok-4.6
- **WHEN** Code Review on Grok Build spawns `diff-reviewer`
- **THEN** `model` is `grok-4.6`
- **AND** the spawn does not inherit the picker
- **AND** a Cursor `diff-reviewer` spawn still uses `composer-2.5`
