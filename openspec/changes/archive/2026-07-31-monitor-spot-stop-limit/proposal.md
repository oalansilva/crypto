## Why

O STOP no gráfico do Monitor é só o nível teórico da estratégia. O trader quer colocar/remover uma ordem Spot stop-limit na Binance nesse preço, com 100% do saldo free, sem digitar manualmente na exchange.

## What Changes

- Botões no gráfico do Monitor: **Proteger stop** / **Remover stop** (não auto ao abrir).
- Backend cria/cancela ordem Spot `STOP_LOSS_LIMIT` `SELL` usando a credencial do usuário.
- Quantidade = 100% do `free` do ativo; `stopPrice` = `opportunity.stop_price`; `limitPrice` = stop − 0,1%.
- Exceção escopada à regra read-only: só este fluxo do Monitor pode alterar a conta Binance (ordens).
- Copy da chave em Meu Perfil indica que Spot trading pode ser necessário (sem withdraw).

**BREAKING (contrato):** a integração Binance deixa de ser estritamente read-only; a carteira continua leitura, mas o Monitor pode enviar/cancelar stop-limit Spot com confirmação explícita.

## Capabilities

### New Capabilities
- `monitor-spot-stop-limit`: place/cancel/status de ordem protetiva Spot no gráfico do Monitor.

### Modified Capabilities
- `external-balances`: exceção escopada — Monitor pode `POST/DELETE` Spot stop-limit; carteira permanece leitura de saldos.
- `user-preferences-binance-credentials`: copy/UX da chave permite Spot trading além de leitura (sem withdraw).

## Impact

- Backend: cliente Spot assinado POST/DELETE, service/rotas `/api/monitor/spot-stop-order*`.
- Frontend: `ChartModal` + copy em `BinanceCredentialsForm`.
- Segurança: chave com Enable Spot Trading; IP whitelist; fail-closed sem trade/saldo.
- Card: #337
