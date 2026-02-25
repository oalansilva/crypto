# Revisão (PT-BR) — monitor-dashboard-mobile-candles

## O que é
Criar uma tela **Dashboard (mobile-first)** para acompanhar o mercado “estilo TradingView”, porém **somente para os símbolos que estão em Favoritos**.

## Principais pontos
- Reaproveitar a tela **Monitor**, adicionando abas:
  - **Status** (o que já existe hoje)
  - **Dashboard** (novo, mobile-first)
- Na aba Dashboard:
  - Lista de cards com os símbolos favoritos.
  - Ao selecionar um símbolo, mostra um **gráfico candlestick**.
  - Troca de timeframe: **15m / 1h / 4h / 1d**.
  - Para **ações**, usar **Yahoo** para intraday e manter `1d` via Stooq/Yahoo:
    - 15m: ~30 dias
    - 1h: ~180 dias
    - 4h: ~365 dias
    - 1d: anos
  - Para **cripto**, usar **CCXT** (15m/1h/4h/1d)
- Usar as **mesmas origens** já existentes quando possível (CCXT para cripto; Stooq/Yahoo para ações).

## Por que
O `/monitor` atual é bom pra status, mas no celular você quer uma visão rápida de preço/tendência por timeframe.

## Como testar (manual rápido)
1) Abrir a nova tela Dashboard no celular.
2) Ver se lista só o que está em Favoritos.
3) Tocar num símbolo e confirmar que o gráfico candlestick aparece.
4) Trocar timeframe:
   - Em cripto, 1h/4h/1d devem funcionar.
   - Em ações, apenas 1d deve ficar habilitado (outros desabilitados/erro claro).

## Observações
- Pode exigir um endpoint backend simples para devolver candles (OHLC) com limite.
- E2E (Playwright) vai validar navegação + troca de timeframe sem depender de rede externa.
