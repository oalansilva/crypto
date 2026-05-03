## Context

Issue #106 targets strategy IP leakage. Today common users can receive and render `strategy_name`, `template_name`, saved `parameters`, `indicator_values`, and analyzer `details` from Favorites and Monitor opportunity APIs. Those fields can reveal moving-average periods and rule structure.

Strategy template and backtest APIs also expose sensitive internals (`description`, `optimization_schema`, `indicators`, `entry_logic`, `exit_logic`) and currently cannot rely on frontend navigation hiding as authorization.

Auth already exposes admin status by email through `ADMIN_EMAILS` and the frontend stores `user.isAdmin`. The backend must be the enforcement point because frontend-only hiding would still leak secrets through API responses.

## Goals / Non-Goals

**Goals:**

- Hide clear strategy identifiers, parameter values, indicator values, and analyzer detail payloads from non-admin API responses.
- Preserve operational decision context for common users: symbol, timeframe, HOLD/WAIT/EXIT state, distances, prices, notes, tier, and signal history needed to use the system.
- Preserve full payloads for admin users.
- Make the frontend render protected payloads without empty/error-looking states.
- Block non-admin direct access to strategy template/backtest/optimization surfaces.

**Non-Goals:**

- Change the internal strategy execution engine.
- Encrypt or migrate stored favorite strategy data.
- Remove admin-only strategy management screens.
- Prevent users from seeing their own trading result metrics already needed for product value.

## Decisions

1. Backend redaction is mandatory.

   Frontend masking alone is insufficient because the issue is about preventing common users from extracting the strategy from network payloads. Route handlers will determine whether the current user is admin and sanitize response objects before returning them.

2. Use a small shared redaction helper.

   Favorites and opportunities expose overlapping fields. A helper keeps the protected label, redacted parameter payload, and `is_strategy_protected` flag consistent without adding a database migration.

3. Return explicit protected metadata.

   Non-admin responses will keep stable response shapes but replace secret fields with safe values and include `is_strategy_protected: true`. Admin responses include `is_strategy_protected: false` and original fields. This lets the UI choose purposeful copy instead of inferring from missing data.

4. Keep operational fields visible.

   Common users still need decision status, distances, prices, entry/stop, timeframe, notes, and signal history to act inside the product. The redaction targets reproducibility details: strategy names, parameter maps, indicator values, and analyzer detail trees.

5. Guard combo/backtest strategy APIs as admin-only.

   Combo pages are already hidden in admin navigation, and the API reveals template logic. Backend admin dependencies will enforce the same boundary for direct requests. Frontend routes will also use `ProtectedRoute requireAdmin` for a cleaner UX, but backend remains authoritative.

## Risks / Trade-offs

- [Risk] Existing tests or clients expect raw strategy names in non-admin responses -> Mitigation: update affected tests and preserve admin/full-detail behavior.
- [Risk] Chart modal uses parameters to draw moving averages -> Mitigation: for protected payloads, avoid showing parameter labels/details and rely on decision markers/price context rather than revealing exact periods.
- [Risk] Some analyzer messages can contain condition names or values -> Mitigation: replace non-admin `message` with generic decision text and remove nested `details`.
- [Risk] Existing tests call combo endpoints without auth -> Mitigation: update tests to override admin dependency where they intentionally exercise admin-only strategy tooling.

## Migration Plan

- No schema migration.
- Deploy backend and frontend together.
- Rollback by reverting the redaction helper and UI protected-state handling.

## Open Questions

- None for implementation. Future product work can refine public strategy branding names, but this card focuses on hiding secrets.
