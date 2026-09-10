## MODIFIED Requirements

### Requirement: Critics inherit model, not transcript
Assessment A, Assessment B, `diff-reviewer`, and `code-reviewer` SHALL use the same model as the parent session and SHALL receive a self-contained prompt. They MUST NOT inherit the parent Design/Apply/Review transcript. Isolated critics MAY write only `.impeccable/critique/**`. They MUST NOT edit `design.md`, prototype HTML, or product code. Their return to the parent MUST be bullets, disposition, verdict, and snapshot path. For Code Review, the parent SHALL attach the materialized interval (`review_diff_path:` and optional `## Diff` bytes) to the versioned agent file; the reviewer prompt MUST NOT instruct the child to fetch that interval with git or by listing transcripts.

#### Scenario: Dual critic without parent chat
- **WHEN** Design spawns Assessment A and Assessment B
- **THEN** each child uses the parent model
- **AND** the spawn prompt does not include the parent transcript
- **AND** the child's user-visible return is bullets plus snapshot path, not the full rubric dump

#### Scenario: Reviewers without Design/Apply transcript
- **WHEN** Code Review spawns `diff-reviewer` or `code-reviewer`
- **THEN** the prompt is the versioned agent file plus the parent-materialized interval
- **AND** it MUST NOT include the Design or Apply chat
- **AND** it MUST NOT ask the child to run git or list transcripts
