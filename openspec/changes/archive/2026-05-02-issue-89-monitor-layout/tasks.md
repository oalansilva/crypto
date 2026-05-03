# Tasks: Issue #89 — Refazer layout do menu e monitor principal

- [x] Atualizar `frontend/src/components/AppNav.tsx` para alinhar seções e itens ao layout de painel (principalmente incluir `Backtests` em Estratégias e manter trilha/labels consistentes).
- [x] Refatorar `frontend/src/components/monitor/MonitorStatusTab.tsx` para novo layout da tela principal do Monitor com:
  - Topbar contextual.
  - KPI strip.
  - Filtros/ordenação.
  - Seções `HOLD / WAIT / EXIT` com tabelas e linhas expansíveis.
  - Preservação de ações existentes (in portfolio, modo, timeframe, abertura de gráfico) e estados existentes de tema.
- [x] Atualizar estilos em `frontend/src/index.css` com as classes novas do layout tabular do Monitor.
- [x] Validar visualmente no frontend local o estado vazio/simplificado e a persistência de tema.
