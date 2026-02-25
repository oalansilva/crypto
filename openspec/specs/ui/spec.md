# ui Specification

## Purpose
TBD - created by syncing delta from change ui-advanced-metrics.
## Requirements
### Requirement: Display Advanced Metrics Card
The UI MUST display a card for the "Best Result" containing:
- Expectancy ($ values)
- Max Consecutive Losses
- Avg ATR and ADX

#### Scenario:
User views optimization results. Next to "Best Return", there is a "Risk & Context" card showing "Expectancy: $15.5", "Max Streak Loss: 4", "Avg ATR: 105".

### Requirement: Display Regime Breakdown
The UI MUST display performance breakdown by regime (Bull/Bear) if available.
#### Scenario:
Inside the Advanced Metrics card (or separate), show "Bull: 60% WR", "Bear: 40% WR".

### Requirement: Lab Page Title
**Description:** The UI SHALL display the title “Agent Trader” on the /lab page header in place of “Strategy Lab”.

#### Scenario: Lab page header title
- **WHEN** the user opens the /lab page
- **THEN** the header title is rendered as “Agent Trader”

