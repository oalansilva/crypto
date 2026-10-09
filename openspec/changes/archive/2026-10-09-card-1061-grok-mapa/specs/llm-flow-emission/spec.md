## MODIFIED Requirements

### Requirement: Critics inherit model, not transcript
On Cursor, Assessment A and Assessment B SHALL use the `juizo.slug` from `.cursor/model-map.yaml`, the same juízo model as Design-autor, and `diff-reviewer` and `code-reviewer` SHALL use the `execucao.slug` from that file. On Grok Build, Assessment A and Assessment B SHALL use `juizo.grok.slug` (`grok-4.7`), the same juízo model as the Grok Design-autor, and `diff-reviewer` and `code-reviewer` SHALL use `execucao.grok.slug` (`grok-4.6`). They SHALL receive a self-contained prompt. They MUST NOT inherit the parent Design/Apply/Review transcript. They MUST NOT inherit the parent chat picker. The Grok spawn MUST NOT omit `model`. Isolated critics MAY write only `.impeccable/critique/**`. They MUST NOT edit `design.md`, prototype HTML, or product code. Their return to the parent MUST be bullets, disposition, verdict, and snapshot path. For Code Review, the parent SHALL attach the materialized interval (`review_diff_path:` and optional `## Diff` bytes) to the versioned agent file; the reviewer prompt MUST NOT instruct the child to fetch that interval with git or by listing transcripts.

#### Scenario: Dual critic without parent chat
- **WHEN** Design spawns Assessment A and Assessment B on Cursor
- **THEN** each child uses the `juizo.slug` from `.cursor/model-map.yaml`
- **AND** the spawn prompt does not include the parent transcript
- **AND** the child's user-visible return is bullets plus snapshot path, not the full rubric dump

#### Scenario: Reviewers without Design/Apply transcript
- **WHEN** Code Review spawns `diff-reviewer` or `code-reviewer` on Cursor
- **THEN** the prompt is the versioned agent file plus the parent-materialized interval
- **AND** the Task `model` is the `execucao.slug` from `.cursor/model-map.yaml`
- **AND** it MUST NOT include the Design or Apply chat
- **AND** it MUST NOT ask the child to run git or list transcripts

#### Scenario: Grok critics use juizo.grok
- **WHEN** Grok Build spawns Assessment A or Assessment B
- **THEN** `model` is `juizo.grok.slug` (`grok-4.7`)
- **AND** the spawn does not include the parent transcript and does not inherit the picker

#### Scenario: Grok reviewers use execucao.grok
- **WHEN** Grok Build spawns `diff-reviewer` or `code-reviewer`
- **THEN** `model` is `execucao.grok.slug` (`grok-4.6`)
- **AND** `model` is not omitted
