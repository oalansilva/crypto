# landing-conversion-copy Specification

## Purpose
TBD - created by archiving change card-193-ajustar-landpage. Update Purpose after archive.
## Requirements
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

The landing page SHALL explain the product capabilities requested in card #193: Binance-history backtests, backtest metrics, and Binance wallet result tracking, aligned to policy Q3=A in plain words. Since card #1160 (Alan's T6 return, 29/10/2026), the backtest SHALL be presented as the ready-made analysis of the strategies the visitor follows (the chart marks every trade of the strategy in the period), not as a tool to test any strategy, because combo, discovery and optimization are admin-only. The wallet copy SHALL distinguish seeing balance and result from optional buying and selling of crypto at spot price through the Farol, each order only after the visitor confirms, never a withdrawal. It SHALL NOT use the internal names "Operar", "Home" or "Spot Trade" in the landing copy. It SHALL NOT mention a scalper, scalp, or Scalp BTCUSDT. It SHALL NOT announce that a scalper was removed. It SHALL NOT claim that Cripto Farol never sends orders.

#### Scenario: Visitor evaluates product capabilities — Spot opcional e scalp opcional

- **Given** visitante na landing publicada e `docs/landing-page.md`
- **WHEN** a visitor reads the product sections (benefícios carteira, confiança)
- **THEN** the page SHALL mention backtests over the available Binance history as the ready-made analysis of each followed strategy
- **AND** it SHALL NOT invite the visitor to "test any strategy" ("Teste qualquer estratégia")
- **AND** it SHALL list the metrics Sharpe, Trades, Win%, Return, Max DD, PF, SQN, Max L, and ATR
- **AND** it SHALL explain the Binance wallet connection as seeing balance and result, and, if the visitor wants, buying and selling crypto at spot price through the Farol with confirmation of each order (never a withdrawal)
- **AND** it SHALL NOT use "Operar", "Home" or "Spot Trade" as names in the copy
- **AND** it SHALL NOT mention scalper, scalp, or Scalp BTCUSDT
- **AND** it SHALL NOT announce that a scalper was removed
- **AND** it SHALL NOT explain the wallet as read-only result tracking only
- **AND** it SHALL NOT claim that Cripto Farol never sends orders

### Requirement: Landing keeps closed-beta lead capture intact
The landing page SHALL keep a two-step lead form posting to the existing `/api/leads` endpoint path, saving the lead at step 1 and treating step 2 as optional enrichment.

#### Scenario: Visitor submits interest
- **WHEN** a visitor submits the landing form
- **THEN** the form SHALL continue posting the lead payload to the existing `/api/leads` endpoint path
- **AND** the page SHALL keep ethical risk copy near the signup area

#### Scenario: Visitor completes two-step qualification
- **WHEN** a visitor enters name and email in step 1 and presses "Entrar na lista do beta"
- **THEN** the page SHALL send name, email, origin and sanitized attribution right away and show step 2 only after the lead is saved
- **AND** step 2 SHALL collect optional WhatsApp, crypto level, and current crypto difficulty, with a way to skip it
- **AND** submitting step 2 SHALL enrich the same lead without creating another

### Requirement: Landing lead endpoint works on production subdomains
The landing page SHALL post lead capture requests through the relative `/api/leads` path on production domain variants.

#### Scenario: Visitor opens a production subdomain
- **WHEN** a visitor opens the landing page on `criptofarol.com.br` or any hostname ending in `.criptofarol.com.br`
- **THEN** the lead form SHALL use `/api/leads`
- **AND** it SHALL NOT target the development `:5174` lead endpoint

#### Scenario: Developer opens local preview
- **WHEN** a developer opens the landing page outside the `criptofarol.com.br` domain family
- **THEN** the lead form SHALL keep using the same host with port `5174` for the local lead endpoint

### Requirement: Landing explains product trust and risk

The landing page SHALL include safety and decision-support copy required for the beta audience, with Spot opt-in policy Q3=A in plain words. It SHALL admit that buying and selling through the Farol is optional and that each order only goes out after the visitor confirms. It SHALL state that it never withdraws and never asks for the Binance password. It SHALL NOT use the internal names "Operar", "Home" or "Spot Trade". It SHALL NOT mention a scalper, scalp, or Scalp BTCUSDT. It SHALL NOT announce that a scalper was removed. It SHALL NOT claim that Cripto Farol never sends orders, that o botão de compra/venda é na sua Binance, or that API access is “apenas para consulta” as absolute truth. It SHALL state that it does not operate by itself.

