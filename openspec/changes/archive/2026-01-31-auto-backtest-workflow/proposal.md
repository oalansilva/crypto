# Auto End-to-End Backtest Workflow

## Problem
Currently, users must manually navigate through multiple screens and click through each optimization stage:
1. Select symbol → **Timeframe Optimization** → Select best timeframe
2. Navigate to **Parameter Optimization** → Wait for results → Select best combination
3. Navigate to **Risk Management (Stop/Take)** → Wait for results → Select best stop/take
4. Manually click "Save to Favorites"

This workflow requires **15+ clicks** and **3-5 minutes** of waiting and manual intervention. Users want a "one-click" solution.

## Solution
Create an **"Auto Backtest"** feature that executes the entire optimization pipeline automatically:

**User Input:**
- Select **Symbol** (e.g., BTC/USDT)
- Select **Strategy** (e.g., RSI, MACD)
- Click **"Run Auto Backtest"**

**System Actions (Automatic):**
1. **Stage 1**: Test all timeframes (`5m, 15m, 30m, 1h, 2h, 4h, 1d`) with default strategy parameters → Select best timeframe by Sharpe Ratio
2. **Stage 2**: Run parameter grid search on the selected timeframe:
   - Fetch strategy schema from `/api/strategies/metadata`
   - Auto-generate ranges: `min = default * 0.5`, `max = default * 1.5` (same logic as ParameterOptimizationPage)
   - Example: RSI `period=14` → Test `[7, 8, 9, ..., 21]`
3. **Stage 3**: Run stop-loss/take-profit optimization grid:
   - Stop grid: `[1%, 2%, 3%, 4%, 5%]`
   - Take grid: `[1%, 2%, 3%, 4%, 5%, 7.5%, 10%]`
   - (Same values as `STOP_GAIN_OPTIONS` in RiskManagementOptimizationPage)
4. **Stage 4**: Auto-save the final best configuration to **Favorites** with note: `"Auto-selected on YYYY-MM-DD"`

**Technical Approach:**
- **Backend**: Minimal orchestrator endpoint `POST /api/backtest/auto` that sequentially calls existing endpoints:
  - **Stage 1**: `POST /optimize/sequential/timeframe` (already exists)
  - **Stage 2**: `POST /backtest/optimize` (already exists)
  - **Stage 3**: `POST /optimize/sequential/risk` (already exists)
  - **Auto-save**: `POST /favorites` (already exists)
  - **Orchestrator logic**: Parse response from each stage → Extract best result → Pass to next stage
- **Logging**: Append stage results to `backend/full_execution_log.txt` (same format as existing logs):
  - `[TIMESTAMP] AUTO_BACKTEST - Stage 1 started - Symbol: BTC/USDT, Strategy: RSI`
  - `[TIMESTAMP] AUTO_BACKTEST - Stage 1 completed - Best timeframe: 1d (Sharpe: 2.5)`
  - `[TIMESTAMP] AUTO_BACKTEST - Stage 2 started - Testing 15 parameter combinations`
  - `[TIMESTAMP] AUTO_BACKTEST - Stage 2 completed - Best params: {period: 14, oversold: 30}`
  - `[TIMESTAMP] AUTO_BACKTEST - Stage 3 started - Testing 35 stop/take combinations`
  - `[TIMESTAMP] AUTO_BACKTEST - Stage 3 completed - Best config: stop=2%, take=5%`
  - `[TIMESTAMP] AUTO_BACKTEST - Final: Saved to favorites (ID: 123)`
- **Frontend**: 
  - **Input Page** (`/backtest/auto`): Simple form with symbol + strategy selectors and "Run" button
  - **Results Page** (`/backtest/auto/results/:runId`): Real-time progress display with:
    - **Stage Progress Bar**: Visual indicator (Stage 1/3, 2/3, 3/3)
    - **Stage 1 Card**: Expandable table showing all timeframe results (currently testing/completed)
    - **Stage 2 Card**: Expandable table showing parameter combinations (starts after Stage 1)
    - **Stage 3 Card**: Expandable table showing stop/take combinations (starts after Stage 2)
    - **Final Result Card**: Highlighted card showing the auto-selected favorite configuration
- **Result**: Auto-redirect to Favorites after completion, with animation highlighting the new entry

## Error Handling & Resilience
- **Stage Failure**: If any stage (1, 2, or 3) fails (timeout, invalid data, API error):
  - Abort the entire process immediately
  - Display clear error message on results page
  - Save partial log (successful stages + error details) for debugging
  - Allow user to retry from failed stage or restart completely
- **Validation**: Before starting, validate:
  - Symbol has sufficient historical data (>1 year)
  - Strategy is compatible with requested workflow
  - All required parameters are available

## Process Control
- **Cancellation**: User can cancel running auto-backtest at any time
  - "Cancel" button on results page during execution
  - Backend endpoint: `DELETE /api/backtest/auto/:runId`
  - Status changes to "CANCELLED" and process terminates gracefully
- **Execution History**: Page `/backtest/auto/history` showing:
  - List of all past auto-backtests (timestamp, symbol, strategy, status)
  - Status: `completed`, `failed`, `cancelled`
  - "View Results" button to re-open results page with full logs
  - Filter by date range, symbol, or status

## Configuration Defaults
- **Fee**: `0.00075` (0.075% - Binance standard) - always enabled
- **Slippage**: `0` (disabled by default - TradingView alignment)
- **Selection Criteria**: Sharpe Ratio (hardcoded for MVP)
- Future: Allow user to configure these in "Advanced Options" section

## Risks
- **Long Execution Time**: Full pipeline could take 5-10 minutes for complex grids
  - Mitigation: Show real-time progress indicator (Stage 1/3, Stage 2/3, etc.)
- **Suboptimal Defaults**: Auto-selection might not align with user's risk tolerance
  - Mitigation: Allow users to configure "selection criteria" (e.g., prefer Sharpe > Win Rate)
