# Capability: Favorites Management

## ADDED Requirements

### Requirement: CRUD Operations
The system MUST support creating, reading, and deleting favorite strategies.

#### Scenario: Save New Favorite
Given I am on the "Optimization Results" page
And I see a profitable result
When I click the "Save" button
And I enter the name "Super BTC Strat"
Then the strategy configuration AND its results metrics are saved to the persistent store.

#### Scenario: List Favorites
Given I have saved multiple strategies
When I navigate to the "Saved Strategies" page
Then I see a list of all saved strategies with their Name, Symbol, and key metrics (Return, Sharpe).

#### Scenario: Delete Favorite
Given I am on the "Saved Strategies" page
When I click "Delete" on a strategy
Then it is removed from the list permanently.
