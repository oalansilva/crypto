# Capability: Strategy Execution

## ADDED Requirements

### Requirement: Re-Run Saved Strategy
The system MUST allow users to execute a backtest or optimization using the exact parameters stored in a favorite.

#### Scenario: Run Favorite
Given I am on the "Saved Strategies" page
And I have a saved strategy named "Test Strategy"
When I click the "Run" button for this strategy
Then I am redirected to the Backtest/Optimization page
And the Symbol, Strategy, Timeframe, Indicators, and Risk parameters are pre-filled with values from "Test Strategy".
