## ADDED Requirements

### Requirement: Discovery GO/NO-GO uses a Discovery criteria profile

The Discovery walk-forward seal SHALL be evaluated with a Discovery criteria profile, not with the Combo profile (`DEFAULT_CRITERIA` 100 in-sample trades / Sharpe 0.8, `OOS_CRITERIA` 20 holdout trades / Sharpe 0.30, nor the 50% Sharpe retention gate). Combo save-favorite SHALL keep that Combo profile unchanged.

On a Discovery result that is ranking-eligible (≥ 30 in-sample closed trades and ≥ 90% coverage of the train window), the persisted `oos_verdict.status` SHALL be:

- `GO` when the in-sample portrait is decent (Calmar ≥ 1, profit factor ≥ 1.5, max drawdown ≤ 35%) **and** holdout Sharpe is finite and **> 0**;
- `NO-GO` when holdout Sharpe is ≤ 0, **or** the holdout Sharpe metric is missing/null/`NaN`/infinite (fail-closed), **or** the row is eligible but the in-sample portrait fails Calmar 1, profit factor 1.5, or max drawdown 35% — even if holdout Sharpe is positive.

The same rule SHALL apply to every Discovery line of the sweep (4h and 1d, long and short, any template). Reasons SHALL name the segment (`Treino` vs `Holdout`), the observed value and the threshold. A training-portrait failure SHALL be attributed to treino, not only to holdout.

Eligibility, Calmar ranking, coverage policy, split 70/30, Preflight, worker, templates and Promover SHALL remain as today. `NO-GO` SHALL NOT lock Promover. New sweeps (and a sweep still running after deploy) SHALL persist the new seal; already `completed` sweeps SHALL NOT be recalculated.

#### Scenario: BTC 1d long eligible becomes GO

- **GIVEN** eligible BTC/USDT 1d long `RS-E0E30719CC` with 43 in-sample trades, Sharpe ~0,50, Calmar ~10,6, 24 holdout trades and Sharpe OOS ~0,35
- **WHEN** Discovery evaluates the seal with the Discovery profile
- **THEN** `oos_verdict.status` is `GO`
- **AND** the Combo floors 100 trades / Sharpe 0,8 are not the reason

#### Scenario: Eligible holdout Sharpe ≤ 0 is NO-GO

- **GIVEN** an eligible Discovery row whose holdout Sharpe is negative (example AGLD/AUCTION)
- **WHEN** Discovery evaluates the seal
- **THEN** `oos_verdict.status` is `NO-GO`
- **AND** a reason identifies Holdout, the observed Sharpe and the threshold `> 0`

#### Scenario: Eligible weak training portrait is NO-GO on treino

- **GIVEN** an eligible Discovery row with finite holdout Sharpe > 0
- **AND** the in-sample portrait fails Calmar ≥ 1, profit factor ≥ 1,5 or max drawdown ≤ 35%
- **WHEN** Discovery evaluates the seal
- **THEN** `oos_verdict.status` is `NO-GO`
- **AND** a reason identifies Treino, the observed value and the failed threshold
- **AND** the reason is not only Holdout

#### Scenario: Missing holdout Sharpe is fail-closed NO-GO

- **GIVEN** an eligible Discovery row whose holdout Sharpe is missing, null, `NaN` or infinite
- **WHEN** Discovery evaluates the seal
- **THEN** `oos_verdict.status` is `NO-GO`
- **AND** a reason identifies Holdout and the invalid metric

#### Scenario: Same rule on 4h and short

- **GIVEN** an eligible 4h or short Discovery row (any template) that meets the Discovery GO bar
- **WHEN** Discovery evaluates the seal
- **THEN** the row receives `GO` by the same rule as 1d long
- **AND** a 4h or short row that fails the same bar receives `NO-GO`

#### Scenario: Completed sweeps are not backfilled

- **GIVEN** a Discovery sweep already `completed` before deploy
- **WHEN** the operator opens Decidir of that sweep
- **THEN** the persisted Combo-era `oos_verdict` is left as stored
- **AND** this change does not recalculate that sweep
