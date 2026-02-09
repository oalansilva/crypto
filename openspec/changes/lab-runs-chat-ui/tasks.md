## Tasks

1) **Normalização de eventos**
   - Criar `RunChatView` que converte `trace_events` em uma lista de itens renderizáveis:
     - `phase_marker`
     - `agent_message`
     - `key_event`
     - `debug_event`

2) **Tabs + filtros**
   - Adicionar tabs (Chat/Debug) na `LabRunPage`.
   - Filtros por persona + toggle “Mostrar eventos técnicos”.

3) **Upstream/Execução**
   - Renderizar um resumo do upstream:
     - `upstream_done.data.approved`
     - `missing[]`
     - `question`
   - Inserir separadores na timeline.

4) **UX polish**
   - Mensagens com layout consistente (bolhas), timestamps, e badges (tokens/duração) opcionais.
   - “Empty state” quando não houver trace.

5) **Viewer de changes (/openspec/changes/...)**
   - Backend: adicionar endpoints read-only para artefatos do change (`openspec/changes/<id>/**`).
   - Frontend: ajustar o viewer para rotear `/openspec/changes/...` e buscar no endpoint de changes.

6) **Validate**
   - Ajustar spec delta em `specs/ui/spec.md`.
   - Rodar `openspec validate lab-runs-chat-ui --type change`.

## Test plan

- Manual:
  - Abrir um run existente e confirmar que o Chat mostra:
    - upstream (quando existir)
    - mensagens das personas
    - decisão do gate
  - Toggle debug: mostra eventos técnicos.

- Automated (lightweight):
  - Teste unitário de normalização (input: trace_events; output: itens + ordem).
