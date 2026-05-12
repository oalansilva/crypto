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

#### Scenario: Visitor reads the card #193 refazer structure
- **WHEN** a visitor scrolls through the published landing variant
- **THEN** the page SHALL include sections for best assets preview, routine, product screen preview, beta benefits, two signals, trust and safety, social proof, FAQ, and beta signup
- **AND** the hero SHALL use the message about knowing when buying and selling crypto makes sense without becoming a trader

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

#### Scenario: Visitor completes two-step qualification
- **WHEN** a visitor enters name and email in step 1
- **THEN** the page SHALL reveal step 2 without sending the lead yet
- **AND** step 2 SHALL collect optional WhatsApp, crypto level, and current crypto difficulty
- **AND** the final submit SHALL send name, email, WhatsApp, profile, pain, and origin to the existing lead endpoint

### Requirement: Landing explains product trust and risk
The landing page SHALL include safety and decision-support copy required for the beta audience.

#### Scenario: Visitor evaluates security and responsibility
- **WHEN** a visitor reads the trust, FAQ, or footer risk areas
- **THEN** the page SHALL explain that Binance access is read-only
- **AND** it SHALL explain that Cripto Farol does not move money, send orders, or decide for the user
- **AND** it SHALL state that crypto investing involves risk and no analysis guarantees results
