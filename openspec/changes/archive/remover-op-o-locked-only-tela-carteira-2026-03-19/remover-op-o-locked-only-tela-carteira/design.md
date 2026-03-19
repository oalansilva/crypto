## Context

The Wallet page (`/external/balances`) currently displays a "Locked only" toggle filter and a "Locked" column in the balances table. These UI elements expose Binance's `locked` balance field. Both are being removed to simplify the interface.

## Goals / Non-Goals

**Goals:**
- Remove "Locked only" toggle from Wallet UI filter bar
- Remove "Locked" column from balances table
- Keep the `locked` field in the API response (no backend change)

**Non-Goals:**
- No backend/API changes
- No changes to other columns (asset, free, total, avg_cost_usdt, pnl_usd, pnl_pct)
- No changes to search functionality

## Decisions

### Remove UI elements only, keep API field
The `locked` field remains in the backend API response. Only the frontend filter toggle and table column are removed. This avoids any breaking changes to API consumers.

### No migration needed
Since the API is unchanged, there is no migration or rollback concern for the backend. Frontend removal is a clean, reversible UI change.

## Risks / Trade-offs

[Risk] User workflow disruption — Users who relied on "Locked only" filter may lose functionality.
→ **Mitigation**: This filter is being removed precisely because it is unused or low-value. If a user complains, the change can be reverted quickly.

[Risk] The `locked` column removal reduces information visibility.
→ **Mitigation**: The `locked` field is almost always zero for spot accounts. The column adds noise without value for most users.
