## MODIFIED Requirements

### Requirement: No Fallback Public Identity For New Winners
Every new strategy key introduced for sequential BTC winner discovery SHALL resolve to a specific public display name and strategy description before saving and after served API readback.

#### Scenario: Public identity is validated before save
- **WHEN** the execution prepares a candidate for saving as a sequential Long winner
- **THEN** the execution SHALL define `name`, `strategy_name`, `strategy_display_name`, `strategy_description`, `direction`, and the public mapping source
- **AND** the public resolver or save payload SHALL return specific non-generic display and description values before the save request is made.

#### Scenario: Generic fallback blocks save
- **WHEN** a candidate public identity resolves to `Estratégia Cripto Farol`, `Strategy`, `Nova estratégia`, an empty value, or another generic fallback
- **THEN** the candidate SHALL NOT be saved as a winner
- **AND** if the fallback is caused by product behavior, the execution SHALL fix and validate the public mapping path before retrying.

#### Scenario: Served readback remains fallback-free
- **WHEN** a winner Favorite is read back from the served Favorites API after save
- **THEN** the Favorite SHALL show the expected `strategy_display_name` and `strategy_description`
- **AND** the new Favorite id SHALL NOT appear with `Estratégia Cripto Farol` in API, database-backed serialization, or UI evidence.
