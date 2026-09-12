# monitor-telegram-alerts Specification

## Purpose
Internal Monitor Telegram alerting for curated Monitor opportunities.
## Requirements
### Requirement: Internal Monitor Telegram alerts
The system SHALL generate Monitor Telegram alert drafts from Monitor opportunities and SHALL send position-aware alerts as individual DMs to each eligible linked user when alerting is enabled and fully configured.

#### Scenario: Enabled alert sends to user's linked DM
- **WHEN** Monitor Telegram alerts are enabled with a bot token
- **AND** a user has linked Telegram and opted in
- **AND** a relevant opportunity changes per the position-aware matrix for that user
- **THEN** the system SHALL send a standardized alert message to that user's DM
- **AND** the message SHALL include symbol, timeframe, strategy, previous reading, new reading, severity, context, and educational disclaimer

#### Scenario: External beta group is not targeted
- **WHEN** the system sends a Monitor Telegram alert
- **THEN** it SHALL use only the user's linked DM destination
- **AND** it SHALL NOT send directly to the beta testers group
- **AND** it SHALL NOT send position-aware alerts to the internal Grupo Crypto topic

#### Scenario: Missing user link skips send for that user
- **WHEN** a user has not linked Telegram or has alerts disabled
- **THEN** the system SHALL NOT send position-aware alerts to that user
- **AND** other eligible users SHALL still be processed

#### Scenario: Missing bot token uses dry run
- **WHEN** Monitor Telegram alerts are enabled but bot token is missing
- **THEN** the system SHALL NOT call Telegram
- **AND** it SHALL record candidate alerts as dry run results

### Requirement: Alert anti-noise controls
The system SHALL prevent repeated or excessive Monitor Telegram alerts through deduplication and rate limiting **per user**, including position-aware alerts and operational Binance failure notices.

#### Scenario: Duplicate status inside minimum window is skipped per user
- **WHEN** an alert for the same user, symbol, timeframe, and status was already recorded inside the configured minimum repeat window
- **THEN** the system SHALL skip sending a duplicate alert to that user
- **AND** it SHALL record or report the skip reason as duplicate

#### Scenario: Rate limit caps messages per user per window
- **WHEN** a user has reached the configured maximum alert count for the current rate-limit window
- **THEN** the system SHALL skip additional sends to that user
- **AND** it SHALL report the skip reason as rate limited

#### Scenario: Operational Binance failure DM is rate limited per user
- **WHEN** multiple cron scans fail Binance wallet sync for the same user within the rate-limit window
- **THEN** the system SHALL send at most one operational failure DM per user per window

### Requirement: Alert audit trail
The system SHALL persist an audit trail for every sent or dry-run Monitor Telegram alert attempt, including the recipient user and destination chat.

#### Scenario: Alert attempt is audited per user
- **WHEN** the system processes a sendable alert for user U
- **THEN** it SHALL persist user identifier, destination chat id, symbol (when applicable), timeframe, previous/new status, severity, send result, payload hash, and source
- **AND** the audit row SHALL be usable for per-user deduplication

#### Scenario: Telegram send failure is audited
- **WHEN** Telegram delivery fails for a user
- **THEN** the system SHALL record the failure status and error text
- **AND** it SHALL NOT stop processing other users' alerts

### Requirement: Administrative execution path
The system SHALL provide an admin-only backend execution path to run a Monitor Telegram alert scan manually.

#### Scenario: Admin triggers scan
- **WHEN** an authenticated admin calls the alert scan endpoint
- **THEN** the system SHALL run one Monitor alert scan
- **AND** return counts for candidates, sent, dry-run, duplicates, rate-limited, skipped, and failed alerts

#### Scenario: Non-admin cannot trigger scan
- **WHEN** a non-admin user calls the alert scan endpoint
- **THEN** the system SHALL reject the request using the existing admin authentication dependency

### Requirement: Daily scanner exposes safe operational diagnostics
The Monitor Telegram alert scanner SHALL expose safe diagnostics including per-user skip reasons and portfolio sync state.

#### Scenario: Scanner reports multi-user summary
- **WHEN** a position-aware Monitor Telegram alert scan runs
- **THEN** the scan result SHALL include counts of eligible users, sent, skipped, suppressed, and failed alerts
- **AND** it SHALL NOT include bot tokens or unrelated users' chat ids in admin diagnostics

#### Scenario: Scanner reports portfolio sync state per user safely
- **WHEN** Binance wallet sync fails for one or more users
- **THEN** the scan result SHALL report how many users were paused due to sync failure
- **AND** it SHALL NOT expose raw Binance credentials

#### Scenario: Scanner explains suppressed transitions
- **WHEN** a transition is suppressed by the position-aware matrix for a user
- **THEN** the scan result MAY report symbol, timeframe, user count suppressed, and reason `suppressed_by_position_matrix`

### Requirement: Daily scanner keeps delivery failures visible
The operational scanner SHALL return a failed process result when Telegram delivery fails.

#### Scenario: Telegram failure returns non-zero from cron script
- **WHEN** the scanner records one or more failed sends
- **THEN** the cron script SHALL print a failure summary without secrets
- **AND** the cron script SHALL exit with non-zero status

