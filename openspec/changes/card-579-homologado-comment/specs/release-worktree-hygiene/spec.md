## MODIFIED Requirements

### Requirement: Homologation comment is verified in pre without GraphQL
`scripts/release-guard pre` SHALL call `normalize_release_cards` locally. Invalid `RELEASE_CARDS` tokens in strict `pre` MUST be blockers before any REST comment call. When `RELEASE_CARDS` is unset, the homologation-comment check SHALL warn and skip and MUST NOT invent a package list. When `CANONICAL_CARDS` is non-empty, `pre` SHALL fetch issue comments over REST for each canonical card ID and SHALL fail in strict mode if the marker `Homologado por Alan na develop.` is absent. This check MUST be a separate branch from the `post|audit` homologation section and MUST NOT call Project `item-list`, PR list, `ensure_snapshots`, or `card_status`. When `gh` is unavailable or unauthenticated while `RELEASE_CARDS` is set, the check SHALL be a blocker. REST comment reads in `pre|post|audit` are permitted and remain outside the GraphQL budget. In `pre`, every canonical ID SHALL require the marker (no Status-based not-applicable). Status-based not-applicable for cards not in `Homologado` or `Pronto` remains only in `post|audit`.

#### Scenario: Pre without comment
- **WHEN** `pre` runs with valid `RELEASE_CARDS` including card N
- **AND** issue N has no comment containing `Homologado por Alan na develop.`
- **THEN** the guard emits a blocker and exits non-zero in strict mode
- **AND** `pre` performs zero Project `item-list` calls

#### Scenario: Pre with canonical comment
- **WHEN** `pre` runs with valid `RELEASE_CARDS` including card N
- **AND** issue N has the canonical homologation marker
- **THEN** that card does not produce a homologation-comment blocker

#### Scenario: Pre without RELEASE_CARDS
- **WHEN** `pre` runs and `RELEASE_CARDS` is unset
- **THEN** the homologation-comment check warns and skips
- **AND** the guard does not invent a package list
- **AND** `pre` still performs zero Project `item-list` calls

#### Scenario: Pre cannot list comments
- **WHEN** `pre` runs with valid `RELEASE_CARDS` and `gh` cannot list comments for a card
- **THEN** the guard emits a blocker (fail-closed) and MUST NOT treat the card as evidenced

#### Scenario: Pre with invalid RELEASE_CARDS
- **WHEN** `pre` runs in strict mode with an invalid `RELEASE_CARDS` token
- **THEN** the guard emits a blocker
- **AND** it MUST NOT call `issues/.../comments`

#### Scenario: Pre does not use board Status
- **WHEN** `pre` has valid `CANONICAL_CARDS` and no `BOARD_JSON`
- **THEN** every canonical ID still requires the homologation marker
- **AND** Status-based not-applicable MUST NOT apply in `pre`
