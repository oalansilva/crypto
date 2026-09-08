## ADDED Requirements

### Requirement: First author delivers parseable gate tokens

The first author SHALL hand off Design with `UI impact`, `live_route`, and `surface` each on its own parseable line. A screen-less card SHALL declare absence with a short justification (`live_route: N/A` + reason, `surface: new`) and MUST NOT borrow a catalog route. A card with screen SHALL mark only the cloned regions. No extra round SHALL be spawned only to satisfy the parser; the critic/dual verifies these tokens as a rubric item. Machine behavior is unchanged.

#### Scenario: Screen-less handoff passes with declared absence

- **WHEN** `design.md` declares `UI impact: none`, `live_route: N/A` with justification, and `surface: new`, with no prototype directory
- **THEN** the clone gate passes on the first author handoff
- **AND** no parser-only round is needed

#### Scenario: Borrowed catalog route on a screen-less card is refused

- **WHEN** a screen-less card declares a catalog key as `live_route` without a prototype
- **THEN** the gate refuses
- **AND** the fix is declaring absence with justification, not borrowing another key