### Requirement: Monitor Telegram scan does not read OpenClaw secrets
The Monitor Telegram scan job SHALL load bot token and destination from canonical Cripto/Hermes secret paths or environment, not from `/root/.openclaw/secrets` or an `openclaw-cron` identity.

#### Scenario: Scan runs without OpenClaw home
- **WHEN** `/root/.openclaw` is absent or unreadable
- **THEN** the scan still resolves configuration from the canonical path
- **AND** it SHALL NOT fail solely because OpenClaw home is missing

### Requirement: Position-aware Monitor Telegram alerts per user
The system SHALL send Monitor Telegram alerts as individual DMs to each eligible user when a status transition is relevant to that user's real Spot portfolio position and Em portfólio scope.

#### Scenario: Bought user receives sell alert on HOLD to EXIT
- **WHEN** a symbol is in the user's Em portfólio scope (`inPortfolio=true`)
- **AND** the user holds an eligible Spot position in the symbol's base asset (`min_usd=1`)
- **AND** any eligible catalog strategy for that symbol (`notify_telegram=true`) changes public status from `HOLD` to `EXIT`
- **THEN** the system SHALL send a DM to that user's linked Telegram chat
- **AND** the message SHALL include symbol, strategy/timeframe, previous reading Compra, and new reading Venda
- **AND** the message SHALL include the educational disclaimer

#### Scenario: Bought user receives stop sell alert with Motivo=Stop
- **WHEN** a symbol is in the user's Em portfólio scope
- **AND** the user holds an eligible Spot position
- **AND** an eligible strategy changes to public status `EXIT` due to stop loss (`STOPPED_OUT` / `stop_breached_now`)
- **THEN** the system SHALL send a DM to that user's chat with new reading Venda
- **AND** the message SHALL include `Motivo=Stop`

#### Scenario: Flat user receives buy alert on EXIT to HOLD
- **WHEN** a symbol is in the user's Em portfólio scope
- **AND** the user has no eligible Spot position (flat)
- **AND** an eligible strategy changes public status from `EXIT` to `HOLD`
- **THEN** the system SHALL send a DM to that user's chat with previous reading Venda and new reading Compra

#### Scenario: Flat user suppresses HOLD to EXIT
- **WHEN** a user is flat for a symbol in scope
- **AND** an eligible strategy changes from `HOLD` to `EXIT`
- **THEN** the system SHALL NOT send a position-aware alert to that user

#### Scenario: Bought user suppresses EXIT to HOLD re-entry
- **WHEN** a user holds an eligible Spot position
- **AND** an eligible strategy changes from `EXIT` to `HOLD` while the position remains
- **THEN** the system SHALL NOT send a position-aware alert to that user

#### Scenario: Two users with different positions receive different alerts
- **WHEN** user A holds Spot position for symbol X and user B is flat for symbol X
- **AND** an eligible strategy for X changes from `HOLD` to `EXIT`
- **THEN** user A SHALL receive a sell DM
- **AND** user B SHALL NOT receive a position-aware alert for that transition

#### Scenario: Strategy is_holding is not used as portfolio proxy
- **WHEN** the scanner evaluates whether a user is bought
- **THEN** it SHALL use that user's Spot wallet / derived `in_portfolio` rules
- **AND** it SHALL NOT use strategy `is_holding` as a proxy

### Requirement: Em portfólio scope resolution per user
The position-aware scanner SHALL resolve Em portfólio scope per user using the same rules as Monitor UI `portfolioStatusBySymbol.inPortfolio`.

#### Scenario: Crypto with Binance uses derived portfolio rule per user
- **WHEN** the symbol is a rated crypto asset and the user has Binance credentials configured
- **THEN** `inPortfolio` for that user SHALL be true when they hold an eligible Spot balance of the base asset

#### Scenario: Non-derived symbols use manual preference per user
- **WHEN** the derived portfolio rule is not active for a user and symbol
- **THEN** `inPortfolio` SHALL follow that user's stored `MonitorPreference.in_portfolio`

#### Scenario: Scope intersects monitored catalog
- **WHEN** the scanner builds candidates for a user
- **THEN** it SHALL consider only symbols in the admin curated catalog with at least one `notify_telegram=true` strategy
- **AND** apply the Em portfólio filter for that user before the position-aware matrix

### Requirement: Binance unavailability operational alert per user
The system SHALL pause position-aware alerts for a user and notify them individually when that user's Binance wallet sync fails during a cron scan.

#### Scenario: Binance failure sends rate-limited operational DM to user
- **WHEN** the cron scan cannot fetch a user's Binance Spot balances
- **THEN** the system SHALL send one operational DM to that user's linked chat stating wallet sync is unavailable and position-aware alerts are paused
- **AND** the operational DM SHALL be rate limited per user

#### Scenario: Binance failure suppresses only that user's position-aware alerts
- **WHEN** Binance wallet sync fails for user A but succeeds for user B in the same scan
- **THEN** user A SHALL NOT receive position-aware signal alerts in that scan
- **AND** user B SHALL continue to receive alerts normally