#### Scenario: Visitor evaluates security and responsibility — Q3/A com scalp opcional

- **Given** visitante em `https://criptofarol.com.br/` lê hero/confiança/FAQ/benefício carteira
- **WHEN** a visitor reads the trust, FAQ, or footer risk areas
- **THEN** the page SHALL explain that the Binance connection shows balance and result and, optionally, lets the visitor buy and sell at spot price through the Farol, each order after confirmation
- **AND** it SHALL state that Cripto Farol never withdraws and never asks for Binance password
- **AND** it SHALL state that the Farol does not operate by itself and that each order needs the visitor's confirmation
- **AND** it SHALL NOT mention scalper, scalp, or Scalp BTCUSDT
- **AND** it SHALL NOT announce that a scalper was removed
- **AND** it SHALL NOT state that Binance API is “apenas para consulta” as absolute truth, nor that Cripto Farol “nunca envia ordem” nor that “quem aperta o botão é sempre você, na sua Binance”
- **AND** it SHALL still state that investing in crypto, stocks and ETFs involves risk and no analysis guarantees results

#### Scenario: FAQ bot e acesso ao dinheiro — não mente

- **Given** visitante no FAQ da landing
- **WHEN** a visitor reads FAQ “É um robô que opera por mim?” and “Vocês têm acesso ao meu dinheiro?”
- **THEN** the answers SHALL say it does not operate by itself and that each buy or sell of crypto needs the visitor's confirmation
- **AND** the answers SHALL NOT mention scalper, scalp, or an optional Monitor loop without confirmation
- **AND** the answers SHALL say never withdraw and never ask for the Binance password
- **AND** the answers SHALL NOT say “API apenas para consulta” or “nunca enviamos ordem” as absolute

### Requirement: Metrics are explained on screen
Each backtest metric listed on the landing (Sharpe, Trades, Win%, Return, Max DD, PF, SQN, Max L, ATR) SHALL have a short plain-Portuguese explanation visible on the page at every width, not only in a `title` attribute.

#### Scenario: Visitor on a phone reads the metrics card
- **WHEN** a visitor opens the benefits section at 390px
- **THEN** each metric name SHALL appear next to its visible explanation without hover

### Requirement: No seat counter
The landing SHALL NOT show a number of registrations or seats, nor a placeholder such as "--". The signup area SHALL show a fixed sentence about the closed beta opening in waves.

#### Scenario: Visitor views the signup area
- **WHEN** a visitor views the signup section
- **THEN** it SHALL show "Beta fechado, com entrada em levas." and SHALL NOT show "cadastrados", "Restam" or "vagas nesta leva"

### Requirement: Asset list and single Monitor image
The asset chips SHALL show POL instead of MATIC and SHALL include examples of Binance stocks and ETFs (NVDA, SPY, QQQ) next to the crypto examples. The Monitor print SHALL appear only once on the page (in the hero); the product section SHALL show only the analysis chart.

#### Scenario: Visitor scans the page
- **WHEN** the page is rendered
- **THEN** "MATIC" SHALL NOT appear and "POL" SHALL appear in the asset chips
- **AND** the asset chips SHALL include at least one stock and one ETF
- **AND** the Monitor image SHALL appear once and the analysis chart image SHALL appear once

### Requirement: Clean and legible product prints
Product prints SHALL show the current product: the Monitor with the states "Em posição" and "Saída / cobertura", the strategy timeframe on each item, the per-strategy Telegram alert control, and at least one stock or ETF next to crypto; and the analysis chart with the strategy's trades marked in the period. Prints SHALL NOT show a target ("alvo"), developer controls (zoom buttons, candle count, "Mouse wheel"/"Roda do mouse", layout toggles), English labels such as "LAST PRICE", personal data (account name or e-mail) or internal strategy parameters (indicator lengths, stop percentage), and SHALL show prices in Brazilian format (for example "US$ 186,10"). At phone width (up to 560px) every print SHALL render its text at a legible size, either because the print is already the app's mobile layout or because it is replaced by a crop; at 390px the smallest text of each print SHALL render at an effective size of at least 11 CSS px (smallest source font × rendered width ÷ natural width). When the same asset appears in more than one print, the prints SHALL be consistent with each other (same state, entry, last price and timeframe), or a different asset SHALL be used.

