## Context

The delivered Telegram alert scan uses `OpportunityService.get_opportunities(user_id=...)`.
That matches the Monitor UI path, but the alert destination is a general MVP Telegram group, not a user-specific screen.
User-level liked/starred strategy preferences are only a personal UI filter and must not decide whether the group receives an entry/exit alert.

The project already treats admin-owned `favorite_strategies` rows as the curated Monitor catalog for common users.
That is the smallest safe source for group alerts because it avoids scanning private non-admin user rows while still covering strategies Alan curated for the MVP.

## Goals / Non-Goals

**Goals:**

- Make Monitor Telegram scans evaluate the general admin-curated strategy catalog.
- Keep the scan independent from the admin caller's personal `user_id`.
- Keep per-user `MonitorStrategyPreference` liked/starred state out of alert coverage.
- Preserve existing tier filtering so Alan can exclude strategies by removing them from the catalog or moving them out of the configured alert tier scope.

**Non-Goals:**

- Add UI for alert exclusions.
- Send directly to the external beta group.
- Scan private non-admin user strategies.
- Change Monitor UI filtering behavior.

## Decisions

1. Add a catalog-level opportunity path to `OpportunityService`.

   The alert service should call a dedicated catalog method instead of overloading user-specific behavior. This keeps existing UI routes stable and makes the alert source explicit.

2. Use admin-owned `favorite_strategies` as the MVP catalog.

   Existing common-user Monitor behavior already uses admin favorites as curated fallback/catalog. Reusing it avoids a new table and avoids leaking ordinary user private strategies into a group alert.

3. Use existing `tier_filter` as the first exclusion mechanism.

   The alert settings already expose `MONITOR_TELEGRAM_TIER_FILTER`. Default `1,2,3` sends curated tiers; setting a strategy outside those tiers or deleting it from the admin catalog excludes it. A dedicated exclusion UI can be added later if needed.

## Risks / Trade-offs

- [Risk] The source table name is still `favorite_strategies`, which is confusing for a general catalog. -> Mitigation: add explicit catalog methods and tests so alert code no longer reads as user favorites.
- [Risk] Untiered admin rows are excluded by default. -> Mitigation: keep `MONITOR_TELEGRAM_TIER_FILTER=all` available when Alan wants all catalog rows.
- [Risk] Duplicate admin rows can produce duplicate alerts. -> Mitigation: existing dedupe by symbol/timeframe/status remains in place.
