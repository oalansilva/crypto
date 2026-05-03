## ADDED Requirements

### Requirement: Common user Monitor tags are localized and concise
The Monitor SHALL show common users a localized wallet tag as `Carteira` and SHALL NOT show the technical `Strategy` tag in the table row tags.

#### Scenario: Common user reads row tags
- **WHEN** a common user opens the Monitor table
- **THEN** each row tag area uses `Carteira` instead of `Portfolio`
- **AND** the row tag area does not include `Strategy`
- **AND** the row tag area keeps the star classification when available
