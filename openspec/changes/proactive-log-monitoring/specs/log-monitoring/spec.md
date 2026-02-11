# Capability: Dev-Stage Proactive Error Correction

## ADDED Requirements

### Requirement: Dev auto-correction step
**Description:** The Dev stage MUST run a pre-execution normalization step before launching the backtest.

#### Scenario: Dev pre-exec normalization
Given the Dev stage receives a strategy_draft with inputs
When the Dev prepares the backtest request
Then it MUST normalize timeframe and symbol before execution.

### Requirement: Auto-correct common interval format issues
**Description:** The system MUST normalize common timeframe formats before requesting data (e.g., `4H` -> `4h`).

#### Scenario: Normalize uppercase timeframe
Given a run input contains timeframe "4H"
When the Dev prepares the exchange request
Then it MUST send "4h" to the exchange without failing.

### Requirement: Auto-correct common symbol format issues
**Description:** The system MUST normalize common symbol formats before requesting data (e.g., `BTC/USDT` -> `BTCUSDT` for Binance).

#### Scenario: Normalize slashed symbol
Given a run input contains symbol "BTC/USDT"
When the Dev prepares the exchange request
Then it MUST send "BTCUSDT" to the exchange without failing.

### Requirement: Detect runtime download errors
**Description:** The system MUST detect download/runtime errors for lab runs (e.g., exchange download failures) and classify them into a known error type.

#### Scenario: Invalid interval from exchange
Given a lab run enters execution and the exchange client returns an "Invalid interval" error
When the system processes the error
Then the run diagnostic MUST include type "invalid_interval" and a human-readable message.

### Requirement: Expose run diagnostic via API
**Description:** The system MUST include a diagnostic object in the lab run API response when a classified error is detected.

#### Scenario: API returns diagnostic
Given a run has a classified error
When the client requests `/api/lab/runs/{run_id}`
Then the response MUST include `diagnostic.type` and `diagnostic.message`.

### Requirement: Persist diagnostic in run log
**Description:** The system MUST persist the diagnostic summary in the run log for later inspection.

#### Scenario: Diagnostic persisted
Given a classified error occurred for a run
When the system writes run logs
Then the diagnostic summary MUST be stored with the run data.
