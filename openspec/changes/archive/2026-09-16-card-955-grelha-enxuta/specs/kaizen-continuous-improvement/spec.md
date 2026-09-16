## ADDED Requirements

### Requirement: Release kaizen reports grill sessions versus Design
`/kaizen release` SHALL report, for the package cards, grill sessions per card and a comparison of Em Refinamento versus Design using the same transcript proxy already used by the skill (`$CURSOR_TRANSCRIPTS_DIR` or sibling `agent-transcripts`, correlation via `#<id>` / `card-<id>`). Grill sessions SHALL count isolated children whose title or description contains `grill-card`. A card whose issue has the exact comment `card nítido; sem grill` and no grill child SHALL count as **0** grill sessions. Design count SHALL be `design-autor` plus `design-critic` plus `Assessment A` / `Assessment B`. The audit MUST NOT parse Cursor/Grok usage meters, MUST NOT add a dashboard, and MUST NOT print dollar amounts from a vendor API. `.cursor/skills/kaizen/SKILL.md` SHALL contain the needles `sessões de grelha por card` and `Em Refinamento vs Design`.

#### Scenario: Release report includes grill session counts
- **WHEN** `/kaizen release` runs for a package
- **THEN** the report SHALL include grill sessions per card
- **AND** SHALL include Em Refinamento vs Design (transcript proxy)
- **AND** it does not call a vendor usage API

#### Scenario: Nítido skip counts as zero grill sessions
- **WHEN** a package card has the exact comment `card nítido; sem grill` and no `grill-card` child
- **THEN** that card's grill-session count SHALL be 0

#### Scenario: Skill names the two needles
- **WHEN** a contributor reads `.cursor/skills/kaizen/SKILL.md`
- **THEN** the file SHALL contain `sessões de grelha por card`
- **AND** SHALL contain `Em Refinamento vs Design`
