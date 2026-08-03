## Why

The `backend-unit-tests` CI job takes 4m36s–4m53s in the five green reference runs and currently starts `pytest` plus coverage once for each of 56 files. We need a measured audit and a faster execution model without weakening PostgreSQL isolation, regression coverage, timeout protection, or the existing 70% coverage gates.

## What Changes

- Add a reproducible baseline that reports collected cases, total duration, p95, the ten slowest files, skips, and warnings.
- Classify every backend unit-test file as keep, refactor/consolidate, or remove, with the production behavior, risk, and evidence behind the decision.
- Avoid charging pure tests for global PostgreSQL schema creation/truncation while keeping PostgreSQL-backed tests isolated and explicit.
- Reduce repeated runner and coverage startup overhead while preserving actionable failure localization and bounded execution.
- Resolve or explicitly classify permanent skips, recurring warnings, redundant coverage, and tests for removed behavior.
- Record comparable before/after measurements and retain total and differential backend coverage at 70% or higher.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `ci-testing-hardening`: Require an auditable, measured, isolated, and time-bounded backend unit-test runner that improves feedback time without reducing coverage or regression protection.

## Impact

Expected impact is limited to the backend test harness, unit-test organization, CI workflow, test dependencies/configuration, and versioned audit evidence. Runtime APIs and product UI do not change; PostgreSQL remains mandatory wherever persistence is exercised.
