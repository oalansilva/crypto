# external-balances Delta Specification

## MODIFIED Requirements

### Requirement: System MUST provide a UI page to display external balances
The system MUST provide a UI page that displays Binance Spot balances in a readable list.

#### Scenario: Display balances
- **WHEN** the user opens the external balances page (`/external/balances`)
- **THEN** the UI MUST show the list of balances and highlight which assets have `locked` amounts

#### Scenario: Sorting
- **WHEN** balances are displayed
- **THEN** the UI MUST sort by `total` descending by default (largest balances first)

#### Scenario: Zebra striping on the desktop table
- **WHEN** the desktop table of balances is rendered
- **THEN** alternating rows MUST use subtly different background colors (zebra striping)
- **AND** the hover state and semantic colors (PnL, participation bar) MUST remain visible

#### Scenario: Mobile cards unchanged
- **WHEN** the mobile layout renders balances as cards
- **THEN** cards MUST NOT use zebra striping

#### Scenario: Redundant descriptive texts removed
- **WHEN** the balances page is rendered
- **THEN** the subtitle "Saldos lidos da Binance Spot por chave API read-only..." MUST NOT appear
- **AND** the note "Layout responsivo: tabela no desktop e cards no mobile." MUST NOT appear

#### Scenario: Binance read-only chip removed
- **WHEN** the balances page header is rendered
- **THEN** the "Binance · read-only" status chip MUST NOT appear
