## ADDED Requirements

### Requirement: Landing highlights beta value before signup
The landing page SHALL present the closed-beta value proposition before the signup form with concrete benefits that support registration intent.

#### Scenario: Visitor scans the first screen
- **WHEN** a visitor opens the landing page
- **THEN** the page SHALL show a primary signup CTA
- **AND** it SHALL show that the first beta testers receive 6 months free
- **AND** it SHALL avoid promises of profit or guaranteed results

#### Scenario: Visitor opens the production domain
- **WHEN** a visitor opens `https://criptofarol.com.br/`
- **THEN** the published landing variant SHALL show the same 6-month free beta offer and requested product capabilities

### Requirement: Landing explains requested product capabilities
The landing page SHALL explain the product capabilities requested in card #193: Binance-history backtests, backtest metrics, and Binance wallet result tracking.

#### Scenario: Visitor evaluates product capabilities
- **WHEN** a visitor reads the product sections
- **THEN** the page SHALL mention backtests over the available Binance history
- **AND** it SHALL list the metrics Sharpe, Trades, Win%, Return, Max DD, PF, SQN, Max L, and ATR
- **AND** it SHALL explain Binance wallet connection as read-only result tracking

### Requirement: Landing keeps closed-beta lead capture intact
The landing page SHALL keep the existing lead form behavior while improving conversion copy.

#### Scenario: Visitor submits interest
- **WHEN** a visitor submits the landing form
- **THEN** the form SHALL continue posting the lead payload to the existing `/api/leads` endpoint path
- **AND** the page SHALL keep ethical risk copy near the signup area
