## Why

O gate automático CP10 (selection gate) força uma decisão automática antes da validação humana final, reduzindo controle explícito do Trader sobre a aprovação da estratégia. Precisamos remover esse acoplamento para que a decisão de aprovar/rejeitar/ajustar seja exclusivamente do Trader, com fluxo mais previsível e auditável.

## What Changes

- Remover o comportamento de gate automático CP10 no fluxo de seleção.
- Centralizar a decisão final de aprovação no passo de validação do Trader.
- Ajustar estados/transições do Lab para não depender de decisão automática no CP10.
- Garantir que respostas e status expostos para UI/API reflitam decisão do Trader como fonte única de verdade.

## Capabilities

### New Capabilities
- Nenhuma.

### Modified Capabilities
- `lab`: remover seleção automática no CP10 e tornar o Trader o único decisor de aprovação.

## Impact

- Backend do fluxo de orquestração do Lab (nós/arestas e critérios de transição).
- Contrato de estado da execução (status e flags relacionadas a seleção/aprovação).
- UI do Lab para refletir claramente que a aprovação depende apenas do Trader.
