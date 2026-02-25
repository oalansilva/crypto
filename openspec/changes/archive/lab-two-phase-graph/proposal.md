## Why

O fluxo atual do Strategy Lab executa um grafo único sequencial (CP7): `coordinator → dev_senior → validator`. Isso mistura clarificação de requisitos com execução, gerando retrabalho (inputs faltando), decisões menos explícitas e custo desnecessário.

## What Changes

- Introduzir um grafo único com **2 etapas** e branch:
  1) **Upstream** (humano no `/lab` + trader/validator): clarifica inputs, riscos e critérios de aceite e produz um `upstream_contract`.
  2) **Implementação + testes**: executa a etapa de implementação e validações determinísticas.
- Tornar Upstream **obrigatório sempre**.
- Tornar a etapa 2 **automática** após upstream aprovado.
- Persistir `upstream_contract` no run JSON e registrar eventos de trace por etapa.

## Capabilities

### New Capabilities
- `lab-two-phase-graph`: Grafo do Lab em 2 etapas com contrato upstream e branch condicional.

### Modified Capabilities
- (nenhuma)

## Impact

- Backend: `backend/app/routes/lab.py`, `backend/app/services/lab_graph.py` (e possivelmente serviços auxiliares)
- Frontend: `/lab` para suportar ciclo `needs_user_input` como conversa
- Logs/trace: novos eventos por etapa
