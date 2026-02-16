## 1. State & Execution Orchestration

- [x] 1.1 Audit current status/phase transitions in lab.py/lab_graph.py
- [x] 1.2 Implement aligned status/phase mapping (upstream vs execution)
- [x] 1.3 Replace raw threading with JobManager-based execution wrapper

## 2. Retry & Output Validation

- [x] 2.1 Add schema validation for Trader/Dev outputs (pydantic models)
- [x] 2.2 Use `reasons` as fallback when `required_fixes` is empty
- [x] 2.3 Emit diagnostics for invalid outputs

## 3. Timeouts & Diagnostics

- [x] 3.1 Add per-node timeout handling
- [x] 3.2 Add total run timeout handling
- [x] 3.3 Ensure failures set diagnostic fields and stop execution

## 4. Tests & Verification

- [x] 4.1 Update/add unit tests for retry + status transitions
- [x] 4.2 Update/add tests for timeout behavior

> Note: Use project skills when applicable (architecture, tests, debugging, frontend).
