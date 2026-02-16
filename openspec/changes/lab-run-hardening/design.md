## Context

The Lab run flow combines upstream validation with a LangGraph execution phase. Today it mixes UI-driven states, raw threads for execution, and loosely structured outputs, which can lead to inconsistent status/phase, stuck runs, and ambiguous retries. We need to harden orchestration, output validation, and timeouts.

## Goals / Non-Goals

**Goals:**
- Align `status` and `phase` transitions with actual execution state.
- Execute runs via a managed worker (job manager) with cancellation support.
- Use `required_fixes` or `reasons` to drive retries consistently.
- Validate Trader/Dev structured outputs and emit diagnostics on failure.
- Enforce per-node and total run timeouts.

**Non-Goals:**
- Redesigning the entire Lab UX or upstream flow.
- Changing external API contracts beyond added diagnostics fields.

## Decisions

- **Managed execution via JobManager**
  - *Rationale:* The project already uses a job pipeline for backtests. Reusing the job manager for Lab runs removes raw threads and supports cancellation/resume.
  - *Alternative:* Keep threads with watchdogs. Rejected due to fragility across reloads.

- **Explicit state machine for `status`/`phase`**
  - *Rationale:* Avoid UI confusion by setting `running` only after execution starts.
  - *Alternative:* Infer from mixed flags. Rejected as ambiguous.

- **Schema validation for Trader/Dev outputs**
  - *Rationale:* Structured JSON is required for downstream logic. Validate with pydantic (or zod equivalent) and fallback on failure.
  - *Alternative:* Best-effort parse only. Rejected due to silent failures.

- **Timeouts at node + run level**
  - *Rationale:* Prevent stuck runs and allow deterministic failure handling.

## Risks / Trade-offs

- **Risk:** Introducing JobManager dependency may require refactoring current run entrypoints. → **Mitigation:** Create a minimal job wrapper for Lab runs and keep current API.
- **Risk:** Stricter validation could reject borderline outputs. → **Mitigation:** Log diagnostics and use safe fallback verdicts instead of hard failure.

## Migration Plan

- Implement the new worker-backed execution path and wire it in `lab.py`.
- Roll out with existing endpoints unchanged; add diagnostics fields.
- Rollback by reverting worker integration and returning to current flow.

## Open Questions

- Exact defaults for timeouts (per-node and total) and configuration location.
