# Proposal: Add Favorite Strategies System

## Problem
Users encounter successful configuration sets during optimization or backtesting but lack a persistent way to save them. Re-running a successful strategy requires manually noting down parameters (symbol, timeframe, indicators, risk settings) and re-entering them. Comparing metrics between different successful runs is also manual and difficult.

## Solution
Implement a "Favorite Strategies" system that persists configuration states and execution metrics. This enables:
1.  **Persistence**: Saving specific parameter combinations with a custom user-defined name.
2.  **Management**: A dedicated dashboard to view, rename, and delete saved strategies.
3.  **Re-execution**: One-click restoration of parameters into the backtester/optimizer to run the strategy again.
4.  **Comparison**: Side-by-side comparison of key performance metrics (Sharpe, Return, Drawdown) for selected favorites.

## Scope
-   **Backend**: 
    -   New SQLite table `favorite_strategies`.
    -   API CRUD endpoints at `/api/favorites`.
-   **Frontend**:
    -   "Save to Favorites" button in Results tables.
    -   "Saved Strategies" Dashboard page.
    -   "Compare" view/modal.

## Risks
-   **Schema Evolution**: If indicator parameters change structure in the future, saved JSON blobs might become incompatible. *Mitigation: Store versioning in the saved JSON or handle migration logic on load.*
