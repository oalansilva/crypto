# Revisão PT-BR — orden-execu-o-dos-cards

## Resumo

Esta change transforma a coluna do Kanban em uma **fila ordenada de execução**, não só uma lista estática.

Hoje falta um jeito simples de dizer:
- qual card vem primeiro
- qual pode esperar
- qual agente deve puxar antes dentro da mesma etapa

## O que entra
- reorder manual de cards dentro da mesma coluna
- persistência da ordem no runtime/workflow DB
- atualização imediata do board após a mudança
- regra operacional explícita: agentes puxam a fila na ordem visível

## O que não entra
- mudar gates/colunas por reorder
- priorização automática
- reorder em lote
- redefinição completa do modelo de backlog

## Decisão de PO
- a posição do card na coluna deve significar prioridade operacional real
- a primeira versão deve privilegiar clareza e baixa fricção, não um sistema complexo de ranking
- o comportamento precisa ser estável e auditável no runtime/Kanban
- por envolver interação de board, o próximo gate é DESIGN para definir a UX mais segura e enxuta

## Próximo gate
- DESIGN definir a interação mínima de reorder (desktop e mobile), feedback visual e limites da operação intra-coluna
