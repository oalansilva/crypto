# strategy-comparison Specification

## Purpose
Enable side-by-side comparison of favorite strategies with visual highlighting of best performing metrics.

## Requirements

### Requirement: Compare Favorites
The system MUST allow side-by-side comparison of metrics from different favorites.

#### Scenario: Compare Two Strategies
Given I have two favorites "Aggressive" and "Conservative" and I am on the "Saved Strategies" page, When I select both and click "Compare", Then a comparison table is displayed with columns for each strategy and rows for Total Return, Sharpe Ratio, Max Drawdown.

### Requirement: Metrics Visualization
The interface MUST visually highlight the best performing metrics (e.g., highest Return, lowest Drawdown) in the comparison table.

#### Scenario: Highlight best metrics in comparison
- **GIVEN** a comparison table with multiple strategies
- **WHEN** the table is displayed
- **THEN** the highest Return is visually highlighted
- **AND** the lowest Drawdown is visually highlighted
- **AND** other best-in-class metrics are similarly highlighted
