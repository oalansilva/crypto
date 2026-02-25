## Context

The Favorites screen already includes filters such as Tier, Symbol, Strategy, Direction, and search. Favorites can contain both crypto pairs (symbols containing `/`) and stock tickers (symbols without `/`).

To improve scanning and day-to-day usage, we add a dedicated asset type dropdown.

## Goals / Non-Goals

**Goals:**
- Add an Asset Type dropdown with All/Crypto/Stocks.
- Apply filtering consistently for both mobile and desktop Favorites layouts.
- Keep the feature frontend-only with no backend changes.

**Non-Goals:**
- Changing the storage format of favorites.
- Adding backend filtering or changing the favorites API.

## Decisions

1) Classification rule based on symbol format
- Decision: classify as crypto if symbol contains `/`, otherwise classify as stock.
- Rationale: consistent with existing dataset and requires no API changes.

2) UI control placement
- Decision: place Asset Type dropdown in the existing filter bar alongside Tier/Symbol/Strategy/Direction.
- Rationale: predictable and consistent with other filters.

3) Implementation approach
- Decision: add a `assetTypeFilter` state and integrate it into `filteredFavorites` predicate.
- Rationale: minimal and low-risk change.

## Risks / Trade-offs

- [Risk] Some non-crypto symbols could include `/` in the future → Mitigation: keep logic isolated so it can be replaced by an explicit `asset_type` field later.
- [Risk] UI clutter in the filter bar → Mitigation: keep dropdown compact and consistent with existing controls.
