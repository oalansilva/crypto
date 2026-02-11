## 1. UI — Chat simplificado no /lab/runs/:run_id

- [x] 1.1 Extrair um componente `RunChatView` (ex.: `frontend/src/components/lab/RunChatView.tsx`) que normaliza `trace_events` em itens renderizáveis:
  - `phase_marker`
  - `agent_message`
  - `key_event`
  - `debug_event`
- [x] 1.2 Adicionar **tabs** na `LabRunPage`: `Chat (simplificado)` (default) e `Eventos (debug)`.
- [x] 1.3 Implementar filtros por persona + toggle **Mostrar eventos técnicos** (off por padrão).
- [x] 1.4 Inserir separadores de fase (Upstream/Execução) e um resumo do upstream quando existir `upstream_done`.
- [x] 1.5 UX polish: empty state quando não houver trace; bolhas consistentes; timestamps.

## 2. Tests / Verify

- [ ] 2.1 (Opcional) Teste unitário da normalização de eventos.
- [x] 2.2 `openspec validate lab-runs-chat-ui --type change`.
- [x] 2.3 `npm --prefix frontend run build`.

## Test plan

- Manual:
  - Abrir um run existente e confirmar que o Chat mostra:
    - upstream (quando existir)
    - mensagens das personas
    - decisão do gate
  - Toggle debug: mostra eventos técnicos.
