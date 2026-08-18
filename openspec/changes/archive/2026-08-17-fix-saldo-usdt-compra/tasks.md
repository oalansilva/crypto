## 1. Backend — expor saldo Spot livre real e Simple Earn

- [x] 1.1 `binance_market_orders.py`: erro de saldo insuficiente em BUY inclui saldo livre real e, quando houver ativo LD* do quote asset, dica de Simple Earn não elegível (mensagem sanitizada, sem segredos)
- [x] 1.2 `binance_spot.py`: `fetch_spot_balances_snapshot` mantém contrato (`free`/`locked`/`total`) e adiciona campo opcional `earn_amount` por ativo (0 quando não houver Earn), sem somar Earn ao `free` operável
- [x] 1.3 Testes unitários backend: divergência Earn vs free no erro de saldo; `earn_amount` no snapshot sem somar ao free

## 2. Frontend — modal de compra com saldo real

- [x] 2.1 `SpotMarketTradePanel.tsx`: etapa `entry` busca o saldo livre real do quote (endpoint `external/binance/spot/balances`) e exibe no campo "Saldo livre" com estados carregando/valor/indisponível; remove texto placeholder "Confirmado pela Binance na próxima etapa"
- [x] 2.2 Mensagem de erro do preview usa payload enriquecido do backend (saldo real + dica Simple Earn quando aplicável)

## 3. Frontend — Carteira com nota de Simple Earn

- [x] 3.1 Tela Carteira (`ExternalBalancesPage` ou componentes de balanço): quando `earn_amount > 0`, exibir badge/nota "inclui X em Simple Earn" na linha do ativo (desktop e mobile)

## 4. Validação e integração

- [x] 4.1 Playwright visual/functional: modal exibe saldo real e mensagem insuficiente com dica Earn; nota Earn na Carteira; sem regressão de overflow/console
- [x] 4.2 Validação OpenSpec da change (`openspec validate --changes fix-saldo-usdt-compra`) e testes proporcionais backend/frontend
