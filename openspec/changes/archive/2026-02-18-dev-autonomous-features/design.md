## Context

The Dev agent often proposes logic that requires simple derived features (e.g., previous RSI) but the current feature pipeline only exposes base indicators. This leads to preflight failures and suboptimal logic rewrites. We need a controlled, safe mechanism for Dev to request derived columns.

## Goals / Non-Goals

**Goals:**
- Allow Dev to declare derived columns explicitly.
- Implement a small, safe set of derived transforms.
- Update Dev prompt/validation to support derived features.

**Non-Goals:**
- Arbitrary user-defined Python expressions in indicators.
- Large-scale refactor of the indicator engine.

## Decisions

- **Derived feature registry**
  - Use a whitelist of transforms (prev/lag, slope, rolling mean) with bounded params.
  - Reject unsupported requests with diagnostics.

- **Structured declaration in Dev output**
  - Extend Dev output schema to include `derived_features` array.

- **Feature pipeline augmentation**
  - Add derived feature generation after base indicators are computed.

## Risks / Trade-offs

- **Risk:** Derived features can increase compute cost. → **Mitigation:** limit transforms/params.
- **Risk:** Dev may request unsupported fields. → **Mitigation:** validate and fall back to simplified logic.

## Migration Plan

- Add derived feature support behind validation checks.
- Update prompts and parser to accept the new field.
- Rollback by ignoring derived feature declarations.

## Open Questions

- Which transforms are needed beyond `prev` and `slope`? (start with minimal set)
