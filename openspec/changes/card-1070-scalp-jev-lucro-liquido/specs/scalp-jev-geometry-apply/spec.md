## ADDED Requirements

### Requirement: The applied version carries target, stop, prazo and regime cut with confidence

The apply step SHALL write one version fingerprint that includes the per-regime numeric confidence policy, the regime boundary, the target, the stop and the prazo. It SHALL promote that fingerprint only when the offline backtest shows a positive mean net return per independent window for that geometry whose 95% confidence-interval lower bound is above zero. The daily diagnosis SHALL promote or revert target, stop, prazo, regime cut and confidence together whenever that day's proof shows, or stops showing, net profit. It SHALL NOT turn the confidence filter off in order to send. While no geometry on BTCUSDT has that net-profit proof, the geometry in use SHALL stay and the change SHALL keep varying prazo, target and stop. Enabling calibration SHALL NOT turn the scalp switch on.

#### Scenario: A paying set is applied as one version

- **WHEN** the backtest of a candidate set has a positive mean net return per independent window and the 95% interval lower bound is above zero
- **THEN** the apply step SHALL write one version with target, stop, prazo, regime boundary and numeric confidence
- **AND** the next entry SHALL consume that version
- **AND** the confidence policy SHALL NOT be recorded as turned off

#### Scenario: Daily diagnosis moves the whole set

- **WHEN** the next closed-day diagnosis runs after a version is in force
- **THEN** it SHALL be allowed to promote or revert target, stop, prazo and regime cut together with confidence
- **AND** SHALL NOT change only confidence while leaving geometry and regime cut untouched

#### Scenario: No paying geometry keeps searching

- **WHEN** no candidate on BTCUSDT has a 95% interval lower bound above zero
- **THEN** the geometry in use SHALL stay
- **AND** the change SHALL continue to vary prazo, target and stop
- **AND** it SHALL NOT close with a visible refusal that the pair is not operable

### Requirement: DEV confirms with a ten-dollar round trip whose net P&L is on the screen

With a promoted version consumed by the scalper in DEV, the scalp SHALL send at least one post-only order of 10 dollars and SHALL close the buy-to-sell cycle. That first live round MAY close at a loss and SHALL still count. The net P&L of that round SHALL appear on `/monitor` even when negative. The net-profit gate required for promotion SHALL remain the backtest's, not the first live round's. T and clip SHALL NOT increase.

#### Scenario: A real DEV cycle shows net P&L even when negative

- **WHEN** the promoted version is in force in DEV and the user scalp switch is on
- **THEN** the bot SHALL send a post-only order of 10 dollars and close the round trip
- **AND** the module SHALL show that round's net P&L per trade even if it is negative
- **AND** a losing first round SHALL NOT undo the backtest net-profit requirement
