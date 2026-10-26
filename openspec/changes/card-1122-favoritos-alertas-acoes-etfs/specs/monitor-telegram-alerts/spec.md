## MODIFIED Requirements

### Requirement: Alert anti-noise controls
The system SHALL prevent repeated Monitor Telegram alerts through event identity **per user**, for signal alerts, data-delay warnings and the transition notice. A signal event is identified by user, favorite, new reading and the start of the closed candle that produced it; a data-delay warning by user, asset and delay episode. The time-based minimum repeat window SHALL NOT decide duplicates anymore. Signal alerts and data-delay warnings of a scan SHALL NOT be capped by the per-user rate limit (Alan's decision 4, 26/10/2026): each one is its own message. The configurable rate limit (`monitor_telegram_rate_limit_count` / `monitor_telegram_rate_limit_window_minutes`) SHALL apply only to the operational Binance failure notice.

#### Scenario: Same event is skipped per user
- **WHEN** an alert with the same event key was already reserved, sent or dry-run for that user
- **THEN** the system SHALL skip sending it again
- **AND** it SHALL report the skip reason as duplicate

#### Scenario: Scan alerts are not rate limited
- **WHEN** seven marked favorites of a user change reading in the same scan and the configured limit is 5 messages per 60 minutes
- **THEN** the system SHALL send seven messages to that user, one per favorite
- **AND** it SHALL NOT report any of them as rate limited

#### Scenario: Operational Binance failure DM is rate limited per user
- **WHEN** multiple cron scans fail Binance wallet sync for the same user within the rate-limit window
- **THEN** the system SHALL send at most one operational failure DM per user per window

### Requirement: Position-aware Monitor Telegram alerts per user
The system SHALL send Monitor Telegram alerts as individual DMs to the owner of each favorite marked "Alertar" when that favorite's reading changes and the change is relevant to the owner's portfolio scope. Crypto keeps the position matrix below. Ação and ETF marked in the owner's portfolio SHALL send both entry (`EXIT`→`HOLD`) and exit (`HOLD`→`EXIT`), independent of any Binance position, until #1124 brings real positions.

#### Scenario: Bought user receives sell alert on HOLD to EXIT
- **WHEN** a crypto symbol is in the user's Em portfólio scope (`inPortfolio=true`)
- **AND** the user holds an eligible Spot position in the symbol's base asset (`min_usd=1`)
- **AND** a favorite of that user for that symbol marked "Alertar" changes public status from `HOLD` to `EXIT`
- **THEN** the system SHALL send a DM to that user's linked Telegram chat
- **AND** the message SHALL include symbol, strategy, configuration, timeframe, previous reading Compra, and new reading Venda
- **AND** the message SHALL include "Este alerta não envia ordem: é só o sinal da estratégia." and the educational disclaimer

#### Scenario: Bought user receives stop sell alert with Motivo=Stop
- **WHEN** a crypto symbol is in the user's Em portfólio scope
- **AND** the user holds an eligible Spot position
- **AND** a marked favorite changes to public status `EXIT` due to stop loss (`STOPPED_OUT` / `stop_breached_now`)
- **THEN** the system SHALL send a DM to that user's chat with new reading Venda
- **AND** the message SHALL include `Motivo=Stop`

#### Scenario: Flat user receives buy alert on EXIT to HOLD
- **WHEN** a crypto symbol is in the user's Em portfólio scope
- **AND** the user has no eligible Spot position (flat)
- **AND** a marked favorite changes public status from `EXIT` to `HOLD`
- **THEN** the system SHALL send a DM to that user's chat with previous reading Venda and new reading Compra

#### Scenario: Flat user suppresses HOLD to EXIT
- **WHEN** a user is flat for a crypto symbol in scope
- **AND** a marked favorite changes from `HOLD` to `EXIT`
- **THEN** the system SHALL NOT send a position-aware alert to that user

#### Scenario: Bought user suppresses EXIT to HOLD re-entry
- **WHEN** a user holds an eligible Spot position
- **AND** a marked crypto favorite changes from `EXIT` to `HOLD` while the position remains
- **THEN** the system SHALL NOT send a position-aware alert to that user

#### Scenario: Ação na carteira recebe entrada e saída
- **WHEN** NVDA is marked in the user's portfolio
- **AND** the user's marked NVDA favorite changes from `HOLD` to `EXIT`, and later from `EXIT` to `HOLD`
- **THEN** the system SHALL send the sell DM and later the buy DM

#### Scenario: Strategy is_holding is not used as portfolio proxy
- **WHEN** the scanner evaluates whether a user is bought
- **THEN** it SHALL use that user's Spot wallet / derived `in_portfolio` rules for crypto and the manual mark for ação and ETF
- **AND** it SHALL NOT use strategy `is_holding` as a proxy

### Requirement: Em portfólio scope resolution per user
The position-aware scanner SHALL resolve Em portfólio scope per user using the same rules as Monitor UI `portfolioStatusBySymbol.inPortfolio`.

#### Scenario: Crypto with Binance uses derived portfolio rule per user
- **WHEN** the symbol is a crypto asset and the user has Binance credentials configured
- **THEN** `inPortfolio` for that user SHALL be true when they hold an eligible Spot balance of the base asset

#### Scenario: Non-derived symbols use manual preference per user
- **WHEN** the derived portfolio rule is not active for a user and symbol (crypto without credentials, ação, ETF)
- **THEN** `inPortfolio` SHALL follow that user's stored `MonitorPreference.in_portfolio`

#### Scenario: Scope intersects the user's marked favorites
- **WHEN** the scanner builds candidates for a user
- **THEN** it SHALL consider only symbols of that user's own favorites with `notify_telegram=true`
- **AND** apply the Em portfólio filter for that user before the position-aware matrix

### Requirement: Binance unavailability operational alert per user
The system SHALL pause crypto position-aware alerts for a user and notify them individually when that user's Binance wallet sync fails during a cron scan. Ação and ETF alerts of that user SHALL continue.

#### Scenario: Binance failure sends rate-limited operational DM to user
- **WHEN** the cron scan cannot fetch a user's Binance Spot balances
- **THEN** the system SHALL send one operational DM to that user's linked chat stating wallet sync is unavailable, crypto alerts are paused, and ações and ETFs continue
- **AND** the operational DM SHALL be rate limited per user

#### Scenario: Binance failure suppresses only that user's crypto alerts
- **WHEN** Binance wallet sync fails for user A but succeeds for user B in the same scan
- **THEN** user A SHALL NOT receive crypto signal alerts in that scan
- **AND** user A SHALL still receive ação and ETF alerts
- **AND** user B SHALL continue to receive alerts normally
