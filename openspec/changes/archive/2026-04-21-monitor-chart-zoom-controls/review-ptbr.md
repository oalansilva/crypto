# Revisão (PT-BR) — monitor-chart-zoom-controls

## O que é
Adicionar controles explícitos de `zoom in` e `zoom out` no gráfico detalhado de uma estratégia dentro do `/monitor`, para ficar mais próximo da navegação esperada por quem usa TradingView.

## Mudanças principais
- Adiciona botões visíveis de zoom no gráfico expandido da estratégia.
- O zoom altera apenas a janela visível de candles; não muda timeframe e não depende de refetch por padrão.
- Mantém o comportamento atual de indicadores, crosshair e painel de RSI sincronizados.
- Mantém o escopo no frontend do Monitor, sem trocar biblioteca de gráfico e sem mudar backend.

## Fora de escopo
- Não transforma o gráfico em um clone completo do TradingView.
- Não adiciona ferramentas de desenho, alertas, anotações ou persistência de zoom.
- Não amplia o escopo para o mini-gráfico embutido no card, a menos que isso seja decidido depois.

## Como validar
1. Abrir `/monitor`.
2. Abrir o gráfico detalhado de uma estratégia.
3. Confirmar que existem controles diretos de zoom.
4. Confirmar que:
   - `zoom in` mostra menos candles
   - `zoom out` mostra mais candles
   - o timeframe atual continua o mesmo
   - indicadores e RSI continuam sincronizados
   - o zoom não dispara recarga de candles por padrão

## Artefatos
- Proposal: `openspec/changes/monitor-chart-zoom-controls/proposal.md`
- Design: `openspec/changes/monitor-chart-zoom-controls/design.md`
- Tasks: `openspec/changes/monitor-chart-zoom-controls/tasks.md`
