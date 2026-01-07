# Spec: Regime Analysis

## ADDED Requirements

### Requirement: Classify Market Regime
The system MUST classify each candle (or trade entry) into a market regime:
- **Bull**: Close > SMA(200)
- **Bear**: Close < SMA(200)
- **Sideways**: Optional refinement (e.g. ADX < 20).
#### Scenario:
Price is above 200 SMA. Regime is Bull.

### Requirement: Segment Performance by Regime
The system MUST aggregate trade performance (count, PnL, Win Rate) grouped by the regime active at the trade entry time.
#### Scenario:
10 trades entered when Price > SMA(200). 5 trades entered when Price < SMA(200). Result should show performance metrics for "Bull" (10 trades) and "Bear" (5 trades) separately.
