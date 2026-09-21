## MODIFIED Requirements

### Requirement: Landing explains requested product capabilities

The landing page SHALL explain the product capabilities requested in card #193: Binance-history backtests, backtest metrics, and Binance wallet result tracking, aligned to policy Q3=A. The wallet/carteira copy SHALL distinguish read-only tracking (Home/Carteira) from optional Spot Trading (comprar / stop / vender Spot no Farol no Operar, após confirmação, nunca saque) and from the optional directional BTCUSDT scalp the user can turn on in the Monitor (default off; while on, post-only limits without per-order confirmation; never withdraw). It SHALL NOT claim that the Farol is never a bot 24/7 as an absolute, nor that every Farol order always requires confirmation.

#### Scenario: Visitor evaluates product capabilities — Spot opcional e scalp opcional

- **Given** visitante na landing v4 e `docs/landing-page.md`
- **WHEN** a visitor reads the product sections (benefícios carteira, confiança)
- **THEN** the page SHALL mention backtests over the available Binance history
- **AND** it SHALL list the metrics Sharpe, Trades, Win%, Return, Max DD, PF, SQN, Max L, and ATR
- **AND** it SHALL explain Binance wallet connection as leitura para Home/Carteira e, com permissão Spot Trade (sem withdraw) opcional, possibilidade de enviar comprar / stop / vender Spot **no Farol** após confirmação no Operar (nunca saque)
- **AND** it SHALL admit an optional directional BTCUSDT scalp on the Monitor that the user turns on (default off; never withdraw)
- **AND** it SHALL NOT explain the wallet as read-only result tracking only
- **AND** it SHALL NOT state «não é bot 24/7» as an absolute once the scalp exists

### Requirement: Landing explains product trust and risk

The landing page SHALL include safety and decision-support copy required for the beta audience, with Spot opt-in policy Q3=A. It SHALL admit that the Farol can enviar comprar / stop / vender Spot no Farol no Operar quando habilitado (opcional, após confirmação), SHALL admit the optional Monitor scalp (default off; while on, post-only without per-order confirmation), SHALL state that it never withdraws, and SHALL NOT claim that Cripto Farol never sends orders, that o botão de compra/venda é na sua Binance, or that it is not a 24/7 bot as an absolute. It SHALL state that it does not operate by itself by omission.

#### Scenario: Visitor evaluates security and responsibility — Q3/A com scalp opcional

- **Given** visitante em `https://criptofarol.com.br/` (v4) e `docs/landing-page.md` lê hero/confiança/FAQ/benefício carteira
- **WHEN** a visitor reads the trust, FAQ, or footer risk areas (v4 `index.html` benefício carteira, confiança, FAQ robô)
- **THEN** the page SHALL explain that Binance access is leitura para acompanhamento (Home/Carteira) e, com permissão Spot Trade (sem saque) opcional, permite enviar comprar / stop / vender Spot **no Farol** após confirmação do utilizador no Operar
- **AND** it SHALL state that Cripto Farol never withdraws and never asks for Binance password
- **AND** it SHALL state that the Farol does not operate by itself by omission (default scalp off; Operar still confirms each click)
- **AND** it SHALL admit that turning on the Monitor scalp sends post-only limits without confirming each order until the user turns it off or kill fires
- **AND** it SHALL NOT state that Binance API is “apenas para consulta” as absolute truth, nor that Cripto Farol “nunca envia ordem” nor that “quem aperta o botão é sempre você, na sua Binance”
- **AND** it SHALL NOT state “Não, não é bot 24/7” as the whole answer
- **AND** it SHALL still state that crypto investing involves risk and no analysis guarantees results

#### Scenario: FAQ bot e acesso ao dinheiro — não mente

- **Given** visitante no FAQ da v4
- **WHEN** a visitor reads FAQ “É um robô que opera por mim?” and “Vocês têm acesso ao meu dinheiro?”
- **THEN** the answers SHALL say it does not operate by itself by omission, that Operar still confirms each click, and that an optional Monitor scalp (default off) can send post-only limits without per-order confirmation
- **AND** the answers SHALL say never withdraw and never ask for the Binance password
- **AND** the answers SHALL NOT say “API apenas para consulta” or “nunca enviamos ordem” as absolute
- **AND** the answers SHALL NOT say the Farol never sends an order without confirmation as absolute
