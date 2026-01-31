# strategy-comparison Specification

## Purpose
TBD - created by syncing delta from change add-favorite-strategies. Side-by-side comparison of favorites.

## Requirements

### Requirement: Compare Favorites
The system MUST allow side-by-side comparison of metrics from different favorites.

#### Scenario: Compare Two Strategies
Given I have two favorites "Aggressive" and "Conservative" and I am on the "Saved Strategies" page, When I select both and click "Compare", Then a comparison table is displayed with columns for each strategy and rows for Total Return, Sharpe Ratio, Max Drawdown.

### Requirement: Metrics Visualization
The interface MUST visually highlight the best performing metrics (e.g., highest Return, lowest Drawdown) in the comparison table.
