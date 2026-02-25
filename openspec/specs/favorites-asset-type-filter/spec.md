# favorites-asset-type-filter Specification

## Purpose
TBD - created by archiving change favorites-asset-type-filter. Update Purpose after archive.
## Requirements
### Requirement: Favorites can be filtered by asset type
The system MUST provide an Asset Type filter on the Favorites screen with options All, Crypto, and Stocks.

#### Scenario: Default selection is All
- **WHEN** the user opens the Favorites screen
- **THEN** the Asset Type filter is set to All and no favorites are excluded by asset type

#### Scenario: Crypto selection shows only crypto pairs
- **WHEN** the user selects Asset Type = Crypto
- **THEN** the Favorites list shows only items whose symbol contains `/`

#### Scenario: Stocks selection shows only stock tickers
- **WHEN** the user selects Asset Type = Stocks
- **THEN** the Favorites list shows only items whose symbol does not contain `/`

### Requirement: Asset type filter applies to both desktop and mobile layouts
The system MUST apply the asset type filter consistently across all responsive layouts of the Favorites screen.

#### Scenario: Mobile cards are filtered
- **WHEN** the Favorites screen is rendered in mobile layout and Asset Type is selected
- **THEN** the mobile card list reflects the chosen asset type filter

#### Scenario: Desktop table is filtered
- **WHEN** the Favorites screen is rendered in desktop layout and Asset Type is selected
- **THEN** the desktop table reflects the chosen asset type filter

