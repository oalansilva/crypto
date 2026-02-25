# Spec: Dev Auto-Itera (Backend)

**Capability:** backend  
**Type:** enhancement  
**Change:** dev-auto-iterate

---

## ADDED Requirements

### Requirement: Auto-iteration loop

**Description:** The system SHALL allow the Dev to iterate automatically on failed backtests before sending to Trader.

#### Scenario: 0 trades
- **Given** Dev runs backtest and total_trades = 0
- **When** auto-iteration is enabled
- **Then** Dev MUST adjust template and re-run backtest

---

### Requirement: Retry on bad metrics

**Description:** The system SHALL auto-adjust when holdout sharpe < min_sharpe or drawdown > max_drawdown.

#### Scenario: Sharpe too low
- **Given** holdout sharpe < threshold
- **When** Dev evaluates
- **Then** Dev MUST adjust and re-test

---

## MODIFIED Requirements

### Requirement: Dev output after refinement

**Description:** The system SHALL only send Dev summary to Trader after auto-iteration completes.

#### Scenario: Multi-iteration
- **Given** Dev runs 2+ iterations
- **When** final version ready
- **Then** Trader receives only refined version
