# Refined Results Layout Design

## Objective
Reduce cognitive load on the Results Page by providing a high-level summary and comparison first, with details available on demand.

## Current Experience
- Displays all strategies immediately.
- Multiple charts and tables load at once.
- Hard to quickly identify the "winner" among multiple strategies.
- Infinite scroll feel makes it difficult to parse parameters.

## Proposed UX
### 1. Global Parameter Summary (Top)
A compact header block showing the context of the run.
- **Market**: Exchange, Symbol, Timeframes.
- **Period**: Start Date, End Date, Duration.
- **Strategies Run**: List of names (e.g., "MACD, RSI, SMA").
- **Cost**: Initial Capital, Fee, Slippage.

### 2. Comparison Grid (Main View)
The primary focus of the page. A card-based or table-based layout comparing strategies side-by-side.
- **Columns**: Strategy Name | Win Rate | Net Profit | Sharpe | Max DD | Trades.
- **Highlight**: The row/card with the highest Net Profit is highlighted as "Best Performer" (Gold border/trophy icon).
- **Visuals**: Sparkline for equity curve (optional, simple line).
- **Action**: Clicking a row/card opens the **Strategy Detail View**.

### 3. Strategy Detail View (Modal/Drawer)
When a user clicks a strategy in the grid:
- Opens a full-screen Modal or dedicated section.
- Displays the detailed interaction:
    - **Header**: Strategy specific metrics.
    - **Main Chart**: Candlestick + Signals + Equity.
    - **Trades Table**: Complete history.
    - **Indicators**: Specific indicator charts (RSI, MACD levels).

## Implementation Details
### Components
- `ResultsPage.tsx`: Refactor to manage state `selectedStrategy`.
- `RunSummary.tsx`: New component for the top header.
- `ComparisonGrid.tsx`: New component for the main table.
- `StrategyDetail.tsx`: Extracted from current `ResultsPage` logic to display single strategy data.

### Data Flow
1. Fetch `run` results.
2. Render `RunSummary`.
3. Compute `ComparativeMetrics` for all strategies.
4. Render `ComparisonGrid`.
5. If `selectedStrategy` is not null, render `StrategyDetail` (overlay or separate view).

## Benefits
- **Performance**: Heavy charts are not rendered until requested.
- **Clarity**: Users see the "bottom line" immediately.
- **Usability**: Easier to compare A/B tests.
