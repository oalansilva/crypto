# Proposal: Refazer o layout do menu e da tela principal do Monitor (Issue #89)

## Why

A tela de Monitor e a navegação principal devem seguir o padrão visual pedido no anexo da issue, com uma estrutura de páginas mais próxima de um painel operacional: sidebar com seções claras, topbar de contexto e listagem principal do Monitor em formato tabular por estado.

## What

Esta change atualiza a experiência do Monitor sem alterar os contratos de backend:

- Reestruturação do layout visual da `MonitorPage` para:
  - Cabeçalho com blocos de contexto (título, última atualização, tema e atualização).
  - KPIs resumidos por estado.
  - Filtros rápidos e ordenação.
  - Tabelas por seção `HOLD / WAIT / EXIT` com linhas expansíveis.
- Mantém a interação de preferência por card (in portfolio, modo, timeframe) e abertura do gráfico.
- Ajusta os itens de navegação para refletir as seções do protótipo (Painel/Estratégias/Conta/Admin), incluindo Backtests no grupo Estratégias.

## Scope

### Frontend
- `frontend/src/components/AppNav.tsx`
- `frontend/src/components/monitor/MonitorStatusTab.tsx`
- `frontend/src/index.css`

### Operacional de processo
- `openspec/changes/issue-89-monitor-layout/`

## Out of Scope

- Modificação de regras de estado de oportunidade no backend.
- Implementação de novo engine de monitoramento/tabelas com paginação remota.

## Impact

- Entrega alinhada com o layout pedido na issue sem mudanças de contrato backend.
- O Monitor passa a ter estrutura mais densa, operacional e com fluxo de leitura por estado.
- Navegação visual mais próxima do protótipo para reduzir ruído no dia a dia.
