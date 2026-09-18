## ADDED Requirements

### Requirement: Favorites list payload is a grade summary

`GET /api/favorites/` SHALL return the catalog summary used by the grade (identity, stars, direction, timeframe, period, grid metrics). It MUST NOT embed `metrics.analysis_candles` or equivalent full historical series for every row. Opening analysis SHALL continue to load candles and trades from the analysis endpoints (`GET /api/favorites/{id}/trades` and market candles), not from the grade list.

#### Scenario: Admin opens Favorites with a large catalog

- **WHEN** the administrator account has dozens of crypto favorites whose stored analysis candles would sum to tens of megabytes
- **AND** the session is valid
- **THEN** `GET /api/favorites/` returns the rows without `analysis_candles` on each favorite
- **AND** `/favorites` lists those crypto pairs after loading

#### Scenario: Operator opens analysis of a listed favorite

- **WHEN** the operator activates the analysis action on a listed crypto favorite
- **THEN** the analysis view still receives candles and trades
- **AND** the Favorites grade remains a summary list

### Requirement: Favorites query error is not catalog empty

The Favorites page MUST branch on list-query error, successful empty catalog, and successful filtered-empty independently. `filteredFavorites.length === 0` after a failed query MUST NOT render the catalog-empty copy.

#### Scenario: Query throws after loading spinner

- **WHEN** `useQuery` for `['favorites']` leaves `isLoading=false` with `isError=true` or with non-array data
- **THEN** the page renders the load-error state with «Tentar de novo»
- **AND** MUST NOT render «Nenhuma estratégia favorita encontrada»

#### Scenario: Non-crypto favorites stay off the grade

- **WHEN** stored favorites include symbols without `/`
- **THEN** those rows remain outside the grade, as today
- **AND** they do not by themselves trigger catalog-empty copy if at least one crypto pair loaded
