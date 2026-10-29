# favorites-asset-type-filter Specification

## Purpose
TBD - created by archiving change favorites-asset-type-filter. Update Purpose after archive.
## Requirements
### Requirement: Favorites can be filtered by asset type
The Favorites screen SHALL list crypto, ação and ETF favorites and MUST offer a "Classe" filter with the options Todas, Cripto, Ações and ETFs, each with its count. The default MUST be Todas.

#### Scenario: Favorites default to all classes
- **WHEN** the user opens the Favorites screen
- **THEN** the Favorites list MUST show crypto pairs, ações and ETFs together

#### Scenario: Filter by class
- **WHEN** the user picks Classe = ETFs
- **THEN** the list MUST show only ETF favorites

### Requirement: Asset type filter applies to both desktop and mobile layouts
The system MUST apply the class filter consistently across all responsive layouts.

#### Scenario: Mobile cards follow the class filter
- **WHEN** the Favorites screen is rendered in mobile layout with Classe = Ações
- **THEN** the mobile card list MUST include only ação favorites

#### Scenario: Desktop table follows the class filter
- **WHEN** the Favorites screen is rendered in desktop layout with Classe = Cripto
- **THEN** the desktop table MUST include only crypto pairs

