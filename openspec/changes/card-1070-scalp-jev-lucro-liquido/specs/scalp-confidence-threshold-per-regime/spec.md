## MODIFIED Requirements

### Requirement: The market regime comes from the window volatility against a single applied boundary

The market regime SHALL be derived from the window volatility (σ, `vol_bp`) against the **single regime boundary** stored on the consumed version (calm below it, active at or above it), the same boundary the backtest used, in the same units as `window.vol_bp`. That boundary SHALL be computed from the backtest volatility distribution; it SHALL NOT be a manual `SCALP_REGIME_BOUNDARY_BP` fill. When the consumed version has no boundary, or the boundary is invalid, both regimes SHALL be treated as **closed** (fail closed) instead of applying a threshold.

#### Scenario: The volatility decides the regime

- **WHEN** a cycle has a reply and the consumed version has a boundary and the window volatility is below that boundary
- **THEN** the cycle SHALL belong to the calm regime
- **AND** the policy of the calm regime SHALL be the one applied

#### Scenario: No boundary closes both regimes

- **WHEN** the consumed version has no regime boundary or the boundary is invalid
- **THEN** both regimes SHALL be closed
- **AND** the cycle SHALL close without an order with the closed-regime token
- **AND** a hand-filled `SCALP_REGIME_BOUNDARY_BP` SHALL NOT open the regimes

#### Scenario: Boundary comes from the backtest

- **WHEN** the offline backtest writes a version
- **THEN** that version SHALL store the volatility cut it used
- **AND** the live decision SHALL read that stored cut, not a process env default
