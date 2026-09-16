## ADDED Requirements

### Requirement: Refresh of a new post-70/30 favorite uses the complete stored period

Automatic and manual refresh of a favorite **created after this card** following 70/30 SHALL rerun on the complete chosen period persisted on that favorite. For period «todo» the refresh SHALL pull through today. The routine SHALL NOT substitute the Discovery training window for that favorite. Favorites already stored with a training window SHALL keep being refreshed on their stored start/end until someone saves them again.

#### Scenario: New todo favorite refresh extends to now

- **WHEN** the refresh routine (or the operator's revalidate) runs for a new «todo» favorite created after 70/30
- **THEN** the run uses first candle → now
- **AND** the list status/period after refresh still show the complete period, not 17/08/2017 → 24/12/2023

#### Scenario: Legacy training favorite refresh unchanged

- **WHEN** the refresh routine runs for a favorite still stored with 17/08/2017 → 24/12/2023
- **THEN** it SHALL keep that window
- **AND** it SHALL NOT silently expand to all-history in this card
