## 1. Spec & contracts

- [x] 1.1 Atualizar contratos de preview/submit Spot para aceitar origem `USDT|USDC` e símbolo de ordem `BASE`+origem, mantendo símbolo de estratégia `BASEUSDT`
- [x] 1.2 Documentar respostas de erro acionáveis: par inexistente/indisponível, saldo insuficiente da origem, notional inválido

## 2. Backend

- [x] 2.1 Resolver símbolo de ordem a partir de base da oportunidade + origem escolhida; validar TRADING + MARKET + quoteOrderQty
- [x] 2.2 Preview/submit BUY usam saldo Spot `free` e `quoteOrderQty` na origem escolhida; sem conversão entre stables
- [x] 2.3 SELL 100% permanece no símbolo da estratégia (`BASEUSDT`)
- [x] 2.4 Testes unitários/integração: USDC ok, USDT regressão, par ausente, saldo insuficiente

## 3. Frontend Monitor

- [x] 3.1 `SpotMarketTradePanel`: radiogroup Pagar com (USDT|USDC) só na compra; saldo/input/validação por origem
- [x] 3.2 Default + preferência de sessão; preço indicativo e labels refletem origem/par da ordem
- [x] 3.3 Review distingue estratégia vs ordem; venda sem seletor
- [x] 3.4 Elegibilidade Operar continua baseada em estratégia USDT (sem exigir BASEUSDC para mostrar o botão)

## 4. Verificação

- [x] 4.1 Testes frontend do fluxo compra USDC / bloqueio / regressão USDT
- [x] 4.2 `/opsx:verify` contra Gist + change após apply
