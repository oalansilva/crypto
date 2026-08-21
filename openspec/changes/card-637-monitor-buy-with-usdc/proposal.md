## Why

Quem opera no Monitor com estratégia `BASE/USDT` (ex.: BTC/USDT) pode ter saldo Spot livre em **USDC**, não em USDT. Hoje a compra Spot trava a origem em USDT e bloqueia a operação, embora o destino desejado continue sendo o base da oportunidade. Separar **par da estratégia** (sinal/gráfico) de **par da ordem** (com o que se paga) destrava o beta sem forçar recriar a estratégia em USDC.

## What Changes

- No modal **Operar** (compra), oferecer origem **USDT** ou **USDC** (v1) via controle “Pagar com”, sem alterar estratégia, gráfico nem símbolo do sinal.
- Montar a ordem MARKET no par Spot `BASE` + origem escolhida (`BTCUSDC` se pagar com USDC), desde que o par exista, esteja negociável e aceite `MARKET` + `quoteOrderQty`.
- Saldo livre, validação e `quoteOrderQty` usam **somente** a origem escolhida; confirmação deixa explícitos origem, destino (base), valor, saldo livre e o par da ordem (pode diferir do par da estratégia).
- Sem hop silencioso USDC→USDT→`BASEUSDT`. Sem par / par indisponível / saldo insuficiente: bloqueio acionável.
- Default: USDT se houver par+saldo; senão primeira origem válida; preferência de sessão pode ser lembrada.
- **Venda 100%** permanece no par da estratégia (`BASEUSDT`) neste card.
- Compra USDT-only atual permanece o caminho padrão e não regride.

## Capabilities

### New Capabilities

_(nenhuma — comportamento estende a capability existente)_

### Modified Capabilities

- `monitor-direct-spot-trading`: compra deixa de exigir quote fixa USDT; permite origem USDT|USDC no envio da ordem Spot mantendo elegibilidade/sinal em pares USDT; confirmação e validação refletem a origem escolhida; venda 100% inalterada no par da estratégia.

## Impact

- Frontend: `SpotMarketTradePanel.tsx`, elegibilidade/copy em `MonitorStatusTab` (se necessário), tipos de preview/ordem.
- Backend: `monitor_spot_market_orders.py` / `binance_market_orders.py` — preview e submit aceitam quote de origem; resolução de símbolo `BASE`+origem; fail-closed se par inválido.
- Spec `monitor-direct-spot-trading` (delta).
- UI impact: `affected` (modal Operar no Monitor). Sem mudança em Discovery/Favoritos/Combo/candles.