### Requirement: Position-aware destination is individual user DM only
Position-aware Monitor Telegram alerts SHALL be delivered only to each eligible user's linked Telegram DM and SHALL NOT be sent to the internal Grupo Crypto topic.

#### Scenario: Each alert uses the user's linked chat id
- **WHEN** a position-aware alert is sent to user U
- **THEN** the destination SHALL be U's persisted `telegram_chat_id`
- **AND** the system SHALL NOT send the alert to `Grupo Crypto` or its `Crypto` thread

#### Scenario: Legacy group destination disabled for position-aware events
- **WHEN** the position-aware scanner runs
- **THEN** it SHALL NOT use the legacy `Grupo Crypto` destination for signal or stop alerts covered by this card

### Requirement: Direct Telegram Bot API delivery
The system SHALL send Monitor Telegram alerts using the Telegram Bot API directly from Cripto Farol without Hermes middleware.

#### Scenario: sendMessage uses Cripto bot token
- **WHEN** the scanner sends an alert
- **THEN** it SHALL call Telegram `sendMessage` with the Cripto-configured bot token
- **AND** it SHALL NOT route through Hermes gateway services

### Requirement: Product systemd timer wakes the daily Monitor Telegram scan
The daily Monitor Telegram alert scan SHALL be started by a product systemd oneshot+timer on the Cripto Farol host, without an LLM agent and without the Hermes cron as the wake path.

#### Scenario: Calendar fire runs the product scan
- **WHEN** the product timer fires at 08:05 BRT (OnCalendar 11:05 UTC)
- **THEN** the scan SHALL run `ops/run_monitor_telegram_alert_scan.py` with that environment's product env
- **AND** the journal of the unit SHALL record enviou, nada a enviar, or falhou
- **AND** the scan SHALL NOT depend on a Hermes/LLM process to start

#### Scenario: Hermes is not the product wake path
- **WHEN** the product timer is installed and enabled
- **THEN** the overlay SHALL list the product scan unit under `environments.*.services`
- **AND** the job Hermes `Monitor Telegram sinais diario` SHALL NOT be listed as product runtime

### Requirement: PROD install fires immediately from the 06/09/2026 baseline
Installing and enabling the PROD timer SHALL start one scan immediately and SHALL send DMs for sendable transitions since the last recorded scan state (PROD baseline 06/09/2026), respecting the existing anti-noise ceiling.

#### Scenario: Enable on PROD starts a scan without waiting for the next calendar
- **WHEN** the PROD oneshot+timer is enabled
- **THEN** one scan SHALL run immediately
- **AND** it SHALL NOT wait for the next 08:05 BRT

#### Scenario: Catch-up DMs since 06/09/2026
- **WHEN** the immediate PROD scan finds sendable position-aware transitions since 06/09/2026 for an eligible linked user
- **THEN** those DMs SHALL be sent via the existing Bot API path
- **AND** the existing anti-noise ceiling SHALL apply (overflow waits for a later scan)
- **AND** audit SHALL record `sent` or `failed`

### Requirement: DEV timer uses DEV env without the PROD bot
The DEV timer SHALL run against the DEV canonical env and SHALL NOT call the PROD bot, token, or webhook.

#### Scenario: DEV fire uses DEV env
- **WHEN** the DEV timer or its install-time oneshot runs
- **THEN** it SHALL source the DEV product env
- **AND** it SHALL NOT use PROD `MONITOR_TELEGRAM_BOT_TOKEN`, `TELEGRAM_WEBHOOK_SECRET`, or the PROD webhook destination

### Requirement: Hermes cron is cut only after one green PROD timer run
The Hermes cron `Monitor Telegram sinais diario` SHALL be disabled or removed only after one PROD product-timer run that finished as enviou or nada a enviar (not falhou). After that cut there SHALL be a single daily wake.

#### Scenario: Cut after a green PROD run
- **WHEN** one PROD product-timer run has journaled enviou or nada a enviar
- **THEN** the Hermes cron `Monitor Telegram sinais diario` SHALL be disabled or removed
- **AND** there SHALL NOT be a second daily wake from Hermes plus the product timer

#### Scenario: Hermes stays until the first green PROD run
- **WHEN** the PROD product timer has not yet completed a green run
- **THEN** the Hermes cron MAY remain until that evidence exists
- **AND** the product SHALL NOT treat enabling that Hermes job as product runtime

### Requirement: Timer failure is journal-only
A failed product-timer run (timeout, exit ≠ 0, incomplete env) SHALL be visible in the unit journal and SHALL NOT send an extra Telegram DM that the clock broke.

#### Scenario: Failed fire does not DM clock-broke
- **WHEN** the product scan oneshot fails (timeout, non-zero exit, or incomplete env)
- **THEN** Alan SHALL NOT receive an extra Telegram DM about the broken clock
- **AND** the failure SHALL be in the unit journal

#### Scenario: Green and failed outcomes are journaled
- **WHEN** a product-timer run finishes
- **THEN** the journal SHALL show enviou, nada a enviar, or falhou without secrets

