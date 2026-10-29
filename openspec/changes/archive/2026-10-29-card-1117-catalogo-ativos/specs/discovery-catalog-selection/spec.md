## MODIFIED Requirements

### Requirement: Every item remains reachable

The Discovery selection SHALL make every template and every asset of the Binance catalog (crypto pairs in USDT, ações and ETFs, thousands of items) reachable through instant search, class filtering, or pagination without materializing a long visible list.

#### Scenario: Reach the final symbol directly

- **WHEN** the administrator searches for `ZRX`
- **THEN** `ZRX/USDT` is displayed on the current result page without scrolling
- **AND** it can be added or removed from that result row.

#### Scenario: Reach an ação and an ETF directly

- **WHEN** the administrator searches for `NVDA` or `QQQ`
- **THEN** the matching ação or ETF is displayed on the current result page with its class
- **AND** it can be added or removed from that result row.

#### Scenario: Browse without a query

- **WHEN** no search query is present
- **THEN** pagination exposes every filtered result set
- **AND** changing pages does not scroll the result region.

### Requirement: Whole-catalog selection with exceptions

The asset axis SHALL NOT offer a whole-catalog selection with exceptions. Its `Todos` action SHALL select only the negociáveis of the current filter (class and search), SHALL show how many assets will be included and how many marked assets stay out before the administrator confirms, and SHALL add them to the current selection as explicit items. The templates axis keeps its whole-axis selection.

#### Scenario: Select every ETF of the filter

- **WHEN** the administrator filters the asset axis by ETFs and activates `Todos`
- **THEN** a confirmation shows the number of negociável ETFs to be included and the number of marked ETFs that stay out
- **AND** after confirming, the summary counts those ETFs as selected items, not as the whole catalog

#### Scenario: Remove one item after Todos

- **WHEN** the administrator removes `SPY` after confirming `Todos` for ETFs
- **THEN** the selected count decreases by one and SPY is no longer selected
- **AND** no exception list is created
