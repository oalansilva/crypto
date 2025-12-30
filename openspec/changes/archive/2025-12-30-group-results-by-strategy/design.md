# Proposal: Group Results by Strategy

## Objective
Restructure the `ResultsPage.tsx` to group backtest data by **Strategy**. Instead of separating charts, metrics, and tables into distinct global sections, each strategy will have its own dedicated section containing its specific statistics, price chart, and trade history. A unified comparison grid will be added at the bottom to facilitate cross-strategy analysis.

## Current vs Proposed Layout

| Section | Current | Proposed |
| :--- | :--- | :--- |
| **Organization** | By Component (All Charts -> All Metrics -> All Tables) | **By Strategy** (Strategy A [Stats, Chart, Table] -> Strategy B [...]) |
| **Strategy Details** | Scattered across page | **Unified** in a single block per strategy |
| **Comparison** | Implicit via side-by-side cards | **Explicit** Comparison Grid at the bottom |

## Detailed Design

### 1. Global Header
*   Retain existing dataset information (Symbol, Candle Count, Date).

### 2. Strategy Blocks (Repeated for each Strategy)
For each strategy (e.g., `sma (1d)`, `macd (4h)`):

*   **Header**: Strategy Name and Timeframe.
*   **Metrics Summary**: A condensed view displaying key performance indicators:
    *   Total Return (%)
    *   Max Drawdown (%)
    *   Sharpe Ratio
    *   Win Rate (%)
    *   Total Trades
    *   Final Balance ($)
*   **Price Chart**: The `CandlestickChart` component displaying price action and buy/sell markers specific to this strategy.
*   **Trade History**: The `TradesTable` component listing individual trades for this strategy.

### 3. Global Comparison Section (Footer)
*   **Combined Equity Curve**: A chart plotting the equity curves of all strategies on a single timeline (retained from current design but moved to comparison section).
*   **Comparison Grid**: A new table/grid component summarising the metrics of all executed strategies side-by-side for quick ranking and comparison.

## Implementation Steps

1.  **Refactor `ResultsPage.tsx`**:
    *   Iterate through `result.results` entries as the primary structural loop.
    *   Inside the loop, render the Metrics, Chart, and Table for the current strategy.
2.  **Create `ComparisonGrid` Component**:
    *   Implement a new UI component to render the summary matrix at the bottom of the page.
3.  **Move Equity Chart**:
    *   Relocate the combined Equity Curve to the "Comparison Section" at the bottom (or top, depending on final preference, but bottom fits the "summary" flow).

## User Story / Experience

1.  User lands on Results Page.
2.  User sees **Strategy A**:
    *   Immediately sees it made -87.11% Return.
    *   Sees the Price Chart to understand *where* it bought/sold.
    *   Sees the Trade History to verify individual execution.
3.  User scrolls to **Strategy B**:
    *   Sees it made -99.50% Return.
    *   Sees specific chart and trades.
4.  User reaches bottom:
    *   Sees a **Comparison Grid** listing Strategy A vs Strategy B to confirm which performed better overall.