#### Scenario: Visitor on a phone views the prints
- **WHEN** a visitor opens the landing at 390px
- **THEN** the Monitor print SHALL be legible without zoom and the chart SHALL be the mobile crop
- **AND** the smallest text in the Monitor print and in the chart crop SHALL render at an effective size of at least 11 CSS px
- **AND** neither SHALL contain developer controls, English price labels, a target, personal data or strategy parameters

#### Scenario: Prints tell the same story
- **WHEN** an asset appears both in the Monitor print and in the analysis print
- **THEN** its state, entry, last price and timeframe SHALL be consistent between the two prints

#### Scenario: Prints follow the current Monitor
- **WHEN** a visitor looks at the Monitor print
- **THEN** it SHALL show "Em posição" and "Saída / cobertura", a timeframe on each item, the "Alerta" control on and off, and a stock or ETF next to crypto
- **AND** the chart print SHALL mark the strategy's buys and sells in the period

### Requirement: Landing covers crypto, stocks and ETFs from Binance
The landing SHALL say, in the hero, the benefits, the prints and the FAQ, that the Farol follows crypto, stocks and ETFs traded on Binance. It SHALL make clear that stocks and ETFs are followed and alerted, not traded by the Farol: buying and selling through the Farol applies only to crypto. It SHALL keep the decision-support positioning and the risk notice, which SHALL cover stocks and ETFs too.

#### Scenario: Visitor reads the hero
- **WHEN** a visitor opens the landing
- **THEN** the hero SHALL mention crypto, stocks and ETFs from Binance
- **AND** the hero risk sentence SHALL say that crypto, stocks and ETFs carry risk

#### Scenario: Visitor asks about stocks and ETFs
- **WHEN** a visitor opens the FAQ
- **THEN** it SHALL answer "Funciona com ações e ETFs?" saying they are followed in the Monitor with analysis, that the Telegram alert applies to the strategies the visitor follows with a star once Telegram is connected in the Profile, that the catalog example strategies show without alert, that the New York session applies and a closed market shows only on screen, and that buying and selling through the Farol is crypto only
- **AND** the FAQ SHALL NOT keep the question about another exchange

### Requirement: Signals use the Monitor vocabulary
The section about the two signals SHALL use the Monitor's state names "Em posição" and "Saída / cobertura" and SHALL NOT present "Compra"/"Venda" as the state names nor promise a target. The "Em posição" copy SHALL say that the Monitor shows entry, stop and the distance to it.

#### Scenario: Visitor reads the signals section
- **WHEN** a visitor reads the signals section
- **THEN** the two cards SHALL be titled "Em posição" and "Saída / cobertura"
- **AND** the page SHALL NOT mention a target ("alvo")

### Requirement: Telegram alert per strategy as a benefit
The benefits SHALL present the Telegram alert per strategy with an honest scope: the alert applies to the strategies the visitor follows with a star in the Monitor, in crypto, stocks and ETFs, after the visitor connects Telegram in the Profile; it comes on by default and can be turned off strategy by strategy. The landing SHALL NOT promise that the catalog showcase (the example strategies a new account sees) sends alerts, SHALL NOT state how often the alert is sent, and SHALL NOT suggest real-time delivery ("na hora", "assim que", "em tempo real"). The copy SHALL NOT say the alert sends an order. The hero trust line, the routine, the FAQ, the meta description and the Open Graph texts SHALL use the same scope (strategies followed with a star).

#### Scenario: Visitor reads the benefits
- **WHEN** a visitor reads the benefits section
- **THEN** one benefit SHALL be the Telegram alert per strategy, for the strategies followed with a star, after connecting Telegram in the Profile, on by default and turned off per strategy
- **AND** the page SHALL NOT contain "na hora", "assim que" or "em tempo real" about the alert, nor a frequency for it

#### Scenario: New beta account reads about the alert
- **WHEN** a visitor reads the FAQ about stocks and ETFs
- **THEN** it SHALL say that the catalog example strategies show in the Monitor without alert

