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
The landing page SHALL explain the product capabilities requested in card #193: Binance-history backtests, backtest metrics, and Binance wallet result tracking, aligned to policy Q3=A. The wallet/carteira copy SHALL distinguish read-only tracking (Home/Carteira) from optional Spot Trading (comprar / stop / vender Spot no Farol, após confirmação, nunca saque, não é bot 24/7).

#### Scenario: Visitor evaluates product capabilities — Spot opcional
- **Given** visitante na landing v4 e `docs/landing-page.md` (critérios 1 e 2)
- **WHEN** a visitor reads the product sections (benefícios carteira, confiança)
- **THEN** the page SHALL mention backtests over the available Binance history
- **AND** it SHALL list the metrics Sharpe, Trades, Win%, Return, Max DD, PF, SQN, Max L, and ATR
- **AND** it SHALL explain Binance wallet connection as leitura para Home/Carteira e, com permissão Spot Trade (sem withdraw) opcional, possibilidade de enviar comprar / stop / vender Spot **no Farol** após confirmação (nunca saque; não é bot)
- **AND** it SHALL NOT explain the wallet as read-only result tracking only

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
The landing page SHALL include safety and decision-support copy required for the beta audience, with Spot opt-in policy Q3=A. It SHALL admit that the Farol can enviar comprar / stop / vender Spot no Farol quando habilitado (opcional), SHALL state that it never withdraws and is not a 24/7 bot, and SHALL NOT claim that Cripto Farol never sends orders nor that o botão de compra/venda é na sua Binance.

#### Scenario: Visitor evaluates security and responsibility — Q3/A
- **Given** visitante em `https://criptofarol.com.br/` (v4) e `docs/landing-page.md` lê hero/confiança/FAQ/benefício carteira (critério 1)
- **WHEN** a visitor reads the trust, FAQ, or footer risk areas (v4 `index.html:175,215,232,236` + `docs/landing-page.md`)
- **THEN** the page SHALL explain that Binance access is leitura para acompanhamento (Home/Carteira) e, com permissão Spot Trade (sem saque) opcional, permite enviar comprar / stop / vender Spot **no Farol** após confirmação do utilizador
- **AND** it SHALL state that Cripto Farol never withdraws, never asks for Binance password, and is not a 24/7 bot that operates by itself
- **AND** it SHALL state that any order in the Farol requires user confirmation and that without Spot permission the user only tracks sinais
- **AND** it SHALL NOT state that Binance API is “apenas para consulta” as absolute truth, nor that Cripto Farol “nunca envia ordem” nor that “quem aperta o botão é sempre você, na sua Binance”
- **AND** it SHALL still state that crypto investing involves risk and no analysis guarantees results

#### Scenario: FAQ bot e acesso ao dinheiro — não mente
- **Given** visitante no FAQ da v4 (critério 1)
- **WHEN** a visitor reads FAQ “É um robô que opera por mim?” and “Vocês têm acesso ao meu dinheiro?”
- **THEN** the answers SHALL say it is not a bot, that it consults data and shows reading, and that with optional Spot Trade the user confirms orders **no Farol** (never withdraw), not automatically via Binance button
- **AND** the answers SHALL NOT say “API apenas para consulta” or “nunca enviamos ordem” as absolute

