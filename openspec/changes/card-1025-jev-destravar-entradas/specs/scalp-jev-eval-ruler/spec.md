## ADDED Requirements

### Requirement: The multi-day Jev ruler is read-only and precedes every threshold change

The Farol SHALL provide `scripts/scalp_jev_eval.py`, a **read-only** evaluation instrument over the #1015 diagnostic log (`backend/scalp_jev_diagnostic.log`, overridable by `SCALP_JEV_LOG_FILE`) joined with realized prices at the 900 s horizon from the existing OHLCV storage. The instrument SHALL report: forecast versus realized with **non-overlapping** windows, segmentation by regime, accuracy of the +35 bp / −28 bp barriers, net expectancy per bucket of `score` and of `confidence`, and the calibration curve (`confidence` → |realized|). It SHALL NOT write product tables, trading state or any database. It SHALL run before any change of the confidence threshold or of the barrier geometry, and an insufficient sample SHALL be declared as such instead of being concluded.

#### Scenario: Multi-day report is produced from the diagnostic log

- **WHEN** the operator runs the ruler over a multi-day diagnostic log with the realized prices available
- **THEN** the report SHALL show forecast versus realized on non-overlapping 900 s windows, segmented by regime
- **AND** SHALL show barrier accuracy for +35 bp / −28 bp, net expectancy per `score` and `confidence` bucket, and the calibration curve

#### Scenario: Insufficient sample is declared, not concluded

- **WHEN** the available log does not cover enough non-overlapping 900 s windows for a bucket or a regime
- **THEN** the report SHALL declare the sample insufficient for that bucket or regime
- **AND** SHALL NOT present a conclusion about the threshold or the geometry from that sample

#### Scenario: No threshold change happens without the report

- **WHEN** a calibration of the confidence threshold or of the barrier geometry is proposed
- **THEN** the report from this requirement SHALL exist for the sample in question
- **AND** without it the current `CONFIDENCE_MIN`, `EXIT_TARGET_BP`, `EXIT_STOP_BP` and `HOLD_AFTER_FILL_S` SHALL stay unchanged

#### Scenario: The instrument is read-only

- **WHEN** the ruler runs
- **THEN** it SHALL NOT write to product tables, to the trading path, to the scalp state or to any new database
- **AND** it SHALL NOT require the scalp loop to be running
