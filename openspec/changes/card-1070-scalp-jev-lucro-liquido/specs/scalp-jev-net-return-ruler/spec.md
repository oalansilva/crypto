## ADDED Requirements

### Requirement: Promotion net return is the backtest mean with interval above zero

The net-profit gate that allows a geometry to be applied SHALL be the offline backtest's mean net return per independent window, after the real fee path, with the 95% confidence-interval lower bound strictly above zero. The 200 independent windows of #1045 SHALL be counted in that backtest, per regime, not in the live log. A live DEV round trip SHALL NOT replace that gate.

#### Scenario: Interval below zero blocks promotion

- **WHEN** a candidate's backtest mean net return is positive but the 95% interval lower bound is not above zero
- **THEN** that geometry SHALL NOT be promoted
- **AND** the geometry in use SHALL stay

#### Scenario: Two hundred windows are backtest windows

- **WHEN** the report states the sample used for promotion
- **THEN** the 200-count SHALL refer to independent backtest windows per regime
- **AND** SHALL NOT treat live diagnostic-log windows as that count

## MODIFIED Requirements

### Requirement: The ruler declares whether the confidence separates good from bad cycles

The ruler SHALL declare, per regime, whether the confidence **separates** good from bad cycles in this sample, where the confidence separates if and only if there is a numeric threshold whose expected net return is strictly positive and strictly better than accepting every eligible cycle (threshold 0), with sufficient sample. When the confidence does not separate, the report SHALL say so explicitly and SHALL NOT record the threshold as **turned off** in order to operate. A set that does not pay SHALL keep the geometry in use and SHALL keep a numeric or closed confidence policy; it SHALL NOT open the filter to get fills.

#### Scenario: The confidence separates

- **WHEN** a threshold has a strictly positive expected net return and a strictly higher expected net return than accepting every eligible cycle
- **THEN** the report SHALL declare that the confidence separates in that regime
- **AND** the justified threshold SHALL be the one with the highest expected net return, expressed on the calibrated scale

#### Scenario: The confidence does not separate

- **WHEN** no threshold beats accepting every eligible cycle, or none has a strictly positive expected net return, with sufficient sample
- **THEN** the report SHALL declare explicitly that the confidence does not separate good from bad cycles in that regime
- **AND** the report SHALL NOT record the threshold as turned off as a way to send
- **AND** that regime SHALL stay closed or on the numeric policy already in use
