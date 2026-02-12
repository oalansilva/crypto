# Change Proposal: iterative-dev-loop

## Summary
Implementar o loop Dev → Backtest → Ajuste → Backtest antes de enviar para Trader, seguindo o fluxograma definido pelo Alan.

## Why
Hoje o pipeline executa apenas um backtest por iteração e envia o resultado direto para o gate/Trader, mesmo quando o diagnóstico aponta filtros restritivos ou inconsistências (ex.: 0 trades). Isso quebra o fluxo esperado e faz o sistema reprovar estratégias sem tentar ajustes mínimos. Precisamos garantir que o **Dev ajuste e re‑rode** o backtest automaticamente quando o resultado não estiver OK, antes de envolver o Trader.

## What Changes
- Adicionar loop de ajuste automático no estágio Dev quando o backtest falhar (ex.: 0 trades, métricas degeneradas).
- Re‑rodar backtest após ajustes até atingir critérios mínimos ou um limite de tentativas.
- Só então chamar o Trader para validação final.

## Out of Scope
- Alterações no frontend (renderização do chat).
- Novos indicadores avançados ou otimizações extensas.

## Risks
- Ajustes automáticos podem mudar o racional original do draft; precisamos registrar os ajustes em trace.
- Loop mal configurado pode aumentar custo/tempo. Limitar tentativas.
