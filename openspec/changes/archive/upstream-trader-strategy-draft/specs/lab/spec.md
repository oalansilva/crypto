# Δ lab Specification — Upstream strategy draft + approval

## ADDED Requirements

### Requirement: Trader MUST produce a strategy draft before execution

When a run is in `phase=upstream`, the system MUST support a **strategy draft** proposed by the Trader.

The system MUST:
- Persist `upstream.strategy_draft` per run.
- Support a conversational loop until `upstream.ready_for_user_review == true`.
- Show the draft to the user for explicit approval before starting execution.

#### Scenario:

User answers symbol/timeframe/objective. Trader returns a draft with suggested indicators + entry/exit + risk plan. UI shows the draft and waits for user approval.

### Requirement: Execution MUST require explicit user approval

The system MUST NOT start downstream execution unless `upstream.user_approved == true`.

#### Scenario:

User sees the draft and clicks “Aprovar e iniciar execução”; only then execution starts.

### Requirement: User can provide feedback to revise draft

The system MUST allow user feedback to request adjustments and the Trader MUST revise the draft accordingly.

#### Scenario:

User writes “quero usar RSI e evitar muita operação” and the Trader returns a revised draft.
