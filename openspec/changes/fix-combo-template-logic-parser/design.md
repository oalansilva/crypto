## Context

Combo templates evaluate entry and exit logic through `ComboStrategy._evaluate_logic_vectorized`. The current evaluator already uses a restricted context and AST rewrite to keep logic vectorized, but its preflight identifier check rejects safe Series method names and only rewrites dotted Bollinger references. Existing stored templates use `macd.macd`, `macd.signal`, `.abs()`, and `.shift(1)`, so they produce zero signals instead of executable backtests.

## Goals / Non-Goals

**Goals:**
- Support existing stored combo template syntax that maps to safe pandas Series operations.
- Preserve strict failure for unsupported identifiers and function calls.
- Add focused regression tests around signal generation for the affected syntax.

**Non-Goals:**
- Build a general Python expression runtime.
- Add arbitrary builtins or unrestricted method calls.
- Redesign MTF strategy execution.
- Change metric formulas, trade extraction, fees, or optimizer scoring.

## Decisions

- Keep the current AST/eval architecture, but expand the allowlist.
  - Rationale: the parser already centralizes vectorized safety and column context; a full parser rewrite would be larger than needed.
  - Alternative rejected: allow all attributes/methods. That would make template logic harder to audit.

- Normalize dotted references by mapping `<alias>.<field>` to `<alias>_<field>` for known indicator outputs.
  - Rationale: template authors naturally use `macd.macd` and `bb.upper`; internally the engine stores `macd_macd` and `bb_upper`.

- Allow only safe Series methods needed by stored templates: `shift`, `abs`, and simple rolling aggregations if directly used.
  - Rationale: these are deterministic vector operations over already-loaded OHLCV/indicator data.

## Risks / Trade-offs

- [Risk] Allowing method names could hide typos in template logic.
  - Mitigation: allow only specific method names and keep unknown identifiers rejected.

- [Risk] Some MTF templates contain prose in `entry_logic` rather than executable logic.
  - Mitigation: keep those failing clearly; this change fixes parser-compatible syntax, not unsupported MTF semantics.

- [Risk] Existing templates may still have business-logic flaws after syntax support.
  - Mitigation: validate by tests and backtest reruns; do not promote templates solely because they now execute.
