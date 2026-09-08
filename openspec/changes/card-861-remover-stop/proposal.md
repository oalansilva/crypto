## Why

O operador Posicionado (HOLD, ex. BTC Spot USDT) não consegue remover a stop order via Farol; a stop travada bloqueia a venda como operação no Monitor, obrigando a ida à exchange.

## What Changes

- Remover stop com confirmação segue alcançável no gráfico (ChartModal + SpotProtectStopPanel) quando Posicionado (HOLD) com stop aberta — sem exigir troca de tela.
- Remover stop passa a ser alcançável também dentro do fluxo de venda (SpotMarketTradePanel): quando a venda trava por causa da stop, o painel oferece remover ali, com confirmação própria.
- Após remover, a venda segue o fluxo normal (nova prévia → revisão → confirmação).
- Remover nunca vende sozinho: são dois gestos separados, cada um confirmado (remover ≠ vender).
- Liberação cobre stops criadas no Farol (`cfstop_`) e stops criadas só na exchange, sem tocar em ordens não-stop do símbolo.
- Sem Posicionado / sem stop aberta, remover não é oferecido.

## Capabilities

### New Capabilities

(nenhuma — comportamento estende capacidades existentes)

### Modified Capabilities

- `monitor-spot-stop-limit`: remover com confirmação alcançável no gráfico quando Posicionado (HOLD) com stop aberta (app ou só-exchange); remover nunca vende sozinho.
- `monitor-direct-spot-trading`: fluxo de venda SELL detecta venda travada pela stop e oferece remover ali (confirmação própria); após remover, a venda segue o fluxo normal.

## Impact

- Frontend: `frontend/src/components/monitor/ChartModal.tsx`, `SpotProtectStopPanel.tsx` (confirmação de remover no gráfico), `SpotMarketTradePanel.tsx` (ramo stop-travada + remover no fluxo de venda), `MonitorStatusTab.tsx` (sem mudança de regra, só hospeda os painéis).
- Backend: `backend/app/routes/monitor_spot_stop.py` + `app/services/binance_spot_orders.py` (cancel já cobre `cfstop_` e só-exchange sem tocar não-stop; sem mudança de regra de preço/%/bot).
- Fora: regra da stop (preço, %, bot); withdraw/transfer/futures/margin; compra.
