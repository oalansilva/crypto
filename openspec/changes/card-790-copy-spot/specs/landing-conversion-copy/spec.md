## MODIFIED Requirements

### Requirement: Landing explains requested product capabilities
The landing page SHALL explain the product capabilities requested in card #193: Binance-history backtests, backtest metrics, and Binance wallet result tracking, aligned to policy Q3=A. The wallet/carteira copy SHALL distinguish read-only tracking (Home/Carteira) from optional Spot Trading (comprar / stop / vender Spot no Farol, após confirmação, nunca saque, não é bot 24/7).

#### Scenario: Visitor evaluates product capabilities — Spot opcional
- **Given** visitante na landing v4 e `docs/landing-page.md` (critérios 1 e 2)
- **WHEN** a visitor reads the product sections (benefícios carteira, confiança)
- **THEN** the page SHALL mention backtests over the available Binance history
- **AND** it SHALL list the metrics Sharpe, Trades, Win%, Return, Max DD, PF, SQN, Max L, and ATR
- **AND** it SHALL explain Binance wallet connection as leitura para Home/Carteira e, com permissão Spot Trade (sem withdraw) opcional, possibilidade de enviar comprar / stop / vender Spot **no Farol** após confirmação (nunca saque; não é bot)
- **AND** it SHALL NOT explain the wallet as read-only result tracking only

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
