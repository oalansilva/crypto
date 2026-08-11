## Context

The Favorites page has separate filters and one free-text search box. The search box currently checks a full lowercase query against individual fields. This works for simple searches, but fails when Alan copies visible fragments from the row, such as base/quote and strategy words.

## Goals / Non-Goals

**Goals:**
- Search by multiple terms across all relevant visible favorite text.
- Treat separators (`/`, `_`, `-`) as spaces for matching.
- Preserve existing sorting, tier filtering, and explicit dropdown filters.

**Non-Goals:**
- Add backend search.
- Change favorite persistence, tier data, or Monitor logic.
- Add fuzzy matching or typo correction.

## Decisions

- Build a combined search haystack per favorite from name, symbol, normalized symbol parts, raw strategy name, display strategy label, description, and timeframe.
- Tokenize the user query and require every token to appear somewhere in the combined haystack.
- Keep an exact normalized-string fallback so simple full-field searches continue to work.

## Risks / Trade-offs

- Very broad terms like `USDT` can still return many rows. Mitigation: explicit symbol/tier/strategy filters remain available.
