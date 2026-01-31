# Capability: Strategy Comparison

## ADDED Requirements

### Requirement: Compare Favorites
The system MUST allow side-by-side comparison of metrics from different favorites.

#### Scenario: Compare Two Strategies
Given I have two favorites "Aggressive" and "Conservative"
And I am on the "Saved Strategies" page
When I select both "Aggressive" and "Conservative"
And I click "Compare"
Then a comparison table is displayed showing columns for each strategy
And rows for metrics like "Total Return", "Sharpe Ratio", "Max Drawdown".

### Requirement: Metrics Visualization
The interface MUST visually highlight the best performing metrics (e.g., highest Return, lowest Drawdown) in the comparison table.

#### Scenario: Verify Highlighting
Given the Comparison view is open
When I view the "Total Return" row
Then the higher return value is visually highlighted (e.g., bold or green).
