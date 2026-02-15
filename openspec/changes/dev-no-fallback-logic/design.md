## Context

The backend already validates and corrects invalid logic using Dev support, but still allows a fallback simplification path when correction does not succeed. For strategy integrity, invalid `entry_logic` and `exit_logic` must be rewritten into valid boolean expressions by Dev, with no simplification fallback.

## Goals / Non-Goals

**Goals:**
- Enforce Dev rewrite of invalid entry/exit logic into valid boolean format.
- Remove fallback simplification behavior (including EMA/RSI fallback) for invalid logic.
- Persist correction metadata for auditability.

**Non-Goals:**
- Introduce new strategy templates or indicator defaults.
- Change frontend behavior or request schema.

## Decisions

1. Remove fallback branch for invalid entry/exit logic
- Decision: invalid logic handling MUST not route to any simplified strategy fallback.
- Rationale: fallback changes strategy semantics and hides invalid inputs.
- Alternative considered: keep fallback as last resort; rejected because it violates deterministic user intent.

2. Gate execution on valid boolean rewrite
- Decision: preflight MUST proceed only when Dev rewrite produces valid boolean expressions for both `entry_logic` and `exit_logic`.
- Rationale: guarantees runtime receives explicit and testable logic.
- Alternative considered: allow partial correction; rejected because mixed valid/invalid logic is ambiguous.

3. Log correction outcomes explicitly
- Decision: trace MUST include original logic, rewritten logic, validation result, and no-fallback marker.
- Rationale: enables debugging and proves that no simplification fallback occurred.
- Alternative considered: minimal generic log entry; rejected because it is not auditable enough.

## Risks / Trade-offs

- Higher hard-fail rate for malformed logic inputs -> Mitigation: keep clear validation error messages and correction logs.
- Dev rewrite quality depends on validator strictness -> Mitigation: use deterministic boolean validation before execution.
