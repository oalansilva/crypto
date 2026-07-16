## Why

A explicação atual destaca o evento ou a posição do trade, mas não garante que o usuário veja simultaneamente como a estratégia entra e como sai. O card #293 torna o funcionamento completo da estratégia consultável em qualquer estado do trade.

## What Changes

- Exibir sempre os blocos “Quando compra” e “Quando vende” ao expandir a explicação de um trade.
- Separar as regras permanentes da estratégia da explicação contextual do evento atual.
- Aplicar a direção executada sem tautologia: em `long`, os títulos “Quando compra/vende” + condição bastam; em `short`, clarificar que a entrada abre por venda (short) e a saída fecha por compra (cobertura).
- Manter as duas regras em posições abertas, fechadas, fora de posição e payloads legados/protegidos, com fallback seguro.
- Validar catálogo completo, acessibilidade, desktop e mobile sem criar colunas horizontais.

## Capabilities

### New Capabilities

- Nenhuma.

### Modified Capabilities

- `strategy-transparency`: preservar no frontend o par permanente e direcional de regras públicas já fornecido para toda estratégia ativa.
- `monitor`: apresentar simultaneamente as regras de compra e venda no disclosure, independentemente do estado ou evento atual.

## Impact

- Frontend: normalizador de transparência, card do Monitor, `StrategyTradesTable` e `TradeExplanationDisclosure`, mantendo componentes/tokens do `DESIGN.md`.
- API/backend: sem alteração; reutiliza `strategy_transparency.logic_blocks` já publicado e protegido.
- Testes: unidade frontend, acessibilidade e Playwright visual desktop/mobile sobre estratégias/estados distintos.
- Sem alteração nas regras de execução, sinais, preços, métricas ou posições.
