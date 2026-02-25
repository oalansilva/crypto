## Context

O fluxo atual do Lab ainda contém o gate automático CP10 (selection gate), que pode influenciar a decisão de continuidade/aprovação sem passar integralmente pelo julgamento do Trader. O objetivo deste change é remover esse gate de decisão automática e consolidar a aprovação final no Trader, mantendo o fluxo mais claro para backend, API e UI.

## Goals / Non-Goals

**Goals:**
- Remover o CP10 como ponto de decisão automática no fluxo.
- Garantir que a aprovação/rejeição final venha somente do Trader.
- Manter rastreabilidade de estados para consumidores de API/UI.
- Preservar o comportamento existente das demais fases que não dependem do CP10.

**Non-Goals:**
- Redesenhar toda a arquitetura do grafo do Lab.
- Alterar critérios internos de avaliação do Trader.
- Mudar regras de persistência de favoritos/templates além do necessário para remover o CP10.

## Decisions

1. Eliminar o branch de decisão automática do CP10 no grafo.
- Racional: evita dupla autoridade de decisão e reduz inconsistência de estado.
- Alternativa considerada: manter CP10 apenas como heurística informativa.
- Motivo para não adotar alternativa: heurística no mesmo ponto tende a ser interpretada como decisão efetiva por UI/API.

2. Tornar o veredito do Trader a única fonte de verdade para aprovação final.
- Racional: alinhamento com requisito de governança humana no estágio final.
- Alternativa considerada: fallback automático quando Trader não responder.
- Motivo para não adotar alternativa: reintroduz decisão automática fora do Trader.

3. Padronizar estados expostos para indicar trajetória Trader-driven.
- Racional: clientes (frontend e integrações) precisam inferência inequívoca do fluxo.
- Alternativa considerada: manter campos antigos de CP10 por compatibilidade total.
- Motivo para não adotar alternativa: preserva ambiguidade e aumenta custo de manutenção.

## Risks / Trade-offs

- [Risco] Fluxos legados podem depender de sinais de CP10 em regras de UI/API.
  Mitigação: mapear consumidores e ajustar contratos de estado + testes de regressão.

- [Risco] Regressão em transições de fase quando CP10 for removido.
  Mitigação: testes de unidade/integrados para caminhos `approved`, `rejected` e `needs_adjustment` pelo Trader.

- [Trade-off] Menos automação inicial em troca de governança explícita do Trader.
  Mitigação: manter telemetria e tempos de fase para avaliar impacto operacional.

## Migration Plan

1. Remover o uso do CP10 como gate de seleção nas transições do fluxo.
2. Ajustar lógica de status/outputs para representar apenas decisão do Trader.
3. Atualizar camadas de API e UI que leem flags ou estados associados ao CP10.
4. Executar suíte de testes focada no fluxo do Lab e cenários de aprovação Trader.
5. Deploy controlado e validação pós-deploy dos runs novos.

Rollback:
- Reverter commit(s) do change caso haja bloqueio crítico em produção.
- Restaurar transição anterior temporariamente até correção do fluxo Trader-only.

## Open Questions

- Existe consumidor externo que dependa explicitamente de um campo com semântica CP10 para analytics?
- O frontend atual já diferencia claramente "pendente do Trader" versus "decidido" sem referências ao CP10?
- Precisamos manter algum evento de observabilidade com nome CP10 apenas para histórico, sem papel decisório?
