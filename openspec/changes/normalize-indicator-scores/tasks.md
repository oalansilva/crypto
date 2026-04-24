## 1. OpenSpec And Contract

- [x] 1.1 Create proposal, design, spec delta, tasks, and benchmark documentation.
- [x] 1.2 Define score output contract with `0-10` bounds and rule version.

## 2. Configurable Versioned Rules

- [x] 2.1 Add default JSON ruleset for technical indicator scores.
- [x] 2.2 Support runtime override via `INDICATOR_SCORE_RULES_PATH`.
- [x] 2.3 Validate required ruleset fields and input definitions.

## 3. Backend Scoring Service

- [x] 3.1 Implement normalized indicator scoring service consuming persisted indicator rows.
- [x] 3.2 Preserve null/warmup behavior by skipping scores with missing inputs.
- [x] 3.3 Return version metadata with every score.

## 4. Validation

- [x] 4.1 Add unit tests for score bounds and default rules.
- [x] 4.2 Add unit tests for configurable override rules and versioning.
- [x] 4.3 Add reproducible benchmark script and document expected use.
