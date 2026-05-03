## Context

Issue #108 reports that Monitor data is not displayed for an affected common user. Database evidence shows that user is active, has one global Monitor preference row, and has zero rows in `favorite_strategies`. The Monitor API derives opportunities from `FavoriteStrategy.user_id == current_user_id`, so a user without Monitor-ready favorites receives an empty list.

This became more visible after common-user access to Favorites/strategy tooling was restricted: common users should use Monitor as the main product surface, but they cannot self-populate the strategy source.

## Goals / Non-Goals

**Goals:**

- Return useful Monitor opportunities for common users with no own favorites.
- Preserve per-user favorites as the highest-priority source when present.
- Preserve backend redaction for non-admin users, including fallback data.
- Avoid schema migration and avoid copying rows between users as a one-off fix.

**Non-Goals:**

- Re-open Favorites or strategy tooling to common users.
- Change strategy execution logic, indicator math, or pricing providers.
- Add a new database table for curated strategies in this card.

## Decisions

1. Use admin favorites as the curated fallback source.

   The current production data already has a large curated set under a configured admin account while the affected common user has none. Reusing that set avoids a migration and keeps operational behavior close to the existing admin-vetted Monitor universe.

2. Fallback only when the requesting user has no Monitor-ready matching favorites for the tier filter.

   User-owned Monitor-ready favorites must remain authoritative. If a user has any crypto Monitor candidate matching the requested tier filter, the service uses only those rows. If their rows are only outside the current Monitor processing scope, the curated fallback is allowed so the Monitor does not render empty.

3. Resolve the fallback user by configured admin emails.

   The backend already defines admin emails in auth middleware. The service reads `ADMIN_EMAILS` in configured order and picks the first admin user with matching Monitor-ready favorites. This keeps fallback priority configurable through the existing operational contract.

4. Keep strategy redaction outside the service and mask fallback metadata.

   `OpportunityService` returns computed opportunities and marks curated fallback rows. `opportunity_routes.get_opportunities` already applies `redact_opportunity_payload` using the requesting user, so fallback opportunities for common users remain protected. For fallback payloads, non-admin redaction also masks admin-authored `name` and `notes`.

## Risks / Trade-offs

- [Risk] Fallback can expose the same symbol universe to all users without favorites. Mitigation: non-admin payload redaction removes strategy identifiers, parameters, indicator values, and details.
- [Risk] Admin has no curated favorites in a fresh environment. Mitigation: service returns the current empty list rather than failing.
- [Risk] Tier filters may make a user appear empty even when they have favorites in another tier. Mitigation: fallback is scoped to the requested tier so the requested Monitor view still receives data.

## Migration Plan

- No schema migration.
- Deploy code and restart services.
- Rollback by reverting fallback selection logic; existing data remains untouched.

## Open Questions

- Future product work can define an explicit public curated strategy table. This card keeps the fix small and aligned with current data.
