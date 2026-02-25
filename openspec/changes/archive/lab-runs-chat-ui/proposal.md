## Why

Hoje o debug do Strategy Lab fica dependente do LangGraph Studio (tela com **UpStream/DownStream**) e a leitura da execução vira um “grafo” confuso para uso diário. Para entender *o que os agentes conversaram* (decisões, argumentos, porquês), o formato de grafo é pesado.

Queremos uma visualização **estilo ChatGPT** (conversa linear, com mensagens e papéis), direto na página do run (`/lab/runs/:run_id`).

## What Changes

- Adicionar na página `/lab/runs/:run_id` um modo de visualização **Chat (simplificado)** para a conversa dos agentes.
- Corrigir o viewer `/openspec/...` para também abrir **artefatos de Change** (ex.: `proposal.md`, `design.md`, `tasks.md`), pois hoje ele tenta carregar como *spec* e retorna 404.
- Separar claramente as fases:
  - **Upstream**: contrato upstream (aprovado/bloqueado, pergunta, itens faltantes) e eventos relevantes.
  - **Downstream (execução)**: mensagens finais das personas (coordinator/dev_senior/validator) e eventos de execução (backtest/selection gate) em ordem.
- Reduzir ruído por padrão (eventos técnicos ficam colapsados), mas permitir expandir.

## Capabilities

### New Capabilities
- `lab-run-chat-ui`: UI de conversa do run em formato de chat, com filtros e colapsos.

### Modified Capabilities
- `lab-run-page`: adicionar navegação/abas e sumarização de trace events.

## Impact

- Frontend: `frontend/src/pages/LabRunPage.tsx` (refatorar o bloco “Conversa dos agentes” em componente e adicionar UX de chat/tabs/filtros)
- Backend: **idealmente none** (usar `trace_events` existentes). Opcional: padronizar melhor os eventos de fase (Upstream/Downstream) no trace para UI.

## Out of scope

- Substituir o LangGraph Studio como ferramenta de dev.
- Persistir histórico completo de prompts/outputs (mantemos truncamento e apenas resumos/mensagens principais).
