## ADDED Requirements

### Requirement: The ruler declares the state of the realized measurement

The read-only Jev ruler (`scripts/scalp_jev_eval.py`) SHALL declare, in its report, the **state of the realized measurement** as one of `medido` (measured), `medição parcial` (partially measured), `não medido` (not measured) or `não aplicável` (not applicable — no decisions to join), together with the **real reason** of the state. The state SHALL be derived from the result of reading the stored OHLCV, not inferred from free text. The state SHALL be declared on its own, distinct from the sample sufficiency of the ruler.

#### Scenario: A fully covered read is declared measured

- **WHEN** the ruler can price every window it needs to measure from the stored OHLCV
- **THEN** the report SHALL declare the realized measurement as `medido`
- **AND** the report SHALL declare the connection used by the measurement

#### Scenario: A read that failed to price every needed window is declared not measured

- **WHEN** the realized side is needed (there are decisions to join) and no window receives a price because the OHLCV could not be read or does not cover the window
- **THEN** the report SHALL declare the realized measurement as `não medido`
- **AND** the report SHALL declare the real reason of the failure

#### Scenario: A run without decisions is declared not applicable

- **WHEN** the log is absent or empty, so there is no realized side to measure
- **THEN** the report SHALL declare the realized measurement as `não aplicável`
- **AND** the report SHALL NOT treat it as a measurement failure

### Requirement: No report path presents a non-measured realized side as insufficient sample

The ruler SHALL NOT present the case in which the realized side was **not measured** as insufficient sample. In every report path, the verdict label SHALL be selected from the measurement state before the sample state, so that a run whose measurement failed is labelled as a failed measurement and a run whose sample is merely small is labelled as insufficient sample. A run whose state is `não medido` SHALL NOT print the insufficient-sample verdict.

#### Scenario: A failed measurement is not labelled insufficient sample

- **WHEN** the measurement state is `não medido`
- **THEN** no path of the report SHALL print the insufficient-sample verdict
- **AND** the report SHALL print a verdict that explicitly says the realized side was not measured

#### Scenario: A small but measured sample keeps the insufficient-sample verdict

- **WHEN** the measurement state is `medido` and the priced sample is below the ruler's minimum
- **THEN** the report SHALL declare the sample insufficient
- **AND** the report SHALL NOT present the sample as a failed measurement

### Requirement: A run that did not measure the realized side terminates in error

The ruler SHALL terminate with a **non-zero exit code** when the realized side was needed and was not measured (`não medido`). The ruler SHALL still emit the report — to stdout and, when requested, as JSON and to the output file — labelled as realized-not-measured, before terminating. A run that did not measure SHALL NOT terminate as a success. Runs whose state is `medido`, `medição parcial` or `não aplicável` SHALL terminate with exit code zero.

#### Scenario: The not-measured run exits non-zero after emitting the report

- **WHEN** the ruler runs with decisions present and the realized side is `não medido`
- **THEN** the process SHALL exit with a non-zero code
- **AND** the report SHALL have been written (stdout, and `--json`/`--out` when requested) with the realized-not-measured label

#### Scenario: A measured or partial run exits zero

- **WHEN** the realized side is `medido`, `medição parcial` or `não aplicável`
- **THEN** the process SHALL exit with code zero

### Requirement: The ruler distinguishes partial measurement from insufficient sample

The ruler SHALL distinguish **partial measurement** from **insufficient sample**. When the gap is one of OHLCV coverage, the report SHALL say how many windows were left without a price and why, instead of presenting them as lack of sample, including in the per-regime closure. The per-regime closing rule of the sample (priced population below the ruler's minimum) SHALL remain unchanged.

#### Scenario: A coverage gap is labelled partial measurement with its count

- **WHEN** some needed windows receive a price and others do not because the stored candles do not cover them
- **THEN** the report SHALL declare the state as `medição parcial`
- **AND** the report SHALL state how many windows were left without a price and the reason

#### Scenario: Partial measurement and insufficient sample can coexist without confusion

- **WHEN** the state is `medição parcial` and the priced sample is also below the ruler's minimum
- **THEN** the report SHALL declare both the partial measurement and the insufficient sample separately
- **AND** the report SHALL NOT present the partial measurement as the insufficient sample

#### Scenario: A regime closed for lack of coverage declares the partial measurement

- **WHEN** a regime's eligible population with price is below the ruler's minimum because windows lacked stored coverage
- **THEN** the regime SHALL be declared closed
- **AND** the closure SHALL state that the measurement was partial, with the count of windows without coverage
