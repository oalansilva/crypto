## MODIFIED Requirements

### Requirement: The market regime comes from the window volatility against a single applied boundary

The market regime SHALL be derived from the window volatility (σ, `vol_bp`) against the **single regime boundary** stored on the consumed version (calm below it, active at or above it), in the same units as `window.vol_bp`. That stored boundary SHALL be the one the live cycle reads from the applied version, not a manual `SCALP_REGIME_BOUNDARY_BP` fill. When the consumed version has no boundary, or the boundary is invalid, both regimes SHALL be treated as **closed** (fail closed) instead of applying a threshold.

For **daily diagnosis**, when no prior version supplies a boundary, the boundary that opens regime measurement SHALL come from bootstrap on finite `vol_bp` in the real diagnostic log (`compute_regime_boundary_bp`), distinct from the volatility cut computed on the **offline synthetic replay** used only for net-profit promotion. The offline backtest boundary SHALL NOT replace that log-measured boundary on the declared or activated version bundle.

#### Scenario: The volatility decides the regime

- **WHEN** a cycle has a reply and the consumed version has a boundary and the window volatility is below that boundary
- **THEN** the cycle SHALL belong to the calm regime
- **AND** the policy of the calm regime SHALL be the one applied

#### Scenario: No boundary closes both regimes

- **WHEN** the consumed version has no regime boundary or the boundary is invalid
- **THEN** both regimes SHALL be closed
- **AND** the cycle SHALL close without an order with the closed-regime token
- **AND** a hand-filled `SCALP_REGIME_BOUNDARY_BP` SHALL NOT open the regimes

#### Scenario: Diagnosis measures boundary from the real log

- **WHEN** the closed-day diagnosis runs and finite `vol_bp` in the real log yields a bootstrap cut via `compute_regime_boundary_bp`
- **THEN** the diagnosis summary and persisted panel SHALL show that measured `regime_boundary_bp`
- **AND** activating a version for that cut SHALL use numeric confidence in use and factory geometry without promoting geometry from offline backtest profit proof
- **AND** the absent-boundary block SHALL NOT remain the visible reason once the measurement is stored

#### Scenario: Promotion backtest boundary is separate

- **WHEN** the offline backtest writes a promotable geometry bundle
- **THEN** that version MAY store the volatility cut from the synthetic replay sample
- **AND** automatic promotion SHALL NOT overwrite a log-measured boundary on the declared bundle with the offline replay cut when the summary already carries the log measurement
