## Context

The group alert source is now the admin-curated Monitor catalog. Tier filtering was a temporary exclusion mechanism, but tier also drives Monitor/Favorites star classification. A separate `notify_telegram` flag gives Alan a direct operational switch per catalog strategy.

## Goals / Non-Goals

**Goals:**

- Store alert eligibility per catalog favorite.
- Default existing/new favorites to `notify_telegram=true` so current alert coverage does not silently disappear.
- Allow admins to toggle the flag from Favorites.
- Keep common users from changing the flag on admin catalog rows.
- Filter Telegram alert scans by the flag.
- Default the legacy Telegram tier filter to `all` so unstarred strategies can still alert when `notify_telegram=true`.

**Non-Goals:**

- Per-user notification preferences.
- Advanced alert rules by status/timeframe/severity.
- External beta group posting.

## Decisions

1. Add `FavoriteStrategy.notify_telegram` as a boolean column with default `true`.

   Default `true` preserves the existing MVP behavior: catalog strategies remain eligible unless Alan opts out.

2. Only owners/admins can update `notify_telegram`.

   Existing route permissions already let common users update only their own tier preference for admin catalog rows. `notify_telegram` should stay an admin/catalog decision.

3. Filter catalog alert rows at the database query level.

   `OpportunityService.get_catalog_favorites()` gets an `alerts_only` mode used by Telegram scans. This avoids computing opportunities for excluded rows.

4. Keep tier as secondary legacy filtering only.

   `MONITOR_TELEGRAM_TIER_FILTER` now defaults to `all`. If Alan later wants an emergency technical cutoff, the configured filter can still narrow the scan, but the MVP control is the Favorites `notify_telegram` flag.

5. Add compact Favorites controls.

   The Favorites table/mobile cards already have dense action surfaces. Use a checkbox/toggle-like button with concise label `Telegram` / `TG` and stable width.

## Risks / Trade-offs

- [Risk] Existing rows need a default value. -> Runtime migration adds the column with `DEFAULT TRUE`.
- [Risk] The name is still on `favorite_strategies`. -> The UI label and service method make operational meaning explicit.
- [Risk] More columns can crowd the Favorites table. -> Add a compact admin-only column.
