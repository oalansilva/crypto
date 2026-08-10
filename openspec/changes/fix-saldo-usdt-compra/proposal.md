## Why

Usuários do beta fechado com saldo USDT livre suficiente recebem "Saldo livre em USDT insuficiente" ao comprar ativo Spot no Monitor, e o campo "Saldo livre" do modal aparece vazio — a funcionalidade core de compra fica bloqueada para saldo disponível (card #463).

## What Changes

- Corrigir a validação de saldo USDT no fluxo de compra Spot para que use o saldo livre real e corretamente populado da conta Binance do usuário.
- Garantir que o modal de compra sempre exiba o saldo livre USDT de forma explícita (valor ou estado de carregamento/erro), nunca vazio e nunca tratado como zero quando não populado.
- Alinhar o saldo exibido ao usuário (Carteira/Modal) com o saldo verificado na validação (free Spot), eliminando divergências de fonte (ex.: Simple Earn/LDUSDT, total vs. free).
- Mensagem de erro de saldo insuficiente deve refletir o valor livre real quando o erro for legítimo.

## Capabilities

### New Capabilities

- Nenhuma nova capability.

### Modified Capabilities

- `monitor-direct-spot-trading`: requisito de validação de saldo livre USDT no fluxo de compra — o saldo deve ser carregado/populado de forma confiável e consistente entre preview, UI e envio; ausência de saldo não pode ser interpretada como saldo zero em validação.

## Impact

- Backend: `backend/app/services/binance_market_orders.py` (mapa de saldo e checagem `Saldo livre em USDT insuficiente`), `backend/app/services/monitor_spot_market_orders.py` (preview e submit), `backend/app/services/binance_spot.py` (snapshot de saldo exibido na Carteira).
- Frontend: `frontend/src/components/monitor/SpotMarketTradePanel.tsx` (exibição de saldo livre e validação no modal).
- API: contrato do preview de ordens Spot (campo `quote_balance`) — compatível, sem quebra.
- Testes: unit tests de validação de saldo no backend e QA visual/Playwright do modal de compra.
