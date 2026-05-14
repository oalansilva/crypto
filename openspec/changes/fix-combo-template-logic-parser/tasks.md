## 1. Parser

- [x] 1.1 Add normalization for supported dotted indicator references beyond Bollinger fields.
- [x] 1.2 Allow safe pandas Series method names used by stored templates while preserving strict unknown identifier failures.

## 2. Tests

- [x] 2.1 Add regression tests for MACD dotted field references.
- [x] 2.2 Add regression tests for `.shift()` and `.abs()` expressions.
- [x] 2.3 Add a negative test showing unsupported method calls are still rejected.

## 3. Validation

- [x] 3.1 Run focused backend tests for combo strategy logic parsing.
- [x] 3.2 Rerun strategy discovery checks that previously produced parser errors.

Note: use project skills for debugging/tests when applicable.
