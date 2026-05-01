## ADDED Requirements

### Requirement: Wallet UI MUST use the Crypto Workbench layout
The Wallet UI (`/external/balances`) MUST present account balances in a compact operational layout aligned with the supplied Crypto Workbench template.

#### Scenario: Wallet overview
- **WHEN** the user opens the Wallet page
- **THEN** the UI MUST show the page title, Binance read-only context, last synchronization time when available, total wallet value, visible asset count, partial PnL summary, and performance summary

#### Scenario: Credential panel
- **WHEN** the user opens the Wallet page
- **THEN** the UI MUST show a Binance credential panel with configured/not configured state, masked API key when available, API key and secret inputs, save action, and remove action when credentials exist

#### Scenario: Filter toolbar
- **WHEN** the user opens the Wallet page
- **THEN** the UI MUST show search, dust threshold, sort selection, reset filters, and export CSV controls in one compact toolbar

#### Scenario: Desktop balance table
- **WHEN** balances are displayed on a desktop viewport
- **THEN** the UI MUST show a tabular balance list with asset, total, free, value USD, price, average cost, PnL, and allocation share

#### Scenario: Mobile balance cards
- **WHEN** balances are displayed on a narrow viewport
- **THEN** the UI MUST show a single-column card list without requiring horizontal scrolling
