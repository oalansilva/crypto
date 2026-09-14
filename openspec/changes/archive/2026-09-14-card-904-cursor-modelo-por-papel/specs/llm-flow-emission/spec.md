## MODIFIED Requirements

### Requirement: Critics inherit model, not transcript
Assessment A, Assessment B SHALL use Grok 4.6 (`cursor-grok-4.6-high`), the same juízo model as Design-autor. `diff-reviewer` and `code-reviewer` SHALL use Composer 2.5 (`composer-2.5`). They SHALL receive a self-contained prompt. They MUST NOT inherit the parent Design/Apply/Review transcript. They MUST NOT inherit the parent chat picker. Isolated critics MAY write only `.impeccable/critique/**`. They MUST NOT edit `design.md`, prototype HTML, or product code. Their return to the parent MUST be bullets, disposition, verdict, and snapshot path. For Code Review, the parent SHALL attach the materialized interval (`review_diff_path:` and optional `## Diff` bytes) to the versioned agent file; the reviewer prompt MUST NOT instruct the child to fetch that interval with git or by listing transcripts.

#### Scenario: Dual critic without parent chat
- **WHEN** Design spawns Assessment A and Assessment B
- **THEN** each child uses Grok 4.6 (`cursor-grok-4.6-high`)
- **AND** the spawn prompt does not include the parent transcript
- **AND** the child's user-visible return is bullets plus snapshot path, not the full rubric dump

#### Scenario: Reviewers without Design/Apply transcript
- **WHEN** Code Review spawns `diff-reviewer` or `code-reviewer`
- **THEN** the prompt is the versioned agent file plus the parent-materialized interval
- **AND** the Task `model` is `composer-2.5`
- **AND** it MUST NOT include the Design or Apply chat
- **AND** it MUST NOT ask the child to run git or list transcripts

### Requirement: Handoff comments record cost proxies
Design, Apply, and Review handoff comments SHALL record proxies: word count of `design.md`, bytes of prototype HTML generated versus copied, number of spawns, and one `proxy modelo: <papel> → <rótulo> (<slug>)` line per spawn of that stage. They MUST NOT parse Cursor/Grok usage meters or add a dashboard.

#### Scenario: Design handoff includes proxies
- **WHEN** the Design comment is published on the card
- **THEN** it includes `design.md` word count, HTML generated-vs-copied bytes (or `N/A` when no prototype), and spawn count
- **AND** it includes one `proxy modelo:` line per Design spawn
- **AND** it does not include a parsed dollar amount from a vendor usage API

#### Scenario: Kaizen can compare the proxy to the runbook table
- **WHEN** `/kaizen release` reads issue comments of the package
- **THEN** it can locate `proxy modelo:` lines
- **AND** it can compare those lines to the vigente juízo/execução table
- **AND** it MUST NOT call a Cursor usage API
