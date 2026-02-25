# Revisão (PT-BR) — monitor-unified-cards-timeframe-prefs

## O que é
Unificar o Monitor em uma **única tela de cards** (sem abas Status/Dashboard) e adicionar **timeframe por card** no modo Preço, com persistência no backend.

## Comportamento
- `/monitor` vira uma única tela de cards.
- Cada card continua com:
  - toggle **Preço ↔ Estratégia**
  - toggle ⭐ **Portfolio** (Em carteira)
- No modo **Preço**, o card passa a ter seletor de **timeframe**.

## Persistência (backend)
Além de `in_portfolio` e `card_mode`, salvar também:
- `price_timeframe` (default: **1d**)

## Regras de timeframe
- **Cripto**: 15m / 1h / 4h / 1d
- **Ações**: somente 1d (por enquanto)

## Defaults
- Filtro padrão: **In Portfolio**
- Símbolos sem preferência aparecem apenas em **All**
- Modo padrão: **Preço**
- Timeframe padrão: **1d**

## Como testar (manual rápido)
1) Abrir `/monitor` (ver que não existem mais abas).
2) Em um cripto (ex: BTC/USDT), mudar timeframe (15m/1h/4h/1d) e dar reload → deve persistir.
3) Em uma ação (ex: NVDA), confirmar que só 1d fica disponível.
