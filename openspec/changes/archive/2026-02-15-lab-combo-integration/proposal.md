## Why

O Lab já possui um fluxo autônomo com aprovação upstream, execução técnica e validação final, mas ainda não integra explicitamente o resultado de otimização do Combo como etapa obrigatória e visível para todos os usuários. Integrar agora reduz retrabalho manual, aumenta consistência entre Lab e Combo, e mantém o Trader avaliando o resultado final já otimizado.

## What Changes

- Integrar o fluxo existente do Combo Strategies dentro da execução do Lab sem alterar regras internas do Combo.
- Tornar obrigatória a sequência automática: template base aprovado -> otimização no Combo -> aplicação automática dos melhores parâmetros -> backtest final -> validação final do Trader.
- Garantir que todo template criado no fluxo use o mesmo contrato de `optimization_schema` do `multi_ma_crossover`: `correlated_groups` + `parameters` com `min`/`max`/`step`.
- Persistir no run do Lab os dados relevantes da otimização do Combo (parâmetros aplicados, métricas e limites usados).
- Exibir no frontend do Lab o resultado da etapa Combo para qualquer usuário que abra o run.
- Manter os mesmos limites e guardrails já aplicados no Combo (sem ampliar ranges, sem novo modo especial no Lab).
- Garantir que TODO template criado no fluxo do Lab use o contrato de `optimization_schema` do `multi_ma_crossover` (correlated_groups obrigatório + parameters com min/max/step), preenchendo ranges como no exemplo do `multi_ma_crossover`.

## Capabilities

### New Capabilities
- `frontend`: Exibir de forma consistente no Lab run o resumo da otimização do Combo e os parâmetros aplicados automaticamente.

### Modified Capabilities
- `backend`: Orquestrar a chamada do Combo dentro do fluxo do Lab, aplicar automaticamente os melhores parâmetros e persistir o resultado no run.

## Impact

- Backend do Lab (`backend/app/routes/lab.py`) e dados persistidos em `backend/logs/lab_runs/<run_id>.json`.
- Integração com serviços já existentes de Combo (`backend/app/services/combo_optimizer.py`, `backend/app/services/combo_service.py`).
- Frontend do Lab run (`frontend/src/pages/LabRunPage.tsx`) para exibição de status e resultado da etapa Combo.
- Sem mudança de contrato do Combo Strategy em si; somente reaproveitamento no Lab.
