# Backend Spec Delta

## ADDED Requirements

### Requirement: Auto Backtest Orchestration
The System SHALL provide an automated end-to-end backtest workflow that executes timeframe selection, parameter optimization, and risk management optimization sequentially without user intervention.
The System MUST return the final optimized configuration and automatically save it to the user's favorites with a timestamp note.

#### Scenario: User runs auto backtest for BTC/USDT with RSI
Given the user selects symbol "BTC/USDT" and strategy "RSI"
When the user triggers the auto backtest endpoint
Then the System SHALL:
1. Execute timeframe optimization across all default timeframes
2. Select the best timeframe based on Sharpe Ratio
3. Execute parameter grid search on the selected timeframe
4. Select the best parameter combination
5. Execute stop-loss/take-profit optimization
6. Select the best risk configuration
7. Save the final configuration to favorites with note "Auto-selected on [DATE]"
And return the run_id and status to the user

#### Scenario: Progress tracking during auto backtest
Given an auto backtest is running
When the user queries the status endpoint
Then the System MUST return:
- Current stage (1/3, 2/3, or 3/3)
- Stage description ("Optimizing timeframes", "Optimizing parameters", "Optimizing risk")
- Progress percentage (e.g., 33%, 66%, 100%)

### Requirement: Stage Result Logging
The System SHALL persist detailed logs of each optimization stage to `backend/full_execution_log.txt` using the existing logging format.
Each stage log MUST include timestamps, stage identifier, and key results.

#### Scenario: View auto backtest execution log
Given an auto backtest has completed
When the administrator views `backend/full_execution_log.txt`
Then the file MUST contain entries like:
- `[2026-01-17 14:00:00] AUTO_BACKTEST - Stage 1 started - Symbol: BTC/USDT, Strategy: RSI`
- `[2026-01-17 14:02:30] AUTO_BACKTEST - Stage 1 completed - Best timeframe: 1d (Sharpe: 2.5)`
- `[2026-01-17 14:02:31] AUTO_BACKTEST - Stage 2 started - Testing 15 combinations`
- `[2026-01-17 14:05:00] AUTO_BACKTEST - Stage 2 completed - Best params: {period: 14}`
- `[2026-01-17 14:10:00] AUTO_BACKTEST - Final: Saved to favorites (ID: 123)`

### Requirement: Error Handling and Recovery
The System SHALL gracefully handle failures at any optimization stage and provide clear error feedback to the user.
The System MUST save partial logs when a stage fails for debugging purposes.

#### Scenario: Stage failure during execution
Given an auto backtest is running
When Stage 2 (parameter optimization) fails due to API timeout
Then the System SHALL:
- Stop the entire process immediately
- Set status to "FAILED"
- Display error message: "Stage 2 failed: API timeout"
- Save partial log with Stage 1 results and error details
- Allow user to retry from Stage 2 or restart completely

### Requirement: Process Cancellation
The System SHALL allow users to cancel a running auto backtest at any time.

#### Scenario: User cancels auto backtest mid-execution
Given an auto backtest is running at Stage 2
When the user clicks "Cancel" button
Then the System SHALL:
- Terminate the current stage gracefully
- Set status to "CANCELLED"
- Save partial execution log
- Return user to input form

### Requirement: Input Validation
The System SHALL validate user inputs before starting the auto backtest workflow.

#### Scenario: Invalid symbol with insufficient data
Given the user selects symbol "NEWCOIN/USDT" with only 30 days of history
When the user clicks "Run Auto Backtest"
Then the System SHALL:
- Display error: "Insufficient data for NEWCOIN/USDT (minimum: 1 year)"
- Prevent form submission
- Keep user on input page

### Requirement: Execution History
The System SHALL persist all auto backtest executions and allow users to view past runs.

#### Scenario: View execution history
Given the user has run 3 auto backtests in the past week
When the user navigates to `/backtest/auto/history`
Then the System SHALL display a table with:
- Columns: Timestamp, Symbol, Strategy, Status, Actions
- Each row showing execution metadata
- "View Results" button to re-open results page

### Requirement: Default Configuration Values
The System SHALL use consistent default values for fee and slippage across all auto backtest executions.

#### Scenario: Fee and slippage defaults
Given a user runs an auto backtest
When the system executes each stage
Then it MUST use:
- Fee: 0.00075 (0.075% - Binance standard)
- Slippage: 0 (disabled - TradingView alignment)
- Selection criteria: Sharpe Ratio
